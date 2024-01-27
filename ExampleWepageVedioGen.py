import os
from tools.tools import current_time_as_folder
from openai import AzureOpenAI
from tools.openai_adapter import OpenaiAdapter
from tools.speech_adapter import SpeechServiceAdapter, DefaultFemaleSpeaker
from tools.bing_search_adapter import BingSearchAdapter
from workers.AIDirector import AIDirector
from dotenv import load_dotenv
import easyocr
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
reader = easyocr.Reader(['ch_sim','en'])
director = AIDirector(oai, speech, bing, reader, config=DirectorConfig({
    # "use_ocr":True,
    # "use_image_in_webpage": True
    'use_table_in_webpage': True
}))

output_dir = current_time_as_folder()
# director.webpage2Video("https://azure.microsoft.com/zh-cn/products/ai-services/?activetab=pivot:azureopenai%E6%9C%8D%E5%8A%A1tab", folderPath)

from workers.webWorker import WebWorker
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

