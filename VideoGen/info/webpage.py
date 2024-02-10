from typing import List
from VideoGen.info.base import BaseInfo, InfoType


class WebpageInfo(BaseInfo):
    def __init__(self, id:str, path:str, name: str = None, content: str = None, images: List[str] = [], tables: List[str] = []):
        BaseInfo.__init__(self, id, InfoType.Webpage, name, path)
        self.content = content 
        self.images:List[str] = images
        self.tables: List[str] = tables
