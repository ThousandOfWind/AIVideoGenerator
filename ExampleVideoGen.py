import os
from tools.tools import getCurrentTimeAsFolder
from openai import AzureOpenAI
from tools.openai_adapter import OpenaiAdapter
from tools.speech_adapter import SpeechServiceAdapter, DefaultMaleSpeaker
from tools.bing_search_adapter import BingSearchAdapter, ChinaCategory, Market
from workers.AIDirector import AIDirector
from dotenv import load_dotenv

load_dotenv()

bing = BingSearchAdapter(
    bing_search_api=os.getenv('BING_SEARCH_ENDPOINT'), 
    bing_search_key=os.getenv('BING_SEARCH_KEY')
)
newsList = bing.newsCategoryTrending(ChinaCategory.Sports.value, Market.China.value)
news = newsList[0]

oai = OpenaiAdapter(openai_client=AzureOpenAI(
    api_version="2023-12-01-preview",
    azure_endpoint=os.getenv('OPANAI_API_ENDPOINT'),
    api_key=os.getenv('OPANAI_API_KEY'),
))
speech = SpeechServiceAdapter(os.getenv('SPEECH_HOST'), os.getenv('SPEECH_REGION'), os.getenv('SPEECH_KEY'), DefaultMaleSpeaker)

director = AIDirector(oai, speech, bing, '/System/Library/Fonts/Supplemental/Arial Unicode.ttf')

director.news2Video(news, folderPath=getCurrentTimeAsFolder())
