import requests
from bs4 import BeautifulSoup
from tools.tools import reduceTokenForLLM, createFolderIfNotExist, saveToJson
import os
import logging
import sys
from workers.imageWorker import ImageWorker
from tools.openai_adapter import OpenaiAdapter
from easyocr import Reader

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,  # set to logging.DEBUG for verbose output
        format="[%(asctime)s] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p %Z")
logger = logging.getLogger(__name__)

class WebWorker:
    @staticmethod
    def extractWebContent(web:str, oai:OpenaiAdapter):
        prompt = "请摘抄下面网页里和主要文章有关的部分，依次输出，不要改动\n```\n{web}\n```".format(web=web)
        return oai.AOAIQuery(prompt)
    
    @staticmethod
    def getWebpage(url:str, output_dir:dir, file_suffix:str=''):
        header = {
            'accept': 'application/json;charset=utf-8',
            'accept-encoding': 'gzip, deflate'
        }
        response = requests.get(url, header)
        response.encoding = response.apparent_encoding
        save_path = os.path.join(output_dir, "webpage-{}.html",format(file_suffix))
        with open(save_path, 'wb') as f:
            f.write(response.content)
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup

    @staticmethod
    def getWebPageContent(url:str, output_dir:dir, file_suffix:str=''):
        soup = WebWorker.getWebpage(url, output_dir, file_suffix)
        content = reduceTokenForLLM(soup.text)
        return content
    
    @staticmethod
    def getWebPageContentDeep(url:str, output_dir:dir, ocr_reader:Reader, file_suffix:str=''):
        save_path = os.path.join(output_dir, "webpage-{}".format(file_suffix))

        logger.info("fetch website content, and save to " + save_path)

        createFolderIfNotExist(save_path)
        soup = WebWorker.getWebpage(url, save_path, file_suffix)

        title = soup.title.text
        content = reduceTokenForLLM(soup.text)

        img_list = soup.find_all('img')
        img_info_list = []
        for img_node in img_list:
            img_local_path = None
            img_name = None
            encoding_format = None
            if str(img_node.get('src')).startswith("http://") or str(img_node.get('src')).startswith("https://"):
                img_local_path, img_name, encoding_format = ImageWorker.downloadWebsiteImage(
                    url=img_node.get('src'),
                    output_dir=save_path,
                    file_name="image_{}".format(len(img_info_list))
                )
            elif str(img_node.get('src')).startswith("//"):
                img_local_path, img_name, encoding_format = ImageWorker.downloadWebsiteImage(
                    url="https://" + img_node.get('src'),
                    output_dir=save_path,
                    file_name="image_{}".format(len(img_info_list))
                )
            elif img_node.get('data-lazyload'):
                img_local_path, img_name, encoding_format = ImageWorker.downloadWebsiteImage(
                    url=img_node.get('data-lazyload'),
                    output_dir=save_path,
                    file_name="image_{}".format(len(img_info_list))
                )
            if (not img_local_path is None) and (not img_name is None) and (not encoding_format is None):
                text = " ".join(ocr_reader.readtext(img_local_path, detail = 0))
                img_info_list.append({
                    "name": img_name,
                    "alt": img_node.get('alt'),
                    "ocr": text,
                    "imgPath": img_local_path,
                    "encodingFormat": encoding_format,
                    "provider": ""
               })
        
        web_info = {
            "title": title,
            "content": content,
            "images": img_info_list
        }
        saveToJson(os.path.join(save_path, "web_info.json"), web_info)
        return web_info

    @staticmethod
    def downloadUrl(url:str, save_to:str = ''):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 			(KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE",
            }
        r = requests.get(url, headers=headers)
        with open(save_to, 'wb') as f:
            f.write(r.content)
