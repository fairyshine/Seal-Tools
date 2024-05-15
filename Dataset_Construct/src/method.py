import copy
import json
import os
import random

from rich.progress import track

from prompts import *
from rules import *
from utils import *

fieldset_raw_path = "./raw_dataset/fieldset_raw.jsonl"
fieldset_path = "./dataset/fieldset.jsonl"
field_path = "./dataset/field.jsonl"

subfield_raw_path = "./raw_dataset/subfield_raw.jsonl"
subfield_path = "./dataset/subfield.jsonl"

api_unfiltered_raw_path = "./raw_dataset/api_unfiltered_raw.jsonl"
api_unfiltered_path = "./dataset/api_unfiltered.jsonl"
apiset_path = "./dataset/api_set.jsonl"

parameter_path = "./dataset/parameter.jsonl"
parameter_fillin_raw_path = "./raw_dataset/parameter_fillin_raw.jsonl"
parameter_fillin_path = "./dataset/parameter_fillin.jsonl"

easy_case_raw_path = "./raw_dataset/easy_case_raw.jsonl"
easy_case_path = "./dataset/easy_case.jsonl"
api_selection_raw_path = "./raw_dataset/api_selection_raw.jsonl"
api_selection_path = "./dataset/api_selection.jsonl"
difficult_case_raw_path = "./raw_dataset/difficult_case_raw.jsonl"
difficult_case_path = "./dataset/difficult_case.jsonl"
difficult_case_fixed_path = "./dataset/difficult_case_fixed.jsonl"

def directory_check():
    if not os.path.exists("./raw_dataset/"):
        os.mkdir("./raw_dataset/")
    if not os.path.exists("./dataset/"):
        os.mkdir("./dataset/")


# * ====== 生成父领域 ======
def fieldset_generation(chat_func):
    #初始化
    fieldset_raw_list = []
    fieldset_list = []
    example_list = initial_field_list
    #主循环
    while(len(example_list) >= 2):
        demo1,demo2 = example_list.pop(random.randint(0,len(example_list)-1)), example_list.pop(random.randint(0,len(example_list)-1))
        prompt = prompt_fieldset_generation.format(demo1, demo2)
        raw_output, _, answer_text = chat_func(prompt)
        fieldset_raw_list.append({"INPUT":prompt,"OUTPUT":raw_output})
        # * 后处理，得到结果
        try:
            answer_text = re.sub("\n", "", answer_text)
            answer_list_text = match_given_pattern(answer_text,r'\[.+\]')
            field_part = json.loads(answer_list_text)
            if type(field_part) == list and type(field_part[0]) == str:
                fieldset_list.append(list(set(field_part)))
        except:
            pass
        #存储
        write_jsonl(fieldset_raw_path,fieldset_raw_list)
        write_jsonl(fieldset_path,fieldset_list)


def field_filter():
    #初始化
    fieldset_list = read_jsonl(fieldset_path)
    field_counter_dict = {}
    #主循环
    for field_part in fieldset_list: # 统计field出现次数
        for field in field_part:
            if field not in field_counter_dict:
                field_counter_dict[field] = 0
            else:
                field_counter_dict[field] += 1
    field_list = [] #initial_field_list
    for field in field_counter_dict: # 筛选出高频出现的field
        if field_counter_dict[field] >= 1 and field not in field_list:#len(fieldset_list)//len(fieldset_list):
            field_list.append(field)
        #存储
        write_jsonl(field_path,[field_list])


# * ====== 生成子领域 ======
def subfield_generation(chat_func):
    #初始化
    field_list = read_jsonl(field_path)[0]
    check_file_path(subfield_raw_path)
    check_file_path(subfield_path)
    subfield_raw_list = read_jsonl(subfield_raw_path)
    subfield_list = read_jsonl(subfield_path)
    #主循环
    for field_id in track(range(len(subfield_list),len(field_list)),description="Subfield Generating ..."):
        field = field_list[field_id]
        while(True): #确保每个子领域均顺利生成
            prompt = prompt_subfield_generation.format(field)
            raw_output, _, answer_text = chat_func(prompt)
            subfield_raw_list.append({"INPUT":prompt,"OUTPUT":raw_output})
            # * 后处理，得到结果
            try:
                answer_text = re.sub("\n", "", answer_text)
                answer_list_text = match_given_pattern(answer_text,r'\[.+\]')
                subfield = json.loads(answer_list_text)
                if type(subfield) == list and type(subfield[0]) == str:
                    # 添加初始例子 Environment/Weather
                    if field == "Environment" and "Weather" not in subfield:
                        subfield.append("Weather")
                    subfield_list.append({field:subfield})
                    #存储
                    write_jsonl(subfield_raw_path,subfield_raw_list)
                    write_jsonl(subfield_path,subfield_list)
                    break
            except:
                pass


