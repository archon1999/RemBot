# Generated by Django 4.0.4 on 2022-07-20 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0009_botuser_cashback_bonus_percentage_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='botuser',
            name='username',
        ),
        migrations.AddField(
            model_name='botuser',
            name='name',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
    ]