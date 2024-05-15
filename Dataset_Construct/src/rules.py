import random
from utils import *

def rules_for_parameters(type_str,parameter,description,mode):
    match type_str:
        case "str":
            return rules_for_str_parameters(parameter,description,mode)
        case "int":
            return rules_for_int_parameters(parameter,description,mode)
        case "float":
            return rules_for_float_parameters(parameter,description,mode)
        case "bool":
            return rules_for_bool_parameters(parameter,description,mode)

def rules_for_str_parameters(paramter,description,mode):
    pattern_list = ["ID", "time", "date", "timestamp", "email", "IP"]
    text = paramter + ' ' + description
    for pattern in pattern_list:
        if pattern.lower() in text.lower():
            match mode:
                case "judge":
                    return True
                case "generate":
                    return generate_str(pattern)
    return False

def rules_for_int_parameters(paramter,description,mode):
    pattern_list = ["age", "year", ""]
    text = paramter + ' ' + description
    for pattern in pattern_list:
        if pattern.lower() in text.lower():
            match mode:
                case "judge":
                    return True
                case "generate":
                    return generate_int(pattern)
    return False

def rules_for_float_parameters(paramter,description,mode):
    pattern_list = ["rate","rating", "latitude", "longtitude", "temperature", "speed", "weight", ""]
    text = paramter + ' ' + description
    for pattern in pattern_list:
        if pattern.lower() in text.lower():
            match mode:
                case "judge":
                    return True
                case "generate":
                    return generate_float(pattern)
    return False

def rules_for_bool_parameters(parameter,description,mode):
    match mode:
        case "judge":
            return True
        case "generate":
            return random.choice([True, False])
        
def generate_str(pattern):
    match pattern:
        case "ID":
            return generate_id(random.randint(8,12))
        case "time":
            return generate_clock()
        case "date":
            return generate_date()
        case "timestamp":
            second = random.randint(0, 59)
            return generate_date()+" "+generate_clock()+f":{second:02d}"
        case "email":
            # 生成随机的用户名部分
            username = generate_id(random.randint(8,12))
            # 随机选择一个域名
            domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'aol.com', 'icloud.com']
            domain = random.choice(domains)
            # 组合用户名和域名来生成电子邮件地址
            email = f"{username}@{domain}"
            return email
        case "IP":
            return "192.168."+str(random.randint(0,255))+"."+str(random.randint(1,255))

def generate_int(pattern):
    match pattern:
        case "age":
            return str(random.randint(5,80))
        case "year":
            return str(random.randint(1975,2023))
        case "":
            return str(random.randint(1,100))

def generate_float(pattern):
    match pattern:
        case "rate":
            return random.random()
        case "rating":
            return str(round(random.uniform(0.0,10.0),1)) 
        case "latitude":
            return str(round(random.uniform(-90.0,90.0),4))
        case "longtitude":
            return str(round(random.uniform(-180.0,180.0),4))
        case "temperature":
            return str(round(random.uniform(20.0,32.0),1))
        case "speed":
            return str(round(random.uniform(1.0,20.0),1))
        case "weight":
            return str(round(random.uniform(50.0,70.0),1))
        case "":
            return str(round(random.uniform(5.0,50.0),1))