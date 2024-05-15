from transformers import AutoTokenizer, AutoModelForCausalLM
class Mistral():
    def __init__(self,checkpoint_path=''):
        self.checkpoint_path = checkpoint_path

        self.tokenizer = AutoTokenizer.from_pretrained(self.checkpoint_path)
        # self.model = AutoModelForCausalLM.from_pretrained(self.checkpoint_path, trust_remote_code=True).half().cuda()
        self.model = AutoModelForCausalLM.from_pretrained(self.checkpoint_path, device_map="auto")
        self.model_name = 'Mistral'
        self.model.eval()

    def answer(self,input_text):
        try:
            messages = [
                {"role": "user", "content": input_text}
            ]
            encodeds = self.tokenizer.apply_chat_template(messages, return_tensors="pt")

            generated_ids = self.model.generate(encodeds, max_new_tokens=1000, do_sample=True)
            decoded = self.tokenizer.batch_decode(generated_ids)
            return decoded[0], decoded[0][len(input_text):]
        except:
            output = ''
            return output, output

    def chat(self):
        pass