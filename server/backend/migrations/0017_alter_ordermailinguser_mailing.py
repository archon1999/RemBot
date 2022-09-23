# Generated by Django 4.0.6 on 2022-08-15 07:18

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0016_remove_ordermailing_users_ordermailinguser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordermailinguser',
            name='mailing',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='backend.ordermailing'),
        ),
    ]
