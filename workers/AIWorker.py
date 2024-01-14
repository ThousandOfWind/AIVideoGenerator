import os
import logging
import sys
from tools.openai_adapter import OpenaiAdapter
from tools.bing_search_adapter import BingSearchAdapter
from tools.tools import save_to_json, image_website
from tools.prompt import PromptMap
from workers.webWorker import WebWorker
from models.image import ImageInfo
from typing import List
from easyocr import Reader

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
            return answer.find("#PASS") > 0
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
        if answer.find('NA') > 0:
            return -1
        try:
            select = int(answer)
            if select>= 0 and select < len(images):
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
            return answer.find("#PASS") > 0
        except Exception:
            print("Error during answer, ", question)
            return False
    
    @staticmethod
    def download_online_image_for_clip(caption:str, news_title:str, folder:str, file_suffix:str, oai: OpenaiAdapter, bing:BingSearchAdapter, ocr_reader:Reader =None, top:int = 5):
        try:
            imageSearchText = AIWorker.get_image_search_query(caption, oai)
            searchedImages = bing.search_image(imageSearchText)
            if folder:
                save_to_json(os.path.join(folder, "searched-images-{}.json".format(file_suffix)), searchedImages)

            for img_index, img_info in enumerate(searchedImages[:top]):
                img_local_path, img_name, encoding_format = WebWorker.downloadWebsiteImage(
                    url=img_info['contentUrl'],
                    output_dir=folder,
                    file_name='online-image-{}-{}'.format(file_suffix, img_index)
                )
                if ocr_reader:
                    ai_description = " ".join(ocr_reader.readtext(img_local_path, detail = 0))
                else:
                    ai_description = ''
                image_info = ImageInfo(img_local_path, img_name, ai_description, image_website(img_info['contentUrl']))
                if not img_local_path is None and AIWorker.review_image(image_info, caption, news_title, oai):
                    return image_info
        except Exception as e:
            logger.error(e)
            
        return None

