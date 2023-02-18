import os
from haversine import haversine
from datetime import datetime, timedelta

from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from functions.sql import Database

weekdays_name = {'Monday':'в понедельник', 'Tuesday':'во вторник', 'Wednesday':'в среду', 'Thursday':'в четверг', 'Friday':'в пятницу', 'Saturday':'в субботу', 'Sunday':'в воскресенье'}


async def web_app_msg(message: types.Message)-> types.Message:
    await message.delete()
    lat, lon = message.web_app_data.data.split(':')
    distance = await check_distance(lat, lon)

    if float(distance) >= float(os.environ['distance']):
        return await message.answer(f'Ты не в зоне нашего места урока {distance}м до него')

    db = Database()
    with db.connection:
        user_id = int(message.from_user.id)
        user_presence = db.get_users_presences(user_id)
        time_now = datetime.now()
        

        if user_presence:
            if time_now.today().strftime("%A").lower() != os.environ['day_of_week'].lower():
                return await message.answer(f"Приходи ко мне {weekdays_name[os.environ['day_of_week']]}.")
            if user_presence[-1][1] + timedelta(days=int(os.environ['days_delay'])) >= time_now:
                return await message.answer(f'Ты уже отметился, хватит!')
    
    inline_kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton('Да', callback_data='ask_about_shabbat-yes'),
        InlineKeyboardButton('Нет', callback_data='ask_about_shabbat-no')
    )

    await message.answer('Был ли ты на шаббате?', reply_markup=inline_kb)


async def ask_about_shabbat(call: types.CallbackQuery)-> types.Message:
    await call.message.delete()
    answer = (call.data.split('-')[1])
    shabbat = False
    if answer == 'yes':
        shabbat = True
    
    db = Database()
    with db.connection:
        db.add_user_presence(call.from_user.id, shabbat=shabbat)
        # user_presence = db.get_users_presences(call.from_user.id)[-1]
    
    # await call.message.answer(f'{user_presence[3]}\n{user_presence[1].strftime("%m/%d/%Y, %H:%M:%S")}\nShabbat - {shabbat}\nAdd to db - ok')
    await call.message.answer(f'Всё отлично, я отметил.')


async def check_distance(lat:str, lon:str)->str:
    """Used for measure distance between two points"""
    try:
        point_lat = os.environ['custom_latitude']
        point_lon = os.environ['custom_longitude']
    except:
        point_lat = os.environ['synagogue_latitude']
        point_lon = os.environ['synagogue_longitude']
        
    distance = haversine((float(lat), float(lon)), (float(point_lat), float(point_lon)))
    return (f"{distance * 1000:.{0}f}")


def handlers_webapp(dp: Dispatcher):
    dp.register_message_handler(web_app_msg, content_types='web_app_data')
    dp.register_callback_query_handler(ask_about_shabbat, regexp='(ask_about_shabbat-)')