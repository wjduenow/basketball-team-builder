# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-07 17:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('team_manager', '0010_auto_20170407_1645'),
    ]

    operations = [
        migrations.AddField(
            model_name='playerstats',
            name='awareness',
            field=models.IntegerField(default=2),
        ),
    ]
