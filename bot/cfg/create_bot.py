from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.files import JSONStorage
from pathlib import Path
import os

from dotenv import load_dotenv
load_dotenv()

telegram_bot = Bot(token=os.environ["TELEGRAM_TOKEN"])
storage = JSONStorage(Path.cwd() / "cfg/fsm_data.json")
dp = Dispatcher(telegram_bot, storage=storage)