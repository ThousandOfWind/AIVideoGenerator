import json
import logging
import time
import requests
import datetime
from collections import namedtuple
import azure.cognitiveservices.speech as speechsdk
from VideoGen.storage import BaseStorage
from VideoGen.infra import LoggerFactory
from VideoGen.config import SpeechConfig
from VideoGen.info import AudioInfo, VideoInfo

SpeechResult = namedtuple('SpeechResult', ['video, audio'])

class SpeechServiceAdapter:
    def __init__(
            self, 
            storage:BaseStorage, 
            config: SpeechConfig, 
            logger: logging.Logger = None
    ):
        self.config = config
        self.storage: BaseStorage = storage
        self.logger: logging.Logger = logger or LoggerFactory.get_logger(SpeechServiceAdapter.__name__)
    
    @property
    def speech_sdk_config(self):
        speech_sdk_config = speechsdk.SpeechConfig(subscription=self.config.key, region=self.config.region)
        speech_sdk_config.speech_synthesis_voice_name = self.config.speech_synthesis_voice_name
        return speech_sdk_config
    
    def text2audio(self, text):
        # use the default speaker as audio output.
        speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.speech_sdk_config)

        result = speech_synthesizer.speak_text(text)
        # Check result
        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            stream = speechsdk.AudioDataStream(result)
            # stream.save_to_wav_file(audio_path)
            id, save_to = self.storage.save_audio_content(stream)
            audio = AudioInfo(id, save_to, text, result.audio_duration.total_seconds())
            return audio
        
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            self.logger.error("Speech synthesis canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                self.logger.error("Error details: {}".format(cancellation_details.error_details))

        raise Exception("Fail to generate a audio! ")
    
    def text2avatar(self, text):
        job_id = self.submit_synthesis(text=text)
        max_try = 20
        result_info = None
        if job_id is not None:
            while max_try > 0:
                status, result_info = self.get_synthesis(job_id)
                if status == 'Succeeded':
                    break
                elif status == 'Failed':
                    self.logger.error('batch avatar synthesis job failed')
                    break
                else:
                    time.sleep(5)
                max_try -= 1
        if result_info:
            url = result_info["outputs"]["result"]
            duration = datetime.timedelta(microseconds= result_info["properties"]["durationInTicks"]/10).total_seconds()
            
            id, save_to = self.storage.save_video_content(url)
            video = VideoInfo(id, save_to, text, duration)
            return video
        else:
            raise Exception("Fail to generate a avatar video! " + str(result_info))
        
    
    def submit_synthesis(self, text:str):
        url = f'https://{self.config.region}.{self.config.host}/api/texttospeech/3.1-preview1/batchsynthesis/talkingavatar'
        header = {
            'Ocp-Apim-Subscription-Key': self.config.key,
            'Content-Type': 'application/json'
        }

        payload = {
            'displayName': 'videoGenerator',
            'description': text,
            "textType": "PlainText",
            'synthesisConfig': {
                "voice": self.config.speech_synthesis_voice_name,
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
            return response.json()["id"]
        else:
            self.logger.error(f'Failed to submit batch avatar synthesis job: {response.text}')


    def get_synthesis(self, job_id:str):
        url = f'https://{self.config.region}.{self.config.host}/api/texttospeech/3.1-preview1/batchsynthesis/talkingavatar/{job_id}'
        header = {
            'Ocp-Apim-Subscription-Key': self.key
        }
        response = requests.get(url, headers=header)
        if response.status_code < 400:
            if response.json()['status'] == 'Succeeded':
                return response.json()['status'], response.json()
            return response.json()['status'], None
        else:
            self.logger.error(f'Failed to get batch synthesis job: {response.text}')
            return 'Inprogress', None
