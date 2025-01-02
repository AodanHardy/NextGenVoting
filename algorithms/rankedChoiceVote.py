import copy
import json

mock_votes = [
    '{"rankings": [1, 3, 2, 4]}',
    '{"rankings": [2, 4, 1]}',
    '{"rankings": [3, 1, 4]}',
    '{"rankings": [4, 2]}',
    '{"rankings": [1, 2]}',
    '{"rankings": [2, 3, 4, 1]}',
    '{"rankings": [4, 1]}',
    '{"rankings": [3, 4]}',
    '{"rankings": [1, 4, 2, 3]}',
    '{"rankings": [2, 3, 1, 4]}',
    '{"rankings": [4, 3, 2, 1]}',
    '{"rankings": [1, 3]}',
    '{"rankings": [2, 4, 3]}',
    '{"rankings": [3, 1, 2, 4]}',
    '{"rankings": [1, 2, 4]}',
    '{"rankings": [2, 3, 1]}',
    '{"rankings": [4, 1, 3]}',
    '{"rankings": [3, 2, 1]}',
    '{"rankings": [1, 4, 3]}',
    '{"rankings": [2, 1]}',
    '{"rankings": [4, 3, 1]}',
    '{"rankings": [1, 2, 3]}',
    '{"rankings": [3, 1]}',
    '{"rankings": [2, 4]}',
    '{"rankings": [4, 1, 3, 2]}',
    '{"rankings": [1, 3, 2, 4]}',
    '{"rankings": [3, 2, 4]}',
    '{"rankings": [2, 1, 4, 3]}',
    '{"rankings": [4, 2, 3]}',
]

candidates = {
    1: "Alice",
    2: "Bob",
    3: "Charlie",
    4: "Diana"
}
""" 
    notes for morning:
    the current way of doing it is eliminateCandidate 
    calls findMin and elinates what it says
    
    but it should be find min first, which returns a list.
     this list is then passed to elininateCanidates which deletes all items in list
"""


