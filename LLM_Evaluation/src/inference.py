from llm_tools.llms import Auto_Model
from llm_tools.evaluation import LLM_eval
llm_eval = LLM_eval()

model_name = "LLaMA"
# model_name = "LLaMA_LoRA"

# model_name = "Mistral"

# model_path = "../PTM/Llama-2-7b-hf"
# model_path = "../PTM/Llama-2-7b-chat-hf"
# model_path = "../PTM/checkpoint-561"
model_path = "../PTM/checkpoint-retrieved_141"
# model_path = "../HWproject/LLM_SFT/output/Llama-2-7b-fp16 | old_dataset/Epoch 10"
# model_path = "../PTM/ToolLLaMA-2-7b-v2"
# model_path = "../PTM/vicuna-7b-v1.5"

# model_path = "../PTM/Mistral-7B-Instruct-v0.2"

# dataset_dir = "./data/fastchat_dataset/"
# output_dir = "lora_finetuned_gold_epcoh10"

# dataset_dir = "./data/fastchat_dataset_new/DPR/"
# output_dir = "finetuned_retrieved_DPR_Top5"

# dataset_dir = "./data/fastchat_dataset_new/DPR/"
# output_dir = "finetuned_retrieved_DPR_Top5_full"

# dataset_dir = "./data/fastchat_dataset_new/DPR/"
# output_dir = "toolllama_DPR_Top5_full"

# dataset_dir = "./data/fastchat_dataset_new/DPR/"
# output_dir = "vicuna_DPR_Top5_full"

# dataset_dir = "./data/fastchat_dataset_new/DPR/"
# output_dir = "mistral_DPR_Top5_full"

# dataset_dir = "./data/fastchat_dataset_new/BM25/"
# output_dir = "finetuned_retrieved_BM25_Top5_full"

# dataset_dir = "./data/fastchat_dataset_new/BM25/"
# output_dir = "finetuned_gold_BM25_Top5_full"

# dataset_dir = "./data/fastchat_dataset_new/DPR/"
# output_dir = "finetuned_gold_DPR_Top5_full"

# dataset_dir = "./data/fastchat_dataset_new/DPR/"
# output_dir = "llama_base_DPR_Top5_full"


# -------------------------------------------------------

print("model_name : ", model_name)
print("model_path : ", model_path)
# print("dataset_dir : ", dataset_dir)
# print("output_dir : ", output_dir)

llm_eval.set_llm(Auto_Model(model_name, model_path))

# llm_eval.ToolLearning_eval()
llm_eval.ToolLearning_eval_ICL()
# llm_eval.Plugin_eval(dataset_dir, output_dir)
