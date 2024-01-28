import os
from dotenv import load_dotenv
from VideoGen.tool import IOTool, OpenaiAdapter, SpeechServiceAdapter, DefaultMaleSpeaker, BingSearchAdapter, ChinaCategory, Market
from VideoGen.workers import AIDirector

load_dotenv()

bing = BingSearchAdapter(
    bing_search_api=os.getenv('BING_SEARCH_ENDPOINT'), 
    bing_search_key=os.getenv('BING_SEARCH_KEY')
)
newsList = bing.news_category_trending(ChinaCategory.Sports.value, Market.China.value)
news = newsList[0]

oai = OpenaiAdapter.from_config({
    "type": 'AzureOpenAI',
    "api_key": os.getenv('OPANAI_API_KEY'),
    "endpoint": os.getenv('OPANAI_ENDPOINT'),
    "chat_model": "gpt-4-32k"
})
speech = SpeechServiceAdapter(os.getenv('SPEECH_HOST'), os.getenv('SPEECH_REGION'), os.getenv('SPEECH_KEY'), DefaultMaleSpeaker)

director = AIDirector(oai, speech, bing)

director.news2Video(news, folderPath=IOTool.current_time_as_folder())
