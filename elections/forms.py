from django import forms


class ElectionDetailsForm(forms.Form):
    title = forms.CharField(max_length=200, label="Election Title")
    description = forms.CharField(max_length=1000, label="Election Description")
    number_of_ballots = forms.IntegerField(min_value=1, label="Number of Ballots")
    use_blockchain = forms.BooleanField(required=False, label="Use Blockchain")
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    end_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))


class BallotForm(forms.Form):
    ballot_title = forms.CharField(max_length=200, label="Ballot Title")
    voting_type = forms.ChoiceField(choices=[
        ('first_past_the_post', 'First-Past-The-Post'),
        ('ranked_choice', 'Ranked Choice'),
        ('yes_no', 'Yes/No')
    ], label="Voting Type")


class CandidatesForm(forms.Form):
    number_of_winners = forms.IntegerField(min_value=1, label="Number of Winners", required=False)
    candidates = forms.CharField(max_length=1000, label="Enter candidates separated by commas")


class VoterUploadForm(forms.Form):
    voter_file = forms.FileField(label="Upload Voter List (CSV format)")
