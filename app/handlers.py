import csv
import os
import logging

from functools import wraps
from aiogram import F
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command, Filter
from aiogram.types import FSInputFile
import app.keyboards as kb
from utils import *
from .messages import INTRO_MESSAGE, MULTIPLE_TRANSLATION_MESSAGE
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


TRANSLATIONS_LIST = []

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

router = Router()

"""
Обработчик отвечающий за множественный перевод
"""
@router.message(F.text.startswith('megatranslate'))
@anti_spam_decorator
async def multiple_translation(message: types.Message) -> None:
    separator = ','

    sentences = message.text[14:].split(separator)
    result = await handle_multiple_requests(sentences)

    for i in result:
        if i:
            await message.answer(f"Перевод: {i[0]} --- > {i[1]}")
            TRANSLATIONS_LIST.append(i)


"""
Функция создает и отправляет пользователю CSV файл
"""
async def create_and_send_csv(user_id: int, chat_id: int, bot) -> None:
    path_to_csv = f"{user_id}.csv"
    try:
        # Создание CSV файла
        with open(path_to_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(TRANSLATIONS_LIST)

        # Отправка CSV файла
        document = FSInputFile(path=path_to_csv)
        await bot.send_document(chat_id, document)
        
    except Exception as e:
        logging.error('Ошибка создания или отправки csv файла: %s', str(e))
    finally:
        # Удаление файла после отправки
        if os.path.exists(path_to_csv):
            os.remove(path_to_csv)

"""
Обработчик сообщений /start, /help
"""
@router.message(Command('start'))
@router.message(Command('help'))
@anti_spam_decorator
async def handle_start(message: types.Message) -> None:
    await message.answer(INTRO_MESSAGE, reply_markup=kb.start_menu)

"""
Обработчик команды /csv
"""
@router.message(Command('csv'))
@anti_spam_decorator
async def handle_csv_command(message: types.Message) -> None:
    if not TRANSLATIONS_LIST:
        await message.answer('CSV Файл пустой. Пожалуйста, добавьте слова/фразы сначало.')
    else:
        await create_and_send_csv(message.from_user.id, message.chat.id, message.bot)

"""
Обработчик команды /multiple_translation и сообщения Множественный перевод
"""
@router.message(Command('multiple_translation'))
@router.message(F.text.lower() == 'множественный перевод')
@anti_spam_decorator
async def handle_multiple_translation(message: types.Message) -> None:
    await message.answer(MULTIPLE_TRANSLATION_MESSAGE, reply_markup=kb.multiple_translation_menu)


"""
Обработчик сообщения главное меню
"""
@router.message(F.text.lower() == 'главное меню')
@anti_spam_decorator
async def main_menu(message: types.Message) -> None:
    await message.answer("Вы вернулись в главное меню", reply_markup=kb.start_menu)

"""
Главный обработчик сообщений. Переводит по слову или целую фразу.
"""
@router.message()
@anti_spam_decorator
async def handle_message(message: types.Message) -> None:

    word = message.text
    if len(word.split()) == 1:
        try:
            translation = check_word(word)
            await message.answer(f'Перевод: {translation}')
            
            download_audio(word)
            audio_file_path = f'audio_{word}.mpeg'
            audio = FSInputFile(path=audio_file_path, filename=f'{word.lower()}.mp3')
            await message.bot.send_audio(message.chat.id, audio=audio)
            
            TRANSLATIONS_LIST.append((word, translation))
            os.remove(audio_file_path)
            
        except Exception as e:
            await message.answer(f'Ошибка: {str(e)}')
    else:
        translation = microsoft_translate(word)
        await message.answer(f'Translation: {translation}', reply_markup=kb.main_menu)
        TRANSLATIONS_LIST.append((word, translation))