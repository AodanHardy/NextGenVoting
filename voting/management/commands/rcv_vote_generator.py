import json
import os
import random

from cryptography.fernet import Fernet

fernet = Fernet(os.environ["ENCRYPTED_MODEL_FIELDS_KEY"])

egOutputVote = {'rankings': [721, 720, 722]}
egCandidates = {719: 'Pete', 720: 'Mick', 721: 'Walter', 722: 'Jessie'}


def generateRcvVotes(candidates, numVotes):
    votes = []

    # Assign a random weight to each candidate
    candidate_weights = {cid: random.uniform(0.6, 1.0) for cid in candidates}

    for _ in range(numVotes):
        # sort candidates by their weight to bias ranking
        ranking = sorted(candidates.keys(), key=lambda cid: random.uniform(0, candidate_weights[cid]), reverse=True)

        vote = {'rankings': ranking}
        # encrypt the vote
        encrypted_vote = fernet.encrypt(json.dumps(vote).encode()).decode()


        # append the biased vote to the list
        votes.append(encrypted_vote)

    return votes
