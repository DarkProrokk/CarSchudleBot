import datetime

from database import session, Days, Intervals, User
from datetime import time, date
from telebot import types
from tools import get_user_by_tg_id, interval_validator, interval_cansalled
from sqlalchemy.orm import Session
import schedule
import time as t
from bot_init import bot

current_date = date.today()

timers = {}


def new_day(session: Session):
    next_day = current_date
    if session.query(Days).filter(Days.date == next_day).first():
        print("meow")
    else:
        new_day = Days(date=next_day)
        session.add(new_day)
        start_time = time(8, 0)
        session.commit()
        while start_time <= time(17, 00):
            minutes = start_time.minute + 30
            hours_to_add = minutes // 60
            new_minutes = minutes % 60
            end_time = time((start_time.hour + hours_to_add) % 24, new_minutes)
            new_time_slot = Intervals(time_start=start_time, time_finish=end_time, day=new_day.id)
            session.add(new_time_slot)
            session.commit()
            start_time = end_time
        bot.send_message("879977403", f"Новый день({next_day}) создан")


def mark_intervals_not_busy(intervals, session):
    for interval in intervals:
        interval.is_selected = False
    session.commit()


def handle_day(message, sess):
    new_day(sess)
    # schedule.every().day.at("18:00").do(lambda: new_day(session))
    # schedule.every(5).seconds.at("18:00").do(lambda: new_day(session))
    # while True:
    #     schedule.run_pending()
    #     t.sleep(1)


def key_board_generator(user: User = None, message: types.Message = None):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    curr_date = session.query(Days).filter(Days.date == current_date).first()
    if user:
        time_slots = session.query(Intervals).order_by(Intervals.id).filter(Intervals.day == curr_date.id,
                                                                            Intervals.user == user.id,
                                                                            Intervals.time_finish > datetime.datetime.now().time()).all()
    else:
        time_slots = session.query(Intervals).filter(Intervals.day == curr_date.id, Intervals.busy == False,
                                                     Intervals.time_finish > datetime.datetime.now().time()).order_by(
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
        interval_text = (
            f"{start_time} {end_time} {time_slot.departure_point + '-' if time_slot.departure_point else ''}"
            f" {time_slot.finish_point if time_slot.finish_point else ''}")
        keyboard.row(types.InlineKeyboardButton(interval_text, callback_data=f"{data}{time_slot.id}"))
    return keyboard


def key_board_redraw(user: User = None, message: str = None):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    curr_date = session.query(Days).filter(Days.date == current_date).first()
    time_query = session.query(Intervals).filter(Intervals.day == curr_date.id)
    if user:
        time_query = time_query.filter(Intervals.user == user.id, Intervals.busy == True,
                                       Intervals.time_finish > datetime.datetime.now().time())
    else:
        time_query = time_query.filter(Intervals.is_selected == False, Intervals.busy == False,
                                       Intervals.time_finish > datetime.datetime.now().time())
    data = "select_" if message and message.startswith("select_") else "decline_" if message and message.startswith(
        "decline_") else ""
    time_slots = time_query.order_by(Intervals.id).all()
    for time_slot in time_slots:
        start_time = time_slot.time_start.strftime("%H:%M")
        end_time = time_slot.time_finish.strftime("%H:%M")
        interval_text = (
            f"{start_time} {end_time} {time_slot.departure_point + '-' if time_slot.departure_point else ''}"
            f" {time_slot.finish_point if time_slot.finish_point else ''}")
        keyboard.add(types.InlineKeyboardButton(interval_text, callback_data=f"{data}{time_slot.id}"))
    if not user:
        keyboard.add(types.InlineKeyboardButton("Продолжить", callback_data=f"accept_"))
    return keyboard


def send_keyboard(message):
    tg_id = message.chat.id
    if not (session.query(User).filter(User.tg_id == str(tg_id)).first()):
        user = User(tg_id=tg_id, tg_username=message.chat.username, is_admin=False)
        session.add(user)
        session.commit()
    bot.send_message(message.chat.id, "Выберите временной интервал:",
                     reply_markup=key_board_generator(message=message))


def handle_button_click(call, sess):
    interval_id = int(call.data.split('_')[1])  # предполагается, что callback_data - это ID интервала
    interval = sess.get(Intervals, interval_id)
    if interval.busy == True or interval.is_selected == True:
        bot.send_message(call.message.chat.id, "Выбранный период занят")
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=key_board_redraw(message=call.data))
    else:
        tg_id = call.from_user.id
        user = get_user_by_tg_id(tg_id)
        interval.is_selected = True
        interval.user = user.id
        sess.commit()
        # intervals = sess.query(Intervals).filter(Intervals.user == user.id, Intervals.is_selected == True).all()
        # timers[call.message.chat.id] = threading.Timer(60, mark_intervals_not_busy, args=[intervals, session])
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=key_board_redraw(message=call.data))


