import telebot
from telebot import types
import random
TOKEN = "8052013665:AAFoRy6Bq0gIXpNKySYgGrdksiIfdOw5G8Q"
bot = telebot.TeleBot(TOKEN)
user_state = {}
@bot.message_handler(commands=['start'])
def play_start(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Да", callback_data="about")
    markup.add(btn1)
    bot.send_message(message.chat.id, "Привет! Я бот-игра 'Угадай число'.\nХочешь попробовать?", reply_markup=markup)
    user_state[message.from_user.id] = {"state": "notPlaying"}

@bot.message_handler(commands=['stop'])
def stop_start(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,f'Игра остановлена')
    user_state[chat_id] = {"state": "notPlaying"}
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    if chat_id not in user_state:
            user_state[chat_id] = {"state": "notPlaying"} 
    state_info = user_state[chat_id]
    state = state_info["state"]
    if call.data == "about" and state == "notPlaying":
        #Кнопки для режима гри
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("😁Легкий", callback_data="Легкий"),
            types.InlineKeyboardButton("🙂Нормальный", callback_data="Нормальный")
        )
        markup.add(
            types.InlineKeyboardButton("😡Тяжелый", callback_data="Тяжелый"),
            types.InlineKeyboardButton("👿Невожможно", callback_data="Невожможно")
        )
        bot.send_message(call.message.chat.id, "Вибери режим", reply_markup=markup)
    elif call.data in ["Легкий", "Нормальный", "Тяжелый", "Невожможно"] and state == "notPlaying":
        user_state[chat_id]['state'] = 'Playing'
        user_state[chat_id]['mod'] = call.data
        playing(chat_id)
    elif state == "Playing":
        mod = user_state[chat_id]['mod']
        bot.send_message(chat_id,f'Вы уже играете, в режиме {mod}!\nЕсли хочешь остановить игру введи команду /stop')
def playing(chat_id):
    difficulty =  user_state[chat_id]['mod']
    max_X = 0
    if difficulty == "Легкий":
        user_state[chat_id]['Hp'] = 3
        max_X = 10
    elif difficulty == "Нормальный":
        user_state[chat_id]['Hp'] = 3
        max_X = 15
    elif difficulty == "Тяжелый":
        user_state[chat_id]['Hp'] = 4
        max_X = 25
    elif difficulty == "Невожможно":
        user_state[chat_id]['Hp'] = 5
        max_X = 100
    number = random.randint(1, max_X)
    user_state[chat_id]['Number'] = number
    user_state[chat_id]['list_podzkazka'] = list(range(1, max_X + 1))
    bot.send_message(chat_id, f'Начинаем игру!\nРежим: {user_state[chat_id]['mod']}\nЯ загадал число от 1 до {max_X}\nУ тебя {user_state[chat_id]['Hp']} HP')


@bot.message_handler()
def play(message):

    chat_id = message.chat.id
    if chat_id not in user_state:
        user_state[chat_id] = {"state": "notPlaying"}
    state = user_state[chat_id]['state']
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Сыграть еще", callback_data="about"))
    if state == "Playing":
        if not message.text.isdigit():
            bot.send_message(chat_id, "Введи число!")
            return
        else:
            numbers = user_state[chat_id]['Number']
            list_ = user_state[chat_id]['list_podzkazka']
            if int(message.text) <= len(list_) and int(message.text) >= 1:
                if int(message.text.lower()) == numbers:
                    user_state[chat_id]['state'] = "notPlaying"
                    bot.send_message(chat_id, f'Ты победиль!')
                    win_score(chat_id)
                elif  int(message.text) != numbers and user_state[chat_id]['Hp'] >= 0:
                    user_state[chat_id]['Hp'] -= 1
                    if user_state[chat_id]['Hp'] == 0:
                        bot.send_message(chat_id,f'Проиграл, я загадал {numbers}', reply_markup=markup)
                        user_state[chat_id]['state'] = "notPlaying"                       
                    else:
                       bot.send_message(chat_id, f'Неугадал, у тебя осталось {user_state[chat_id]['Hp']} жизни')

                     
            else:
                bot.send_message(chat_id, f'Введи число в радиусе {list_[0]} - {list_[-1]}')
    elif state == "notPlaying":
        bot.send_message(chat_id, f'Чтобы начать игру, напишите /start')
def win_score(chat_id):
    d = 1    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Сыграть еще", callback_data="about"))
    if user_state[chat_id]['mod'] == "Легкий":
        d = 1
    elif user_state[chat_id]['mod'] == "Нормальный":
        d = 1.5
    elif user_state[chat_id]['mod'] == "Тяжелый":
        d = 3
    elif user_state[chat_id]['mod'] == "Невожможно":
        d = 4
    score_add = 2 * d * user_state[chat_id]['Hp']
    bot.send_message(chat_id, f'Заработаны очки: {score_add}', reply_markup=markup)

bot.polling(none_stop=True)