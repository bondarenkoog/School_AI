from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command
from aiogram.utils import executor
import asyncio
import logging

TOKEN = '6253053031:AAF8tQLUVZrqyFJUMzOgm9Kzv5-e-c31drc'
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Определение состояний
class Form(StatesGroup):
    name = State()  # Состояние для имени

# Запуск задачи на сброс состояния
async def reset_state_after_timeout(state: FSMContext, user_id: int, delay: int):
    await asyncio.sleep(delay)
    current_state = await state.get_state()
    if current_state is not None:  # Проверяем, активно ли ещё состояние
        await state.finish()
        await bot.send_message(user_id, "Время ожидания ответа истекло. Попробуйте снова.")


# Обработчик команды /hi
@dp.message_handler(commands=['hi'], state='*')
async def start_dialog(message: types.Message, state: FSMContext):
    await Form.name.set()
    await message.reply("Как тебя зовут? Ответь в течение 10 секунд.")
    # Передаём user_id в задачу
    asyncio.create_task(reset_state_after_timeout(state, message.from_user.id, 10))

# Обработчик для получения имени
@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    if state_data.get("canceled"):  # Проверяем, была ли задача отменена
        return  # Если задача отменена, не реагируем на сообщение

    async with state.proxy() as data:
        data['name'] = message.text
    await state.finish()
    await message.reply(f"Приятно познакомиться, {message.text}!")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)