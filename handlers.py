from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from gpt3_communication import communicate_with_gpt3
import logging

class Form(StatesGroup):
    choose_type = State()
    enter_word_count = State()
    enter_topic = State()

async def start_handler(message: types.Message):
    help_message = (
        "Доступные команды:\n"
        "/start - Информация о боте и его возможностях.\n"
        "/document - Сгенерировать доклад или эссе.\n"
    )
    instructions_message = (
        "Инструкция по использованию команды /document:\n"
        "1. Выберите команду /document.\n"
        "2. Следуйте указаниям бота для создания доклада/эссе."
    )
    await message.answer(help_message)
    await message.answer(instructions_message)


async def ask_question(message: types.Message):
    user_input = message.text.replace("/ask ", "")
    response = communicate_with_gpt3(user_input)
    await message.reply("Мой ответ: " + response)

async def repeat_message(message: types.Message):
    user_input = message.text.replace("/repeat ", "")
    await message.reply(user_input)

async def check_requirements_for_doc(message: types.Message):
    await Form.choose_type.set()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(types.KeyboardButton("Доклад"), types.KeyboardButton("Эссе"))
    await message.reply("Выберите, что вы хотите сгенерировать? Можно доклад или эссе.", reply_markup=markup)
    logging.info(f'Пользователь {message["from"]["first_name"]} находится в состоянии выбора кнопки ')

async def process_choose_type_invalid(message: types.Message):
    return await message.reply("Пожалуйста, используйте клавиатуру для выбора типа!")

async def process_choose_type(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['type'] = message.text
    await Form.enter_word_count.set()
    await message.reply("Сколько слов будет? (Введите число)")

async def process_enter_word_count_invalid(message: types.Message):
    return await message.reply("Пожалуйста, введите корректное число слов (только цифры)!")

async def process_enter_word_count(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['word_count'] = int(message.text)
    await Form.enter_topic.set()
    await message.reply("Введите тему для доклада:")

async def process_enter_topic_invalid(message: types.Message):
    return await message.reply("Пожалуйста, введите более длинную тему.")

async def process_enter_topic(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['topic'] = message.text
        response_text = f"Вы выбрали сгенерировать {data['type']} на тему '{data['topic']}'. Количество слов = {data['word_count']}."
        prompt = f"Помоги мне написать {data['type']}. Тема: {data['topic']}, Количество слов = {data['word_count']} "
        await message.answer('Ваши параметры приняты. Генерация может занять от 1 до 5 минут, пожалуйста подожите...')
        try:
            response = communicate_with_gpt3(prompt) ### здесь будет готовый ответ от чатгпт
            await message.reply(response_text, reply_markup=types.ReplyKeyboardRemove())
            await message.reply(response)
        except Exception as e:
            await message.answer(f"ошибка генерации.",reply_markup=types.ReplyKeyboardRemove())
            
    

    await state.finish()

def setup_handlers(dp):
    dp.message_handler(commands=['ask'])(ask_question)
    dp.message_handler(commands=['repeat'])(repeat_message)
    dp.message_handler(commands=['document'])(check_requirements_for_doc)
    dp.message_handler(lambda message: message.text not in ["Доклад", "Эссе"], state=Form.choose_type)(process_choose_type_invalid)
    dp.message_handler(lambda message: message.text in ["Доклад", "Эссе"], state=Form.choose_type)(process_choose_type)
    dp.message_handler(lambda message: not message.text.isdigit(), state=Form.enter_word_count)(process_enter_word_count_invalid)
    dp.message_handler(lambda message: message.text.isdigit(), state=Form.enter_word_count)(process_enter_word_count)
    dp.message_handler(lambda message: len(message.text) < 3, state=Form.enter_topic)(process_enter_topic_invalid)
    dp.message_handler(lambda message: len(message.text) >= 3, state=Form.enter_topic)(process_enter_topic)
    dp.message_handler(commands=['start'])(start_handler)

