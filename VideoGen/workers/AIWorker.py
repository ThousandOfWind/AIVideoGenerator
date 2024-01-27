import os
import logging
import sys
from typing import List
from easyocr import Reader
from VideoGen.info import ImageInfo, TableInfo
import VideoGen.prompt as PromptMap
from VideoGen.tools.tools import save_to_json
from VideoGen.workers.imageWorker import ImageWorker
from VideoGen.tools.openai_adapter import OpenaiAdapter
from VideoGen.tools.bing_search_adapter import BingSearchAdapter

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,  # set to logging.DEBUG for verbose output
        format="[%(asctime)s] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p %Z")
logger = logging.getLogger(__name__)

class AIWorker:
    @staticmethod
    def review_script(news_title: str, script: str, oai: OpenaiAdapter):
        question = "Title: {news}\nRequired Script Length: about 200\nScript: {script}".format(
            news=news_title,
            script=script
        )
        try:
            answer = oai.ask_llm(question, PromptMap.reviewGeneratedScripts)
            return answer.find("#PASS") >= 0
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def script_for_news(news_provider:str, news_title:str, news_content:str, oai: OpenaiAdapter, max_try:int = 2):
        q = """消息源: {provider}
        title: {title}

        {content}""".format(provider=news_provider, title=news_title, content=news_content)
        script = oai.ask_llm(q, PromptMap.summaryNewsScript, max_try=max_try)
        return script
    
    @staticmethod
    def script_for_any_webpage(webpage_text:str, oai: OpenaiAdapter, max_try:int = 2):
        script = oai.ask_llm(webpage_text, PromptMap.commonWebPageScript, max_try=max_try)
        return script

    @staticmethod
    def select_image_for_clip(title:str, script:str, images: List[ImageInfo], oai: OpenaiAdapter, max_try:int = 2):
        q = """Title: {title}
        Script: {script}
        Image list:
        {image_list}""".format(
            title=title, 
            script=script,
            image_list="\n".join(["{}. {}".format(index, image.description) for index, image in enumerate(images)]))
        answer = oai.ask_llm(q, PromptMap.selectImageForCaption, max_try=max_try)
        if answer.find('NA') >= 0:
            return -1
        try:
            select = int(answer)
            if select>= 0 and select < len(images):
                return select
        except Exception as e:
            logger.error("answer `{}` cannot be a legal index".format(answer))
        return -1
    
    @staticmethod
    def select_tale_for_clip(title:str, script:str, tables: List[TableInfo], oai: OpenaiAdapter, max_try:int = 2):
        q = """Title: {title}
        Script: {script}
        Image list:
        {image_list}""".format(
            title=title, 
            script=script,
            image_list="\n".join(["{}. {}".format(index, tables.title) for index, tables in enumerate(tables)]))
        answer = oai.ask_llm(q, PromptMap.selectImageForCaption, max_try=max_try)
        if answer.find('NA') >= 0:
            return -1
        try:
            select = int(answer)
            if select>= 0 and select < len(tables):
                return select
        except Exception as e:
            logger.error("answer `{}` cannot be a legal index".format(answer))
        return -1
    
    @staticmethod
    def get_image_search_query(caption:str, oai: OpenaiAdapter, retry:int = 3):
        if retry<0:
            raise "General new fail as no chance for retry!"
        try:
            return oai.ask_llm(caption, PromptMap.getImageSearchQuery)
        except Exception as e:
            return AIWorker.get_image_search_query(caption, oai, retry-1)
    
    @staticmethod
    def review_image(image_info: ImageInfo, caption: str, news_title: str, oai: OpenaiAdapter):
        question = "Illustration for sentence `{caption}` of news `{news}`\nImage: {imageName}".format(
            imageName=image_info.description,
            caption=caption,
            news=news_title
        )
        try:
            answer = oai.ask_llm(question, PromptMap.reviewGeneratedScripts)
            return answer.find("#PASS") >= 0
        except Exception:
            print("Error during answer, ", question)
            return False
    
    @staticmethod
    def download_online_image_for_clip(
        script:str, 
        title:str, 
        folder:str, 
        file_suffix:str, 
        oai: OpenaiAdapter, 
        bing:BingSearchAdapter, 
        ocr_reader:Reader =None, 
        top:int = 5) -> ImageInfo:
        try:
            image_search_text = AIWorker.get_image_search_query(script, oai)
            logger.info("search `{}` for caption `{}`".format(image_search_text, script))
            searchedImages = bing.search_image(image_search_text)
            save_to_json(os.path.join(folder, "searched-images-{}.json".format(file_suffix)), searchedImages)
            images = []
            
            for img_index, bing_img_info in enumerate(searchedImages[:top]):
                try:
                    image_info = ImageWorker.downloadWebsiteImage(
                        url=bing_img_info['contentUrl'],
                        output_dir=folder,
                        file_name='online-image-{}-{}'.format(file_suffix, img_index)
                    )
                    image_info.title = bing_img_info['name']
                    if ocr_reader:
                        image_info.ocr_result = " ".join(ocr_reader.readtext(image_info.path, detail = 0))
                    
                    images.append(image_info)
                except Exception as e:
                    logger.error(e)
            selected = AIWorker.select_image_for_clip(
                title=title,
                script=script,
                images=images,
                oai=oai
            )
            if selected >= 0:
                return images[selected]
        except Exception as e:
            logger.error(e)
            
        return None

