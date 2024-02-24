from typing import List
from VideoGen.config.config import Config

class InformationConfig(Config):
    def __init__(self, conf: dict = {}):
        super().__init__(conf)
    
    @property
    def use_image_in_webpage(self) -> bool:
        return self.get_property("use_image_in_webpage") or False
    
    @property
    def use_table_in_webpage(self) -> bool:
        return self.get_property("use_table_in_webpage") or False
    
    @property
    def use_ocr(self) -> bool:
        return self.get_property("use_ocr") or False
    
    @property
    def ocr_lang_list(self) -> List[str]:
        return self.get_property("ocr_lang_list") or ['ch_sim','en']
    
    # @property
    # def depth_relevant_webpage(self) -> int:
    #     return self.get_property(0) or False
    