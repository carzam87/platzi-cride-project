# Generated by Django 2.0.9 on 2021-12-05 20:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('circles', '0005_auto_20210805_0404'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='circle',
            options={'get_latest_by': 'created', 'ordering': ('name',)},
        ),
    ]
