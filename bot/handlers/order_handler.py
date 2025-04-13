import json
import os

import aiohttp
import requests
from geopy.distance import geodesic
from aiogram import types
from aiogram.types import ContentType, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.buttons.reply_buttons import main_menu_buttons
from bot.buttons.text import order
from bot.dispatcher import dp, Config, bot
from aiogram.dispatcher.filters import Text

API_URL = "http://127.0.0.1:8005/api/orders/orders/"

SAVE_PATH = "images/order_images/"

os.makedirs(SAVE_PATH, exist_ok=True)


class OrderState(StatesGroup):
    pickup_location = State()
    delivery_location = State()
    product_price = State()
    delivery_price = State()
    delivery_payer = State()
    product_payer = State()
    product_photo = State()
    pickup_comment = State()
    delivery_comment = State()
    confirm = State()


cancel_button = KeyboardButton("❌ Отменить")
skip_button = KeyboardButton("⏭ Пропустить")


@dp.message_handler(Text(order))
async def start_order(msg: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("📍 Отправить местоположение", request_location=True)], [cancel_button]],
        resize_keyboard=True
    )
    await msg.answer("📍 Отправьте местоположение A (откуда забрать товар)", reply_markup=keyboard)
    await OrderState.pickup_location.set()


@dp.message_handler(Text("❌ Отменить"), state='*')
async def cancel_order(msg: types.Message, state: FSMContext):
    await state.finish()
    await msg.answer("🚫 Заказ отменен.", reply_markup=await main_menu_buttons(msg.from_user.id))


@dp.message_handler(state=OrderState.pickup_location, content_types=ContentType.LOCATION)
async def set_pickup_location(msg: types.Message, state: FSMContext):
    await state.update_data(
        pickup_latitude=msg.location.latitude,
        pickup_longitude=msg.location.longitude
    )
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("📍 Отправить местоположение", request_location=True)], [cancel_button]],
        resize_keyboard=True
    )
    await msg.answer("📍 Отправьте местоположение B (куда доставить товар)", reply_markup=keyboard)
    await OrderState.delivery_location.set()


@dp.message_handler(state=OrderState.delivery_location, content_types=ContentType.LOCATION)
async def set_delivery_location(msg: types.Message, state: FSMContext):
    await state.update_data(
        delivery_latitude=msg.location.latitude,
        delivery_longitude=msg.location.longitude
    )
    await msg.answer("💰 Введите сумму товара", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[cancel_button]], resize_keyboard=True
    ))
    await OrderState.product_price.set()


@dp.message_handler(state=OrderState.product_price, content_types=ContentType.TEXT)
async def set_product_price(msg: types.Message, state: FSMContext):
    await state.update_data(product_price=msg.text)
    await msg.answer("💰 Введите сумму доставки", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[cancel_button]], resize_keyboard=True
    ))
    await OrderState.delivery_price.set()


@dp.message_handler(state=OrderState.delivery_price, content_types=ContentType.TEXT)
async def set_delivery_price(msg: types.Message, state: FSMContext):
    await state.update_data(delivery_price=msg.text)
    await msg.answer("👤 Кто оплачивает доставку? (Клиент / Заказчик)", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("Клиент"), KeyboardButton("Заказчик")], [cancel_button]], resize_keyboard=True
    ))
    await OrderState.delivery_payer.set()


@dp.message_handler(state=OrderState.pickup_comment, content_types=ContentType.TEXT)
async def set_pickup_comment(msg: types.Message, state: FSMContext):
    if msg.text != "⏭ Пропустить":
        await state.update_data(pickup_comment=msg.text)
    else:
        await state.update_data(pickup_comment="")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[skip_button], [cancel_button]], resize_keyboard=True
    )
    await msg.answer("✏ Напишите комментарий к точке B (куда доставить товар) или нажмите ⏭ Пропустить.",
                     reply_markup=keyboard)
    await OrderState.delivery_comment.set()


