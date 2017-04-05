from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^start_gym_slot_session/([0-9]*)$', views.start_gym_slot_session, name='start_gym_slot_session'),
    url(r'^gym_slot_session/([0-9]*)$', views.gym_slot_session, name='gym_slot_session'),
    url(r'^gym_slot_session_update/([0-9]*)$', views.gym_slot_session_update, name='gym_slot_session_update'),
    url(r'^gym_slot_session_create/([0-9]*)$', views.gym_slot_session_create, name='gym_slot_session_create'),
    url(r'players$', views.players, name='players'),
    url(r'^usage/([0-9]*)$', views.start_gym_slot_session, name='start_gym_slot_session2'),
]


