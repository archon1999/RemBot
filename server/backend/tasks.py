from django.utils import timezone

from backend.models import BotUser
from backend import ro_api


def update_bonus_for_user(user: BotUser):
    params = {'closed_at[]': user.bonus_updated.timestamp() * 1000}
    user.bonus_updated = timezone.now()
    user.save()
    orders = ro_api.get_client_orders(user.rem_id, **params)
    for order in orders:
        if order.status.group != 6:
            continue

        payed = order.payed
        user.bonus += user.cashback_bonus_percentage * payed / 100

    for referal_user in user.referals.all():
        orders = ro_api.get_client_orders(referal_user.rem_id, **params)
        for order in orders:
            if order.status.group != 6:
                continue

            payed = order.payed
            user.bonus += user.referals_bonus_percentage * payed / 100

    user.save()


def update_bonus_for_all():
    for user in BotUser.objects.all():
        update_bonus_for_user(user)
