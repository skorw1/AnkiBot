from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton)

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='/csv')],
],

                                                    resize_keyboard=True,
                                                    input_field_placeholder='Воспользуйтесь меню ниже')


