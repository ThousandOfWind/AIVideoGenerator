import os
from dotenv import load_dotenv
from VideoGen.tool import IOTool, OpenaiAdapter, SpeechServiceAdapter, DefaultFemaleSpeaker, BingSearchAdapter, ChinaCategory, Market
from VideoGen.workers import AIDirector
from VideoGen.config import DirectorConfig

load_dotenv()

oai = OpenaiAdapter.from_config({
    "type": 'AzureOpenAI',
    "api_key": os.getenv('OPANAI_API_KEY'),
    "endpoint": os.getenv('OPANAI_ENDPOINT'),
    "chat_model": "gpt-4-32k"
})
speech = SpeechServiceAdapter(os.getenv('SPEECH_HOST'), os.getenv('SPEECH_REGION'), os.getenv('SPEECH_KEY'), DefaultFemaleSpeaker)
bing = BingSearchAdapter(bing_search_api=os.getenv('BING_SEARCH_ENDPOINT'), bing_search_key=os.getenv('BING_SEARCH_KEY'))
config = DirectorConfig({
    "use_avatar": True,
    "use_image_in_webpage": True,
    "search_online_image": True,
    "script_seps": ('\n', '。', "？", "！"),
    "use_bgm": True
})
director = AIDirector(oai, speech, bing, config=config)

folderPath = IOTool.current_time_as_folder()
newsList = bing.news_category_trending(ChinaCategory.ScienceAndTechnology.value, Market.China.value)
director.news2Video(newsList[2], folderPath)


