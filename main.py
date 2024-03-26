import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_TOKEN


bot = Bot(BOT_TOKEN)
dp = Dispatcher()


async def start():
    logging.basicConfig(level=logging.DEBUG)

    try:
        await dp.start_polling(bot, allowed_updates=[])
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())

