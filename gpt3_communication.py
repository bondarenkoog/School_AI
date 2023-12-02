import openai
from dotenv import load_dotenv
import os

def setup_gpt3():
    # Загрузите переменные окружения из файла .env
    load_dotenv()
    OPENAI_TOKEN = os.getenv("OPENAI_TOKEN")

    # Проверка наличия токена OpenAI
    if not OPENAI_TOKEN:
        raise ValueError("No OPENAI_TOKEN provided in .env file")
    
    # Установите свой ключ API OpenAI здесь
    openai.api_key = OPENAI_TOKEN

def communicate_with_gpt3(prompt):
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[
        {"role": "system", "content": "Hello"},
        {"role": "user", "content": prompt},
    ]
)
    return response['choices'][0]['message']['content']
    