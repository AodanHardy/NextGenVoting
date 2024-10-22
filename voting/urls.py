from django.urls import path

from voting import views

urlpatterns = [
    # Voting intro page
    path('<uuid:voter_id>/', views.voting_intro, name='voting_intro'),

    path('<uuid:vote_id>/ballot/<int:ballot_index>/', views.voting_ballot, name='voting_ballot')

]