import os
import gc

import torch
from rich.progress import track

from .process_input import process_input_text
from .transform_output import transform_output_format
from .calculate import calculate_score,calculate_score_ToolLearning
from llm_tools.llms import Auto_Model
from llm_tools.utils import read_jsonl,write_jsonl,read_json,write_json

class LLM_eval():
    def __init__(self):
        if not os.path.exists('./output/eval/raw/'):
            os.makedirs('./output/eval/raw/')
        if not os.path.exists('./output/eval/pred/'):
            os.makedirs('./output/eval/pred/')
        if not os.path.exists('./output/eval/result/'):
            os.makedirs('./output/eval/result/')
        self.llm = None
        
    def set_llm(self, model):
        self.llm = model
        if not os.path.exists('./output/eval/raw/'+self.llm.model_name+'/'):
            os.makedirs('./output/eval/raw/'+self.llm.model_name+'/')
        if not os.path.exists('./output/eval/pred/'+self.llm.model_name+'/'):
            os.makedirs('./output/eval/pred/'+self.llm.model_name+'/')

    def rm_llm(self):
        del self.llm
        gc.collect()
        torch.cuda.empty_cache()
        self.llm = None

    def get_prompt(self, dataset_name, task):
        match task:
            case 'IE':
                return read_json('./data/IE_prompts.json')[dataset_name]
            case 'API':
                return read_json('./data/API_prompts.json')[dataset_name]
            case _:
                print("ERROR!") 

    def API_eval_one(self, dataset_name):
        dataset = read_jsonl('./data/API_eval/'+dataset_name+'.jsonl')
        prompt_list = self.get_prompt(dataset_name, 'API')
        raw_datapath = './output/eval/raw/' + self.llm.model_name + '/' + dataset_name+'.jsonl'
        pred_datapath = './output/eval/pred/' + self.llm.model_name + '/' + dataset_name+'.jsonl'
        result_path = './output/eval/result/' + self.llm.model_name + '_' + dataset_name+'.json'

        if not os.path.exists(result_path):
            # * 加载中途记录
            if os.path.exists(raw_datapath):
                raw_list = read_jsonl(raw_datapath)
            else:
                raw_list = []
            if os.path.exists(pred_datapath):
                pred_list = read_jsonl(pred_datapath)
            else:
                pred_list = []

            # * 与大模型问答
            for idx in track(range(len(pred_list), len(dataset)),description='Chating with '+self.llm.model_name+' ... '+'( '+dataset_name+' )'):

                input_text_list, doc_id = process_input_text(dataset_name, prompt_list, dataset[idx])

                raw_output = {
                                'id':doc_id,
                                'text':[],
                                'raw':[]
                            }
                pred_output = {
                                'id':doc_id,
                                'predict':[],
                                'gold_data':dataset[idx],
                            }

                for input_text in input_text_list:
                    output_raw, output_text = self.llm.answer(input_text)
                    torch.cuda.empty_cache()

                    pred_text = transform_output_format(dataset_name, output_text)

                    raw_output['text'].append(output_text)
                    raw_output['raw'].append(output_raw)

                    pred_output['predict'].append(pred_text)

                raw_list.append(raw_output)
                pred_list.append(pred_output)
                write_jsonl(raw_datapath, raw_list)
                write_jsonl(pred_datapath, pred_list)

            # * 计算评价指标
            result = calculate_score(dataset_name, pred_datapath)
            # 保存结果  
            write_json(result_path, result, indent=4)
    
    def API_eval(self):
        dataset_list = []
        for dataset_name in read_json('./data/API_prompts.json'):
            dataset_list.append(dataset_name)

        for dataset_name in dataset_list:
            self.API_eval_one(dataset_name)

    def IE_eval_one(self, dataset_name):
        dataset = read_jsonl('./data/IE_eval/'+dataset_name+'.jsonl')
        prompt_list = self.get_prompt(dataset_name, 'IE')
        raw_datapath = './output/eval/raw/' + self.llm.model_name + '/' + dataset_name+'.jsonl'
        pred_datapath = './output/eval/pred/' + self.llm.model_name + '/' + dataset_name+'.jsonl'
        result_path = './output/eval/result/' + self.llm.model_name + '_' + dataset_name+'.json'

        if not os.path.exists(result_path):
            # * 加载中途记录
            if os.path.exists(raw_datapath):
                raw_list = read_jsonl(raw_datapath)
            else:
                raw_list = []
            if os.path.exists(pred_datapath):
                pred_list = read_jsonl(pred_datapath)
            else:
                pred_list = []

            # * 与大模型问答
            for idx in track(range(len(pred_list), len(dataset)),description='Chating with '+self.llm.model_name+' ... '+'( '+dataset_name+' )'):

                input_text_list, doc_id = process_input_text(dataset_name, prompt_list, dataset[idx])

                raw_output = {
                                'id':doc_id,
                                'text':[],
                                'raw':[]
                            }
                pred_output = {
                                'id':doc_id,
                                'predict':[],
                                'gold_data':dataset[idx],
                            }

                for input_text in input_text_list:
                    output_raw, output_text = self.llm.answer(input_text)
                    torch.cuda.empty_cache()

                    pred_text = transform_output_format(dataset_name, output_text)

                    raw_output['text'].append(output_text)
                    raw_output['raw'].append(output_raw)

                    pred_output['predict'].append(pred_text)

                raw_list.append(raw_output)
                pred_list.append(pred_output)
                write_jsonl(raw_datapath, raw_list)
                write_jsonl(pred_datapath, pred_list)
            
            # * 计算评价指标
            result = calculate_score(dataset_name, pred_datapath)
            # 保存结果  
            write_json(result_path, result, indent=4)


    def IE_eval(self):
        dataset_list = []
        for dataset_name in read_json('./data/IE_prompts.json'):
            dataset_list.append(dataset_name)

        for dataset_name in dataset_list:
            self.IE_eval_one(dataset_name)


    def ToolLearning_eval(self):
        dataset_name_list = [
            "dev",
            "test_in_domain",
            "test_out_domain"
        ]
        for dataset_name in dataset_name_list:
            dataset = read_json('./data/ToolLearning_eval/'+dataset_name+'.json')
            raw_datapath = './output/raw_ToolLearning_' + dataset_name+'.jsonl'
            pred_datapath = './output/pred_ToolLearning_' + dataset_name+'.jsonl'
            result_path = './output/result_ToolLearning_' + dataset_name+'.json'

            if not os.path.exists(result_path):
                # * 加载中途记录
                if os.path.exists(raw_datapath):
                    raw_list = read_jsonl(raw_datapath)
                else:
                    raw_list = []
                if os.path.exists(pred_datapath):
                    pred_list = read_jsonl(pred_datapath)
                else:
                    pred_list = []

                # * 与大模型问答
                for idx in track(range(len(pred_list), len(dataset)),description='Chating with '+self.llm.model_name+' ... '+'( ToolLearning '+dataset_name+' )'):

                    input_text, doc_id = dataset[idx]["conversations"][0]["value"],dataset[idx]["id"]

                    raw_output = {
                                    'id':doc_id,
                                    'text':[],
                                    'raw':[]
                                }
                    pred_output = {
                                    'id':doc_id,
                                    'predict':[],
                                    'gold_data':dataset[idx],
                                }

                    output_raw, output_text = self.llm.answer(input_text)
                    torch.cuda.empty_cache()

                    pred_text = transform_output_format("ToolLearning", output_text)

                    raw_output['text'].append(output_text)
                    raw_output['raw'].append(output_raw)

                    pred_output['predict'].append(pred_text)

                    raw_list.append(raw_output)
                    pred_list.append(pred_output)
                    write_jsonl(raw_datapath, raw_list)
                    write_jsonl(pred_datapath, pred_list)

                # * 计算评价指标
                result = calculate_score_ToolLearning(pred_datapath)
                # 保存结果  
                write_json(result_path, result, indent=4)


    def ToolLearning_eval_ICL(self):
        dataset_name_list = [
            # "dev",
            "test_in_domain",
            "test_out_domain"
        ]

        text_A = '''Please chooose the needed apis and return api_calling list according to the task_instruction in given format as the example.'''
        text_B = '''Please chooose the needed apis and return api_calling list according to the task_instruction in given format as the example.
        Return format: [{"api": "", "parameters": {"": ""}, "responses": ["API_call_0","API_call_1"]},{"api": "", "parameters": {"": ""}, "responses": ["API_call_2"]}]
        Responses can be used as parameter value.
        '''

        for dataset_name in dataset_name_list:
            dataset = read_json('./data/ToolLearning_eval/'+dataset_name+'.json')
            raw_datapath = './output/raw_ToolLearningICL_' + dataset_name+'.jsonl'
            pred_datapath = './output/pred_ToolLearningICL_' + dataset_name+'.jsonl'
            result_path = './output/result_ToolLearningICL_' + dataset_name+'.json'

            if not os.path.exists(result_path):
                # * 加载中途记录
                if os.path.exists(raw_datapath):
                    raw_list = read_jsonl(raw_datapath)
                else:
                    raw_list = []
                if os.path.exists(pred_datapath):
                    pred_list = read_jsonl(pred_datapath)
                else:
                    pred_list = []

                # * 与大模型问答
                for idx in track(range(len(pred_list), len(dataset)),description='Chating with '+self.llm.model_name+' ... '+'( ToolLearning ICL '+dataset_name+' )'):


                    input_text, doc_id = dataset[idx]["conversations"][0]["value"].replace(text_A,text_B), dataset[idx]["id"]

                    raw_output = {
                                    'id':doc_id,
                                    'text':[],
                                    'raw':[]
                                }
                    pred_output = {
                                    'id':doc_id,
                                    'predict':[],
                                    'gold_data':dataset[idx],
                                }

                    output_raw, output_text = self.llm.answer(input_text)
                    torch.cuda.empty_cache()

                    pred_text = transform_output_format("ToolLearning", output_text)

                    raw_output['text'].append(output_text)
                    raw_output['raw'].append(output_raw)

                    pred_output['predict'].append(pred_text)

                    raw_list.append(raw_output)
                    pred_list.append(pred_output)
                    write_jsonl(raw_datapath, raw_list)
                    write_jsonl(pred_datapath, pred_list)

                # * 计算评价指标
                result = calculate_score_ToolLearning(pred_datapath)
                # 保存结果  
                write_json(result_path, result, indent=4)

    def Plugin_eval(self,dataset_dir,output_dir):
        dataset_name_list = [
            # "dev",
            # "test_in_domain",
            # "test_out_domain",
            "nested",
            ]

        os.makedirs('./output/' + output_dir + '/', exist_ok=True)

        for dataset_name in dataset_name_list:
            dataset = read_json(dataset_dir+dataset_name+'.json')
            raw_datapath = './output/' + output_dir + '/raw_' + dataset_name+'.jsonl'
            pred_datapath = './output/' + output_dir + '/pred_' + dataset_name+'.jsonl'
            result_path = './output/' + output_dir + '/result_' + dataset_name+'.json'

            if not os.path.exists(result_path):
                # * 加载中途记录
                if os.path.exists(raw_datapath):
                    raw_list = read_jsonl(raw_datapath)
                else:
                    raw_list = []
                if os.path.exists(pred_datapath):
                    pred_list = read_jsonl(pred_datapath)
                else:
                    pred_list = []

                # * 与大模型问答
                for idx in track(range(len(pred_list), len(dataset)),description='Chating with '+self.llm.model_name+' ... '+'( ToolLearning '+dataset_name+' )'):

                    input_text, doc_id = dataset[idx]["conversations"][0]["value"],dataset[idx]["id"]

                    raw_output = {
                                    'id':doc_id,
                                    'text':[],
                                    'raw':[]
                                }
                    pred_output = {
                                    'id':doc_id,
                                    'predict':[],
                                    'gold_data':dataset[idx],
                                }

                    output_raw, output_text = self.llm.answer(input_text)
                    torch.cuda.empty_cache()

                    pred_text = transform_output_format("ToolLearning", output_text)

                    raw_output['text'].append(output_text)
                    raw_output['raw'].append(output_raw)

                    pred_output['predict'].append(pred_text)

                    raw_list.append(raw_output)
                    pred_list.append(pred_output)
                    write_jsonl(raw_datapath, raw_list)
                    write_jsonl(pred_datapath, pred_list)

                # * 计算评价指标
                result = calculate_score_ToolLearning(pred_datapath)
                # 保存结果  
                write_json(result_path, result, indent=4)