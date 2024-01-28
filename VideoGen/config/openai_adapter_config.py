import os
from VideoGen.config.config import Config

class OpenAIAdapterConfig(Config):
    def __init__(self, conf: dir):
        super().__init__(conf)
    
    @property
    def type(self) -> str:
        return self.get_property("type") or 'OpenAI'
    
    @property
    def api_version(self) -> str:
        return self.get_property("api_version") or "2023-12-01-preview"
    
    @property
    def api_key(self) -> str:
        return self.get_property("api_key") or os.getenv('OPANAI_API_KEY'),
    
    @property
    def endpoint(self) -> str:
        return self.get_property("endpoint") or os.getenv('OPANAI_ENDPOINT')
    
    @property
    def chat_model(self) -> str:
        return self.get_property("chat_model") or "gpt-4-32k"
    
    @property
    def max_retries(self) -> int:
        return self.get_property("max_retries") or 3
    