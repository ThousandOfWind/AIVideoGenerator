from VideoGen.config.director_config import DirectorConfig
from VideoGen.config.information_config import InformationConfig
from VideoGen.config.openai_adapter_config import AIConfig
from VideoGen.config.speech_config import SpeechConfig
from VideoGen.config.search_config import SearchConfig
from VideoGen.config.config import Config

class ManagerConfig(Config):    
    def __init__(self, conf: dict = {}):
        super().__init__(conf)
    
    @property
    def director_config(self):
        return self.get_property("director_config") or DirectorConfig()
    
    @property
    def information_config(self):
        return self.get_property("information_config") or InformationConfig()
    
    @property
    def ai_config(self):
        return self.get_property("ai_config") or AIConfig()
    
    @property
    def speech_config(self):
        return self.get_property("speech_config") or SpeechConfig()
    
    @property
    def search_config(self):
        return self.get_property("search_config") or SearchConfig()
    