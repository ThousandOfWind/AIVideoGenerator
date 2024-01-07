import json
import logging
import sys
import time
import requests
import datetime
from enum import Enum
import azure.cognitiveservices.speech as speechsdk
from tools.tools import download

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,  # set to logging.DEBUG for verbose output
        format="[%(asctime)s] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p %Z")
logger = logging.getLogger(__name__)


class Gender(Enum):
    Male = "male"
    Female = "female"

class Speaker:
    def __init__(self, language:str, name: str, gender: str, tone_type: str='Neural'):
        self.language = language
        self.name = name
        self.tone_type = tone_type
        self.gender = gender
    
    @property
    def speech_synthesis_voice_name(self):
        return f'{self.language}-{self.name}{self.tone_type}'

DefaultMaleSpeaker = Speaker("zh-CN", "Yunyang", Gender.Male.value)
DefaultFemaleSpeaker = Speaker("zh-CN", "Xiaoqiu", Gender.Female.value)


class SpeechServiceAdapter:
    def __init__(self, host:str, region:str, key:str, speaker:Speaker):
        self.host = host
        self.region = region
        self.key = key
        self.speaker = speaker
        self.speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
        self.speech_config.speech_synthesis_voice_name = speaker.speech_synthesis_voice_name
    
    def text2audio(self, text, audio_path:str):
        # use the default speaker as audio output.
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_config)

        result = speech_synthesizer.speak_text(text)
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text [{}]".format(text))
            stream = speechsdk.AudioDataStream(result)
            stream.save_to_wav_file(audio_path)
            return {"audio_duration": result.audio_duration.seconds}, audio_path

        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))

        return None, None
    
    def text2avatar(self, text, avatar_path:str):
        job_id = self.submit_synthesis(text=text)
        max_try = 20
        result_info = None
        if job_id is not None:
            while max_try > 0:
                status, result_info = self.get_synthesis(job_id)
                if status == 'Succeeded':
                    logger.info('batch avatar synthesis job succeeded')
                    break
                elif status == 'Failed':
                    logger.error('batch avatar synthesis job failed')
                    break
                else:
                    logger.info(f'batch avatar synthesis job is still running, status [{status}]')
                    time.sleep(5)
                max_try -= 1
        if result_info:
            url = result_info["outputs"]["result"]
            download(avatar_path, url)
            return {
                "audio_duration": datetime.timedelta(microseconds= result_info["properties"]["durationInTicks"]/10).total_seconds()
            }, avatar_path
        else:
            raise "Fail to generate a avatar video!"
        
    
    def submit_synthesis(self, text:str):
        url = f'https://{self.region}.{self.host}/api/texttospeech/3.1-preview1/batchsynthesis/talkingavatar'
        header = {
            'Ocp-Apim-Subscription-Key': self.key,
            'Content-Type': 'application/json'
        }

        payload = {
            'displayName': 'videoGenerator',
            'description': text,
            "textType": "PlainText",
            'synthesisConfig': {
                "voice": self.speaker.speech_synthesis_voice_name,
            },
            # Replace with your custom voice name and deployment ID if you want to use custom voice.
            # Multiple voices are supported, the mixture of custom voices and platform voices is allowed.
            # Invalid voice name or deployment ID will be rejected.
            'customVoices': {
                # "YOUR_CUSTOM_VOICE_NAME": "YOUR_CUSTOM_VOICE_ID"
            },
            "inputs": [
                {
                    "text": text,
                },
            ],
            "properties": {
                "customized": False, # set to True if you want to use customized avatar
                "talkingAvatarCharacter": "lisa",  # talking avatar character
                "talkingAvatarStyle": "graceful-sitting",  # talking avatar style, required for prebuilt avatar, optional for custom avatar
                "videoFormat": "webm",  # mp4 or webm, webm is required for transparent background
                "videoCodec": "vp9",  # hevc, h264 or vp9, vp9 is required for transparent background; default is hevc
                "subtitleType": "soft_embedded",
                "backgroundColor": "transparent",
            }
        }

        response = requests.post(url, json.dumps(payload), headers=header)
        if response.status_code < 400:
            logger.info('Batch avatar synthesis job submitted successfully')
            logger.info(f'Job ID: {response.json()["id"]}')
            return response.json()["id"]
        else:
            logger.error(f'Failed to submit batch avatar synthesis job: {response.text}')


    def get_synthesis(self, job_id:str):
        url = f'https://{self.region}.{self.host}/api/texttospeech/3.1-preview1/batchsynthesis/talkingavatar/{job_id}'
        header = {
            'Ocp-Apim-Subscription-Key': self.key
        }
        response = requests.get(url, headers=header)
        if response.status_code < 400:
            logger.debug('Get batch synthesis job successfully')
            logger.debug(response.json())
            if response.json()['status'] == 'Succeeded':
                logger.info(f'Batch synthesis job succeeded, download URL: {response.json()["outputs"]["result"]}')
                logger.info(f'response content: {response.text}')

                return response.json()['status'], response.json()

            return response.json()['status'], None
        else:
            logger.error(f'Failed to get batch synthesis job: {response.text}')
            return 'Inprogress', None
