import requests
from tools.tools import reduceTokenForLLM, createFolderIfNotExist
import cv2
import numpy as np
import os
import logging
import sys
from enum import Enum
from collections import namedtuple
from tools.openai_adapter import OpenaiAdapter
from workers.AIWorker import PromptMap

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG,  # set to logging.DEBUG for verbose output
        format="[%(asctime)s] %(message)s", datefmt="%m/%d/%Y %I:%M:%S %p %Z")
logger = logging.getLogger(__name__)

ImageInfo = namedtuple("ImageInfo", ["name", "alt", "imgPath", "encodingFormat", "provider"])

class ImageEncodingFormatEnum(Enum):
    JPEG = 'jpeg'
    PNG = 'png'

ImageTypeSuffix = {
    ImageEncodingFormatEnum.JPEG.value: [
        'jpg',
        'jpeg'
    ],
    ImageEncodingFormatEnum.PNG.value: [
        'png'
    ]
}

class ImageWorker:
    @staticmethod
    def downloadWebsiteImage(url:str, output_dir: str, file_name:str):
        raw_name_with_suffix = str(url).lower().split('!')[0].split('?')[0].split('/')[-1]
        raw_name = raw_name_with_suffix.split('.')[0]
        suffix = raw_name_with_suffix.split('.')[-1]
        type_suffix = ''

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 			(KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE",
            }
        r = requests.get(url, headers=headers)
        encoding_format = r.headers.get("Content_Type").split('/')[1]

        for supported_encode in ImageEncodingFormatEnum:
            if encoding_format == supported_encode.value:
                if suffix in ImageTypeSuffix[supported_encode.value]:
                    type_suffix = suffix
                break
        if not type_suffix:
            return None, None, None
        save_to = os.path.join(output_dir, "{0}.{1}".format(file_name, type_suffix))
        with open(save_to, 'wb') as f:
            f.write(r.content)
        return save_to, raw_name, encoding_format
    
    @staticmethod
    def getDefaultAvatarImage():
        return {
            "provider": "Dalle",
            "name": 'Avatar',
            "encodingFormat": ImageEncodingFormatEnum.JPEG.value
               }, 'docs/anchor.jpeg'

    @staticmethod
    def drawBackgroundImage(folder: str, shape:tuple=(720, 1080)):
        image_path = os.path.join(folder, 'blank_image.jpg')
        if not os.path.isfile(image_path):
            blank_img = np.zeros(shape=(shape[1], shape[0], 3), dtype=np.uint8)
            cv2.imwrite(image_path, blank_img)
        return {
            "provider": "",
            "name": 'blank background',
            "encodingFormat": ImageEncodingFormatEnum.JPEG.value
               }, image_path

    @staticmethod
    def resize_image_watermark(image_path: str, output_dir: str, image_suffix:str, water_mark="", shape:tuple=(720, 1080)):
        resize_img_path = os.path.join(
            output_dir,
            'image-resized-watermark_{}.{}'.format(image_suffix, image_path.split('.')[-1]))
        try:
            img = cv2.imread(image_path, cv2.IMREAD_COLOR)
            h, w, c = img.shape
            ratio = min(shape[0] / w, shape[1] / h)
            new_w, new_h = int(w * ratio), int(h * ratio)
            delta_w, delta_h = shape[0] - new_w, shape[1] - new_h
            top, bottom = delta_h // 2, delta_h - delta_h // 2
            left, right = delta_w // 2, delta_w - delta_w // 2
            new_img = cv2.resize(img, (new_w, new_h))
            print("after resize", new_img.shape)

            if (water_mark):
                # 创建一个空白的图片

                # 水印放置的横纵坐标
                org = (40, 90)
                # 水印的字体相关的参数
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.8
                # 水印的颜色
                color = (255, 255, 255)
                # 印有水印的图片相关的设置，线条的粗细哇、线条的样式哇等等
                thickness = 1
                line_type = cv2.LINE_4
                blank_img = np.zeros(shape=new_img.shape, dtype=np.uint8)
                # 在空白图片上添加水印
                cv2.putText(blank_img, text=water_mark, org=org, fontFace=font, fontScale=font_scale, color=(128, 128, 128),
                            thickness=thickness * 2, lineType=line_type)
                cv2.putText(blank_img, text=water_mark, org=org, fontFace=font, fontScale=font_scale, color=color,
                            thickness=thickness, lineType=line_type)

                # 将印有水印的图片和原图进行结合
                new_img = cv2.addWeighted(src1=new_img, alpha=1, src2=blank_img, beta=0.3, gamma=2)
            
            color = [0, 0, 0]
            new_img = cv2.copyMakeBorder(new_img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
            print("after border", new_img.shape)
            cv2.imwrite(resize_img_path, new_img)
            return resize_img_path
        except Exception as e:
            logger.error(e)
            _, bg_image_path = ImageWorker.drawBackgroundImage(output_dir, shape)
            return bg_image_path
    
    @staticmethod
    def drawAnchor(text:str, folder:str, file_suffix:str, oai: OpenaiAdapter):
        question = "When you broadcast `{text}`, what expression and gesture you will perform? Answer the key look in one short sentence. ".format(
            text=text)

        try:
            answer = oai.AOAIQuery(question, PromptMap.reviewGeneratedScripts)
            return oai.draw(
                "realistic 3d rendering, created using C4D modeling. A famous Chinese male anchor, {0}".format(answer),
                folder,
                "anchor-{0}".format(file_suffix)
            )
        except Exception:
            print("Error during answer, ", question)
            return ImageWorker.getDefaultAvatarImage()