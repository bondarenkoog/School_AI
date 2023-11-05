import aiogram
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
import openai
from dotenv import load_dotenv
import os
from aiogram.types import InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

# Загрузите переменные окружения из файла .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_TOKEN = os.getenv("OPENAI_TOKEN")

# Установите свой ключ API OpenAI здесь
api_key = OPENAI_TOKEN 
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
bot = Bot(token=BOT_TOKEN)
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

@dp.message_handler(commands=['document'])
async def check_requirements_for_doc(message:types.Message):
    
    doklad = KeyboardButton(text = 'доклад')
    essay = KeyboardButton(text = 'эссе')

    kb_choose_item = ReplyKeyboardMarkup(resize_keyboard =True).add(doklad,essay)
    await message.answer('Выберите , что вы хотите сгенерировать? Можно доклад или эссе ',reply_markup=kb_choose_item)
    k_word_100 = KeyboardButton(text = '100 слов')
    k_word_500 = KeyboardButton(text = '500 слов')
    k_word_1000 = KeyboardButton(text = '1000 слов')
    k_word_5000 = KeyboardButton(text = '5000 слов')
    kb_choose_count_word = ReplyKeyboardMarkup(resize_keyboard =True).add(k_word_100,k_word_500,
                                                                          k_word_1000,k_word_5000)
    
    
    await message.answer('Выберите количество слов ',reply_markup=kb_choose_count_word)








# Запускаем бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)