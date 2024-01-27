from typing import List
from bs4 import BeautifulSoup
from VideoGen.tool import StringTool
from VideoGen.info.base import BaseInfo, InfoType
from VideoGen.info.image import ImageInfo
from VideoGen.info.table import TableInfo


class WebpageInfo(BaseInfo):
    def __init__(self, soup:BeautifulSoup, path:str, title: str = None, content: str = None, images: List[ImageInfo] = [], tables: List[TableInfo] = []):
        BaseInfo.__init__(self, InfoType.Webpage, title, path)
        self.soup = soup
        self.content = content if content else self.soup.text
        self.images:List[ImageInfo] = images
        self.tables: List[TableInfo] = tables

    def toJSON(self):
        return {
            **BaseInfo.toJSON(self),
            "content": self.content,
            "images": [image.toJSON() for image in self.images],
            "tables": [table.toJSON() for table in self.tables]
        }
    
    @staticmethod
    def from_raw_text(raw_text:str, path:str):
        soup = BeautifulSoup(raw_text, 'html.parser')
        title = soup.title.text if soup.title else ''
        content = StringTool.reduce_token_for_LLM(soup.text)
        return WebpageInfo(soup, path, title, content=content)
    
    @staticmethod
    def from_path(path:str):
        with open(path, 'w', encoding="utf8") as file:
            raw_text = file.read()
        return WebpageInfo.from_raw_text(raw_text, path)
    
    @staticmethod
    def fromJSON(jsonValue: dict):
        webpage_info = WebpageInfo.from_path(jsonValue['path'])
        webpage_info.title = jsonValue['title']
        webpage_info.content = jsonValue['content']
        webpage_info.images = [ImageInfo.fromJSON(image_json) for image_json in jsonValue['images']]
        webpage_info.tables = [TableInfo.fromJSON(table_json) for table_json in jsonValue['tables']]
        return webpage_info