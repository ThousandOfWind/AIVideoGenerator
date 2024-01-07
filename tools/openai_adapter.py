import copy
from openai import Client
import json
from pprint import pprint


class OpenaiAdapter:
    def __init__(self, openai_client: Client, chat_param: dict = None):
        self.openai_client = openai_client
        if (chat_param):
            self.chat_param = copy.deepcopy(chat_param)
        else:
            self.chat_param = {}
        if (not "model" in self.chat_param or not self.chat_param["model"]):
            self.chat_param["model"] = "gpt-4-32k"

    def AOAIquery(self, user_question: str, prompt_path: str = ''):
        if prompt_path:
            with open(prompt_path, "r") as f:
                content = f.read()
                messages = list(json.loads(content))
        else:
            messages = []

        messages.append({
            "role": "user",
            "content": user_question
        })

        completion = self.openai_client.chat.completions.create(
            messages=messages,
            **self.chat_param,
        )

        try:
            answer = completion.choices[0].message.content.strip()
            return answer
        except Exception as e:
            print(user_question, prompt_path)
            pprint(completion)
            raise e
