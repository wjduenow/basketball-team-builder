from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.template import RequestContext
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.template import loader
from django.template.context_processors import csrf
from django.contrib import messages
from datetime import datetime, timedelta
from django.contrib.auth.models import User
import json
import operator
from django.http import JsonResponse
from .forms import PlayerForm




from .models import Player, Group, GymSlot, GymSession, Game, Team, PlayerStats, PlayerSummary


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
    messages.success(request, 'You have successfully logged out.')
    return HttpResponseRedirect("/")
    
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


def create_gym_session(request):
    gym_slot = GymSlot.objects.get(id = request.POST['gym_slot_id'])

    today = datetime.now().date()
    gym_session = GymSession.objects.filter(gym_slot = gym_slot).filter(created_at__date = today)

    if gym_session:
        print("Found Existing Session")
        gym_session = gym_session[0]
    else:
        print("Creating Session Session")
        gym_session = GymSession.objects.create(gym_slot = gym_slot)

    return HttpResponseRedirect('/gym_session/' + str(gym_session.id))

def player_win_loss(request, player_id=None):
    ps = PlayerSummary.objects.filter(player_id = player_id).values('game_date', 'win_loss')

    ps2 = [{'date': '24-Apr-07','close': '93.24'},
          {'date': '25-Apr-07','close': '95.35'},
          {'date': '26-Apr-07','close': '98.84'},
          {'date': '27-Apr-07','close': '99.92'},
          {'date': '30-Apr-07','close': '99.80'},
          {'date': '1-May-07','close': '99.47'}]


    return JsonResponse(list(ps), safe=False)


def view_gym_slot(request, gym_slot_id=None):
    template = loader.get_template('team_manager/gym_slot.html')
    gym_slot = GymSlot.objects.get(id = gym_slot_id)

    today = datetime.now().date()

    context = ({'gym_slot': gym_slot, 'today': today})
    return HttpResponse(template.render(context, request))

def view_player(request, player_id=None):
    template = loader.get_template('team_manager/player.html')
    player = Player.objects.get(id = player_id)

    context = ({'player': player})
    return HttpResponse(template.render(context, request))


def new_player(request):
    template = loader.get_template('team_manager/player_form.html')
    player = "Add Player"
    form = PlayerForm()

    context = ({'player': player, 'form': form})
    return HttpResponse(template.render(context, request))

def add_update_player(request):
    #print request.POST.dict
    print request.POST.getlist('player*')
    template = loader.get_template('team_manager/player_form.html')
    

    if request.method == "POST":
        if 'player_id' in request.POST:
            player = Player.objects.get(id = request.POST['player_id'])
            form = PlayerForm(request.POST, instance=player)
        else: 
            form = PlayerForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('/players')
    else:
        form = PostForm()

    context = ({'player': player, 'form': form})
    return HttpResponse(template.render(context, request))

def edit_player(request, player_id=None):
    template = loader.get_template('team_manager/player_form.html')
    player = Player.objects.get(id = player_id)

    form = PlayerForm(instance=player)

    context = ({'player': player, 'form': form})
    return HttpResponse(template.render(context, request))

def view_gym_session(request, gym_session_id=None):
    template = loader.get_template('team_manager/start_gym_slot_session.html')
    gym_session = GymSession.objects.get(id = gym_session_id)

    available_players = Player.objects.exclude(pk__in=gym_session.players.values_list('id', flat=True)).filter(pk__in=gym_session.gym_slot.players.values_list('id', flat=True))

    context = ({'gym_session': gym_session, 'available_players': available_players})
    return HttpResponse(template.render(context, request))

def view_game(request, game_id=None):
    template = loader.get_template('team_manager/game.html')
    game = Game.objects.get(id = game_id)

    team_scores = {} ## Used for Stores Scores to Calculate the Winner
    if request.method == 'POST':
        for team in game.teams.all():
            team.score = int(request.POST[str(team.id)])
            team_scores[team.id] = team.score
            team.won = False
            team.save()

        ## Find the Winner and Save
        winning_team = max(team_scores.iteritems(), key=operator.itemgetter(1))[0]
        winner = Team.objects.get(id = winning_team)
        winner.won = True
        winner.save()

        #Set the Game End Time Unless it is already set
        if game.end_time == None:
            game.end_time = datetime.now()
            game.save()
            game = Game.objects.get(id = game_id) # For Some Reason Game Length is being nulled on save


    scores = range(0, 21)
    game_end = game.created_at + timedelta(minutes=21) + timedelta(hours=0)

    context = ({'game': game, 'game_end': game_end, 'scores': scores})
    return HttpResponse(template.render(context, request))


