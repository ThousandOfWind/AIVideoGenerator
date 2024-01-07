import requests
import os
import time
import json
import pickle

def download(file_path, url):
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 			(KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE",
		}
	r = requests.get(url, headers=headers)
	with open(file_path, 'wb') as f:
		f.write(r.content)

def createFolderIfNotExist(folder):
	if not os.path.exists(folder):
		os.makedirs(folder)

def reduceTokenForLLM(text:str):
	lines = text.split('\n')
	lines = [line.strip() for line in lines]
	return "\n".join(lines)

def getCurrentTimeAsFolder():
	now = str(time.time_ns())
	path = os.path.join("output", now)
	createFolderIfNotExist(path)
	return path

def saveToJson(fileName, content):
	with open(fileName, 'w', encoding="utf8") as file:
		json.dump(content, file, ensure_ascii=False, indent=2)

def saveToPickle(fileName, content):
	with open(fileName, 'w') as file:
		pickle.dump(content, file)

def imageWebsite(href:str):
	url = href.split("//")[1]
	host = url.split("/")[0]
	return host

def script2caption(script:str):
	sections = script.split("\n")
	if len(sections) > 3:
		captions = sections
	else:
		captions = []
		for section in sections:
			captions += section.split("。")

	captions = filter(lambda s: len(s) > 0, captions)
	return captions

