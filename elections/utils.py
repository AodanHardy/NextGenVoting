

class Ballot:
    def __init__(self, title, voting_type):
        self.title = title
        self.voting_type = voting_type
        self.candidates = []


    def add_candidate(self, candidate):
        self.candidates.append(candidate)


class Election:
    def __init__(self, title, description, start_time, end_time):
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.ballots = []

    def add_ballot(self, ballot):
        self.ballots.append(ballot)