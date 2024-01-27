from enum import Enum
from VideoGen.info.base import BaseInfo, InfoType

class ImageInfo(BaseInfo):
    def __init__(self, path:str, title:str='', ocr_result:str='', provider:str=''):
        BaseInfo.__init__(self, InfoType.Image, title=title, path=path)
        self.title = title
        self.ocr_result = ocr_result
        self.provider = provider
    
    def toJSON(self):
        return {
            **BaseInfo.toJSON(self),
            "ocrResult": self.ocr_result,
            "provider": self.provider
        }
    
    @staticmethod
    def fromJSON(jsonValue: dict):
        return ImageInfo(
            path=jsonValue['path'],
            title=jsonValue['title'],
            ocr_result=jsonValue['ocrResult'],
            provider=jsonValue['provider']
        )
    
    @property
    def description(self):
        return ". ".join([
            "description: `{}`".format(self.title) if self.title else " ",
            "ocr result: `{}`".format(self.ocr_result) if self.ocr_result else " "
        ])

class ImageEncodingFormatEnum(Enum):
    JPEG = 'jpeg'
    PNG = 'png'
    GIF = 'gif'
    SVG = 'svg+xml'

ImageTypeSuffix = {
    ImageEncodingFormatEnum.JPEG.value: [
        'jpg',
        'jpeg',
        'jfif',
        'pjpeg',
        'pjp'
    ],
    ImageEncodingFormatEnum.PNG.value: [
        'png'
    ],
    ImageEncodingFormatEnum.GIF.value: [
        'gif'
    ],
    ImageEncodingFormatEnum.SVG.value: [
        'svg'
    ]
}