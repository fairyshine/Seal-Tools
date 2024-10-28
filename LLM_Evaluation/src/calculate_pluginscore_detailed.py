from llm_tools.utils import read_jsonl,write_json
import json
import os

def calculate_score_ToolLearning(raw_dataset):
    result_dict = {}

    correct_format_num = 0

    correct_api_num = 0
    predict_api_num = 0
    gold_api_num = 0

    correct_param_num = 0
    predict_param_num = 0
    gold_param_num = 0

    for data in raw_dataset:
        gold_answer = json.loads(json.dumps(eval(data['gold_data']["conversations"][1]["value"])))

        gold_api_num += len(gold_answer)
        for gold_api in gold_answer:
            gold_param_num += len(gold_api['parameters'])

        if data['predict'][0] != -1:
            predict_answer = data['predict'][0]
            correct_format_num += 1
            for predict_api in predict_answer:
                if "api" in predict_api:
                    predict_api_num += 1
                    if "parameters" in predict_api and type(predict_api["parameters"])==dict:
                        predict_param_num += len(predict_api["parameters"])
                    gold_idx = -1
                    for idx in range(len(gold_answer)):
                        if gold_answer[idx]["api"] == predict_api["api"]:
                            gold_idx = idx
                            break
                    if gold_idx != -1:
                        correct_api_num += 1
                        if "parameters" in predict_api and type(predict_api["parameters"])==dict:
                            for parameter_name in predict_api["parameters"]:
                                if parameter_name in gold_answer[gold_idx]["parameters"] and str(predict_api["parameters"][parameter_name])==str(gold_answer[gold_idx]["parameters"][parameter_name]):
                                    correct_param_num += 1

    if correct_format_num > 0:
        result_dict["AMOUNT"] = 1.0*correct_format_num/len(raw_dataset)

    if correct_api_num * predict_api_num * gold_api_num > 0:
        result_dict["P_api"] = 1.0*correct_api_num/predict_api_num
        result_dict["R_api"] = 1.0*correct_api_num/gold_api_num
        result_dict["F1_api"] = 2*result_dict["P_api"]*result_dict["R_api"]/(result_dict["P_api"]+result_dict["R_api"])
    
    if correct_param_num * predict_param_num * gold_param_num > 0:
        result_dict["P_param"] = 1.0*correct_param_num/predict_param_num
        result_dict["R_param"] = 1.0*correct_param_num/gold_param_num
        result_dict["F1_param"] = 2*result_dict["P_param"]*result_dict["R_param"]/(result_dict["P_param"]+result_dict["R_param"])

    return result_dict

if __name__=="__main__":
    path_prefix = "/public/home/jhfang/mswu_wlchen/HWproject/LLM_HW_2/output/"
    folder_name_list = ["retrieved_epoch3"]
    path_suffix_list = ["/pred_ToolLearning_dev.jsonl",
                        "/pred_ToolLearning_test_in_domain.jsonl",
                        "/pred_ToolLearning_test_out_domain.jsonl"]

    for folder_name in folder_name_list:
        for path_suffix in path_suffix_list:
            path = path_prefix + folder_name + path_suffix
            if os.path.exists(path):
                raw_dataset = read_jsonl(path)
                easy_split = []
                difficult_split = []
                for raw_data in raw_dataset:
                    if "easy" in raw_data["id"]:
                        easy_split.append(raw_data)
                    else:
                        assert "difficult" in raw_data["id"]
                        difficult_split.append(raw_data)
                
                easy_result = calculate_score_ToolLearning(easy_split)
                difficult_result = calculate_score_ToolLearning(difficult_split)
                result = {}
                result["easy"] = easy_result
                result["difficult"] = difficult_result
                save_path = path_prefix + folder_name + "/result_split" + path_suffix.split("pred")[-1][:-1]
                write_json(save_path, result, indent=4)


    # folder_name_list = ["187-ToolLearning",
    #                     "375-ToolLearning",
    #                     "561-ToolLearning",
    #                     "561-ICL",
    #                     "561-TOD",
    #                     "Chat-ICL",
    #                     "Chat-ToolLearning"]

    # for folder_name in folder_name_list:
    #     path_prefix = "/public/home/jhfang/mswu_wlchen/HWproject/LLM_HW_2/output/"

    #     path_suffix_list = ["/pred_ToolLearning_dev.jsonl",
    #                         "/pred_ToolLearning_test_in_domain.jsonl",
    #                         "/pred_ToolLearning_test_out_domain.jsonl",
    #                         "/pred_ToolLearningICL_dev.jsonl",
    #                         "/pred_ToolLearningICL_test_in_domain.jsonl",
    #                         "/pred_ToolLearningICL_test_out_domain.jsonl"]
        
    #     for path_suffix in path_suffix_list:
    #         path = path_prefix + folder_name + path_suffix
    #         if os.path.exists(path):
    #             raw_dataset = read_jsonl(path)
    #             result = calculate_score_ToolLearning(raw_dataset)
    #             result_path = path_prefix + folder_name + "/result2_" + path_suffix.split('ToolLearning')[-1]
    #             write_json(result_path, result, indent=4)