# * ====== 生成领域内API ======
def api_check(api_dict):
    if ("api_name" not in api_dict) or ("api_description" not in api_dict) \
    or ("field" not in api_dict) or ("parameters" not in api_dict) \
    or ("required" not in api_dict) or ("responses" not in api_dict):
        return 0
    
    #检查required是否都在parameters里
    if api_dict["required"] != []:
        for key_parameter in api_dict["required"]:
            if key_parameter not in api_dict["parameters"]:
                return 0      
    #检查parameters格式完整性 
    if api_dict["parameters"] != {}:
        for parameter in api_dict["parameters"]:
            if ("type" not in api_dict["parameters"][parameter]) \
            or ("description" not in api_dict["parameters"][parameter]):
                return 0
            if api_dict["parameters"][parameter]["type"] not in api_type_list:
                return 0
    #检查responses格式完整性
    if api_dict["responses"] == {}:
        return 0
    for response in api_dict["responses"]:
        if ("type" not in api_dict["responses"][response]) \
        or ("description" not in api_dict["responses"][response]):
            return 0
        if api_dict["responses"][response]["type"] not in api_type_list:
            return 0
    # #检查parameters中required的部分是否都有参数取值实例
    # for parameter in api_dict["parameters"]:
    #     type_str = api_dict["parameters"][parameter]["type"]
    #     description = api_dict["parameters"][parameter]["description"]
    #     try:
    #         example_string = match_given_pattern(description,'\(e\.g\.,.+\)')[6:-1]
    #         example_list = [ example.strip(' ').strip(',').strip('"').strip("'") for example in example_string.split(',')]
    #         for example in example_list:
    #             try:
    #                 if type_str == "int":
    #                     int(example)
    #                 if type_str == "float":
    #                     float(example)
    #                 if type_str == "bool":
    #                     bool(example)
    #             except:
    #                 return 0
    #     except:
    #         if parameter in api_dict["required"]:
    #             return 0
    return 1

def api_generation(chat_func):
    #初始化
    subfield_list = read_jsonl(subfield_path)
    check_file_path(api_unfiltered_raw_path)
    check_file_path(api_unfiltered_path)
    check_file_path(apiset_path)
    api_unfiltered_raw_list = read_jsonl(api_unfiltered_raw_path)
    api_unfiltered_list = read_jsonl(api_unfiltered_path)
    apiset_list = read_jsonl(apiset_path)
    api_list = [initial_api]
    for apiset in apiset_list:
        for key in apiset:
            api_list.extend(apiset[key])

    field_subfield_list = []
    for i in range(len(subfield_list)):
        for field in subfield_list[i]:
            for subfield in subfield_list[i][field]:
                field_subfield_list.append([field,subfield])

    #主循环
    for field_id in track(range(len(apiset_list)-1,len(field_subfield_list)),description="API Generating ..."):
        field = field_subfield_list[field_id][0]
        subfield = field_subfield_list[field_id][1]
        field_subfield = field + "/" + subfield
        no_output_flag = 0
        field_api_list = []
        while(no_output_flag<2):
            id_ICL = 0#random.randint(0,len(api_list)-1)
            field_ICL = api_list[id_ICL]["field"].split("/")
            prompt = prompt_api_generation.format(field_ICL[0],field_ICL[1],json.dumps(api_list[id_ICL]),field,subfield)
            raw_output, _, answer_text = chat_func(prompt)
            api_unfiltered_raw_list.append({"INPUT":prompt,"OUTPUT":raw_output})
            # - 后处理，得到结果
            answer_split_text = re.split(r'\n{2,}',answer_text)
            for answer_split in answer_split_text:
                count = 0
                try:
                    answer_split = re.sub("\n", "", answer_split)
                    api_unfiltered_part = match_given_pattern(answer_split,r'\{.+\}')
                    api_unfiltered = json.loads(api_unfiltered_part)
                    if api_check(api_unfiltered) and api_unfiltered["field"] == field_subfield:
                        api_unfiltered_list.append(api_unfiltered)
                        # * api_filter 筛选 
                        duplicate_flag = 0
                        for api in api_list:
                            if str_similarity(api["api_name"],api_unfiltered["api_name"]) >= 0.8:
                                duplicate_flag = 1
                                break
                        if duplicate_flag == 0:
                            field_api_list.append(api_unfiltered)
                            api_list.append(api_unfiltered)
                            count += 1
                            print("领域：",field_subfield," |  生成API：",api_unfiltered["api_name"])
                except:
                    pass
            if count == 0:
                no_output_flag += 1
        apiset_list.append({field_subfield:copy.deepcopy(field_api_list)})
        #存储
        write_jsonl(api_unfiltered_raw_path,api_unfiltered_raw_list)
        write_jsonl(api_unfiltered_path,api_unfiltered_list)
        write_jsonl(apiset_path,apiset_list)


