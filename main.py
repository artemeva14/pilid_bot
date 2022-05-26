import telebot
import sqlite3
from Token import t
from telebot import types
bot = telebot.TeleBot(t)
users = {}


class User:
    def __init__(self, name):
        self.name = name
        self.age = None
        self.sex = None


@bot.message_handler(commands=['start'])
def start(message):
    global i
    i = 0
    keyboard_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton("Добавить игрока")
    button2 = types.KeyboardButton("Закончить игру")
    keyboard_menu.add(button1, button2)
    bot.send_message(message.chat.id, 'Привет! Я бот-ведущий для игры в "Правда или Действие" \n\n' +
                     'Я создан чтобы экономить ваше время, поэтому я буду придумывать вопросы за вас! \n' +
                                      '\nСкорее добавляй игроков и приступим же к игре!', reply_markup=keyboard_menu)


@bot.message_handler(content_types='text')
def message_reply(message):
    global i
    if message.text == "Добавить игрока" or message.text == "Добавить еще одного игрока":
        msg = bot.send_message(message.chat.id, 'Введите имя игрока, которого сейчас добавляете')
        bot.register_next_step_handler(msg, process_name_step)
    if message.text == "Удалить игрока" or message.text == "Удалить еще одного игрока":
        msg = bot.send_message(message.chat.id, 'Введите имя игрока, которого хотите удалить')
        bot.register_next_step_handler(msg, process_delete)
    if message.text == "Вывести список игроков":
        select_all_users(message)
    if message.text == "Вернуться в меню":
        keyboard_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Добавить игрока")
        button2 = types.KeyboardButton("Удалить игрока")
        button3 = types.KeyboardButton("Вывести список игроков")
        button4 = types.KeyboardButton("Играть!")
        button5 = types.KeyboardButton("Закончить игру")
        keyboard_menu.add(button1, button2, button3)
        keyboard_menu.add(button4, button5)
        bot.send_message(message.chat.id, "Выберети дальнейшее действие", reply_markup=keyboard_menu)
    if message.text == "Играть!" or message.text == "Перейти к следующему игроку":
        play_game(message, i)
        i += 1
    if message.text == "Правда":
        if_choice_is_truth(message)
    if message.text == "Действие":
        if_choice_is_dare(message)
    if message.text == "Рандом":
        if_choice_is_random(message)
    if message.text == "Закончить игру":
        game_is_end(message)


'''тут человек вводит свое имя, пол и возраст'''


def process_name_step(message):
    try:
        chat_id = message.chat.id
        name = message.text
        user = User(name)
        users[chat_id] = user
        msg = bot.send_message(message.chat.id, 'Сколько лет игроку')
        bot.register_next_step_handler(msg, process_age_step)
    except Exception as e:
        bot.reply_to(message, 'Что-то пошло не по плану!')


def process_age_step(message):
    try:
        chat_id = message.chat.id
        age = message.text
        if not age.isdigit():
            msg = bot.send_message(message.chat.id, 'Пожалуйста, напишите свой возраст цифрой!')
            bot.register_next_step_handler(msg, process_age_step)
            return
        user = users[chat_id]
        user.age = age
        keyboard_sex = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        keyboard_sex.add('Male', 'Female')
        msg = bot.send_message(message.chat.id, 'Выберите пол:', reply_markup=keyboard_sex)
        bot.register_next_step_handler(msg, process_sex_step)
    except Exception as e:
        bot.reply_to(message, 'Что-то пошло не по плану!')


def process_sex_step(message):
    global user
    try:
        chat_id = message.chat.id
        sex = message.text
        user = users[chat_id]
        if (sex == u'Male') or (sex == u'Female'):
            user.sex = sex
        else:
            raise Exception('Такого варианта не было...')
        db_table_val(message.chat.id, user.name, user.sex, user.age)
    except Exception as e:
        bot.reply_to(message, 'Что-то пошло не по плану!')


def db_table_val(user_id, user_name, user_sex, user_age):
    try:
        conn = sqlite3.connect('database_pilid.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (user_id, user_name, user_sex, user_age) VALUES (?, ?, ?, ?)',
                       (user_id, user_name, user_sex, user_age))
        conn.commit()
        bot.send_message(user_id, 'Игрок ' + user.name + ' успешно добавлен')
        keyboard_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Добавить еще одного игрока")
        button2 = types.KeyboardButton("Вернуться в меню")
        button3 = types.KeyboardButton("Играть!")
        keyboard_menu.add(button1, button2)
        keyboard_menu.add(button3)
        bot.send_message(user_id, "Что делаем дальше?", reply_markup=keyboard_menu)
        cursor.close()
    except Exception as e:
        bot.reply_to(user_id, 'Что-то пошло не по плану!')


def process_delete(user_name):
    try:
        conn = sqlite3.connect('database_pilid.db', check_same_thread=False)
        cursor = conn.cursor()
        chat_id = user_name.chat.id
        cursor.execute('DELETE FROM users WHERE user_name = ? AND user_id = ?', (user_name.text, chat_id))
        conn.commit()
        keyboard_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
        bot.send_message(chat_id, 'Игрок ' + user_name.text + ' успешно удален')
        button1 = types.KeyboardButton("Удалить еще одного игрока")
        button2 = types.KeyboardButton("Вернуться в меню")
        button3 = types.KeyboardButton("Играть!")
        keyboard_menu.add(button1, button2)
        keyboard_menu.add(button3)
        bot.send_message(chat_id, "Что делаем дальше?", reply_markup=keyboard_menu)
        cursor.close()
    except Exception as e:
        bot.send_message(user_name.chat.id, 'такого игрока нет!')


