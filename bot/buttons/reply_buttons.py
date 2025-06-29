import json

import requests
from aiogram.types import ReplyKeyboardMarkup

from bot.buttons.text import adverts, none_advert, forward_advert, back_main_menu_ru, order, my_works, free_works


async def main_menu_buttons(chat_id: int):
    tg_user = json.loads(requests.get(url=f"http://127.0.0.1:8000/api/telegram-users/chat_id/{chat_id}/").content)
    if tg_user['is_courier']:
        design = [
            [my_works],
            [free_works]
        ]
    else:
        design = [
            [order]
        ]
    return ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)


async def back_main_menu_button():
    design = [[back_main_menu_ru]]
    return ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)


async def admin_menu_buttons():
    design = [
        [adverts],
        [back_main_menu_ru]
    ]
    return ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)


async def advert_menu_buttons():
    design = [
        [none_advert, forward_advert],
        [back_main_menu_ru]
    ]
    return ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)
