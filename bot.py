import telebot
from config import token
import sqlite3


bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start_work'])
def start_work(message):
    global global_user_data
    user_id = message.from_user.id
    username = message.from_user.username
    user_found = False

    # Соединение с базой данных
    db = sqlite3.connect("info.db")

    # Создание курсора для текущего потока
    c = db.cursor()
    c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    username TEXT,
                    vozrast INTEGER,
                    pol INTEGER,
                    interesi TEXT
                )
            ''')

    c.execute('SELECT * FROM users WHERE username=?', (username,))
    row = c.fetchone()

    if row:
        user_found = True
        bot.reply_to(message,
                     f"{username}, вы уже есть в базе. Если у вас есть вопросы по командам, используйте /help.")
    elif username == None:
        bot.reply_to(message, "У вас нет имени пользователя. Создайте его, если у вас ПК, то "
                              "[ссылка на создание ника в телеграме](https://sitevam.com/ustanovka-nika-v-telegrame). "
                              "Если у вас телефон, то [ссылка для iOS](https://clientdiary.com/knowledgebase/find-or-create-your-telegram-username-ios/), "
                              "[ссылка для Android](https://clientdiary.com/knowledgebase/find-or-create-your-telegram-username-android/).")

    if user_found == False:
        markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        item1 = telebot.types.KeyboardButton("мужской")
        item2 = telebot.types.KeyboardButton("женский")
        item3 = telebot.types.KeyboardButton("психическое отклонение")
        markup.add(item1, item2, item3)

        bot.reply_to(message, "Выберите, ваш пол:", reply_markup=markup)

        # Вызываем обработчик для выбора пола
        bot.register_next_step_handler(message, process_gender)


def process_gender(message):
    choice = message.text.lower()
    user_id = message.from_user.id
    username = message.from_user.username
    pol = 1 if choice == 'мужской' else 0

    bot.reply_to(message, f"{username}, укажите ваш возраст.")

    # Вызываем обработчик для ввода возраста
    bot.register_next_step_handler(message, process_age, pol)


def process_age(message, pol):
    user_id = message.from_user.id
    username = message.from_user.username
    age = message.text

    if not age.isdigit() or not 7 <= int(age) <= 99:
        bot.reply_to(message, f"{username}, укажите ваш настоящий возраст.")
        # Повторяем запрос возраста
        bot.register_next_step_handler(message, process_age, pol)
        return

    vozrast = int(age)
    bot.reply_to(message, f"{username}, укажите ваши интересы или что-то о себе (не более 75 символов).")

    # Вызываем обработчик для ввода интересов
    bot.register_next_step_handler(message, process_interests, pol, vozrast)


def process_interests(message, pol, vozrast):
    user_id = message.from_user.id
    username = message.from_user.username

    if len(message.text) > 75:
        bot.reply_to(message, f"{username}, у вас слишком много символов ({len(message.text)}).")
    else:
        interesi = message.text
        user_data = (username, vozrast, pol, interesi)
        db = sqlite3.connect("info.db")
        c = db.cursor()
        c.execute('INSERT INTO users (username, vozrast, pol, interesi) VALUES (?, ?, ?, ?)', user_data)
        db.commit()
        bot.reply_to(message,
                     f"Поздравляем с первым входом, {username}! Этот бот помогает людям найти человека для общения или получения помощи от реальных людей. Прежде чем продолжить, примите политику конфиденциальности.")
        bot.send_message(user_id,
                         "Если вы продолжите пользоваться ботом, примите политику конфиденциальности. Её можно посмотреть, вызвав функцию /privacy_policy_and_creators.")
        bot.reply_to(message,
                     "в случае вопросов напишите команду /help! в случае дополнительных вопросов напишите пользователю @aaaaaa366 важно! если у вас нет имени пользователя это значит что вам нужно его указать или дать другой способ связаться друшим с вами")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_message = "Список доступных команд:\n"
    help_message += "/start_work - добавление в базу пользователей\n"
    help_message += "/help - отображение списка команд и их описаний\n"
    help_message += "/settings - возможность поменять язык you can change language\n"
    help_message += "/privacy_policy_and_creators - возможность ознакомиться с самой новой версией политики конфиденциальности\n"
    help_message += "/list_applications - ознакомится со списком заявок\n"
    help_message += "/del_applications - изменение заявки анкеты\n"
    help_message += "/sponsor рекламодатели на сегодня"
    help_message += "1 если отснауться вопросы или жалобы и иное что вы не смогли решить то напишите пользователю @aaaaaa366 "
    bot.reply_to(message, help_message)


@bot.message_handler(commands=['del_applications'])
def del_applications(message):
    user_id = message.from_user.id

    # Создаем клавиатуру с выбором пользователя
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    item1 = telebot.types.KeyboardButton("Удалить из заявок")
    item2 = telebot.types.KeyboardButton("Удалить из базы")
    item3 = telebot.types.KeyboardButton("Удалить все")
    markup.add(item1, item2, item3)

    bot.reply_to(message, "Выберите, что вы хотите удалить:", reply_markup=markup)

    # Регистрируем обработчик следующего шага только для этого сообщения
    bot.register_next_step_handler(message, process_del_choice)

def process_del_choice(message):
    user_id = message.from_user.id
    choice = message.text.lower()

    if choice == "удалить из заявок":
        # Создаем подключение к базе данных info.db
        conn = sqlite3.connect("info.db")
        cursor = conn.cursor()
        username = message.from_user.username
        # Удаляем пользователя из заявок
        cursor.execute("DELETE FROM users WHERE username=?", (username,))
        conn.commit()

        bot.reply_to(message, "Ваша заявка удалена из заявок.")

        # Закрываем соединение с базой данных
        conn.close()

    elif choice == "удалить из базы":
        # Создаем подключение к базе данных info.db
        conn = sqlite3.connect("info.db")
        cursor = conn.cursor()
        username = message.from_user.username
        # Удаляем пользователя из базы
        cursor.execute("DELETE FROM users WHERE username=?", (username,))
        conn.commit()

        bot.reply_to(message, "Ваши данные удалены из базы.")

        # Закрываем соединение с базой данных
        conn.close()

    # Clear the keyboard after processing the choice

@bot.message_handler(commands=['privacy_policy_and_creators'])
def creators(message):
    bot.reply_to(message,"вот политика конфиденциальности")
    with open('policy_privacy.txt', 'r', encoding='utf-8') as file:
        # Read the entire content of the file
        file_content = file.read()
        bot.reply_to(message, f"вот политика конфиденциальности {file_content}")

@bot.message_handler(commands=['list_applications'])
def applications1(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    item1 = telebot.types.KeyboardButton("мужской")
    item2 = telebot.types.KeyboardButton("женский")
    item3 = telebot.types.KeyboardButton("пропуск")
    markup.add(item1, item2, item3)

    bot.reply_to(message, "Выберите, фильтр по полу, если не надо выберите пропуск:", reply_markup=markup)
    bot.register_next_step_handler(message, filtr_pol)

def filtr_pol(message):
    conn = sqlite3.connect("info.db")
    cursor = conn.cursor()
    try:
        if message.text == "пропуск":
            bot.reply_to(message, "Ок")
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            bot.reply_to(message, f"{rows}")
        elif message.text == "мужской":
            pol = 1
            bot.reply_to(message, "Введите возраст или пропуск")
            bot.register_next_step_handler(message, find, pol=pol)
        elif  message.text == "женский":
            pol = 2
            bot.reply_to(message, "Введите возраст или пропуск")
            bot.register_next_step_handler(message, find, pol=pol)
        else:
            bot.reply_to(message, "Команда отменена")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")
    finally:
        conn.close()

def find(message, pol):
    conn = sqlite3.connect("info.db")
    cursor = conn.cursor()
    try:
        if message.text != "пропуск":
            vozrast = message.text
            cursor.execute("SELECT * FROM users WHERE vozrast=? AND pol=?", (vozrast, pol))
            rows = cursor.fetchall()
            bot.reply_to(message, f"{rows}")
        else:
            bot.reply_to(message, "Команда отменена")
    except Exception as e:
        bot.reply_to(message, f"Произошла ошибка: {e}")
    finally:
        conn.close()

bot.infinity_polling()