# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-21 21:02
from __future__ import unicode_literals

from django.db import migrations
import sqlparse


class Migration(migrations.Migration):


    run_sql = "CREATE OR REPLACE VIEW vw_player_win_summary AS SELECT UUID() as id, player_id, first_name, SUM(1) as played, sum(won) as won, (sum(won)/Sum(1)) as win_loss, DATE(start_time) game_date FROM (SELECT p.id as player_id, p.first_name, t.won, g.start_time FROM team_manager_team t INNER JOIN team_manager_game_teams gt on gt.team_id = t.id INNER JOIN team_manager_game g on g.id = gt.game_id INNER JOIN team_manager_team_players tp on tp.team_id = t.id INNER JOIN team_manager_player p on p.id = tp.player_id) st GROUP BY player_id, first_name, DATE(start_time);"

    dependencies = [
        ('team_manager', '0019_auto_20170421_1402'),
    ]

    operations = [
        migrations.RunSQL(
            sqlparse.format(run_sql), 
            sqlparse.format("DROP view vw_player_win_summary")
        )
    ]
