import os
import sys
import logging
from moviepy.editor import AudioFileClip, TextClip, concatenate_audioclips, CompositeVideoClip, ImageSequenceClip, VideoFileClip, ImageClip
from workers.webWorker import WebWorker
from tools.tools import script2caption, save_to_json, save_to_txt
from workers.AIWorker import AIWorker
from tools.openai_adapter import OpenaiAdapter
from tools.bing_search_adapter import BingSearchAdapter
from tools.speech_adapter import SpeechServiceAdapter, Gender
from workers.imageWorker import ImageWorker
from easyocr import Reader
from configs.directorConfig import DirectorConfig
from models.webpage import WebpageInfo

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,  # set to logging.DEBUG for verbose output
        format="[%(asctime)s] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p %Z")
logger = logging.getLogger(__name__)

class AIDirector:
    def __init__(self, oai: OpenaiAdapter, speech: SpeechServiceAdapter, bing:BingSearchAdapter, ocr_reader: Reader = None, config: DirectorConfig=None):
        self.oai = oai
        self.speech = speech
        self.bing = bing
        self.ocr_reader = ocr_reader
        self.config = config if config else DirectorConfig({})
        if self.config.use_ocr and self.ocr_reader is None:
            logger.warning("ocr enabled, but ocr reader is none! It may cause error later")
    
    def webpage2script(self, webpage_info: WebpageInfo, output_dir:str, config: DirectorConfig=None):
        config = config if config else self.config
        script = AIWorker.script_for_any_webpage(
            webpage_info.content,
            oai=self.oai
        )
        save_to_txt(
            file_name=os.path.join(output_dir, 'script.txt'),
            content=script
        )
        return script
    
    
    def get_avatar(self, caption:str, output_dir:str, index:int, clip:dict):
        if self.speech.speaker.gender == Gender.Female.value:
                avatar_path = os.path.join(output_dir, "avatar-{0}.webm".format(index))
                audio_info, avatar_path = self.speech.text2avatar(
                    caption,
                    avatar_path
                )
                logger.info("avatar_path " + str(avatar_path))
                clip["avatarPath"] = avatar_path
                clip["audioInfo"] = audio_info
                image_info, image_path = ImageWorker.drawBackgroundImage(folder=output_dir)
                clip["imagePath"] = image_path
                clip["imageInfo"] = image_info
                return clip
        image_info, image_path = ImageWorker.drawAnchor(caption, output_dir, str(index), self.oai)
        clip["imagePath"] = image_path
        clip["imageInfo"] = image_info
        return clip


    def webpage_script2multimedia(self, script:str, webpage_info: WebpageInfo, output_dir:str, config: DirectorConfig=None):
        config = config if config else self.config

        captions = script2caption(script, sep_list=tuple('\n'))

        if len(captions) < 2:
            raise Exception('num caption less than 2')
        else:
            logger.info(str(len(captions) )+ ' captions start find multimedia resource')
        
        enriched_script = {
            "clips": []
        }
        images_to_be_selected = webpage_info.images[:]

        for index, caption in enumerate(captions):
            clip = {
                "caption": caption
            }
            if config.use_image_in_webpage and len(images_to_be_selected) > 0:
                selected = AIWorker.select_image_for_clip(
                    title=webpage_info.title_text,
                    script=caption,
                    images=images_to_be_selected,
                    oai=self.oai
                )
                if selected > 0:
                    clip["imagePath"] = images_to_be_selected[selected].path
                    clip["imageInfo"] = images_to_be_selected[selected].toJSON()
                    images_to_be_selected.pop(selected)
            
            if not "imagePath" in clip or not clip["imagePath"]:
                image_info= AIWorker.download_online_image_for_clip(
                    caption,
                    news_title=webpage_info.title_text,
                    folder=output_dir,
                    file_suffix=str(index),
                    oai=self.oai,
                    bing=self.bing,
                    ocr_reader=self.ocr_reader if config.use_ocr else None
                )
                if image_info:
                    clip["imagePath"] = image_info.path 
                    clip["imageInfo"] = image_info.toJSON()
            if (not "imagePath" in clip or not clip["imagePath"]) and config.use_avatar:
                clip = self.get_avatar(caption, output_dir, index, clip)
            
            if (not "imagePath" in clip or not clip["imagePath"]) and config.use_dalle:
                image_info, image_path = self.oai.draw(caption, output_dir, str(index))
                clip["imagePath"] = image_path
                clip["imageInfo"] = image_info
            
            if not "imagePath" in clip or not clip["imagePath"] :
                image_info, image_path = ImageWorker.drawBackgroundImage(output_dir, config.video_shape)
                clip["imagePath"] = image_path
                clip["imageInfo"] = image_info

            if not "audioInfo" in clip or not clip["audioInfo"]:
                audio_info, audio_path = self.speech.text2audio(
                    caption,
                    os.path.join(output_dir, "audio-{}.wav".format(index)),
                )
                clip["audioPath"] = audio_path
                clip["audioInfo"] = audio_info
            logger.info("Add clips " + str(clip))
            enriched_script['clips'].append(clip)
        save_to_json(
            file_name=os.path.join(output_dir, 'enrich.json'),
            content=enriched_script
        )
        return enriched_script


    def enriched_script2video(self, enriched_script: dict, output_dir:str, config: DirectorConfig=None):
        config = config if config else self.config
        shape = config.video_shape
        logger.info("Generate news video")

        audio_clips = []
        avatar_clips = []

        text_clips = []
        timer = 0
        image_clips = []
        for index, clip in enumerate(enriched_script["clips"]):
            audio_info = clip["audioInfo"]

            if ("avatarPath" in clip and clip["avatarPath"]):
                audio_clips.append(AudioFileClip(clip["avatarPath"]))
                avatar_clip = VideoFileClip(clip["avatarPath"], has_mask=True) \
                        .resize(width=shape[0]) \
                        .set_start(timer) \
                        .set_end(timer + audio_info["audio_duration"]) \
                        .set_position(("center"))
                avatar_clips.append(avatar_clip)
            else:
                audio_clips.append(AudioFileClip(clip["audioPath"]))
            text_clip = TextClip(
                clip["caption"],
                fontsize=32,
                color='white',
                bg_color='black',
                font=self.config.path_to_font,
                size=(int(shape[0] * 0.9), None),
                method='caption') \
                .set_start(timer) \
                .set_end(timer + audio_info["audio_duration"]) \
                .set_position((10, int(shape[1] * 0.85))) \
                .set_opacity(0.7)
            text_clips.append(text_clip)

            if 'imagePath' in clip and clip['imagePath']:
                resize_img_path = ImageWorker.resize_image_watermark(
                    image_path=clip['imagePath'], 
                    output_dir=output_dir, 
                    image_suffix=str(index), 
                    water_mark=clip['imageInfo']['provider'], 
                    shape=shape)
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

    def news2Video(self, news: dict, output_dir:str, config: DirectorConfig=None):
        config = config if config else self.config
        webpage_info = WebWorker.getWebPageContentDeep(
            url=news['url'], 
            output_dir=output_dir, 
            ocr_reader=self.ocr_reader if config.use_ocr else None)
        script = AIWorker.script_for_news(
            news_provider=','.join([provider['name'] for provider in news['provider']]),
            news_title=news['name'],
            news_content=webpage_info.content,
            oai=self.oai
        )
        enriched_script = self.webpage_script2multimedia(
            script=script,
            webpage_info=webpage_info,
            output_dir=output_dir
        )
        self.enriched_script2video(enriched_script, output_dir)


    def webpage2Video(self, url: str, output_dir:str, config: DirectorConfig=None):
        config = config if config else self.config
        logger.info("Start webpage video generator for " + url)

        webpage_info = WebWorker.getWebPageContentDeep(
            url=url, 
            output_dir=output_dir, 
            ocr_reader=self.ocr_reader if config.use_ocr else None)
        script = self.webpage2script(
            webpage_info=webpage_info,
            output_dir=output_dir,
            config=config
        )
        enriched_script = self.webpage_script2multimedia(
            script=script,
            webpage_info=webpage_info,
            output_dir=output_dir
        )
        self.enriched_script2video(enriched_script, output_dir)