def handle_button_click_decline(call, sess):
    interval_id = int(call.data.split('_')[1])  # предполагается, что callback_data - это ID интервала
    interval = sess.get(Intervals, interval_id)
    tg_id = call.from_user.id
    user = get_user_by_tg_id(tg_id)
    interval.busy = False
    interval.user = None
    interval.finish_point = None
    interval.departure_point = None
    sess.commit()
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=key_board_redraw(user, call.data))


def handle_my_intervals(message: types.Message, ):
    user = get_user_by_tg_id(message.chat.id)
    bot.send_message(message.chat.id, "Нажмите на интервалы, которые хотите отменить:",
                     reply_markup=key_board_generator(user, message=message))


def handle_start(message: types.Message):
    text = ("Привет! Этот бот создан для предварительной записи на служебную машину МИАЦ \n"
            "Для того, чтобы посмотреть свободные интервалы нажмите на кнопку /free \n"
            "Для того, чтобы посмотреть выбранные Вами интервалы на сегодняшний день нажмите на кнопку /my")
    msg = bot.send_message(message.chat.id, text)
    user = get_user_by_tg_id(message.chat.id)
    if user:
        bot.send_message(message.chat.id, text)
    else:
        pass


def handle_button_accept(call: types.CallbackQuery, sess):
    user = get_user_by_tg_id(call.message.chat.id)
    intervals = session.query(Intervals).filter(Intervals.user == user.id, Intervals.is_selected == True).order_by(
        Intervals.time_start).all()
    if interval_validator(intervals):
        message_text = "Выберите или введите место отправления"
        reply_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        input_field = types.KeyboardButton("Советская")
        input_field2 = types.KeyboardButton("Истомина")
        reply_markup.add(input_field)
        reply_markup.add(input_field2)
        msg = bot.send_message(call.message.chat.id, message_text, reply_markup=reply_markup)
        # Отправляем сообщение с клавиатурами
        bot.register_next_step_handler(msg, add_departure_point, sess, intervals)
    else:
        interval_cansalled(intervals)
        bot.send_message(call.message.chat.id, "Нужно выбирать последовательный интервалы")


def add_departure_point(message, session: Session, intervals):
    for interval in intervals:
        interval.departure_point = message.text
    session.commit()
    reply_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    finish_points = ["МЗХК", "Правительство", "ФСТЭК", "Военкомат", "Казначейство"]
    for i in finish_points:
        finish_field = types.KeyboardButton(i)
        reply_markup.add(finish_field)
    msg = bot.send_message(message.chat.id, "Выберите или введите место назначения", reply_markup=reply_markup)
    bot.register_next_step_handler(msg, add_finish_point)


def add_finish_point(message):
    user = get_user_by_tg_id(message.chat.id)
    intervals = session.query(Intervals).filter(Intervals.user == user.id, Intervals.is_selected == True).all()
    for interval in intervals:
        interval.finish_point = message.text
    session.commit()
    text = 'Ваши интервалы: \n'
    for interval in intervals:
        start_time = interval.time_start.strftime("%H:%M")
        end_time = interval.time_finish.strftime("%H:%M")
        text += f"{start_time} - {end_time} {interval.departure_point} - {interval.finish_point} \n"
    reply_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    finish_points = ["Да", "Нет"]
    for i in finish_points:
        finish_field = types.KeyboardButton(i)
        reply_markup.add(finish_field)
    bot.send_message(message.chat.id, text)
    msg = bot.send_message(message.chat.id, "Всё верно?", reply_markup=reply_markup)
    bot.register_next_step_handler(msg, accept_intervals, session)


def accept_intervals(message, session: Session):
    if message.text == 'Да':
        user = get_user_by_tg_id(message.chat.id)
        intervals = session.query(Intervals).filter(Intervals.user == user.id, Intervals.is_selected == True).all()
        for interval in intervals:
            interval.busy = True
            interval.is_selected = False
        session.commit()
        bot.send_message(message.chat.id, "Интервалы записаны")
