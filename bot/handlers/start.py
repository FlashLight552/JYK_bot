import os

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import CommandStart
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types.web_app_info import WebAppInfo

from functions.sql import Database
from filters.IsAdmin import IsAdmin



weekdays_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
inline_cancel_btn = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Отмена', callback_data='cancel'))

class Form(StatesGroup):
    user_name = State()
    day = State()
    distance = State()
    custom_loc = State()


async def start(message: types.Message):
    db = Database()
    with db.connection:
        user_name = db.get_user_name(message.from_user.id)
        if user_name:
            text = f'Привет {user_name[0]}.\nОшибся с именем? Напиши мне /edit.\n\nВозникли технические проблемы? Пиши @ShtefanNein'
            return await message.answer(text)
    
    text =  'Привет, я JYK бот и я предназначен для того, чтоб отмечать присутствующих на нашей аниме сходке. '\
            'Напиши мне свое имя и фамилию и я добавлю тебя в список учеников.\n\n'\
            'Возникли технические проблемы? Пиши @ShtefanNein'
    
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
    await message.answer(text, reply_markup=inline_cancel_btn)
    await Form.user_name.set()


async def set_distance(message: types.Message):
    await message.answer('Введи радиус в метрах.', reply_markup=inline_cancel_btn)
    await Form.distance.set()


async def save_distance(message: types.Message, state: FSMContext):
    os.environ['distance'] = message.text
    await message.answer(f"Новый радиус - {os.environ['distance']}м")
    await state.finish()


async def current_distance(message: types.Message):
    await message.answer(f"Текущий радиус до точки урока - {os.environ['distance']}м")
    

async def error_distance(message: types.Message):
    await message.answer('Принимаю только цифры!!!')


async def set_day(message: types.Message):
    await message.answer('Введи день недели на английском. Я буду ждать, пока не введешь один из них - Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday', reply_markup=inline_cancel_btn)
    await Form.day.set()


async def save_day(message: types.Message, state: FSMContext):
    os.environ['day_of_week'] = message.text
    await message.answer(f"День урока - {os.environ['day_of_week']}")
    await state.finish()


async def error_day(message: types.Message):
    await message.answer('Введи день недели на английском!!!')


async def current_day(message:types.Message):
    await message.answer(f"Текущий день урока - {os.environ['day_of_week']}")


async def set_custom_point(massage: types.Message):
    await massage.answer('Пришли мне геолокацию, для создания нового места для урока.', reply_markup=inline_cancel_btn)
    await Form.custom_loc.set()


async def save_custom_point(message: types.Message, state: FSMContext):
    os.environ['custom_latitude'] = str(message.location.latitude)
    os.environ['custom_longitude'] = str(message.location.longitude)
    await message.answer(f"Записал новые координаты для урока.\nlat: {os.environ['custom_latitude']}\nlon: {os.environ['custom_longitude']}")
    await state.finish()


async def error_custom_point(message: types.Message):
    await message.answer('Пришли мне геолокацию!!!')
    

async def del_custom_point(message: types.Message):
    try:
        del os.environ['custom_latitude']
        del os.environ['custom_longitude'] 
        await message.answer('Пользовательская геолокация удалена, текущее место урока - синагога.')
    except: 
        await message.answer('Пользовательская геолокация не была установлена, текущее место урока - синагога.')


async def current_point(message: types.Message):
    try:
        if os.environ['custom_latitude']:
            await message.answer(f"Пользовательская геолокация:\nlat: {os.environ['custom_latitude']}\nlon: {os.environ['custom_longitude']}")
    except:
        await message.answer('Текущее место урока - синагога.')


async def cancel_handler(call: types.CallbackQuery, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.finish()
    await call.message.answer('Охрана отмена!')


async def my_id(message : types.Message):
    await message.answer(message.from_user.id)


async def admin_help(message: types.Message):
    text =  'ADMINS ONLY\n\n'\
            '/set_distance - изменение радиуса до места урока\n'\
            '/current_distance - текущий радиус до точки урока\n\n'\
            '/set_day - изменение дня урока\n'\
            '/current_day - текущий день урока\n\n'\
            '/set_custom_point - задать пользовательскою точку для урока\n'\
            '/delete_custom_point - Удаление пользовательской точки\n'\
            '/current_point - текущее заданное место урока\n\n'\
            '/all - статистика посещений за текущий месяц.\n'\
            '/all мм гггг - статистика посещений за заданий месяц и год.\n'
    await message.answer(text)

async def user_help(message: types.Message):
    text =  'Команды для пользователей\n\n'\
            '/edit - изменение имени\n'\
            '/stats - статистика посещений за текущий месяц\n'\

    await message.answer(text)


def handlers_start(dp: Dispatcher):
    dp.register_message_handler(start, CommandStart())
    dp.register_message_handler(save_name, state=Form.user_name)
    dp.register_message_handler(edit_name, commands={'edit'})
    dp.register_message_handler(my_id, commands=['id'])
    dp.register_message_handler(admin_help, IsAdmin(),commands=['adm_help'])
    dp.register_message_handler(user_help, commands=['help'])

    dp.register_callback_query_handler(cancel_handler, text='cancel', state='*')

    dp.register_message_handler(set_distance, IsAdmin(), commands={'set_distance'})
    dp.register_message_handler(error_distance, lambda message: not message.text.isdigit(), state=Form.distance)
    dp.register_message_handler(save_distance, lambda message: message.text.isdigit(), state=Form.distance)
    dp.register_message_handler(current_distance, IsAdmin(), commands=['current_distance'])

    dp.register_message_handler(set_day, IsAdmin(), commands={'set_day'})
    dp.register_message_handler(error_day, lambda message: message.text not in weekdays_name, state=Form.day)
    dp.register_message_handler(save_day, lambda message: message.text in weekdays_name, state=Form.day)
    dp.register_message_handler(current_day, IsAdmin(), commands=['current_day'])

    dp.register_message_handler(set_custom_point, IsAdmin(), commands={'set_custom_point'})
    dp.register_message_handler(save_custom_point, state=Form.custom_loc, content_types=['location'])
    dp.register_message_handler(error_custom_point, lambda message: message.content_type != 'location', state=Form.custom_loc)
    dp.register_message_handler(del_custom_point, IsAdmin(), commands=['delete_custom_point'])
    dp.register_message_handler(current_point, IsAdmin(), commands=['current_point'])