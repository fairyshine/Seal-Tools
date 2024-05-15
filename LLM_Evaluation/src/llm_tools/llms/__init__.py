from llm_tools.llms.ChatGPT import ChatGPT
from llm_tools.llms.ChatGLM import ChatGLM
from llm_tools.llms.MOSS import MOSS
from llm_tools.llms.ChatYuan import ChatYuan
from llm_tools.llms.CPM_Bee import CPM_Bee
from llm_tools.llms.LLaMA import LLaMA
from llm_tools.llms.LLaMA_LoRA import LLaMA_LoRA
from llm_tools.llms.Baichuan import Baichuan
from llm_tools.llms.InternLM import InternLM
from llm_tools.llms.Qwen import Qwen
from llm_tools.llms.Mistral import Mistral

__all__ = [
    "Auto_Model",
    "ChatGPT",
    "ChatGLM",
    "MOSS",
    "ChatYuan",
    "CPM_Bee",
    "LLaMA",
    "LLaMA_LoRA",
    "Baichuan",
    "InternLM",
    "Qwen",
    "Mistral"
]

def Auto_Model(model_name,model_path,distribute=False):
    match model_name:
        case "ChatGLM":
            return ChatGLM(model_path,distribute=distribute)
        case "MOSS":
            return MOSS(model_path)
        case "ChatYuan":
            return ChatYuan(model_path)
        case "CPM_Bee":
            return CPM_Bee(model_path)
        case "LLaMA":
            return LLaMA(model_path)
        case "LLaMA_LoRA":
            return LLaMA_LoRA(model_path)
        case "Baichuan":
            return Baichuan(model_path)
        case "InternLM":
            return InternLM(model_path)
        case "Qwen":
            return Qwen(model_path)
        case "Mistral":
            return Mistral(model_path)