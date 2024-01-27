from VideoGen.info.base import BaseInfo, InfoType

class ScriptInfo(BaseInfo):
    def __init__(self, title:str, path:str):
        BaseInfo.__init__(self, InfoType.Table, title, path)
    
    def toJSON(self):
        return {
            **BaseInfo.toJSON(self),
        }
    
    @staticmethod
    def fromJSON(jsonValue: dict):
        return ScriptInfo(**jsonValue)