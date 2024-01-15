import os
from tools.tools import current_time_as_folder
from openai import AzureOpenAI
from tools.openai_adapter import OpenaiAdapter
from tools.speech_adapter import SpeechServiceAdapter, DefaultFemaleSpeaker
from tools.bing_search_adapter import BingSearchAdapter, ChinaCategory, Market
from workers.AIDirector import AIDirector
from dotenv import load_dotenv
from configs.directorConfig import DirectorConfig


load_dotenv()

client = AzureOpenAI(
    api_version="2023-12-01-preview",
    azure_endpoint=os.getenv('OPANAI_API_ENDPOINT'),
    api_key=os.getenv('OPANAI_API_KEY'),
)
oai = OpenaiAdapter(openai_client=client)
speech = SpeechServiceAdapter(os.getenv('SPEECH_HOST'), os.getenv('SPEECH_REGION'), os.getenv('SPEECH_KEY'), DefaultFemaleSpeaker)
bing = BingSearchAdapter(bing_search_api=os.getenv('BING_SEARCH_ENDPOINT'), bing_search_key=os.getenv('BING_SEARCH_KEY'))
config = DirectorConfig({
    "use_avatar": True,
    "use_ocr":True,
    "use_image_in_webpage": True,
    "search_online_image": True,
    "script_seps": ('\n', '。', "？", "！")
})
director = AIDirector(oai, speech, bing, config=config)

folderPath = current_time_as_folder()
newsList = bing.news_category_trending(ChinaCategory.ScienceAndTechnology.value, Market.China.value)
director.news2Video(newsList[2], folderPath)


