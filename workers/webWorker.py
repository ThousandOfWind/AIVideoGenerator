from bs4.element import PageElement as PageElement, SoupStrainer as SoupStrainer
import requests
from bs4 import BeautifulSoup
from tools.tools import reduce_token_for_LLM, create_folder_if_not_exist, save_to_json
import os
import logging
import sys
from workers.imageWorker import ImageWorker
from tools.openai_adapter import OpenaiAdapter
from easyocr import Reader
from models.image import ImageInfo
from models.webpage import WebpageInfo

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,  # set to logging.DEBUG for verbose output
        format="[%(asctime)s] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p %Z")
logger = logging.getLogger(__name__)

class WebWorker:
    @staticmethod
    def extractWebContent(web:str, oai:OpenaiAdapter):
        prompt = "请摘抄下面网页里和主要文章有关的部分，依次输出，不要改动\n```\n{web}\n```".format(web=web)
        return oai.ask_llm(prompt)
    
    @staticmethod
    def getWebpageInfo(url:str, output_dir:dir, file_suffix:str=''):
        header = {
            'accept': 'application/json;charset=utf-8',
            'accept-encoding': 'gzip, deflate'
        }
        response = requests.get(url, header)
        response.encoding = response.apparent_encoding
        save_path = os.path.join(output_dir, "webpage-{}.html".format(file_suffix) if file_suffix else "webpage")
        with open(save_path, 'wb') as f:
            f.write(response.content)
        soup = BeautifulSoup(response.text, 'html.parser')
        webpage_info = WebpageInfo(soup)
        webpage_info.content = reduce_token_for_LLM(soup.text)
        return webpage_info
    
    @staticmethod
    def getWebPageContentDeep(url:str, output_dir:dir, ocr_reader:Reader=None, file_suffix:str='') -> WebpageInfo:
        web_content_output_dir = os.path.join(output_dir, "web-content-{}".format(file_suffix) if file_suffix else "web-content")
        create_folder_if_not_exist(web_content_output_dir)
        logger.info("fetch website content, and save to " + web_content_output_dir)

        webpage_info = WebWorker.getWebpageInfo(url, web_content_output_dir)

        img_list = webpage_info.soup.find_all('img')
        img_info_list = []
        for img_node in img_list:
            try:
                image_info = ImageWorker.get_image_by_image_node(
                    img_node=img_node,
                    output_dir=web_content_output_dir,
                    image_suffix=str(len(img_info_list)),
                    ocr_reader=ocr_reader)
                img_info_list.append(image_info)
                
            except Exception as e:
                logger.error(e)
        logger.info('load {} from web'.format(len(img_info_list)))
        webpage_info.images = img_info_list
        
        save_to_json(os.path.join(web_content_output_dir, "web_info.json"), webpage_info.toJSON())
        return webpage_info

    @staticmethod
    def downloadUrl(url:str, save_to:str = ''):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 			(KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE",
            }
        r = requests.get(url, headers=headers)
        with open(save_to, 'wb') as f:
            f.write(r.content)
