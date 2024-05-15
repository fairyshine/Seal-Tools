import glob
import json

import pandas as pd


result_folder_path = './output/eval/result/'
models = ['ChatGLM2','Qwen','InternLM','LLaMA','Baichuan']
model_list = [
    'ChatGLM2_0','ChatGLM2_1','ChatGLM2_2','ChatGLM2_3',
    'Qwen_0','Qwen_1','Qwen_2','Qwen_3',
    'InternLM_0','InternLM_1','InternLM_2','InternLM_3',
    'LLaMA_0','LLaMA_1','LLaMA_2','LLaMA_3',
    'Baichuan_0','Baichuan_1','Baichuan_2','Baichuan_3'
    ]
metrics_list = [
    '14lap_amount','14lap_P','14lap_R','14lap_F1',
    '14res_amount','14res_P','14res_R','14res_F1',
    '15res_amount','15res_P','15res_R','15res_F1',
    '16res_amount','16res_P','16res_R','16res_F1',
    'ag_news_amount','ag_news_ACC',
    'MedQA_amount','MedQA_ACC',
    'MRPC_amount','MRPC_ACC',
    'SNLI_amount','SNLI_ACC',
    'MIT_MOVIE_Review_amount','MIT_MOVIE_Review_P','MIT_MOVIE_Review_R','MIT_MOVIE_Review_F1',
    'MIT_Restaurant_Review_amount','MIT_Restaurant_Review_P','MIT_Restaurant_Review_R','MIT_Restaurant_Review_F1',
    'NCBIdisease_amount','NCBIdisease_P','NCBIdisease_R','NCBIdisease_F1',
    'ontoNotes5_amount','ontoNotes5_P','ontoNotes5_R','ontoNotes5_F1',
    'scierc_amount','scierc_P','scierc_R','scierc_F1',
    'semeval_amount','semeval_P','semeval_R','semeval_F1',
    'WebNLG_amount','WebNLG_P','WebNLG_R','WebNLG_F1',
    'ace05-evt_amount','ace05-evt_P_trigger','ace05-evt_R_trigger','ace05-evt_F1_trigger','ace05-evt_P','ace05-evt_R','ace05-evt_F1',
    'casie_amount','casie_P_trigger','casie_R_trigger','casie_F1_trigger','casie_P','casie_R','casie_F1',
    'PHEE_amount','PHEE_P_trigger','PHEE_R_trigger','PHEE_F1_trigger','PHEE_P','PHEE_R','PHEE_F1',
    'api_we_instructed_ACC_api','api_we_instructed_P_slot','api_we_instructed_R_slot','api_we_instructed_F1_slot','api_we_instructed_P_value','api_we_instructed_R_value','api_we_instructed_F1_value',
    ]

def read_json(data_path):
    dataset=[]
    with open(data_path,'r', encoding='UTF-8') as f:
        dataset = json.load(f)
    return dataset

data_init = [[None]*len(metrics_list)]*len(model_list)
df = pd.DataFrame(data_init, index=model_list, columns=metrics_list).astype(float)
df.index.name = '%'
for result_file_path in glob.glob(result_folder_path+'*.json'):
    result_file_name = result_file_path.split('/')[-1][:-5]
    for i in range(len(result_file_name)-1,0,-1):
        if result_file_name[i]=='_' and result_file_name[:i] in models:
            split = i
            break
    model,metrics = result_file_name[:split],result_file_name[split+1:]

    result = read_json(result_file_path)
    for prompt_idx in range(4):
        for key in result[str(prompt_idx)]:
            if key == 'amount':
                df.loc[model+'_'+str(prompt_idx), metrics+'_'+key] = result[str(prompt_idx)][key][1] / result[str(prompt_idx)][key][0] * 100
            else:
                df.loc[model+'_'+str(prompt_idx), metrics+'_'+key] = result[str(prompt_idx)][key] * 100
            

df.to_csv('./output/LLM评测结果.csv',float_format="%.2f")