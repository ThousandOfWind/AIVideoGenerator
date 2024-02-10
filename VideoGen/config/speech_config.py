from VideoGen.config.config import Config

class SpeechConfig(Config):
    def __init__(self, conf: dict = {}):
        super().__init__(conf)

    @property
    def language(self):
        return self.get_property('language') or 'zh'
    
    @property
    def voice_name(self):
        return self.get_property('voice_name') or 'Xiaoxiao'
    
    @property
    def tone_type(self):
        return self.get_property('tone_type') or 'Neural'
    
    @property
    def host(self):
        return self.get_property('host') or 'customvoice.api.speech.microsoft.com'
    
    @property
    def region(self):
        return self.get_property('region') or 'southeastasia'
    
    @property
    def key(self):
        return self.get_property('key') or ''
    
    @property
    def speech_synthesis_voice_name(self):
        return f'{self.language}-{self.voice_name}{self.tone_type}'
    
    @property
    def use_avatar(self):
        return self.get_property('use_avatar') or False
