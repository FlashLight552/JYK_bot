import os

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.web_app_info import WebAppInfo

from functions.sql import Database


class Form(StatesGroup):
    user_name = State()


async def start(message: types.Message):
    db = Database()
    with db.connection:
        user_name = db.get_user_name(message.from_user.id)
        if user_name:
            text = f'Привет {user_name[0]}.\nОшибся с именем? Напиши мне /edit.'
            return await message.answer(text)
    
    text = 'Привет, я JYK бот и я предназначен для того, чтоб отмечать присутствующих на нашей аниме сходке. '\
            'Напиши мне свое имя и фамилию и я добавлю тебя в список учеников.\n'\
            'Ошибся с именем? Напиши мне /edit.'
    
    await message.answer(text)
    await Form.user_name.set()


async def save_name(message: types.Message, state: FSMContext):
    location_btn = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text='Определить геолокацию',
                                                            web_app=WebAppInfo(url=os.environ['webapp_path'])))
    await state.finish()
    
    text = f'Твое имя - {message.text}, я запомнил)'
    await message.answer(text, 
                        reply_markup=location_btn)

    db = Database()
    with db.connection:
        db.add_user_name(message.from_user.id, message.text)


async def edit_name(message: types.Message):
    text = 'Напиши мне своё новое имя.'
    await message.answer(text)
    await Form.user_name.set()


def handlers_start(dp: Dispatcher):
    dp.register_message_handler(start, CommandStart())
    dp.register_message_handler(save_name, state=Form.user_name)
    dp.register_message_handler(edit_name, commands={'edit'})