# * ====== 生成API参数取值填充 ======
def get_example_list(type_str, description, mode):
    flag = 1
    try:
        example_string = match_given_pattern(description,'\(e\.g\.,.+\)')[6:-1]
        example_list = [ example.strip(' ').strip(',').strip('"').strip("'") for example in example_string.split(',')]
        for example in example_list:
            try:
                if type_str == "int":
                    int(example)
                if type_str == "float":
                    float(example)
                if type_str == "bool":
                    bool(example)
            except:
                flag = 0
    except:
        flag = 0
    match mode:
        case "judge":
            return bool(flag)
        case "get":
            return example_list

def api_param_example_check():
    apiset_list = read_jsonl(apiset_path)
    wait_list = { key:{} for key in api_type_list}
    #寻找required参数中取值实例缺失的部分
    for api_set in apiset_list:
        for field in api_set:
            api_list = api_set[field]
            for api in api_list:
                for parameter in api["required"]:
                    type_str = api["parameters"][parameter]["type"]
                    description = api["parameters"][parameter]["description"]
                    if not get_example_list(type_str, description, "judge"):
                        if api["api_name"] not in wait_list[type_str]:
                            wait_list[type_str][api["api_name"]] = {}
                        wait_list[type_str][api["api_name"]][parameter] = description

    # 打印wait_list大致情况
    # print("wait_list: ")
    # for type_str in wait_list:
    #     print("================== ==================")
    #     print(type_str)
    #     print("数量：",len(wait_list[type_str]))
    #     for param in wait_list[type_str]:
    #         print(param, " ", wait_list[type_str][param])

    # 判断是否能用规则处理
    for_generate_list = { key:{} for key in api_type_list}
    for type_str in wait_list:
        for api in wait_list[type_str]:
            for parameter in wait_list[type_str][api]:
                description = wait_list[type_str][api][parameter]
                if not rules_for_parameters(type_str, parameter, description, "judge"):
                    if api not in for_generate_list[type_str]:
                        for_generate_list[type_str][api] = {}
                    for_generate_list[type_str][api][parameter] = description


    parameter_list = [{api:for_generate_list["str"][api]} for api in for_generate_list["str"]]
    write_jsonl(parameter_path,parameter_list)

def api_param_example_generation(chat_func):
    parameter_list = read_jsonl(parameter_path)
    check_file_path(parameter_fillin_raw_path)
    check_file_path(parameter_fillin_path)
    parameter_fillin_raw_list = read_jsonl(parameter_fillin_raw_path)
    parameter_fillin_list = read_jsonl(parameter_fillin_path)
    for api_id in track(range(len(parameter_fillin_list),len(parameter_list)), description="API parameters fillin ing ..."):
        parameter = parameter_list[api_id]
        for api in parameter:
            api_answer_dict = {}
            api_answer_dict[api]={}
            for param in parameter[api]:
                param_name = param
                param_description = parameter[api][param]
                while(True): #确保每个子领域均顺利生成
                    prompt = prompt_api_param.format(param_description)
                    raw_output, _, answer_text = chat_func(prompt)
                    parameter_fillin_raw_list.append({"INPUT":prompt,"OUTPUT":raw_output})
                    # * 后处理，得到结果 
                    try:
                        answer_list_text = match_given_pattern(answer_text,r'\[.+\]')
                        answer_list = json.loads(answer_list_text)
                        print(answer_list)
                        api_answer_dict[api][param_name]=[answer_list, param_description]
                        break
                    except:
                        pass
            parameter_fillin_list.append(api_answer_dict)
            write_jsonl(parameter_fillin_raw_path, parameter_fillin_raw_list)
            write_jsonl(parameter_fillin_path, parameter_fillin_list)

