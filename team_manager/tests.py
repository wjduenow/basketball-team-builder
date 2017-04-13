from django.test import TestCase
from .models import Player, Group, GymSlot, GymSession, Game, Team, TeamPlayer, PlayerStats

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
        players = Player.objects.all()
        for player in players:
    		print player.first_name

        self.assertEqual(1,1)
        self.assertEqual(2,2)

