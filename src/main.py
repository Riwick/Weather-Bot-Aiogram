import asyncio
import logging
from datetime import datetime, timedelta

import aiohttp

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from asyncpg import UniqueViolationError

from config import BOT_TOKEN, ADMIN_ID, API_KEY
from database import save_position, update_position, get_all_users
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
        await save_position(user_id=message.from_user.id, lat=message.location.latitude,
                            lon=message.location.longitude)
    except UniqueViolationError:
        try:
            await update_position(user_id=message.from_user.id, lat=message.location.latitude,
                                  lon=message.location.longitude)
        except Exception as e:
            logging.log(level=logging.ERROR, msg=e)
            await message.answer('Похоже, что-то пошло не так. '
                                 'Пожалуйста проверь отправленную геолокацию или попробуй'
                                 'ещё раз позже')
    async with aiohttp.ClientSession() as session:
        response = await session.get(
            f'http://api.openweathermap.org/data/2.5/weather?lat={message.location.latitude}'
            f'&lon={message.location.longitude}&lang=ru&units=metric&appid={API_KEY}'
        )
        data = await response.json()
        city = data['name']
        cur_temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        clouds = data['weather'][0].get('description')
        humidity = data["main"]["humidity"]
        wind = data["wind"]["speed"]

        code_to_smile = {
            "Clear": "Ясно \U00002600",
            "Clouds": "Облачно \U00002601",
            "Rain": "Дождь \U00002614",
            "Drizzle": "Дождь \U00002614",
            "Thunderstorm": "Гроза \U000026A1",
            "Snow": "Снег \U0001F328",
            "Mist": "Туман \U0001F32B"
        }
        weather_description = data["weather"][0]["main"]

        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "Посмотри в окно, я не понимаю, что там за погода..."

        await message.answer(f'Сегодня на улицах города <b>{city}</b>: \n'
                             f'Температура: <b>{cur_temp}°C</b>, ощущается как: <b>{feels_like}°C</b>, '
                             f'<b>{wd.lower()}</b>\n'
                             f'Влажность воздуха: <b>{humidity}%</b>\n'
                             f'Ветер: <b>{wind} м/с</b>\n'
                             f'<b>Хорошего дня!</b>')


async def send_weather_interval(bot: Bot):
    try:
        offset = 0
        result = await get_all_users(offset=offset)
        for i in result:
            async with aiohttp.ClientSession() as session:
                response = await session.get(
                    f'http://api.openweathermap.org/data/2.5/weather?lat={i[1]}'
                    f'&lon={i[2]}&lang=ru&units=metric&appid={API_KEY}'
                )
                data = await response.json()
                city = data['name']
                cur_temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                clouds = data['weather'][0].get('description')
                humidity = data["main"]["humidity"]
                wind = data["wind"]["speed"]
                await bot.send_message(i[0], f'Сегодня на улицах города <b>{city}</b>: \n'
                                                            f'Температура: <b>{cur_temp}°C</b>, ощущается как: '
                                                            f'<b>{feels_like}°C</b>,'
                                                            f'<b>{clouds}</b>\n'
                                                            f'Влажность воздуха: <b>{humidity}%</b>\n'
                                                            f'Ветер: <b>{wind} м/с</b>\n'
                                                            f'<b>Хорошего дня!</b>')
            offset += 1
    except Exception as e:
        logging.log(level=logging.ERROR, msg=e)


async def main():
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)

    scheduler = AsyncIOScheduler(timezone='Asia/Yekaterinburg')
    scheduler.add_job(send_weather_interval, trigger='interval',
                      seconds=7200, kwargs={'bot': bot})
    scheduler.start()

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s-%(asctime)s-%(message)s')
    asyncio.run(main())
