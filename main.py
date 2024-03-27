import time

import requests
from database import Session
from bot_init import bot
from admin import (handler_admin_all_intervals, handle_admin_choice, handle_admin_choice_late,
                   handle_admin_choice_ready, handle_admin_choice_dicline)
from handlers import handle_day, send_keyboard, handle_button_click, handle_my_intervals, handle_button_click_decline, \
    handle_start, handle_button_accept
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)


@bot.message_handler(commands=["new"])
def handle_day_wrapper(message):
    handle_day()


@bot.message_handler(commands=['start'])
def handle_start_wrapper(message):
    logging.info(f"Пользователь {message.from_user.username} активировал бота")
    handle_start(message)


@bot.message_handler(commands=['free'])
def send_keyboard_wrapper(message):
    send_keyboard(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('select_'))
def handle_button_click_wrapper(call):
    with Session() as session:
        handle_button_click(call, session)


@bot.callback_query_handler(func=lambda call: call.data.startswith('decline_'))
def handle_button_click_decline_wrapper(call):
    handle_button_click_decline(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('declineA_'))
def handle_button_click_decline_wrapper(call):
    handle_admin_choice_dicline(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('accept_'))
def handle_button_accept_wrapper(call):
    with Session() as session:
        handle_button_accept(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('choice_'))
def handle_button_accept_wrapper(call):
    handle_admin_choice(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('ready_'))
def handle_button_accept_wrapper(call):
    handle_admin_choice_ready(call)


@bot.callback_query_handler(func=lambda call: call.data.startswith('late_'))
def handle_button_accept_wrapper(call):
    handle_admin_choice_late(call)


@bot.message_handler(commands=['my'])
def handle_my_intervals_wrapper(message):
    logging.info(f"Пользователь {message.from_user.username} посмотрел активные интервалы")
    handle_my_intervals(message=message)


@bot.message_handler(commands=['today'])
def handler_admin_all_intervals_wrapper(message):
    logging.info(f"Пользователь {message.from_user.username} посмотрел активные за весь день")
    handler_admin_all_intervals(message)


def start_bot():
    try:
        print("Бот работает!")
        bot.polling(none_stop=True)
    except Exception as e:
        logging.info(f"Произошла ошибка {e}")
        time.sleep(5)
        start_bot()


start_bot()
