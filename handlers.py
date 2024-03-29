import datetime
import schedule
from database import session, Days, Intervals, User
from datetime import time
from telebot import types
from tools import get_user_by_tg_id, interval_validator, interval_cancaller, interval_combiner, \
    interval_decliner_by_group, get_current_date, check_characters
from text import TEXT_START, TEXT_HELP
from bot_init import bot
import time as t
from kb import my_key_board
import threading

timers = {}


def mark_intervals_not_selected(user):
    intervals = session.query(Intervals).filter(Intervals.user == user.id, Intervals.is_selected == True).all()
    if int(user.tg_id) in timers:
        del timers[int(user.tg_id)]
    interval_cancaller(intervals)
    session.commit()
    print("Таймер отработал")


def handle_start(message: types.Message):
    user = get_user_by_tg_id(message.chat.id)
    if user:
        bot.send_message(message.chat.id, TEXT_HELP)
    else:
        bot.register_next_step_handler(bot.send_message(message.chat.id, TEXT_START), register_user)


def register_user(message: types.Message):
    user = User(tg_id=message.chat.id, tg_username=message.chat.username, surname=message.text)
    session.add(user)
    session.commit()
    bot.send_message(message.chat.id, "Вы успешно зарегистрированы \n \n" + TEXT_HELP)


# region new_day

def new_day():
    next_day = get_current_date()
    if session.query(Days).filter(Days.date == next_day).first():
        print("meow")
    else:
        new_date = Days(date=next_day)
        session.add(new_date)
        start_time = time(8, 0)
        session.commit()
        while start_time <= time(17, 00):
            minutes = start_time.minute + 30
            hours_to_add = minutes // 60
            new_minutes = minutes % 60
            end_time = time((start_time.hour + hours_to_add) % 24, new_minutes)
            new_time_slot = Intervals(time_start=start_time, time_finish=end_time, day=new_date.id)
            if not start_time == time(13, 00) or start_time == time(13, 30):
                session.add(new_time_slot)
                session.commit()
            start_time = end_time
        bot.send_message("879977403", f"Новый день({next_day}) создан")


def handle_day():
    if session.query(Days).filter(Days.date == get_current_date()).first():
        pass
    else:
        new_day()
    bot.send_message("879977403", "Бот был перезапущен. Функция генерации дня работает.")
    schedule.every().day.at("18:01").do(new_day)
    while True:
        schedule.run_pending()
        print("meowtest")
        t.sleep(20)


# endregion

# region keyboard
def key_board_generator(user: User = None, message: types.Message = None):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    curr_date = session.query(Days).filter(Days.date == get_current_date()).first()
    if user:
        time_slots = (session
                      .query(Intervals)
                      .order_by(Intervals.id)
                      .filter(Intervals.day == curr_date.id, Intervals.user == user.id,
                              Intervals.time_finish > datetime.datetime.now().time()).all())
    else:
        time_slots = session.query(Intervals).filter(Intervals.day == curr_date.id, Intervals.busy == False,
                                                     Intervals.is_selected == False,
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
    curr_date = session.query(Days).filter(Days.date == get_current_date()).first()
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
        keyboard.add(types.InlineKeyboardButton("Отменить все выбранные интервалы", callback_data=f"cancel_"))
    return keyboard


# endregion

# region interval_selector

def handle_button_click(call: types.CallbackQuery, sess):
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
        if call.message.chat.id not in timers:
            t = threading.Timer(120, mark_intervals_not_selected, args=[user])
            t.start()
            timers[call.message.chat.id] = t
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=key_board_redraw(message=call.data))


def handler_cancel_intervals(call: types.CallbackQuery):
    user = get_user_by_tg_id(call.message.chat.id)
    mark_intervals_not_selected(user)
    bot.send_message(call.message.chat.id, "Все выбранные интервалы отменены \n"
                                           "Посмотреть свободные /free")


