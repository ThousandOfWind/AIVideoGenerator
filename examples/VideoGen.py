import os
import time
from dotenv import load_dotenv
from VideoGen.config import ManagerConfig, DirectorConfig, InformationConfig, AIConfig, SpeechConfig, SearchConfig
from VideoGen.workers import Manager
from VideoGen.storage import LocalStorage
from VideoGen.tool import ChinaCategory

load_dotenv()
storage = LocalStorage(os.path.join("output", str(time.time_ns())))
config = ManagerConfig({
    "director_config": DirectorConfig(),
    "information_config": InformationConfig(),
    "ai_config": AIConfig({
        "type": "AzureOpenAI",
        "api_version": "2023-12-01-preview",
        "api_key": os.getenv('OPANAI_API_KEY'), 
        "endpoint": os.getenv('OPANAI_ENDPOINT')
    }),
    "speech_config": SpeechConfig({
        "key": os.getenv('SPEECH_KEY'),
        "region": 'southeastasia'
    }),
    "search_config": SearchConfig({
        "bing_search_key": os.getenv('BING_SEARCH_KEY')
    })
})

manager = Manager(storage, config)
news = manager.search.news_category_trending(ChinaCategory.Auto.value)[0]
webpage_info = manager.information_collector.get_webpage(news['url'])
script = manager.video_director.webpage2script(webpage_info)
draft_video = manager.video_director.direct(script, webpage_info.name)
output_video_info = manager.video_director.export(draft_video)

