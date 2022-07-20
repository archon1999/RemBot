import time

from telebot import TeleBot, types

from backend.templates import Messages, Keys
from backend.models import BotUser
from backend import ro_api

import utils
from call_types import CallTypes


def start_command_handler(bot: TeleBot, message):
    chat_id = message.chat.id
    if not BotUser.objects.filter(chat_id=chat_id).exists():
        user = BotUser.objects.create(chat_id=chat_id)
        if len(message.text.split()) == 2:
            from_phone_number = message.text.split()[-1]
            if (from_user := BotUser.objects.filter(
                    phone_number=from_phone_number)):
                user.from_user = from_user
                user.save()

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(types.KeyboardButton(text=Keys.SEND_CONTACT,
                                          request_contact=True))
        bot.send_message(chat_id, Messages.START_COMMAND,
                         reply_markup=keyboard)
    else:
        menu_command_handler(bot, message)


def menu_command_handler(bot: TeleBot, message):
    chat_id = message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    if user.rem_id:
        client = ro_api.get_client_by_phone_number(user.phone_number)
        client_info = Messages.CLIENT_INFO.format(
            id=client.id,
            name=client.name,
            phone=client.phone[0],
            email=client.email,
            address=client.address,
            registration_date=time.ctime(client.created_at // 1000),
        )
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(Keys.MENU)
        bot.send_message(chat_id, client_info,
                         reply_markup=keyboard)

        if ro_api.get_client_open_orders(user.rem_id):
            bot.send_message(chat_id, Messages.HAS_OPEN_ORDERS)

    open_orders_button = utils.make_inline_button(
        text=Keys.OPEN_ORDERS,
        CallType=CallTypes.OpenOrders,
    )
    contact_administrator_button = types.InlineKeyboardButton(
        text=Keys.CONTACT_ADMINISTRATOR,
        url='https://t.me/NaZaR_IO',
    )
    consultation_with_master_button = types.InlineKeyboardButton(
        text=Keys.CONSULTATION_WITH_MASTER,
        url='https://t.me/NaZaR_IO',
    )
    referal_program_button = utils.make_inline_button(
        text=Keys.REFERAL_PROGRAM,
        CallType=CallTypes.ReferalProgram,
    )
    contacts_button = utils.make_inline_button(
        text=Keys.CONTACTS,
        CallType=CallTypes.Contacts,
    )
    keyboard = types.InlineKeyboardMarkup()
    if user.rem_id:
        keyboard.add(open_orders_button)

    keyboard.add(contact_administrator_button)
    keyboard.add(consultation_with_master_button)
    if user.rem_id:
        keyboard.add(referal_program_button)

    keyboard.add(contacts_button)
    bot.send_message(chat_id, utils.text_to_fat(Keys.MENU),
                     reply_markup=keyboard)


def menu_callback_query_handler(bot: TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    open_orders_button = utils.make_inline_button(
        text=Keys.OPEN_ORDERS,
        CallType=CallTypes.OpenOrders,
    )
    contact_administrator_button = types.InlineKeyboardButton(
        text=Keys.CONTACT_ADMINISTRATOR,
        url='https://t.me/NaZaR_IO',
    )
    consultation_with_master_button = types.InlineKeyboardButton(
        text=Keys.CONSULTATION_WITH_MASTER,
        url='https://t.me/NaZaR_IO',
    )
    referal_program_button = utils.make_inline_button(
        text=Keys.REFERAL_PROGRAM,
        CallType=CallTypes.ReferalProgram,
    )
    contacts_button = utils.make_inline_button(
        text=Keys.CONTACTS,
        CallType=CallTypes.Contacts,
    )
    keyboard = types.InlineKeyboardMarkup()
    if user.rem_id:
        keyboard.add(open_orders_button)

    keyboard.add(contact_administrator_button)
    keyboard.add(consultation_with_master_button)
    if user.rem_id:
        keyboard.add(referal_program_button)

    keyboard.add(contacts_button)
    bot.edit_message_text(
        chat_id=chat_id,
        text=utils.text_to_fat(Keys.MENU),
        message_id=call.message.id,
        reply_markup=keyboard,
    )
