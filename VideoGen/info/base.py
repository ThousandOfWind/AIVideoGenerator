from abc import abstractmethod, ABCMeta
from enum import Enum

class InfoType(Enum):
    Image = 'Image'
    Table = 'Table'
    Webpage = 'Webpage'
    Audio = 'Audio'
    Video = 'Video'


class BaseInfo(meteaclass=ABCMeta):
    def __init__(self, id: str, type:InfoType, title:str, path: str=None):
        self.id = id
        self.title = title
        self.type = type
        self.path = path