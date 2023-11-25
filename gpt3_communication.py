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
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150,
        stop=None,
        temperature=0.7,
    )
    return response['choices'][0]['text'].strip()
