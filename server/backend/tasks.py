import os
import traceback
import datetime

import telebot
from django.utils import timezone

from backend import ro_api
from backend.models import (BONUS_UPDATE_DAYS_FOR_NEW_USER, BotUser,
                            OrderMailing, filter_html)
from backend.templates import Messages

import locale
locale.setlocale(locale.LC_ALL, 'ru_RU')


TOKEN = os.getenv('BOT_TOKEN')


def get_cashback_bonus_percentage():
    return int(os.getenv('CASHBACK_BONUS_PERCENTAGE'))


def get_referals_bonus_percentage():
    return int(os.getenv('REFERALS_BONUS_PERCENTAGE'))


def update_bonus_for_new_user(user: BotUser, limit=1):
    closed_at = user.bonus_updated - timezone.timedelta(
        days=BONUS_UPDATE_DAYS_FOR_NEW_USER
    )
    params = {'closed_at[]': int(closed_at.timestamp() * 1000)}
    orders = ro_api.get_client_orders(user.phone_number, **params)
    bonus = 0
    for order in orders:
        if limit == 0:
            break

        if order.status.group != 6:
            continue

        payed = order.payed
        bonus += get_cashback_bonus_percentage() * payed / 100
        limit -= 1

    if bonus > 0:
        user.bonus += bonus
        user.save()
        bot = telebot.TeleBot(TOKEN, parse_mode='HTML')
        text = Messages.BONUSES_ACCRUED.format(
            bonus=int(bonus),
        )
        try:
            bot.send_message(user.chat_id, text)
        except Exception:
            traceback.print_exc()


def update_bonus_for_user(user: BotUser):
    if not user.phone_number:
        return

    params = {'closed_at[]': int(user.bonus_updated.timestamp() * 1000)}
    user.bonus_updated = timezone.now()
    user.save()
    orders = ro_api.get_client_orders(user.phone_number, **params)
    bonus = 0
    for order in orders:
        if order.status.group != 6:
            continue

        payed = order.payed
        bonus += get_cashback_bonus_percentage() * payed / 100

    for referal_user in user.referals.all():
        orders = ro_api.get_client_orders(referal_user.phone_number, **params)
        for order in orders:
            if order.status.group != 6:
                continue

            payed = order.payed
            bonus += get_referals_bonus_percentage() * payed / 100

    if bonus > 0:
        user.bonus += bonus
        user.save()
        bot = telebot.TeleBot(TOKEN, parse_mode='HTML')
        text = Messages.BONUSES_ACCRUED.format(
            bonus=int(bonus),
        )
        try:
            bot.send_message(user.chat_id, text)
        except Exception:
            traceback.print_exc()


def update_bonus_for_all():
    for user in BotUser.objects.all():
        update_bonus_for_user(user)


def order_mailing_run(order_mailing_id):
    order_mailing: OrderMailing = OrderMailing.objects.get(id=order_mailing_id)
    params = {}
    if order_mailing.created_at_duration:
        dt = timezone.now()-order_mailing.created_at_duration
        params['created_at[]'] = int(dt.timestamp() * 1000)

    if order_mailing.closed_at_duration:
        dt = timezone.now()-order_mailing.closed_at_duration
        params['closed_at[]'] = int(dt.timestamp() * 1000)

    group = order_mailing.status_group
    statuses = ro_api.get_group_statuses(group)
    params['statuses[]'] = statuses
    orders = ro_api.get_orders(**params)
    for order in orders:
        items = ro_api.get_items(order)
        if not order_mailing.check_filters(items):
            continue

        if order_mailing.has_order(order.id):
            continue

        order_mailing.insert_order(order.id)
        if not order.client.phone:
            continue

        phone_number = order.client.phone[0]
        if not BotUser.objects.filter(phone_number=phone_number).exists():
            continue

        user = BotUser.objects.get(phone_number=phone_number)
        if order_mailing.user_unique and order_mailing.users.filter(user=user):
            continue

        if not order_mailing.users.filter(user=user):
            order_mailing.users.create(user=user)

        if (estimated_done_at := order.get('estimated_done_at', None)):
            estimated_done_at = datetime.datetime.fromtimestamp(
                estimated_done_at / 1000)
            estimated_done_at = estimated_done_at.strftime('%d %B %Y в %H:%M')
            order['estimated_done_at'] = estimated_done_at

        items = ro_api.get_items(order)
        text = filter_html(order_mailing.text.format(
            name=user.name,
            bonus=user.bonus,
            **items
        ))
        bot = telebot.TeleBot(TOKEN, parse_mode='HTML')
        if order_mailing.image:
            photo = open(order_mailing.image.name, 'rb')
            bot.send_photo(user.chat_id, photo, text)
        else:
            bot.send_message(user.chat_id, text)
