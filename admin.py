from telebot import types, TeleBot
from tools import get_user_by_tg_id
from database import session, Intervals, User

def handler_admin_all_intervals(message: types.Message, bot: TeleBot):
    tg_id = message.chat.id
    user = get_user_by_tg_id(tg_id)
    if user.is_admin:
        result = session.query(Intervals, User).join(User).filter(Intervals.busy == True).all()
        text = ""
        for interval, user in result:
            start_time = interval.time_start.strftime("%H:%M")
            end_time = interval.time_finish.strftime("%H:%M")
            text += f"| {start_time} - {end_time} | {interval.departure_point} - {interval.finish_point} | - {user.tg_username}\n"
        bot.send_message(message.chat.id, text)
    else:
        bot.send_message(message.chat.id, "Недостаточно прав для использования этой команды")