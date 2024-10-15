from django import forms


class ElectionDetailsForm(forms.Form):
    title = forms.CharField(max_length=200, label="Election Title")
    description = forms.CharField(widget=forms.Textarea, label="Election Description")
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
    candidates = forms.CharField(widget=forms.Textarea, label="Enter candidates separated by commas")


class VotersListForm(forms.Form):
    voter_file = forms.FileField(label="Upload Voter List (CSV format)")
