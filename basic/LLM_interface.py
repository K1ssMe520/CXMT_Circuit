from openai import OpenAI
import os

class KIMI:
    name = 'moonshot-v1-8k'
    key = os.getenv("KIMI_KEY")
    client = OpenAI(api_key = key, base_url = "https://api.moonshot.cn/v1")
    def get_answer(request: str):
        completion = KIMI.client.chat.completions.create(
            model = "moonshot-v1-8k",
            messages = [
                {"role": "assistant", "content": request}
            ],
            temperature = 0.0
        )
        
        return completion.choices[0].message.content

class DeepSeek_R1:
    name = 'deepseek-chat'
    key = os.getenv("DSV3_KEY")
    client = OpenAI(api_key = key, base_url = "https://api.deepseek.com")
    def get_answer(request: str):
        completion = DeepSeek_R1.client.chat.completions.create(
            model = "deepseek-chat",
            messages = [
                {"role": "assistant", "content": request}
            ],
            temperature = 0.0,
        )
        
        return completion.choices[0].message.content

