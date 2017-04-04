from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.template.context_processors import csrf
from datetime import datetime

from .models import Player, Group, GymSlot, GymSession, Game, Team, TeamPlayer



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

    context = ({'players': players, 'gym_slot_id': gym_slot_id, 'gym_slot': gym_slot})
    return HttpResponse(template.render(context, request))

# Create your views here.

