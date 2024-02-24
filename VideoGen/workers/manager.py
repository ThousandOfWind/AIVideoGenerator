import logging
from VideoGen.config import ManagerConfig
from VideoGen.infra import LoggerFactory
from VideoGen.storage import BaseStorage
from VideoGen.infra import LoggerFactory
from VideoGen.tool import AIAdapter, SpeechServiceAdapter, SearchAdapter
from VideoGen.workers.table_visualizer import TableVisualizer
from VideoGen.workers.information_collector import InformationCollector
from VideoGen.workers.video_director import VideoDirector

class Manager:
    def __init__(
            self,
            storage:BaseStorage, 
            config: ManagerConfig=ManagerConfig(),
            logger: logging.Logger = None
        ):
        self.config = config
        self.storage = storage
        self.oai = AIAdapter.from_config(config.ai_config)
        self.search = SearchAdapter.from_config(config.search_config)
        self.speech = SpeechServiceAdapter(self.storage, config.speech_config)
        self.table_visualizer = TableVisualizer(self.storage)
        self.information_collector = InformationCollector(self.storage, config.information_config)
        self.video_director = VideoDirector(self.oai, self.speech, self.search, self.storage, self.information_collector, self.table_visualizer, config.director_config)
        self.logger = logger if logger != None else LoggerFactory.get_logger(Manager.__name__)