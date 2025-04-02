import telebot
from telebot import types
import datetime
import threading
import time
import os
from dotenv import load_dotenv

# Завантаження змінних оточення
load_dotenv()
token = os.getenv("TELEGRAM_BOT_TOKEN")

# Перевірка, чи токен існує
if not token:
    raise ValueError("Токен бота не знайдено! Додайте його в .env")

bot = telebot.TeleBot(token)


# Змінні для збереження даних
user_habits = {}
deleted_habits = {}
reminder_schedules = {}
habit_stats = {}

# Функція для відображення всіх команд
@bot.message_handler(commands=['help'])
def send_help_message(message):
    help_text = (
        "Доступні команди:\n"
        "/start - Початок роботи з ботом\n"
        "/add_habit - Додати нову звичку\n"
        "/my_habits - Показати ваші звички\n"
        "/mark_done - Відзначити виконану звичку\n"
        "/delete - Видалити звичку\n"
        "/review_previous_habits - Переглянути видалені звички\n"
        "/remind_me_of_habits - Нагадування про звички\n"
        "/delete_reminder - Видалити нагадування\n"
        "/stats - Показати статистику успіху\n"
        "/help - Показати цю довідку"
    )
    bot.reply_to(message, help_text)

# Старт бота
@bot.message_handler(commands=['start'])
def start(message):
    send_help_message(message)

# Додавання нової звички
@bot.message_handler(commands=['add_habit'])
def add_habit(message):
    msg = bot.reply_to(message, "Напишіть назву вашої звички (наприклад, 'Читання книги').")
    bot.register_next_step_handler(msg, process_habit)

def process_habit(message):
    user_id = message.from_user.id
    habit_name = message.text.strip()
    now = datetime.date.today()

    if user_id not in user_habits:
        user_habits[user_id] = []
        habit_stats[user_id] = {}

    user_habits[user_id].append({'habit': habit_name, 'completed': False, 'created_date': now})
    habit_stats[user_id][habit_name] = {'completed_days': 0, 'missed_days': 0}
    bot.reply_to(message, f"Звичка '{habit_name}' додана!")
    show_habits(message)

# Показати звички
@bot.message_handler(commands=['my_habits'])
def show_habits(message):
    user_id = message.from_user.id
    if user_id not in user_habits or not user_habits[user_id]:
        bot.reply_to(message, "У вас ще немає звичок. Додайте їх за допомогою /add_habit.")
        return

    habits_text = "Ваші звички:\n"
    for idx, habit in enumerate(user_habits[user_id], 1):
        status = "Зроблено" if habit['completed'] else "Не зроблено"
        habits_text += f"{idx}. {habit['habit']} - {status}\n"

    bot.reply_to(message, habits_text)

# Відмітка виконаної звички
@bot.message_handler(commands=['mark_done'])
def mark_done(message):
    user_id = message.from_user.id
    if user_id not in user_habits or not user_habits[user_id]:
        bot.reply_to(message, "У вас немає звичок для відмітки. Додайте їх за допомогою /add_habit.")
        return

    msg = bot.reply_to(message, "Введіть номер звички, яку ви хочете відзначити як виконану.")
    bot.register_next_step_handler(msg, process_mark_done)

def process_mark_done(message):
    user_id = message.from_user.id
    try:
        habit_number = int(message.text.strip())
        if 0 < habit_number <= len(user_habits[user_id]):
            habit = user_habits[user_id][habit_number - 1]
            if not habit['completed']:
                habit['completed'] = True
                habit_name = habit['habit']
                habit_stats[user_id][habit_name]['completed_days'] += 1
                bot.reply_to(message, f"Звичка '{habit_name}' відзначена як виконана!")
            else:
                bot.reply_to(message, "Ця звичка вже відзначена як виконана.")
        else:
            raise ValueError
    except ValueError:
        bot.reply_to(message, "Невірний номер звички. Ось ваші звички:\n")
        show_habits(message)
        msg = bot.reply_to(message, "Спробуйте ще раз:")
        bot.register_next_step_handler(msg, process_mark_done)

# Видалення звички
@bot.message_handler(commands=['delete'])
def delete_habit(message):
    user_id = message.from_user.id
    if user_id not in user_habits or not user_habits[user_id]:
        bot.reply_to(message, "У вас немає звичок для видалення. Додайте їх за допомогою /add_habit.")
        return

    msg = bot.reply_to(message, "Введіть номер звички, яку ви хочете видалити.")
    bot.register_next_step_handler(msg, process_delete)

def process_delete(message):
    user_id = message.from_user.id
    try:
        habit_number = int(message.text.strip())
        if 0 < habit_number <= len(user_habits[user_id]):
            habit = user_habits[user_id].pop(habit_number - 1)
            habit_name = habit['habit']
            deleted_habits[user_id] = deleted_habits.get(user_id, [])
            deleted_habits[user_id].append(habit)
            habit_stats[user_id].pop(habit_name, None)
            bot.reply_to(message, f"Звичка '{habit_name}' видалена.")
            show_habits(message)
        else:
            raise ValueError
    except ValueError:
        bot.reply_to(message, "Невірний номер звички. Ось ваші звички:\n")
        show_habits(message)
        msg = bot.reply_to(message, "Спробуйте ще раз:")
        bot.register_next_step_handler(msg, process_delete)

