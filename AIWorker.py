import os
import requests
import azure.cognitiveservices.speech as speechsdk
from tools.openai_adapter import OpenaiAdapter
from tools.bing_search_adapter import BingSearchAdapter
from tools.tools import download, saveToJson, imageWebsite

class ImageEncodingFormat:
    JPEG = 'jpeg'
    PNG = 'png'

class PromptMap:
    getImageSearchQuery = "prompts/ImageSearchSystemMessageExample.json"
    summaryNewsSript = "prompts/newsWebsiteToScript.json"
    reviewGeneratedScripts = "prompts/reviewGeneratedScripts.json"

class AIWorker:
    @staticmethod
    def reviewGeneratedScript(news_title: str, script: str, oai: OpenaiAdapter):
        question = "Title: {news}\nRequired Script Length: about 200\nScript: {script}".format(
            news=news_title,
            script=script
        )
        try:
            answer = oai.AOAIquery(question, PromptMap.reviewGeneratedScripts)
            return answer.find("#PASS") > 0
        except Exception as e:
            print(e)
            return False

    @staticmethod
    def summaryNewsSript(news_provider:str, news_title:str, news_content:str, oai: OpenaiAdapter, retry:int = 2):
        if retry<0:
            raise "General new fail as no chance for retry!"
        q = """消息源: {provider}
        title: {title}

        {content}""".format(provider=news_provider, title=news_title, content=news_content)
        script = oai.AOAIquery(q, PromptMap.summaryNewsSript)
        if AIWorker.reviewGeneratedScript(news_title=news_title, script=script, oai=oai):
            return script
        else:
            AIWorker.summaryNewsSript(news_provider, news_title, news_content, oai, retry-1)

    @staticmethod
    def getImageSearchQuery(caption:str, oai: OpenaiAdapter, retry:int = 3):
        if retry<0:
            raise "General new fail as no chance for retry!"
        try:
            return oai.AOAIquery(caption, PromptMap.getImageSearchQuery)
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
            answer = oai.AOAIquery(question, PromptMap.reviewGeneratedScripts)
            return answer.find("#PASS") > 0
        except Exception:
            print("Error during answer, ", question)
            return False
    
    @staticmethod
    def downloadOnlineImagesForCaption(caption:str, news_title:str, folder:str, file_suffix:str, oai: OpenaiAdapter, bing:BingSearchAdapter):
        imageSearchText = AIWorker.getImageSearchQuery(caption, oai)
        searchedImages = bing.searchImage(imageSearchText)
        if folder:
            saveToJson(os.path.join(folder, "searched-images-{}.json".format(file_suffix)), searchedImages)

        for img_index, img_info in enumerate(searchedImages):
            if img_info['encodingFormat'] in [ImageEncodingFormat.JPEG, ImageEncodingFormat.PNG]:
                type_suffix = str(img_info['contentUrl']).split('.')[-1]
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
    def drawImage(prompt:str, folder:str, file_suffix:str, oai: OpenaiAdapter):
        # result = (oai.openai_client).images.generate(
        #     model="dall-e-3", # the name of your DALL-E 3 deployment
        #     prompt=prompt,
        #     size="1024x1024",
        #     n=1
        # )
        # image_url = json.loads(result.model_dump_json())['data'][0]['url']
        url = "https://julieaoaisweden.openai.azure.com/openai/deployments/Dalle3/images/generations?api-version=2023-12-01-preview"
        headers = {"api-key": oai.openai_client.api_key, "Content-Type": "application/json"}
        body = {
            # Enter your prompt text here
            "prompt": prompt,
            "size": "1024x1024",  # supported values are “1792x1024”, “1024x1024” and “1024x1792”
            "n": 1,
            "quality": "hd",  # Options are “hd” and “standard”; defaults to standard
            "style": "vivid"  # Options are “natural” and “vivid”; defaults to “vivid”
        }
        submission = requests.post(url, headers=headers, json=body)
        image_url = submission.json()['data'][0]['url']
        image_path = os.path.join(folder, 'dalle-image-{}.png'.format(file_suffix))
        download(image_path, image_url)
        return {
            "provider": "Dalle",
            "name": prompt,
            "encodingFormat": "png"
               }, image_path


    @staticmethod
    def text2audio(text, audio_path:str, speech_config: speechsdk.SpeechConfig):
        # use the default speaker as audio output.
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)

        result = speech_synthesizer.speak_text(text)
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(text))
            stream = speechsdk.AudioDataStream(result)
            stream.save_to_wav_file(audio_path)
            return {"audio_duration": result.audio_duration.seconds}, audio_path

        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))

        return None, None
