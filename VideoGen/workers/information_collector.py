import logging
import requests
import io
import pandas as pd
from bs4 import BeautifulSoup
from easyocr import Reader
from VideoGen.info import WebpageInfo, TableInfo, ImageInfo, ImageTypeSuffix, ImageEncodingFormatEnum
from VideoGen.config import InformationConfig
from VideoGen.infra import LoggerFactory
from VideoGen.storage import BaseStorage

class InformationCollector:
    @staticmethod
    def get_host(href:str) -> str:
        url = href.split("//")[1]
        host = url.split("/")[0]
        return host
    
    @staticmethod
    def get_url_from_image_node(img_node) -> str | None:
        for potential_field in ('src', 'data-src', 'data-lazyload'):
            if str(img_node.get(potential_field)).startswith("http://") or str(img_node.get(potential_field)).startswith("https://"):
                return img_node.get(potential_field)
            elif str(img_node.get(potential_field)).startswith("//"):
                return "https:" + img_node.get(potential_field)
        return 
    
    def __init__(
            self, 
            storage:BaseStorage, 
            config: InformationConfig = InformationConfig(), 
            logger: logging.Logger = None
    ):
        self.config: InformationConfig = config
        self.storage: BaseStorage = storage
        self.ocr_reader = Reader(self.config.ocr_lang_list)
        self.logger: logging.Logger = logger or LoggerFactory.get_logger(InformationCollector.__name__)


    def get_image_from_url(self, url:str, title: str = '') -> ImageInfo:
        raw_name_with_suffix = str(url).lower().split('!')[0].split('?')[0].split('/')[-1]
        filename_split = raw_name_with_suffix.split('.')
        if len(filename_split)>1:
            type_suffix = filename_split[-1]
        else:
            type_suffix = ''
        encoding_format = ''

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 			(KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE",
            }
        r = requests.get(url, headers=headers)

        if r.status_code > 200:
            raise Exception('get image fail. code: {}, text: {}'.format(r.status_code, r.text))
        
        if r.headers.get("content-type"):
            encoding_format = r.headers.get("content-type").split('/')[1]
            if not encoding_format in ImageTypeSuffix:
                raise Exception("encoding_format {} is not supported now".format(encoding_format))
            if not type_suffix in ImageTypeSuffix[encoding_format]:
                type_suffix = ImageTypeSuffix[encoding_format][0]
        else:
            for supported_encode in ImageEncodingFormatEnum:
                if type_suffix in ImageTypeSuffix[supported_encode.value]:
                    encoding_format = supported_encode.value
                    break
            if not encoding_format:
                raise Exception("encoding_format {} is not supported now".format(type_suffix))

        id, save_path = self.storage.save_image_content(r.content, type_suffix)
        image_info = ImageInfo(id=id, path=save_path, title=title, provider=InformationCollector.get_host(url))
        if self.config.use_ocr:
            image_info.ocr_result = " ".join(self.ocr_reader.readtext(image_info.path, detail = 0))
        self.storage.save_image_metadata(image_info, id)
        return image_info
    
    def get_webpage(self, url:str) -> WebpageInfo:
        header = {
            'accept': 'application/json;charset=utf-8',
            'accept-encoding': 'gzip, deflate'
        }
        response = requests.get(url, header)
        response.encoding = response.apparent_encoding

        soup = BeautifulSoup(response.text, 'html.parser')
        if str(soup.text).find("Enable JavaScript and cookies to continue") >= 0:
            raise Exception('Can not read {}, because javascript and cookies are required'.format(url))
        
        id, save_to = self.storage.save_webpage_content(response.content)

        title = soup.title.text if soup.title else ''
        content = soup.text
        
        images = []
        if self.config.use_image_in_webpage:
            img_list = soup.find_all('img')
            for img_node in img_list:
                try:
                    url = InformationCollector.get_url_from_image_node(img_node)
                    if url:
                        img_title = img_node.get('alt')
                        img_info = self.get_image_from_url(url, img_title)
                        images.append(img_info.id)
                
                except Exception as e:
                    self.logger.error(e)
        
        tables = []
        if self.config.use_table_in_webpage:
            table_list = soup.find_all('table')
            for table_node in table_list:
                table_title = table_list[0].find('caption').text
                df = pd.read_html(io.StringIO(str(table_node)))[0]
                bytes_io = io.BytesIO()
                df.to_json(bytes_io)
                table_id, table_save_to = self.storage.save_table_content(bytes_io)
                table_info = TableInfo(table_id, table_title, table_save_to)
                self.storage.save_table_metadata(table_info, table_id)
                tables.append(table_id)
        
        webpage_info = WebpageInfo(id, save_to, title, content, images, tables)
        self.storage.save_webpage_metadata(webpage_info)
        return webpage_info

