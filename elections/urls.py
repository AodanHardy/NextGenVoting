from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('add/', views.election_details, name='add_election'),
    path('add/ballots/', views.add_ballots, name='add_ballots'),
    path('add/candidates/', views.add_candidates, name='add_candidates'),
    path('add/voters', views.add_voters, name='add_voters'),
    path('add/review_election',  views.review_election, name='review_election'),
    path('elections/<int:election_id>/', views.manage_election, name='manage_election'),
]


