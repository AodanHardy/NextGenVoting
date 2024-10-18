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