import requests
import os
import time
import json
import pickle
from typing import Tuple

def download(file_path, url, timeout=120):
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 			(KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE",
		}
	r = requests.get(url, headers=headers, timeout=timeout)
	with open(file_path, 'wb') as f:
		f.write(r.content)

def create_folder_if_not_exist(folder):
	if not os.path.exists(folder):
		os.makedirs(folder)

def reduce_token_for_LLM(text:str):
	lines = text.split('\n')
	lines = [line.strip() for line in lines]
	lines = filter(lambda s: len(s) > 0, lines)
	return "\n".join(lines)

def current_time_as_folder():
	now = str(time.time_ns())
	path = os.path.join("output", now)
	create_folder_if_not_exist(path)
	return path

def save_to_txt(file_name, content:str):
	with open(file_name, 'w', encoding="utf8") as file:
		file.write(content)

def save_to_json(file_name, content):
	with open(file_name, 'w', encoding="utf8") as file:
		json.dump(content, file, ensure_ascii=False, indent=2)

def save_to_pickle(file_name, content):
	with open(file_name, 'w') as file:
		pickle.dump(content, file)

def image_website(href:str):
	url = href.split("//")[1]
	host = url.split("/")[0]
	return host

def str_list_split(str_list: [str], sep:str='。', min_length:int=6):
	new_str_list = []
	for text in str_list:
		if (len(text)):
			sub_list = text.split(sep)
			if len(sub_list) > 1 and len(text) > min_length:
				array_meet_min_length = []
				suffix = ""
				for element_index, element in enumerate(sub_list):
					if len(suffix) > 0:
						suffix += sep + element
					else:
						suffix = element
					if len(suffix) > min_length:
						array_meet_min_length.append(suffix + (sep if element_index < len(sub_list) - 1 else ""))
						suffix = ""
				if suffix:
					if len(array_meet_min_length)  == 0:
						array_meet_min_length = [suffix]
					else:
						last_element = array_meet_min_length[-1]
						array_meet_min_length = array_meet_min_length[:-1] + [last_element + suffix]

				new_str_list += array_meet_min_length
			else:
				new_str_list.append(text)
	return new_str_list


def script2caption(script:str, sep_list:Tuple[str]=('\n', '。', "？", "！", "，"), min_length:int=6):
	captions = [script]
	for sep in sep_list:
		captions = str_list_split(captions, sep=sep, min_length=min_length)
	return captions

def try_handle(func, max_try:int = 3, **args):
	try:
		return func(**args)
	except Exception as e:
		if max_try > 0:
			return try_handle(func, max_try=max_try -1, **args )
		else:
			raise e

