import os
import asyncio
import aioschedule as schedule
from datetime import datetime, timedelta

from .sql import Database
from cfg.create_bot import telegram_bot as bot


async def remember():
    time_now = datetime.now()
    db = Database()
    with db.connection:
        users = db.get_allow_blackmail()
        for item in users:
            user_presence = db.get_users_presences(item[0])
            
            if user_presence:
                if user_presence[-1][1] + timedelta(days=int(os.environ['days_delay'])) >= time_now:
                    continue

            text = f'Привет {item[1]}, если ты на уроке, отметь себя.'
            await bot.send_message(chat_id=item[0],text=text)
            await asyncio.sleep(1)


async def scheduler_remember():
    schedule.every().sunday.at("16:00").do(remember)
    # schedule.every().wednesday.at("21:27").do(remember)
    # schedule.every(1).minutes.do(remember)
    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)
