import telebot
from telebot import types
import datetime
import threading
import time
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import uuid
import traceback

# Налаштування логування
log_level = os.getenv("LOG_LEVEL", "INFO").upper()

# Основне налаштування логів
logging.basicConfig(
    level=log_level,
    format="%(asctime)s [%(levelname)s] [%(user_id)s] %(message)s",  # додано user_id в формат
    handlers=[
        logging.FileHandler("habit_tracker.log"),
        logging.StreamHandler()
    ]
)

# Ротація логів
log_file = RotatingFileHandler(
    "C:\\Users\\Asus\\Desktop\\SumDU\\Diploma\\DiplomaProject\\logs\\bot.log", maxBytes=1_000_000, backupCount=3)
log_file.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s"))

logging.basicConfig(
    level=getattr(logging, log_level, logging.INFO),
    handlers=[
        log_file,
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Завантаження змінних оточення
load_dotenv()
token = os.getenv("TELEGRAM_BOT_TOKEN")

if not token:
    raise ValueError("Токен бота не знайдено! Додайте його в .env")

bot = telebot.TeleBot(token)

user_habits = {}
deleted_habits = {}
reminder_schedules = {}
habit_stats = {}

# Функція для логування контексту
def log_user_action(user_id, message, level="INFO"):
    logger.log(getattr(logging, level), message, extra={"user_id": user_id})

# Старт бота
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    send_help_message(message)
    log_user_action(user_id, f"Початок роботи з ботом")

# Додавання нової звички
@bot.message_handler(commands=['add_habit'])
def add_habit(message):
    user_id = message.from_user.id
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
    log_user_action(user_id, f"Звичка '{habit_name}' додана")

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
                log_user_action(user_id, f"Звичка '{habit_name}' відзначена як виконана")
                bot.reply_to(message, f"Звичка '{habit_name}' відзначена як виконана!")
            else:
                bot.reply_to(message, "Ця звичка вже відзначена як виконана.")
        else:
            raise ValueError
    except ValueError:
        bot.reply_to(message, "Невірний номер звички. Спробуйте ще раз.")

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
            log_user_action(user_id, f"Видалено звичку '{habit_name}'")
            bot.reply_to(message, f"Звичка '{habit_name}' видалена.")
        else:
            raise ValueError
    except ValueError:
        bot.reply_to(message, "Невірний номер звички. Спробуйте ще раз.")

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

# Фонова перевірка нагадувань
def check_reminders():
    while True:
        now = datetime.datetime.now()
        for user_id, habits in reminder_schedules.items():
            for habit_name, reminder_time in habits.items():
                if now.time().hour == reminder_time.hour and now.time().minute == reminder_time.minute:
                    bot.send_message(user_id, f"Нагадування: пора виконати звичку '{habit_name}'!")
        time.sleep(60)
        logger.debug(f"Надіслано нагадування користувачу {user_id} про звичку '{habit_name}'")

# Запуск фонового потоку
reminder_thread = threading.Thread(target=check_reminders, daemon=True)
reminder_thread.start()

# Запуск бота
print("Бот запущено!")
logger.info("Бот запущено та слухає оновлення")
bot.polling(none_stop=True)
