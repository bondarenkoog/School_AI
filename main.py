import aiogram
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import openai

# Установите свой ключ API OpenAI здесь
api_key = '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'
openai.api_key = api_key

# Функция для взаимодействия с GPT-3.5 и получения ответа
def communicate_with_gpt3(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",  # Используем модель GPT-3.5
        prompt=prompt,
        max_tokens=150,  # Максимальное количество токенов в ответе
        stop=None,  # Параметр для указания стоп-фразы, если необходимо
        temperature=0.7,  # Параметр температуры для управления генерацией
    )
    return response['choices'][0]['text'].strip()

# Создаем экземпляр бота и диспетчера
bot = Bot(token="6253053031:AAFUrJcwqdnJtupxFf_U5M3Qmgqkj-GCKgk")
dp = Dispatcher(bot)

# Функция-хендлер для обработки команды /ask
@dp.message_handler(commands=['ask'])
async def ask_question(message: types.Message):
    # Получаем вопрос от пользователя
    user_input = message.text.replace("/ask ", "")
    
    # Построение запроса к GPT-3.5 и получение ответа
    response = communicate_with_gpt3(user_input)
    
    # Отправка ответа пользователю
    await message.reply("Мой ответ: " + response)

# Функция-хендлер которая будет дублировать сообщение
@dp.message_handler(commands=['repeat'])
async def ask_question(message: types.Message):
    # Получаем вопрос от пользователя
    user_input = message.text.replace("/repeat ", "")
    
    # Отправка ответа пользователю
    await message.reply(user_input)


# Запускаем бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)