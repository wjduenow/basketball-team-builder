from __future__ import division
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
from .models import Player, Group, GymSlot, GymSession, Game, Team, PlayerStats, PlayerSummary, PlayerPlayerSummary
from django.db.models import Count, Avg, Sum, Min, Max
from operator import itemgetter
from collections import defaultdict
#from analysis import analysis2, create_dataset, analysis

#from google.appengine.api.taskqueue import taskqueue


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
    return HttpResponseRedirect("/login/")

#Logs a user out, redirects to login page
def logout(request):
    auth_logout(request)
    messages.success(request, 'You have successfully logged out.')
    return HttpResponseRedirect("/")

@login_required        
def index(request):
    #return HttpResponse("Hello, world. You're at the team manager index.")
    template = loader.get_template('team_manager/index.html')
    today = (datetime.now() - timedelta(hours=7)).strftime("%A")

    gym_slots_today = GymSlot.objects.filter(start_date__lte = datetime.now()).filter(end_date__gte = datetime.now()).filter(day_of_week = today).all()
    gym_slots_other = GymSlot.objects.filter(start_date__lte = datetime.now()).filter(end_date__gte = datetime.now()).exclude(day_of_week = today).all()
    active_games = Game.objects.filter(end_time = None)
    active_sessions = GymSession.objects.filter(created_at__date = datetime.now())


    total_games = Game.objects.all().aggregate(played=Count('id'))
    leader_qualified_games = int(total_games['played'] * .25)
    tandem_qualified_games = int(total_games['played'] * .10)

    ### Leaderboard Stuff
    player_summary = []
    ps = PlayerSummary.objects.values('player_id').annotate(played__sum=Sum('played'), won__sum = Sum('won'), point_differential__avg = Avg('point_differential')).filter(played__sum__gt=leader_qualified_games)
    for p in ps:
        p['win_ratio'] = p['won__sum'] / p['played__sum']
        p['player'] = Player.objects.get(id = p['player_id'])

    ps_win_ratio = sorted(ps, key=itemgetter('win_ratio'), reverse=True)[:5]
    ps_win_ratio_bad = sorted(ps, key=itemgetter('win_ratio'), reverse=False)[:5]
    ps_point_differential = sorted(ps, key=itemgetter('point_differential__avg'), reverse=True)[:5]
    ps_point_differential_bad = sorted(ps, key=itemgetter('point_differential__avg'), reverse=False)[:5]

    best_tandem_point_differential = PlayerPlayerSummary.objects.filter(relationship='WITH').filter(played__gt=tandem_qualified_games).order_by("-point_differential")[:5]
    best_tandem_win_ratio = PlayerPlayerSummary.objects.filter(relationship='WITH').filter(played__gt=tandem_qualified_games).order_by("-win_loss")[:5]

    best_tandem_point_differential_bad = PlayerPlayerSummary.objects.filter(relationship='WITH').filter(played__gt=tandem_qualified_games).order_by("point_differential")[:5]
    best_tandem_win_ratio_bad = PlayerPlayerSummary.objects.filter(relationship='WITH').filter(played__gt=tandem_qualified_games).order_by("win_loss")[:5]


    best_opponent_point_differential = PlayerPlayerSummary.objects.filter(relationship='OPP').filter(played__gt=tandem_qualified_games).order_by("-point_differential")[:5]
    best_opponent_win_ratio = PlayerPlayerSummary.objects.filter(relationship='OPP').filter(played__gt=tandem_qualified_games).order_by("-win_loss")[:5]

    best_opponent_point_differential_bad = PlayerPlayerSummary.objects.filter(relationship='OPP').filter(played__gt=tandem_qualified_games).order_by("point_differential")[:5]
    best_opponent_win_ratio_bad = PlayerPlayerSummary.objects.filter(relationship='OPP').filter(played__gt=tandem_qualified_games).order_by("win_loss")[:5]


    context = ({'gym_slots_today': gym_slots_today, 'gym_slots_other': gym_slots_other, 'active_games': active_games, 
                'active_sessions': active_sessions, 'ps_win_ratio': ps_win_ratio, 'ps_point_differential': ps_point_differential, 
                'best_tandem_point_differential': best_tandem_point_differential, 'best_tandem_win_ratio': best_tandem_win_ratio, 
                'ps_win_ratio_bad': ps_win_ratio_bad, 'ps_point_differential_bad': ps_point_differential_bad, 
                'best_tandem_point_differential_bad': best_tandem_point_differential_bad,
                'best_tandem_win_ratio_bad': best_tandem_win_ratio_bad,
                'best_opponent_point_differential':best_opponent_point_differential,
                'best_opponent_win_ratio':best_opponent_win_ratio,
                'best_opponent_point_differential_bad':best_opponent_point_differential_bad,
                'best_opponent_win_ratio_bad':best_opponent_win_ratio_bad})

    return HttpResponse(template.render(context, request))

