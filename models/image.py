from enum import Enum

class ImageInfo:
    def __init__(self, path:str, raw_description:str='', ai_description:str='', provider:str=''):
        self.path = path
        self.raw_description = raw_description
        self.ai_description = ai_description
        self.provider = provider
    
    def toJSON(self):
        return {
            "path": self.path,
            "raw_description": self.raw_description,
            "ai_description": self.ai_description,
            "provider": self.provider
        }
    
    @property
    def description(self):
        return " ".join([
            "description: `{}`".format(self.raw_description) if self.raw_description else " ",
            "ocr result: `{}`".format(self.ai_description) if self.ai_description else " "
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