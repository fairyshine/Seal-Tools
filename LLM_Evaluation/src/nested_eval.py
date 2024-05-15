from llm_tools.llms import Auto_Model
from llm_tools.evaluation import LLM_eval
llm_eval = LLM_eval()

# model_name = "LLaMA"
# model_name = "LLaMA_LoRA"

model_name = "Mistral"

# model_path = "/public/home/jhfang/mswu_wlchen/PTM/Llama-2-7b-hf"
# model_path = "/public/home/jhfang/mswu_wlchen/PTM/Llama-2-7b-chat-hf"
# model_path = "/public/home/jhfang/mswu_wlchen/PTM/checkpoint-561"
# model_path = "/public/home/jhfang/mswu_wlchen/PTM/checkpoint-retrieved_141"
# model_path = "/public/home/jhfang/mswu_wlchen/HWproject/LLM_SFT/output/Llama-2-7b-fp16 | old_dataset/Epoch 10"
# model_path = "/public/home/jhfang/mswu_wlchen/PTM/ToolLLaMA-2-7b-v2"
# model_path = "/public/home/jhfang/mswu_wlchen/PTM/vicuna-7b-v1.5"

model_path = "/public/home/jhfang/mswu_wlchen/PTM/Mistral-7B-Instruct-v0.2"

dataset_dir = "./data/fastchat_dataset_new/DPR/"

# output_dir = "llama2-Chat_nested"
# output_dir = "finetuned_retrieved_nested"
output_dir = "mistral_nested"

# -------------------------------------------------------

print("model_name : ", model_name)
print("model_path : ", model_path)
print("dataset_dir : ", dataset_dir)
print("output_dir : ", output_dir)

llm_eval.set_llm(Auto_Model(model_name, model_path))

llm_eval.Plugin_eval(dataset_dir, output_dir)