def get_api_param_example(api_name, parameter, type_str, description):
    parameter_fillin_list = read_jsonl(parameter_fillin_path)
    parameter_fillin_dict = {}
    for param in parameter_fillin_list:
        for key in param:
            parameter_fillin_dict[key] = param[key]

    if rules_for_parameters(type_str, parameter, description, "judge"):
        return rules_for_parameters(type_str, parameter, description, "generate")
    elif get_example_list(type_str, description, "judge"):
        return random.choice(get_example_list(type_str, description, "get"))
    else:
        return random.choice(parameter_fillin_dict[api_name][parameter][0])
    
def get_api_calling(api):
    api_calling = {}
    api_calling["api"] = api["api_name"]
    api_calling["parameters"] = {}
    for parameter in api["parameters"]:
        type_str = api["parameters"][parameter]["type"]
        description = api["parameters"][parameter]["description"]
        if parameter in api["required"] or ((random.random() >= 0.5) and (get_example_list(type_str, description, "judge"))):
            api_calling["parameters"][parameter] = get_api_param_example(api["api_name"], parameter, type_str, description)
    return api_calling

def get_api_calling_list(api_list):
    api_calling_list = []
    idx_response = 0
    for api in api_list:
        api_calling = {}
        api_calling["api"] = api["api_name"]
        api_calling["parameters"] = {}
        for parameter in api["parameters"]:
            type_str = api["parameters"][parameter]["type"]
            description = api["parameters"][parameter]["description"]
            if parameter in api["required"] or ((random.random() >= 0.5) and (get_example_list(type_str, description, "judge"))):
                api_calling["parameters"][parameter] = get_api_param_example(api["api_name"], parameter, type_str, description)
        api_calling["responses"] = []
        for _ in api["responses"]:
            api_calling["responses"].append("API_call_"+str(idx_response))
            idx_response += 1
        api_calling_list.append(api_calling)
    return api_calling_list

# * ====== 生成简单用例 ======
def easy_usecase_generation(chat_func):
    apiset_list = read_jsonl(apiset_path)
    api_list = []
    for field in apiset_list:
        for field_name in field:
            api_list.extend(field[field_name])
    check_file_path(easy_case_raw_path)
    check_file_path(easy_case_path)
    easy_case_raw_list = read_jsonl(easy_case_raw_path)
    easy_case_list = read_jsonl(easy_case_path)
    for api_id in track(range(len(easy_case_list),len(api_list)), description="easy case generating ..."):
        while(True): #确保每个API均顺利生成一个简单样例
            api = api_list[api_id]
            api_calling = get_api_calling(api)
            prompt = prompt_easy_case.format(str(api_calling))
            raw_output, _, answer_text = chat_func(prompt)
            easy_case_raw_list.append({"INPUT":prompt,"OUTPUT":raw_output})
            # * 后处理，得到结果 
            try:
                task_description = match_given_pattern(answer_text.split("Task description")[-1],r'\[.+\]')[1:-1].strip('"').strip("'")
                print(task_description)
                # flag = 1
                # for parameter in api_calling["parameters"]:
                #     if api_calling["parameters"][parameter] not in task_description:
                #         flag = 0
                # if flag != 1:
                #     continue
                easy_case = []
                easy_case.append(api_calling)
                easy_case.append(task_description)
                easy_case_list.append(easy_case)
                write_jsonl(easy_case_raw_path, easy_case_raw_list)
                write_jsonl(easy_case_path, easy_case_list)
                break
            except:
                pass


