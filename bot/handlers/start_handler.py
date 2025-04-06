import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, Text

from bot.buttons.reply_buttons import main_menu_buttons
from bot.buttons.text import back_main_menu_ru
from bot.dispatcher import dp


@dp.message_handler(Text(back_main_menu_ru), state='*')
async def back_main_menu_function_1(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer(text=msg.text, reply_markup=await main_menu_buttons(msg.from_user.id))


@dp.callback_query_handler(Text(back_main_menu_ru), state='*')
async def back_main_menu_function_1(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.delete()
    await call.message.answer(text=call.data, reply_markup=await main_menu_buttons(call.from_user.id))


@dp.message_handler(CommandStart())
async def start_handler(msg: types.Message):
    data = {
        "chat_id": str(msg.from_user.id),
        "username": msg.from_user.username,
        "full_name": msg.from_user.full_name,
    }
    requests.post(url="http://127.0.0.1:8005/api/telegram-users/create/", data=data)
    await msg.answer(text="👋 Привет! Добро пожаловать в наш бот. \n\n✅ Выберите одну из следующих услуг:",
                     reply_markup=await main_menu_buttons(msg.from_user.id))
