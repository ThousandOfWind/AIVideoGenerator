from abc import abstractmethod, ABCMeta
from enum import Enum

class InfoType(Enum):
    Image = 'Image'
    Table = 'Table'
    Webpage = 'Webpage'


class BaseInfo(meteaclass=ABCMeta):
    def __init__(self, type:InfoType, title:str, path: str=None):
        self.title = title
        self.type = type
        self.path = path
    
    @abstractmethod
    def toJSON(self) -> dict:
        return {
            'title': self.title,
            'type': self.type.value,
            'path': self.path
        }
    
    @abstractmethod
    @staticmethod
    def fromJSON(jsonValue: dict):pass