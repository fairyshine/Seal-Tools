from method import apiset_path
from utils import *

from rank_bm25 import BM25Okapi

def plugin_dict_to_corpus(plugin_dict):
    corpus = []
    for plugin_name in plugin_dict:
        document = []
        document.extend(sent_string_to_word_list(plugin_dict[plugin_name]['api_description']))
        for param in plugin_dict[plugin_name]["required"]:
            document.extend(sent_string_to_word_list(plugin_dict[plugin_name]['parameters'][param]["description"]))
        corpus.append(document)
    return corpus

def retrieve_relevant_plugins(user_query, plugin_list, corpus):
    retriever = BM25Okapi(corpus)
    scores = retriever.get_scores(sent_string_to_word_list(user_query)).tolist()
    top_k_plugins_index = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:10]
    relevant_plugin_list = []
    for idx in top_k_plugins_index:
        relevant_plugin_list.append(plugin_list[idx]["api_name"])
    return relevant_plugin_list


apiset_list = read_jsonl(apiset_path)
api_list = []
api_dict = {}
for field in apiset_list:
    for field_name in field:
        api_list.extend(field[field_name])
        for api in field[field_name]:
            api_dict[api["api_name"]] = api

corpus = plugin_dict_to_corpus(api_dict)

file_list = [
    "train",
    "dev",
    "test_in_domain",
    "test_out_domain"
]
for file in file_list:
    raw_dataset = read_jsonl("./splitted_dataset/"+file+".jsonl")
    output_dataset = []
    for raw_data in raw_dataset:
        output_data = dict()
        question = raw_data[1]
        answers = [api_calling["api"] for api_calling in raw_data[0]] if type(raw_data[0])==list else [raw_data[0]["api"]]
        retrieved_list = retrieve_relevant_plugins(question, api_list, corpus)
        ctxs = [{"title":api_name} for api_name in retrieved_list]
        output_data["question"] = question
        output_data["answers"] = answers
        output_data["ctxs"] = ctxs
        output_dataset.append(output_data)

    write_json("./retriever_result_BM25/result_"+file+".json", output_dataset)

        
    