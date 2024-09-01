import telebot
from telebot import types
from tinydb import TinyDB, Query
import random

# Инициализация бота и базы данных
bot_token = "7340124584:AAH5GfjUaY5mPobBb5ajhOmCZz7Hmlpn3ME"
bot = telebot.TeleBot(bot_token)
db = TinyDB('db.json')
users_db = db.table('users')
admin_db = db.table('admins')
ban_db = db.table('banned')
settings_db = db.table('settings')

TWG = 'TWG'  # Название валюты

# ID администратора
admin_id = 6918180010

# Основные настройки бота
settings = settings_db.get(Query().key == 'settings')
if not settings:
    settings_db.insert({'key': 'settings', 'maintenance': False})
    settings = settings_db.get(Query().key == 'settings')

# Функция проверки, находится ли бот в режиме тех. работ
def is_maintenance():
    settings = settings_db.get(Query().key == 'settings')
    return settings['maintenance']

# Основные команды
@bot.message_handler(commands=['start'])
def start(message):
    if is_maintenance() and message.chat.id != admin_id:
        bot.send_message(message.chat.id, "Бот временно недоступен из-за технических работ.")
        return

    user_id = message.chat.id
    if not users_db.contains(Query().user_id == user_id):
        users_db.insert({'user_id': user_id, 'coins': 0, 'farm_level': 1, 'video_cards': 1, 'income_per_hour': 1, 'tax': 0.1, 'last_bonus': None})

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('👷 Моя ферма', '💰 Доход', '🎲 Кубик', '🎁 Ежедневный бонус')
    if user_id == admin_id:
        markup.add('🔧 Админ панель')
    bot.send_message(user_id, "Добро пожаловать в мир майнинга!", reply_markup=markup)

# Проверка бана
def is_banned(user_id):
    return ban_db.contains(Query().user_id == user_id)

# Команда для отображения фермы
@bot.message_handler(regexp="👷 Моя ферма")
def my_farm(message):
    if is_maintenance() and message.chat.id != admin_id:
        bot.send_message(message.chat.id, "Бот временно недоступен из-за технических работ.")
        return

    if is_banned(message.chat.id):
        bot.send_message(message.chat.id, "Вы забанены и не можете пользоваться ботом.")
        return

    user_id = message.chat.id
    user = users_db.get(Query().user_id == user_id)
    farm_info = f"📈 Уровень фермы: {user['farm_level']}\n" \
                f"🖥 Видеокарты: {user['video_cards']}\n" \
                f"💰 Доход в час: {user['income_per_hour']} {TWG}\n" \
                f"💸 Налог: {user['tax'] * 100}%"
    bot.send_message(user_id, farm_info)

# Команда для отображения дохода
@bot.message_handler(regexp="💰 Доход")
def income(message):
    if is_maintenance() and message.chat.id != admin_id:
        bot.send_message(message.chat.id, "Бот временно недоступен из-за технических работ.")
        return

    if is_banned(message.chat.id):
        bot.send_message(message.chat.id, "Вы забанены и не можете пользоваться ботом.")
        return

    user_id = message.chat.id
    user = users_db.get(Query().user_id == user_id)
    income = user['income_per_hour'] * (1 - user['tax'])
    bot.send_message(user_id, f"Ваш текущий доход в час: {income} {TWG}")

# Прокачка фермы
@bot.message_handler(regexp="📈 Прокачать ферму")
def upgrade_farm(message):
    if is_maintenance() and message.chat.id != admin_id:
        bot.send_message(message.chat.id, "Бот временно недоступен из-за технических работ.")
        return

    if is_banned(message.chat.id):
        bot.send_message(message.chat.id, "Вы забанены и не можете пользоваться ботом.")
        return

    user_id = message.chat.id
    user = users_db.get(Query().user_id == user_id)
    users_db.update({'farm_level': user['farm_level'] + 1, 'income_per_hour': user['income_per_hour'] + 1, 'video_cards': user['video_cards'] + 1}, Query().user_id == user_id)
    bot.send_message(user_id, "Вы успешно прокачали ферму!")

