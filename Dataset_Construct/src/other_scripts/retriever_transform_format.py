from method import apiset_path
from utils import *

# * ====================================================
# * 将数据集转化为DPR格式 

# apiset_list = read_jsonl(apiset_path)
# api_list = []
# api_dict = {}
# for field in apiset_list:
#     for field_name in field:
#         api_list.extend(field[field_name])
#         for api in field[field_name]:
#             api_dict[api["api_name"]] = api

# file_list = [
#     "train.jsonl",
#     "dev.jsonl",
#     "test_in_domain.jsonl",
#     "test_out_domain.jsonl"
# ]

# raw_path = "./splitted_dataset/"
# retriever_path = "./for_retriever_training/"

# for file in file_list:
#     input_path = raw_path + file
#     output_path = retriever_path + file

#     input_dataset = read_jsonl(input_path)
#     output_dataset = list()

#     for input_data in input_dataset:
#         if type(input_data[0])==list:
#             for plugin_calling in input_data[0]:
#                 output_data = dict()
#                 question = input_data[1]
#                 positive_ctxs = list()

#                 positive_ctx = dict()
#                 positive_ctx["title"] = plugin_calling["api"]
#                 positive_ctx["text"] = api_dict[plugin_calling["api"]]["api_description"]
#                 positive_ctxs.append(positive_ctx)

#                 output_data["question"] = question
#                 output_data["answers"] = []
#                 output_data["positive_ctxs"] = positive_ctxs
#                 output_data["negative_ctxs"] = []
#                 output_data["hard_negative_ctxs"] = []

#                 output_dataset.append(output_data)
#         else:
#             output_data = dict()
#             question = input_data[1]
#             positive_ctxs = list()

#             positive_ctx = dict()
#             positive_ctx["title"] = input_data[0]["api"]
#             positive_ctx["text"] = api_dict[input_data[0]["api"]]["api_description"]
#             positive_ctxs.append(positive_ctx)

#             output_data["question"] = question
#             output_data["answers"] = []
#             output_data["positive_ctxs"] = positive_ctxs
#             output_data["negative_ctxs"] = []
#             output_data["hard_negative_ctxs"] = []

#             output_dataset.append(output_data)

#     write_json(output_path[:-6]+"_split.json", output_dataset)


# * ====================================================
# * 将数据集中的插件信息保存为DPR的context 

# import pandas as pd


# apiset_list = read_jsonl(apiset_path)
# api_list = []
# api_dict = {}
# for field in apiset_list:
#     for field_name in field:
#         api_list.extend(field[field_name])
#         for api in field[field_name]:
#             api_dict[api["api_name"]] = api

# data_init = [[None]*2]*len(api_list)
# df = pd.DataFrame(data_init, index=range(1,len(api_list)+1), columns=["text", "title"]).astype(str)
# df.index.name = 'id'
# for i in range(len(api_list)):
#     df.loc[i+1,"text"] = api_list[i]["api_description"]
#     df.loc[i+1,"title"] = api_list[i]["api_name"]

# df.to_csv('./for_retriever_training/Plugin_context.tsv', sep='\t')


# * ====================================================
# * 将DPR格式的数据集处理为推理的格式

# import pandas as pd

# train_input =  "./for_retriever_training/PluginLLM_train.json"
# train_output = "./for_retriever_training/PluginLLM_train_qa.csv"

# dataset = read_json(train_input)
# data_init = [[None]*2]*len(dataset)
# df = pd.DataFrame(data_init, index=range(1,len(dataset)+1), columns=["Q", "A"]).astype(str)
# df.index.name = 'id'
# for i in range(len(dataset)):
#     answer_list = [positive_ctx["title"] for positive_ctx in dataset[i]["positive_ctxs"]]
#     df.loc[i+1,"Q"] = dataset[i]["question"]
#     df.loc[i+1,"A"] = answer_list

# df.to_csv(train_output, sep='\t', header=False, index=False)

# # ---

# dev_input =  "./for_retriever_training/PluginLLM_dev.json"
# dev_output = "./for_retriever_training/PluginLLM_dev_qa.csv"

# dataset = read_json(dev_input)
# data_init = [[None]*2]*len(dataset)
# df = pd.DataFrame(data_init, index=range(1,len(dataset)+1), columns=["Q", "A"]).astype(str)
# df.index.name = 'id'
# for i in range(len(dataset)):
#     answer_list = [positive_ctx["title"] for positive_ctx in dataset[i]["positive_ctxs"]]
#     df.loc[i+1,"Q"] = dataset[i]["question"]
#     df.loc[i+1,"A"] = answer_list

# df.to_csv(dev_output, sep='\t', header=False, index=False)

# # ---

# in_domain_input =  "./for_retriever_training/PluginLLM_test_in_domain.json"
# in_domain_output = "./for_retriever_training/PluginLLM_test_in_domain_qa.csv"

# dataset = read_json(in_domain_input)
# data_init = [[None]*2]*len(dataset)
# df = pd.DataFrame(data_init, index=range(1,len(dataset)+1), columns=["Q", "A"]).astype(str)
# df.index.name = 'id'
# for i in range(len(dataset)):
#     answer_list = [positive_ctx["title"] for positive_ctx in dataset[i]["positive_ctxs"]]
#     df.loc[i+1,"Q"] = dataset[i]["question"]
#     df.loc[i+1,"A"] = answer_list

# df.to_csv(in_domain_output, sep='\t', header=False, index=False)

# # ---

# out_domain_input = "./for_retriever_training/PluginLLM_test_out_domain.json"
# out_domain_output = "./for_retriever_training/PluginLLM_test_out_domain_qa.csv"

# dataset = read_json(out_domain_input)
# data_init = [[None]*2]*len(dataset)
# df = pd.DataFrame(data_init, index=range(1,len(dataset)+1), columns=["Q", "A"]).astype(str)
# df.index.name = 'id'
# for i in range(len(dataset)):
#     answer_list = [positive_ctx["title"] for positive_ctx in dataset[i]["positive_ctxs"]]
#     df.loc[i+1,"Q"] = dataset[i]["question"]
#     df.loc[i+1,"A"] = answer_list

# df.to_csv(out_domain_output, sep='\t', header=False, index=False)


# * ====================================================
# * 旧形式的fastchat数据集 , 用于评测，提供API检索结果，不保证有所需API，真实场景 

prompt = '''Please chooose the needed apis and return api_calling list according to the task_instruction in given format as the example.
input:
api_list = {}
task_instruction = {}
output:
'''

# path_list = [
#     [
#         "./splitted_dataset/train.jsonl",
#         "./retriever_result/result_split_train.json",
#         "./fastchat_dataset/DPR/train.json"
#     ],
#     [
#         "./splitted_dataset/dev.jsonl",
#         "./retriever_result/result_split_dev.json",
#         "./fastchat_dataset/DPR/dev.json"
#     ],
#     [
#         "./splitted_dataset/test_in_domain.jsonl",
#         "./retriever_result/result_split_test_in_domain.json",
#         "./fastchat_dataset/DPR/test_in_domain.json"
#     ],
#     [
#         "./splitted_dataset/test_out_domain.jsonl",
#         "./retriever_result/result_split_test_out_domain.json",
#         "./fastchat_dataset/DPR/test_out_domain.json"
#     ]
# ]

path_list = [
    [
        "./splitted_dataset/train.jsonl",
        "./retriever_result_BM25/result_train.json",
        "./fastchat_dataset/BM25/train.json"
    ],
    [
        "./splitted_dataset/dev.jsonl",
        "./retriever_result_BM25/result_dev.json",
        "./fastchat_dataset/BM25/dev.json"
    ],
    [
        "./splitted_dataset/test_in_domain.jsonl",
        "./retriever_result_BM25/result_test_in_domain.json",
        "./fastchat_dataset/BM25/test_in_domain.json"
    ],
    [
        "./splitted_dataset/test_out_domain.jsonl",
        "./retriever_result_BM25/result_test_out_domain.json",
        "./fastchat_dataset/BM25/test_out_domain.json"
    ]
]

if not os.path.exists("./fastchat_dataset/"):
    os.mkdir("./fastchat_dataset/")

apiset_list = read_jsonl(apiset_path)
api_list = []
api_dict = {}
for field in apiset_list:
    for field_name in field:
        api_list.extend(field[field_name])
        for api in field[field_name]:
            api_dict[api["api_name"]] = api

