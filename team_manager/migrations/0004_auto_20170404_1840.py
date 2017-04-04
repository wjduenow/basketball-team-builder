# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-04 18:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team_manager', '0003_auto_20170404_1835'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gymslotplayer',
            name='gym_slot',
        ),
        migrations.RemoveField(
            model_name='gymslotplayer',
            name='players',
        ),
        migrations.AddField(
            model_name='gymslot',
            name='players',
            field=models.ManyToManyField(to='team_manager.Player'),
        ),
        migrations.DeleteModel(
            name='GymSlotPlayer',
        ),
    ]
