from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

get_location_markup = ReplyKeyboardMarkup(keyboard=[
    [
        KeyboardButton(text='Отправить геолокацию', request_location=True)
    ],
], resize_keyboard=True, input_field_placeholder='Отправь свою геолокацию, чтобы я мог присылать тебе погоду')

