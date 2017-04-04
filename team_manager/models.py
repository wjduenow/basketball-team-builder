from __future__ import unicode_literals

from django.db import models
from datetime import datetime


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
        return None

class PlayerStats(models.Model):
    player = models.ForeignKey(Player, blank=True, null=True)
    scoring = models.IntegerField()
    passing = models.IntegerField()
    rebounding = models.IntegerField()
    defend_large = models.IntegerField()
    defend_fast = models.IntegerField()
    movement = models.IntegerField()
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
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=200, blank=True, null=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField()
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

class GymSessionPlayer(models.Model):
    gym_session = models.ForeignKey(GymSession, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class TeamPlayer(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)



    #def __str__(self):
    #    return str(self.gym_slot) + ": " + str(self.player)