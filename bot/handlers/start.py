from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.web_app_info import WebAppInfo

from functions.sql import Database
import os

class Form(StatesGroup):
    user_name = State()


async def start(message: types.Message):
    db = Database()
    with db.connection:
        user_name = db.get_user_name(message.from_user.id)
        if user_name:
            text = f'welcome text and your name is {user_name[0]}'
            return await message.answer(text)
    
    text = 'Write your name'
    await message.answer(text)
    await Form.user_name.set()


async def save_name(message: types.Message, state: FSMContext):
    location_btn = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text='Определить геолокацию',
                                                            web_app=WebAppInfo(url=os.environ['webapp_path'])))
    await state.finish() 
    
    text = f'Your name is {message.text}'
    await message.answer(text, 
                        reply_markup=location_btn)

    db = Database()
    with db.connection:
        db.add_user_name(message.from_user.id, message.text)


async def edit_name(message: types.Message):
    text = 'Write your name'
    await message.answer(text)
    await Form.user_name.set()


def handlers_start(dp: Dispatcher):
    dp.register_message_handler(start, CommandStart())
    dp.register_message_handler(save_name, state=Form.user_name)

    dp.register_message_handler(edit_name, commands={'edit_name'})