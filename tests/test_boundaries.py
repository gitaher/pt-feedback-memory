import copy
import unittest

import test_verifier as helpers

from plugin.logic import solve
from verifier import verify_input


class BoundaryTests(unittest.TestCase):
    setUp = helpers.VerifierTests.setUp
    check = helpers.VerifierTests.check

    def reject(self, x):
        self.assertFalse(verify_input("compute", x)["valid"])

    def accept(self, x, gold):
        self.assertTrue(self.check(gold, x))
        self.assertEqual(solve(x), gold)

    def test_zero_top_k(self):
        self.accept(dict(self.x, top_k=0), {"hits": []})

    def test_no_memories(self):
        self.accept(dict(self.x, memories=[]), {"hits": []})

    def test_zero_ttl_includes_exact_resolution(self):
        self.accept(dict(self.x, ttl_days=0), {"hits": [{"id": "m2", "score": 5}]})

    def test_ttl_lower_boundary_is_inclusive(self):
        x = copy.deepcopy(self.x)
        x["memories"][0]["resolved_at"] = "2026-01-03T00:00:00Z"
        self.accept(x, self.gold)

    def test_one_second_expired(self):
        x = copy.deepcopy(self.x)
        x["memories"][0]["resolved_at"] = "2026-01-02T23:59:59Z"
        self.accept(x, {"hits": [{"id": "m2", "score": 5}]})

    def test_score_dominates_utility(self):
        x = copy.deepcopy(self.x)
        x["memories"][0]["utility"] = -100
        self.accept(x, self.gold)

    def test_ties_use_id_ascending(self):
        x = copy.deepcopy(self.x)
        r = copy.deepcopy(x["memories"][0])
        r["id"] = "m0"
        x["memories"].append(r)
        self.accept(x, {"hits": [{"id": "m0", "score": 7}, {"id": "m1", "score": 7}]})

    def test_no_context_match(self):
        self.accept(dict(self.x, profile="other", symbol="OTHER", regime="other"), {"hits": []})

    def test_future_and_pending_are_not_evidence(self):
        x = copy.deepcopy(self.x)
        x["memories"] = x["memories"][2:]
        self.accept(x, {"hits": []})

    def test_bad_resolution_or_parameters(self):
        x = copy.deepcopy(self.x)
        x["memories"][0]["resolved_at"] = "2025-12-31T00:00:00Z"
        self.reject(x)
        self.reject(dict(self.x, top_k=-1))
        self.reject(dict(self.x, ttl_days=-1))
