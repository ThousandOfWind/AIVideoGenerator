import json
import requests
from pprint import pprint
from openai import AzureOpenAI, OpenAI, Client
from VideoGen.config import AIConfig


class AIAdapter:
    def __init__(self, openai_client: Client, chat_param: dict = None):
        self.openai_client = openai_client
        self.chat_param = chat_param

    def ask_llm(self, prompt: str, prompt_path: str = ''):
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
            ** self.chat_param,
        )

        try:
            answer = completion.choices[0].message.content.strip()
            return answer
        except Exception as e:
            print(prompt, prompt_path)
            pprint(completion)
            raise e
    
    def draw_by_dalle(self, prompt:str):
        # result = (oai.openai_client).images.generate(
        #     model="dall-e-3", # the name of your DALL-E 3 deployment
        #     prompt=prompt,
        #     size="1024x1024",
        #     n=1
        # )
        # image_url = json.loads(result.model_dump_json())['data'][0]['url']
        url = "https://{host}/openai/deployments/Dalle3/images/generations?api-version=2023-12-01-preview".format(host=self.openai_client.base_url.host)
        headers = {"api-key": self.openai_client.api_key, "Content-Type": "application/json"}
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
        return image_url

    @staticmethod
    def from_config(oai_config: AIConfig | dict):
        if type(oai_config) == dict:
            oai_config = AIConfig(oai_config)
        if oai_config.type == 'OpenAI':
            client = OpenAI(
                api_key=oai_config.api_key, 
                base_url=oai_config.endpoint,
                max_retries=oai_config.max_retries)
        elif oai_config.type == 'AzureOpenAI':
            client = AzureOpenAI(
                api_version=oai_config.api_version,
                azure_endpoint=oai_config.endpoint,
                api_key=oai_config.api_key,
                max_retries=oai_config.max_retries
            )
        else:
            raise Exception("unsupported openai client type")
        
        return AIAdapter(
            client=client, 
            chat_param={
                "model": oai_config.chat_model
            })