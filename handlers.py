from database import session, Days, Intervals, User
from datetime import time, date
from telebot import types
from telebot import TeleBot
from sqlalchemy import Boolean
from tools import get_user_by_tg_id
current_date = date.today()





def handle_day(message, sess):
    if sess.query(Days).filter(Days.date == current_date).first():
        print("meow")
    else:
        new_day = Days(date=current_date)
        sess.add(new_day)
        start_time = time(8, 0)
        sess.commit()
        while start_time <= time(17, 00):
            minutes = start_time.minute + 30
            hours_to_add = minutes // 60
            new_minutes = minutes % 60
            end_time = time((start_time.hour + hours_to_add) % 24, new_minutes)
            new_time_slot = Intervals(time_start=start_time, time_finish=end_time, day=new_day.id)
            sess.add(new_time_slot)
            sess.commit()
            start_time = end_time


def key_board_generator(user: User = None, message: types.Message = None):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    curr_date = session.query(Days).filter(Days.date == current_date).first()
    if user:
        time_slots = session.query(Intervals).order_by(Intervals.id).filter(Intervals.day == curr_date.id,
                                                                            Intervals.user == user.id).all()
    else:
        time_slots = session.query(Intervals).filter(Intervals.day == curr_date.id, Intervals.busy == False).order_by(
            Intervals.id).all()
    data = ""
    if message:
        if message.text == "/free":
            data = "select_"
        elif message.text == "/my":
            data = "decline_"
    for time_slot in time_slots:
        start_time = time_slot.time_start.strftime("%H:%M")
        end_time = time_slot.time_finish.strftime("%H:%M")
        interval_text = f"{start_time} - {end_time}"
        keyboard.add(types.InlineKeyboardButton(interval_text, callback_data=f"{data}{time_slot.id}"))
    return keyboard


def key_board_redraw(user: User = None, message: str = None):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    curr_date = session.query(Days).filter(Days.date == current_date).first()
    if user:
        time_slots = session.query(Intervals).order_by(Intervals.id).filter(Intervals.day == curr_date.id,
                                                                            Intervals.user == user.id).all()
    else:
        time_slots = session.query(Intervals).filter(Intervals.day == curr_date.id, Intervals.busy == False).order_by(
            Intervals.id).all()
    data = ""
    if message:
        if message.startswith("select_"):
            data = "select_"
        elif message.startswith("decline_"):
            data = "decline_"
    for time_slot in time_slots:
        start_time = time_slot.time_start.strftime("%H:%M")
        end_time = time_slot.time_finish.strftime("%H:%M")
        interval_text = f"{start_time} - {end_time}"
        keyboard.add(types.InlineKeyboardButton(interval_text, callback_data=f"{data}{time_slot.id}"))
    return keyboard


def send_keyboard(message, bot):
    tg_id = message.chat.id
    if not (session.query(User).filter(User.tg_id == str(tg_id)).first()):
        user = User(tg_id=tg_id, tg_username=message.chat.username, is_admin=False)
        session.add(user)
        session.commit()
    bot.send_message(message.chat.id, "Выберите временной интервал:",
                     reply_markup=key_board_generator(message=message))


def handle_button_click(call, sess, bot: TeleBot):
    interval_id = int(call.data.split('_')[1])  # предполагается, что callback_data - это ID интервала
    interval = sess.get(Intervals, interval_id)
    if interval.busy == True:
        bot.send_message(call.message.chat.id, "Выбранный период занят")
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=key_board_redraw(message=call.data))
    else:
        tg_id = call.from_user.id
        user = get_user_by_tg_id(tg_id)
        interval.busy = True
        interval.user = user.id
        sess.commit()
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=key_board_redraw(message=call.data))


def handle_button_click_decline(call, sess, bot):
    interval_id = int(call.data.split('_')[1])  # предполагается, что callback_data - это ID интервала
    interval = sess.get(Intervals, interval_id)
    tg_id = call.from_user.id
    user = get_user_by_tg_id(tg_id)
    interval.busy = False
    interval.user = None
    sess.commit()
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=key_board_redraw(user, call.data))


def handle_my_intervals(message: types.Message, bot: TeleBot):
    user = get_user_by_tg_id(message.chat.id)
    bot.send_message(message.chat.id, "Нажмите на интервалы, которые хотите отменить:",
                     reply_markup=key_board_generator(user, message=message))


def handle_start(message: types.Message, bot: TeleBot):
    text = ("Привет! Этот бот создан для предварительной записи на служебную машину МИАЦ \n"
            "Для того, чтобы посмотреть свободные интервалы нажмите на кнопку /free \n"
            "Для того, чтобы посмотреть выбранные Вами интервалы на сегодняшний день нажмите на кнопку /my")
    bot.send_message(message.chat.id, text)
