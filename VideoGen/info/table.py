from VideoGen.info.base import BaseInfo, InfoType

class TableInfo(BaseInfo):
    def __init__(self, title:str, content):
        BaseInfo.__init__(self, InfoType.Table, title)
        self.content = content
    
    def toJSON(self):
        return {
            **BaseInfo.toJSON(self),
            "content": self.content
        }
    
    @staticmethod
    def fromJSON(jsonValue: dict):
        return TableInfo(**jsonValue)