import telebot
import json
import os
import threading
import time

USER_DATA_FILE = "user_data.json"

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, "r") as file:
            return json.load(file)
    return {}

def save_user_data(user_data):
    with open(USER_DATA_FILE, "w") as file:
        json.dump(user_data, file, indent=4)

def get_user_data(user_id):
    user_data = load_user_data()
    if str(user_id) not in user_data:
        user_data[str(user_id)] = {
            "name": "",
            "score": 0,
            "tap_power": 1,
            "auto_tap": {"1": 0, "10": 0, "100": 0, "1000": 0}
        }
    return user_data[str(user_id)]

def update_user_data(user_id, data):
    user_data = load_user_data()
    user_data[str(user_id)] = data
    save_user_data(user_data)

def auto_tap(bot):
    while True:
        user_data = load_user_data()
        for user_id, data in user_data.items():
            auto_tap_income = (
                    data["auto_tap"]["1"] * 1 +
                    data["auto_tap"]["10"] * 10 +
                    data["auto_tap"]["100"] * 100 +
                    data["auto_tap"]["1000"] * 1000
            )
            data["score"] += auto_tap_income
            update_user_data(user_id, data)
        time.sleep(1)


bot = telebot.TeleBot("7715916868:AAEE208ePltIAG4WvAUjMcErYCqC7crh_b0")

PROMO_CODES = {
    "FREE10000": 10000,
    "BONUS50000": 50000,
    "MEGA1000000": 1000000
}

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)

    if not user_data.get("name"):  # Проверяем, есть ли имя
        bot.send_message(message.chat.id, "Добро пожаловать в Shishi4ka Coin! 💰\n\n"
                                          "Этот бот дает вам настоящие деньги, которые можно заработать.\n"
                                          "1000 тапов = 100 рублей. Начните прямо сейчас!\n\n"
                                          "Для начала введите ваше имя:")
        bot.register_next_step_handler(message, ask_name)
    else:
        show_main_menu(message)

