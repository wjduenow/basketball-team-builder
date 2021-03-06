# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-19 22:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team_manager', '0014_auto_20170419_2119'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teamplayer',
            name='player',
        ),
        migrations.RemoveField(
            model_name='teamplayer',
            name='team',
        ),
        migrations.AddField(
            model_name='team',
            name='players',
            field=models.ManyToManyField(to='team_manager.Player'),
        ),
        migrations.DeleteModel(
            name='TeamPlayer',
        ),
    ]
