from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django_q.tasks import schedule, Schedule

from backend.models import Template, OrderMailing


def generate_code():
    code_text = str()
    code_text += 'from backend.models import Template\n'
    code_text += '\n\nclass Messages():\n'
    for message in Template.messages.all():
        code_text += f'    {message.title} = Template.messages.get(id={message.id}).gettext()\n'

    code_text += '\n\nclass Keys():\n'
    for key in Template.keys.all():
        code_text += f'    {key.title} = Template.keys.get(id={key.id}).gettext()\n'

    code_text += '\n\nclass Smiles():\n'
    for smile in Template.smiles.all():
        code_text += f'    {smile.title} = Template.smiles.get(id={smile.id}).gettext()\n'

    return code_text


@receiver(post_save, sender=Template)
def template_post_save_handler(instance, **kwargs):
    template_file = 'backend/templates.py'
    with open(template_file, 'w') as file:
        file.write(generate_code())


@receiver(post_delete, sender=Template)
def template_post_delete_handler(instance, **kwargs):
    template_file = 'backend/templates.py'
    with open(template_file, 'w') as file:
        file.write(generate_code())


@receiver(post_save, sender=OrderMailing)
def order_mailing_post_save_handler(instance, **kwargs):
    name = f'order-mailing-{instance.id}'
    if Schedule.objects.filter(name=name).exists():
        sch = Schedule.objects.get(name=name)
        sch.minutes = instance.period
        sch.repeat = instance.repeat
        sch.save()
    else:
        schedule('backend.tasks.order_mailing_run', instance.id,
                 name=name,
                 schedule_type=Schedule.MINUTES,
                 minutes=instance.period,
                 next_run=timezone.now(),
                 repeats=instance.repeat)


@receiver(post_delete, sender=OrderMailing)
def order_mailing_post_delete_handler(instance, **kwargs):
    name = f'order-mailing-{instance.id}'
    Schedule.objects.filter(name=name).delete()