@login_required    
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

@login_required    
def player_win_loss(request, player_id=None):
    ps = PlayerSummary.objects.filter(player_id = player_id).values('game_date', 'win_loss', 'point_differential').order_by('game_date')

    return JsonResponse(list(ps), safe=False)

@login_required    
def view_gym_slot(request, gym_slot_id=None):
    template = loader.get_template('team_manager/gym_slot.html')
    gym_slot = GymSlot.objects.get(id = gym_slot_id)


    today =  datetime.now().date()
    print today
    today = datetime.now().date() - timedelta(hours=8)
    print today

    context = ({'gym_slot': gym_slot, 'today': today})
    return HttpResponse(template.render(context, request))

@login_required    
def view_player(request, player_id=None):
    template = loader.get_template('team_manager/player.html')
    player = Player.objects.get(id = player_id)

    ps = PlayerSummary.objects.filter(player = player).values('player_id').annotate(played__sum=Sum('played'), won__sum = Sum('won'), point_differential__avg = Avg('point_differential'))

    ps_all = PlayerSummary.objects.all().aggregate(played__sum=Sum('played'), won__sum = Sum('won'), point_differential__avg = Avg('point_differential'))
    #pps = PlayerPlayerSummary.objects.filter(player = player_id).exclude(other_player = player_id).all()

    if ps:
        ps[0]['win_ratio'] = (ps[0]['won__sum'] / ps[0]['played__sum']) * 100
        player.player_summary = ps[0]

    context = ({'player': player, 'ps_all': ps_all}) #, 'pps': pps})
    return HttpResponse(template.render(context, request))


@login_required    
def new_player(request):
    template = loader.get_template('team_manager/player_form.html')
    player = "Add Player"
    form = PlayerForm()

    context = ({'player': player, 'form': form})
    return HttpResponse(template.render(context, request))

@login_required    
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

@login_required    
def edit_player(request, player_id=None):
    template = loader.get_template('team_manager/player_form.html')
    player = Player.objects.get(id = player_id)

    form = PlayerForm(instance=player)

    context = ({'player': player, 'form': form})
    return HttpResponse(template.render(context, request))

@login_required    
def view_gym_session(request, gym_session_id=None):
    today =  datetime.now().date()
    gym_session = GymSession.objects.get(id = gym_session_id)

    session_start_time = "Session DB Start: %s - Today: %s" % ((gym_session.start_time - timedelta(hours=7)).date(), today)
    print today

    #if (gym_session.start_time - timedelta(hours=7)).date() == today:
    #    print "This Session is Today"
    template = loader.get_template('team_manager/start_gym_slot_session.html')
    #else:
    #template = loader.get_template('team_manager/gym_slot_session.html')
    

    available_players = Player.objects.exclude(pk__in=gym_session.players.values_list('id', flat=True)).filter(pk__in=gym_session.gym_slot.players.values_list('id', flat=True))

    context = ({'session_start_time': session_start_time, 'gym_session': gym_session, 'available_players': available_players})
    return HttpResponse(template.render(context, request))

@login_required    
def edit_gym_session(request, gym_session_id=None):

    gym_session = GymSession.objects.get(id = gym_session_id)

    if request.user.is_superuser == False:
        return HttpResponseRedirect('/gym_session/' + str(gym_session.id))

    template = loader.get_template('team_manager/start_gym_slot_session.html')
    
       

    available_players = Player.objects.exclude(pk__in=gym_session.players.values_list('id', flat=True)).filter(pk__in=gym_session.gym_slot.players.values_list('id', flat=True))

    context = ({'gym_session': gym_session, 'available_players': available_players})
    return HttpResponse(template.render(context, request))

