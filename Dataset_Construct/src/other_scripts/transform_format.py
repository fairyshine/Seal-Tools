from utils import *
from method import *

prompt = '''Please chooose the needed apis and return api_calling list according to the task_instruction in given format as the example.
input:
api_list = {}
task_instruction = {}
output:
'''

path_list = [
    "./splitted_dataset/train.jsonl",
    "./splitted_dataset/dev.jsonl",
    "./splitted_dataset/test_in_domain.jsonl",
    "./splitted_dataset/test_out_domain.jsonl",    
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
    raw_dataset = read_jsonl(path)
    dataset = []
    for data_idx in range(len(raw_dataset)):
        raw_data = raw_dataset[data_idx]
        if type(raw_data[0]) != list:
            api_list_string = [api_dict[raw_data[0]["api"]]]
            counter = 4
            while(counter):
                idx = random.randint(0,len(api_list)-1)
                if api_list[idx]["api_name"] != raw_data[0]["api"]:
                    api_list_string.append(api_list[idx])
                    counter -= 1
            # TODO 打乱api顺序
            api_list_string = str(shuffle_list(api_list_string))
            answer_string = str([raw_data[0]])
        else:
            api_list_string = str(shuffle_list([api_dict[api["api"]] for api in raw_data[0]]))
            answer_string = str(raw_data[0])
        data = {}
        data["id"]= path.split('/')[-1].split('.')[0]+'-'+('easy' if type(raw_data[0]) != list else 'difficult')+'-'+str(data_idx)
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

    write_json("./fastchat_dataset/"+path.split('/')[-1][:-1],dataset)

# write_json("./fastchat_dataset/train_dev.json",all_dataset)