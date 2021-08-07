# Generated by Django 2.0.9 on 2021-08-05 04:04

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('circles', '0004_auto_20210805_0358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='circle',
            name='members',
            field=models.ManyToManyField(related_name='_circle_members_+', through='circles.Membership', to=settings.AUTH_USER_MODEL),
        ),
    ]
