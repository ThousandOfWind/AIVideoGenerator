import os
import logging
import sys
import requests
import json
from easyocr import Reader
from VideoGen.info import WebpageInfo, TableInfo
import VideoGen.prompt as PromptMap
from VideoGen.workers.imageWorker import ImageWorker
from VideoGen.tool import IOTool, OpenaiAdapter


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,  # set to logging.DEBUG for verbose output
        format="[%(asctime)s] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p %Z")
logger = logging.getLogger(__name__)

class WebWorker:
    @staticmethod
    def extract_webpage_content(web:str, oai:OpenaiAdapter):
        prompt = "请摘抄下面网页里和主要文章有关的部分，依次输出，不要改动\n```\n{web}\n```".format(web=web)
        return oai.ask_llm(prompt)
    
    @staticmethod
    def get_webpage_info(url:str, output_dir:dir, file_suffix:str=''):
        header = {
            'accept': 'application/json;charset=utf-8',
            'accept-encoding': 'gzip, deflate'
        }
        response = requests.get(url, header)
        response.encoding = response.apparent_encoding
        save_path = os.path.join(output_dir, "webpage-{}.html".format(file_suffix) if file_suffix else "webpage")
        with open(save_path, 'wb') as f:
            f.write(response.content)
        webpage_info = WebpageInfo.from_raw_text(response.text, save_path)
        if str(webpage_info.soup.text).find("Enable JavaScript and cookies to continue") >= 0:
            raise Exception('Can not read {}, because javascript and cookies are required'.format(url))
        return webpage_info
    
    @staticmethod
    def enrich_webpage_image(webpage_info:WebpageInfo, web_content_output_dir:dir, ocr_reader:Reader=None) -> WebpageInfo:
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
        return webpage_info
    
    @staticmethod
    def enrich_web_image(webpage_info:WebpageInfo, web_content_output_dir:dir, ocr_reader:Reader=None) -> WebpageInfo:
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
        return webpage_info
    
    @staticmethod
    def enrich_web_table(webpage_info:WebpageInfo, oai: OpenaiAdapter) -> WebpageInfo:
        q = webpage_info.content
        answer = oai.ask_llm(q, PromptMap.findTable)
        start_pattern = '\n```json'
        end_pattern = '\n```'
        table_list = []
        for section in answer.split('\n====\n'):
            table_content_start_index = section.find(start_pattern)
            if table_content_start_index < 1:
                continue
            table_title = section[:table_content_start_index-1]
            logger.info('table: ' + table_title)
            table_content_start = section[table_content_start_index + start_pattern.__len__():]
            table_content_end_index = table_content_start.find(end_pattern)
            if table_content_end_index < 1:
                continue
            table_content = table_content_start[: table_content_end_index]
            try:
                table_json = json.loads(table_content)
                table_list.append(TableInfo(title=table_title, content=table_json))
            except Exception as e:
                logger.error(table_content)
                logger.error(e)
        webpage_info.tables = table_list
        return webpage_info

    
    @staticmethod
    def get_enriched_webpage_info(url:str, output_dir:dir, ocr_reader:Reader=None, file_suffix:str='', table_oai:OpenaiAdapter = None) -> WebpageInfo:
        web_content_output_dir = os.path.join(output_dir, "web-content-{}".format(file_suffix) if file_suffix else "web-content")
        IOTool.create_folder_if_not_exist(web_content_output_dir)
        logger.info("fetch website content, and save to " + web_content_output_dir)

        webpage_info = WebWorker.get_webpage_info(url, web_content_output_dir)
        webpage_info = WebWorker.enrich_webpage_image(webpage_info, web_content_output_dir, ocr_reader)
        if (table_oai):
            webpage_info = WebWorker.enrich_web_table(webpage_info, table_oai)
        
        IOTool.save_to_json(os.path.join(web_content_output_dir, "web_info.json"), webpage_info.toJSON())
        return webpage_info

    @staticmethod
    def download_url(url:str, save_to:str = ''):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 			(KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE",
            }
        r = requests.get(url, headers=headers)
        with open(save_to, 'wb') as f:
            f.write(r.content)
