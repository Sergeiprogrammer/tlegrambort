import telebot
import time
import random
from config import token
import sqlite3

bot = telebot.TeleBot(token)

ban_count = 0

@bot.message_handler(commands=['sponsor'])
def ad(message):
    with open("ad.txt", encoding="utf-8", mode="r") as file:
        user_id = message.from_user.id
        line = file.read()
        bot.send_message(user_id,f"{line}")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,"привет вас приведствует мой бот для поиска знакомств нажмите /help что бы воспользоваться функционалом бота")

@bot.message_handler(commands=['start_work'])
def send_welcome(message):
    global global_user_data
    user_id = message.from_user.id
    username = message.from_user.username  # Добавлено получение имени пользователя
    user_found = False

    # Соединение с базой данных
    db = sqlite3.connect("data_account.db")

    # Создание курсора для текущего потока
    c = db.cursor()
    c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id_user1 TEXT,
                vozrast INTEGER,
                pol INTEGER,
                interesi TEXT
            )
        ''')

    row = c.fetchone()

    if row:
        user_found = True
        bot.reply_to(message,
                     f"{username}, вы уже есть в базе. Если у вас есть вопросы по командам, используйте /help.")
    else:
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
    bot.register_next_step_handler(message, process_interests, pol, vozrast, None)

def process_interests(message, pol, vozrast, intersi):
    global global_user_data
    user_id = message.from_user.id
    username = message.from_user.username

    if len(message.text) > 75:
        bot.reply_to(message, f"{username}, у вас слишком много символов ({len(message.text)}).")
    else:
        interesi = message.text
        user_data = (username,vozrast, pol, interesi)
        username = message.from_user.username
        global_user_data = user_data
        db = sqlite3.connect("data_account.db")
        c = db.cursor()
        c.execute('INSERT INTO users (id_user1, vozrast, pol, interesi) VALUES (?, ?, ?, ?)', (user_data))
        db.commit()
        bot.reply_to(message, f"Поздравляем с первым входом, {username}! Этот бот помогает людям найти человека для общения или получения помощи от реальных людей. Прежде чем продолжить, примите политику конфиденциальности.")
        bot.send_message(user_id, "Если вы продолжите пользоваться ботом, примите политику конфиденциальности. Её можно посмотреть, вызвав функцию /privacy_policy_and_creators.")
        bot.reply_to(message, "в случае вопросов напишите команду /help! в случае дополнительных вопросов напишите пользователю @aaaaaa366 важно! если у вас нет имени пользователя это значит что вам нужно его указать или дать другой способ связаться друшим с вами")

@bot.message_handler(commands=['help'])
def send_help(message):
    help_message = "Список доступных команд:\n"
    help_message += "/start - приветсвие\n"
    help_message += "/start_work - добавление в базу пользователей\n"
    help_message += "/get_status - получение статуса пользователя (в разработке)\n"
    help_message += "/help - отображение списка команд и их описаний\n"
    help_message += "/main - подать заявку на знакомство\n"
    help_message += "/settings - возможность поменять язык you can change language\n"
    help_message += "/privacy_policy_and_creators - возможность ознакомиться с самой новой версией политики конфиденциальности\n"
    help_message += "/list_applications - ознакомится со списком заявок\n"
    help_message += "/del_applications - изменение заявки анкеты\n"
    help_message += "/sponsor рекламодатели на сегодня"
    help_message += "1 если отснауться вопросы или жалобы и иное что вы не смогли решить то напишите пользователю @aaaaaa366 2 добавление в базу 3 просмотр подача заявки 4 удаленть заявку, очисть базу ,очитстить всё 5 изменить заявку. 2 чтобы добавить себя в базу напишите /start база нужна чтобы сделать в ней заявку которая будет подана.если вы уже та есть то вы получите сообщение ''имя_пользователя', вы уже есть в базе со статусом 'название_статуса'. Если у вас есть вопросы по командам, используйте /help.'3 если хотите подать заявку на поиск общения и в принцыпе людей то воспользуйтесь командой halp_main если не хотиете подавать заявку а посмтореть уже поданные воспользуйтесь командой /list_applicationsс 3 если хотите удалить заявку то используйте команду del/applications и выберите удалить заявку а потом  5 чтобы изменить заявку посмторите 4 пункт только выберите удалить из базы а потом заново пропишите /del_aplications и выберите удалить из заявок после чего напшите /start ответив на все вопросы после чего пропишите /help_main "
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
        conn = sqlite3.connect("data_account.db")
        cursor = conn.cursor()
        username = message.from_user.username
        # Удаляем пользователя из заявок
        cursor.execute("DELETE FROM users WHERE id_user1=?", (username,))
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



@bot.message_handler(commands=['settings'])
def settings(message):
    bot.reply_to(message, "язык")
    if message.text == "язык":
        bot.reply_to(message, "Доступные языки: английский, русский. Введите 1 или 2.")
    elif message.text == "1":
        bot.reply_to(message, "Русский по умолчанию.")
    elif message.text == "2":
        bot.reply_to(message, "Default language is English.")
    else:
        bot.reply_to(message, "english")


@bot.message_handler(commands=['privacy_policy_and_creators'])
def creators(message):
    bot.reply_to(message,"вот политика конфиденциальности")
    with open('policy_privacy.txt', 'r', encoding='utf-8') as file:
        # Read the entire content of the file
        file_content = file.read()
        bot.reply_to(message, f"вот политика конфиденциальности {file_content}")

@bot.message_handler(commands=['list_applications'])
def applications(message):
    # Создаем подключение к базе данных info.db
    conn = sqlite3.connect("info.db")
    cursor = conn.cursor()

    # Выполняем запрос, чтобы получить все заявки
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()
    bot.reply_to(message,f"{rows}")

    # Закрываем соединение с базой данных
    conn.close()

    # Добавляем отладочные выводы


def create_users_table():
    conn = sqlite3.connect("info.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT,
            vozrast INTEGER,
            pol INTEGER,
            interesi TEXT
            
        )
    ''')
    conn.commit()
    conn.close()