@dp.message_handler(state=OrderState.delivery_comment, content_types=ContentType.TEXT)
async def set_delivery_comment(msg: types.Message, state: FSMContext):
    if msg.text != "⏭ Пропустить":
        await state.update_data(delivery_comment=msg.text)
    else:
        await state.update_data(delivery_comment="")

    await msg.answer("📸 Отправьте фото товара", reply_markup=ReplyKeyboardRemove())
    await OrderState.product_photo.set()


async def get_location_name(lat, lon):
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("display_name", "Noma'lum joy")
    return "Xatolik yuz berdi!"


def calculate_distance(lat1, lon1, lat2, lon2):
    return round(geodesic((lat1, lon1), (lat2, lon2)).km, 2)


def google_maps_directions_link(lat1, lon1, lat2, lon2):
    return f"https://www.google.com/maps/dir/?api=1&origin={lat1},{lon1}&destination={lat2},{lon2}"


@dp.message_handler(state=OrderState.product_photo, content_types=types.ContentType.PHOTO)
async def set_product_photo(msg: types.Message, state: FSMContext):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"http://127.0.0.1:8005/api/telegram-users/chat_id/{msg.from_user.id}/") as resp:
                if resp.status != 200:
                    await msg.answer("❌ Ошибка при получении данных пользователя!")
                    return
                tg_user = await resp.json()
                user_id = tg_user.get("id")

            photo_id = msg.photo[-1].file_id
            file_info = await msg.bot.get_file(photo_id)
            file_path = file_info.file_path
            photo_url = f"https://api.telegram.org/file/bot{Config.BOT_TOKEN}/{file_path}"

            async with session.get(photo_url) as photo_resp:
                if photo_resp.status != 200:
                    await msg.answer("❌ Ошибка при загрузке изображения с сервера Telegram!")
                    return
                image_bytes = await photo_resp.read()

            filename = f"{msg.from_user.id}_{photo_id}.jpg"
            saved_path = os.path.join("images", filename)

            with open(saved_path, "wb") as f:
                f.write(image_bytes)

            data = await state.get_data()

            pickup_lat = float(data.get('pickup_latitude', 0))
            pickup_lon = float(data.get('pickup_longitude', 0))
            delivery_lat = float(data.get('delivery_latitude', 0))
            delivery_lon = float(data.get('delivery_longitude', 0))

            pickup_address = await get_location_name(pickup_lat, pickup_lon)
            delivery_address = await get_location_name(delivery_lat, delivery_lon)

            distance_km = calculate_distance(pickup_lat, pickup_lon, delivery_lat, delivery_lon)

            directions_link = google_maps_directions_link(pickup_lat, pickup_lon, delivery_lat, delivery_lon)

            order_data = {
                "user": str(user_id),
                "pickup_latitude": str(pickup_lat),
                "pickup_longitude": str(pickup_lon),
                "pickup_address": pickup_address,
                "delivery_latitude": str(delivery_lat),
                "delivery_longitude": str(delivery_lon),
                "delivery_address": delivery_address,
                "distance_km": str(distance_km),
                "order_price": str(data.get('product_price', 0)),
                "delivery_price": str(data.get('delivery_price', 0)),
                "deliver_payment_by": "user" if data.get('delivery_payer') == "клиент" else "customer",
                "payment_by": "user" if data.get('product_payer') == "клиент" else "courier",
                "pickup_comment": data.get('pickup_comment', ""),
                "delivery_comment": data.get('delivery_comment', ""),
                "image": saved_path,
                "map": directions_link
            }

            async with session.post("http://127.0.0.1:8005/api/orders/orders/", json=order_data) as api_resp:
                if api_resp.status == 201:
                    response_data = await api_resp.json()
                    order_id = response_data.get("id")
                    await msg.answer(text="✅ *Ваш заказ успешно создан!*",
                                     reply_markup=await main_menu_buttons(msg.from_user.id), parse_mode="Markdown")
                    order_summary = (
                        f"📍 *Откуда:* {pickup_address}\n"
                        f"📍 *Куда:* {delivery_address}\n"
                        f"🛤 *Расстояние:* {distance_km} км\n"
                        f"💰 *Цена товара:* {data.get('product_price', 0)} сум\n"
                        f"🚚 *Цена доставки:* {data.get('delivery_price', 0)} сум\n"
                        f"💳 *Оплата товара:* {data.get('product_payer')}\n"
                        f"💳 *Оплата доставки:* {data.get('delivery_payer')}\n"
                        f"📝 *Комментарий к забору:* {data.get('pickup_comment', 'Нет')}\n"
                        f"📝 *Комментарий к доставке:* {data.get('delivery_comment', 'Нет')}\n"
                        f"📞 *Контакт:* {tg_user['phone_number']}"
                        f"📸 *Фото товара:*\n\n"
                        f"🗺 *Посмотреть маршрут:* [Google Maps]({directions_link})"
                    )
                    cancel_button = InlineKeyboardMarkup().add(
                        InlineKeyboardButton("❌ Отменить заказ", callback_data=f"cancel_order_{order_id}")
                    )
                    accept_button = InlineKeyboardMarkup().add(
                        InlineKeyboardButton("✅  Принятие", callback_data=f"accept_order_{order_id}")
                    )
                    await msg.answer_photo(photo=photo_id, caption=order_summary, parse_mode="Markdown",
                                           reply_markup=cancel_button)

                    couriers = json.loads(
                        requests.get(url=f"http://127.0.0.1:8005/api/telegram-users/couriers/").content)['results']
                    for courier in couriers:
                        if courier['is_available']:
                            await bot.send_photo(chat_id=courier['chat_id'], photo=photo_id, caption=order_summary,
                                                 parse_mode="Markdown",
                                                 reply_markup=accept_button)
                else:
                    await msg.answer(f"❌ Ошибка при создании заказа! {await api_resp.text()}",
                                     reply_markup=await main_menu_buttons(msg.from_user.id))

    except Exception as e:
        await msg.answer(f"❌ Ошибка при создании заказа!\n{str(e)}",
                         reply_markup=await main_menu_buttons(msg.from_user.id))

    await state.finish()


