import telebot
import psycopg2
import bcrypt
from telebot import types

connection = psycopg2.connect(
    host="localhost",
    database="botwallet",
    user="postgres",
    password="MH2012"
)
cursor = connection.cursor()

BOT_TOKEN = "8046691167:AAHYyMtVjpFHnlycQ_G3sB1AWJAV0clZVmE"
bot = telebot.TeleBot(BOT_TOKEN)

create_table = '''
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        tg_id VARCHAR(100) NOT NULL,
        username VARCHAR(100) NOT NULL,
        balance INTEGER DEFAULT 0,
        create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
'''
cursor.execute(create_table)
connection.commit()

def exists_user(tg_id):
    select = '''
        SELECT * FROM users WHERE tg_id = (%s);
    '''
    cursor.execute(select, (tg_id,))
    connection.commit()
    users = cursor.fetchone()
    if users:
        return True
        
def add_user(tg_id, username):
    insert = '''
        INSERT INTO users (tg_id, username) VALUES (%s, %s);
    '''
    cursor.execute(insert, (tg_id, username,))
    connection.commit()
    return True

def get_balance(tg_id):
    select = '''
        SELECT * FROM users WHERE tg_id = (%s);
    '''
    cursor.execute(select, (tg_id,))
    connection.commit()
    users = cursor.fetchone()
    return users[3]


@bot.message_handler(commands=["start"])
def start(message):
    username = message.from_user.username
    tg_id = str(message.from_user.id)
    if exists_user(tg_id):
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Տեսնել իմ հաշիվը", callback_data="tesnel")
        btn2 = types.InlineKeyboardButton("Ավելացնել գումար իմ հաշվին", callback_data="avelacnel")
        btn3 = types.InlineKeyboardButton("Փոխանցում կատարել", callback_data="poxancum")
        markup.add(btn1, btn2, btn3)
        bot.reply_to(message, "Խնդրում եմ ընտրեք կոճակը", reply_markup=markup)
    else:
        add_user(tg_id, username)
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Տեսնել իմ հաշիվը", callback_data="tesnel")
        btn2 = types.InlineKeyboardButton("Ավելացնել գումար իմ հաշվին", callback_data="avelacnel")
        btn3 = types.InlineKeyboardButton("Փոխանցում կատարել", callback_data="poxancum")
        markup.add(btn1, btn2, btn3)
        bot.reply_to(message, "Խնդրում եմ ընտրեք կոճակը", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = str(call.from_user.id)
    if call.data == "tesnel":
        bot.send_message(call.message.chat.id, f"Ձեր հաշվի մնացորդը՝ {get_balance(user_id)} դրամ")
    elif call.data == "avelacnel":
        bot.send_message(call.message.chat.id, "Խնդրում եմ գրեք գումարի չափը")
        bot.register_next_step_handler(call.message, avelacnel)

def avelacnel(message):
    user_id = str(message.from_user.id)
    sum = int(message.text)

    if sum <= 100:
        bot.reply_to(message, "Գումարի չափը պետք է 100 դրամից մեծ լինի")
    else:
        update = '''
            UPDATE users SET balance = (%s) WHERE tg_id = (%s);
        '''
        cursor.execute(update, (get_balance(user_id) + sum, user_id))
        connection.commit()
        bot.reply_to(message, "Ձեր գումարը ավելացվեց ձեր հաշվին")

bot.polling()