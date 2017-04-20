from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.template import loader
from django.template.context_processors import csrf
from django.contrib import messages
from datetime import datetime, timedelta
from django.contrib.auth.models import User
import json



from .models import Player, Group, GymSlot, GymSession, Game, Team, PlayerStats


#Form to login  
def login(request):
    if request.method == 'POST':
        identifier = request.POST['identifier']
        password = request.POST['password']
        users = User.objects.filter(email = identifier)
        if len(users) == 1:
            username = users[0].username
        else:
            username = identifier
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth_login(request, user)
            messages.success(request, 'Welcome ' + str(username) + ', you are now logged in!')
            return HttpResponseRedirect("/")
    else:
        template = loader.get_template('team_manager/login.html')
        context = {}
        return HttpResponse(template.render(context, request))
    messages.error(request, 'Email or password are invalid!')
    return HttpResponseRedirect("team_manager//login/")

#Logs a user out, redirects to login page
def logout(request):
    auth_logout(request)
    #template = loader.get_template('team_manager/login.html')
    #context = {}
    messages.success(request, 'You have successfully logged out.')
    return HttpResponseRedirect("/")
    #return HttpResponse(template.render(context, request))
    


def index(request):
    #return HttpResponse("Hello, world. You're at the team manager index.")
    template = loader.get_template('team_manager/index.html')
    today = (datetime.now() - timedelta(hours=8)).strftime("%A")
    print((datetime.now() - timedelta(hours=8)))
    print(today)
    gym_slots_today = GymSlot.objects.filter(start_date__lte = datetime.now()).filter(end_date__gte = datetime.now()).filter(day_of_week = today).all()
    gym_slots_other = GymSlot.objects.filter(start_date__lte = datetime.now()).filter(end_date__gte = datetime.now()).exclude(day_of_week = today).all()
    context = ({'gym_slots_today': gym_slots_today, 'gym_slots_other': gym_slots_other})
    return HttpResponse(template.render(context, request))

def view_game(request, game_id=None):
    template = loader.get_template('team_manager/game.html')
    game = Game.objects.get(id = game_id)

    game_end = game.created_at + timedelta(minutes=20) + timedelta(hours=0)

    gym_session = game.gym_session
    teams = Team.objects.filter(game_id = game_id)

    context = ({'teams': teams, 'game': game, 'gym_slot': gym_session.gym_slot, 'game_end': game_end})
    return HttpResponse(template.render(context, request))


def start_game(request, gym_slot_id=None):
    #template = loader.get_template('team_manager/game.html')
    team_a_ids = [ int(x) for x in request.POST.getlist('team_a[]') ]
    team_b_ids = [ int(x) for x in request.POST.getlist('team_b[]') ]
    team_a_players = Player.objects.filter(pk__in=team_a_ids)
    team_b_players = Player.objects.filter(pk__in=team_b_ids)

    today = datetime.now().strftime("%Y-%m-%d")

    gym_slot = GymSlot.objects.get(id = gym_slot_id)

    gym_session = GymSession.objects.filter(gym_slot = gym_slot).filter(created_at__date = today)

    if gym_session:
        print("Found Existing Session")
        gym_session = gym_session[0]
    else:
        print("Creating Session Session")
        gym_session = GymSession.objects.create(gym_slot = gym_slot)

    new_game = Game.objects.create(gym_session = gym_session)

    team_a = Team.objects.create(game = new_game, name = 'Team A')
    team_a.players = team_a_players
    team_a.save

    team_b = Team.objects.create(game = new_game, name = 'Team B')
    team_b.players = team_b_players
    team_b.save

    teams = {'team_a': team_a, 'team_b': team_b}



    context = ({'teams': teams, 'game': new_game, 'gym_slot': gym_slot})
    return HttpResponseRedirect('/game/' + str(new_game.id))
    #return HttpResponse(template.render(context, request))

