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
    [KeyboardButton(text='Раделитель: запятая')],
    [KeyboardButton(text='Раделитель: пробел')],
    [KeyboardButton(text='Раделитель: перенос строки')],
    [KeyboardButton(text='Главное меню')],
])


