import datetime
from telebot import TeleBot, types

from django.utils import timezone

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
    bot.delete_message(chat_id, call.message.id)
    back_button = utils.make_inline_button(
        text=Keys.MENU,
        CallType=CallTypes.Menu,
    )
    contact_administrator_button = types.InlineKeyboardButton(
        text=Keys.CONTACT_ADMINISTRATOR,
        url=Messages.LINK_ADMINISTRATOR,
    )
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(contact_administrator_button)
    keyboard.add(back_button)
    text = Messages.WAITING_FOR_OPEN_ORDERS.format(name=user.name)
    message_id = bot.send_message(chat_id, text,
                                  reply_markup=keyboard).id

    orders = ro_api.get_client_open_orders(user.phone_number)
    text = utils.text_to_fat(Keys.OPEN_ORDERS) + '\n\n'
    for order in orders:
        notes = [order.kindof_good, order.brand,
                 order.model, order.appearance,
                 order.malfunction]
        description = ', '.join(filter(lambda s: s, notes))
        tmp_order = dict(order)
        tmp_order.pop('id')
        tmp_order.pop('status', '')
        tmp_order.pop('estimated_cost', '')
        tmp_order.pop('estimated_done_at', '')
        created_at = datetime.datetime.fromtimestamp(order.created_at / 1000)
        estimated_done_at = datetime.datetime.fromtimestamp(
            order.estimated_done_at / 1000)
        order_info = Messages.ORDER_INFO.format(
            id=order.id,
            description=description,
            status=order.status.name,
            created=created_at.strftime('%d %B %Y в %H:%M'),
            estimated_cost=order.estimated_cost,
            estimated_done_at=estimated_done_at.strftime('%d %B %Y в %H:%M'),
            **tmp_order,
        )
        text += order_info + '\n\n'

    bot.edit_message_text(
        chat_id=chat_id,
        text=text,
        message_id=message_id,
        reply_markup=keyboard,
    )


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
    if (timezone.now() - user.bonus_updated).total_seconds() >= 3600:
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
        disable_web_page_preview=True,
    )


def discounts_callback_query_handler(bot: TeleBot, call):
    chat_id = call.message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    text = Messages.DISCOUNTS.format(name=user.name, bonus=user.bonus)
    contact_administrator_button = types.InlineKeyboardButton(
        text=Keys.CONTACT_ADMINISTRATOR,
        url=Messages.LINK_ADMINISTRATOR,
    )
    back_button = utils.make_inline_button(
        text=Keys.BACK,
        CallType=CallTypes.Menu,
    )
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(contact_administrator_button)
    keyboard.add(back_button)
    bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=call.message.id,
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )
