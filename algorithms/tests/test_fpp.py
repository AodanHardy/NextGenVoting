from django.test import TestCase

from algorithms.firstPastThePost import FPTPVoteProcessor


# update this import path

class FPTPAlgorithmTest(TestCase):

    def setUp(self):
        self.basic_candidates = {1: "Alice", 2: "Bob", 3: "Charlie", 4: "Diana"}

    def test_basic_vote_count(self):
        votes = [
            {"id": 1}, {"id": 2}, {"id": 1},
            {"id": 3}, {"id": 4}, {"id": 2}, {"id": 1}
        ]
        processor = FPTPVoteProcessor(self.basic_candidates, votes)
        self.assertEqual(processor.result, {1: 3, 2: 2, 3: 1, 4: 1})

    def test_invalid_votes_ignored(self):
        votes = [{"id": 1}, {"id": 2}, {"id": 99}, {"id": 3}, {"id": 1}]
        processor = FPTPVoteProcessor(self.basic_candidates, votes)
        self.assertEqual(processor.result, {1: 2, 2: 1, 3: 1, 4: 0})

    def test_empty_vote_list(self):
        votes = []
        processor = FPTPVoteProcessor(self.basic_candidates, votes)
        self.assertEqual(processor.result, {1: 0, 2: 0, 3: 0, 4: 0})

    def test_all_votes_one_candidate(self):
        votes = [{"id": 2}] * 5
        processor = FPTPVoteProcessor(self.basic_candidates, votes)
        self.assertEqual(processor.result, {1: 0, 2: 5, 3: 0, 4: 0})

    def test_vote_tie(self):
        votes = [{"id": 1}, {"id": 2}, {"id": 1}, {"id": 2}]
        processor = FPTPVoteProcessor({1: "Alice", 2: "Bob"}, votes)
        self.assertEqual(processor.result, {1: 2, 2: 2})
