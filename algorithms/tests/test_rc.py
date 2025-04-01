from django.test import TestCase

from algorithms.rankedChoiceVote import RankedChoiceVoteProcessor


class RankedChoiceAlgorithmTest(TestCase):

    def setUp(self):
        self.candidates = {
            1: "Alice",
            2: "Bob",
            3: "Charlie",
            4: "Diana"
        }

    def test_single_winner_result(self):
        votes = [
            {"rankings": [1, 3, 2, 4]},
            {"rankings": [2, 4, 1]},
            {"rankings": [3, 1, 4]},
            {"rankings": [4, 2]},
            {"rankings": [1, 2]},
            {"rankings": [2, 3, 4, 1]},
            {"rankings": [4, 1]},
            {"rankings": [3, 4]},
            {"rankings": [1, 4, 2, 3]},
            {"rankings": [3, 1, 4]},
            {"rankings": [4, 3, 2, 1]},
            {"rankings": [1, 3]},
            {"rankings": [2, 4, 3]},
            {"rankings": [3, 1, 2, 4]},
            {"rankings": [1, 2, 4]},
            {"rankings": [2, 3, 1]},
            {"rankings": [4, 1, 3]},
            {"rankings": [3, 2, 1]},
            {"rankings": [1, 4, 3]},
            {"rankings": [2, 1]},
            {"rankings": [4, 3, 1]},
            {"rankings": [1, 2, 3]},
            {"rankings": [3, 1]},
            {"rankings": [2, 4]},
            {"rankings": [4, 1, 3, 2]},
            {"rankings": [1, 3, 2, 4]},
            {"rankings": [3, 2, 4]},
            {"rankings": [2, 1, 4, 3]},
            {"rankings": [4, 2, 3]},
        ]

        processor = RankedChoiceVoteProcessor(votes, self.candidates, num_winners=1)
        result = processor.finalize_results()

        self.assertEqual(len(result["winners"]), 1)
        self.assertIn(result["winners"][0], self.candidates.values())

    def test_quota_calculation(self):
        votes = [{"rankings": [1]} for _ in range(10)]
        processor = RankedChoiceVoteProcessor(votes, self.candidates, num_winners=1)
        self.assertEqual(processor.quota, 6)

    def test_tie_detection(self):
        votes = [
            {"rankings": [1]},
            {"rankings": [2]},
            {"rankings": [3]},
            {"rankings": [4]},
        ]
        processor = RankedChoiceVoteProcessor(votes, self.candidates, num_winners=1)
        result = processor.finalize_results()
        self.assertEqual(len(result["ties"]), 4)
        self.assertEqual(result["winners"], [])
