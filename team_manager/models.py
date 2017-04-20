from __future__ import unicode_literals

from django.db import models
from datetime import datetime
from operator import itemgetter
from collections import defaultdict

from django.core.signals import request_finished
from django.dispatch import receiver

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
    size = models.IntegerField(blank=True, null=True, choices=[(1, 'Small'), (2, 'Medium'), (3, 'Large')])
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

    class Meta:
        ordering = ('first_name',)

class PlayerStats(models.Model):
    player = models.ForeignKey(Player, blank=True, null=True, db_index=True)
    scoring = models.IntegerField(default=2)
    outside_shooting = models.IntegerField(default=2)
    passing = models.IntegerField(default=2)
    rebounding = models.IntegerField(default=2)
    defend_large = models.IntegerField(default=2)
    defend_fast = models.IntegerField(default=2)
    movement = models.IntegerField(default=2)
    awareness = models.IntegerField(default=2)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def player_score(self):
        return mean([self.scoring, self.outside_shooting, self.passing, self.rebounding, self.defend_large, self.defend_fast, self.movement, self.awareness, self.player.size])

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

    class Meta:
        ordering = ('-start_time',)

class Team(models.Model):
    name = models.CharField(max_length=200)
    players = models.ManyToManyField(Player)
    score = models.IntegerField(null=True)
    won = models.NullBooleanField(null=True)
    
    @classmethod
    def make_team(cls, player_ids, model_weights = {}):
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
                player['size'] = player['size']
                player['scoring'] = stats_dict[int(player['id'])].scoring
                player['outside_shooting'] = stats_dict[int(player['id'])].outside_shooting
                player['passing'] = stats_dict[int(player['id'])].passing
                player['rebounding'] = stats_dict[int(player['id'])].rebounding
                player['defend_large'] = stats_dict[int(player['id'])].defend_large
                player['defend_fast'] = stats_dict[int(player['id'])].defend_fast
                player['movement'] = stats_dict[int(player['id'])].movement
                player['awareness'] = stats_dict[int(player['id'])].awareness
                player['player_score'] = stats_dict[int(player['id'])].player_score

                ## Add in Weights
                for k,v in model_weights.items():
                    if v.isnumeric():
                        player[k] = float(player[k]) * float(v)

            else:
                print("DID NOT FIND STATS FOR %s" % (player['id']))
                player['player_score'] = 2


        #Sort by Scoring and Assign to B and then A
        sl = sorted(players, key=itemgetter('scoring', 'player_score'), reverse=True)
        team_a.append(sl.pop(0))
        team_b.append(sl.pop(0))
        

        if group_size < 4:
            return teams

        ### Sort by Ball Handler and Assign Best Ball Handlers to Teams A and B
        sl = sorted(sl, key=itemgetter('ball_handler', 'player_score'), reverse=True)        
        team_b.append(sl.pop(0))
        team_a.append(sl.pop(0))

        if group_size < 6:
            return teams

        ### Scoring Existing Teams for OutSide Shooting and Assign Best Shooter to Worst Team
        sl = sorted(sl, key=itemgetter('outside_shooting'), reverse=True)

        sorted_team = Team.sort_team_on_metric(teams, 'outside_shooting')
        if sorted_team['team_a'] < sorted_team['team_a']:
            team_a.append(sl.pop(0))
            team_b.append(sl.pop(0))
        else:
            team_b.append(sl.pop(0))
            team_a.append(sl.pop(0))

        if group_size < 8:
            return teams

        ### Scoring Existing Teams for player_score and Assign Best Movement to Worst Team
        sl = sorted(sl, key=itemgetter('player_score'), reverse=True)

        sorted_team = sort_team_on_metric_size(teams, 'player_score')
        if sorted_team['team_a'] < sorted_team['team_b']:
            team_a.append(sl.pop(0))
            team_b.append(sl.pop(0))
        else:
            team_b.append(sl.pop(0))
            team_a.append(sl.pop(0))

        if group_size < 10:
            return teams

        ### Scoring Existing Teams for player_score and Assign Best big player_score to Worst Team
        sl = sorted(sl, key=itemgetter('player_score'), reverse=True)

        sorted_team = sort_team_on_metric_size(teams, 'player_score')
        if sorted_team['team_a'] < sorted_team['team_b']:
            team_a.append(sl.pop(0))
            team_b.append(sl.pop(0))
        else:
            team_b.append(sl.pop(0))
            team_a.append(sl.pop(0))

        ### Calculate Team Scores
        sorted_team = Team.sort_team_on_metric(teams, 'player_score')
        team_score = {'team_a': sorted_team['team_a'], 'team_b': sorted_team['team_b']}
        #if abs(sorted_team['team_a'] - sorted_team['team_b']) > 2:
        #    print("Model Error: The Teams are Mismatched")

        return teams

    @classmethod
    def sort_team_on_metric(cls, teams, metric):
        sorted_team = {}
        for team,players in teams.items():
            outside_shooting = 0
            for player in teams[team]:
                outside_shooting += player[metric]

            sorted_team[team] = int(outside_shooting)

        return sorted_team

class Game(models.Model):
    gym_session = models.ForeignKey(GymSession, on_delete=models.CASCADE)
    teams = models.ManyToManyField(Team)
    court = models.CharField(max_length=200, blank=True, null=True)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=200, blank=True, null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def end_game(self):
        self.end_time = datetime.now()
        self.save

    @property
    def game_duration(self):
        return self.end_time - self.start_time

    @property
    def game_duration_friendly(self):
        min_secs = divmod(self.game_duration.days * 86400 + self.game_duration.seconds, 60)
        return "%s Minutes and %s Seconds" % (min_secs[0], min_secs[1])

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

def sort_team_on_metric_size(teams, metric):
    sorted_team = {}
    for team,players in teams.items():
        outside_shooting = 0
        for player in teams[team]:
            outside_shooting += player[metric] * (player['size'])

        sorted_team[team] = int(outside_shooting)

    return sorted_team

    #def __str__(self):
    #    return str(self.gym_slot) + ": " + str(self.player)