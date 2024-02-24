from VideoGen.config.config import Config

class SearchConfig(Config):
    def __init__(self, conf: dict = {}):
        super().__init__(conf)
    
    @property
    def bing_search_api(self):
        return self.get_property("bing_search_api") or  "https://api.bing.microsoft.com/v7.0/"
    
    @property
    def bing_search_key(self):
        return self.get_property("bing_search_key") or  ""