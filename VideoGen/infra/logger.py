import sys
import logging

class LoggerFactory:
    def get_logger(name:str = None):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,  # set to logging.DEBUG for verbose output
                format="[%(asctime)s] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p %Z")
        return logging.getLogger(__name__)