from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_menu = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Множественный перевод'), KeyboardButton(text='Мои темы')],
        [KeyboardButton(text='/csv'), KeyboardButton(text='Моя статистика')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Воспользуйтесь меню ниже')

main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='/csv')],
],  resize_keyboard=True,
    input_field_placeholder='Воспользуйтесь меню ниже')

multiple_translation_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Главное меню')],
])


topic_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Добавить тему'), KeyboardButton(text='Удалить тему')],
    [KeyboardButton(text='Мои темы'), KeyboardButton(text='Добавить слова в тему')],
    [KeyboardButton(text='Главное меню'), KeyboardButton(text='Добавленные слова')]
],  resize_keyboard=True,
    input_field_placeholder='Воспользуйтесь меню ниже')

topic_adding_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отменить создание темы')]

],  resize_keyboard=True,
    input_field_placeholder='Воспользуйтесь меню ниже')


topic_deleting_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отменить создание темы')]

],  resize_keyboard=True,
    input_field_placeholder='Воспользуйтесь меню ниже')

word_adding_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Отменить добавление темы')]

],  resize_keyboard=True,
    input_field_placeholder='Воспользуйтесь меню ниже')

word_adding_to_topic_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Прекратить добавление слов')]

],  resize_keyboard=True,
    input_field_placeholder='Воспользуйтесь меню ниже')