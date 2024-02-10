from VideoGen.clip.base import MovieClip, ClipHasImage, ClipHasAudio, ClipHasRef

class MovieText(MovieClip, ClipHasImage):
    def __init__(
            self, 
            text: str, 
            duration: float = 2, 
            start: float = 0,
            mask = None,
            opacity = None,
            position = None,
            bg_color = None,
            width = None,
            fontsize:int = 12,
            color = 'black',
            method = 'caption'
    ):
        MovieClip.__init__(self, duration, start)
        ClipHasImage.__init__(self, mask, opacity, position, bg_color, width)
        self.text = text
        self.fontsize = fontsize
        self.color = color
        self.method = method

    
class MovieAudio(MovieClip, ClipHasRef, ClipHasAudio):
    def __init__(
            self, 
            path: str, 
            duration: float = 2, 
            start: float = 0,
            vol_scale:float = 1
    ):
        MovieClip.__init__(self, duration, start)
        ClipHasRef(self, path)
        ClipHasAudio.__init__(self, vol_scale)


class MovieImage(MovieClip, ClipHasRef, ClipHasImage):
    def __init__(
            self, 
            path: str,
            duration: float = 2, 
            start: float = 0,
            mask=None,
            opacity=None,
            position=None,
            bg_color=None,
            width=None
    ):
        MovieClip.__init__(self, duration, start)
        ClipHasRef.__init__(self, path)
        ClipHasImage.__init__(self, mask, opacity, position, bg_color, width)



class MovieVideo(MovieClip, ClipHasRef, ClipHasImage, ClipHasAudio):
    def __init__(
            self, 
            path: str, 
            duration: float = 2, 
            start: float = 0,
            mask=None,
            opacity=None,
            position=None,
            bg_color=None,
            width=None,
            vol_scale:float = 1
    ):
        MovieClip.__init__(self, duration, start)
        ClipHasRef.__init__(self, path)
        ClipHasImage.__init__(self, mask, opacity, position, bg_color, width)
        ClipHasAudio.__init__(self, vol_scale)