from llm_tools.utils import read_jsonl
import json

def calculate_score(dataset_name, data_path):
    raw_dataset = read_jsonl(data_path)
    result_dict = {}
    for idx_prompt in range(len(raw_dataset[0]['predict'])):
        dataset = []
        for raw_data in raw_dataset:
            import copy
            data = copy.deepcopy(raw_data)
            data['predict'] = raw_data['predict'][idx_prompt]
            dataset.append(data)

        match dataset_name:
            case "TableEE":
                gold_data_list = []
                pred_dict = {}
                for data in dataset:
                    gold_data_list.append(data['gold_data'])
                    if data['predict'] != -1:
                        pred_dict[data['id']] = data['predict']

                fault_list = list()

                COUNT_exact = 0
                COUNT_P = 0
                COUNT_R = 0

                COUNT_type = 0
                COUNT_P_type = 0
                COUNT_R_type = 0

                COUNT_exact_O = 0
                COUNT_P_O = 0
                COUNT_R_O = 0
                COUNT_exact_M = 0
                COUNT_P_M = 0
                COUNT_R_M = 0

                correct_classified_argument = [0,0,0] # * 0-表格，1-混合，2-文本 
                all_classified_argument = [0,0,0]

                OM_flag = 0

                for gold_data in gold_data_list:
                    doc_id = gold_data['doc_id']
                    event_type = gold_data["events"][0]["event_type"]
                    if len(gold_data["events"]) > 1:
                        OM_flag = 1
                    else:
                        OM_flag = 0

                    # * 统计事件要素来源：表格/文本 
                    argument_classified_dict = dict()
                    for argument in gold_data['entity_span']:
                        count = [0,0]
                        for position in gold_data['entity_span'][argument]:
                            if type(gold_data['content_list'][position[0]]) == list:
                                count[0] += 1
                            else:
                                assert type(gold_data['content_list'][position[0]]) == str
                                count[1] += 1
                        if count[0] > 0:
                            if count[1] > 0:
                                argument_classified_dict[argument] = 1
                            else:
                                argument_classified_dict[argument] = 0
                        else:
                            argument_classified_dict[argument] = 2
                    for event in gold_data['events']:
                        for key in event:
                            if key != 'event_id' and key != 'event_type':
                                all_classified_argument[argument_classified_dict[event[key]]] += 1

                    COUNT_R += sum([len(event)-2 for event in gold_data['events']]) # * -2是去掉event_id 和 event_type 
                    COUNT_R_type += 1
                    if OM_flag == 0:
                        COUNT_R_O += sum([len(event)-2 for event in gold_data['events']])
                    else:
                        COUNT_R_M += sum([len(event)-2 for event in gold_data['events']])
                    if doc_id in pred_dict:
                        COUNT_P += sum([len(event)-1 for event in pred_dict[doc_id] if event != None]) # * -1是去掉event_type
                        # COUNT_P_type += len(pred_dict[doc_id])
                        if OM_flag == 0:
                            COUNT_P_O += sum([len(event)-1 for event in pred_dict[doc_id] if event != None])
                        else:
                            COUNT_P_M += sum([len(event)-1 for event in pred_dict[doc_id] if event != None])

                        # * type
                        type_set = list()
                        for pred_event in pred_dict[doc_id]:
                            if pred_event != None:
                                if pred_event['event_type'] not in type_set:
                                    type_set.append(pred_event['event_type'])
                        COUNT_P_type += len(type_set)
                        if event_type in type_set:
                            COUNT_type += 1

                        if doc_id not in fault_list:
                            print("doc_id:",doc_id)
                            print("gold_event",gold_data['events'])
                            print("pred_event",pred_dict[doc_id])
                            import copy
                            gold_event_list = copy.deepcopy(gold_data['events'])
                            for pred_event in pred_dict[doc_id]:
                                if pred_event != None:
                                    if len(gold_event_list) > 0:
                                        match_score = [0]*len(gold_event_list)
                                        for i in range(len(gold_event_list)):
                                            for key in gold_event_list[i]:
                                                if key != 'event_id' and key != 'event_type':
                                                    if key in pred_event:
                                                        if pred_event[key] == gold_event_list[i][key]:
                                                            match_score[i] += 1
                                        match_index = match_score.index(max(match_score))
                                        for key in gold_event_list[match_index]:
                                            if key != 'event_id' and key != 'event_type':
                                                if key in pred_event:
                                                    if pred_event[key] == gold_event_list[match_index][key]:
                                                        correct_classified_argument[argument_classified_dict[pred_event[key]]]+=1                              
                                        COUNT_exact += match_score[match_index]
                                        if OM_flag == 0:
                                            COUNT_exact_O += match_score[match_index]
                                        else:
                                            COUNT_exact_M += match_score[match_index]
                                        gold_event_list.pop(match_index)
                                    else:
                                        break
                result = {}
                if COUNT_P * COUNT_R * COUNT_exact > 0:
                    P = 1.0*COUNT_exact/COUNT_P
                    R = 1.0*COUNT_exact/COUNT_R
                    F1 = 2*P*R/(P+R)
                    print('TEST SCORE (共{}条测试集数据)'.format(len(pred_dict)))
                    print('    - P:'+str(P))
                    print('    - R:'+str(R))
                    print('    - F1:'+str(F1))
                    print(str(correct_classified_argument))
                    print(str(all_classified_argument))
                    print(str([1.0*correct_classified_argument[i]/all_classified_argument[i] for i in range(3)]))
                    result['amount'] = [len(dataset), len(pred_dict)]
                    result['P'] = P
                    result['R'] = R
                    result['F1'] = F1
                    print("======其他结果======")
                    try:
                        print("======类型======")
                        P_type = 1.0*COUNT_type/COUNT_P_type
                        R_type = 1.0*COUNT_type/COUNT_R_type
                        F1_type = 2*P_type*R_type/(P_type+R_type)
                        print('    - P:'+str(P_type))
                        print('    - R:'+str(R_type))
                        print('    - F1:'+str(F1_type))
                        result['P_type'] = P_type
                        result['R_type'] = R_type
                        result['F1_type'] = F1_type
                    except:
                        pass
                    try:
                        print("======事件O2O======")
                        P_o = 1.0*COUNT_exact_O/COUNT_P_O
                        R_o = 1.0*COUNT_exact_O/COUNT_R_O
                        F1_o = 2*P_o*R_o/(P_o+R_o)
                        print('    - P:'+str(P_o))
                        print('    - R:'+str(R_o))
                        print('    - F1:'+str(F1_o))
                        result['P_o'] = P_o
                        result['R_o'] = R_o
                        result['F1_o'] = F1_o
                    except:
                        pass
                    try:
                        print("======事件O2M======")
                        P_m = 1.0*COUNT_exact_M/COUNT_P_M
                        R_m = 1.0*COUNT_exact_M/COUNT_R_M
                        F1_m = 2*P_m*R_m/(P_m+R_m)
                        print('    - P:'+str(P_m))
                        print('    - R:'+str(R_m))
                        print('    - F1:'+str(F1_m))
                        result['P_m'] = P_m
                        result['R_m'] = R_m
                        result['F1_m'] = F1_m
                    except:
                        pass


            case '14lap' | '14res' | '15res' | '16res':   #absa
                corrrect_num=0
                ans_sum=0
                predict_sum=0
                all_datas_sum=0
                wrong_sum=0

                for row in dataset:
                    all_datas_sum += 1
                    if row['predict'] == -1:
                        wrong_sum += 1
                        row['predict'] = []
                    predicts = row['predict']
                    ans = row['gold_data']['ans']
                    ans_sum += len(ans)
                    predict_sum += len(predicts)
                    ans_temp=ans[:]
                    for triple in predicts:
                        triple_temp={}
                        triple_temp["relation"]=triple["Sentiment"]
                        triple_temp["head"]=triple["Aspect_Term"]
                        triple_temp["tail"]=triple["Opinion_Term"]

                        if triple_temp in ans_temp:
                            ans_temp.pop(ans_temp.index(triple_temp))
                            corrrect_num += 1
                result = {}
                if corrrect_num * predict_sum * ans_sum > 0:
                    p=corrrect_num/predict_sum
                    r=corrrect_num/ans_sum
                    f1=2*p*r/(p+r)
                    print('------p值为: '+str(p)+"    -----------------")
                    print('------r值为: '+str(r)+"    -----------------")
                    print('------f1值为: '+str(f1)+"    -----------------")
                    print('------共计   '+str(all_datas_sum)+'    条数据，其中正确数据共   '+str(all_datas_sum-wrong_sum)+'   条--------')

                    result['amount'] = [all_datas_sum, all_datas_sum - wrong_sum]
                    result['P'] = p
                    result['R'] = r
                    result['F1'] = f1


            case 'ag_news' | 'MedQA' | 'MRPC' | 'SNLI':  #CLS
                ans_sum=0
                correct_num=0
                all_datas_sum=0
                wrong_sum=0

                for row in dataset:
                    all_datas_sum += 1

                    if row['predict'] == -1:
                        wrong_sum += 1

                    predict = row['predict']
                    ans = row['gold_data']['ans']
                    ans_sum += 1
                    if ans == predict:
                        correct_num += 1

                result = {}
                if ans_sum > 0:
                    acc=correct_num/ans_sum
                    print('------------- acc : '+str(acc)+'--------------')
                    print('------共计   '+str(all_datas_sum)+'    条数据，其中正确数据共   '+str(all_datas_sum-wrong_sum)+'   条--------')

                    
                    result['amount'] = [all_datas_sum, all_datas_sum - wrong_sum]
                    result['ACC'] = acc


            case 'MIT_MOVIE_Review' | 'MIT_Restaurant_Review' | 'NCBIdisease' | 'ontoNotes5':  #NER
                correct_sum=0
                predict_sum=0
                ans_sum=0
                all_datas_sum=0
                wrong_sum=0

                for row in dataset:
                    all_datas_sum += 1

                    if row['predict'] == -1:
                        wrong_sum += 1
                        row['predict'] = []
                    predict = row['predict']
                    ans = row['gold_data']['ans']
                    ans_temp=ans[:]
                    for ner in predict:
                        if ner in ans_temp:
                            ans_temp.pop(ans_temp.index(ner))
                            correct_sum += 1
                    predict_sum += len(predict)
                    ans_sum += len(ans)

                result = {}
                result['amount'] = [all_datas_sum, all_datas_sum - wrong_sum]
                if predict_sum * ans_sum * correct_sum > 0:
                    p=correct_sum/predict_sum
                    r=correct_sum/ans_sum
                    f1=2*p*r/(p+r)
                    print('-----------Entity F1 : '+str(f1)+'--------------- ')
                    print('------共计   '+str(all_datas_sum)+'    条数据，其中正确数据共   '+str(all_datas_sum-wrong_sum)+'   条--------')
                    
                    result['P'] = p
                    result['R'] = r
                    result['F1'] = f1


            case 'scierc' | 'semeval' | 'WebNLG':  #RE
                correct_num=0
                ans_relations_sum=0
                predict_relations_sum=0
                all_datas_sum=0
                wrong_sum=0

                for row in dataset:
                    all_datas_sum += 1

                    if row['predict'] == -1:
                        wrong_sum += 1
                        row['predict'] = []
                    ans_relations = row['gold_data']['ans']
                    ans_relations_temp=ans_relations[:]
                    predict_relations = row['predict']
                    ans_relations_sum += len(ans_relations)
                    predict_relations_sum += len(predict_relations)

                    for rel in predict_relations:
                        if rel in ans_relations_temp:
                            ans_relations_temp.pop(ans_relations_temp.index(rel))
                            correct_num += 1
                
                result = {}
                result['amount'] = [all_datas_sum, all_datas_sum - wrong_sum]
                if predict_relations_sum * ans_relations_sum * correct_num > 0:
                    p=correct_num/predict_relations_sum
                    r=correct_num/ans_relations_sum
                    f1=2*p*r/(p+r)
                    print('-----------Relation Strict F1 : '+str(f1)+'--------------- ')
                    print('------共计   '+str(all_datas_sum)+'    条数据，其中正确数据共   '+str(all_datas_sum-wrong_sum)+'   条--------')
                    result['P'] = p
                    result['R'] = r
                    result['F1'] = f1


            case 'ace05-evt' | 'casie' | 'PHEE':  #EE
                def match_max_args(arg_list1, arg_list2):  # arg_list1中的每个元素代表predict中的一个论元
                    match_sum = 0
                    for arg_temp in arg_list1:
                        if arg_temp in arg_list2:
                            match_sum += 1
                    return match_sum

                ans_triggers_sum = 0
                predict_triggers_sum = 0
                correct_triggers_sum = 0
                ans_args_sum = 0
                predict_args_sum = 0
                correct_args_sum = 0

                all_datas_sum = 0
                wrong_sum = 0

                for row in dataset:
                    all_datas_sum += 1
                    predict_events = row['predict']
                    ans_events = row['gold_data']['ans']
                    if predict_events == -1:
                        wrong_sum += 1
                        predict_events = []
                    ans_triggers_sum += len(ans_events)
                    predict_triggers_sum += len(predict_events)

                    for event in predict_events:
                        for ans_event in ans_events:
                            if event["event_type"] == ans_event["event_type"] and event['trigger'] == ans_event['trigger']:
                                correct_triggers_sum += 1

                    ## 上面处理的准则是以trigger为单位
                    ## 下面算论元的情况
                    ans_events_temp = ans_events[:]
                    for event in predict_events:
                        temp_args_dict = {}

                        for i in range(len(ans_events_temp)):
                            ans_event = ans_events_temp[i]
                            if event["event_type"] == ans_event["event_type"] and event['trigger'] == ans_event['trigger']:
                                my_key = event["event_type"] + '|' + event['trigger']
                                if temp_args_dict.get(my_key, None) == None:
                                    temp_args_dict[my_key] = [0, 0, -1]
                                match_num = match_max_args(event['args'], ans_event['args'])
                                if match_num > temp_args_dict[my_key][0]:
                                    temp_args_dict[my_key][0] = match_num
                                    temp_args_dict[my_key][1] = len(event['args'])
                                    temp_args_dict[my_key][2] = i
                        for _, my_eval in temp_args_dict.items():
                            correct_args_sum += my_eval[0]
                            predict_args_sum += my_eval[1]
                            if my_eval[2] != -1:
                                ans_events_temp.pop(my_eval[2])

                        if len(temp_args_dict) == 0:
                            predict_args_sum += len(event['args'])
                    for event in ans_events:
                        ans_args_sum += len(event['args'])

                result = {}
                if predict_triggers_sum * ans_triggers_sum * correct_triggers_sum > 0:
                    trigger_p = correct_triggers_sum / predict_triggers_sum
                    trigger_r = correct_triggers_sum / ans_triggers_sum
                    trigger_f1 = 2 * trigger_r * trigger_p / (trigger_r + trigger_p)
                    print('-----------Event Trigger F1 : ' + str(trigger_f1) + '--------------- ')
                    result['P_trigger'] = trigger_p
                    result['R_trigger'] = trigger_r
                    result['F1_trigger'] = trigger_f1

                if predict_args_sum * ans_args_sum * correct_args_sum > 0:
                    arg_p = correct_args_sum / predict_args_sum
                    arg_r = correct_args_sum / ans_args_sum
                    arg_f1 = 2 * arg_r * arg_p / (arg_r + arg_p)
                    print('-----------Event Argument F1 : ' + str(trigger_f1) + '--------------- ')
                    result['P'] = arg_p
                    result['R'] = arg_r
                    result['F1'] = arg_f1

                print('------共计   ' + str(all_datas_sum) + '    条数据，其中正确数据共   ' + str(
                    all_datas_sum - wrong_sum) + '   条--------')
                result['amount'] = [all_datas_sum, all_datas_sum - wrong_sum]

            case 'api_we_instructed':
                api_correct_sum=0
                api_all_sum=0

                slot_correct_sum=0
                slot_rawdata_all_sum=0
                slot_predict_all_sum=0

                value_correct_sum=0
                value_rawdata_all_sum=0
                value_predict_all_sum=0


                for data in dataset:
                    gold=data["gold_data"]["gold_answer"][0]
                    id=data["id"]
                    predict=data["predict"]

                    api_all_sum+=1

                    slot_rawdata_all_sum+=len(gold["slot"])
                    value_rawdata_all_sum=slot_rawdata_all_sum

                    if predict != -1:
                        if predict.get("api"):
                            if predict["api"]==gold["api"]:
                                api_correct_sum+=1
                        
                        if predict.get("slots"):
                            slot_predict_all_sum+=len(predict["slots"])
                            value_predict_all_sum=slot_predict_all_sum

                            for slot in predict["slots"]:
                                try:
                                    if slot in gold["slot"].keys():
                                        slot_correct_sum+=1
                                        predict_value=predict["slots"][slot]
                                        gold_value=gold["slot"][slot]
                                        if isinstance(gold_value,list):
                                            for result_value in gold_value:
                                                if result_value.lower()==predict_value.lower():
                                                    value_correct_sum+=1
                                                    break
                                        if isinstance(gold_value,str):
                                            if gold_value.lower()==predict_value.lower():
                                                value_correct_sum+=1
                                except:
                                    pass
                
                result={}
                if api_all_sum > 0:
                    ACC_api=1.0*api_correct_sum/api_all_sum
                    result["ACC_api"]=ACC_api
                    print('    - ACC_api:'+str(ACC_api))

                if slot_correct_sum * slot_predict_all_sum * slot_rawdata_all_sum > 0:
                    P_slot=1.0*slot_correct_sum/slot_predict_all_sum
                    R_slot=1.0*slot_correct_sum/slot_rawdata_all_sum
                    F1_slot=2*P_slot*R_slot/(P_slot+R_slot)
                    result["P_slot"]=P_slot
                    result["R_slot"]=R_slot
                    result["F1_slot"]=F1_slot
                    print('    - P_slot:'+str(P_slot))
                    print('    - R_slot:'+str(R_slot))
                    print('    - F1_slot:'+str(F1_slot))

                if value_correct_sum * value_predict_all_sum * value_rawdata_all_sum > 0:
                    P_value=1.0*value_correct_sum/value_predict_all_sum
                    R_value=1.0*value_correct_sum/value_rawdata_all_sum
                    F1_value=2*P_value*R_value/(F1_slot+R_value)
                    print('    - P_value:'+str(P_value))
                    print('    - R_value:'+str(R_value))
                    print('    - F1_value:'+str(F1_value))    
                    result["P_value"]=P_value
                    result["R_value"]=R_value
                    result["F1_value"]= F1_value

            case _:
                print("ERROR!")

        result_dict[idx_prompt] = result
    return result_dict

def calculate_score_ToolLearning(data_path):
    raw_dataset = read_jsonl(data_path)
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