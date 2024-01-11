import requests
from bs4 import BeautifulSoup
from tools.tools import reduceTokenForLLM
import cv2
import numpy as np
import os

class LogisticsWorker:
    @staticmethod
    def getWebPageContent(url:str, save_path:str = ''):
        header = {
            'accept': 'application/json;charset=utf-8',
            'accept-encoding': 'gzip, deflate'
        }
        response = requests.get(url, header)
        if (save_path):
            with open(save_path, 'wb') as f:
                f.write(response.content)
        soup = BeautifulSoup(response.text, 'html.parser')
        content = reduceTokenForLLM(soup.text)
        return content

    @staticmethod
    def downloadUrl(url:str, save_to:str = ''):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 			(KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE",
            }
        r = requests.get(url, headers=headers)
        with open(save_to, 'wb') as f:
            f.write(r.content)

    @staticmethod
    def getDefaultAvatarImage():
        return {
            "provider": "Dalle",
            "name": 'Avatar',
            "encodingFormat": "jpg"
               }, 'docs/anchor.jpeg'

    @staticmethod
    def drawBackgroundImage(folder: str, shape:tuple=(720, 1080)):
        image_path = os.path.join(folder, 'blank_image.jpg')
        if not os.path.exists(image_path):
            blank_img = np.zeros(shape=(shape[1], shape[0], 3), dtype=np.uint8)
            cv2.imwrite(image_path, blank_img)
        return {
            "provider": "",
            "name": 'blank background',
            "encodingFormat": "png"
               }, image_path

    @staticmethod
    def resize_image_watermark(image_path: str, resize_img_path: str, water_mark="", shape:tuple=(720, 1080)):
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
        return new_img
    
