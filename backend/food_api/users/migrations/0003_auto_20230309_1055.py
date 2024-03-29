# Generated by Django 3.2.16 on 2023-03-09 06:55

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_subscription'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='followed',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscription_followed', to=settings.AUTH_USER_MODEL, verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='follower',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscription_follower', to=settings.AUTH_USER_MODEL, verbose_name='Подписчик'),
        ),
    ]
