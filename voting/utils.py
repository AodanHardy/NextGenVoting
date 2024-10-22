
class VoterData:
    def __init__(self, voterId, electionId):
        self.voter_id = voterId
        self.election_id = electionId
        self.ballots = []

    def addBallot(self, ballot):
        self.ballots.append(ballot)


class VoteBallotData:
    def __init__(self, title, description, voting_type):
        self.title = title
        self.description = description
        self.voting_type = voting_type
        self.candidates = []
        self.voteData = []

    def add_candidates(self, candidate):
        self.candidates.append(candidate)
