from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^start_gym_slot_session/([0-9]*)$', views.start_gym_slot_session, name='start_gym_slot_session'),
    url(r'^usage/([0-9]*)$', views.start_gym_slot_session, name='start_gym_slot_session2'),
]