# all_dataset = []
for path in path_list:
    raw_dataset = read_jsonl(path[0])
    api_retriever_dataset = read_json(path[1])
    dataset = []
    for data_idx in range(len(raw_dataset)):
        raw_data = raw_dataset[data_idx]
        api_list_string = []
        for i in range(5):
            api_list_string.append(api_dict[api_retriever_dataset[data_idx]["ctxs"][i]["title"]])
        api_list_string = str(shuffle_list(api_list_string))
        if type(raw_data[0]) != list:
            answer_string = [raw_data[0]]
            answer_string[0]["responses"] = ["API_call_"+str(i) for i in range(len(api_dict[answer_string[0]["api"]]["responses"]))]
            answer_string = str(answer_string)
        else:
            answer_string = str(raw_data[0])
        data = {}
        data["id"]= path[0].split('/')[-1].split('.')[0]+'-'+('easy' if type(raw_data[0]) != list else 'difficult')+'-'+str(data_idx)
        data["conversations"]=[]
        data["conversations"].append(
            {"from":"human",
             "value":prompt.format(api_list_string, '"'+raw_data[1]+'"')
             })
        data["conversations"].append(
            {"from":"gpt",
             "value":answer_string
             })

        dataset.append(data)
        # all_dataset.append(data)

    write_json(path[2],dataset)


# * ====================================================
# * ============ fastchat_dataset_new ================== 用于评测，提供API检索结果，不保证有所需API，真实场景 


# prompt = '''Please chooose the needed apis and return api_calling list according to the task_instruction.
# Output format: [{{"api": "", "parameters": {{"": ""}}, "responses": ["API_call_0","API_call_1"]}},{{"api": "", "parameters": {{"": ""}}, "responses": ["API_call_2"]}}]
# Responses can be used as parameter value. The number of responses depends on information in api_list.

# Input:
# api_list = {}
# task_instruction = {}
# Output:
# '''

# # path_list = [
# #     [
# #         "./splitted_dataset/train.jsonl",
# #         "./retriever_result/result_split_train.json",
# #         "./fastchat_dataset_new/DPR/train.json"
# #     ],
# #     [
# #         "./splitted_dataset/dev.jsonl",
# #         "./retriever_result/result_split_dev.json",
# #         "./fastchat_dataset_new/DPR/dev.json"
# #     ],
# #     [
# #         "./splitted_dataset/test_in_domain.jsonl",
# #         "./retriever_result/result_split_test_in_domain.json",
# #         "./fastchat_dataset_new/DPR/test_in_domain.json"
# #     ],
# #     [
# #         "./splitted_dataset/test_out_domain.jsonl",
# #         "./retriever_result/result_split_test_out_domain.json",
# #         "./fastchat_dataset_new/DPR/test_out_domain.json"
# #     ]
# # ]

# path_list = [
#     [
#         "./splitted_dataset/train.jsonl",
#         "./retriever_result_BM25/result_train.json",
#         "./fastchat_dataset_new/BM25/train.json"
#     ],
#     [
#         "./splitted_dataset/dev.jsonl",
#         "./retriever_result_BM25/result_dev.json",
#         "./fastchat_dataset_new/BM25/dev.json"
#     ],
#     [
#         "./splitted_dataset/test_in_domain.jsonl",
#         "./retriever_result_BM25/result_test_in_domain.json",
#         "./fastchat_dataset_new/BM25/test_in_domain.json"
#     ],
#     [
#         "./splitted_dataset/test_out_domain.jsonl",
#         "./retriever_result_BM25/result_test_out_domain.json",
#         "./fastchat_dataset_new/BM25/test_out_domain.json"
#     ]
# ]

# if not os.path.exists("./fastchat_dataset_new/"):
#     os.mkdir("./fastchat_dataset_new/")

# apiset_list = read_jsonl(apiset_path)
# api_list = []
# api_dict = {}
# for field in apiset_list:
#     for field_name in field:
#         api_list.extend(field[field_name])
#         for api in field[field_name]:
#             api_dict[api["api_name"]] = api

