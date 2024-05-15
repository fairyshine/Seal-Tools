import pandas as pd

from method import *
from utils import *

def field_information_statistics():
    field_list = read_jsonl(subfield_path)
    subfield_count = 0
    for field in field_list:
        for field_name in field:
            subfield_count += len(field[field_name])
    print("领域数量： ",len(field_list))
    print("子领域数量：",subfield_count)
    print("\n")

def api_information_statistics():
    apiset_list = read_jsonl(apiset_path)
    api_count = 0
    for apiset in apiset_list:
        for field_name in apiset:
            api_count += len(apiset[field_name])
    print("已尝试的子领域数量： ",len(apiset_list))
    print("已生成的API数量：  ",api_count)

    type_set = set()
    for apiset in apiset_list:
        for field_name in apiset:
            for api in apiset[field_name]:
                try:
                    for param in api["parameters"]:
                        type_inform = api["parameters"][param]["type"]
                        if type_inform not in type_set:
                            type_set.add(type_inform)
                except:
                    pass
    print("包含的type类型：",type_set)

def api_generation_statistics():
    #初始化
    check_file_path(api_unfiltered_raw_path)
    api_unfiltered_raw_list = read_jsonl(api_unfiltered_raw_path)
    api_unfiltered_list = []
    api_list = [initial_api]
    unfiltered_counter_list = []
    filtered_counter_list = []
    #主循环
    for idx in range(0,len(api_unfiltered_raw_list)):
        unfiltered_counter = 0
        filtered_counter = 0
        raw_output = api_unfiltered_raw_list[idx]["OUTPUT"]
        answer_text = raw_output['choices'][0]['message']['content'].encode('utf-8').decode('utf-8')
        # - 后处理，得到结果
        answer_split_text = re.split(r'\n{2,}',answer_text)
        for answer_split in answer_split_text:
            try:
                answer_split = re.sub("\n", "", answer_split)
                api_unfiltered_part = match_given_pattern(answer_split,r'\{.+\}')
                api_unfiltered = json.loads(api_unfiltered_part)
                if api_check(api_unfiltered):
                    api_unfiltered_list.append(api_unfiltered)
                    unfiltered_counter += 1
                    # * api_filter 筛选 
                    duplicate_flag = 0
                    for api in api_list:
                        if str_similarity(api["api_name"],api_unfiltered["api_name"]) >= 0.8:
                            duplicate_flag = 1
                            break
                    if duplicate_flag == 0:
                        api_list.append(api_unfiltered)
                        filtered_counter += 1
            except:
                pass
        unfiltered_counter_list.append(unfiltered_counter)
        filtered_counter_list.append(filtered_counter)
    
    print(len(api_unfiltered_raw_list)) #14324
    print(len(unfiltered_counter_list))
    print(len(filtered_counter_list))

    added_unfiltered_counter = 0
    added_filtered_counter = 0
    added_unfiltered_counter_list = []
    added_filtered_counter_list = []
    N = 200
    for i in range(len(api_unfiltered_raw_list)):
        added_unfiltered_counter += unfiltered_counter_list[i]
        added_filtered_counter += filtered_counter_list[i]
        if i%N == N-1:
            added_unfiltered_counter_list.append(added_unfiltered_counter)
            added_filtered_counter_list.append(added_filtered_counter)
            added_unfiltered_counter = 0
            added_filtered_counter = 0

    print(len(added_unfiltered_counter_list))
    print(len(added_filtered_counter_list))
    for i in range(len(added_filtered_counter_list)):
        print(added_unfiltered_counter_list[i],"    ",added_filtered_counter_list[i])
    print(sum(filtered_counter_list))

    data_init = [[None]*2]*len(added_unfiltered_counter_list)
    df = pd.DataFrame(data_init, index=range(0,len(added_unfiltered_counter_list)), columns=["unfiltered", "filtered"]).astype(float)
    df.index.name = 'N'
    for i in range(len(added_unfiltered_counter_list)):
        df.loc[i,"unfilterd"] = added_unfiltered_counter_list[i]
        df.loc[i,"filtered"] = added_filtered_counter_list[i]
     

    df.to_csv('.//API生成分析结果.csv',float_format="%d")