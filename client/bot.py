from telebot import TeleBot

import config
import commands
import handlers
from call_types import CallTypes

from backend.models import BotUser
from backend.templates import Messages, Keys
from backend import ro_api, tasks

message_handlers = {
    '/start': commands.start_command_handler,
    '/menu': commands.menu_command_handler,
}

key_handlers = {
    Keys.MENU: commands.menu_command_handler,
}

state_handlers = {
    BotUser.State.REGISTRATION: handlers.registration_state_handler,
}

bot = TeleBot(
    token=config.TOKEN,
    num_threads=3,
    parse_mode='HTML',
)


@bot.message_handler()
def message_handler(message):
    print(message.text)
    if message.chat.type != 'private':
        return

    chat_id = message.chat.id
    if not BotUser.objects.filter(chat_id=chat_id).exists():
        commands.start_command_handler(bot, message)
        return

    user = BotUser.objects.get(chat_id=chat_id)
    if user.bot_state:
        state_handlers[user.bot_state](bot, message)
        return

    for text, handler in message_handlers.items():
        if message.text.startswith(text):
            handler(bot, message)
            break

    for key, handler in key_handlers.items():
        if message.text == key:
            handler(bot, message)
            break


@bot.message_handler(content_types=['contact'])
def contact_handler(message):
    if message.forward_from:
        return

    chat_id = message.chat.id
    user = BotUser.objects.get(chat_id=chat_id)
    if user.phone_number:
        return

    phone_number = message.contact.phone_number.removeprefix('+')
    if (other := BotUser.objects.filter(phone_number=phone_number).first()):
        user.delete()
        other.chat_id = chat_id
        other.save()
        commands.menu_command_handler(bot, message)
        return

    user.phone_number = phone_number
    if (client := ro_api.get_client_by_phone_number(phone_number)):
        user.rem_id = client.id
        user.name = client.name
        user.save()
        tasks.update_bonus_for_new_user(user)
        commands.menu_command_handler(bot, message)
    else:
        user.bot_state = BotUser.State.REGISTRATION
        user.save()
        bot.send_message(chat_id, Messages.NEW_CLIENT_INFO)


callback_query_handlers = {
    CallTypes.Menu: commands.menu_callback_query_handler,
    CallTypes.OpenOrders: handlers.open_orders_callback_query_handler,
    CallTypes.ReferalProgram: handlers.referal_program_callback_query_handler,
    CallTypes.RecalcBonus: handlers.recalc_bonus_callback_query_handler,
    CallTypes.Referals: handlers.referals_callback_query_handler,
    CallTypes.Contacts: handlers.contacts_callback_query_handler,
    CallTypes.Discounts: handlers.discounts_callback_query_handler,
}


@bot.callback_query_handler(func=lambda call: True)
def callback_query_handler(call):
    call_type = CallTypes.parse_data(call.data)
    for CallType, handler in callback_query_handlers.items():
        if CallType == call_type.__class__:
            handler(bot, call)
            break


if __name__ == "__main__":
    import locale
    locale.setlocale(locale.LC_ALL, 'ru_RU')
    print(bot.get_me())
    # bot.polling()
    bot.infinity_polling()
