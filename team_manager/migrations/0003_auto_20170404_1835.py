# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-04 18:35
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('team_manager', '0002_auto_20170404_0402'),
    ]

    operations = [
        migrations.CreateModel(
            name='GymSessionPlayer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('gym_session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='team_manager.GymSession')),
            ],
        ),
        migrations.RemoveField(
            model_name='gymslotplayer',
            name='player',
        ),
        migrations.AddField(
            model_name='gymslotplayer',
            name='players',
            field=models.ManyToManyField(to='team_manager.Player'),
        ),
        migrations.AlterField(
            model_name='gymslot',
            name='black_out_dates',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='position',
            field=models.CharField(blank=True, choices=[('Guard', 'Guard'), ('Forward', 'Forward')], max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='size',
            field=models.CharField(blank=True, choices=[('Small', 'Small'), ('Medium', 'Medium'), ('Large', 'Large')], max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='status',
            field=models.CharField(blank=True, choices=[('Active', 'Active'), ('Inactive', 'Inactive')], max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='gymsessionplayer',
            name='player',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='team_manager.Player'),
        ),
    ]
