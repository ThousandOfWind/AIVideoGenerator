import os
import pickle
from collections import namedtuple
from typing import List, Tuple
from azure.cognitiveservices.speech import AudioDataStream
from VideoGen.storage.base import BaseStorage
from VideoGen.info import WebpageInfo, ImageInfo, TableInfo, AudioInfo, VideoInfo, BaseInfo
from VideoGen.clip import MovieComposite

TypeFolder = namedtuple('TypeFolder', ("content", "metadata"))
def get_type_folder(folder_name:str, type:str):
    return TypeFolder(
             os.path.join(folder_name, f"{type}-content"),
             os.path.join(folder_name, f"{type}-metadata")
    )

class LocalStorage(BaseStorage):
    @staticmethod
    def create_folder_if_not_exist(folder_name):
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

    @staticmethod
    def save_content(content:bytes, folder_name:str, type_suffix:str):
        count = len(os.listdir(folder_name))
        save_path = os.path.join(folder_name, "{}.{}".format(count, type_suffix))
        with open(save_path, 'wb') as f:
            f.write(content)
        return str(count), save_path
    
    def save_hook(hook, folder_name:str, type_suffix:str):
        count = len(os.listdir(folder_name))
        save_path = os.path.join(folder_name, "{}.{}".format(count, type_suffix))
        hook(save_path)
        return str(count), save_path
    
    @staticmethod
    def save_metadata(metadata: BaseInfo, folder_name:str):
        save_path = os.path.join(folder_name, "{}.pkl".format(metadata.id))
        with open(save_path, 'wb') as file:
            pickle.dump(metadata, file)

    @staticmethod
    def get_metadata(folder_name:str, id:str):
        save_path = os.path.join(folder_name, "{}.pkl".format(id))
        with open(save_path, 'rb') as file:
            return pickle.load(file)
        
    @staticmethod
    def get_all_metadata(folder_name:str):
        metadata_list = []
        for filename in os.listdir(folder_name):
            if filename.endswith('.pkl'):
                save_path = os.path.join(folder_name, filename)
                with open(save_path, 'r') as file:
                    metadata_list.append(pickle.load(file))
        return metadata_list

    def __init__(self, folder_name:str):
        BaseStorage.__init__(self, folder_name)
        self.webpage_folder = get_type_folder(self.index, 'webpages')
        self.image_folder = get_type_folder(self.index, 'images')
        self.table_folder = get_type_folder(self.index, 'tables')
        self.audio_folder = get_type_folder(self.index, 'audios')
        self.video_folder = get_type_folder(self.index, 'videos')

        for folder in [
            self.index,
            * self.webpage_folder,
            * self.image_folder,
            * self.table_folder,
            * self.audio_folder,
            * self.video_folder
        ]:
            LocalStorage.create_folder_if_not_exist(folder)
    
    def save_webpage_content(self, content:bytes):
        return LocalStorage.save_content(content, self.webpage_folder.content, 'html')
    
    def save_webpage_metadata(self, webpage_info: WebpageInfo):
        return LocalStorage.save_metadata(webpage_info, self.webpage_folder.metadata)

    def get_webpage_metadata(self, id:str) -> WebpageInfo: 
        return LocalStorage.get_metadata(self.webpage_folder.metadata, id)
    
    def query_webpage_metadata(self, query:str = None) -> List[WebpageInfo]: 
        return LocalStorage.get_all_metadata(self.webpage_folder.metadata)

    def save_image_content(self, content:bytes, type_suffix:str):
        return LocalStorage.save_content(content, self.image_folder.content, type_suffix)
    
    def save_image_metadata(self, image_info: ImageInfo):
        return LocalStorage.save_metadata(image_info, self.image_folder.metadata)
    
    def get_image_metadata(self, id:str) -> ImageInfo: 
        return LocalStorage.get_metadata(self.image_folder.metadata, id)
    
    def query_image_metadata(self, query:str = None) -> List[ImageInfo]: 
        return LocalStorage.get_all_metadata(self.image_folder.metadata)
    
    def save_table_content(self, content:bytes) -> Tuple[str, str]:
        return LocalStorage.save_content(content, self.table_folder.content, 'json')

    def save_table_metadata(self, table_info: TableInfo):
        return LocalStorage.save_metadata(table_info, self.table_folder.metadata)

    def get_table_metadata(self, id:str) -> TableInfo: 
        return LocalStorage.get_metadata(self.table_folder.metadata, id)

    def query_table_metadata(self, query:str = None) -> List[TableInfo]: 
        return LocalStorage.get_all_metadata(self.table_folder.metadata)

    def save_audio_content(self, stream: AudioDataStream) -> Tuple[str, str]:
        count = len(os.listdir(self.audio_folder.content))
        save_path = os.path.join(self.audio_folder.content, "{}.wav".format(count))
        stream.save_to_wav_file(file_name=save_path)
        return str(count), save_path
    
    def save_audio_metadata(self, audio_info: AudioInfo):
        return LocalStorage.save_metadata(audio_info, self.audio_folder.metadata)
    
    def get_audio_metadata(self, id:str) -> AudioInfo: 
        return LocalStorage.get_metadata(self.audio_folder.metadata, id)
    
    def query_audio_metadata(self, query:str = None) -> List[AudioInfo]: 
        return LocalStorage.get_all_metadata(self.audio_folder.metadata)

    def save_video_content(self, content:bytes, type_suffix:str) -> Tuple[str, str]:
        return LocalStorage.save_content(content, self.video_folder.content, type_suffix)
    
    def save_video_hook(self, hook, type_suffix:str) -> Tuple[str, str]:
        return LocalStorage.save_hook(hook, self.video_folder.content, type_suffix)
    
    def save_video_metadata(self, video_info: VideoInfo):
        return LocalStorage.save_metadata(video_info, self.video_folder.metadata)
    
    def get_video_metadata(self, id:str) -> VideoInfo: 
        return LocalStorage.get_metadata(self.video_folder.metadata, id)
    
    def query_video_metadata(self, query:str = None) -> List[VideoInfo]: 
        return LocalStorage.get_all_metadata(self.video_folder.metadata)
    
    def save_draft(self, draft:MovieComposite) -> str:
        save_path = os.path.join(self.index, "draft.pkl")
        with open(save_path, 'wb') as file:
            pickle.dump(draft, file)
        return save_path
    
    def load_draft(self, path:str = None) -> MovieComposite:
        if path:
            save_path = path
        else:
            save_path = os.path.join(self.index, "draft.pkl")
        with open(save_path, 'rb') as file:
            return pickle.load(file)