def handle_button_accept(call: types.CallbackQuery):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    user = get_user_by_tg_id(call.message.chat.id)
    intervals = session.query(Intervals).filter(Intervals.user == user.id, Intervals.is_selected == True).order_by(
        Intervals.time_start).all()
    if interval_validator(intervals):
        interval_combiner(intervals)
        message_text = "Выберите или введите место отправления"
        reply_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        input_field = types.KeyboardButton("Советская")
        input_field2 = types.KeyboardButton("Истомина")
        input_field3 = types.KeyboardButton("Назад")
        reply_markup.add(input_field)
        reply_markup.add(input_field2)
        reply_markup.add(input_field3)
        msg = bot.send_message(call.message.chat.id, message_text, reply_markup=reply_markup)
        # Отправляем сообщение с клавиатурами
        bot.register_next_step_handler(msg, add_departure_point, intervals)
    else:
        interval_cancaller(intervals)
        bot.send_message(call.message.chat.id, "Нужно выбирать последовательный интервалы")


def add_departure_point(message, intervals):
    if check_characters(message.text):
        bot.send_message(message.chat.id, "Введён некорректный адрес")
        interval_cancaller(intervals)
        message.text = "/free"
        send_keyboard(message)
        return
    if message.text == "Назад":
        message.text = "/free"
        interval_cancaller(intervals)
        send_keyboard(message)
        return
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
    intervals = session.query(Intervals).order_by(Intervals.time_start).filter(Intervals.user == user.id,
                                                                               Intervals.is_selected == True).all()
    if check_characters(message.text):
        bot.send_message(message.chat.id, "Введён некорректный адрес")
        interval_cancaller(intervals)
        message.text = "/free"
        send_keyboard(message)
        return
    for interval in intervals:
        interval.finish_point = message.text
    session.commit()
    text = 'Ваши интервалы: \n'
    start_time = intervals[0].time_start.strftime("%H:%M")
    end_time = intervals[-1].time_finish.strftime("%H:%M")
    text += f"{start_time} - {end_time} {intervals[0].departure_point} - {intervals[0].finish_point} \n"
    reply_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    finish_points = ["Да", "Нет"]
    for i in finish_points:
        finish_field = types.KeyboardButton(i)
        reply_markup.add(finish_field)
    bot.send_message(message.chat.id, text)
    msg = bot.send_message(message.chat.id, "Всё верно?", reply_markup=reply_markup)
    bot.register_next_step_handler(msg, accept_intervals)


def accept_intervals(message):
    user = get_user_by_tg_id(message.chat.id)
    intervals = session.query(Intervals).filter(Intervals.user == user.id, Intervals.is_selected == True).all()
    if message.text.startswith('Да'):
        for interval in intervals:
            interval.busy = True
            interval.is_selected = False
        session.commit()
        bot.send_message(message.chat.id, "Интервалы записаны")

    elif message.text.startswith('Нет'):
        interval_cancaller(intervals)
        message.text = "/free"
        send_keyboard(message)
    else:
        bot.register_next_step_handler(bot.send_message(message.chat.id, "Введите Да или Нет"), accept_intervals)


# endregion

def send_keyboard(message):
    tg_id = message.chat.id
    if not (session.query(User).filter(User.tg_id == str(tg_id)).first()):
        user = User(tg_id=tg_id, tg_username=message.chat.username, is_admin=False)
        session.add(user)
        session.commit()
    bot.send_message(message.chat.id,
                     f"Сегодня {get_current_date().day}.{get_current_date().month:02d}\n"
                     "Выберите один или несколько интервалов\n"
                     "Важно! Выбирать нужно последовательные по времени интервалы",
                     reply_markup=key_board_generator(message=message))


def handle_button_click_decline(call):
    group_id = int(call.data.split('_')[1])
    tg_id = call.from_user.id
    user = get_user_by_tg_id(tg_id)
    interval_decliner_by_group(group_id)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  reply_markup=my_key_board(user.id))


def handle_my_intervals(message: types.Message, ):
    user = get_user_by_tg_id(message.chat.id)
    key = my_key_board(user.id)
    bot.send_message(message.chat.id, "Нажмите на интервалы, которые хотите отменить:",
                     reply_markup=key)


def handle_help(message: types.Message):
    bot.send_message(message.chat.id, TEXT_HELP)


def handle_change_surname(message: types.Message):
    bot.send_message(message.chat.id, "Введите фамилию:")
    bot.register_next_step_handler(message, change_surname)


def change_surname(message: types.Message):
    user = get_user_by_tg_id(message.chat.id)
    user.surname = message.text
    session.commit()
    bot.send_message(message.chat.id, f"Фамилия изменена, текущая фамилия: \n"
                                      f"{user.surname}")


def test():
    pass