def select_all_users(user_name):
    try:
        conn = sqlite3.connect('database_pilid.db', check_same_thread=False)
        cursor = conn.cursor()
        chat_id = user_name.chat.id
        record = cursor.execute(f'SElECT user_name FROM users WHERE user_id = ?', (str(chat_id),)).fetchall()
        bot.send_message(user_name.chat.id, '\n'.join(str(x)[2:-3] for x in record))
        keyboard_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button2 = types.KeyboardButton("Вернуться в меню")
        button3 = types.KeyboardButton("Играть!")
        keyboard_menu.add(button2)
        keyboard_menu.add(button3)
        bot.send_message(chat_id, "Что делаем дальше?", reply_markup=keyboard_menu)
        cursor.close()
    except Exception as e:
        bot.send_message(user_name.chat.id, 'Что-то пошло не по плану!')


def play_game(user_message, i):
    try:
        conn = sqlite3.connect('database_pilid.db', check_same_thread=False)
        cursor = conn.cursor()
        chat_id = user_message.chat.id
        record = cursor.execute(f'SElECT user_name FROM users WHERE user_id = ?', (str(chat_id),)).fetchall()
        number = i % len(record)
        bot.send_message(user_message.chat.id, 'Ход игрока ' + (str(record[number])[2:-3]))
        keyboard_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton("Правда")
        button2 = types.KeyboardButton("Действие")
        button3 = types.KeyboardButton("Рандом")
        button4 = types.KeyboardButton("Вернуться в меню")
        keyboard_menu.add(button1, button2, button3)
        keyboard_menu.add(button4)
        bot.send_message(chat_id, "Выбирай!", reply_markup=keyboard_menu)
        cursor.close()
    except Exception as e:
        bot.send_message(user_message.chat.id, 'Что-то пошло не по плану!')


def if_choice_is_truth(user_message):
    try:
        conn = sqlite3.connect('database_pilid.db', check_same_thread=False)
        cursor = conn.cursor()
        chat_id = user_message.chat.id
        record = cursor.execute('select text from truth_or_dare WHERE type_id = 1 order by random() limit 1').fetchall()
        bot.send_message(chat_id, (str(record)[3:-4]))
        keyboard_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button2 = types.KeyboardButton("Перейти к следующему игроку")
        button3 = types.KeyboardButton("Вернуться в меню")
        keyboard_menu.add(button2)
        keyboard_menu.add(button3)
        bot.send_message(chat_id, "Что делаем дальше?", reply_markup=keyboard_menu)
    except Exception as e:
        bot.send_message(user_message.chat.id, 'Что-то пошло не по плану!')


def if_choice_is_dare(user_message):
    try:
        conn = sqlite3.connect('database_pilid.db', check_same_thread=False)
        cursor = conn.cursor()
        chat_id = user_message.chat.id
        record = cursor.execute('select text from truth_or_dare WHERE type_id = 2 order by random() limit 1').fetchall()
        bot.send_message(chat_id, str(record)[3:-4])
        keyboard_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button2 = types.KeyboardButton("Перейти к следующему игроку")
        button3 = types.KeyboardButton("Вернуться в меню")
        keyboard_menu.add(button2)
        keyboard_menu.add(button3)
        bot.send_message(chat_id, "Что делаем дальше?", reply_markup=keyboard_menu)
    except Exception as e:
        bot.send_message(user_message.chat.id, 'Что-то пошло не по плану!')


def if_choice_is_random(user_message):
    try:
        conn = sqlite3.connect('database_pilid.db', check_same_thread=False)
        cursor = conn.cursor()
        chat_id = user_message.chat.id
        record = cursor.execute('select text from truth_or_dare order by random() limit 1').fetchall()
        bot.send_message(chat_id, str(record)[3:-4])
        keyboard_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button2 = types.KeyboardButton("Перейти к следующему игроку")
        button3 = types.KeyboardButton("Вернуться в меню")
        keyboard_menu.add(button2)
        keyboard_menu.add(button3)
        bot.send_message(chat_id, "Что делаем дальше?", reply_markup=keyboard_menu)
    except Exception as e:
        bot.send_message(user_message.chat.id, 'Что-то пошло не по плану!')


def game_is_end(user_message):
    try:
        conn = sqlite3.connect('database_pilid.db', check_same_thread=False)
        cursor = conn.cursor()
        chat_id = user_message.chat.id
        cursor.execute('DELETE FROM users WHERE user_id = ?', (chat_id,))
        conn.commit()
        bot.send_message(user_message.chat.id, 'Ждем тебя снова!')
        bot.send_photo(user_message.chat.id, open('end_photo.jpg', 'rb'))
    except Exception as e:
        bot.send_message(user_message.chat.id, 'Что-то пошло не по плану!')


bot.infinity_polling()