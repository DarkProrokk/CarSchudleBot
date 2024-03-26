from telebot import types
from tools import get_user_by_tg_id
from bot_init import bot
from kb import admin_key_board


def handler_admin_all_intervals(message: types.Message):
    tg_id = message.chat.id
    user = get_user_by_tg_id(tg_id)
    if user.is_admin:
        bot.send_message(message.chat.id, "Нажмите на интервалы, которые хотите отменить:",
                         reply_markup=admin_key_board())
    else:
        bot.send_message(message.chat.id, "Недостаточно прав для использования этой команды")
