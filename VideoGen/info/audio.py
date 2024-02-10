from enum import Enum
from VideoGen.info.base import BaseInfo, InfoType

class AudioInfo(BaseInfo):
    def __init__(self, id:str, path:str, title:str='', duration:float = 0):
        BaseInfo.__init__(self, id, InfoType.Audio, title=title, path=path)
        self.duration = duration
    