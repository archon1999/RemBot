# Generated by Django 4.0.4 on 2022-07-14 10:36

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='botuser',
            name='first_name',
        ),
        migrations.RemoveField(
            model_name='botuser',
            name='lang',
        ),
        migrations.RemoveField(
            model_name='botuser',
            name='last_name',
        ),
        migrations.RemoveField(
            model_name='template',
            name='body_en',
        ),
        migrations.RemoveField(
            model_name='template',
            name='body_ru',
        ),
        migrations.RemoveField(
            model_name='template',
            name='body_uz',
        ),
        migrations.AddField(
            model_name='botuser',
            name='rem_id',
            field=models.IntegerField(default=1, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='template',
            name='body',
            field=ckeditor.fields.RichTextField(default=''),
            preserve_default=False,
        ),
    ]