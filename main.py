import asyncio
import logging

from aiogram import Bot, Dispatcher, Router, F
from aiogram.enums import ParseMode, ContentType
from aiogram.filters import CommandStart
from aiogram.types import Message

from config import BOT_TOKEN, ADMIN_ID
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
    await message.answer(f'Ваша геопозиция: {message.location.latitude}, {message.location.longitude}')


async def main():
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    try:
        await dp.start_polling(bot, allowed_updates=[])
    finally:
        await bot.session.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(main())

