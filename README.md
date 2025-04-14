# TaskPlannerBot

**TaskPlannerBot** — це Telegram-бот, що допомагає ефективно планувати завдання, розподіляти пріоритети та не втрачати фокус. Інтелектуальна система оптимізує щоденне планування та підказує, як краще використати свій час.

##  Функціональні можливості

- Додавання нових завдань з пріоритетами
- Встановлення дедлайнів
- Розумне сортування завдань за важливістю
- Отримання щоденного списку завдань
- Редагування та видалення завдань
- Режим "Фокус" для покращення продуктивності
- Збереження завдань у базу даних
- Команди `/help`, `/today`, `/add`, `/delete`, `/focus`

##  Технології

- **Python 3.10+** — основна мова розробки
- **python-telegram-bot** — інтеграція з Telegram API
- **PostgreSQL** або **SQLite** — для зберігання даних
- **dotenv** — керування змінними середовища
- **SQLAlchemy** — ORM для бази даних

##  Необхідні інструменти

Перед початком роботи переконайся, що у тебе встановлено:

- [Python 3.10+](https://www.python.org/)
- [pip](https://pip.pypa.io/en/stable/)
- [Git](https://git-scm.com/)
- [PostgreSQL](https://www.postgresql.org/) (або використовуй SQLite)
- Рекомендовано: [VS Code](https://code.visualstudio.com/)

##  Налаштування середовища розробки

### Клонування репозиторію

```bash
git clone https://github.com/yanassdd/DiplomaProject
cd DiplomaProject

##  Налаштування віртуального середовища

python3 -m venv venv
source venv/bin/activate

## Встановлення та конфігурація залежностей

pip install --upgrade pip
pip install -r requirements.txt

## Створення та налаштування бази даних:
Якщо ти використовуєш SQLite, цей крок можна пропустити — база створиться автоматично.

## Крок 1: Встановлення PostgreSQL

sudo apt install postgresql postgresql-contrib

## Крок 2: Створення бази даних

CREATE DATABASE taskplanner;
CREATE USER botuser WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE taskplanner TO botuser;

## Крок 3: Налаштування .env

BOT_TOKEN=your_telegram_bot_token
DATABASE_URL=postgresql://botuser:yourpassword@localhost:5432/taskplanner

### Запуск проєкту у режимі розробки

python bot.py

Бот повинен запуститися й очікувати повідомлення від користувачів.