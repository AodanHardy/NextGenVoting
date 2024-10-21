from django.urls import path

from voting import views

urlpatterns = [
    # Voting intro page
    path('<uuid:vote_id>/', views.voting_intro, name='voting_intro'),

    # Ballot page (for individual ballots)
    path('<uuid:vote_id>/ballot/<int:ballot_id>/', views.voting_ballot, name='voting_ballot'),
]