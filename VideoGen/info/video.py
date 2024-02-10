from VideoGen.info.base import BaseInfo, InfoType

class VideoInfo(BaseInfo):
    def __init__(self, id:str, path:str, title:str='', duration:float = 0):
        BaseInfo.__init__(self, id, InfoType.Video, title=title, path=path)
        self.duration = duration
    