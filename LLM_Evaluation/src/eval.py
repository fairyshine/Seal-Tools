import re
import json

from llm_tools.utils import read_jsonl, read_json, write_jsonl, write_json
from llm_tools.evaluation.calculate import calculate_score_ToolLearning

if __name__=="__main__":
    # # path_prefix = "/public/home/jhfang/mswu_wlchen/ToolLearningResult/retrieved_test/"
    # path_prefix = "/public/home/jhfang/mswu_wlchen/ToolLearningResult/gold_test/"

    # folder_name_list = [
    #                 # "llama_base_DPR_Top5_full",
    #                 # "llama_DPR_Top5_full",
    #                 # "toolllama_DPR_Top5_full",
    #                 # "vicuna_DPR_Top5_full",
    #                 # "mistral_DPR_Top5_full",
    #                 # "finetuned_gold_BM25_Top5_full",
    #                 # "finetuned_gold_DPR_Top5_full",
    #                 # "finetuned_retrieved_BM25_Top5_full",
    #                 # "finetuned_retrieved_DPR_Top5_full",
    #                 # "ChatGPT_DPR_Top5_full",
    #                 # "GPT4_DPR_Top5_full",
    #                 "561-ICL",
    #                 "Chat-ICL",
    #                 "retrieved-ICL",
    #                 "ChatGPT-ICL",
    #                 ]
    # # path_suffix_list = [
    # #                     # "_dev.jsonl",
    # #                     "_test_in_domain.jsonl",
    # #                     "_test_out_domain.jsonl",
    # #                     ]


    # for folder_name in folder_name_list:
    #     print(folder_name)

    #     # # 合并两个test数据集 in/out domain
    #     # pred_in_domain_datapath = path_prefix + folder_name + "/new_pred_test_in_domain.jsonl"
    #     # pred_out_domain_datapath = path_prefix + folder_name + "/new_pred_test_out_domain.jsonl"
    #     # pred_test_path = path_prefix + folder_name + "/new_pred_test.jsonl"
    #     # dataset = []
    #     # dataset.extend(read_jsonl(pred_in_domain_datapath))
    #     # dataset.extend(read_jsonl(pred_out_domain_datapath))
    #     # write_jsonl(pred_test_path, dataset)
    #     # # 测试
    #     # result = calculate_score_ToolLearning(pred_test_path)
    #     # write_json(path_prefix + folder_name + "/new_result_test.json", result, indent=4)

    #     # 测试简单/困难集
    #     pred_test_path = path_prefix + folder_name + "/new_pred_test.jsonl"
    #     pred_test_easy_path = path_prefix + folder_name + "/new_pred_test_easy.jsonl"
    #     pred_test_difficult_path = path_prefix + folder_name + "/new_pred_test_difficult.jsonl"
    #     all_dataset = read_jsonl(pred_test_path)
    #     easy_dataset = []
    #     difficult_dataset = []
    #     for data in all_dataset:
    #         if "easy" in data["id"]:
    #             easy_dataset.append(data)
    #         else:
    #             difficult_dataset.append(data)
    #     write_jsonl(pred_test_easy_path, easy_dataset)
    #     write_jsonl(pred_test_difficult_path, difficult_dataset)
    #     # 测试
    #     easy_result = calculate_score_ToolLearning(pred_test_easy_path)
    #     write_json(path_prefix + folder_name + "/new_result_test_easy.json", easy_result, indent=4)
    #     difficult_result = calculate_score_ToolLearning(pred_test_difficult_path)
    #     write_json(path_prefix + folder_name + "/new_result_test_difficult.json", difficult_result, indent=4)  

# * ===================================================

    # pred_dataset_path = "/public/home/jhfang/mswu_wlchen/HWproject/LLM_HW_2/output/finetuned_retrieved_nested/pred_nested_untrain.jsonl"
    # output_path = "/public/home/jhfang/mswu_wlchen/HWproject/LLM_HW_2/output/finetuned_retrieved_nested/result_nested_untrain.json"
    # write_json(output_path, calculate_score_ToolLearning(pred_dataset_path), indent=4)

# * ===================================================

    pred_dataset_path = "./output/finetuned_retrieved_DPR_Top5_full/new_pred_test.jsonl"
    dataset = read_jsonl(pred_dataset_path)

    def match_square_bracket(text, pos_s):
        counter = -1
        for i in range(pos_s+1,len(text)):
            if text[i] == '[':
                counter -= 1
            elif text[i] == ']':
                counter += 1
            if counter == 0:
                return i
        return -1

    # For tools
    error_retriever = 0
    error_not_need = 0
    error_hallucination = 0

    # For parameters
    error_omission = 0
    error_surplus = 0
    error_extraction_wrong = 0
    error_transformation_wrong = 0

    for data in dataset:
        predict_calling = data["predict"][0]
        if predict_calling != -1:
            # get predict_calling、retriever_tool、gold_calling
            retriever_tool_text = data["gold_data"]["conversations"][0]["value"]
            gold_calling_text = data["gold_data"]["conversations"][1]["value"]
            retriever_tool_part = retriever_tool_text.split("api_list =")[1]
            pattern = re.compile("\[", re.DOTALL)
            search_result = re.search(pattern, retriever_tool_part)
            pos_s = search_result.span()[0]
            pos_e = match_square_bracket(retriever_tool_part, pos_s)
            retriever_tool_part = retriever_tool_part[pos_s:pos_e+1]
            retriever_tool = json.loads(json.dumps(eval(retriever_tool_part)))
            gold_calling = json.loads(json.dumps(eval(gold_calling_text)))

            predict_tool_name_list = [tool["api"] for tool in predict_calling]
            retrieved_tool_name_list = [ tool["api_name"] for tool in retriever_tool]
            gold_tool_name_list = [tool["api"] for tool in gold_calling]
            for tool in gold_tool_name_list:
                if tool not in retrieved_tool_name_list:
                    error_retriever += 1
            for tool in predict_tool_name_list:
                if tool not in gold_tool_name_list:
                    if tool in retrieved_tool_name_list:
                        error_not_need += 1
                    else:
                        error_hallucination += 1
                else:
                    # tool选择正确，判断param的问题
                    for predict_call in predict_calling:
                        if predict_call["api"] == tool:
                            predict_parameters = predict_call["parameters"]
                            break
                    for gold_call in gold_calling:
                        if gold_call["api"] == tool:
                            gold_parameters = gold_call["parameters"]
                            break
                    for gold_param in gold_parameters:
                        if gold_param not in predict_parameters:
                            error_omission += 1
                    for predict_param in predict_parameters:
                        if predict_param not in gold_parameters:
                            error_surplus += 1
                        else:
                            predict_value = str(predict_parameters[predict_param])
                            gold_value = str(gold_parameters[gold_param])
                            if predict_value != gold_value:
                                if gold_value in retriever_tool_text.split("task_instruction =")[1]:
                                    error_extraction_wrong += 1
                                else:
                                    error_transformation_wrong += 1

    print("==== Tools =====")
    print("error_retriever: ",error_retriever)
    print("error_not_need: ",error_not_need)
    print("error_hallucination: ",error_hallucination)
    print("==== Parameters ====")
    print("error_omission: ",error_omission)
    print("error_surplus: ",error_surplus)
    print("error_extraction_wrong: ",error_extraction_wrong)
    print("error_transformation_wrong: ",error_transformation_wrong)



