# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-26 23:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team_manager', '0025_manual_20170426_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='last_game_date',
            field=models.DateTimeField(null=True),
        ),
    ]
