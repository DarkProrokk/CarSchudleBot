from telebot import types
from tools import get_user_by_tg_id, interval_decliner_by_group, get_intervals_by_group_choices
from bot_init import bot
from kb import admin_key_board, admin_choice_keyboard


def handler_admin_all_intervals(message: types.Message):
    tg_id = message.chat.id
    user = get_user_by_tg_id(tg_id)
    if user.is_admin:
        bot.send_message(message.chat.id, "Выберете интервал:",
                         reply_markup=admin_key_board())
    else:
        bot.send_message(message.chat.id, "Недостаточно прав для использования этой команды")


def handle_admin_choice(call: types.CallbackQuery):
    group_id = int(call.data.split('_')[1])
    user_tg_id = int(call.data.split('_')[2])
    tg_id = call.from_user.id
    user = get_user_by_tg_id(tg_id)
    if user.is_admin:
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      reply_markup=admin_choice_keyboard(group_id, user_tg_id))
    else:
        bot.send_message(call.message.chat.id, "Недостаточно прав для использования этой команды")


def handle_admin_choice_dicline(call: types.CallbackQuery):
    group_id = int(call.data.split('_')[1])
    user_tg_id = int(call.data.split('_')[2])
    interval = get_intervals_by_group_choices(call)
    interval_decliner_by_group(group_id)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(user_tg_id, f"Интервал {interval.departure_point} - {interval.finish_point} отменен")
    bot.send_message(call.message.chat.id, f"Интервал {interval.departure_point} - {interval.finish_point} отменён")


def handle_admin_choice_ready(call: types.CallbackQuery):
    user_tg_id = int(call.data.split('_')[2])
    interval = get_intervals_by_group_choices(call)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Сообщение отправлено")
    bot.send_message(user_tg_id,
                     f"Водитель по заявке | {interval.departure_point} - {interval.finish_point} | готов ")


def handle_admin_choice_late(call: types.CallbackQuery):
    user_tg_id = int(call.data.split('_')[2])
    interval = get_intervals_by_group_choices(call)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.send_message(call.message.chat.id, "Сообщение отправлено")
    bot.send_message(user_tg_id,
                     f"Водитель по заявке | {interval.departure_point} - {interval.finish_point} | задерживается ")
