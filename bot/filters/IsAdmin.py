from aiogram.dispatcher.filters import BoundFilter
from aiogram import types, Dispatcher

from aiogram import types
import os

admins = list(os.environ['owner'].replace('[','').replace(']','').split(','))

class IsAdmin(BoundFilter):
    key = "is_admin"
    async def check(self, message: types.Message):
        return str(message.from_user.id) in admins


def filters_IsAdmin(dp: Dispatcher):
    dp.filters_factory.bind(IsAdmin)