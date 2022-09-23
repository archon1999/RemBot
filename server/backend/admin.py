from django.contrib import admin

from .models import (BotUser, OrderMailing, OrderMailingFilter,
                     OrderMailingUser, Template)
from .tasks import update_bonus_for_user


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    @admin.action(description='Пересчитать бонусы')
    def update_bonus(self, request, queryset):
        for user in queryset:
            update_bonus_for_user(user)

    list_display = ['id', 'name', 'bonus', 'rem_id', 'chat_id']
    search_fields = ['phone_number']
    actions = [update_bonus]


class OrderMailingFilterInlineAdmin(admin.TabularInline):
    model = OrderMailingFilter
    extra = 1


class OrderMailingUserInlineAdmin(admin.TabularInline):
    model = OrderMailingUser
    extra = 0


@admin.register(OrderMailing)
class OrderMailingAdmin(admin.ModelAdmin):
    exclude = ['orders', 'users']
    list_display = ['id', 'title', 'status_group', 'period', 'created']
    list_filter = ['status_group']
    inlines = [OrderMailingFilterInlineAdmin, OrderMailingUserInlineAdmin]


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'title']
