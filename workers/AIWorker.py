import os
import logging
import sys
from tools.openai_adapter import OpenaiAdapter
from tools.bing_search_adapter import BingSearchAdapter
from tools.tools import download, saveToJson, imageWebsite
from workers.webWorker import WebWorker
from workers.imageWorker import ImageWorker

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,  # set to logging.DEBUG for verbose output
        format="[%(asctime)s] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p %Z")
logger = logging.getLogger(__name__)

class PromptMap:
    getImageSearchQuery = "./prompts/ImageSearchSystemMessageExample.json"
    summaryNewsScript = "./prompts/newsWebsiteToScript.json"
    reviewGeneratedScripts = "./prompts/reviewGeneratedScripts.json"
    textToAnchorPrompt = "./prompts/textToAnchor.json"
    commonWebPageScript = "./prompts/webpageToScript.json"
    selectImageForCaption = "./prompts/selectImageForCaption.json"


class AIWorker:
    @staticmethod
    def reviewGeneratedScript(news_title: str, script: str, oai: OpenaiAdapter):
        question = "Title: {news}\nRequired Script Length: about 200\nScript: {script}".format(
            news=news_title,
            script=script
        )
        try:
            answer = oai.AOAIQuery(question, PromptMap.reviewGeneratedScripts)
            return answer.find("#PASS") > 0
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def summaryNewsScript(news_provider:str, news_title:str, news_content:str, oai: OpenaiAdapter, max_try:int = 2):
        q = """消息源: {provider}
        title: {title}

        {content}""".format(provider=news_provider, title=news_title, content=news_content)
        script = oai.AOAIQuery(q, PromptMap.summaryNewsScript, max_try=max_try)
        return script
    
    @staticmethod
    def summaryAnyWebpageScript(webpage_text:str, oai: OpenaiAdapter, max_try:int = 2):
        script = oai.AOAIQuery(webpage_text, PromptMap.commonWebPageScript, max_try=max_try)
        return script

    @staticmethod
    def selectImageForCaption(title:str, script:str, images:list, oai: OpenaiAdapter, max_try:int = 2):
        q = """Title: {title}
        Script: {script}
        Image list:
        {image_list}""".format(
            title=title, 
            script=script,
            image_list="\n".join([str(index) + '. ' + str({
                "fileName": image["name"],
                "description": image["alt"] + ("\nOCR results" + image["ocr"]) if len(image["ocr"])> 0 else ""}) for index, image in enumerate(images)])
            )
        answer = oai.AOAIQuery(q, PromptMap.selectImageForCaption, max_try=max_try)
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
    def getImageSearchQuery(caption:str, oai: OpenaiAdapter, retry:int = 3):
        if retry<0:
            raise "General new fail as no chance for retry!"
        try:
            return oai.AOAIQuery(caption, PromptMap.getImageSearchQuery)
        except Exception as e:
            return AIWorker.getImageSearchQuery(caption, oai, retry-1)
    
    @staticmethod
    def reviewImageForCaption(image_name: str, caption: str, news_title: str, oai: OpenaiAdapter):
        question = "Illustration for sentence `{caption}` of news `{news}`\nImage name: {imageName}".format(
            imageName=image_name,
            caption=caption,
            news=news_title
        )
        try:
            answer = oai.AOAIQuery(question, PromptMap.reviewGeneratedScripts)
            return answer.find("#PASS") > 0
        except Exception:
            print("Error during answer, ", question)
            return False
    
    @staticmethod
    def downloadOnlineImagesForCaption(caption:str, news_title:str, folder:str, file_suffix:str, oai: OpenaiAdapter, bing:BingSearchAdapter, top:int = 5):
        try:
            imageSearchText = AIWorker.getImageSearchQuery(caption, oai)
            searchedImages = bing.searchImage(imageSearchText)
            if folder:
                saveToJson(os.path.join(folder, "searched-images-{}.json".format(file_suffix)), searchedImages)

            for img_index, img_info in enumerate(searchedImages[:5]):
                img_local_path, img_name, encoding_format = WebWorker.downloadWebsiteImage(
                    url=img_info['contentUrl'],
                    output_dir=folder,
                    file_name='online-image-{}-{}'.format(file_suffix, img_index)
                )
                if not img_local_path is None and AIWorker.reviewImageForCaption(img_info['name'], caption, news_title, oai):
                    return {
                        "provider": imageWebsite(img_info['contentUrl'],),
                        "img_name": img_name,
                        "alt": img_info["name"],
                        "encodingFormat": encoding_format,
                        "img_local_path": img_local_path
                        }, img_local_path
        except Exception as e:
            logger.error(e)
            
        return None, None

