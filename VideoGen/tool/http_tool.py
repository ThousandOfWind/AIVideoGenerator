import requests

def download(file_path, url, timeout=120):
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 			(KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE",
		}
	r = requests.get(url, headers=headers, timeout=timeout)
	with open(file_path, 'wb') as f:
		f.write(r.content)

def get_host(href:str):
	url = href.split("//")[1]
	host = url.split("/")[0]
	return host