# * ====== 生成复杂用例 ======
def api_pool_selection(chat_func):
    check_file_path(apiset_path)
    apiset_list = read_jsonl(apiset_path)
    api_list = []
    for field in apiset_list:
        for field_name in field:
            api_list.extend(field[field_name])
    check_file_path(api_selection_raw_path)
    check_file_path(api_selection_path)
    api_selection_raw_list = read_jsonl(api_selection_raw_path)
    api_selection_list = read_jsonl(api_selection_path)
    api_selection_index_list = []

    while(True):
        random_numbers_list = random.sample(range(0, len(api_list)), 100)
        api_name_pool = [api_list[i]["api_name"] for i in random_numbers_list]
        api_pool = [{api_list[i]["api_name"]:api_list[i]["api_description"]} for i in random_numbers_list]
        prompt = prompt_api_selection.format(str(api_pool))
        raw_output, _, answer_text = chat_func(prompt)
        api_selection_raw_list.append({"INPUT":prompt,"OUTPUT":raw_output})
        write_jsonl(api_selection_raw_path, api_selection_raw_list)
        # * 后处理，得到结果 
        try:
            api_selection = eval(match_given_pattern(answer_text.split("selected_apis")[-1].split("task_description")[0],r'\[.+\]'))
            for api in api_selection:
                if api not in api_pool:
                    continue
            api_selection_index = [random_numbers_list[api_name_pool.index(api)] for api in api_selection]
            flag = 1
            for api_selection_index_before in api_selection_index_list:
                if set_similarity(set(api_selection_index),set(api_selection_index_before)) >= 0.8:
                    flag = 0
            if flag == 1:
                print("api_selection: ", api_selection)
                api_selection_list.append(api_selection)
                write_jsonl(api_selection_path, api_selection_list)
                break
        except:
            pass

def api_calling_check(api_calling,api_information):
    if ("api" not in api_calling) or ("parameters" not in api_calling) or ("responses" not in api_calling):
        return 0
    
    if api_information["required"] != []:
        for key_parameter in api_information["required"]:
            if key_parameter not in api_calling["parameters"]:
                return 0

    for parameter in api_calling["parameters"]:
        value = api_calling["parameters"][parameter]
        if parameter not in api_information["parameters"]:
            return 0
        if "API_call_" in str(value):
            if str(value) in api_calling["responses"]:
                return 0
        
    if len(api_calling["responses"]) != len(api_information["responses"]):
        return 0
    
    return 1

# def difficult_usecase_generation(chat_func): #-有参数填充版
#     check_file_path(apiset_path)
#     apiset_list = read_jsonl(apiset_path)
#     api_dict = {}
#     for field in apiset_list:
#         for field_name in field:
#             for api in field[field_name]:
#                 api_dict[api["api_name"]] = api
#     check_file_path(api_selection_path)
#     api_selection_list = read_jsonl(api_selection_path)
#     check_file_path(difficult_case_raw_path)
#     check_file_path(difficult_case_path)
#     difficult_case_raw_list = read_jsonl(difficult_case_raw_path)
#     difficult_case_list = read_jsonl(difficult_case_path)
#     for idx in track(range(len(difficult_case_list),len(api_selection_list)), description="difficult case generating..."):
#         duplicate_flag = 0
#         while(True): #确保每个API均顺利生成一个简单样例
#             duplicate_flag += 1
#             if duplicate_flag >= 5:
#                 difficult_case_list.append([None,None])
#                 write_jsonl(difficult_case_raw_path, difficult_case_raw_list)
#                 write_jsonl(difficult_case_path, difficult_case_list)
#                 break                
#             api_information_list = [copy.deepcopy(api_dict[api_name]) for api_name in api_selection_list[idx]]
#             api_calling = get_api_calling_list(api_information_list)
#             for api_idx in range(len(api_information_list)):
#                 for parameter in api_information_list[api_idx]["parameters"]:
#                     api_information_list[api_idx]["parameters"][parameter]["description"] = api_information_list[api_idx]["parameters"][parameter]["description"].split("(e.g.")[0].strip(" ")
#             prompt = prompt_difficult_case.format(str(api_information_list),str(api_calling))
#             raw_output, _, answer_text = chat_func(prompt)
#             print("=============")
#             print("ChatGPT's answer:")
#             print(answer_text)
#             difficult_case_raw_list.append({"INPUT":prompt,"OUTPUT":raw_output})
#             # * 后处理，得到结果 
#             try:
#                 task_description = answer_text.replace("\n","").split("task_description")[-1].split("[")[1].split("]")[0].strip('"').strip("'")
#                 if ("API_call_" or '"api"' or "'api'" or '"parameters"' or "'parameters'") in task_description:
#                     continue
#                 modified_api_calling_list = json.loads(match_given_pattern(answer_text.replace("\n","").split("modified_api_calling")[-1],r'\[.+\]').replace("'",'"'))
#                 print("=============")
#                 print("task description:")
#                 print(task_description)
#                 print("modified api calling list:")
#                 print(modified_api_calling_list)
#                 flag = 1
#                 for api_calling in modified_api_calling_list:
#                     if not api_calling_check(api_calling,api_dict[api_calling["api"]]):
#                         flag = 0
#                         break
#                 if flag == 1:
#                     difficult_case_list.append([task_description,modified_api_calling_list])
#                     write_jsonl(difficult_case_raw_path, difficult_case_raw_list)
#                     write_jsonl(difficult_case_path, difficult_case_list)
#                     break
#             except:
#                 pass    

