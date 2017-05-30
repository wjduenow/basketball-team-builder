from __future__ import unicode_literals
from __future__ import division
from django.db import models
from datetime import datetime, timedelta
from operator import itemgetter
from collections import defaultdict
from django.core.signals import request_finished
from django.dispatch import receiver
from django.db import connection
from django.db.models import Count, Avg, Sum, Min, Max

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
    referred_by = models.ForeignKey('self', blank=True, null=True, related_name='referred')
    status = models.CharField(max_length=200, blank=True, null=True, choices=[('Active', 'Active'), ('Inactive', 'Inactive')])
    size = models.IntegerField(blank=True, default=2, choices=[(1, 'Small'), (2, 'Medium'), (3, 'Large')])
    position = models.CharField(max_length=200, blank=True, null=True, choices=[('Guard', 'Guard'), ('Forward', 'Forward')])
    ball_handler = models.BooleanField(default=False)
    last_game_date = models.DateTimeField(null=True)
    last_game_id = models.IntegerField(blank=True, null=True)
    ninety_day_games_played = models.FloatField(default=2)
    ninety_day_plus_minus = models.FloatField(default=2)
    win_contribution = models.FloatField(default=0)
    score_contribution = models.FloatField(default=0)
    ninety_day_win_percentage = models.FloatField(default=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('first_name',)

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

    @classmethod
    def update_player_game_stats(cls):
        str_sql = """UPDATE team_manager_player INNER JOIN (
                        SELECT p.id, MAX(gt.game_id) game_id, MAX(gs.created_at) as created_at 
                            FROM team_manager_player p 
                            INNER JOIN team_manager_team_players tp on tp.player_id = p.id 
                            INNER JOIN team_manager_game_teams gt on gt.id = tp.team_id 
                            INNER JOIN team_manager_game g on g.id = gt.game_id 
                            INNER JOIN team_manager_gymsession gs on gs.id = g.gym_session_id 
                            GROUP BY 1) tmp_query 
                        ON tmp_query.id = team_manager_player.id
                        SET 
                            last_game_date = tmp_query.created_at,
                            last_game_id = tmp_query.game_id;"""

        with connection.cursor() as cursor:
            cursor.execute(str_sql)



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

class PlayerSummary(models.Model):
    player = models.ForeignKey(Player, on_delete=models.DO_NOTHING)
    first_name = models.CharField(max_length=200)
    played = models.IntegerField(default=2)
    won = models.IntegerField(default=2)
    win_loss = models.FloatField(default=2)
    point_differential = models.FloatField(default=2)
    game_date = models.DateField()
 
    class Meta:
        managed = False
        db_table = 'vw_player_win_summary'

class PlayerPlayerSummary(models.Model):
    player = models.ForeignKey(Player, on_delete=models.DO_NOTHING, related_name='player_player_summary')
    other_player = models.ForeignKey(Player, on_delete=models.DO_NOTHING, related_name='+')
    played = models.IntegerField(default=2)
    won = models.IntegerField(default=2)
    win_loss = models.FloatField(default=2)
    point_differential = models.FloatField(default=2)
    relationship = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'player_player_stats'

    @property
    def meta_score(self):
        return self.win_loss * self.point_differential

    @classmethod
    def update(cls):
        summary_sql_with = """   INSERT INTO player_player_stats (SELECT UUID() as id, my_teams.player_id as my_player_id, their_teams.player_id as their_player_id, sum(1) as played, SUM(won) as won, (sum(won)/Sum(1)) as win_loss, AVG(t.point_differential) as point_differential, "WITH" as relationship
                    FROM team_manager_team_players my_teams 
                    INNER JOIN team_manager_team_players their_teams on my_teams.team_id = their_teams.team_id
                    INNER JOIN team_manager_team t ON my_teams.team_id = t.id
                    INNER JOIN team_manager_game_teams gt on gt.team_id = t.id 
                    INNER JOIN team_manager_game g on g.id = gt.game_id 
                    INNER JOIN team_manager_gymsession gs on gs.id = g.gym_session_id 
                    WHERE my_teams.player_id=PLAYER1
                    AND their_teams.player_id=PLAYER2
                    AND their_teams.player_id<>PLAYER1
                    AND g.end_time IS NOT NULL
                    AND gs.created_at > DATE_SUB(NOW(), INTERVAL 180 DAY) 
                    GROUP BY 1,2);"""

        summary_sql_against = """   INSERT INTO player_player_stats (SELECT 
                                     UUID() as id, 
                                     me.player_id as my_player_id, 
                                     them.player_id as their_player_id, 
                                     sum(1) as played,
                                     SUM(won) as won, (sum(won)/Sum(1)) as win_loss, AVG(point_differential) as point_differential, "OPP"
                                FROM 
                                (SELECT gt.game_id, my_teams.team_id, my_teams.player_id, t.won, t.point_differential
                                FROM team_manager_team_players my_teams 
                                INNER JOIN team_manager_team t ON my_teams.team_id = t.id
                                INNER JOIN team_manager_game_teams gt ON gt.team_id = t.id 
                                WHERE my_teams.player_id=PLAYER1) me
                                INNER JOIN 
                                (SELECT gt.game_id, their_teams.team_id, their_teams.player_id
                                FROM team_manager_team_players their_teams 
                                INNER JOIN team_manager_team t ON their_teams.team_id = t.id
                                INNER JOIN team_manager_game_teams gt ON gt.team_id = t.id 
                                WHERE their_teams.player_id=PLAYER2) them
                                ON me.game_id = them.game_id
                                WHERE me.team_id <> them.team_id
                                GROUP BY 1,2);"""

        players1 = Player.objects.all()
        players2 = Player.objects.all()

        computed_pairs = []
        with connection.cursor() as cursor:
            cursor.execute("TRUNCATE player_player_stats;")

            for player in players1:
                for other_player in players2:
                    str_sql_w = summary_sql_with.replace("PLAYER1", str(player.id)).replace("PLAYER2", str(other_player.id))
                    str_sql_a = summary_sql_against.replace("PLAYER1", str(player.id)).replace("PLAYER2", str(other_player.id))

                    pair_key1 = "%s-%s" % (player.id, other_player.id)
                    pair_key2 = "%s-%s" % (other_player.id, player.id)

                    #if (pair_key1 not in computed_pairs) and (pair_key2 not in computed_pairs):
                    print str_sql_w
                    cursor.execute(str_sql_w)

                    print str_sql_a
                    cursor.execute(str_sql_a)

                    #    computed_pairs.append(pair_key1)
                    #    computed_pairs.append(pair_key2)

class GymSlot(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    players = models.ManyToManyField(Player)
    status = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=400, blank=True, null=True)
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

    @property
    def location_parsed(self):
        if self.location != None:
            try:
                new_location_list = self.location.split(",")
                new_location = {}
                new_location['name'] = new_location_list[0]
                new_location['street'] = new_location_list[1]
                new_location['city'] = new_location_list[2]
                new_location['state'] = new_location_list[3].split()[0]
                new_location['zipcode'] = new_location_list[3].split()[1]
            except:
                new_location = self.location

            return new_location
        else:
            return self.location


    @property
    def black_out_dates_parsed(self):
        if self.black_out_dates == '':
            return "None"
        else:
            return self.black_out_dates


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

    #def __str__(self):
    #    return self.start_time

    class Meta:
        ordering = ('-start_time',)

class Team(models.Model):
    name = models.CharField(max_length=200)
    players = models.ManyToManyField(Player)
    score = models.IntegerField(null=True)
    won = models.NullBooleanField(null=True)
    point_differential = models.IntegerField(null=True)

    def __str__(self):
        return self.name   

    def update_results(self):
        point_differential = Team.objects.raw("""SELECT t.id, t.score - t2.score as point_differential 
                                                    FROM team_manager_team t INNER JOIN team_manager_game_teams gt on gt.team_id = t.id 
                                                    INNER JOIN team_manager_game_teams gt2 ON gt.game_id = gt2.game_id AND gt2.team_id <> t.id 
                                                    INNER JOIN team_manager_team t2 on t2.id = gt2.team_id 
                                                    WHERE t.id = %s;""" % (self.id))[0]

        if point_differential.point_differential > 0:
            self.won = True

        self.point_differential = point_differential.point_differential
        self.save()




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
                player['win_contribution'] = player['win_contribution']
                player['score_contribution'] = player['score_contribution']
                

                ## Collect the Score and Win Contribution Model Weights
                score_contribution = model_weights['score_contribution']
                win_contribution = model_weights['win_contribution']
                #del ['score_contribution']
                #del ['win_contribution']
                
                #print model_weights
                for k,v in model_weights.items():
                    #print v
                    if 1==1: #v.isnumeric():
                        #print("%s - %s" % (k,v))
                        player[k] = float(player[k]) * float(v)

                player['player_score'] = mean([player['scoring'], player['outside_shooting'], player['passing'], player['rebounding'], player['defend_large'], player['defend_fast'], player['movement'], player['awareness'], player['size']])

                if win_contribution:
                    player['player_score'] = player['player_score'] * (player['win_contribution'] + 1)


                if score_contribution:
                    player['player_score'] = player['player_score'] * player['score_contribution']

                print "%s: %s" % (player['id'], player['player_score'])


            else:
                print("DID NOT FIND STATS FOR %s" % (player['id']))
                player['player_score'] = 2


        #Sort by Scoring and Assign Worst to A and then B
        sl = sorted(players, key=itemgetter('scoring', 'player_score'), reverse=False)
        team_a.append(sl.pop(0))
        team_b.append(sl.pop(0))
        

        if group_size < 4:
            return teams



        ### Scoring Existing Teams for player_score and Assign Best Player Score to Worst Team
        sl = sorted(sl, key=itemgetter('player_score'), reverse=True)

        sorted_team = Team.sort_team_on_metric(teams, 'player_score')
        if sorted_team['team_a'] < sorted_team['team_a']:
            team_a.append(sl.pop(0))
            team_b.append(sl.pop(0))
        else:
            team_b.append(sl.pop(0))
            team_a.append(sl.pop(0))

        if group_size < 6:
            return teams

        ### Scoring Existing Teams for OutSide Shooting and Assign Best Shooter to Worst Team
        sl = sorted(sl, key=itemgetter('player_score'), reverse=True)

        sorted_team = sort_team_on_metric_size(teams, 'player_score')
        if sorted_team['team_a'] < sorted_team['team_b']:
            team_a.append(sl.pop(0))
            team_b.append(sl.pop(0))
        else:
            team_b.append(sl.pop(0))
            team_a.append(sl.pop(0))

        if group_size < 8:
            return teams

        ### Scoring Existing Teams for player_score and Assign Best  player_score to Worst Team
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


        ### Sort by Ball Handler and Assign Best Ball Handlers to Teams A and B
        sl = sorted(sl, key=itemgetter('ball_handler', 'player_score'), reverse=True)        
        team_b.append(sl.pop(0))
        team_a.append(sl.pop(0))



        ### Calculate Team Scores
        sorted_team = Team.sort_team_on_metric(teams, 'player_score')
        team_score = {'team_a': sorted_team['team_a'], 'team_b': sorted_team['team_b']}
        if abs(sorted_team['team_a'] - sorted_team['team_b']) > 2:
            print("Model Error: The Teams are Mismatched: %s" % (team_score))

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
        return "%s: %s (%s)"  % (self.name, self.start_time, self.game_duration_friendly)

    def end_game(self):
        self.end_time = datetime.now() - timedelta(hours=7)
        self.save()

    @property
    def game_duration(self):
        if self.end_time != None:
            return self.end_time - self.start_time
        else:
            return self.start_time - self.start_time

    @property
    def game_duration_friendly(self):
        min_secs = divmod(self.game_duration.days * 86400 + self.game_duration.seconds, 60)
        return "%s Minutes and %s Seconds" % (min_secs[0], min_secs[1])

    @property
    def game_duration_minutes(self):
        min_secs = divmod(self.game_duration.days * 86400 + self.game_duration.seconds, 60)
        return min_secs[0]



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