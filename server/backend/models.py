import re
import os

from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag

BONUS_UPDATE_DAYS_FOR_NEW_USER = int(
    os.getenv('BONUS_UPDATE_DAYS_FOR_NEW_USER'))


class BotUser(models.Model):
    class State(models.IntegerChoices):
        NOTHING = 0
        REGISTRATION = 1

    chat_id = models.CharField(unique=True, max_length=255)
    rem_id = models.IntegerField(unique=True, null=True, blank=True)
    name = models.CharField(max_length=255)
    from_user = models.ForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='referals',
        null=True,
        blank=True,
    )
    bonus = models.IntegerField(default=0)
    bonus_updated = models.DateTimeField(default=timezone.now)
    phone_number = models.CharField(max_length=255)
    bot_state = models.IntegerField(default=State.NOTHING)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class OrderMailing(models.Model):
    class StatusGroup(models.IntegerChoices):
        CUSTOM = 0, '0 - Пользовательские'
        NEW = 1, '1 - Новый'
        ON_EXECUTION = 2, '2 - На исполнении'
        DEFERRED = 3, '3 - Отложенные'
        FULFILLED = 4, '4 - Исполненные'
        DELIVERY = 5, '5 - Доставка'
        CLOSED_SUCCESSFULLY = 6, '6 - Закрытые успешно'
        CLOSED_UNSUCCESSFULLY = 7, '7 - Закрытые неуспешно'

    orders = models.TextField(blank=True, default='')
    title = models.CharField(max_length=255, verbose_name='Название')
    image = models.ImageField(null=True, blank=True,
                              upload_to='backend/images')
    status_group = models.IntegerField(choices=StatusGroup.choices)
    text = RichTextField()
    created_at_duration = models.DurationField(null=True, blank=True)
    closed_at_duration = models.DurationField(null=True, blank=True)
    period = models.IntegerField()
    repeat = models.IntegerField(default=-1)
    user_unique = models.BooleanField()
    created = models.DateTimeField(auto_now_add=True)

    def get_orders(self):
        return self.orders.split(',')

    def has_order(self, order_id):
        return str(order_id) in self.get_orders()

    def insert_order(self, order_id):
        orders = self.get_orders()
        orders.append(str(order_id))
        self.orders = ','.join(orders)
        self.save()

    def check_filters(self, items: dict):
        if self.filters.all().count() == 0:
            return True

        for filter in self.filters.all():
            attr_name = filter.attr_name
            pattern = filter.pattern
            if not items.get(attr_name, None):
                continue

            value = str(items[attr_name])
            if re.findall(pattern, value):
                return True

        return False

    class Meta:
        verbose_name = 'Рассылка для заказа'
        verbose_name_plural = 'Рассылка для заказов'


class OrderMailingUser(models.Model):
    user = models.ForeignKey(BotUser, on_delete=models.CASCADE)
    mailing = models.ForeignKey(OrderMailing,
                                on_delete=models.CASCADE,
                                related_name='users')


class OrderMailingFilter(models.Model):
    order_mailing = models.ForeignKey(OrderMailing,
                                      on_delete=models.CASCADE,
                                      related_name='filters')
    attr_name = models.CharField(max_length=255)
    pattern = models.CharField(max_length=255)


def filter_tag(tag: Tag, ol_number=None):
    if isinstance(tag, NavigableString):
        text = tag
        text = text.replace('<', '&#60;')
        text = text.replace('>', '&#62;')
        return text

    html = str()
    li_number = 0
    for child_tag in tag:
        if tag.name == 'ol':
            if child_tag.name == 'li':
                li_number += 1
        else:
            li_number = None

        html += filter_tag(child_tag, li_number)

    format_tags = ['strong', 'em', 'pre', 'b', 'u', 'i', 'code']
    if tag.name in format_tags:
        return f'<{tag.name}>{html}</{tag.name}>'

    if tag.name == 'a':
        return f"""<a href="{tag.get("href")}">{tag.text}</a>"""

    if tag.name == 'li':
        if ol_number:
            return f'{ol_number}. {html}'
        return f'•  {html}'

    if tag.name == 'br':
        html += '\n'

    if tag.name == 'span':
        styles = tag.get_attribute_list('style')
        if 'text-decoration: underline;' in styles:
            return f'<u>{html}</u>'

    if tag.name == 'ol' or tag.name == 'ul':
        return '\n'.join(map(lambda row: f'   {row}', html.split('\n')))

    return html


def filter_html(html: str):
    soup = BeautifulSoup(html, 'lxml')
    return filter_tag(soup)


class MessageManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=Template.Type.MESSAGE)


class KeyManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=Template.Type.KEY)


class SmileManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(type=Template.Type.SMILE)


class Template(models.Model):
    class Type(models.IntegerChoices):
        MESSAGE = 1
        KEY = 2
        SMILE = 3

    templates = models.Manager()
    messages = MessageManager()
    keys = KeyManager()
    smiles = SmileManager()

    type = models.IntegerField(choices=Type.choices)
    title = models.CharField(max_length=255)
    body = RichTextField()

    def gettext(self):
        return filter_html(self.body)

    class Meta:
        verbose_name = 'Шаблон'
        verbose_name_plural = 'Шаблоны'

    def __str__(self):
        return self.title
