from bs4 import BeautifulSoup
from models.image import ImageInfo
from typing import List

class WebpageInfo:
    def __init__(self, soup:BeautifulSoup):
        self.soup = soup
        self.title_text = self.soup.title.text if self.soup.title else ''
        self.content = self.soup.text
        self.images:List[ImageInfo] = []

    def toJSON(self):
        return {
            "title": self.title_text,
            "content": self.content,
            "images": [image.toJSON() for image in self.images]
        }