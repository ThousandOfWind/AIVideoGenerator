from typing import Tuple

def reduce_token_for_LLM(text:str):
	lines = text.split('\n')
	lines = [line.strip() for line in lines]
	lines = filter(lambda s: len(s) > 0, lines)
	return "\n".join(lines)

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
