from django.shortcuts import redirect

from .models import BotUser


def cashback_bonus_percentage_edit(request):
    value = int(request.POST['value'])
    BotUser.objects.all().update(cashback_bonus_percentage=value)
    return redirect('/admin/backend/botuser/')


def referals_bonus_percentage_edit(request):
    value = int(request.POST['value'])
    BotUser.objects.all().update(referals_bonus_percentage=value)
    return redirect('/admin/backend/botuser/')