def start_game(request, gym_session_id=None):
    #template = loader.get_template('team_manager/game.html')
    team_a_ids = [ int(x) for x in request.POST.getlist('team_a[]') ]
    team_b_ids = [ int(x) for x in request.POST.getlist('team_b[]') ]
    team_a_players = Player.objects.filter(pk__in=team_a_ids)
    team_b_players = Player.objects.filter(pk__in=team_b_ids)

    today = datetime.now().strftime("%Y-%m-%d")

    gym_session = GymSession.objects.get(id = gym_session_id)
    new_game = Game.objects.create(gym_session = gym_session)

    team_a = Team.objects.create(name = 'Team A')
    team_a.players = team_a_players
    team_a.save()

    team_b = Team.objects.create(name = 'Team B')
    team_b.players = team_b_players
    team_b.save()

    new_game.teams = [team_a, team_b]
    new_game.save()



    teams = {'team_a': team_a, 'team_b': team_b}



    context = ({'teams': teams, 'game': new_game, 'gym_session': gym_session})
    return HttpResponseRedirect('/game/' + str(new_game.id))
    #return HttpResponse(template.render(context, request))

def new_game(request, gym_session_id=None, teams=None):
    template = loader.get_template('team_manager/new_game.html')

    teams = json.loads(request.POST['teams'])

    team_a_ids = [ int(x) for x in request.POST.getlist('team_a[]') ]
    team_b_ids = [ int(x) for x in request.POST.getlist('team_b[]') ]
    team_a = []
    team_b = []

    #for team, players in teams.items():
    #    if team == 'team_a':
    players = Player.objects.values()
    for player in players:
        if int(player['id']) in team_a_ids:
            team_a.append(player)

    #    if team == 'team_b':
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
            player['player_score'] = stats_dict[int(player['id'])].player_score

    for player in team_b:
        if player['id'] in stats_dict:
            player['stats'] = stats_dict[int(player['id'])]
            player['player_score'] = stats_dict[int(player['id'])].player_score

    teams = {'team_a': team_a, 'team_b': team_b}

    if teams:
        sorted_team = Team.sort_team_on_metric(teams, 'player_score')
        team_score = {'team_a': sorted_team['team_a'], 'team_b': sorted_team['team_b']}
        sorted_team_size = Team.sort_team_on_metric(teams, 'size')
        team_size = {'team_a': sorted_team_size['team_a'], 'team_b': sorted_team_size['team_b']}


    gym_session = GymSession.objects.get(id = gym_session_id)

    context = ({'players': players, 'gym_session_id': gym_session.id, 'gym_session': gym_session, 'teams': teams, 'team_score': team_score, 'team_size': team_size})
    return HttpResponse(template.render(context, request))

def start_gym_slot_session(request, gym_session_id=None):
    template = loader.get_template('team_manager/start_gym_slot_session2.html')

    players_group = request.POST.getlist('players_group[]')
    teams = ""
    team_score = ""
    team_size = ""

    model_weights = {'scoring': request.POST.get("scoring", '1'), 
                     'outside_shooting': request.POST.get("outside_shooting", '1'), 
                     'passing': request.POST.get("passing", '1'), 
                     'rebounding': request.POST.get("rebounding", '1'),  
                     'defend_large': request.POST.get("defend_large", '1'),  
                     'defend_fast': request.POST.get("defend_fast", '1'), 
                     'movement': request.POST.get("movement", '1'), 
                     'awareness': request.POST.get("awareness", '1'), 
                     'size': request.POST.get("size", '2')}

    if players_group:
        teams = Team.make_team(players_group, model_weights)
        sorted_team = Team.sort_team_on_metric(teams, 'player_score')
        team_score = {'team_a': sorted_team['team_a'], 'team_b': sorted_team['team_b']}

        sorted_team_size = Team.sort_team_on_metric(teams, 'size')
        team_size = {'team_a': sorted_team_size['team_a'], 'team_b': sorted_team_size['team_b']}

    players_group = map(int, players_group)
    gym_session = GymSession.objects.get(id = gym_session_id)
    players = gym_session.players.order_by('first_name')
    
    context = ({'players': players, 'gym_session_id': gym_session_id, 'gym_session': gym_session, 'teams_json': json.dumps(teams, default=date_handler), 'teams': teams, 'players_group': players_group, 'team_score': team_score, 'team_size': team_size, 'model_weights': model_weights})
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

#def gym_slot_session_create(request, gym_slot_id=None):
#    template = loader.get_template('team_manager/start_gym_slot_session.html')
#
#    gym_slot = GymSlot.objects.get(id = gym_slot_id)
#    players = gym_slot.players.all().order_by('last_name')
#    gym_session = GymSession.objects.create(gym_slot = gym_slot)
#    gym_session.players = players
#    gym_session.save()
#
#
#    context = ({'players': players, 'gym_slot_id': gym_slot_id, 'gym_slot': gym_slot})
#    return HttpResponse(template.render(context, request))

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

@require_http_methods(["POST"])
def add_player_to_session(request):
    print request.POST.dict
    gym_session = GymSession.objects.get(id = request.POST['gym_session_id'])
    player = Player.objects.get(id = request.POST['player_id'])
    gym_session.players.add(player)

    data = {'success': True}

    return JsonResponse(data)

@require_http_methods(["POST"])
def remove_player_from_session(request):
    print request.POST.dict
    gym_session = GymSession.objects.get(id = request.POST['gym_session_id'])
    player = Player.objects.get(id = request.POST['player_id'])
    gym_session.players.remove(player)

    data = {'success': True}

    return JsonResponse(data)

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError

