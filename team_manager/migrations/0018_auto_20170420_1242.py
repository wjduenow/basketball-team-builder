# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-20 19:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('team_manager', '0017_auto_20170420_1157'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gymslot',
            name='gym_sessions',
        ),
        migrations.AddField(
            model_name='gymsession',
            name='gym_slot',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='team_manager.GymSlot'),
            preserve_default=False,
        ),
    ]
