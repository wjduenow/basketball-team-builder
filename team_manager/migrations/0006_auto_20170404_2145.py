# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-04 21:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team_manager', '0005_gymslot_day_of_week'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gymsessionplayer',
            name='gym_session',
        ),
        migrations.RemoveField(
            model_name='gymsessionplayer',
            name='player',
        ),
        migrations.AddField(
            model_name='gymsession',
            name='players',
            field=models.ManyToManyField(to='team_manager.Player'),
        ),
        migrations.DeleteModel(
            name='GymSessionPlayer',
        ),
    ]
