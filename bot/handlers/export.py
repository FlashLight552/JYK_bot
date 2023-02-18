import os
import pandas as pd
from datetime import datetime

from aiogram import types, Dispatcher
from functions.sql import Database
from filters.IsAdmin import IsAdmin


async def get_all_users_presences(message: types.Message) -> types.Message:
    try:
        mounth, year = (message.text.split(' ')[1:3])
    except:
        year, mounth = str(datetime.today().strftime("%Y-%m")).split('-')

    db = Database()
    with db.connection:
        user_presence = db.get_users_presences(mounth=mounth,year=year)
        filename = await create_exel_export(user_presence, mounth, year, message.from_user.id)

        doc = open(filename, 'rb')
        await message.answer_document(doc)
        os.remove(filename)


async def get_user_presences(message: types.Message) -> types.Message:
    year, mounth = str(datetime.today().strftime("%Y-%m")).split('-')
    db = Database()
    with db.connection:
        user_presence = db.get_users_presences(message.from_user.id)
        filename = await create_exel_export(user_presence, mounth, year, message.from_user.id)

        doc = open(filename, 'rb')
        await message.answer_document(doc)
        
        os.remove(filename)
        os.environ['owner']


async def create_exel_export(user_presence:list, mounth:str, year:str, user_id:str) ->str:
        """Creates an Excel file with user visits. Returns the filename."""
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
        filename = f'./{user_id}__{mounth}-{year}-export.xlsx'
        writer = pd.ExcelWriter(filename)
        df.to_excel(writer, sheet_name='My_stats')

        for column in df:
            col_idx = df.columns.get_loc(column)
            writer.sheets['My_stats'].set_column(col_idx+1, col_idx, 25)

        writer.close()
        return filename


def handlers_export(dp: Dispatcher):
    dp.register_message_handler(get_all_users_presences, IsAdmin(), commands=['all'])
    dp.register_message_handler(get_user_presences, commands=['stats'])
    