# # all_dataset = []
# for path in path_list:
#     raw_dataset = read_jsonl(path[0])
#     api_retriever_dataset = read_json(path[1])
#     dataset = []
#     for data_idx in range(len(raw_dataset)):
#         raw_data = raw_dataset[data_idx]
#         api_list_string = []
#         for i in range(5):
#             api_list_string.append(api_dict[api_retriever_dataset[data_idx]["ctxs"][i]["title"]])
#         api_list_string = str(shuffle_list(api_list_string))
#         if type(raw_data[0]) != list:
#             answer_string = [raw_data[0]]
#             answer_string[0]["responses"] = ["API_call_"+str(i) for i in range(len(api_dict[answer_string[0]["api"]]["responses"]))]
#             answer_string = str(answer_string)
#         else:
#             answer_string = str(raw_data[0])
#         data = {}
#         data["id"]= path[0].split('/')[-1].split('.')[0]+'-'+('easy' if type(raw_data[0]) != list else 'difficult')+'-'+str(data_idx)
#         data["conversations"]=[]
#         data["conversations"].append(
#             {"from":"human",
#              "value":prompt.format(api_list_string, '"'+raw_data[1]+'"')
#              })
#         data["conversations"].append(
#             {"from":"gpt",
#              "value":answer_string
#              })

#         dataset.append(data)
#         # all_dataset.append(data)

#     write_json(path[2],dataset)

# * ====================================================
# * ============ fastchat_dataset_new ================== 检索结果+后处理，保证context包含所需API 


# prompt = '''Please chooose the needed apis and return api_calling list according to the task_instruction.
# Output format: [{{"api": "", "parameters": {{"": ""}}, "responses": ["API_call_0","API_call_1"]}},{{"api": "", "parameters": {{"": ""}}, "responses": ["API_call_2"]}}]
# Responses can be used as parameter value. The number of responses depends on information in api_list.

# Input:
# api_list = {}
# task_instruction = {}
# Output:
# '''

# path_list = [
#     [
#         "./splitted_dataset/train.jsonl",
#         "./retriever_result/result_split_train.json",
#         "./fastchat_dataset_new/train.json"
#     ],
#     [
#         "./splitted_dataset/dev.jsonl",
#         "./retriever_result/result_split_dev.json",
#         "./fastchat_dataset_new/dev.json"
#     ],
#     [
#         "./splitted_dataset/test_in_domain.jsonl",
#         "./retriever_result/result_split_test_in_domain.json",
#         "./fastchat_dataset_new/test_in_domain.json"
#     ],
#     [
#         "./splitted_dataset/test_out_domain.jsonl",
#         "./retriever_result/result_split_test_out_domain.json",
#         "./fastchat_dataset_new/test_out_domain.json"
#     ]
# ]

# if not os.path.exists("./fastchat_dataset/"):
#     os.mkdir("./fastchat_dataset/")

# apiset_list = read_jsonl(apiset_path)
# api_list = []
# api_dict = {}
# for field in apiset_list:
#     for field_name in field:
#         api_list.extend(field[field_name])
#         for api in field[field_name]:
#             api_dict[api["api_name"]] = api

# # all_dataset = []
# for path in path_list:
#     raw_dataset = read_jsonl(path[0])
#     api_retriever_dataset = read_json(path[1])
#     dataset = []
#     for data_idx in range(len(raw_dataset)):
#         raw_data = raw_dataset[data_idx]
#         api_name_list = [api_retriever_dataset[data_idx]["ctxs"][i]["title"] for i in range(5)]
#         gold_api_name_list = [data["api"] for data in raw_data[0]] if type(raw_data[0])==list else [raw_data[0]["api"]]
#         for gold_api in gold_api_name_list:
#             if gold_api not in api_name_list:
#                 for i in range(len(api_name_list)-1,-1,-1):
#                     if api_name_list[i] not in gold_api_name_list:
#                         api_name_list[i] = gold_api
#                         break
#         api_list_string = str(shuffle_list([ api_dict[api_name] for api_name in api_name_list]))
#         if type(raw_data[0]) != list:
#             answer_string = [raw_data[0]]
#             answer_string[0]["responses"] = ["API_call_"+str(i) for i in range(len(api_dict[answer_string[0]["api"]]["responses"]))]
#             answer_string = str(answer_string)
#         else:
#             answer_string = str(raw_data[0])
#         data = {}
#         data["id"]= path[0].split('/')[-1].split('.')[0]+'-'+('easy' if type(raw_data[0]) != list else 'difficult')+'-'+str(data_idx)
#         data["conversations"]=[]
#         data["conversations"].append(
#             {"from":"human",
#              "value":prompt.format(api_list_string, '"'+raw_data[1]+'"')
#              })
#         data["conversations"].append(
#             {"from":"gpt",
#              "value":answer_string
#              })

#         dataset.append(data)
#         # all_dataset.append(data)

#     write_json(path[2],dataset)