import json
import re

import openai

from openai_key import organization,api_key
from model import LLM
from prompts import *
from rules import *
from utils import *
from method import *

ChatGPT = LLM()
openai.organization = organization
openai.api_key = api_key

prompt = "Please check the API.\nTips:\n1.First, check whether the name of the API should be closely related to the field.When the field is fine-grained, your API name should not mean coarse-grained. For example,the \"field\" is \"Communication/Voicemail\",the \"api_name\" \"getEmails\" is not compliant,because the field \"Voicemail\" is fine-grained while the \"api_name\" \"getEmails\" is coarse-grained compared to \"Voicemail\".Once the API name does not meet the requirements, You need to modify the \"api_name\" to make it more consistent with the field and the meaning of the API,but do not modify the \"field\".\n2.You need to check whether the description of each API parameter conforms to the logic and API meaning, and rewrite the description that does not meet the requirements.\n3.The parameters in the \"required\" list are necessary to implement the functionality of the API and are needed each time.You need to check if any important parameters have not been added to the \"required\" list, and add these parameters to the \"required\" list. And check whether the \"required\" list contains some non-essential parameters, and remove these parameters from the \"required\" list.\n4.Your answer should be in JSON format.After checking, return your modified API in the origin JSON format. If there is no problems after checking, return the original API in the origin JSON format.\n\nNow the API is:\n"

input_path = "./dataset/api_set.jsonl"
output_path = "./api_check_set.jsonl"
check_file_path(input_path)
check_file_path(output_path)
file = read_jsonl(input_path)
corrected_api_list = read_jsonl(output_path)

for field_api_set in file:
    for field in field_api_set:
        for raw_api in field_api_set[field]:
            corrected_field_api_set = {field:[]}
            new_prompt=prompt+str(raw_api)
            raw_output,_,answer_text = ChatGPT.answer(new_prompt)
            # - 后处理，得到结果
            answer_split_text = re.split(r'\n{2,}',answer_text)
            for answer_split in answer_split_text:
                count = 0
                try:
                    answer_split = re.sub("\n", "", answer_split)
                    api_part = match_given_pattern(answer_split,r'\{.+\}')
                    api = json.loads(api_part)
                    if api_check(api):
                        corrected_field_api_set[field].append(api)
                except:
                    pass
        corrected_api_list.append(corrected_field_api_set)
        #存储
        write_jsonl(output_path,corrected_api_list)
            
