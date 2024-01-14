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
    "use_ocr":True,
    "use_image_in_webpage": True
}))

folderPath = current_time_as_folder()
# director.webpage2Video("https://culture.ifeng.com/c/8DNrjMVdo30", folderPath)

enrich = {
  "clips": [
    {
      "caption": "大家好，我是你们的网络达人小易！今天我要来和大家分享一篇来自凤凰网的影评——《四海》口碑崩塌：原本它真的可以很动人。\n",
      "imagePath": "output/1705259663207175000/web-content/image_5.jpg",
      "imageInfo": {
        "path": "output/1705259663207175000/web-content/image_5.jpg",
        "raw_description": "电影《四海》官方海报。",
        "ai_description": "蒉 OMLI HOOLS RUSHIN 憩褰 周 奇   9 0淘 蓠 嚣鲨 綮 囊黛 暴 正 食 乔 蕾 甓 蕴鞲",
        "provider": ""
      },
      "audioPath": "output/1705259663207175000/audio-0.wav",
      "audioInfo": {
        "audio_duration": 11.387
      }
    },
    {
      "caption": "很明显的，随着豆瓣评分5.6的发布，韩寒导演的《四海》已经锁定了2022年春节档口碑垫底的电影之一的位置。该电影刻画了小镇青年男女吴仁耀（刘昊然饰）和周欢颂（刘浩存饰）的爱情故事，两人在一个乌托邦式的海岛上相知相熟，暗生情愫，又因意外离开故乡、远赴广州谋生。而在这座大城市，他们承受的压力和挑战让这部电影染上了悲剧的色彩。\n",
      "imagePath": "output/1705259663207175000/web-content/image_5.jpg",
      "imageInfo": {
        "path": "output/1705259663207175000/web-content/image_5.jpg",
        "raw_description": "电影《四海》官方海报。",
        "ai_description": "蒉 OMLI HOOLS RUSHIN 憩褰 周 奇   9 0淘 蓠 嚣鲨 綮 囊黛 暴 正 食 乔 蕾 甓 蕴鞲",
        "provider": ""
      },
      "audioPath": "output/1705259663207175000/audio-1.wav",
      "audioInfo": {
        "audio_duration": 32.862
      }
    },
    {
      "caption": "但问题在于，评价《四海》的争议并不完全出在其悲剧色彩上，而在于韩寒试图在这部电影中做的太多，带有太多的复杂元素，导致电影给观众的体验变得混乱。就像评论中所说，什么都想要，结果就是什么也没得到。它没有专心地拍好剧中小人物的悲剧，而是试图用低级笑料和风格频转的方式来调整氛围，因此使得台词和剧情感觉断裂、观众的情绪在荒诞无厘头和严肃沉浸间反复横跳。\n",
      "imagePath": "output/1705259663207175000/web-content/image_5.jpg",
      "imageInfo": {
        "path": "output/1705259663207175000/web-content/image_5.jpg",
        "raw_description": "电影《四海》官方海报。",
        "ai_description": "蒉 OMLI HOOLS RUSHIN 憩褰 周 奇   9 0淘 蓠 嚣鲨 綮 囊黛 暴 正 食 乔 蕾 甓 蕴鞲",
        "provider": ""
      },
      "audioPath": "output/1705259663207175000/audio-2.wav",
      "audioInfo": {
        "audio_duration": 35.875
      }
    },
    {
      "caption": "最后，面对这样一部口碑崩塌的电影，我们不能只是抱怨和怀疑，更应该尝试深入理解和思考。当流量疲软、多样性减少、疫情重重的时代下，影片像是在试图寻找保持自我和迎合主流之间的一种平衡，并保留最后一点真诚。不幸的是，《四海》并没有找到这个平衡点，因此得到了现在的结果。但试图寻找这个平衡的尝试，或许对于我们自身，也有所启示和思考。\n",
      "imagePath": "output/1705259663207175000/web-content/image_5.jpg",
      "imageInfo": {
        "path": "output/1705259663207175000/web-content/image_5.jpg",
        "raw_description": "电影《四海》官方海报。",
        "ai_description": "蒉 OMLI HOOLS RUSHIN 憩褰 周 奇   9 0淘 蓠 嚣鲨 綮 囊黛 暴 正 食 乔 蕾 甓 蕴鞲",
        "provider": ""
      },
      "audioPath": "output/1705259663207175000/audio-3.wav",
      "audioInfo": {
        "audio_duration": 33.675
      }
    },
    {
      "caption": "这就是我今天要分享的内容，希望大家喜欢。欢迎留言和我一起交流哦！",
      "imagePath": "output/1705259663207175000/web-content/image_5.jpg",
      "imageInfo": {
        "path": "output/1705259663207175000/web-content/image_5.jpg",
        "raw_description": "电影《四海》官方海报。",
        "ai_description": "蒉 OMLI HOOLS RUSHIN 憩褰 周 奇   9 0淘 蓠 嚣鲨 綮 囊黛 暴 正 食 乔 蕾 甓 蕴鞲",
        "provider": ""
      },
      "audioPath": "output/1705259663207175000/audio-4.wav",
      "audioInfo": {
        "audio_duration": 7.037
      }
    }
  ]
}
director.enriched_script2video(enriched_script=enrich, output_dir="output/1705259663207175000")