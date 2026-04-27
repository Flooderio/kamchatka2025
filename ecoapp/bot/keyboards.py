from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def options_keyboard(options: list[str]) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=option)] for option in options],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
