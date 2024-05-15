import re
import json

def transform_output_format(dataset_name, output_text):

    match dataset_name:
        case "TableEE":
            try:
                api_text=re.search("\[[^\[\]]*\]",output_text)
                if api_text == None:
                    api_text=re.findall("{[^{}]*}",output_text)
                    structured_output = []
                    for i in range(len(api_text)):
                        try:
                            structured_output.append(json.loads(api_text[i]))
                        except:
                            pass
                else:
                    structured_output = json.loads(api_text.group())
                if type(structured_output)!=list:
                    structured_output = [structured_output]
                pred_text = []
                for i in range(len(structured_output)):
                    if type(structured_output[i])==dict:
                        if '事件类型' in structured_output[i]:
                            structured_output[i]['event_type'] = structured_output[i]['事件类型']
                            del structured_output[i]['事件类型']
                        else:
                            structured_output[i]['event_type'] = None
                        pred_text.append(structured_output[i])
            except:
                pred_text = -1
            return pred_text

        case '14lap' | '14res' | '15res' | '16res':   #absa
            LLM_ans = output_text
            LLM_ans = re.sub("'", '"', LLM_ans)
            LLM_ans_splits = re.split('\n\n', LLM_ans)
            # pattern=re.compile(r'\{(?:"ent":\s?\[(\".*\".*)*(\".*\")].*)(?:\"rel\":\s?\[(\{(?:\"relation\":\s?\".*\".*)'
            #                    r'(?:\"head\":\s?\".*\".*)(?:\"tail\":\s?\".*\")\}.*)*\{(?:\"relation\":\s?\".*\".*)'
            #                    r'(?:\"head\":\s?\".*\".*)(?:\"tail\":\s?\".*\".*)\}\].*)\}')
            try:
                # pattern = re.compile(r'\[(\{((\"relation\":(.|\s)*\"(.|\s)*\"(.|\s)*)|(\"head\":(.|\s)*\"(.|\s)*\"(.|\s)*)|(\"tail\":(.|\s)*\"(.|\s)*\"(.|\s)*)){3}\})*\]')
                pattern = re.compile(r'\[[^\[\]]*\]')
                predict_ans_all = []
                for LLM_ans_temp in LLM_ans_splits:
                    LLM_ans_temp = re.sub("\n", "", LLM_ans_temp)
                    predict_ans_all_temp = pattern.findall(LLM_ans_temp)
                    predict_ans_all.extend(predict_ans_all_temp)

                for i in range(len(predict_ans_all)):
                    if predict_ans_all[i] != '[]':
                        predict_ans_all[i], predict_ans_all[0] = predict_ans_all[0], predict_ans_all[i]
                        break
                if len(predict_ans_all)==0:
                    return -1
                for predict_ans in predict_ans_all:

                    try:
                        judge=0
                        lsts = json.loads(predict_ans)
                        for lst in lsts:
                            if lst.get('Sentiment', -1) == -1 or lst.get('Aspect_Term', -1) == -1 or lst.get('Opinion_Term', -1) == -1:
                                judge=1
                        if judge:
                            continue
                        else:
                            return lsts
                    except:
                        continue
                return -1

            except:
                return -1

        case 'ag_news' | 'MedQA' | 'MRPC' | 'SNLI':  #CLS
            LLM_ans = output_text
            LLM_ans = re.sub("'", '"', LLM_ans)
            LLM_ans_splits = re.split('\n\n', LLM_ans)
            try:
                # pattern = re.compile(r'(\{\".*\"\})|(\[.*\])')
                pattern1 = re.compile(r'\{[^\{\}]*\}')
                predict_ans1_all = []
                for LLM_ans1_temp in LLM_ans_splits:
                    LLM_ans1_temp = re.sub("\n", "", LLM_ans1_temp)
                    predict_ans1_all_temp = pattern1.findall(LLM_ans1_temp)
                    predict_ans1_all.extend(predict_ans1_all_temp)

                pattern2 = re.compile(r'\[[^\[\]]*\]')
                predict_ans2_all = []
                for LLM_ans2_temp in LLM_ans_splits:
                    LLM_ans2_temp = re.sub("\n", "", LLM_ans2_temp)
                    predict_ans2_all_temp = pattern2.findall(LLM_ans2_temp)
                    predict_ans2_all.extend(predict_ans2_all_temp)

                if len(predict_ans1_all):
                    for predict_ans1 in predict_ans1_all:

                        s_p_ans = predict_ans1
                        s_p_ans = s_p_ans[1:-1]

                        try:
                            return json.loads(s_p_ans)
                        except:
                            continue

                    return -1
                elif len(predict_ans2_all):
                    for predict_ans2 in predict_ans2_all:

                        s_p_ans = predict_ans2
                        s_p_ans = '\"' + s_p_ans + '\"'

                        try:
                            return json.loads(s_p_ans)
                        except:
                            continue

                    return -1
                else:
                    return -1
            except:
                return -1

        case 'MIT_MOVIE_Review' | 'MIT_Restaurant_Review' | 'NCBIdisease' | 'ontoNotes5':  #NER
            LLM_ans = output_text
            LLM_ans = re.sub("'", '"', LLM_ans)
            LLM_ans_splits = re.split('\n\n', LLM_ans)
            try:
                #pattern = re.compile(r'\[(\{((\"text\":(.|\s)*\"(.|\s)*\"(.|\s)*)|(\"type\":(.|\s)*\"(.|\s)*\"(.|\s)*)){2}\})*\]')
                pattern=re.compile(r'\[[^\[\]]*\]')
                predict_ans_all = []
                for LLM_ans_temp in LLM_ans_splits:
                    LLM_ans_temp = re.sub("\n", "", LLM_ans_temp)
                    predict_ans_all_temp = pattern.findall(LLM_ans_temp)
                    predict_ans_all.extend(predict_ans_all_temp)

                for i in range(len(predict_ans_all)):
                    if predict_ans_all[i] != '[]':
                        predict_ans_all[i], predict_ans_all[0] = predict_ans_all[0], predict_ans_all[i]
                        break
                for predict_ans in predict_ans_all:

                    try:
                        lsts = json.loads(predict_ans)
                        judge=0
                        for dict_temp in lsts:
                            if dict_temp.get('text', -1) == -1 or dict_temp.get('type', -1) == -1:
                                judge=1
                        if judge:
                            continue
                        else:
                            return lsts
                    except:
                        continue
                return -1

            except:
                return -1

        case 'scierc' | 'semeval' | 'WebNLG':  #RE
            LLM_ans = output_text
            LLM_ans = re.sub("'", '"', LLM_ans)
            LLM_ans_splits = re.split('\n\n', LLM_ans)
            try:
                #pattern = re.compile(r'\[(\{((\"relation\":(.|\s)*\"(.|\s)*\"(.|\s)*)|(\"head\":(.|\s)*\"(.|\s)*\"(.|\s)*)|(\"tail\":(.|\s)*\"(.|\s)*\"(.|\s)*)){3}\})*\]')
                pattern=re.compile(r'\[[^\[\]]*\]')
                predict_ans_all = []
                for LLM_ans_temp in LLM_ans_splits:
                    LLM_ans_temp = re.sub("\n", "", LLM_ans_temp)
                    predict_ans_all_temp = pattern.findall(LLM_ans_temp)
                    predict_ans_all.extend(predict_ans_all_temp)
                for i in range(len(predict_ans_all)):
                    if predict_ans_all[i] != '[]':
                        predict_ans_all[i], predict_ans_all[0] = predict_ans_all[0], predict_ans_all[i]
                        break
                for predict_ans in predict_ans_all:
                    try:
                        lsts = json.loads(predict_ans)
                        judge=0
                        for lst in lsts:
                            if lst.get('relation', -1) == -1 or lst.get('head', -1) == -1 or lst.get('tail', -1) == -1:
                                judge=1
                        if judge:
                            continue
                        else:
                            return lsts
                    except:
                        continue
                return -1

            except:
                return -1

        case 'ace05-evt' | 'casie' | 'PHEE':  #EE
            LLM_ans = output_text
            LLM_ans = re.sub("'", '"', LLM_ans)
            LLM_ans_splits = re.split('\n\n', LLM_ans)
            try:
                # pattern = re.compile(r'\[(\{((\"event_type\":.*\".*\".*)|(\"trigger\":.*\".*\".*)|('
                #                      r'\"args\":.*\[(\{((\"role\":.*\".*\".*)|(\"text\":.*\".*\".*)){2}\})*\].*)){3}\})*\]')

                pattern = re.compile(r'\[\{.*\}\]')
                predict_ans_all = []
                for LLM_ans_temp in LLM_ans_splits:
                    LLM_ans_temp = re.sub("\n", "", LLM_ans_temp)
                    predict_ans_all_temp = pattern.findall(LLM_ans_temp)
                    predict_ans_all.extend(predict_ans_all_temp)

                for i in range(len(predict_ans_all)):
                    if predict_ans_all[i] != '[]':
                        predict_ans_all[i], predict_ans_all[0] = predict_ans_all[0], predict_ans_all[i]

                if len(predict_ans_all) == 0:
                    pattern = re.compile(r'\[[^\[\]]*\]')
                    predict_ans_all = pattern.findall(LLM_ans)

                for predict_ans in predict_ans_all:

                    try:
                        dict_temps = json.loads(predict_ans)

                        judge = 0
                        for dict_temp in dict_temps:

                            if dict_temp.get('event_type', -1) != -1 and dict_temp.get('trigger',-1) != -1 and dict_temp.get('args',-1) != -1:
                                args = dict_temp['args']

                                for arg in args:
                                    if arg.get('role', -1) == -1 or arg.get('text', -1) == -1:
                                        judge = 1

                            else:
                                judge = 1
                        if judge:
                            continue
                        else:
                            return dict_temps
                    except:

                        continue
                return -1

            except:
                return -1

        case 'api_we_instructed':
            #example:"answer": {"api": "FindMovies", "slots": {"genre": "Family", "show_type": "3D", "location": "San Jose"}}
            try:
                pattern = re.compile("{.*}", re.DOTALL)
                api_text = re.search(pattern, output_text)
                if api_text:
                    api_output = json.loads(api_text.group(0))
                    return api_output
                else:
                    return -1
            except:
                return -1     

        case 'ToolLearning':
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
                
            text = re.sub("'", '"', output_text)
            text = re.sub("\n", "", text)
            pattern = re.compile("\[\s*\{\s*\"api\"", re.DOTALL)

            search_result = re.search(pattern, text)

            if search_result != None:
                pos_s = search_result.span()[0]
                pos_e = match_square_bracket(text, pos_s)

                text = text[pos_s:pos_e+1]
                if "api" in text and "parameters" in text and "responses" in text:
                    try:
                        output = json.loads(text)
                        return output
                    except:
                        return -1
                else:
                    return -1
            else:
                return -1  

        case _:
            print("ERROR!")
