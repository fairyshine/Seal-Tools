import difflib
import json
import os
import random
import re
import string


def read_jsonl(data_path):
    dataset=[]
    with open(data_path,'r', encoding='UTF-8') as f:
        for line in f:
            dataset.append(json.loads(line))
    return dataset

def read_json(data_path):
    with open(data_path,'r', encoding='UTF-8') as f:
        dataset= json.load(f)
    return dataset

def write_jsonl(data_path,dataset):
    with open(data_path,'w', encoding='UTF-8') as f:
        for data in dataset:
            f.writelines(json.dumps(data, ensure_ascii=False))
            f.write('\n')

def write_json(data_path,dataset):
    with open(data_path,'w', encoding='UTF-8') as f:
            f.write(json.dumps(dataset, indent=2, ensure_ascii=False))

def append_jsonl(data_path,append_dataset):
    with open(data_path, 'a', encoding='UTF-8') as f:
        for data in append_dataset:
            f.writelines(json.dumps(data, ensure_ascii=False))
            f.write('\n')

def str_similarity(s1, s2):
    return difflib.SequenceMatcher(None, s1, s2).quick_ratio()

def set_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    jaccard_similarity = intersection / union
    # print("Jaccard 相似度:", jaccard_similarity)
    return jaccard_similarity


def match_given_pattern(text,pattern):
    location = re.search(pattern,text).span()
    matched_text = text[location[0]:location[1]]
    return matched_text

def check_file_path(data_path):
    if not os.path.exists(data_path):
        open(data_path, 'a', encoding='UTF-8').close()

def generate_id(length=8):
    # 可以包含在用户名中的字符集
    characters = string.ascii_letters + string.digits  # 字母和数字
    username = ''.join(random.choice(characters) for _ in range(length))
    return username


def generate_date():
    # 生成随机年份（在范围内选择一个年份，例如 2000 到 2023）
    year = random.randint(2000, 2023)
    # 生成随机月份（在 1 到 12 之间选择一个月份）
    month = random.randint(1, 12)
    # 根据月份确定该月的最大天数
    if month in [1, 3, 5, 7, 8, 10, 12]:
        max_day = 31
    elif month == 2:
        # 如果是2月，需要考虑闰年
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            max_day = 29
        else:
            max_day = 28
    else:
        max_day = 30
    # 生成随机日期（在 1 到 max_day 之间选择一个日期）
    day = random.randint(1, max_day)
    # 格式化日期为 YYYY-MM-DD
    return f"{year:04d}-{month:02d}-{day:02d}"

def generate_clock():
    # 生成随机的小时和分钟
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    # 格式化为时钟时间（HH:MM）
    return f"{hour:02d}:{minute:02d}"

def shuffle_list(raw_list):
    idx_list = [i for i in range(len(raw_list))]
    new_list = []
    for idx in idx_list:
        new_list.append(raw_list[idx])
    return new_list


def sent_string_to_word_list(text):
    modified_text = text.replace(".","").replace(",","")
    word_list = [word.lower() for word in modified_text.split(" ")]
    return word_list