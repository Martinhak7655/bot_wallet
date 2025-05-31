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
        tg_id BYTEA NOT NULL,
        username VARCHAR(100) NOT NULL,
        balance INTEGER DEFAULT 0,
        create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
'''
cursor.execute(create_table)
connection.commit()

def exists_user(tg_id):
    select = '''
        SELECT tg_id FROM users;
    '''
    cursor.execute(select, (tg_id,))
    connection.commit()
    users = cursor.fetchall()
    for (db_id,) in users:
        if bcrypt.checkpw(tg_id, bytes(db_id)):
            return True
        else:
            return False
        
def add_user(tg_id, username):
    id_hashed = bcrypt.hashpw(tg_id, bcrypt.gensalt(rounds=12))

    insert = '''
        INSERT INTO users (tg_id, username) VALUES (%s, %s);
    '''
    cursor.execute(insert, (id_hashed, username,))
    connection.commit()
    return True

@bot.message_handler(commands=["start"])
def start(message):
    username = message.from_user.username
    tg_id = bytes(str(message.from_user.id), "utf-8")
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
    print(call.from_user.id)
    if call.data == "tesnel":
        print(call)
        tg_id = bytes(str(call.from_user.id))

        select = '''
            SELECT tg_id FROM users;
        '''
        cursor.execute(select, (tg_id,))
        connection.commit()
        users = cursor.fetchall()
        for (db_id,) in users:
            if bcrypt.checkpw(tg_id, bytes(db_id)):
                select = '''
                    SELECT * FROM users WHERE tg_id = (%s);
                '''
                cursor.execute(select, (db_id,))
                connection.commit()
                balance = cursor.fetchone()
                print(balance)
                if balance:
                
                    bot.send_message(call.message.chat.id, f"Ձեր հաշվի մնացորդը՝ {balance[3]}")
                    return True
        else:
            return False
    # elif call.data == "avelacnel":
    #     # bot.register_next_step_handler(call.message, avelacnel)
    # elif call.data == "poxancum":
    #     bot.send_message(call.message.chat.id, "Խնդրում եմ գրեք տվյալ մարդու այդին")
    #     # bot.register_next_step_handler(call.message, poxancum)

# def tesnel(message):
#     tg_id = bytes(str(message.from_user.id))

#     select = '''
#         SELECT tg_id FROM users;
#     '''
#     cursor.execute(select, (tg_id,))
#     connection.commit()
#     users = cursor.fetchall()
#     for (db_id,) in users:
#         if bcrypt.checkpw(tg_id, bytes(db_id)):
#             select = '''
#                 SELECT * FROM users WHERE tg_id = (%s);
#             '''
#             cursor.execute(select, (db_id,))
#             connection.commit()
#             balance = cursor.fetchone()
#             print(balance)
#             if balance:
                
#                 bot.reply_to(message, f"Ձեր հաշվի մնացորդը՝ {balance[3]}")
#                 return True
#         else:
#             return False

bot.polling()