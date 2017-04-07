from __future__ import unicode_literals

from django.db import models
from datetime import datetime
from operator import itemgetter
from collections import defaultdict

# Create your models here.


class Group(models.Model):
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=200, blank=True, null=True)
    has_logo = models.BooleanField(default=False)
    logo_image = models.BinaryField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Player(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200, blank=True, null=True)
    nick_name = models.CharField(max_length=200, blank=True, null=True)
    referred_by = models.ForeignKey('self', blank=True, null=True)
    status = models.CharField(max_length=200, blank=True, null=True, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])
    size = models.CharField(max_length=200, blank=True, null=True, choices=[('Small', 'Small'), ('Medium', 'Medium'), ('Large', 'Large')])
    position = models.CharField(max_length=200, blank=True, null=True, choices=[('Guard', 'Guard'), ('Forward', 'Forward')])
    ball_handler = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.nick_name:
            return self.first_name + " " + str(self.last_name) + " (" + self.nick_name + ")"
        else:
            return self.first_name + " " + str(self.last_name)

    def current_stats(self):
        player_stats = PlayerStats.objects.filter(player = self).latest('created_at')
        if player_stats:
            return player_stats
        else:
            player_stats = PlayerStats.create(player = self).scoring
            player_stats.save
            return player_stats

class PlayerStats(models.Model):
    player = models.ForeignKey(Player, blank=True, null=True, db_index=True)
    scoring = models.IntegerField(default=2)
    outside_shooting = models.IntegerField(default=2)
    passing = models.IntegerField(default=2)
    rebounding = models.IntegerField(default=2)
    defend_large = models.IntegerField(default=2)
    defend_fast = models.IntegerField(default=2)
    movement = models.IntegerField(default=2)
    created_at = models.DateTimeField(auto_now_add=True)

class GymSlot(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    players = models.ManyToManyField(Player)
    status = models.CharField(max_length=200, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    day_of_week = models.CharField(max_length=200, 
                                   blank=True, null=True, 
                                   choices=[('Monday', 'Monday'), ('Tuesday', 'Tuesday'), 
                                         ('Wednesday', 'Wednesday'), ('Thursday', 'Thursday'), 
                                         ('Friday', 'Friday'), ('Saturday', 'Saturday'), 
                                         ('Sunday', 'Sunday')])
    black_out_dates = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class GymSession(models.Model):
    gym_slot = models.ForeignKey(GymSlot, on_delete=models.CASCADE)
    players = models.ManyToManyField(Player)
    name = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=200, blank=True, null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def end_session(self):
        self.end_time = datetime.now()
        self.save

class Game(models.Model):
    gym_session = models.ForeignKey(GymSession, on_delete=models.CASCADE)
    court = models.CharField(max_length=200, blank=True, null=True)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=200, blank=True, null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def end_game(self):
        self.end_time = datetime.now()
        self.save

class Team(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    score = models.IntegerField()
    won = models.NullBooleanField()
    
    @classmethod
    def make_team(cls, player_ids):
        team_a = []
        team_b = []
        stats_dict = {}
        teams = {'team_a': team_a, 'team_b': team_b}
        group_size = len(player_ids)

        ### Get List of Players
        players = Player.objects.filter(pk__in=player_ids).values()
        
        ### Creating Dict of Player Stats in Order to Join to Players
        ids_string = ",".join(str(v) for v in player_ids)
        stats = PlayerStats.objects.raw("SELECT * FROM team_manager_playerstats s WHERE s.id in (SELECT MAX(id) as id FROM team_manager_playerstats WHERE player_id IN (%s) GROUP BY player_id);" % (ids_string))
        for stat in stats:
            stats_dict[int(stat.player_id)] = stat

        ### Append Stats to Players
        for player in players:
            if player['id'] in stats_dict:
                player['scoring'] = stats_dict[int(player['id'])].scoring
                player['outside_shooting'] = stats_dict[int(player['id'])].outside_shooting
                player['passing'] = stats_dict[int(player['id'])].passing
                player['rebounding'] = stats_dict[int(player['id'])].rebounding
                player['defend_large'] = stats_dict[int(player['id'])].defend_large
                player['defend_fast'] = stats_dict[int(player['id'])].defend_fast
                player['movement'] = stats_dict[int(player['id'])].movement
                player['player_score'] = mean([player['scoring'], player['outside_shooting'], 
                                               player['passing'], player['rebounding'], player['defend_large'], 
                                               player['defend_fast'], player['movement']])
            else:
                print("DID NOT FIND STATS FOR %s" % (player['id']))
                player['player_score'] = 2.1

      

        ### Sort by Ball Handler and Assign Best Ball Handlers to Teams A and B
        sl = sorted(players, key=itemgetter('ball_handler', 'player_score'), reverse=True)
        team_a.append(sl.pop(0))
        team_b.append(sl.pop(0))

        if group_size < 4:
            return teams
 

        #Sort by Scoring and Assign to B and then A
        sl = sorted(sl, key=itemgetter('scoring', 'player_score'), reverse=True)
        team_a.append(sl.pop(0))
        team_b.append(sl.pop(0))

        if group_size < 6:
            return teams

        ### Scoring Existing Teams for OutSide Shooting and Assign Best Shooter to Worst Team
        sl = sorted(sl, key=itemgetter('outside_shooting'), reverse=True)

        sorted_team = sort_team_on_metric(teams, 'outside_shooting')
        if sorted_team['team_a'] < sorted_team['team_a']:
            team_a.append(sl.pop(0))
            team_b.append(sl.pop(0))
        else:
            team_b.append(sl.pop(0))
            team_a.append(sl.pop(0))

        if group_size < 8:
            return teams

        ### Scoring Existing Teams for player_score and Assign Best Movement to Worst Team
        sl = sorted(sl, key=itemgetter('movement'), reverse=True)

        sorted_team = sort_team_on_metric(teams, 'player_score')
        if sorted_team['team_a'] < sorted_team['team_a']:
            team_a.append(sl.pop(0))
            team_b.append(sl.pop(0))
        else:
            team_b.append(sl.pop(0))
            team_a.append(sl.pop(0))

        if group_size < 10:
            return teams

        ### Scoring Existing Teams for player_score and Assign Best player_score to Worst Team
        sl = sorted(sl, key=itemgetter('player_score'), reverse=True)

        sorted_team = sort_team_on_metric(teams, 'player_score')
        if sorted_team['team_a'] < sorted_team['team_a']:
            team_a.append(sl.pop(0))
            team_b.append(sl.pop(0))
        else:
            team_b.append(sl.pop(0))
            team_a.append(sl.pop(0))

        return teams


class TeamPlayer(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

def sort_team_on_metric(teams, metric):
    sorted_team = {}
    for team,players in teams.items():
        outside_shooting = 0
        for player in teams[team]:
            outside_shooting += player[metric]

        sorted_team[team] = int(outside_shooting)

    return sorted_team

    #def __str__(self):
    #    return str(self.gym_slot) + ": " + str(self.player)