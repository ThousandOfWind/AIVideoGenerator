import os
from tools.tools import getCurrentTimeAsFolder
from openai import AzureOpenAI
from tools.openai_adapter import OpenaiAdapter
from tools.speech_adapter import SpeechServiceAdapter, DefaultFemaleSpeaker
from tools.bing_search_adapter import BingSearchAdapter, ChinaCategory, Market
from workers.AIDirector import AIDirector, EditConfig
from dotenv import load_dotenv
import easyocr

load_dotenv()

client = AzureOpenAI(
    api_version="2023-12-01-preview",
    azure_endpoint=os.getenv('OPANAI_API_ENDPOINT'),
    api_key=os.getenv('OPANAI_API_KEY'),
)
oai = OpenaiAdapter(openai_client=client)
speech = SpeechServiceAdapter(os.getenv('SPEECH_HOST'), os.getenv('SPEECH_REGION'), os.getenv('SPEECH_KEY'), DefaultFemaleSpeaker)
bing = BingSearchAdapter(bing_search_api=os.getenv('BING_SEARCH_ENDPOINT'), bing_search_key=os.getenv('BING_SEARCH_KEY'))
config = EditConfig('/System/Library/Fonts/Supplemental/Arial Unicode.ttf', (720, 1280), True, False)
reader = easyocr.Reader(['ch_sim','en'])
director = AIDirector(oai, speech, bing, reader, config=config)

folderPath = getCurrentTimeAsFolder()
director.webpage2Video("https://culture.ifeng.com/c/8DNrjMVdo30", folderPath)