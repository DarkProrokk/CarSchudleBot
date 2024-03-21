import requests
import telebot
import config
from database import Intervals, session, Days, User
from handlers import handle_day, send_keyboard, handle_button_click, handle_my_intervals, handle_button_click_decline, handle_start
from admin import handler_admin_all_intervals
from telebot import types

bot = telebot.TeleBot(config.BOT_TOKEN, skip_pending=True)


@bot.message_handler(commands=["new"])
def handle_day_wrapper(message):
    handle_day(message, session)

@bot.message_handler(commands=['start'])
def handle_start_wrapper(message):
    handle_start(message, bot)

@bot.message_handler(commands=['free'])
def send_keyboard_wrapper(message):
    send_keyboard(message, bot)


@bot.callback_query_handler(func=lambda call: call.data.startswith('select_'))
def handle_button_click_wrapper(call):
    handle_button_click(call, session, bot)


@bot.callback_query_handler(func=lambda call: call.data.startswith('decline_'))
def handle_button_click_decline_wrapper(call):
    handle_button_click_decline(call, session, bot)


@bot.message_handler(commands=['my'])
def handle_my_intervals_wrapper(message):
    handle_my_intervals(bot=bot, message=message)

@bot.message_handler(commands=['today'])
def handler_admin_all_intervals_wrapper(message):
    handler_admin_all_intervals(message, bot)
while True:
    try:
        bot.polling(none_stop=True)
        exit()  # для остановки бота через ctrl+c, не удалять!
    except requests.exceptions.ReadTimeout as tmp:
        print(str(tmp))
    except requests.exceptions.SSLError as tmp:
        print(str(tmp))
    except requests.exceptions.ConnectionError as tmp:  # Max retries exceeded with url

        print(str(tmp))
