import time
from telebot import TeleBot, types

import utils
from commands import menu_command_handler
from call_types import CallTypes

from backend.models import BotUser
from backend.templates import Messages, Keys
from backend.tasks import update_bonus_for_user
from backend import ro_api


def registration_state_handler(bot: TeleBot, message):
    name = message.text
    chat_id = message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    rem_id = ro_api.create_new_client(user.phone_number, name)
    user.rem_id = rem_id
    user.name = name
    user.bot_state = BotUser.State.NOTHING
    user.save()
    menu_command_handler(bot, message)


def open_orders_callback_query_handler(bot: TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    orders = ro_api.get_client_open_orders(user.rem_id)
    text = utils.text_to_fat(Keys.OPEN_ORDERS) + '\n\n'
    for order in orders:
        notes = [order.kindof_good, order.brand,
                 order.model, order.appearance,
                 order.malfunction]
        description = ', '.join(filter(lambda s: s, notes))
        order_info = Messages.ORDER_INFO.format(
            id=order.id,
            description=description,
            status=order.status.name,
            created=time.ctime(order.created_at / 1000),
            estimated_cost=order.estimated_cost,
            estimated_done_at=time.ctime(order.estimated_done_at / 1000),
        )
        text += order_info + '\n\n'

    keyboard = types.InlineKeyboardMarkup()
    back_button = utils.make_inline_button(
        text=Keys.MENU,
        CallType=CallTypes.Menu,
    )
    contact_administrator_button = types.InlineKeyboardButton(
        text=Keys.CONTACT_ADMINISTRATOR,
        url='https://t.me/NaZaR_IO',
    )
    keyboard.add(contact_administrator_button)
    keyboard.add(back_button)
    bot.send_message(chat_id, text,
                     reply_markup=keyboard)
    bot.delete_message(chat_id, call.message.id)


def referal_program_callback_query_handler(bot: TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    bot_username = bot.get_me().username
    referal_link = f'https://t.me/{bot_username}/?start={user.phone_number}'
    text = Messages.REFERAL_PROGRAM.format(
        referals_count=user.referals.count(),
        bonus=user.bonus,
        cashback_bonus_percentage=user.cashback_bonus_percentage,
        referals_bonus_percentage=user.referals_bonus_percentage,
        referal_link=utils.text_to_code(referal_link),
    )
    keyboard = types.InlineKeyboardMarkup()
    recalc_bonus_button = utils.make_inline_button(
        text=Keys.RECALC_BONUS,
        CallType=CallTypes.RecalcBonus,
    )
    referals_button = utils.make_inline_button(
        text=Keys.REFERALS,
        CallType=CallTypes.Referals,
    )
    back_button = utils.make_inline_button(
        text=Keys.BACK,
        CallType=CallTypes.Menu,
    )
    keyboard.add(recalc_bonus_button)
    keyboard.add(referals_button)
    keyboard.add(back_button)
    bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=call.message.id,
        reply_markup=keyboard,
    )


def recalc_bonus_callback_query_handler(bot: TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    update_bonus_for_user(user)
    bot.answer_callback_query(callback_query_id=call.id,
                              text=Messages.RECALC_BONUS_SUCCESS,
                              show_alert=True)
    referal_program_callback_query_handler(bot, call)


def referals_callback_query_handler(bot: TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    text = utils.text_to_fat(Keys.REFERALS) + '\n\n'
    for index, referal_user in enumerate(user.referals.all(), 1):
        created = referal_user.created.strftime('%Y-%m-%d %H:%M')
        text += Messages.REFERAL_INFO.format(
            index=index,
            name=referal_user.name,
            created=utils.text_to_code(created),
        ) + '\n\n'

    back_button = utils.make_inline_button(
        text=Keys.BACK,
        CallType=CallTypes.ReferalProgram,
    )
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(back_button)
    bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=call.message.id,
        reply_markup=keyboard,
    )


def contacts_callback_query_handler(bot: TeleBot, call):
    chat_id = call.message.chat.id
    text = Messages.CONTACTS
    back_button = utils.make_inline_button(
        text=Keys.BACK,
        CallType=CallTypes.Menu,
    )
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(back_button)
    bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=call.message.id,
        reply_markup=keyboard,
    )