# def difficult_usecase_generation(chat_func): #-无参数填充版
#     check_file_path(apiset_path)
#     apiset_list = read_jsonl(apiset_path)
#     api_dict = {}
#     for field in apiset_list:
#         for field_name in field:
#             for api in field[field_name]:
#                 api_dict[api["api_name"]] = api
#     check_file_path(api_selection_path)
#     api_selection_list = read_jsonl(api_selection_path)
#     check_file_path(difficult_case_raw_path)
#     check_file_path(difficult_case_path)
#     difficult_case_raw_list = read_jsonl(difficult_case_raw_path)
#     difficult_case_list = read_jsonl(difficult_case_path)
#     for idx in track(range(len(difficult_case_list),len(api_selection_list)), description="difficult case generating..."):
#         duplicate_flag = 0
#         while(True): #确保每个API均顺利生成一个简单样例
#             duplicate_flag += 1
#             if duplicate_flag >= 5:
#                 difficult_case_list.append([])
#                 write_jsonl(difficult_case_path, difficult_case_list)
#                 break                
#             api_information_list = [api_dict[api_name] for api_name in api_selection_list[idx]]
#             prompt = prompt_difficult_case_no_value.format(str(api_information_list))
#             raw_output, _, answer_text = chat_func(prompt)
#             print("=============")
#             print("ChatGPT's answer:")
#             print(answer_text)
#             difficult_case_raw_list.append({"INPUT":prompt,"OUTPUT":raw_output})
#             # * 后处理，得到结果 
#             try:
#                 task_description = answer_text.replace("\n","").split("detailed_task_description")[-1].split("[")[1].split("]")[0].strip('"').strip("'")
#                 if ("API_call_" or '"api"' or "'api'" or '"parameters"' or "'parameters'") in task_description:
#                     continue
#                 api_calling_list = json.loads(match_given_pattern(answer_text.replace("\n","").split("detailed_task_description")[0].split("api_calling")[-1],r'\[.+\]').replace("'",'"'))
#                 print("=============")
#                 print("task description:")
#                 print(task_description)
#                 print("api calling list:")
#                 print(api_calling_list)
#                 flag = 1
#                 for api_calling in api_calling_list:
#                     if not api_calling_check(api_calling,api_dict[api_calling["api"]]):
#                         flag = 0
#                         break
#                 if flag == 1:
#                     difficult_case_list.append([task_description,api_calling_list])
#                     write_jsonl(difficult_case_raw_path, difficult_case_raw_list)
#                     write_jsonl(difficult_case_path, difficult_case_list)
#                     break
#             except:
#                 pass    

