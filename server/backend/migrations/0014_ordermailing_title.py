# Generated by Django 4.0.6 on 2022-07-30 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0013_alter_ordermailing_options_ordermailing_users_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordermailing',
            name='title',
            field=models.CharField(default='', max_length=255, verbose_name='Название'),
            preserve_default=False,
        ),
    ]
