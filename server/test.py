import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from backend.tasks import update_bonus_for_user
from backend.models import BotUser, OrderMailing


# user = BotUser.objects.get(rem_id=25098087)
# update_bonus_for_user(user)
OrderMailing.objects.first().users.all().delete()
mailing = OrderMailing.objects.first()
mailing.orders = ''
mailing.save()
