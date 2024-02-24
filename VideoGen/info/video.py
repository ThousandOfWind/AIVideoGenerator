from VideoGen.info.base import BaseInfo, InfoType

class VideoInfo(BaseInfo):
    def __init__(self, id:str, path:str, name:str='', duration:float = 0):
        BaseInfo.__init__(self, id, InfoType.Video, name=name, path=path)
        self.duration = duration
    