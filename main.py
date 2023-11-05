import logging
import aiogram.utils.markdown as md
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import openai
from dotenv import load_dotenv
import os

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
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)

logging.basicConfig(level=logging.INFO)

# Определение состояний бота
class Form(StatesGroup):
    choose_type = State()  # Состояние выбора типа (доклад или эссе)
    enter_word_count = State()  # Состояние ввода количества слов
    enter_topic = State()  # Состояние ввода темы

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
    await Form.choose_type.set()

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    item1 = types.KeyboardButton("Доклад")
    item2 = types.KeyboardButton("Эссе")

    markup.add(item1, item2)

    await message.reply("Выберите, что вы хотите сгенерировать? Можно доклад или эссе.", reply_markup=markup)

@dp.message_handler(lambda message: message.text not in ["Доклад", "Эссе"], state=Form.choose_type)
async def process_choose_type_invalid(message: types.Message):
    """
    Обработчик, если пользователь выбрал неверный тип
    """
    return await message.reply("Пожалуйста, используйте клавиатуру для выбора типа!")

@dp.message_handler(lambda message: message.text in ["Доклад", "Эссе"], state=Form.choose_type)
async def process_choose_type(message: types.Message, state: FSMContext):
    """
    Обработчик выбора типа (доклад или эссе)
    """
    async with state.proxy() as data:
        data['type'] = message.text

    # Переходим к следующему состоянию - "enter_word_count"
    await Form.enter_word_count.set()

    await message.reply("Сколько слов будет? (Введите число)")

@dp.message_handler(lambda message: not message.text.isdigit(), state=Form.enter_word_count)
async def process_enter_word_count_invalid(message: types.Message):
    """
    Обработчик, если пользователь ввел некорректное количество слов
    """
    return await message.reply("Пожалуйста, введите корректное число слов (только цифры)!")

@dp.message_handler(lambda message: message.text.isdigit(), state=Form.enter_word_count)
async def process_enter_word_count(message: types.Message, state: FSMContext):
    """
    Обработчик ввода количества слов
    """
    async with state.proxy() as data:
        data['word_count'] = int(message.text)

    # Переходим к следующему состоянию - "enter_topic"
    await Form.enter_topic.set()

    await message.reply("Введите тему для доклада:")

@dp.message_handler(lambda message: len(message.text) < 3, state=Form.enter_topic)
async def process_enter_topic_invalid(message: types.Message):
    """
    Обработчик, если пользователь ввел некорректную тему
    """
    return await message.reply("Пожалуйста, введите более длинную тему.")

@dp.message_handler(lambda message: len(message.text) >= 3, state=Form.enter_topic)
async def process_enter_topic(message: types.Message, state: FSMContext):
    """
    Обработчик ввода темы
    """
    async with state.proxy() as data:
        data['topic'] = message.text

        # Определяем текст ответа
        response_text = f"Вы выбрали сгенерировать {data['type']} на тему '{data['topic']}'. Количество слов = {data['word_count']}."

    # Отправляем ответ
    await message.reply(response_text, reply_markup=types.ReplyKeyboardRemove())

    # Сбрасываем состояние
    await state.finish()


# Запускаем бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)