import ast
from collections import defaultdict

def validate_candidates(candidates):
    if len(candidates) < 2:
        return False, "You must enter more than 1 Candidate"
    for candidate in candidates:
        if len(candidate) < 1:
            return False

def organise_votes_by_ballot(votes):
    ballot_votes = defaultdict(list)

    for vote in votes:
        # Safely evaluate the string to convert it into a Python list of dictionaries
        parsed_vote = ast.literal_eval(vote)
        for ballot in parsed_vote:
            for ballot_id, ballot_data in ballot.items():
                ballot_votes[int(ballot_id)].append(ballot_data)

    return dict(ballot_votes)





def getWinningVote(vote_dict):
    max_votes = max(vote_dict.values())
    winners = [key for key, value in vote_dict.items() if value == max_votes]
    return winners


class BallotData:
    def __init__(self, title, voting_type):
        self.title = title
        self.voting_type = voting_type
        self.candidates = []
        self.number_of_winners = 1

    def add_candidate(self, candidate):
        self.candidates.append(candidate)

    def setNumOfWinners(self, num):
        self.number_of_winners = num


class VoterData:
    def __init__(self, name, email):
        self.name = name
        self.email = email


class ElectionData:
    def __init__(self, title, description, numOfBallots, useBlockchain):
        self.title = title
        self.description = description
        self.num_of_ballots = numOfBallots
        self.useBlockchain = useBlockchain

        self.ballots = []
        self.voters = []

    def add_ballot(self, ballot):
        self.ballots.append(ballot)

    def add_voter(self, voter):
        self.voters.append(voter)