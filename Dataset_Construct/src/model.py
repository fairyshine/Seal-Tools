import json

import openai

from openai_key import organization,api_key

openai.organization = organization
openai.api_key = api_key

class LLM():
    def __init__(self):
        pass

    def answer(self,input_text):
        output_full_json = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": input_text}
            ]
        )

        output_full_text = json.dumps(output_full_json, ensure_ascii=False)
        output_text = output_full_json['choices'][0]['message']['content'].encode('utf-8').decode('utf-8')

        return output_full_json, output_full_text, output_text