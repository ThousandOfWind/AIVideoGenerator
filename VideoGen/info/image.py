from enum import Enum
from VideoGen.info.base import BaseInfo, InfoType

class ImageInfo(BaseInfo):
    def __init__(self, id:str, path:str, name:str='', ocr_result:str='', provider:str=''):
        BaseInfo.__init__(self, id, InfoType.Image, name=name, path=path)
        self.ocr_result = ocr_result
        self.provider = provider
    
    @property
    def description(self):
        title_text = self.name if self.name else "No title image",
        recognize_text = ". In the image, you see text: {}".format(self.ocr_result) if self.ocr_result else ""
        return "Image: {}{}".format(title_text, recognize_text)

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