class RankedChoiceVoteProcessor:
    def __init__(self, vote_data, candidates_list, num_winners):
        self.vote_data = vote_data
        self.candidates = {id: {"name": name, "votes": 0, "elected": False} for id, name in candidates_list.items()}
        self.originalCandidates = copy.deepcopy(self.candidates)
        self.num_winners = num_winners
        self.processed_votes = []
        self.rounds = []
        self.quota = None
        self.winners = []

        self.processVotes()

    def finalize_results(self):
        result_data = {
            "candidates": {
                candidate_id: {
                    "name": candidate_info["name"],
                }
                for candidate_id, candidate_info in self.originalCandidates.items()
            },
            "num_winners": self.num_winners,
            "quota": self.quota,
            "rounds": self.rounds,
            "winners": self.winners
        }

        return json.dumps(result_data)

    def processVotes(self):
        self._initialize_votes()
        self.quota = self._calculate_quota()

        round_number = 1
        while len(self.winners) < self.num_winners:
            round_data = self._process_round(round_number)
            self.rounds.append(round_data)
            round_number += 1

    def _initialize_votes(self):
        # Convert the JSON into a usable format and initialize vote counts
        for vote_str in self.vote_data:
            try:
                vote_data = json.loads(vote_str)
                rankings = vote_data.get('rankings', [])
                self.processed_votes.append(rankings)
            except json.JSONDecodeError:
                print(f"Invalid vote data: {vote_str}")

        # Count first-choice votes
        for vote in self.processed_votes:
            first_choice = vote[0]
            if first_choice in self.candidates:
                self.candidates[first_choice]["votes"] += 1

    def _calculate_quota(self):
        # Formula is -> Quota = (Votes / (Winners + 1)) + 1
        total_valid_votes = len(self.processed_votes)
        return (total_valid_votes // (self.num_winners + 1)) + 1

    def _process_round(self, round_number):
        round_data = {"round_number": round_number}
        initial_votes = {id: candidate["votes"] for id, candidate in self.candidates.items()}
        round_data["initial_votes"] = initial_votes

        # Check if any candidate surpasses the quota
        for candidate_id, candidate_info in self.candidates.items():
            if candidate_info["votes"] >= self.quota and not candidate_info["elected"]:
                self.winners.append(candidate_info["name"])
                candidate_info["elected"] = True
                round_data["elected"] = candidate_info["name"]

                # Handle surplus votes and transfer them
                # Each transfer vote is proportional to the size of the surplus
                surplus = candidate_info["votes"] - self.quota
                round_data["surplus"] = surplus
                transfers = self._transfer_surplus_votes(candidate_id, surplus)
                round_data["transfers"] = transfers
                # I'm only going to process one candidates surplus at a time - might need changed
                break

        # If no one met the quota - eliminate the candidate with the fewest votes
        if "elected" not in round_data:
            # need to call find min here first and then call eliminate ******

            # Finding candidate/s with the smallest vote and return dictionary of them
            lowestCandidates = self._findMinCandidate()

            # Checking if it's safe to delete
            # (If deleting multiple candidates who are drawing could mean
            # that there are lest candidates than winners available)
            if len(lowestCandidates) + len(self.winners) <= len(self.candidates) - self.num_winners:
                # Eliminate all candidates with the lowest votes
                eliminated_names = []
                for candidate_id, candidate_info in lowestCandidates.items():
                    # Call the eliminate method for each candidate in the lowestCandidates group
                    eliminated_id, eliminated_name = self._eliminate_candidate(candidate_id)
                    eliminated_names.append(eliminated_name)

                    # Transfer votes from eliminated candidate to next ranked choice
                    transfers = self._transfer_votes(eliminated_id)
                    round_data["transfers"] = transfers

                # Add all eliminated candidates to round data
                round_data["eliminated"] = eliminated_names
            else:

                # Need to implement logic for tiebreaker if not safe to delete tied candidates
                print("not safe to eliminate")

                # First tiebreaker idea -> check who had the least first choice votes and eliminate them

        final_votes = {id: candidate["votes"] for id, candidate in self.candidates.items()}
        round_data["final_votes"] = final_votes

        remaining_valid_candidates = self._getRemainingValidCandidates()
        remaining_winners_needed = self.num_winners - len(self.winners)

        # If there are as many remaining candidates as winners needed then
        # there's no point continuing to next round
        if len(remaining_valid_candidates) == remaining_winners_needed:
            for candidate_id in remaining_valid_candidates:
                if not self.candidates[candidate_id]["elected"]:
                    self.winners.append(self.candidates[candidate_id]["name"])
                    self.candidates[candidate_id]["elected"] = True
                    round_data.setdefault("elected", []).append(self.candidates[candidate_id]["name"])

        return round_data

    def _transfer_surplus_votes(self, candidate_id, surplus):
        # Calculate the surplus transfer ratio
        total_votes = self.candidates[candidate_id]["votes"]
        transfer_ratio = surplus / total_votes if total_votes != 0 else 0

        transfers = {id: 0 for id in self.candidates if not self.candidates[id]["elected"]}

        for vote in self.processed_votes:
            # Check if vote list is not empty and first choice matches candidate_id
            if len(vote) > 0 and vote[0] == candidate_id:
                # Remove the elected candidate from the voter's ranking
                vote.pop(0)
                # If there are other candidates in the ranking
                if vote:
                    next_choice = vote[0]
                    if next_choice in self.candidates and not self.candidates[next_choice]["elected"]:
                        # Transfer a fractional vote
                        fractional_vote = transfer_ratio
                        self.candidates[next_choice]["votes"] += fractional_vote
                        transfers[next_choice] += fractional_vote

        return transfers

    def _eliminate_candidate(self, candidate_id):
        # Get the name of the candidate to be eliminated
        eliminated_name = self.candidates[candidate_id]["name"]

        # Remove the eliminated candidate from the self.candidates dictionary
        del self.candidates[candidate_id]

        # Return the eliminated candidate's ID and name
        return candidate_id, eliminated_name

    def _transfer_votes(self, eliminated_id):
        # Initialize the transfers dictionary for remaining candidates
        transfers = {id: 0 for id in self.candidates}

        for vote in self.processed_votes:
            # Ensure the vote has candidates left in the ranking
            if not vote:
                continue  # Skip empty votes

            # Check if the first choice matches the eliminated candidate
            if vote[0] == eliminated_id:
                vote.pop(0)  # Remove the eliminated candidate

                # Ensure there's another candidate to transfer the vote to
                if vote:
                    next_choice = vote[0]
                    if next_choice in self.candidates and not self.candidates[next_choice]["elected"]:
                        self.candidates[next_choice]["votes"] += 1
                        transfers[next_choice] += 1

        return transfers

    def _findMinCandidate(self):
        # Initialize the minimum vote count as None
        min_votes = None

        # Create an empty dictionary to store candidates with the minimum votes
        min_candidates = {}

        # Iterate over the candidates to find the ones with the fewest votes
        for candidate_id, candidate_info in self.candidates.items():
            # Skip candidates who have already been elected
            if candidate_info["elected"]:
                continue

            # Check if the candidate has fewer votes than the current minimum
            if min_votes is None or candidate_info["votes"] < min_votes:
                # Set the new minimum vote count
                min_votes = candidate_info["votes"]
                # Reset the min_candidates dictionary to only include this candidate
                min_candidates = {candidate_id: candidate_info}
            elif candidate_info["votes"] == min_votes:
                # If the candidate's votes are equal to the current minimum, add them to the dictionary
                min_candidates[candidate_id] = candidate_info

        # Return the dictionary of candidates with the fewest votes
        return min_candidates

    def _getRemainingValidCandidates(self):
        valid_candidates = []
        for candidate_id, candidate_info in self.candidates.items():
            if not candidate_info["elected"]:
                valid_candidates.append(candidate_id)
        return valid_candidates


