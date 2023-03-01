import os
import asyncio
# from aiogram.utils import exceptions
import aioschedule as schedule
from datetime import datetime, timedelta

from .sql import Database
from cfg.create_bot import telegram_bot as bot


async def check_in_reminder(msg=None):
    time_now = datetime.now()
    db = Database()
    text = 'Starting send blackmail ^__^'
    await bot.send_message('330663508', text)
    
    with db.connection:
        users = db.get_allow_blackmail()
        count = 0
        for item in users:
            user_presence = db.get_users_presences(item[0])
            
            if user_presence:
                if user_presence[-1][1] + timedelta(days=int(os.environ['days_delay'])) >= time_now:
                    continue

            text = f'Привет {item[1]}, если ты на уроке, отметь себя.'
            try:
                await bot.send_message(chat_id=item[0],text=text)
                count += 1
                await asyncio.sleep(1)
            except:
                pass
    
    text = f'Stopping send blackmail, successfully sent notifications - {count}'
    await bot.send_message('330663508', text)


async def scheduler_remember():
    """
    Creates scheduler
    """
    schedule.every().sunday.at("15:45").do(check_in_reminder)
    # schedule.every(8).seconds.do(check_in_reminder)
    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)