# Команда "Кубик" для игры со ставками
@bot.message_handler(regexp="🎲 Кубик")
def roll_dice(message):
    if is_maintenance() and message.chat.id != admin_id:
        bot.send_message(message.chat.id, "Бот временно недоступен из-за технических работ.")
        return

    if is_banned(message.chat.id):
        bot.send_message(message.chat.id, "Вы забанены и не можете пользоваться ботом.")
        return

    user_id = message.chat.id
    bot.send_message(user_id, "Введите вашу ставку в TWG:")

    @bot.message_handler(func=lambda msg: msg.text.isdigit() and msg.chat.id == user_id)
    def place_bet(msg):
        bet = int(msg.text)
        user = users_db.get(Query().user_id == user_id)

        if bet > user['coins']:
            bot.send_message(user_id, "У вас недостаточно TWG для ставки.")
            return

        bot.send_dice(user_id)
        result = random.randint(1, 6)
        bot.send_message(user_id, f"Выпало число: {result}")

        if result >= 4:  # Победа при 4, 5, 6
            win_amount = bet * 2
            users_db.update({'coins': user['coins'] + win_amount}, Query().user_id == user_id)
            bot.send_message(user_id, f"Вы выиграли {win_amount} {TWG}!")
        else:
            users_db.update({'coins': user['coins'] - bet}, Query().user_id == user_id)
            bot.send_message(user_id, f"Вы проиграли {bet} {TWG}. Попробуйте снова!")

# Ежедневный бонус
@bot.message_handler(regexp="🎁 Ежедневный бонус")
def daily_bonus(message):
    if is_maintenance() and message.chat.id != admin_id:
        bot.send_message(message.chat.id, "Бот временно недоступен из-за технических работ.")
        return

    if is_banned(message.chat.id):
        bot.send_message(message.chat.id, "Вы забанены и не можете пользоваться ботом.")
        return

    user_id = message.chat.id
    user = users_db.get(Query().user_id == user_id)
    from datetime import datetime, timedelta

    if user['last_bonus']:
        last_bonus_time = datetime.strptime(user['last_bonus'], "%Y-%m-%d %H:%M:%S")
        if datetime.now() - last_bonus_time < timedelta(days=1):
            bot.send_message(user_id, "Вы уже получили бонус сегодня. Приходите завтра!")
            return

    bonus_amount = 100  # Сумма бонуса
    users_db.update({'coins': user['coins'] + bonus_amount, 'last_bonus': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, Query().user_id == user_id)
    bot.send_message(user_id, f"Вы получили ежедневный бонус: {bonus_amount} {TWG}!")

# Админ-панель
@bot.message_handler(regexp="🔧 Админ панель")
def admin_panel(message):
    user_id = message.chat.id
    if user_id == admin_id:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📜 Список игроков", callback_data='players_list'))
        markup.add(types.InlineKeyboardButton("⛔ Бан", callback_data='ban_player'))
        markup.add(types.InlineKeyboardButton("✅ Разбан", callback_data='unban_player'))
        markup.add(types.InlineKeyboardButton("🛠 Вкл/Выкл тех. работы", callback_data='toggle_maintenance'))
        bot.send_message(user_id, "Админ-панель", reply_markup=markup)
    else:
        bot.send_message(user_id, "У вас нет прав администратора.")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "players_list":
        players = users_db.all()
        players_info = "\n".join([f"ID: {p['user_id']}, Монеты: {p['coins']}" for p in players])
        bot.send_message(call.message.chat.id, f"Список игроков:\n{players_info}")
    elif call.data == "ban_player":
        bot.send_message(call.message.chat.id, "Введите ID пользователя для бана:")

        @bot.message_handler(func=lambda msg: msg.chat.id == admin_id)
        def ban_user(msg):
            user_id_to_ban = int(msg.text)
            if users_db.contains(Query().user_id == user_id_to_ban):
                if not is_banned(user_id_to_ban):
                    ban_db.insert({'user_id': user_id_to_ban})
                    bot.send_message(call.message.chat.id, f"Пользователь {user_id_to_ban} забанен.")
                else:
                    bot.send_message(call.message.chat.id, "Пользователь уже забанен.")
            else:
                bot.send_message(call.message.chat.id, "Пользователь не найден.")

    elif call.data == "unban_player":
        bot.send_message(call.message.chat.id, "Введите ID пользователя для разбана:")

        @bot.message_handler(func=lambda msg: msg.chat.id == admin_id)
        def unban_user(msg):
            user_id_to_unban = int(msg.text)
            if is_banned(user_id_to_unban):
                ban_db.remove(Query().user_id == user_id_to_unban)
                bot.send_message(call.message.chat.id, f"Пользователь {user_id_to_unban} разбанен.")
            else:
                bot.send_message(call.message.chat.id, "Пользователь не найден или не был забанен.")

    elif call.data == "toggle_maintenance":
        current_status = is_maintenance()
        settings_db.update({'maintenance': not current_status}, Query().key == 'settings')
        new_status = "включены" if not current_status else "выключены"
        bot.send_message(call.message.chat.id, f"Технические работы {new_status}.")

# Запуск бота
bot.polling()
