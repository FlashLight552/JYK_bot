import os
import asyncio
from aiogram.utils import exceptions
import aioschedule as schedule
from datetime import datetime, timedelta

from .sql import Database
from cfg.create_bot import telegram_bot as bot


async def check_in_reminder():
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
            
            try:
                await send_message(user_id=item[0],text=text)
                await asyncio.sleep(1)
            finally:
                pass


async def send_message(user_id: int, text: str, disable_notification: bool = False) -> bool:
    """
    Safe messages sender

    :param user_id:
    :param text:
    :param disable_notification:
    :return:
    """
    try:
        await bot.send_message(user_id, text, disable_notification=disable_notification)
    except exceptions.BotBlocked:
        print(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.ChatNotFound:
        print(f"Target [ID:{user_id}]: invalid user ID")
    except exceptions.RetryAfter as e:
        print(f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds.")
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        print(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        print(f"Target [ID:{user_id}]: failed")
    else:
        print(f"Target [ID:{user_id}]: success")
        return True
    return False


async def scheduler_remember():
    """
    Creates scheduler
    """
    schedule.every().sunday.at("16:00").do(check_in_reminder)
    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)