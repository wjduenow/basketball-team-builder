from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login),
    url(r'^accounts/login/$', views.login),
    url(r'^logout/$', views.logout),
    url(r'^start_gym_slot_session/([0-9]*)$', views.start_gym_slot_session, name='start_gym_slot_session'),
    url(r'create_gym_session$', views.create_gym_session, name='create_gym_session'),
    url(r'^update_player_stats$', views.update_player_stats, name='update_player_stats'),
    url(r'player_stats$', views.player_stats, name='player_stats'),
    url(r'players$', views.players, name='players'),
    url(r'^player/([0-9]*)$', views.view_player, name='view_player'),
    url(r'^player_win_loss/([0-9]*)$', views.player_win_loss, name='player_win_loss'),
    url(r'^edit_player/([0-9]*)$', views.edit_player, name='edit_player'),
    url(r'^new_player$', views.new_player, name='new_player'),
    url(r'^add_update_player$', views.add_update_player, name='add_update_player'),
    url(r'^edit_profile$', views.edit_profile, name='edit_profile'),
    url(r'gym_slots$', views.gym_slots, name='gym_slots'),
    url(r'^new_gym_slot$', views.new_gym_slot, name='new_gym_slot'),
    url(r'^edit_gym_slot/([0-9]*)$', views.edit_gym_slot, name='edit_gym_slot'),
    url(r'^add_update_gym_slot$', views.add_update_gym_slot, name='add_update_gym_slot'),
    url(r'^new_game/([0-9]*)$', views.new_game, name='new_game'),
    url(r'^game/([0-9]*)$', views.view_game, name='view_game'),
    url(r'^edit_game/([0-9]*)$', views.edit_game, name='edit_game'),
    url(r'^gym_slot/([0-9]*)$', views.view_gym_slot, name='view_gym_slot'),
    url(r'^gym_session/([0-9]*)$', views.view_gym_session, name='view_gym_session'),
    url(r'^edit_gym_session/([0-9]*)$', views.edit_gym_session, name='edit_gym_session'),
    url(r'^start_game/([0-9]*)$', views.start_game, name='start_game'),
    url(r'^add_player_to_session$', views.add_player_to_session, name='add_player_to_session'),
    url(r'^remove_player_from_session$', views.remove_player_from_session, name='remove_player_from_session'),
    url(r'^add_player_to_team$', views.add_player_to_team, name='add_player_to_team'),
    url(r'^remove_player_from_team$', views.remove_player_from_team, name='remove_player_from_team'),
    url(r'^add_player_to_gym_slot$', views.add_player_to_gym_slot, name='add_player_to_gym_slot'),
    url(r'^remove_player_from_gym_slot$', views.remove_player_from_gym_slot, name='remove_player_from_gym_slot'),
    url(r'^update_game_stats$', views.update_game_stats, name='update_game_stats'),
    url(r'^test_task$', views.test_task, name='test_task'),
    url(r'^usage/([0-9]*)$', views.start_gym_slot_session, name='start_gym_slot_session'),
]


