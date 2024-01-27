import os
import time
import json
import pickle

def create_folder_if_not_exist(folder):
	if not os.path.exists(folder):
		os.makedirs(folder)
		
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