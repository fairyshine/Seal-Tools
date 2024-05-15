import json

def read_json(data_path):
    dataset=[]
    with open(data_path,'r', encoding='UTF-8') as f:
        dataset = json.load(f)
    return dataset

def write_json(data_path, dataset,indent=0):
    with open(data_path,'w', encoding='UTF-8') as f:
            json.dump(dataset, f, ensure_ascii=False, indent=indent)

def read_jsonl(data_path):
    dataset=[]
    with open(data_path,'r', encoding='UTF-8') as f:
        for line in f:
            dataset.append(json.loads(line))
    return dataset

def write_jsonl(data_path, dataset):
    with open(data_path,'w', encoding='UTF-8') as f:
        for data in dataset:
            f.writelines(json.dumps(data, ensure_ascii=False))#, indent=4))
            f.write('\n')