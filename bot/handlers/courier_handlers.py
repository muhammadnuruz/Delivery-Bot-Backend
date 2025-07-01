import json

import aiohttp
import requests
from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from bot.buttons.reply_buttons import main_menu_buttons
from bot.buttons.text import my_works, free_works
from bot.dispatcher import dp, bot
import os


@dp.message_handler(text=my_works)
async def show_my_orders_filter(message: types.Message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("📅 Сегодня", callback_data="orders_filter:today"),
        InlineKeyboardButton("🗓 Последние 7 дней", callback_data="orders_filter:week"),
        InlineKeyboardButton("📆 Последние 30 дней", callback_data="orders_filter:month"),
        InlineKeyboardButton("🔄 Все заказы", callback_data="orders_filter:all"),
    )
    await message.answer("Выберите период для отображения заказов:", reply_markup=markup)


@dp.callback_query_handler(lambda c: c.data.startswith("orders_filter:"))
async def filter_orders_callback(callback_query: types.CallbackQuery):
    period = callback_query.data.split(":")[1]
    chat_id = callback_query.from_user.id

    url = f'http://127.0.0.1:8005/api/orders/courier/orders/?chat_id={chat_id}&period={period}'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                orders = await response.json()
                if orders['count'] > 0:
                    for order in orders['results']:
                        status_map = {
                            "pending": "Ожидает",
                            "in_progress": "В процессе",
                            "delivered": "Доставлено",
                            "cancelled": "Отменено",
                        }
                        status_text = status_map.get(order['status'], "Неизвестно")

                        payment_by_text = (
                            "Платеж от пользователя" if order['payment_by'] == 'user'
                            else "Платеж курьером"
                        )
                        deliver_payment_by_text = (
                            "Платеж за доставку от пользователя" if order['deliver_payment_by'] == 'user'
                            else "Платеж за доставку от заказчика"
                        )
                        user = json.loads(
                            requests.get(
                                url=f"http://127.0.0.1:8005/api/telegram-users/detail/{order['user']}").content)
                        order_text = (
                            f"**Ваш заказ #{order['id']}**\n"
                            f"📍 *Откуда:* {order['pickup_address']}\n"
                            f"📍 *Куда:* {order['delivery_address']}\n"
                            f"🛤 *Приблизительно км::* {order['distance_km']} км\n"
                            f"💰 *Цена товара:* {order['order_price']} сум\n"
                            f"🚚 *Цена доставки:* {order['delivery_price']} сум\n"
                            f"📝 *Комментарий по сбору:* {order['pickup_comment'] or 'Нет комментариев'}\n"
                            f"📝 *Комментарий по доставке:* {order['delivery_comment'] or 'Нет комментариев'}\n"
                            f"📸 *Фото заказа:*\n"
                            f"🗺 *Посмотреть маршрут:* [Google Maps]({order['map']})\n"
                            f"📞 *Контакт:* {user['phone_number']}\n"
                            f"📑 *Статус:* {status_text}\n"
                            f"💳 *Оплата товара:* {payment_by_text}\n"
                            f"💳 *Оплата доставки:* {deliver_payment_by_text}\n\n"
                        )

                        base_dir = os.path.dirname(os.path.abspath(__file__))
                        photo_url = os.path.join(base_dir, 'images', order['image'][7:])
                        try:
                            with open(photo_url, 'rb') as photo_file:
                                await bot.send_photo(callback_query.from_user.id, photo=photo_file,
                                                     caption=order_text, parse_mode="Markdown")
                        except FileNotFoundError:
                            await bot.send_message(callback_query.from_user.id,
                                                   f"Не удалось найти изображение для заказа #{order['id']}")
                else:
                    await callback_query.message.answer("У вас нет заказов за выбранный период.")
            else:
                await callback_query.message.answer("Произошла ошибка при получении заказов.")

    await callback_query.answer()