# Нагадування про звички
@bot.message_handler(commands=['remind_me_of_habits'])
def remind_me_of_habits(message):
    user_id = message.from_user.id
    if user_id not in user_habits or not user_habits[user_id]:
        bot.reply_to(message, "У вас немає звичок для нагадування. Додайте їх за допомогою /add_habit.")
        return

    habits_text = "Виберіть звичку для нагадування:\n"
    for idx, habit in enumerate(user_habits[user_id], 1):
        habits_text += f"{idx}. {habit['habit']}\n"

    msg = bot.reply_to(message, habits_text)
    bot.register_next_step_handler(msg, process_reminder)

def process_reminder(message):
    user_id = message.from_user.id
    try:
        habit_number = int(message.text.strip())
        if 0 < habit_number <= len(user_habits[user_id]):
            habit_name = user_habits[user_id][habit_number - 1]['habit']
            msg = bot.reply_to(message, "Вкажіть час нагадування у форматі HH:MM (наприклад, 14:30):")
            bot.register_next_step_handler(msg, process_set_reminder, habit_name)
        else:
            raise ValueError
    except ValueError:
        bot.reply_to(message, "Невірний номер звички.")
        remind_me_of_habits(message)

def process_set_reminder(message, habit_name):
    user_id = message.from_user.id
    try:
        reminder_time = datetime.datetime.strptime(message.text.strip(), "%H:%M").time()
        if user_id not in reminder_schedules:
            reminder_schedules[user_id] = {}
        reminder_schedules[user_id][habit_name] = reminder_time
        bot.reply_to(message, f"Нагадування для звички '{habit_name}' встановлено на {reminder_time}.")
    except ValueError:
        bot.reply_to(message, "Невірний формат часу. Спробуйте ще раз у форматі HH:MM.")

# Видалення нагадування
@bot.message_handler(commands=['delete_reminder'])
def delete_reminder(message):
    user_id = message.from_user.id
    if user_id not in reminder_schedules or not reminder_schedules[user_id]:
        bot.reply_to(message, "У вас немає нагадувань для видалення.")
        return

    habits_text = "Виберіть звичку для видалення нагадування:\n"
    for idx, habit in enumerate(reminder_schedules[user_id], 1):
        habits_text += f"{idx}. {habit}\n"

    msg = bot.reply_to(message, habits_text)
    bot.register_next_step_handler(msg, process_delete_reminder)

def process_delete_reminder(message):
    user_id = message.from_user.id
    try:
        habit_number = int(message.text.strip())
        habits = list(reminder_schedules[user_id].keys())
        if 0 < habit_number <= len(habits):
            habit_name = habits[habit_number - 1]
            reminder_schedules[user_id].pop(habit_name)
            bot.reply_to(message, f"Нагадування для звички '{habit_name}' видалено.")
        else:
            raise ValueError
    except ValueError:
        bot.reply_to(message, "Невірний номер звички.")
        delete_reminder(message)

# Перегляд видалених звичок
@bot.message_handler(commands=['review_previous_habits'])
def review_previous_habits(message):
    user_id = message.from_user.id
    if user_id not in deleted_habits or not deleted_habits[user_id]:
        bot.reply_to(message, "У вас немає видалених звичок.")
        return

    habits_text = "Ваші видалені звички:\n"
    for habit in deleted_habits[user_id]:
        habits_text += f"- {habit['habit']}\n"

    bot.reply_to(message, habits_text)

# Статистика успіху
@bot.message_handler(commands=['stats'])
def show_stats(message):
    user_id = message.from_user.id
    if user_id not in user_habits or not user_habits[user_id]:
        bot.reply_to(message, "У вас немає активних звичок.")
        return

    stats_text = "Статистика успіху:\n"
    for habit in user_habits[user_id]:
        habit_name = habit['habit']
        stats = habit_stats[user_id].get(habit_name, {'completed_days': 0, 'missed_days': 0})
        created_date = habit['created_date']
        stats_text += (
            f"Звичка: {habit_name}\n"
            f"Дата створення: {created_date}\n"
            f"Дні виконання: {stats['completed_days']}\n"
            f"Пропущені дні: {stats['missed_days']}\n\n"
        )

    bot.reply_to(message, stats_text)

# Фонова перевірка нагадувань
def check_reminders():
    while True:
        now = datetime.datetime.now()
        for user_id, habits in reminder_schedules.items():
            for habit_name, reminder_time in habits.items():
                if now.time().hour == reminder_time.hour and now.time().minute == reminder_time.minute:
                    bot.send_message(user_id, f"Нагадування: пора виконати звичку '{habit_name}'!")
        time.sleep(60)

# Запуск фонового потоку
reminder_thread = threading.Thread(target=check_reminders, daemon=True)
reminder_thread.start()

# Запуск бота
print("Бот запущено!")
bot.polling(none_stop=True)
