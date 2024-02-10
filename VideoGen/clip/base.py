from abc import abstractmethod, ABCMeta

class MovieClip(meteaclass=ABCMeta):
    def __init__(self, duration: float, start: float, name:str = ''):
        self.duration = duration
        self.start = start if start else 0
        self.name = name


class ClipHasRef(meteaclass=ABCMeta):
    def __init__(self, path:str):
        self.path = path


class ClipHasAudio(meteaclass=ABCMeta):
    def __init__(self, vol_scale: float):
        self.vol_scale = vol_scale


class ClipHasImage(meteaclass=ABCMeta):
    def __init__(
            self, 
            mask=None,
            opacity=None, 
            position=None,
            bg_color=None,
            width = None,
        ):
        self.mask = mask
        self.opacity = opacity
        self.position = position
        self.bg_color = bg_color
        self.width = width