@dp.message_handler(text=free_works)
async def free_works_filter(msg: types.Message):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://127.0.0.1:8005/api/orders/orders/?status=pending") as resp:
                if resp.status != 200:
                    await msg.answer("❌ Ошибка при получении заказов!")
                    return
                orders = await resp.json()

            if not orders:
                await msg.answer("📭 Пока нет доступных заказов.")
                return

            for order in orders['results']:
                user = json.loads(
                    requests.get(url=f"http://127.0.0.1:8005/api/telegram-users/detail/{order['user']}").content)
                caption = (
                    f"📍 *Откуда:* {order['pickup_address']}\n"
                    f"📍 *Куда:* {order['delivery_address']}\n"
                    f"🛤 *Приблизительно км::* {order['distance_km']} км\n"
                    f"💰 *Цена товара:* {order['order_price']} сум\n"
                    f"🚚 *Цена доставки:* {order['delivery_price']} сум\n"
                    f"💳 *Оплата товара:* {order['payment_by']}\n"
                    f"💳 *Оплата доставки:* {order['deliver_payment_by']}\n"
                    f"📝 *Комментарий к забору:* {order['pickup_comment']}\n"
                    f"📝 *Комментарий к доставке:* {order['delivery_comment']}\n"
                    f"📞 *Контакт:* {user['phone_number']}\n"
                    f"📸 *Фото товара:*\n\n"
                    f"🗺 *Посмотреть маршрут:* [Google Maps]({order['map']})"
                )

                accept_button = InlineKeyboardMarkup().add(
                    InlineKeyboardButton("✅ Принять заказ", callback_data=f"accept_order_{order['id']}")
                )
                base_dir = os.path.dirname(os.path.abspath(__file__))
                photo_url = os.path.join(base_dir, 'images', order['image'][7:])
                with open(photo_url, 'rb') as photo_file:
                    await msg.answer_photo(photo=photo_file, caption=caption,
                                         parse_mode="Markdown",
                                         reply_markup=accept_button)

    except Exception as e:
        await msg.answer(f"❌ Произошла ошибка:\n{str(e)}")


@dp.callback_query_handler(lambda call: call.data.startswith("accept_order_"))
async def accept_order(call: types.CallbackQuery):
    order_id = call.data.split("_")[-1]

    try:
        response = requests.get(f"http://127.0.0.1:8005/api/orders/orders/{order_id}/")
        if response.status_code != 200:
            raise Exception("Buyurtma topilmadi.")

        order = response.json()

        if order['status'] == 'pending':
            accept_button = InlineKeyboardMarkup().add(
                InlineKeyboardButton("❌ Отменить заказ", callback_data=f"cancel_courier_{order_id}"),
                InlineKeyboardButton("✅ Доставлен", callback_data=f"done_courier_{order_id}")
            )

            await call.message.reply(
                f"✅ Заказ #{order_id} успешно принят!\n📦 Статус: В процессе доставки.",
                reply_markup=accept_button
            )
            user_response = requests.get(f"http://127.0.0.1:8005/api/telegram-users/chat_id/{call.from_user.id}/")
            if user_response.status_code != 200:
                raise Exception("Kuryer topilmadi.")

            tg_user = user_response.json()

            s_data = {
                "status": "in_progress",
                "courier": tg_user['id']
            }

            new_order = json.loads(
                requests.patch(url=f"http://127.0.0.1:8005/api/orders/update/{order_id}/", json=s_data).content)
            user = json.loads(
                requests.get(url=f"http://127.0.0.1:8005/api/telegram-users/detail/{new_order['user']}").content)
            courier_name = tg_user.get('full_name', 'Без имени')
            courier_username = tg_user.get('username')
            courier_contact = f"@{courier_username}" if courier_username else "Username недоступен"
            await bot.send_message(
                chat_id=user['chat_id'],
                text=f"""📦 Ваш заказ был принят!
                
🚶 Курьер: {courier_name}
🔗 Связаться: {courier_contact}
📲 Номер телефона: {tg_user['phone_number']}
⏳ Ожидайте доставку. Спасибо, что выбрали нас!"""
            )
        else:
            await call.message.delete()
            await call.message.answer(
                "❌ Заказ уже был принят другим курьером или отменён.",
                reply_markup=await main_menu_buttons(call.from_user.id)
            )

    except Exception as e:
        await call.message.answer(
            f"⚠ Xatolik: {e}",
            reply_markup=await main_menu_buttons(call.from_user.id)
        )


