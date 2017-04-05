from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import RequestContext
from django.template import loader
from django.template.context_processors import csrf
from datetime import datetime

from .models import Player, Group, GymSlot, GymSession, Game, Team, TeamPlayer, PlayerStats



def index(request):
    #return HttpResponse("Hello, world. You're at the team manager index.")
    template = loader.get_template('team_manager/index.html')

    gym_slots_today = GymSlot.objects.filter(start_date__lte = datetime.now()).filter(end_date__gte = datetime.now()).filter(day_of_week = datetime.now().weekday()).all()
    gym_slots_other = GymSlot.objects.filter(start_date__lte = datetime.now()).filter(end_date__gte = datetime.now()).exclude(day_of_week = datetime.now().weekday()).all()
    context = ({'gym_slots_today': gym_slots_today, 'gym_slots_other': gym_slots_other})
    return HttpResponse(template.render(context, request))

def start_gym_slot_session(request, gym_slot_id=None):
    template = loader.get_template('team_manager/start_gym_slot_session.html')

    gym_slot = GymSlot.objects.get(id = gym_slot_id)
    players = gym_slot.players.all().order_by('last_name')
    sessions = GymSession.objects.filter(gym_slot = gym_slot).all()

    context = ({'players': players, 'gym_slot_id': gym_slot_id, 'gym_slot': gym_slot, 'sessions': sessions})
    return HttpResponse(template.render(context, request))

def gym_slot_session(request, gym_session_id=None):
    template = loader.get_template('team_manager/gym_slot_session.html')

    gym_slot = GymSession.objects.get(id = gym_session_id)
    players = gym_slot.players.all().order_by('last_name')

    context = ({'players': players, 'gym_slot_id': gym_slot_id, 'gym_slot': gym_slot})
    return HttpResponse(template.render(context, request))

def gym_slot_session_update(request, gym_session_id=None):
    template = loader.get_template('team_manager/start_gym_slot_session.html')

    gym_slot = GymSession.objects.get(id = gym_session_id)
    players = gym_slot.players.all().order_by('last_name')

    context = ({'players': players, 'gym_slot_id': gym_slot_id, 'gym_slot': gym_slot})
    return HttpResponse(template.render(context, request))

def gym_slot_session_create(request, gym_slot_id=None):
    template = loader.get_template('team_manager/start_gym_slot_session.html')

    gym_slot = GymSlot.objects.get(id = gym_slot_id)
    players = gym_slot.players.all().order_by('last_name')
    gym_session = GymSession.objects.create(gym_slot = gym_slot)
    gym_session.players = players
    gym_session.save()


    context = ({'players': players, 'gym_slot_id': gym_slot_id, 'gym_slot': gym_slot})
    return HttpResponse(template.render(context, request))

def players(request):
    template = loader.get_template('team_manager/players.html')
    players = Player.objects.all().order_by('last_name')
    player_ids = [int(p.id) for p in players]
    stats = PlayerStats.objects.raw("SELECT * FROM team_manager_playerstats s WHERE s.id in (SELECT MAX(id) as id FROM team_manager_playerstats GROUP BY player_id);")
    stats_dict = {}

    for stat in stats:
        stats_dict[stat.player_id] = stat

    #for player in players:
    #    player.stats = player.current_stats
    for player in players:
        if player.id in stats_dict:
            player.stats = stats_dict[int(player.id)]

    context = ({'players': players, 'player_ids': player_ids})
    return HttpResponse(template.render(context, request))

def update_player_stats(request):

    #players = Player.objects.all()#.order_by('last_name')

    for key in request.POST:
        print(key)
        value = request.POST[key]
        print(value)

    print("############")

    print(request.POST["player_ids"])

    for id in request.POST["player_ids"].split():
        print id

    #for player in players:
    #    print(player.id)
        #print(request.POST["stats[" + str(player.id) + "]scoring"])


    return redirect(players)



