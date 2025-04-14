# Розгортання в продакшн

## Вимоги
- Архітектура: x86_64
- CPU: 1 vCore (2+ рекомендовано)
- RAM: 512 МБ (1 ГБ рекомендовано)
- Disk: 2 ГБ SSD (для логів, БД, віртуалки, оновлень)

## Необхідне програмне забезпечення
- Python 3.10+
- pip
- python-telegram-bot
- psycopg2-binary
- python-dotenv

## Налаштування мережі
- Портів для Telegram API відкривати не треба — бот сам ініціює з'єднання.
- Перевірити, щоб був вихід в інтернет.
- Ввімкнена підтримка DNS, ping до api.telegram.org має працювати.

## Конфігурація серверів
1. Створити користувача:
sudo adduser botuser
sudo usermod -aG sudo botuser

2. Оновити систему:
sudo apt update && sudo apt upgrade -y

3. Встановити необхідне:
sudo apt install python3 python3-venv python3-pip postgresql git -y

4. Клонувати репозиторій:
git clone ps://github.com/yanassdd/DiplomaProject
cd /home/botuser/DiplomaProject

## Налаштування СУБД
1. Зайти в PostgreSQL:
sudo -u postgres psql

2. Створити базу і користувача:
CREATE DATABASE taskplanner;
CREATE USER botuser WITH PASSWORD 'strongpassword';
GRANT ALL PRIVILEGES ON DATABASE taskplanner TO botuser;
\q

3. Перевірити підключення з Python:
у .env файлі має бути:
DATABASE_URL=postgresql://botuser:strongpassword@localhost:5432/taskplanner

## Розгортання коду
1. Активувати віртуальне середовище:
python3 -m venv venv
source venv/bin/activate

2. Встановити залежності:
pip install -r requirements.txt

3. Заповнити .env:
BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://botuser:strongpassword@localhost:5432/taskplanner

4. Запуск вручну (перший раз):
python bot.py

## Перевірка працездатності
1. Сервіс працює:
systemctl status taskplannerbot

Очікуємо active (running)

2. Бот відповідає:
Відкрий Telegram, напиши /start — бот повинен відповісти вітальним повідомленням.

3. Перевірка логів:
journalctl -u taskplannerbot -f

Там буде видно всі команди користувачів і помилки (якщо є).

