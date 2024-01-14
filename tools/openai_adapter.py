import copy
import os
from openai import Client
import json
import requests
from pprint import pprint
from tools.tools import tryHandle, download


class OpenaiAdapter:
    def __init__(self, openai_client: Client, chat_param: dict = None, model:str="gpt-4-32k", max_try:int = 3):
        self.openai_client = openai_client
        if (chat_param):
            self.chat_param = copy.deepcopy(chat_param)
        else:
            self.chat_param = {}
        if (not "model" in self.chat_param or not self.chat_param["model"]):
            self.chat_param["model"] = model
        
        self.max_try = max_try

    def AOAIQuery(self, prompt: str, prompt_path: str = '', max_try:int = None) -> str:
        return tryHandle(
            self._AOAIQuery, 
            max_try=max_try if max_try else self.max_try, 
            user_question=prompt, 
            prompt_path=prompt_path)
    
    def _AOAIQuery(self, prompt: str, prompt_path: str = ''):
        if prompt_path:
            with open(prompt_path, "r") as f:
                content = f.read()
                messages = list(json.loads(content))
        else:
            messages = []

        messages.append({
            "role": "user",
            "content": prompt
        })

        completion = self.openai_client.chat.completions.create(
            messages=messages,
            **self.chat_param,
        )

        try:
            answer = completion.choices[0].message.content.strip()
            return answer
        except Exception as e:
            print(prompt, prompt_path)
            pprint(completion)
            raise e
    
    def draw(self, prompt:str, folder:str, file_suffix:str, max_try:int = None):
        return tryHandle(self._draw, max_try=max_try if max_try else self.max_try, prompt=prompt, folder=folder, file_suffix=file_suffix)

    
    def _draw(self, prompt:str, folder:str, file_suffix:str):
        # result = (oai.openai_client).images.generate(
        #     model="dall-e-3", # the name of your DALL-E 3 deployment
        #     prompt=prompt,
        #     size="1024x1024",
        #     n=1
        # )
        # image_url = json.loads(result.model_dump_json())['data'][0]['url']
        url = "https://{host}/openai/deployments/Dalle3/images/generations?api-version=2023-12-01-preview".format(host=self.openai_client.base_url.host)
        headers = {"api-key": oai.openai_client.api_key, "Content-Type": "application/json"}
        body = {
            # Enter your prompt text here
            "prompt": prompt,
            "size": "1024x1024",  # supported values are “1792x1024”, “1024x1024” and “1024x1792”
            "n": 1,
            "quality": "hd",  # Options are “hd” and “standard”; defaults to standard
            "style": "vivid"  # Options are “natural” and “vivid”; defaults to “vivid”
        }
        submission = requests.post(url, headers=headers, json=body)
        image_url = submission.json()['data'][0]['url']
        image_path = os.path.join(folder, 'dalle-image-{}.png'.format(file_suffix))
        download(image_path, image_url)
        return {
            "provider": "Dalle",
            "name": prompt,
            "alt": prompt,
            "encodingFormat": "png"
               }, image_path
