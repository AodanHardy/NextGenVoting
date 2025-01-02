import json

# mock example data that this class requires
votes_data = [
    '{"id": 1}',
    '{"id": 2}',
    '{"id": 1}',
    '{"id": 3}',
    '{"id": 4}',
    '{"id": 2}',
    '{"id": 1}'
]
candidates = {
    1: "Alice",
    2: "Bob",
    3: "Charlie",
    4: "Diana"
}


class FPTPVoteProcessor:
    def __init__(self, candidates_list, vote_data):
        self.candidatesList = candidates_list
        self.voteData = vote_data
        self.result = {candidate_id: 0 for candidate_id in candidates_list}

        self.processVotes()

    def processVotes(self):
        '''
        for vote_str in self.voteData:
            try:
                vote_data = json.loads(vote_str)
                vote = vote_data.get('id')
                if vote in self.result:
                    self.result[vote] += 1

            except json.JSONDecodeError:
                print(f"Invalid vote data: {vote_str}")
        '''

        for voteDict in self.voteData:
            vote = voteDict.get("id")

            if vote in self.result:
                self.result[vote] += 1

