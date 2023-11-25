import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
import os

from handlers import setup_handlers
from gpt3_communication import setup_gpt3

# Загрузите переменные окружения из файла .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Проверка наличия токена бота
if not BOT_TOKEN:
    raise ValueError("No BOT_TOKEN provided in .env file")

# Создаем экземпляр бота и диспетчера
storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)

logging.basicConfig(level=logging.INFO)

# Устанавливаем связь с GPT-3
setup_gpt3()

# Устанавливаем обработчики
setup_handlers(dp)

# Запускаем бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
