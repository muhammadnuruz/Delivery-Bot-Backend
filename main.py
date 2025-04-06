import logging
import asyncio
from courier_handlers import *
from aiogram import executor
from bot.handlers import *

admins = [1974800905]

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    executor.start_polling(dp, skip_updates=True)
