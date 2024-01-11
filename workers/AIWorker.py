import os
from tools.openai_adapter import OpenaiAdapter
from tools.bing_search_adapter import BingSearchAdapter
from tools.tools import download, saveToJson, imageWebsite
from workers.logisticsWorker import LogisticsWorker

class ImageEncodingFormat:
    JPEG = 'jpeg'
    PNG = 'png'

class PromptMap:
    getImageSearchQuery = "./prompts/ImageSearchSystemMessageExample.json"
    summaryNewsScript = "./prompts/newsWebsiteToScript.json"
    reviewGeneratedScripts = "./prompts/reviewGeneratedScripts.json"
    textToAnchorPrompt = "./prompts/textToAnchor.json"

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
    def summaryNewsScript(news_provider:str, news_title:str, news_content:str, oai: OpenaiAdapter, retry:int = 2):
        if retry<0:
            raise "General new fail as no chance for retry!"
        q = """消息源: {provider}
        title: {title}

        {content}""".format(provider=news_provider, title=news_title, content=news_content)
        script = oai.AOAIQuery(q, PromptMap.summaryNewsScript)
        if AIWorker.reviewGeneratedScript(news_title=news_title, script=script, oai=oai):
            return script
        else:
            AIWorker.summaryNewsScript(news_provider, news_title, news_content, oai, retry-1)

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
        imageSearchText = AIWorker.getImageSearchQuery(caption, oai)
        searchedImages = bing.searchImage(imageSearchText)
        if folder:
            saveToJson(os.path.join(folder, "searched-images-{}.json".format(file_suffix)), searchedImages)

        for img_index, img_info in enumerate(searchedImages[:5]):
            if img_info['encodingFormat'] in [ImageEncodingFormat.JPEG, ImageEncodingFormat.PNG]:
                type_suffix = str(img_info['contentUrl']).split('!')[0].split('?')[0].split('.')[-1]
            else:
                continue
            if AIWorker.reviewImageForCaption(img_info['name'], caption, news_title, oai):
                contentUrl = img_info['contentUrl']
                image_path = os.path.join(folder, 'online-image-{}.{}'.format(file_suffix, type_suffix))
                try:
                    download(image_path, contentUrl)
                    return {
                        "provider": imageWebsite(contentUrl),
                        "name": img_info["name"],
                        "encodingFormat": img_info["encodingFormat"]
                           }, image_path
                except Exception as e:
                    continue
        return None, None
    
    @staticmethod
    def drawAnchor(text:str, folder:str, file_suffix:str, oai: OpenaiAdapter):
        question = "When you broadcast `{text}`, what expression and gesture you will perform? Answer the key look in one short sentence. ".format(
            text=text)

        try:
            answer = oai.AOAIQuery(question, PromptMap.reviewGeneratedScripts)
            return oai.draw(
                "realistic 3d rendering, created using C4D modeling. A famous Chinese male anchor, {0}".format(answer),
                folder,
                "anchor-{0}".format(file_suffix)
            )
        except Exception:
            print("Error during answer, ", question)
            return LogisticsWorker.getDefaultAvatarImage()
    

