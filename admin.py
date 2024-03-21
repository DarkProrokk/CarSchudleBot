from telebot import types, TeleBot
from tools import get_user_by_tg_id


def handler_admin_all_intervals(message: types.Message, bot: TeleBot):
    tg_id = message.chat.id
    user = get_user_by_tg_id(tg_id)
    if user.is_admin:
        pass
    else:
        bot.send_message(message.chat.id, "Недостаточно прав для использования этой команды")