@dp.callback_query_handler(lambda call: call.data.startswith("cancel_order_"))
async def cancel_order(call: types.CallbackQuery):
    order_id = call.data.split("_")[-1]

    async with aiohttp.ClientSession() as session:
        async with session.post(f"http://127.0.0.1:8005/api/orders/orders/{order_id}/cancel/") as resp:
            if resp.status == 200:
                await call.message.delete()
                await call.message.answer("❌ Ваш заказ был отменён!",
                                                reply_markup=await main_menu_buttons(call.from_user.id))
            else:
                await call.message.answer("⚠ Не удалось отменить заказ!",
                                          reply_markup=await main_menu_buttons(call.from_user.id))


@dp.message_handler(state=OrderState.delivery_payer, content_types=ContentType.TEXT)
async def set_delivery_payer(msg: types.Message, state: FSMContext):
    if msg.text.lower() not in ["клиент", "заказчик"]:
        await msg.answer("❌ Пожалуйста, выберите: Клиент или Заказчик")
        return
    await state.update_data(delivery_payer=msg.text.lower())
    await msg.answer("👤 Кто оплачивает товар? (Клиент / Курьер)", reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("Клиент"), KeyboardButton("Курьер")], [cancel_button]],
        resize_keyboard=True
    ))
    await OrderState.product_payer.set()


@dp.message_handler(state=OrderState.product_payer, content_types=ContentType.TEXT)
async def set_product_payer(msg: types.Message, state: FSMContext):
    if msg.text.lower() not in ["клиент", "курьер"]:
        await msg.answer("❌ Пожалуйста, выберите: Клиент или Курьер")
        return
    await state.update_data(product_payer=msg.text.lower())

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton("⏭ Пропустить")], [cancel_button]], resize_keyboard=True
    )
    await msg.answer("✏ Напишите комментарий к точке A (откуда забрать товар) или нажмите ⏭ Пропустить.",
                     reply_markup=keyboard)
    await OrderState.pickup_comment.set()
