from abc import abstractmethod, ABCMeta
from typing import List, Tuple
from azure.cognitiveservices.speech import AudioDataStream
from VideoGen.info import WebpageInfo, ImageInfo, TableInfo, AudioInfo, VideoInfo

class BaseStorage(meteaclass=ABCMeta):
    def __init__(self, index:str):
        self.index = index
    
    @abstractmethod
    def save_webpage_content(self, content:bytes) -> Tuple[str, str]: pass
    @abstractmethod
    def save_webpage_metadata(self, webpage_info: WebpageInfo): pass
    @abstractmethod
    def get_webpage_metadata(self, id:str) -> WebpageInfo: pass
    @abstractmethod
    def query_webpage_metadata(self, query:str = None) -> List[WebpageInfo]: pass
    
    @abstractmethod
    def save_image_content(self, content:bytes, type_suffix:str) -> Tuple[str, str]:pass
    @abstractmethod
    def save_image_metadata(self, image_info: ImageInfo): pass
    @abstractmethod
    def get_image_metadata(self, id:str) -> ImageInfo: pass
    @abstractmethod
    def query_image_metadata(self, query:str = None) -> List[ImageInfo]: pass

    @abstractmethod
    def save_table_content(self, content:bytes) -> Tuple[str, str]:pass
    @abstractmethod
    def save_table_metadata(self, table_info: TableInfo):pass
    @abstractmethod
    def get_table_metadata(self, id:str) -> TableInfo: pass
    @abstractmethod
    def query_table_metadata(self, query:str = None) -> List[TableInfo]: pass

    @abstractmethod
    def save_audio_content(self, stream: AudioDataStream) -> Tuple[str, str]:pass
    @abstractmethod
    def save_audio_metadata(self, audio_info: AudioInfo):pass
    @abstractmethod
    def get_audio_metadata(self, id:str) -> AudioInfo: pass
    @abstractmethod
    def query_audio_metadata(self, query:str = None) -> List[AudioInfo]: pass

    @abstractmethod
    def save_video_content(self, content:bytes, type_suffix:str) -> Tuple[str, str]:pass
    @abstractmethod
    def save_video_metadata(self, audio_info: VideoInfo):pass
    @abstractmethod
    def get_video_metadata(self, id:str) -> VideoInfo: pass
    @abstractmethod
    def query_video_metadata(self, query:str = None) -> List[VideoInfo]: pass
    @abstractmethod
    def save_video_hook(self, hook:function, type_suffix:str) -> Tuple[str, str]:pass
