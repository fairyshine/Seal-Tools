from method import apiset_path
from utils import *

apiset_list = read_jsonl(apiset_path)
api_list = []
api_dict = {}
for field in apiset_list:
    for field_name in field:
        api_list.extend(field[field_name])
        for api in field[field_name]:
            api_dict[api["api_name"]] = api

file_list = [
    "train",
    "dev",
    "test_in_domain",
    "test_out_domain"
]

# raw_path_prefix = "./retriever_result/result_split_"
# result_path = "./retriever_result/result_split.json"

raw_path_prefix = "./retriever_result_BM25/result_"
result_path = "./retriever_result_BM25/result.json"

result_dict = dict()

for file in file_list:
    input_path = raw_path_prefix + file + ".json"
    input_dataset = read_json(input_path)
    result = dict()
    TOP5 = 0
    TOP10 = 0
    for data in input_dataset:
        answer_list = data["answers"]
        retriver_top5 = [data["ctxs"][i]["title"] for i in range(5)]
        retriver_top10 = [data["ctxs"][i]["title"] for i in range(10)]

        flag_top5 = 1
        flag_top10 = 1
        for answer in answer_list:
            if answer not in retriver_top5:
                flag_top5 = 0
            if answer not in retriver_top10:
                flag_top10 = 0
        if flag_top5 == 1:
            TOP5 += 1
        if flag_top10 == 1:
            TOP10 += 1
    
    result["TOP_5"] = TOP5 / len(input_dataset)
    result["TOP_10"] = TOP10 / len(input_dataset)
    result_dict[file] = result
write_json(result_path, result_dict)
    