@login_required    
def view_game(request, game_id=None):
    template = loader.get_template('team_manager/game.html')
    game = Game.objects.get(id = game_id)

    today =  datetime.now().date()

    team_scores = {} ## Used for Stores Scores to Calculate the Winner
    if request.method == 'POST':
        for team in game.teams.all():
            team.score = int(request.POST[str(team.id)])
            team_scores[team.id] = team.score
            team.won = False
            team.save()

        ## Find the Winner and Save Point Differential
        for team in game.teams.all():
            team.update_results()
        
        #Set the Game End Time Unless it is already set
        if game.end_time == None:
            game.end_game()
            game = Game.objects.get(id = game_id) # For Some Reason Game Length is being nulled on save
            Player.update_player_game_stats()


    scores = range(0, 21)
    game_end = game.created_at + timedelta(minutes=21) + timedelta(hours=0)

    context = ({'game': game, 'game_end': game_end, 'scores': scores, 'today': today})
    return HttpResponse(template.render(context, request))


@login_required
def edit_game(request, game_id=None):
    template = loader.get_template('team_manager/edit_game.html')
    game = Game.objects.get(id = game_id)
    print game.start_time.strftime("%Y-%m-%d %H:%M")

    players = []
    for team in game.teams.all():
        for player in team.players.all():
            players.append(player.id)

    available_players = Player.objects.exclude(pk__in=players).filter(pk__in=game.gym_session.players.values_list('id', flat=True))

    today =  datetime.now().date()

    if request.user.is_superuser == False:
        return HttpResponseRedirect('/game/' + str(game.id))

    team_scores = {} ## Used for Stores Scores to Calculate the Winner
    if request.method == 'POST':
        for team in game.teams.all():
            team.score = int(request.POST[str(team.id)])
            team_scores[team.id] = team.score
            team.won = False
            team.save()

        ## Find the Winner and Save Point Differential
        for team in game.teams.all():
            team.update_results()
        
        #Set the Game End Time Unless it is already set
        if game.end_time == None:
            game.end_game()
            game = Game.objects.get(id = game_id) # For Some Reason Game Length is being nulled on save
            Player.update_player_game_stats()

        if request.POST['start_time']:
            game.start_time = datetime.strptime(request.POST['start_time'], "%Y-%m-%d %H:%M")
            game.end_time = datetime.strptime(request.POST['end_time'], "%Y-%m-%d %H:%M")
            game.save()

        messages.success(request, 'The Game has been updated')


    scores = range(0, 21)
    game_end = game.created_at + timedelta(minutes=21) + timedelta(hours=0)

    context = ({'game': game, 'game_end': game_end, 'scores': scores, 'today': today, 'available_players': available_players})
    return HttpResponse(template.render(context, request))


@login_required    
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

@login_required    
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

