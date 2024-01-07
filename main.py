import os
from tools.tools import getCurrentTimeAsFolder
from openai import AzureOpenAI
from tools.openai_adapter import OpenaiAdapter
import azure.cognitiveservices.speech as speechsdk
from tools.bing_search_adapter import BingSearchAdapter, ChinaCategory, Market
from AIDirector import AIDirector
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    api_version="2023-12-01-preview",
    azure_endpoint=os.getenv('OPANAI_API_ENDPOINT'),
    api_key=os.getenv('OPANAI_API_KEY'),
)
oai = OpenaiAdapter(openai_client=client)
speech_config = speechsdk.SpeechConfig(subscription=os.getenv('SPEECH_KEY'), region=os.getenv('SPEECH_REGION'))
speech_config.speech_synthesis_voice_name = "zh-CN-YunyangNeural"
bing = BingSearchAdapter(bing_search_api=os.getenv('BING_SEARCH_ENDPOINT'), bing_search_key=os.getenv('BING_SEARCH_KEY'))
director = AIDirector(oai, speech_config, bing, '/System/Library/Fonts/Supplemental/Arial Unicode.ttf')

folderPath = getCurrentTimeAsFolder()
newsList = bing.newsCategoryTrending(ChinaCategory.Sports, Market.China)
director.news2Video(newsList[0], folderPath)



