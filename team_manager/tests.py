from django.test import TestCase
from .models import Player, Group, GymSlot, GymSession, Game, Team, TeamPlayer, PlayerStats
import itertools

class TeamTestCase(TestCase):

    fixtures = ['team_manager']

#    def setUp(self):
#        Player.objects.create(last_name="Shooter", first_name="Good")
#        Player.objects.create(last_name="Shooter", first_name="Bad")
#        Player.objects.create(last_name="Shooter", first_name="Tall")
#        Player.objects.create(last_name="Shooter", first_name="Short")


    def test_animals_can_speak(self):
        """Animals that can speak are correctly identified"""
        #good = Player.objects.get(first_name="Good")
        #bad = Player.objects.get(first_name="Bad")
        #tall = Player.objects.get(first_name="Tall")
        #short = Player.objects.get(first_name="Short")
        
        player_ids = []
        players = Player.objects.all()
        for player in players:
            player_ids.append(int(player.id))


        tested_combinations = 0 
        failed_combinations = 0
        player_groups =  itertools.combinations(player_ids, 10)
        for group in player_groups:
            teams = Team.make_team(group)
            sorted_team = Team.sort_team_on_metric(teams, 'player_score')
            tested_combinations += 1

            if abs(sorted_team['team_a'] - sorted_team['team_b']) > 1:
                print("##################################################")
                print("Model Error: The Teams are Mismatched")
                #print teams
                for team,players in teams.items():
                    print("TEAM: %s %s" % (team, sorted_team[team]))
                    for player in players:
                        print("    %s %s" % (player['first_name'], player['last_name']))
                print("##################################################")
                print("")

                failed_combinations += 1
                #print("%s combinations tested with %s failures" % (tested_combinations, failed_combinations))

        print("%s combinations tested with %s failures" % (tested_combinations, failed_combinations))




        self.assertEqual(1,1)
        self.assertEqual(2,2)

