import requests
import os
import time
import json
import pickle

def download(file_path, url, timeout=120):
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 			(KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE",
		}
	r = requests.get(url, headers=headers, timeout=timeout)
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

def getTextArrayFromArray(textArrays: [str], sep:str='。'):
	newArray = []
	for text in textArrays:
		subArray = text.split(sep)
		if len(subArray) > 1:
			newArray += [v + sep for v in subArray[:-1]]
			newArray.append(subArray[-1])
		else:
			newArray.append(text)
	return newArray


def script2caption(script:str):
	captions = getTextArrayFromArray(script.split("\n"), "。")
	captions = getTextArrayFromArray(captions, "？")
	captions = getTextArrayFromArray(captions, "！")
	captions = filter(lambda s: len(s) > 0, captions)
	return captions

def tryHandle(func, max_try:int = 3, **args):
	try:
		return func(**args)
	except Exception as e:
		if max_try > 0:
			return tryHandle(func, max_try=max_try -1, **args )
		else:
			raise e

