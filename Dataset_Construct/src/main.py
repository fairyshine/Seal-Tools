from model import LLM
from method import *


if __name__ == "__main__":
    ChatGPT = LLM()
    directory_check()

    fieldset_generation(ChatGPT.answer)
    field_filter()
    subfield_generation(ChatGPT.answer)

    api_generation(ChatGPT.answer)

    api_param_example_check()
    api_param_example_generation(ChatGPT.answer)

    easy_usecase_generation(ChatGPT.answer)

    for i in range(1000):
        api_pool_selection(ChatGPT.answer)
        difficult_usecase_generation(ChatGPT.answer)

