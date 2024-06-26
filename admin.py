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
    username = get_user_by_tg_id(user_tg_id).tg_username
    interval = get_intervals_by_group_choices(call)
    bot.delete_message(call.message.chat.id, call.message.message_id)
    reply_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    finish_points = ["Не указана фамилия, для изменения фамилии используйте команду /surname", "Директор занял машину"]
    for i in finish_points:
        finish_field = types.KeyboardButton(i)
        reply_markup.add(finish_field)
    bot.register_next_step_handler(bot.send_message(call.message.chat.id, f"Выбранный интервал: \n"
                                                                          f"{interval.departure_point} - {interval.finish_point} \n"
                                                                          "Выберете или напишите причину отмены:",
                                                    reply_markup=reply_markup),
                                   admin_decline_cause,
                                   interval.departure_point, interval.finish_point, group_id, user_tg_id)


def admin_decline_cause(message: types.Message, departure_point: str, finish_point: str, group_id, user_tg_id):
    reply_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    finish_points = ["Да", "Нет"]
    for i in finish_points:
        finish_field = types.KeyboardButton(i)
        reply_markup.add(finish_field)
    bot.register_next_step_handler(
        bot.send_message(message.chat.id, f"Отменить интервал {departure_point} - {finish_point} с причиной: \n"
                                          f"{message.text}?", reply_markup=reply_markup), admin_decline_accept,
        group_id, user_tg_id, message.text,
        departure_point, finish_point)


def admin_decline_accept(message: types.Message, group_id, user_tg_id, cause, departure_point, finish_point):
    if message.text == "Да":
        interval_decliner_by_group(group_id)
        username = get_user_by_tg_id(user_tg_id).tg_username
        bot.send_message(message.chat.id, f"Интервал ||{departure_point} - {finish_point} ||"
                                          f"отменён, для уточнения причины напишите пользователю @{username} \n"
                                          f"Посмотреть занятое расписание на сегодняшний день можно при помощи команды"
                                          f" /today")
        bot.send_message(user_tg_id, f"Интервал ||{departure_point} - {finish_point}|| отменён c причиной:\n{cause}")
    elif message.text == "Нет":
        admin_key_board()
    else:
        bot.register_next_step_handler(bot.send_message(message.chat.id, "Введите Да или Нет"),
                                       admin_decline_accept(message, group_id, user_tg_id, cause, departure_point,
                                                            finish_point))


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