@login_required    
def start_gym_slot_session(request, gym_session_id=None):
    template = loader.get_template('team_manager/start_gym_slot_session2.html')

    players_group = request.POST.getlist('players_group[]')
    teams = ""
    team_score = ""
    team_size = ""

    rematch_game_id = request.POST.get('game_id')
    if rematch_game_id:
        print "Rematching %s" % (rematch_game_id)
        teams = {'team_a': [], 'team_b': []}
        old_team_ids = Game.objects.get(id = rematch_game_id).teams.values_list('id', flat=True)
        team_a = Game.objects.get(id = rematch_game_id)

        team_a_players = Team.objects.get(id = old_team_ids[0]).players.values()
        for player in team_a_players:
            teams['team_a'].append(player)

        team_b_players = Team.objects.get(id = old_team_ids[1]).players.values()
        for player in team_b_players:
            teams['team_b'].append(player)


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
        print "Using Team Maker"
        teams = Team.make_team(players_group, model_weights)
        sorted_team = Team.sort_team_on_metric(teams, 'player_score')
        team_score = {'team_a': sorted_team['team_a'], 'team_b': sorted_team['team_b']}

        sorted_team_size = Team.sort_team_on_metric(teams, 'size')
        team_size = {'team_a': sorted_team_size['team_a'], 'team_b': sorted_team_size['team_b']}

    selected_players_list = []
    for team in teams:
        for player in teams[team]:
            selected_players_list.append(str(player['id']))

    players_group = map(int, players_group)
    gym_session = GymSession.objects.get(id = gym_session_id)

    players = Player.objects.filter(pk__in=gym_session.players.values_list('id', flat=True)).exclude(pk__in=selected_players_list).order_by('first_name')    
    context = ({'rematch_game_id': rematch_game_id, 'players': players, 'gym_session_id': gym_session_id, 'gym_session': gym_session, 'teams_json': json.dumps(teams, default=date_handler), 'teams': teams, 'players_group': players_group, 'team_score': team_score, 'team_size': team_size, 'model_weights': model_weights})
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

    player_game_summary_dict = {}
    ps = PlayerSummary.objects.values('player_id').annotate(played__sum=Sum('played'), won__sum = Sum('won'), point_differential__avg = Avg('point_differential'))
    for p in ps:
        p['win_ratio'] = p['won__sum'] / p['played__sum']
        player_game_summary_dict[p['player_id']] = p

    #for player in players:
    for player in players:
        if player.id in stats_dict:
            player.stats = stats_dict[int(player.id)]
            player.player_score = round(player.stats.player_score, 2)

        if player.id in player_game_summary_dict:
            player.game_summary = player_game_summary_dict[int(player.id)]


    context = ({'players': players, 'player_ids': player_ids})
    return HttpResponse(template.render(context, request))


@login_required    
def player_stats(request):
    template = loader.get_template('team_manager/player_stats.html')
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

    return HttpResponseRedirect('/player_stats')

###  Background Job Methods ###

def test_task(request):
    #task = taskqueue.add(
    #            url='/update_game_stats',
    #            target='worker',
    #            params={'amount': 1})
    #
    #print task.name
    #print task.eta

    return HttpResponseRedirect('/')




@login_required    
def update_game_stats(request):
    PlayerPlayerSummary.update()
    Player.update_player_game_stats()
    
    #create_dataset.create()
    # win_contributions = analysis2.main()
    # for id, value in win_contributions.items():
    #         player = Player.objects.get(id = id)
    #         player.win_contribution = value
    #         player.save()

    # score_contributions = analysis.score_factors()
    # for id, value in score_contributions.items():
    #         player = Player.objects.get(id = id)
    #         player.score_contribution = value
    #         player.save()

    return HttpResponseRedirect('/')


###  AJAX METHODS  ###
@login_required    
@require_http_methods(["POST"])
def add_player_to_session(request):
    print request.POST.dict
    gym_session = GymSession.objects.get(id = request.POST['gym_session_id'])
    player = Player.objects.get(id = request.POST['player_id'])
    gym_session.players.add(player)

    data = {'success': True}

    return JsonResponse(data)

@login_required    
@require_http_methods(["POST"])
def remove_player_from_session(request):
    print request.POST.dict
    gym_session = GymSession.objects.get(id = request.POST['gym_session_id'])
    player = Player.objects.get(id = request.POST['player_id'])
    gym_session.players.remove(player)

    data = {'success': True}

    return JsonResponse(data)

@login_required    
@require_http_methods(["POST"])
def add_player_to_team(request):
    print request.POST.dict
    team = Team.objects.get(id = request.POST['team_id'])
    player = Player.objects.get(id = request.POST['player_id'])
    team.players.add(player)

    data = {'success': True}

    return JsonResponse(data)

@login_required    
@require_http_methods(["POST"])
def remove_player_from_team(request):
    print request.POST.dict
    team = Team.objects.get(id = request.POST['team_id'])
    player = Player.objects.get(id = request.POST['player_id'])
    team.players.remove(player)

    data = {'success': True}

    return JsonResponse(data)

##3 Helper Methods

def mean(numbers):
    return float(sum(numbers)) / max(len(numbers), 1)

def date_handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    else:
        raise TypeError

