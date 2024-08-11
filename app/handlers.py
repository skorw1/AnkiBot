import csv
import os
import logging

from functools import wraps
from aiogram import F
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import Command, Filter
from aiogram.types import FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import app.keyboards as kb
from utils import *
from app.database import *
from .messages import INTRO_MESSAGE, MULTIPLE_TRANSLATION_MESSAGE
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


TRANSLATIONS_LIST = []

# Настройка логгирования
logging.basicConfig(level=logging.INFO)

router = Router()

class TopicState(StatesGroup):
    title = State()
    deleting_title = State()
    adding_topic = State()
    adding_word = State()
    title_list = State()


@router.message(F.text.lower().strip() == 'добавить тему')
async def add_topic(message: types.Message, state: FSMContext):
    await state.set_state(TopicState.title)
    await message.answer('Введите название для темы:', reply_markup=kb.topic_adding_menu)

@router.message(F.text.lower() == 'отменить создание темы')
async def cancel_topic_creation(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer('Вы отменили создание темы', reply_markup=kb.topic_menu)

@router.message(TopicState.title)
async def adding_topic_to_db(message: types.Message, state: FSMContext):

    await state.update_data(title=message.text)
    data = await state.get_data()
    title = data.get('title', 'ошибка')
    await add_topics(message.from_user.id, title)
    await message.answer(f'Вы создали тему {title}', reply_markup=kb.topic_menu)
    await state.clear()


@router.message(F.text.lower().strip() == 'удалить тему')
async def delete_topic(message: types.Message, state: FSMContext):
    await state.set_state(TopicState.deleting_title)
    await message.answer('Введите название темы, которую хотите удалить:', reply_markup=kb.topic_deleting_menu)

@router.message(TopicState.deleting_title)
@router.message(F.text.lower() == 'отменить удаление темы')
async def deleting_topic_from_db(message: types.Message, state: FSMContext):

    if message.text.lower() == 'отменить удаление темы':
        await state.clear()
        await message.answer('Вы отменили удаление темы', reply_markup=kb.topic_menu)
    else:
        await state.update_data(deleting_title=message.text)
        data = await state.get_data()
        title = data.get('deleting_title', 'ошибка')
        await delete_words_by_topic_title(message.from_user.id, title=title)
        flag = await delete_topics(message.from_user.id, title)
        if flag:
            
            await message.answer(f'Вы удалили тему {title}', reply_markup=kb.topic_menu)
            await state.clear()
        else:
            await message.answer(f'Тема {title} не найдена для удаления')


@router.message(F.text.lower() == 'добавленные слова')
async def title_list(message: types.Message, state: FSMContext):
    await state.set_state(TopicState.title_list)
    await message.answer('Введите название темы которую хотите посмотреть')



@router.message(TopicState.title_list)
async def choosing_topic(message: types.Message, state: FSMContext):
    title = message.text
    if title.lower() == 'назад':
        await state.clear()
        await message.answer('Вы успешно вернулись назад', reply_markup=kb.topic_menu)
    else:
        topic_id = await if_topic_exist(message.from_user.id, title)
        if not topic_id[0] is None:
            topics = await get_words_by_topic(topic_id=topic_id[0])
            message_to_send = ''
            for i in topics:
                message_to_send += f'{i[0]} ---> {i[1]}\n'
            await message.answer(message_to_send, reply_markup=kb.topic_menu)
            await state.clear()
        else:
            await message.answer(f'Тема {title} не найдена для удаления')



@router.message(F.text.lower() == 'добавить слова в тему')
async def adding_topics(message: types.Message, state: FSMContext):
    await state.set_state(TopicState.adding_topic)
    await message.answer('Введите название <название темы>, куда будете добавлять слова', reply_markup=kb.word_adding_menu)

@router.message(F.text.lower() == 'отменить добавление темы')
async def remove_adding_words(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer('Отменение добавления слов успешно', reply_markup=kb.topic_menu)


@router.message(TopicState.adding_topic)
async def process_topic(message: types.Message, state: FSMContext):
    topics = await get_topics_by_user(message.from_user.id)
    topic_id = 0
    flag = False
    for i in topics:
        if i[1] == message.text:
            flag = True
            topic_id = i[0]
            break
    if flag:
        print(topics)
        await state.update_data(adding_topic=topic_id)
        await message.answer('Тема успешно добавлена, теперь введите слово или слова через megatranslate,', reply_markup=kb.word_adding_to_topic_menu)
        await state.set_state(TopicState.adding_word)
    else:
        await message.answer('Тема не найдена. Попробуйте снова')
            


@router.message(F.text.lower() == 'прекратить добавление слов')
async def remove_adding_words(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer('Отменение добавления слов успешно', reply_markup=kb.topic_menu)


    
@router.message(TopicState.adding_word)
async def process_words(message: types.Message, state: FSMContext):
    word = message.text
    async with aiohttp.ClientSession() as session:
        translated_word = await handle_text(session, word)
    data = await state.get_data()
    topic_id = data.get('adding_topic')
    word_id = await add_word(topic_id=topic_id, word=word, translation=translated_word[1])
    # Добавляем запись в learned_words
    await add_learned_word(message.from_user.id, word_id)
    await message.answer('успех')


@router.message(F.text.lower() == 'моя статистика')
async def my_statistic(message: types.Message):
    user_id = message.from_user.id
    topics = len(await get_topics_by_user(user_id=user_id))
    words = await get_count_words_by_user(message.from_user.id)
    await message.answer(f"Всего тем: {topics}, всего слов: {words}")






















@router.message(F.text.lower().strip() == 'мои темы')
async def topic_list(message: types.Message):
    topics = await get_topics_by_user(message.from_user.id)
    answer = 'Вот список ваших тем:\n\n'
    for i in range(len(topics)):
        answer += f"{i+1}. {topics[i][1]}\n"
    await message.answer(answer, reply_markup=kb.topic_menu)



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