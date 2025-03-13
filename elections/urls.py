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
    path("election/<int:election_id>/edit/", views.edit_election, name="edit_election"),
    path('add_new_ballot/<int:election_id>/', views.add_new_ballot, name='add_new_ballot'),
    path('<int:ballot_id>/results/', views.view_results, name='view_results'),
    path('<int:ballot_id>/edit/', views.edit_ballot, name='edit_ballot'),
    path("election/<int:election_id>/update-voters/", views.update_voters, name="update_voters"),

]


