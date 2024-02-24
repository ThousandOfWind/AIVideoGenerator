from typing import List
from VideoGen.clip.base import MovieClip, ClipHasAudio, ClipHasImage
from VideoGen.clip.simple import MovieText, MovieImage, MovieAudio, MovieVideo

class MovieComposite(MovieClip, ClipHasAudio, ClipHasImage):
    def __init__(
            self, 
            duration: float = 2, 
            start: float = 0,
            name: str = '',
            mask=None,
            opacity=None,
            position=None,
            vol_scale:float = 1,
            video_channels: List[List[MovieText | MovieImage | MovieVideo ]] = [],
            audio_channels: List[List[MovieVideo | MovieAudio]] = []
    ):
        MovieClip.__init__(self, duration, start, name)
        ClipHasImage.__init__(self, mask, opacity, position)
        ClipHasAudio.__init__(self, vol_scale)
        self.video_channels = video_channels
        self.audio_channels = audio_channels
