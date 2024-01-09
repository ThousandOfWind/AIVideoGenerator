import os
from moviepy.editor import AudioFileClip, TextClip, concatenate_audioclips, CompositeVideoClip, ImageSequenceClip, VideoFileClip, ImageClip
from logisticsWorker import LogisticsWorker
from tools.tools import createFolderIfNotExist, script2caption, saveToJson
from AIWorker import AIWorker
from tools.openai_adapter import OpenaiAdapter
from tools.bing_search_adapter import BingSearchAdapter
from tools.speech_adapter import SpeechServiceAdapter

class AIDirector:
    def __init__(self, oai: OpenaiAdapter, speech: SpeechServiceAdapter, bing:BingSearchAdapter, path_to_font:str):
        self.oai = oai
        self.speech = speech
        self.bing = bing
        self.font = path_to_font

    def new2script(self, news: dict, output_dir:str):
        print("fetch website content, and writing script")

        content = LogisticsWorker.getWebPageContent(news['url'], os.path.join(output_dir, "news.html"))
        script = AIWorker.summaryNewsScript(
            news_provider=','.join([provider['name'] for provider in news['provider']]),
            news_title=news['name'],
            news_content=content,
            oai=self.oai
        )
        return script

    def script2multimedia(self, script:str, news: dict, output_dir:str, with_avatar:bool = False):
        print("Generate multimedia according to script")

        captions = script2caption(script)
        enriched_script = {
            "clips": []
        }
        for index, caption in enumerate(captions):
            image_info, image_path = AIWorker.downloadOnlineImagesForCaption(
                caption,
                news_title=news['name'],
                folder=output_dir,
                file_suffix=str(index),
                oai=self.oai,
                bing=self.bing
            )
            if image_path is None or image_info is None:
                image_info, image_path = AIWorker.drawImage(caption, output_dir, str(index), self.oai)
            
            if with_avatar:
                audio_info, avatar_path = self.speech.text2avatar(
                    caption,
                    os.path.join(output_dir, "avatar-{}.webm".format(index))
                )
                enriched_script['clips'].append({
                    "caption": caption,
                    "imagePath": image_path,
                    "avatarPath": avatar_path,
                    "imageInfo": image_info,
                    "audioInfo": audio_info,
                })
            else:      
                audio_info, audio_path = self.speech.text2audio(
                    caption,
                    os.path.join(output_dir, "audio-{}.wav".format(index)),
                )
                enriched_script['clips'].append({
                    "caption": caption,
                    "imagePath": image_path,
                    "audioPath": audio_path,
                    "imageInfo": image_info,
                    "audioInfo": audio_info,
                })
        saveToJson(os.path.join(output_dir, "enriched-script.json"), enriched_script)
        return enriched_script

    def enriched_script2video(self, enriched_script: dict, output_dir:str):
        print("Generate news video")

        audio_clips = []
        avatar_clips = []

        text_clips = []
        timer = 0
        image_paths = []
        for index, clip in enumerate(enriched_script["clips"]):
            audio_info = clip["audioInfo"]

            if ("avatarPath" in clip):
                audio_clips.append(AudioFileClip(clip["avatarPath"]))
                avatar_clip = VideoFileClip(clip["avatarPath"], has_mask=True) \
                        .resize(0.5) \
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
                .set_position((10, 800)) \
                .set_opacity(0.7)
            text_clips.append(text_clip)
            timer += audio_info["audio_duration"]

            resize_img_path = os.path.join(
                output_dir,
                'image-{}-resized-watermark.{}'.format(index, str(clip['imagePath']).split('.')[-1]))
            LogisticsWorker.resize_image_watermark(image_path=clip['imagePath'], resize_img_path=resize_img_path, water_mark=clip['imageInfo']['provider'])
            image_paths.append(resize_img_path)
        concated_audio_clip = concatenate_audioclips(audio_clips)

        imageClip = ImageSequenceClip(image_paths,
                                      durations=[clip["audioInfo"]["audio_duration"] for clip in
                                                 enriched_script["clips"]])

        final_clip = CompositeVideoClip([imageClip, *avatar_clips, *text_clips], bg_color=None, use_bgclip=True)

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
        print("Start news video generator")
        createFolderIfNotExist(output_dir)
        script = self.new2script(news, output_dir)
        enriched_script = self.script2multimedia(script, news, output_dir, with_avatar)
        self.enriched_script2video(enriched_script, output_dir)



