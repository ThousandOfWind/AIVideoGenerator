import os
import sys
import logging
from moviepy.editor import AudioFileClip, TextClip, concatenate_audioclips, CompositeVideoClip, ImageSequenceClip, VideoFileClip, ImageClip
from workers.logisticsWorker import LogisticsWorker
from tools.tools import script2caption, saveToJson
from workers.AIWorker import AIWorker
from tools.openai_adapter import OpenaiAdapter
from tools.bing_search_adapter import BingSearchAdapter
from tools.speech_adapter import SpeechServiceAdapter, Gender

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,  # set to logging.DEBUG for verbose output
        format="[%(asctime)s] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p %Z")
logger = logging.getLogger(__name__)

class AIDirector:
    def __init__(self, oai: OpenaiAdapter, speech: SpeechServiceAdapter, bing:BingSearchAdapter, path_to_font:str):
        self.oai = oai
        self.speech = speech
        self.bing = bing
        self.font = path_to_font

    def new2script(self, news: dict, output_dir:str):
        logger.info("fetch website content, and writing script")

        content = LogisticsWorker.getWebPageContent(news['url'], os.path.join(output_dir, "news.html"))
        script = AIWorker.summaryNewsScript(
            news_provider=','.join([provider['name'] for provider in news['provider']]),
            news_title=news['name'],
            news_content=content,
            oai=self.oai
        )
        return script
    
    def useAvatarForText(self, caption:str, output_dir:str, index:int, clip:dict):
        if self.speech.speaker.gender == Gender.Female.value:
                avatar_path = os.path.join(output_dir, "avatar-{0}.webm".format(index))
                audio_info, _ = self.speech.text2avatar(
                    caption,
                    avatar_path
                )
                clip["avatarPath"] = avatar_path,
                clip["audioInfo"] = audio_info
                return clip
        image_info, image_path = AIWorker.drawAnchor(caption, output_dir, str(index), self.oai)
        clip["imagePath"] = image_path
        clip["imageInfo"] = image_info
        return clip


    def script2multimedia(self, script:str, news: dict, output_dir:str, with_avatar:bool = False):
        logger.info("Generate multimedia according to script")

        captions = script2caption(script)
        enriched_script = {
            "clips": []
        }
        for index, caption in enumerate(captions):
            clip = {
                "caption": caption
            }
            if index == 0:
                clip = self.useAvatarForText(caption, output_dir, index, clip)

            if not "imagePath" in clip:
                image_info, image_path = AIWorker.downloadOnlineImagesForCaption(
                    caption,
                    news_title=news['name'],
                    folder=output_dir,
                    file_suffix=str(index),
                    oai=self.oai,
                    bing=self.bing
                )
                clip["imagePath"] = image_path
                clip["imageInfo"] = image_info
                if image_path is None or image_info is None:
                    if with_avatar:
                        clip = self.useAvatarForText(caption, output_dir, index, clip)
                    else:
                        image_info, image_path = self.oai(caption, output_dir, str(index))
                        clip["imagePath"] = image_path
                        clip["imageInfo"] = image_info

            if not "audioInfo" in clip:
                audio_info, audio_path = self.speech.text2audio(
                    caption,
                    os.path.join(output_dir, "audio-{}.wav".format(index)),
                )
                clip["audioPath"] = audio_path
                clip["audioInfo"] = audio_info
            logger.info("Add clips", *clip)
            enriched_script['clips'].append(clip)
        saveToJson(os.path.join(output_dir, "enriched-script.json"), enriched_script)
        return enriched_script

    def enriched_script2video(self, enriched_script: dict, output_dir:str, shape:tuple=(720, 1280)):
        logger.info("Generate news video")

        audio_clips = []
        avatar_clips = []

        text_clips = []
        timer = 0
        image_clips = []
        for index, clip in enumerate(enriched_script["clips"]):
            audio_info = clip["audioInfo"]

            if ("avatarPath" in clip):
                audio_clips.append(AudioFileClip(clip["avatarPath"]))
                avatar_clip = VideoFileClip(clip["avatarPath"], has_mask=True) \
                        .resize(width=shape[0]) \
                        .set_start(timer) \
                        .set_end(timer + audio_info["audio_duration"]) \
                        .set_position(("right","bottom"))
                avatar_clips.append(avatar_clip)
            else:
                audio_clips.append(AudioFileClip(clip["audioPath"]))
            text_clip = TextClip(
                clip["caption"],
                fontsize=32,
                color='white',
                bg_color='black',
                font=self.font,
                size=(700, None),
                method='caption') \
                .set_start(timer) \
                .set_end(timer + audio_info["audio_duration"]) \
                .set_position((10, 900)) \
                .set_opacity(0.7)
            text_clips.append(text_clip)

            if 'imagePath' in clip:
                resize_img_path = os.path.join(
                    output_dir,
                    'image-{}-resized-watermark.{}'.format(index, str(clip['imagePath']).split('.')[-1]))
                LogisticsWorker.resize_image_watermark(image_path=clip['imagePath'], resize_img_path=resize_img_path, water_mark=clip['imageInfo']['provider'], shape=shape)
            
                image_clip = ImageClip(resize_img_path) \
                    .set_start(timer) \
                    .set_end(timer + audio_info["audio_duration"])
                image_clips.append(image_clip)
            
            timer += audio_info["audio_duration"]

        concated_audio_clip = concatenate_audioclips(audio_clips)

        final_clip = CompositeVideoClip([*image_clips, *avatar_clips, *text_clips], bg_color="#000000", use_bgclip=True)

        final_video = final_clip.set_audio(concated_audio_clip)
        output_file = os.path.join(output_dir, 'output.mp4')
        final_video.write_videofile(
            output_file,
            fps=30,
            codec='libx264',
            # # preset='ultrafast',
            audio_codec="aac",
            # threads=4
        )

        return output_file

    def news2Video(self, news: dict, output_dir:str, with_avatar:bool = False):
        logger.info("Start news video generator")
        script = self.new2script(news, output_dir)
        enriched_script = self.script2multimedia(script, news, output_dir, with_avatar)
        self.enriched_script2video(enriched_script, output_dir)



