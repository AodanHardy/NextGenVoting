def get_ranked_order(ranked_dict):
    sorted_candidates = []

    # Loop through the ranks from 1 to the number of candidates
    for rank in range(1, len(ranked_dict) + 1):
        # Find the candidate with the current rank and add to the list
        for candidate, candidate_rank in ranked_dict.items():
            if int(candidate_rank) == rank:
                sorted_candidates.append(candidate)

    return sorted_candidates


def rcv_validator(postData, candidateIds):
    """
    function is called to check if users input for rcv ballot is valid
    """
    votes = {}
    rankings = []

    for id in candidateIds:
        if postData.get(str(id)):
            rankings.append(int(postData.get(str(id))))

    if len(rankings) == 0:
        return False, "YOU MUST MAKE A SELECTION"

    rankings.sort()
    print()

    # check dupes

    # check no missing numbers
    for i, rank in enumerate(rankings, start=1):
        if rank != i:
            return False, "Ranks must be consecutive numbers starting from 1."

    return True, None


# i ended up not using these
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
