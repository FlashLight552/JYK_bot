from aiogram import types, Dispatcher
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import os
import pandas as pd
from haversine import haversine
from datetime import datetime, timedelta

from functions.sql import Database


async def web_app_msg(message: types.Message):
    await message.delete()

    lat, lon = message.web_app_data.data.split(':')
    distance = await check_distance(lat, lon)

    if float(distance) >= float(os.environ['distance']):
        return await message.answer(f'Ты не в зоне синагоги {distance}м до неё')

    db = Database()
    with db.connection:
        user_id = int(message.from_user.id)
        user_presence = db.get_users_presences(user_id)
        time_now = datetime.now()
        
        if user_presence:
            if time_now.today().strftime("%A") != os.environ['day_of_weekay']:
                return await message.answer(f'Приходи ко мне в воскресенье.')
            if user_presence[-1][1] + timedelta(days=int(os.environ['days_delay'])) >= time_now:
                return await message.answer(f'Ты уже отметился, хватит!')
    
    inline_kb = InlineKeyboardMarkup().add(
        InlineKeyboardButton('Да', callback_data='ask_about_shabbat-yes'),
        InlineKeyboardButton('Нет', callback_data='ask_about_shabbat-no')
    )

    await message.answer('Были ли вы на шаббате?', reply_markup=inline_kb)


async def ask_about_shabbat(call: types.CallbackQuery):
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

async def get_all_users_presences(message: types.Message, mounth:int=None, year:int=None) -> types.Message:
    try:    
        mounth, year = (message.text.split(' ')[1:3])
    except:
        year, mounth = str(datetime.today().strftime("%Y-%m")).split('-')

    db = Database()
    with db.connection:
        user_presence = db.get_users_presences(mounth=mounth,year=year)
        all_users = []
        all_date = []

        for item in user_presence:
            user_name = item[3]
            date = item[1].strftime("%d/%m/%Y")
            if not user_name in all_users:
                all_users.append(user_name)
            if not date in all_date:
                all_date.append(f'{date}_shabbat')
                all_date.append(date)

        df = pd.DataFrame({}, columns=all_date, index=all_users)
        for item in user_presence:
            user_name = item[3]
            date = item[1].strftime("%d/%m/%Y")
            shabbat_presence = item[2]

            df.at[user_name, date] = 1
            df.at[user_name, (f'{date}_shabbat')] = shabbat_presence

        
        df = df.fillna(0)
        filename = f'./{mounth}-{year}-export.xlsx'
        df.to_excel(filename)
        
        doc = open(filename, 'rb')
        await message.answer_document(doc)

        os.remove(filename)


async def check_distance(lat, lon):
    syn_lat = os.environ['synagogue_latitude']
    syn_lon = os.environ['synagogue_longitude']
    distance = haversine((float(lat), float(lon)), (float(syn_lat), float(syn_lon)))
    return (f"{distance * 1000:.{0}f}")


def handlers_webapp(dp: Dispatcher):
    dp.register_message_handler(web_app_msg, content_types='web_app_data')
    dp.register_message_handler(get_all_users_presences, commands={'all'})
    
    dp.register_callback_query_handler(ask_about_shabbat, text=['ask_about_shabbat-yes', 'ask_about_shabbat-no'])