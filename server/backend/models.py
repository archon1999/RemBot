from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField
from bs4 import BeautifulSoup
from bs4.element import NavigableString, Tag


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
    cashback_bonus_percentage = models.IntegerField(default=2)
    referals_bonus_percentage = models.IntegerField(default=2)
    phone_number = models.CharField(max_length=255)
    bot_state = models.IntegerField(default=State.NOTHING)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


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

    def __str__(self):
        return self.body
