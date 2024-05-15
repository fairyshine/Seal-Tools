
def process_input_text(dataset_name, PROMPT_LIST, data):
    match dataset_name:
        case "TableEE":
            return [PROMPT.format(str(data['content_list'])) for PROMPT in PROMPT_LIST], data['doc_id']
        case '14lap' | '14res' | '15res' | '16res' \
            | 'ag_news' | 'MedQA' | 'MRPC' | 'SNLI' \
            | 'MIT_MOVIE_Review' | 'MIT_Restaurant_Review' | 'NCBIdisease' | 'ontoNotes5' \
            | 'scierc' | 'semeval' | 'WebNLG' \
            | 'ace05-evt' | 'casie' | 'PHEE':
            return [PROMPT + str(data['text']) + '\n' for PROMPT in PROMPT_LIST], data['id']
        case 'api_we_instructed':
            input_text_list = []
            for PROMPT in PROMPT_LIST:
                input_text = PROMPT
                for i in data['text']:
                    if i['speaker'] == 'USER':
                        input_text += 'user:\"' + str(i['text']) + '\"\n'
                    if i['speaker'] == 'SYSTEM':
                        input_text += 'assistant:\"' + str(i['text']) + '\"\n'
                input_text_list.append(input_text)
            return input_text_list , data["id"]                
        case _:
            print("ERROR!")
