import os
import logging
import asyncio
import pandas as pd
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

# Указываем токен бота
TOKEN = "7990633748:AAGI2aInnuvBoODhK5hglwJwIjxP_jrzQTw"

# Путь к файлу со словами
file_path = "english_words_fully_fixed.xlsx"  # Файл должен находиться в той же директории

def load_words():
    if os.path.exists(file_path):
        return pd.read_excel(file_path).to_dict(orient='records')
    return []

# Загружаем список слов
words = load_words()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Создаем бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Клавиатура для старта
start_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Начать тренировку")]], resize_keyboard=True
)

# Словарь для отслеживания текущего слова пользователей
user_progress = {}

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Привет! Давай учить слова! Нажми 'Начать тренировку'", reply_markup=start_keyboard)

@dp.message(Command("reload"))
async def reload_words(message: types.Message):
    global words
    words = load_words()
    await message.reply("Список слов обновлён! 🆕")

@dp.message(lambda message: message.text == "Начать тренировку")
async def start_training(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_progress:
        user_progress[user_id] = 0
    await send_next_word(message)

async def send_next_word(message: types.Message):
    user_id = message.from_user.id
    if user_progress[user_id] < len(words):
        word_pair = words[user_progress[user_id]]
        user_progress[user_id] += 1
        await message.answer(f"Как переводится: {word_pair.get('English', 'Неизвестное слово')}?")
    else:
        await message.answer("Вы выучили все слова! 🎉")

@dp.message()
async def check_translation(message: types.Message):
    user_id = message.from_user.id
    current_index = user_progress.get(user_id, 0) - 1
    if current_index < 0:
        await message.answer("Нажмите 'Начать тренировку'")
        return
    
    correct_translation = words[current_index].get('Russian', '').lower().strip()
    if message.text.lower().strip() == correct_translation:
        await message.answer("✅ Верно! Двигаемся дальше.")
        await send_next_word(message)
    else:
        await message.answer(f"❌ Неправильно. Правильный перевод: {correct_translation}")

async def main():
    try:
        await dp.start_polling(bot, skip_updates=True)
    except asyncio.CancelledError:
        logging.info("Polling was cancelled.")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(main())
    else:
        loop.run_until_complete(main())