def new_game(request, gym_slot_id=None, teams=None):
    template = loader.get_template('team_manager/new_game.html')

    teams = json.loads(request.POST['teams'])

    team_a_ids = [ int(x) for x in request.POST.getlist('team_a[]') ]
    team_b_ids = [ int(x) for x in request.POST.getlist('team_b[]') ]
    team_a = []
    team_b = []

    for team, players in teams.items():
        if team == 'team_a':
            for player in players:
                if int(player['id']) in team_a_ids:
                    team_a.append(player)

        if team == 'team_b':
            for player in players:
                if int(player['id']) in team_b_ids:
                    team_b.append(player)
     
    stats = PlayerStats.objects.raw("SELECT * FROM team_manager_playerstats s WHERE s.id in (SELECT MAX(id) as id FROM team_manager_playerstats GROUP BY player_id);")
    stats_dict = {}

    for stat in stats:
        stats_dict[stat.player_id] = stat

    #for player in players:
    for player in team_a:
        if player['id'] in stats_dict:
            player['stats'] = stats_dict[int(player['id'] )]
            player['player_score'] = player['player_score']#, 2)

    for player in team_b:
        if player['id'] in stats_dict:
            player['stats'] = stats_dict[int(player['id'])]
            player['player_score'] = player['player_score']#, 2)

    teams = {'team_a': team_a, 'team_b': team_b}

    if teams:
        sorted_team = Team.sort_team_on_metric(teams, 'player_score')
        team_score = {'team_a': sorted_team['team_a'], 'team_b': sorted_team['team_b']}
        sorted_team_size = Team.sort_team_on_metric(teams, 'size')
        team_size = {'team_a': sorted_team_size['team_a'], 'team_b': sorted_team_size['team_b']}


    gym_slot = GymSlot.objects.get(id = gym_slot_id)
    sessions = GymSession.objects.filter(gym_slot = gym_slot).all()

    context = ({'players': players, 'gym_slot_id': gym_slot_id, 'gym_slot': gym_slot, 'sessions': sessions, 'teams': teams, 'team_score': team_score, 'team_size': team_size})
    return HttpResponse(template.render(context, request))

def start_gym_slot_session(request, gym_slot_id=None):
    template = loader.get_template('team_manager/start_gym_slot_session.html')

    players_group = request.POST.getlist('players_group[]')
    teams = ""
    team_score = ""
    team_size = ""

    model_weights = {'scoring': request.POST.get("scoring", 1), 
                     'outside_shooting': request.POST.get("outside_shooting", 1), 
                     'passing': request.POST.get("passing", 1), 
                     'rebounding': request.POST.get("rebounding", 1),  
                     'defend_large': request.POST.get("defend_large", 1),  
                     'defend_fast': request.POST.get("defend_fast", 1), 
                     'movement': request.POST.get("movement", 1), 
                     'awareness': request.POST.get("awareness", 1), 
                     'size': request.POST.get("size", 1)}

    if players_group:
        teams = Team.make_team(players_group, model_weights)
        sorted_team = Team.sort_team_on_metric(teams, 'player_score')
        team_score = {'team_a': sorted_team['team_a'], 'team_b': sorted_team['team_b']}

        sorted_team_size = Team.sort_team_on_metric(teams, 'size')
        team_size = {'team_a': sorted_team_size['team_a'], 'team_b': sorted_team_size['team_b']}

    players_group = map(int, players_group)
    gym_slot = GymSlot.objects.get(id = gym_slot_id)
    players = gym_slot.players.all().order_by('first_name')
    sessions = GymSession.objects.filter(gym_slot = gym_slot).all()

    context = ({'players': players, 'gym_slot_id': gym_slot_id, 'gym_slot': gym_slot, 'sessions': sessions, 'teams_json': json.dumps(teams, default=date_handler), 'teams': teams, 'players_group': players_group, 'team_score': team_score, 'team_size': team_size, 'model_weights': model_weights})
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

@login_required    
def players(request):
    template = loader.get_template('team_manager/players.html')
    players = Player.objects.all().order_by('last_name')
    player_ids = ','.join([str(p.id) for p in players])
    stats = PlayerStats.objects.raw("SELECT * FROM team_manager_playerstats s WHERE s.id in (SELECT MAX(id) as id FROM team_manager_playerstats GROUP BY player_id);")
    stats_dict = {}

    for stat in stats:
        stats_dict[stat.player_id] = stat

    #for player in players:
    for player in players:
        if player.id in stats_dict:
            player.stats = stats_dict[int(player.id)]
            player.player_score = round(player.stats.player_score, 2)

    context = ({'players': players, 'player_ids': player_ids})
    return HttpResponse(template.render(context, request))

@login_required    
def update_player_stats(request):
    ids = request.POST["player_ids"]
    for id in ids.split(","):
        scoring = request.POST["scoring[" + str(id) + "]"]
        outside_shooting = request.POST["outside_shooting[" + str(id) + "]"]
        passing = request.POST["passing[" + str(id) + "]"]
        rebounding = request.POST["rebounding[" + str(id) + "]"]
        defend_large = request.POST["defend_large[" + str(id) + "]"]
        defend_fast = request.POST["defend_fast[" + str(id) + "]"]
        movement = request.POST["movement[" + str(id) + "]"]
        awareness = request.POST["awareness[" + str(id) + "]"]

        PlayerStats.objects.create(player = Player.objects.get(id = id), scoring = scoring,
                                   outside_shooting = outside_shooting, passing = passing, rebounding = rebounding, 
                                   defend_large = defend_large, defend_fast = defend_fast, movement = movement, awareness = awareness)

    return redirect(players)

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError

