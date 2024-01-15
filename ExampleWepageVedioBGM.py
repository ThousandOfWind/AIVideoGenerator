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
    'use_bgm': True
}))

director.enriched_script2video(
    enriched_script={
        "bgm": "docs/Neon Lights.mp3",
        "clips": [
            {
            "caption": "划重点，我们即将迈向新的音频技术巅峰。",
            "avatarPath": "output/1705333707072025000/avatar-0.webm",
            "audioInfo": {
                "audio_duration": 4.19
            },
            "imagePath": "output/1705333707072025000/blank_image.jpg",
            "imageInfo": {
                "provider": "",
                "name": "blank background",
                "encodingFormat": "jpeg"
            }
            },
            {
            "caption": "来自森海塞尔的TCC M天花阵列麦克风，现已与快思聪Crestron Automate VX的语音激活麦克风追踪方案成功集成。",
            "imagePath": "output/1705333707072025000/online-image-1-0.png",
            "imageInfo": {
                "path": "output/1705333707072025000/online-image-1-0.png",
                "raw_description": "森海塞尔推出中型空间解决方案TCC M天花阵列麦克风产品-爱云资讯",
                "ai_description": "",
                "provider": "www.icloudnews.net"
            },
            "audioPath": "output/1705333707072025000/audio-1.wav",
            "audioInfo": {
                "audio_duration": 11.387
            }
            },
            {
            "caption": "Automate VX技术提供专业级别的相机切换，实现高水平会议体验。",
            "imagePath": "output/1705333707072025000/online-image-2-1.jpeg",
            "imageInfo": {
                "path": "output/1705333707072025000/online-image-2-1.jpeg",
                "raw_description": "让会议体验提升到新高度—奥尼电子4K超高清视频会议摄像头-深圳奥尼电子股份有限公司",
                "ai_description": "",
                "provider": "5b0988e595225.cdn.sohucs.com"
            },
            "audioPath": "output/1705333707072025000/audio-2.wav",
            "audioInfo": {
                "audio_duration": 6.925
            }
            },
            {
            "caption": "尤其是，当加上TCC M天花阵列麦克风，确保了会议的包容性。",
            "imagePath": "output/1705333707072025000/online-image-3-0.png",
            "imageInfo": {
                "path": "output/1705333707072025000/online-image-3-0.png",
                "raw_description": "森海塞尔推出中型空间解决方案TCC M天花阵列麦克风产品-爱云资讯",
                "ai_description": "",
                "provider": "www.icloudnews.net"
            },
            "audioPath": "output/1705333707072025000/audio-3.wav",
            "audioInfo": {
                "audio_duration": 6.562
            }
            },
            {
            "caption": "难道在未来，我们对老式“手持麦克风”将成为历史？\n",
            "imagePath": "output/1705333707072025000/online-image-4-2.png",
            "imageInfo": {
                "path": "output/1705333707072025000/online-image-4-2.png",
                "raw_description": "SHURE手持麦克风BLX-24/SM58视频介绍_SHURE手持麦克风BLX-24/SM58功能演示视频-苏宁易购",
                "ai_description": "",
                "provider": "imgservice.suning.cn"
            },
            "audioPath": "output/1705333707072025000/audio-4.wav",
            "audioInfo": {
                "audio_duration": 4.725
            }
            },
            {
            "caption": "麦克风配合摄像头，能准确追踪房间内的发言者，更妙的是，它可以消除摄像头运动时引发的晃动和扰动。",
            "imagePath": "output/1705333707072025000/online-image-5-2.jpg",
            "imageInfo": {
                "path": "output/1705333707072025000/online-image-5-2.jpg",
                "raw_description": "中大腾创MG1000语音智能跟踪视频会议摄像头一体机 4K超高清网络会议摄像机内置全向拾音麦克风高保真扬声器_虎窝淘",
                "ai_description": "",
                "provider": "img.alicdn.com"
            },
            "audioPath": "output/1705333707072025000/audio-5.wav",
            "audioInfo": {
                "audio_duration": 10.05
            }
            },
            {
            "caption": "难道是不是我们无处不在的“讲话者追踪”即将上线？\n",
            "imagePath": "output/1705333707072025000/online-image-6-0.png",
            "imageInfo": {
                "path": "output/1705333707072025000/online-image-6-0.png",
                "raw_description": "视频会议怎么实现自动追踪发言人？网牛智能办公提供解决方案",
                "ai_description": "",
                "provider": "www.wnkj88.com"
            },
            "audioPath": "output/1705333707072025000/audio-6.wav",
            "audioInfo": {
                "audio_duration": 4.537
            }
            },
            {
            "caption": "结合Automate VX的解决方案，多摄像头能无缝协同，随着房间内的对话来回切换，确保发言者的声音始终清晰传达。",
            "avatarPath": "output/1705333707072025000/avatar-7.webm",
            "audioInfo": {
                "audio_duration": 11.29
            },
            "imagePath": "output/1705333707072025000/blank_image.jpg",
            "imageInfo": {
                "provider": "",
                "name": "blank background",
                "encodingFormat": "jpeg"
            }
            },
            {
            "caption": "看来络绎不绝的视频会议将成为过去，我们在迈向更加无缝、包容、且成果领先的会议体验。",
            "avatarPath": "output/1705333707072025000/avatar-8.webm",
            "audioInfo": {
                "audio_duration": 8.82
            },
            "imagePath": "output/1705333707072025000/blank_image.jpg",
            "imageInfo": {
                "provider": "",
                "name": "blank background",
                "encodingFormat": "jpeg"
            }
            },
            {
            "caption": "但会是怎样一幅图景，我们又能如何应对这一变量？\n",
            "imagePath": "output/1705333707072025000/online-image-9-15.png",
            "imageInfo": {
                "path": "output/1705333707072025000/online-image-9-15.png",
                "raw_description": "【保险科普】面对未知风险，我们可以如何应对？ - 知乎",
                "ai_description": "",
                "provider": "pic3.zhimg.com"
            },
            "audioPath": "output/1705333707072025000/audio-9.wav",
            "audioInfo": {
                "audio_duration": 4.487
            }
            },
            {
            "caption": "为此，“拭目以待”暂且放下，让我们更多思索下一步的可能性。",
            "imagePath": "output/1705333707072025000/online-image-10-16.jpg",
            "imageInfo": {
                "path": "output/1705333707072025000/online-image-10-16.jpg",
                "raw_description": "商业照片展示了解下一步的动作思索Trivia集思广益探险游戏Trivi高清图片下载-正版图片505847706-摄图网",
                "ai_description": "",
                "provider": "img95.699pic.com"
            },
            "audioPath": "output/1705333707072025000/audio-10.wav",
            "audioInfo": {
                "audio_duration": 5.687
            }
            },
            {
            "caption": "缤纷多彩的技术时代总是亟待我们的探索，是惊喜，也是挑战。",
            "imagePath": "output/1705333707072025000/online-image-11-3.png",
            "imageInfo": {
                "path": "output/1705333707072025000/online-image-11-3.png",
                "raw_description": "未来科技的探索者|平面|海报|wyrapple - 原创作品 - 站酷 (ZCOOL)",
                "ai_description": "",
                "provider": "img.zcool.cn"
            },
            "audioPath": "output/1705333707072025000/audio-11.wav",
            "audioInfo": {
                "audio_duration": 6.075
            }
            }
        ]
        },
        output_dir="output/1705333707072025000",
)