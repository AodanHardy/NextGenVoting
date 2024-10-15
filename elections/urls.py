from django.urls import path, include
from django.contrib.auth import views as auth_views

import elections
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.election_details, name='add_election'),
    path('add/ballots/', views.add_ballots, name='add_ballots'),

]
