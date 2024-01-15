from configs.config import Config
from typing import Tuple

class DirectorConfig(Config):
    def __init__(self, conf: dir):
        super().__init__(conf)

    @property
    def path_to_font(self) -> str:
        return self.get_property("path_to_font") or '/System/Library/Fonts/Supplemental/Arial Unicode.ttf'
    
    @property
    def video_shape(self) -> (int, int):
        return self.get_property("video_shape") or tuple((720, 1280))
    
    @property
    def use_avatar(self) -> bool:
        return self.get_property("use_avatar") or False
    
    @property
    def use_image_in_webpage(self) -> bool:
        return self.get_property("use_image_in_webpage") or False
    
    @property
    def use_ocr(self) -> bool:
        return self.get_property("use_ocr") or False
    
    @property
    def use_dalle(self) -> bool:
        return self.get_property("use_dalle") or False
    
    @property
    def search_online_image(self) -> bool:
        return self.get_property("search_online_image") or False
    
    @property
    def script_seps(self) -> Tuple[str]:
        return self.get_property("script_seps") or tuple('\n')
    
