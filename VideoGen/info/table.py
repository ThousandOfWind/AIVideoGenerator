from VideoGen.info.base import BaseInfo, InfoType

class TableInfo(BaseInfo):
    def __init__(self, id:str, title:str, path:str):
        BaseInfo.__init__(self, id, InfoType.Table, title, path)
