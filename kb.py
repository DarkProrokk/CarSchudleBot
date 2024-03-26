from telebot import types
from typing import List
from database import Intervals, User
from database import session
from sqlalchemy import func


def my_key_board(user_id) -> types.InlineKeyboardMarkup:
    results = (session.query(Intervals.group_id,
                             func.min(Intervals.time_start).label('min_time_start'),
                             func.max(Intervals.time_finish).label('max_time_finish'), Intervals.departure_point,
                             Intervals.finish_point)
               .filter(Intervals.user == user_id, Intervals.busy == True)
               .group_by(Intervals.group_id, Intervals.departure_point, Intervals.finish_point)
               .order_by('min_time_start')
               .all())
    reply_markup = types.InlineKeyboardMarkup()
    for interval in results:
        text = f'{interval[1].strftime("%H:%M")} - {interval[2].strftime("%H:%M")} - {interval[3]} - {interval[4]}'
        reply_markup.add(types.InlineKeyboardButton(text, callback_data=f"decline_{interval[0]}"))
    return reply_markup


def admin_key_board() -> types.InlineKeyboardMarkup:
    results = (session.query(Intervals.group_id,
                             func.min(Intervals.time_start).label('min_time_start'),
                             func.max(Intervals.time_finish).label('max_time_finish'),
                             Intervals.departure_point,
                             Intervals.finish_point,
                             User.tg_username)
               .select_from(Intervals)
               .join(User, Intervals.user == User.id)  # Join the Intervals and User tables
               .filter(Intervals.busy == True)
               .group_by(Intervals.group_id, Intervals.departure_point, Intervals.finish_point, User.tg_username)
               .order_by('min_time_start')
               .all())
    reply_markup = types.InlineKeyboardMarkup()
    for interval in results:
        text = f'| {interval[1].strftime("%H:%M")} - {interval[2].strftime("%H:%M")} | - | {interval[3]} - {interval[4]} | - @{interval[5]}'
        reply_markup.add(types.InlineKeyboardButton(text, callback_data=f"decline_{interval[0]}"))
    return reply_markup
