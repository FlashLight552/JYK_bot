from aiogram.utils import executor
import logging
from time import sleep

from cfg.create_bot import dp
from functions.sql import Database

from handlers.start import handlers_start
from handlers.webapp import handlers_webapp

# Логи
logging.basicConfig(level=logging.INFO)

# Коннект хендлеров
handlers_start(dp)
handlers_webapp(dp)

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
    executor.start_polling(dp, skip_updates=True)