# def difficult_case_parameter_variation():
#     apiset_list = read_jsonl(apiset_path)
#     api_dict = {}
#     for field in apiset_list:
#         for field_name in field:
#             for api in field[field_name]:
#                 api_dict[api["api_name"]] = api
#     check_file_path(difficult_case_path)
#     difficult_case_list = read_jsonl(difficult_case_path)
#     check_file_path(difficult_case_fixed_path)
#     difficult_case_fixed_list = read_jsonl(difficult_case_fixed_path)
#     for idx in range(len(difficult_case_fixed_list),len(difficult_case_list)):
#         for api_idx in range(len(difficult_case_list[idx][1])):
#             api_name = difficult_case_list[idx][1][api_idx]["api"]
#             for parameter_name in difficult_case_list[idx][1][api_idx]["parameters"]:
#                 parameter_type = api_dict[api_name]["parameters"][parameter_name]["type"]
#                 parameter_description = api_dict[api_name]["parameters"][parameter_name]["description"]
#                 # *判断api参数取值是否需要修改并修改
#                 # *根据difficult case实际生成结果再做修改，目前看只需修改str类型规则部分
#                 pass
#     write_jsonl(difficult_case_fixed_path, difficult_case_fixed_list)

def difficult_usecase_generation(chat_func): # - 填空版 给出api calling格式
    check_file_path(apiset_path)
    apiset_list = read_jsonl(apiset_path)
    api_dict = {}
    for field in apiset_list:
        for field_name in field:
            for api in field[field_name]:
                api_dict[api["api_name"]] = api
    check_file_path(api_selection_path)
    api_selection_list = read_jsonl(api_selection_path)
    check_file_path(difficult_case_raw_path)
    check_file_path(difficult_case_path)
    difficult_case_raw_list = read_jsonl(difficult_case_raw_path)
    difficult_case_list = read_jsonl(difficult_case_path)
    for idx in track(range(len(difficult_case_list),len(api_selection_list)), description="difficult case generating..."):
        duplicate_flag = 0
        while(True): #确保每个API均顺利生成一个简单样例
            duplicate_flag += 1
            if duplicate_flag >= 4:
                difficult_case_list.append([None,None])
                write_jsonl(difficult_case_raw_path, difficult_case_raw_list)
                write_jsonl(difficult_case_path, difficult_case_list)
                break                
            api_information_list = [copy.deepcopy(api_dict[api_name]) for api_name in api_selection_list[idx]]
            api_calling = get_api_calling_list(api_information_list)
            for calling_idx in range(len(api_calling)):
                for parameter in api_calling[calling_idx]["parameters"]:
                    api_calling[calling_idx]["parameters"][parameter] = "___"
            for api_idx in range(len(api_information_list)):
                api_name = api_information_list[api_idx]["api_name"]
                for parameter in api_information_list[api_idx]["parameters"]: #TODO 添加example
                    parameter_type = api_information_list[api_idx]["parameters"][parameter]["type"]
                    parameter_description = api_information_list[api_idx]["parameters"][parameter]["description"]
                    if ("(e.g." not in parameter_description) and (parameter in api_information_list[api_idx]["required"]):
                        api_information_list[api_idx]["parameters"][parameter]["description"] += " (e.g., "+ str(get_api_param_example(api_name, parameter, parameter_type, parameter_description)) +")"

            prompt = prompt_difficult_case_fillin.format(str(api_information_list),str(api_calling).replace("'___'","___"))
            try:
                raw_output, _, answer_text = chat_func(prompt)
            except:
                continue
            print("=============")
            print("ChatGPT's answer:")
            print(answer_text)
            difficult_case_raw_list.append({"INPUT":prompt,"OUTPUT":raw_output})
            # * 后处理，得到结果 
            try:
                improved_api_calling_list = json.loads(match_given_pattern(answer_text.replace("\n","").split("improved_api_calling")[-1].split("task_description")[0],r'\[.+\]').replace("'",'"'))
                task_description = answer_text.replace("\n","").split("task_description")[-1].split("[")[1].split("]")[0].strip('"').strip("'")
                if ("API_call_" or '"api"' or "'api'" or '"parameters"' or "'parameters'") in task_description:
                    continue
                print("=============")
                print("improved api calling list:")
                print(improved_api_calling_list)
                print("task description:")
                print(task_description)
                flag = 1
                for api_calling in improved_api_calling_list:
                    if not api_calling_check(api_calling,api_dict[api_calling["api"]]):
                        flag = 0
                        break
                if flag == 1:
                    difficult_case_list.append([improved_api_calling_list, task_description])
                    write_jsonl(difficult_case_raw_path, difficult_case_raw_list)
                    write_jsonl(difficult_case_path, difficult_case_list)
                    break
            except:
                pass