def ask_name(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    name = message.text.strip()

    user_data_all = load_user_data()
    for user in user_data_all.values():
        if user["name"].lower() == name.lower():
            bot.send_message(message.chat.id,
                             "❌ Пользователь с таким именем уже существует. Пожалуйста, выберите другое имя.")
            bot.register_next_step_handler(message, ask_name)
            return

    user_data["name"] = name
    update_user_data(user_id, user_data)
    bot.send_message(message.chat.id,
                     f"Отлично, {user_data['name']}! Теперь вы можете начать зарабатывать Shishi4ka Coin.")
    show_main_menu(message)

def show_main_menu(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
    btn_tap = telebot.types.KeyboardButton("Тапнуть")
    btn_shop = telebot.types.KeyboardButton("Магазин")
    btn_leaders = telebot.types.KeyboardButton("Лидеры")
    btn_transfer = telebot.types.KeyboardButton("Перевести деньги")
    markup.add(btn_tap, btn_shop, btn_leaders, btn_transfer)
    bot.send_message(
        message.chat.id,
        f"👋 Привет, {user_data['name']}!\n"
        f"💰 Ваши очки: {user_data['score']}\n"
        f"💪 Сила тапа: {user_data['tap_power']}\n"
        f"🤖 Автотапы: 1/s: {user_data['auto_tap']['1']}, 10/s: {user_data['auto_tap']['10']}, "
        f"100/s: {user_data['auto_tap']['100']}, 1000/s: {user_data['auto_tap']['1000']}",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "Тапнуть")
def tap(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    user_data["score"] += user_data["tap_power"]
    update_user_data(user_id, user_data)
    bot.send_message(message.chat.id, f"Вы тапнули! 💥 Ваши очки: {user_data['score']}")

@bot.message_handler(func=lambda message: message.text == "Магазин")
def shop(message):
    markup = telebot.types.InlineKeyboardMarkup()
    btn_upgrade_tap = telebot.types.InlineKeyboardButton(
        f"💪 +1 тап (100)", callback_data="upgrade_tap"
    )
    btn_buy_auto_1 = telebot.types.InlineKeyboardButton(
        f"🤖 1/s (500)", callback_data="buy_auto_1"
    )
    btn_buy_auto_10 = telebot.types.InlineKeyboardButton(
        f"🤖 10/s (5000)", callback_data="buy_auto_10"
    )
    btn_buy_auto_100 = telebot.types.InlineKeyboardButton(
        f"🤖 100/s (50000)", callback_data="buy_auto_100"
    )
    btn_buy_auto_1000 = telebot.types.InlineKeyboardButton(
        f"🤖 1000/s (500000)", callback_data="buy_auto_1000"
    )
    markup.add(btn_upgrade_tap, btn_buy_auto_1, btn_buy_auto_10, btn_buy_auto_100, btn_buy_auto_1000)
    bot.send_message(message.chat.id, "🛒 Магазин улучшений:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Лидеры")
def leaders(message):
    user_data = load_user_data()
    sorted_users = sorted(user_data.items(), key=lambda x: x[1]["score"], reverse=True)
    leaderboard = "🏆 Топ игроков:\n"
    for i, (user_id, data) in enumerate(sorted_users[:10], 1):
        leaderboard += f"{i}. {data['name']}: {data['score']} очков\n"
    bot.send_message(message.chat.id, leaderboard)

@bot.message_handler(func=lambda message: message.text == "Перевести деньги")
def transfer_money(message):
    bot.send_message(message.chat.id, "Введите ник получателя и сумму перевода в формате: `ник сумма`\n\n"
                                      "Пример: `Иван 100`")
    bot.register_next_step_handler(message, process_transfer)


def process_transfer(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    try:
        recipient_name, amount = message.text.split()
        amount = int(amount)
        if amount <= 0:
            bot.send_message(message.chat.id, "❌ Сумма должна быть больше нуля.")
            return

        if amount > user_data["score"]:
            bot.send_message(message.chat.id, "❌ Недостаточно очков для перевода.")
            return

        user_data_all = load_user_data()
        recipient_id = None
        for uid, data in user_data_all.items():
            if data["name"].lower() == recipient_name.lower():
                recipient_id = uid
                break

        if not recipient_id:
            bot.send_message(message.chat.id, "❌ Пользователь с таким именем не найден.")
            return

        if str(recipient_id) == str(user_id):
            bot.send_message(message.chat.id, "❌ Нельзя переводить деньги самому себе.")
            return

        user_data["score"] -= amount
        recipient_data = get_user_data(recipient_id)
        recipient_data["score"] += amount
        update_user_data(user_id, user_data)
        update_user_data(recipient_id, recipient_data)
        bot.send_message(message.chat.id, f"✅ Успешно переведено {amount} очков пользователю {recipient_name}.")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат. Используйте: `ник сумма`")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    user_data = get_user_data(user_id)

    if call.data == "upgrade_tap":
        if user_data["score"] >= 100:
            user_data["score"] -= 100
            user_data["tap_power"] += 1
            update_user_data(user_id, user_data)
            bot.answer_callback_query(call.id, "💪 Тап улучшен!")
        else:
            bot.answer_callback_query(call.id, "❌ Недостаточно очков!")
    elif call.data == "buy_auto_1":
        if user_data["score"] >= 500:
            user_data["score"] -= 500
            user_data["auto_tap"]["1"] += 1
            update_user_data(user_id, user_data)
            bot.answer_callback_query(call.id, "🤖 Автокликер (1/s) куплен!")
        else:
            bot.answer_callback_query(call.id, "❌ Недостаточно очков!")
    elif call.data == "buy_auto_10":
        if user_data["score"] >= 5000:
            user_data["score"] -= 5000
            user_data["auto_tap"]["10"] += 1
            update_user_data(user_id, user_data)
            bot.answer_callback_query(call.id, "🤖 Автокликер (10/s) куплен!")
        else:
            bot.answer_callback_query(call.id, "❌ Недостаточно очков!")
    elif call.data == "buy_auto_100":
        if user_data["score"] >= 50000:
            user_data["score"] -= 50000
            user_data["auto_tap"]["100"] += 1
            update_user_data(user_id, user_data)
            bot.answer_callback_query(call.id, "🤖 Автокликер (100/s) куплен!")
        else:
            bot.answer_callback_query(call.id, "❌ Недостаточно очков!")
    elif call.data == "buy_auto_1000":
        if user_data["score"] >= 500000:
            user_data["score"] -= 500000
            user_data["auto_tap"]["1000"] += 1
            update_user_data(user_id, user_data)
            bot.answer_callback_query(call.id, "🤖 Автокликер (1000/s) куплен!")
        else:
            bot.answer_callback_query(call.id, "❌ Недостаточно очков!")

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"💰 Ваши очки: {user_data['score']}\n"
             f"💪 Сила тапа: {user_data['tap_power']}\n"
             f"🤖 Автотапы: 1/s: {user_data['auto_tap']['1']}, 10/s: {user_data['auto_tap']['10']}, "
             f"100/s: {user_data['auto_tap']['100']}, 1000/s: {user_data['auto_tap']['1000']}",
        reply_markup=call.message.reply_markup
    )

@bot.message_handler(commands=["admin"])
def admin_panel(message):
    if message.text == "/admin hack":
        user_id = message.from_user.id
        user_data = get_user_data(user_id)
        user_data["score"] = float("inf")
        update_user_data(user_id, user_data)
        bot.send_message(message.chat.id, "🔓 Админ-панель активирована. У вас бесконечные деньги!")
    else:
        bot.send_message(message.chat.id, "❌ Неверный пароль.")

@bot.message_handler(commands=["promo"])
def promo(message):
    promo_code = message.text.split()[1] if len(message.text.split()) > 1 else None
    if promo_code in PROMO_CODES:
        user_id = message.from_user.id
        user_data = get_user_data(user_id)
        user_data["score"] += PROMO_CODES[promo_code]
        update_user_data(user_id, user_data)
        bot.send_message(message.chat.id, f"🎉 Промокод активирован! Вы получили {PROMO_CODES[promo_code]} очков.")
    else:
        bot.send_message(message.chat.id, "❌ Неверный промокод.")

threading.Thread(target=auto_tap, args=(bot,), daemon=True).start()

bot.polling(none_stop=True)