# Вызываем функцию для создания таблицы перед выполнением запросов
@bot.message_handler(commands=['main'])
def normal_function(message):
    global global_user_data
    create_users_table()
    username = message.from_user.username
    h = 0

    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    item1 = telebot.types.KeyboardButton("да")
    item2 = telebot.types.KeyboardButton("нет")
    markup.add(item1, item2)

    bot.reply_to(message, "Вы можете отправить анкету котором будет ваш ник. Отправить или нет?:",
                 reply_markup=markup)

    # Проверяем, отправлял ли пользователь уже запрос
    conn = sqlite3.connect("data_account.db")
    user_id = message.from_user.id
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id_user1=?', (username,))
    row = cursor.fetchone()
    conn.close()
    username = message.from_user.username

    if row:
        h = row[2]
    elif username == None:
        bot.reply_to(message, "У вас нет имени пользователя. Создайте его, если у вас ПК, то "
                              "[ссылка на создание ника в телеграме](https://sitevam.com/ustanovka-nika-v-telegrame). "
                              "Если у вас телефон, то [ссылка для iOS](https://clientdiary.com/knowledgebase/find-or-create-your-telegram-username-ios/), "
                              "[ссылка для Android](https://clientdiary.com/knowledgebase/find-or-create-your-telegram-username-android/).")

@bot.message_handler(func=lambda message: True)
def handle_user_response(message):
    global user_data
    user_id = message.from_user.id
    username = message.from_user.username
    choice = message.text.lower()

    # Проверяем, отправлял ли пользователь уже запрос
    conn = sqlite3.connect("info.db")
    cursor = conn.cursor()
    create_users_table()
    cursor.execute('SELECT * FROM users WHERE username=?', (username,))
    row = cursor.fetchone()

    if choice == "да" and not row and username is not None:
        a = random.choice(range(1, 400)) / 100
        time.sleep(a)
        bot.reply_to(message, "Проверка пройдена")
        bot.reply_to(message, "Операция может занять время")

        time.sleep(a)

        # Соединение с базой данных data_account.db
        conn_data = sqlite3.connect("data_account.db")
        cursor_data = conn_data.cursor()

        # Проверяем наличие пользователя в data_account.db
        cursor_data.execute("SELECT * FROM users WHERE id_user1=?", (username,))
        row_data = cursor_data.fetchone()
        bot.reply_to(message, f"{row_data}")
        if row_data is not None and username in row_data:
            # Добавляем пользователя в базу данных info.db
            db = sqlite3.connect("info.db")
            c = db.cursor()  # Исправлено здесь
            c.execute('INSERT INTO users (username, pol, interesi, vozrast) VALUES (?, ?, ?, ?)', row_data)  # Исправлено здесь
            db.commit()

            bot.reply_to(message, f"Выполнено 1/1 операций")
            c.execute("SELECT * FROM users WHERE username=?", (username,))  # Исправлено здесь
            print(c.fetchall())  # Исправлено здесь
            db.close()
        else:
            bot.reply_to(message, "Пользователь не найден в data_account.db ")

        conn_data.close()
    elif username is None:
        pass
    else:
        bot.reply_to(message, "Место уже занято. Попробуйте позже.")

    conn.close()



@bot.message_handler(commands=['get_status'])
def get_status(message):
    user_id = message.from_user.id
    bot.send_message(user_id, "Доступен для получения 1 уровень. Получить? да/нет")

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    global ban_count

    if message.text.lower() == "да":
        user_id = message.from_user.id
        bot.reply_to(message, "Проверка")
        with open('data_account.txt','r',encoding='utf-8' ) as file_object:
            lines = file_object.readlines()
            e = str(f"{user_id}status = 1\n")
            j = str(f"{user_id}status = 2\n")
            for line in lines:
                if e not in line:
                    bot.reply_to(message, "Проверка не пройдена статус обычный доступ к функции недоступен")
                elif j not in line:
                    bot.reply_to(message, "Проверка пройдена статус админ")
                    bot.reply_to(message, "введите ник чтобы забанить человека")
                else:
                    bot.reply_to(message, "Проверка не пройдена. Проблема: отсутствие аккаунта и статуса в базе. Решение: напишите команду /start.")
                    break

    elif message.text.lower() == "нет":
        bot.reply_to(message, "Ок, команда отменена.")
    else:
        ban_count += 1
        if ban_count >= 10:
            time.sleep(30)
            ban_count = 0
            bot.reply_to(message, "Бан! Причина: спам. Заблокирован на 30 секунд.")
        else:
            bot.reply_to(message, f"Такой команды нет. До бана по причине 'спам' осталось {10 - ban_count} вводов.")




bot.infinity_polling()
