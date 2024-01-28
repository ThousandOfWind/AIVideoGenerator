import os
from dotenv import load_dotenv
import easyocr
from VideoGen.tool import IOTool, OpenaiAdapter, SpeechServiceAdapter, DefaultFemaleSpeaker, BingSearchAdapter, ChinaCategory, Market
from VideoGen.workers import AIDirector, WebWorker
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
reader = easyocr.Reader(['ch_sim','en'])
director = AIDirector(oai, speech, bing, reader, config=DirectorConfig({
    # "use_ocr":True,
    # "use_image_in_webpage": True
    'use_table_in_webpage': True
}))

output_dir = IOTool.current_time_as_folder()
# director.webpage2Video("https://azure.microsoft.com/zh-cn/products/ai-services/?activetab=pivot:azureopenai%E6%9C%8D%E5%8A%A1tab", folderPath)

webpage_info = WebWorker.get_enriched_webpage_info(
    url='https://learn.microsoft.com/en-us/azure/ai-services/openai/overview',
    output_dir=output_dir,
    table_oai=oai
)
script = director.webpage2script(
    webpage_info=webpage_info,
    output_dir=output_dir,
)
enriched_script = director.webpage_script2multimedia(
    script=script,
    webpage_info=webpage_info,
    output_dir=output_dir
)
director.enriched_script2video(enriched_script, output_dir)

