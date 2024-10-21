
class VoterData:
    def __init__(self, voterId, electionId):
        self.voter_id = voterId
        self.election_id = electionId
        self.ballots = []


class VoteBallotData:
    def __init__(self, title, description, votingType):
        self.title = title
        self.description = description
        self.voting_type = votingType
        self.candidates = []
        self.voteData = []