@dp.callback_query_handler(lambda call: call.data.startswith("cancel_courier_"))
async def cancel_order(call: types.CallbackQuery):
    try:
        order_id = call.data.split("_")[-1]
        s_data = {
            "status": "pending",
            "courier": None
        }
        new_order = json.loads(
            requests.patch(url=f"http://127.0.0.1:8005/api/orders/update/{order_id}/", json=s_data).content)
        user = json.loads(
            requests.get(url=f"http://127.0.0.1:8005/api/telegram-users/detail/{new_order['user']}").content)
        order_summary = (
            f"📍 *Откуда:* {new_order['pickup_address']}\n"
            f"📍 *Куда:* {new_order['delivery_address']}\n"
            f"🛤 *Приблизительно км::* {new_order['distance_km']} км\n"
            f"💰 *Цена товара:* {new_order['order_price']} сум\n"
            f"🚚 *Цена доставки:* {new_order['delivery_price']} сум\n"
            f"💳 *Оплата товара:* {new_order['payment_by']}\n"
            f"💳 *Оплата доставки:* {new_order['deliver_payment_by']}\n"
            f"📝 *Комментарий к забору:* {new_order['pickup_comment']}\n"
            f"📝 *Комментарий к доставке:* {new_order['delivery_comment']}\n"
            f"📞 *Контакт:* {user['phone_number']}\n"
            f"📸 *Фото товара:*\n\n"
            f"🗺 *Посмотреть маршрут:* [Google Maps]({new_order['map']})"
        )
        accept_button = InlineKeyboardMarkup().add(
            InlineKeyboardButton("✅  Принятие", callback_data=f"accept_order_{order_id}")
        )
        couriers = json.loads(
            requests.get(url=f"http://127.0.0.1:8005/api/telegram-users/couriers/").content)['results']
        base_dir = os.path.dirname(os.path.abspath(__file__))
        photo_url = os.path.join(base_dir, 'images', new_order['image'][7:])
        for courier in couriers:
            if courier['is_available']:
                try:
                    with open(photo_url, 'rb') as photo_file:
                        await bot.send_photo(chat_id=courier['chat_id'], photo=photo_file, caption=order_summary,
                                             parse_mode="Markdown",
                                             reply_markup=accept_button)
                except FileNotFoundError:
                    pass
        await call.message.delete()
        await call.message.answer("❌ Ваша работа отменена!",
                                  reply_markup=await main_menu_buttons(call.from_user.id))
    except Exception as e:
        await call.message.answer(f"⚠ Произошла ошибка при отмене заказа: {e}")


@dp.callback_query_handler(lambda call: call.data.startswith("done_courier_"))
async def mark_order_delivered(call: types.CallbackQuery):
    order_id = call.data.split("_")[-1]

    try:
        s_data = {
            "status": "delivered",
        }
        new_order = requests.patch(
            url=f"http://127.0.0.1:8005/api/orders/update/{order_id}/",
            json=s_data
        ).json()
        user = requests.get(
            url=f"http://127.0.0.1:8005/api/telegram-users/detail/{new_order['user']}"
        ).json()

        courier = requests.get(
            url=f"http://127.0.0.1:8005/api/telegram-users/detail/{new_order['courier']}"
        ).json()
        courier_name = courier.get('full_name', 'Неизвестно')
        courier_username = courier.get('username')
        courier_contact = f"@{courier_username}" if courier_username else "неизвестен"

        await bot.send_message(
            chat_id=user['chat_id'],
            text=(
                f"✅ Ваш заказ #{order_id} был доставлен!\n\n"
                f"🚶 Курьер: {courier_name}\n"
                f"🔗 Связаться: {courier_contact}\n"
                f"📲 Телефон: {courier.get('phone_number', 'не указан')}\n\n"
                f"Спасибо, что воспользовались нашей службой доставки! 🙏"
            )
        )
        await call.message.delete()
        await call.message.answer(
            f"✅ Заказ #{order_id} успешно отмечен как доставленный.",
            reply_markup=await main_menu_buttons(call.from_user.id)
        )

    except Exception as e:
        await call.message.answer(
            f"⚠ Произошла ошибка: {e}",
            reply_markup=await main_menu_buttons(call.from_user.id)
        )
