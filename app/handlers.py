import csv
import os
import logging
from functools import wraps
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command
from aiogram.types import FSInputFile
import app.keyboards as kb
from utils import check_word, download_audio, google_translate, microsoft_translate
from utils import anti_spam_decorator



TRANSLATIONS_LIST = []

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

router = Router()

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


@router.message(Command('csv'))
@anti_spam_decorator
async def handle_csv_command(message: types.Message) -> None:
    await create_and_send_csv(message.from_user.id, message.chat.id, message.bot)



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
        await message.answer(f'Translation: {translation}', reply_markup=kb.main)
        TRANSLATIONS_LIST.append((word, translation))