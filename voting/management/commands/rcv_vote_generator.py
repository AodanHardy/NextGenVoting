import random

egOutputVote = {'rankings': [721, 720, 722]}
egCandidates = {719: 'Pete', 720: 'Mick', 721: 'Walter', 722: 'Jessie'}


def generateRcvVotes(candidates, numVotes):
    votes = []

    # Assign a random weight (likelihood) to each candidate
    candidate_weights = {cid: random.uniform(0.6, 1.0) for cid in candidates}

    for _ in range(numVotes):
        # sort candidates by their weight to bias ranking
        ranking = sorted(candidates.keys(), key=lambda cid: random.uniform(0, candidate_weights[cid]), reverse=True)

        # append the biased vote to the list
        votes.append({'rankings': ranking})

    return votes
