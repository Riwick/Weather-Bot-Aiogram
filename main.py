import asyncio
import logging

import requests
from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_TOKEN, ADMIN_ID, API_KEY
from keyboards import get_location_markup

dp = Dispatcher()


@dp.startup()
async def start_bot(bot: Bot):
    logging.log(level=logging.INFO, msg='Бот запущен')
    await bot.send_message(ADMIN_ID, 'Бот запущен')


@dp.shutdown()
async def stop_bot(bot: Bot):
    logging.log(level=logging.INFO, msg='Бот остановлен')
    await bot.send_message(ADMIN_ID, 'Бот остановлен')


@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer(f'Привет, {message.from_user.username}, '
                         f'отправь свою геолокацию чтобы я мог присылать тебе погоду',
                         reply_markup=get_location_markup)


@dp.message(F.content_type == ContentType.LOCATION)
async def confirm_location(message: Message):
    try:
        response = requests.get(
            f'http://api.openweathermap.org/data/2.5/weather?lat={message.location.latitude}'
            f'&lon={message.location.longitude}&lang=ru&units=metric&appid={API_KEY}'
        )
        data = response.json()
        logging.log(level=logging.INFO, msg=data)
        city = data['name']
        cur_temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        clouds = data['weather'][0].get('description')
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]
        await message.reply(f'Сегодня на улицах города <b>{city}</b>: \n'
                            f'Температура: <b>{cur_temp}°C</b>, ощущается как: <b>{feels_like}°C</b>, '
                            f'<b>{clouds}</b>\n'
                            f'Влажность воздуха: <b>{humidity}%</b>\n'
                            f'Ветер: <b>{wind} м/с</b>\n'
                            f'<b>Хорошего дня!</b>')
    except Exception as e:
        logging.log(level=logging.ERROR, msg=e)
        await message.reply('Возможно ты отправил мне неправильную геолокацию, попробуй ещё раз позже')

    return message.location.latitude, message.location.longitude


async def main():
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)

    try:
        await dp.start_polling(bot, allowed_updates=[])
    finally:
        await bot.session.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())
