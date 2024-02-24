from VideoGen.info.base import BaseInfo, InfoType

class TableInfo(BaseInfo):
    def __init__(self, id:str, name:str, path:str):
        BaseInfo.__init__(self, id, InfoType.Table, name, path)
