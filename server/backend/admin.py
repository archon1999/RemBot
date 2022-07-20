from django.contrib import admin

from .models import BotUser, Template
from .tasks import update_bonus_for_user


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    @admin.action(description='Пересчитать бонусы')
    def update_bonus(self, request, queryset):
        for user in queryset:
            update_bonus_for_user(user)

    list_display = ['id', 'name', 'bonus', 'rem_id', 'chat_id']
    actions = [update_bonus]


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'title']
