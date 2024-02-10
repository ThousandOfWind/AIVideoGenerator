import logging
from io import BytesIO
import numpy as np
from typing import List
import matplotlib.colors as mcolors
from moviepy.editor import AudioFileClip, TextClip, CompositeVideoClip, CompositeAudioClip, VideoFileClip, ImageClip
from moviepy.audio.fx.volumex import volumex
from VideoGen.info import WebpageInfo, TableInfo, ImageInfo, VideoInfo
from VideoGen.tool import StringTool, OpenaiAdapter, SpeechServiceAdapter, BingSearchAdapter
from VideoGen.config import DirectorConfig
from VideoGen.workers.table_visualizer import TableVisualizer
from VideoGen.workers.AIWorker import AIWorker
from VideoGen.workers.information_collector import InformationCollector
from VideoGen.infra import LoggerFactory
from VideoGen.storage import BaseStorage
import VideoGen.prompt as PromptMap
from VideoGen.clip import MovieVideo, MovieAudio, MovieText, MovieImage, MovieComposite


class VideoDirector:
    def __init__(
            self, 
            oai: OpenaiAdapter, 
            speech: SpeechServiceAdapter, 
            bing:BingSearchAdapter, 
            storage:BaseStorage, 
            information: InformationCollector,
            table_visualizer: TableVisualizer,
            config: DirectorConfig=DirectorConfig(),
            logger: logging.Logger = None
    ):
        self.oai = oai
        self.speech = speech
        self.bing = bing
        self.storage: BaseStorage = storage
        self.table_visualizer = table_visualizer
        self.information = information
        self.config = config if config else DirectorConfig({})
        self.logger = logger if logger != None else LoggerFactory.get_logger(VideoDirector.__name__)


    def webpage2script(self, webpage_info: WebpageInfo):
        script = AIWorker.script_for_any_webpage(
            webpage_info.content,
            oai=self.oai
        )
        script = self.oai.ask_llm(webpage_info.content, PromptMap.commonWebPageScript)
        self.logger.info('script generate: ' + script)
        return script
    
    def direct(self, raw_script:str, title: str):
        captions = StringTool.script2caption(raw_script, sep_list=self.config.script_seps)

        images_to_be_selected = self.storage.query_image_metadata()
        tables_to_be_selected = self.storage.query_table_metadata()

        pointer = 0
        duration = 0
        text_channel: List[MovieText] = []
        avatar_channel: List[MovieVideo] = []
        illustration_channel: List[MovieImage|MovieVideo] = []
        audio_channel: List[MovieAudio|MovieVideo] = []
        bgm_channel: List[MovieAudio] = []
        shape = self.config.video_shape

        video_param = {
            "position": ("center"),
            "width": shape[0]
        }

        for caption in captions:
            if self.config.use_avatar:
                video_info = self.speech.text2avatar(caption)
                duration = video_info.duration
                movie_avatar = MovieVideo(
                    path=video_info.path,
                    duration=duration,
                    start=pointer,
                    **video_param
                )
                if(self.config.use_bgm):
                    movie_avatar.vol_scale = 2
                avatar_channel.append(movie_avatar)
                audio_channel.append(movie_avatar)
            else:
                audio_info = self.speech.text2audio(caption)
                duration = audio_info.duration
                movie_narrate = MovieAudio(
                    path=audio_info.path,
                    duration=duration,
                    start=pointer
                )
                if(self.config.use_bgm):
                    movie_narrate.vol_scale = 2
                audio_channel.append(audio_info)

            text_channel.append(
                MovieText(
                    caption, 
                    duration, 
                    pointer,
                    opacity=0.7,
                    position=(10, int(shape[1] * 0.85)),
                    bg_color='black',
                    fontsize=32,
                    color='white',
                    method='caption',
                    width=int(shape[0] * 0.9)
                ))
            
            image_param = {
                "duration": duration,
                "start": pointer,
                "position": ("center"),
                "width": shape[0]
            }

            lack_illustration_flag = True
            if lack_illustration_flag and (len(images_to_be_selected) + len(tables_to_be_selected)) > 0:
                selected_table_index, selected_image_index = self.__select_illustration_for_clip(
                    title=title,
                    caption=caption,
                    tables=tables_to_be_selected,
                    images=images_to_be_selected,
                )
                if selected_table_index >= 0:
                    table = tables_to_be_selected.pop(selected_table_index)
                    table_image_info = self.table_visualizer.draw_table(table)
                    illustration_channel.append(MovieImage(table_image_info.path, **image_param))
                    lack_illustration_flag = False
                elif selected_image_index >= 0:
                    image = images_to_be_selected.pop(selected_image_index)
                    illustration_channel.append(MovieImage(image.path, **image_param))
                    lack_illustration_flag = False
            if lack_illustration_flag and self.config.search_online_image:
                try:
                    image_search_text = AIWorker.get_image_search_query(caption, self.oai)
                    searched_images = self.bing.search_image(image_search_text)
                    searched_online_images = []
                    
                    for bing_img_info in searched_images[:self.config.search_online_image_top]:
                        image_info = self.information.get_image_from_url(bing_img_info['contentUrl'], bing_img_info['name'])
                        searched_online_images.append(image_info)
                    
                    _, selected_image_index = self.__select_illustration_for_clip(
                        title=title,
                        caption=caption,
                        tables=[],
                        images=searched_online_images,
                    )
                    if selected_image_index >= 0:
                        image = images_to_be_selected.pop(selected_image_index)
                        illustration_channel.append(MovieImage(image.path, **image_param))
                        lack_illustration_flag = False
                except Exception as e:
                    self.logger.error(e)

            if lack_illustration_flag and self.config.use_dalle:
                image_url = self.oai.draw_by_dalle(caption)
                image_info = self.information.get_image_from_url(image_url, caption)
                illustration_channel.append(MovieImage(image.path, **image_param))
                lack_illustration_flag = False

            pointer += duration

        if self.config.use_bgm:
            bgm_channel.append(MovieAudio(
                "docs/Neon Lights.mp3",
                pointer,
                0,
                0.5
            ))
        
        return MovieComposite(pointer, 0, title, audio_channels=[audio_channel, bgm_channel], video_channels=[illustration_channel, avatar_channel, text_channel])

    def concat_audio(self, movie_composite: MovieComposite):
        audio_clips = []
        for audio_channel in movie_composite.audio_channels:
            for audio in audio_channel:
                audio_clip = AudioFileClip(audio.path).set_start(audio.start).set_duration(audio.duration)
                if audio.vol_scale != 1:
                    audio_clip = audio_clip.fx(volumex, audio.vol_scale)
                audio_clips.append(audio_clip)
        concated_audio_clip = CompositeAudioClip(audio_clips)
        if movie_composite.vol_scale != 1:
            concated_audio_clip = concated_audio_clip.fx(volumex, movie_composite.vol_scale)
        
        return ConnectionAbortedError
    
    def concat_video(self, movie_composite: MovieComposite):
        shape = self.config.video_shape
        if movie_composite.bg_color == None:
            color = (0,0,0)
            canvas_img = np.zeros(shape=(shape[1], shape[0], 3), dtype=np.uint8)
        else:
            color_float = mcolors.to_rgb(movie_composite.bg_color)
            color = (max(0, min(255, int(c * 255))) for c in color_float)
            canvas_img = np.ones(shape=(shape[1], shape[0], 3), dtype=np.uint8) * color
        
        canvas = ImageClip(canvas_img).set_start(movie_composite.start).set_duration(movie_composite.duration)
        video_clips = [canvas]
        for video_channel in movie_composite.audio_channels:
            for video in video_channel:
                if isinstance(video, MovieText):
                    video_clip = TextClip(
                        video.text,
                        size=(video.width, None),
                        color=video.color,
                        bg_color=video.bg_color,
                        fontsize=video.fontsize,
                        font=self.config.path_to_font,
                        method='caption'
                    )
                else:
                    if isinstance(video, MovieImage):
                        video_clip = ImageClip(video.path)
                    else:
                        video_clip = VideoFileClip(video.path, audio=False)
                    if video.width != None:
                        video_clip = video_clip.resize(width=video.width)

                video_clip = video_clip.set_start(video.start).set_duration(video.duration)
                if video.position!= None:
                    video_clip = video_clip.set_position(video.position)
                if video.opacity != None:
                    video_clip = video_clip.set_opacity(video.opacity)
                
                video_clips.append(video_clip)
        final_clip = CompositeVideoClip(video_clips)
        return final_clip


    def export(self, movie_composite: MovieComposite):
        audio_clip = self.concat_audio(movie_composite)
        video_clip = self.concat_video(movie_composite)
        final_clip = video_clip.set_audio(audio_clip)
        hook = lambda filepath: final_clip.write_videofile(
            filepath,
            fps=30,
            codec='libx264',
            # # preset='ultrafast',
            audio_codec="aac",
            # threads=4
        )
        id, save_to = self.storage.save_video_hook(hook, 'wav')
        video_info = VideoInfo(id, save_to, movie_composite.name, duration=movie_composite.duration)
        self.storage.save_video_metadata(video_info)
        return video_info

    def __select_illustration_for_clip(self, title: str, caption:str, tables: List[TableInfo], images: List[ImageInfo]) -> (int, int):
        q = """Video title: {title}
Current caption: {caption}
Candidate list:
{table_list}\n{image_list}""".format(
            title=title, 
            caption=caption,
            table_list="\n".join(["{}. {}".format(index, tables.title) for index, tables in enumerate(tables)]),
            image_list="\n".join(["{}. {}".format(index + len(tables), image.description) for index, image in enumerate(images)]) )
        answer = self.oai.ask_llm(q, PromptMap.selectImageForCaption)
        if answer.find('NA') >= 0:
            return -1, -1
        try:
            select = int(answer)
            if select>= 0:
                if select < len(tables):
                    return select, -1
                if select < len(tables) + len(images):
                    image_index = select - len(tables)
                    return -1, image_index
        except Exception as e:
            self.logger.error("answer `{}` cannot be a legal index".format(answer))
        return -1, -1


            
            

            