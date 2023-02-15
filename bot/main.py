from aiogram.utils import executor
import logging
from time import sleep
from dotenv import load_dotenv
import asyncio

from cfg.create_bot import dp
from functions.sql import Database
from functions.remember import scheduler_remember

from handlers.start import handlers_start
from handlers.export import handlers_export
from handlers.webapp import handlers_webapp

from filters.IsAdmin import filters_IsAdmin

# Логи
logging.basicConfig(level=logging.INFO)

# Коннект хендлеров
handlers_start(dp)
handlers_webapp(dp)
handlers_export(dp)
filters_IsAdmin(dp)


async def on_startup(_):
    load_dotenv()
    asyncio.create_task(scheduler_remember())

if __name__ == '__main__':
    while True:
        try:
            db = Database()
            with db.connection:
                db.create_user_data_table()
                db.create_class_attendance_table()

        except:
            sleep(5)
        else:
            break

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)