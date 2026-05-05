from pathlib import Path
import json
import unittest

import yaml

from engine.auction import Auction
from engine.cards import Hand
from engine.explanation import explain
from app import simulate, system_notes
from engine.legality import auction_is_complete, is_call_legal, legal_calls
from engine.loader import load_convention_set
from engine.matcher import matches_context
from engine.selector import choose_bid
from engine.system_notes import generate_system_notes


BACKEND_DIR = Path(__file__).resolve().parents[1]
CASES_DIR = Path(__file__).resolve().parent / "cases"


def _read_cases(file_name: str) -> list[dict]:
    return _read_yaml(file_name).get("cases", [])


def _read_yaml(file_name: str) -> dict:
    return yaml.safe_load((CASES_DIR / file_name).read_text(encoding="utf-8")) or {}


class FixtureBiddingTests(unittest.TestCase):
    def test_bidding_cases(self):
        for case in _read_cases("bidding.yaml"):
            with self.subTest(case=case["name"]):
                result = self._run_bidding_case(case)
                self._assert_bidding_expectations(result, case.get("expected", {}))

    def _run_bidding_case(self, case: dict) -> dict:
        environment = case.get("environment", {})
        convention_set = load_convention_set(case["convention_set"], BACKEND_DIR)
        auction = Auction.parse(
            case.get("auction", []),
            dealer=environment.get("dealer", "n"),
            vulnerability=environment.get("vulnerability", "none"),
        )
        hand = Hand.parse(case["hand"])
        return explain(choose_bid(convention_set, auction, hand, environment))

    def _assert_bidding_expectations(self, result: dict, expected: dict) -> None:
        if "call" in expected:
            self.assertEqual(result["call"], expected["call"])

        origin = expected.get("origin", {})
        actual_origin = result["public_meaning"]["origin"] if result["public_meaning"] else {}
        for key, value in origin.items():
            self.assertEqual(actual_origin.get(key), value)

        public_meaning = expected.get("public_meaning", {})
        actual_meaning = result["public_meaning"]["meaning"] if result["public_meaning"] else {}
        for key, value in public_meaning.items():
            self.assertEqual(actual_meaning.get(key), value)

        if "compared_candidate_calls" in expected:
            self.assertEqual(
                [candidate["call"] for candidate in result["internal_origin"]["compared_candidates"]],
                expected["compared_candidate_calls"],
            )

        if "selected_algorithm" in expected:
            self.assertEqual(result["internal_origin"]["selected"]["algorithm"], expected["selected_algorithm"])

        selected_plan_origin = expected.get("selected_plan_origin", {})
        actual_selected_plan_origin = result["internal_origin"]["selected"].get("plan_origin") or {}
        for key, value in selected_plan_origin.items():
            self.assertEqual(actual_selected_plan_origin.get(key), value)

        selection_policy = expected.get("selection_policy", {})
        actual_policy = result["internal_origin"]["selection_policy"] or {}
        for key, value in selection_policy.items():
            self.assertEqual(actual_policy.get(key), value)

        if "diagnostics" in expected:
            self.assertEqual(result["diagnostics"], expected["diagnostics"])

        for text in expected.get("diagnostics_include", []):
            self.assertTrue(any(text in diagnostic for diagnostic in result["diagnostics"]), result["diagnostics"])

        if "semantic_fact_types" in expected:
            self.assertEqual(
                [fact["fact_type"] for fact in result["internal_origin"]["semantic_facts"]],
                expected["semantic_fact_types"],
            )

        for state_expected in expected.get("auction_state_include", []):
            self.assertTrue(
                any(_mapping_contains(actual, state_expected) for actual in result["internal_origin"]["auction_state"]),
                {
                    "expected": state_expected,
                    "actual": result["internal_origin"]["auction_state"],
                },
            )

        for index, fact_origin in enumerate(expected.get("semantic_fact_origins", [])):
            actual = result["internal_origin"]["semantic_facts"][index]["origin"]
            for key, value in fact_origin.items():
                self.assertEqual(actual.get(key), value)

        for index, frame_expected in enumerate(expected.get("protocol_frames", [])):
            actual = result["internal_origin"]["protocol_frames"][index]
            for key, value in frame_expected.items():
                self.assertEqual(actual.get(key), value)

        for index, plan_expected in enumerate(expected.get("plan_states", [])):
            actual = result["internal_origin"]["plan_states"][index]
            for key, value in plan_expected.items():
                self.assertEqual(actual.get(key), value)

        selected_criteria = {
            item["criterion_id"]
            for item in result["internal_origin"]["selected"].get("criteria_results", [])
        }
        for criterion_id in expected.get("selected_criteria_include", []):
            self.assertIn(criterion_id, selected_criteria)


class FixtureFullAuctionTests(unittest.TestCase):
    def test_full_auction_cases(self):
        for case in _read_cases("full_auctions.yaml"):
            with self.subTest(case=case["name"]):
                result = simulate(
                    {
                        "convention_set": {"id": case["convention_set"]},
                        "hands": case["hands"],
                        "environment": case.get("environment", {}),
                        "max_calls": case.get("max_calls", 80),
                    }
                )
                expected = case.get("expected", {})
                if "auction" in expected:
                    self.assertEqual(result["auction"], expected["auction"])
                if "diagnostics" in expected:
                    self.assertEqual(result["diagnostics"], expected["diagnostics"])
                if "calls_by_our_side" in expected:
                    self.assertEqual(
                        [record["call"] for record in result["records"] if record["explanation"] is not None],
                        expected["calls_by_our_side"],
                    )


class FixtureMatcherTests(unittest.TestCase):
    def test_matcher_cases(self):
        for case in _read_cases("matcher.yaml"):
            with self.subTest(case=case["name"]):
                for calls in case.get("matches", []):
                    self.assertTrue(matches_context(case["context"], Auction.parse(calls)), calls)
                for calls in case.get("rejects", []):
                    self.assertFalse(matches_context(case["context"], Auction.parse(calls)), calls)


class FixtureLegalityTests(unittest.TestCase):
    def test_legality_cases(self):
        for case in _read_cases("legality.yaml"):
            with self.subTest(case=case["name"]):
                environment = case.get("environment", {})
                auction = Auction.parse(
                    case.get("auction", []),
                    dealer=environment.get("dealer", "n"),
                    vulnerability=environment.get("vulnerability", "none"),
                )
                expected = case.get("expected", {})
                if "complete" in expected:
                    self.assertEqual(auction_is_complete(auction), expected["complete"])
                if "legal_calls_include" in expected:
                    actual_legal_calls = set(legal_calls(auction))
                    for call in expected["legal_calls_include"]:
                        self.assertIn(call, actual_legal_calls)
                for call in expected.get("legal", []):
                    self.assertTrue(is_call_legal(auction, call), call)
                for call in expected.get("illegal", []):
                    self.assertFalse(is_call_legal(auction, call), call)


class FixtureHandParserTests(unittest.TestCase):
    def test_valid_hand_cases(self):
        for case in _read_yaml("hands.yaml").get("valid", []):
            with self.subTest(case=case["name"]):
                hand = Hand.parse(case["hand"])
                expected = case.get("expected", {})
                for suit in ("spades", "hearts", "diamonds", "clubs"):
                    if suit in expected:
                        self.assertEqual(getattr(hand, suit), expected[suit])
                if "hcp" in expected:
                    self.assertEqual(hand.hcp, expected["hcp"])

    def test_invalid_hand_cases(self):
        for case in _read_yaml("hands.yaml").get("invalid", []):
            with self.subTest(case=case["name"]):
                with self.assertRaisesRegex((ValueError, TypeError), case["error_contains"]):
                    Hand.parse(case["hand"])


class InfrastructureTests(unittest.TestCase):
    def test_auction_calls_are_canonicalized(self):
        auction = Auction.parse("1NT pass 2d", dealer="N", vulnerability="NONE")

        self.assertEqual(auction.calls, ("1N", "P", "2D"))
        self.assertEqual(auction.canonical_key(), "dealer=n;vul=none;calls=1NP2D")

    def test_compact_auction_allows_arbitrary_spaces(self):
        auction = Auction.parse(" 1N   P 1S P X R ")

        self.assertEqual(auction.calls, ("1N", "P", "1S", "P", "X", "R"))
        self.assertEqual(auction.compact_sequence(), "1NP1SPXR")

    def test_loader_accepts_json_compatible_yaml(self):
        scratch = BACKEND_DIR / "tmp_json_compat"
        convention_sets_dir = scratch / "convention_sets"
        convention_dir = scratch / "conventions" / "nt" / "simple"
        convention_sets_dir.mkdir(parents=True, exist_ok=True)
        convention_dir.mkdir(parents=True, exist_ok=True)
        try:
            (convention_sets_dir / "json_style.yaml").write_text(
                json.dumps({"id": "json_style", "name": "JSON Style", "conventions": ["nt.simple"]}),
                encoding="utf-8",
            )
            (convention_dir / "convention.yaml").write_text(
                json.dumps(
                    {
                        "id": "simple",
                        "namespace": "nt",
                        "name": "Simple JSON-Compatible Convention",
                        "version": "0.1.0",
                        "author": {"name": "Partner Prototype"},
                    }
                ),
                encoding="utf-8",
            )
            (convention_dir / "calls.yaml").write_text(
                json.dumps(
                    {
                        "call_specifications": [
                            {
                                "id": "c1",
                                "context": {"auction_pattern": ""},
                                "call": "1N",
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            convention_set = load_convention_set("json_style", scratch)

            self.assertEqual(len(convention_set.call_specifications), 1)
            self.assertEqual(convention_set.call_specifications[0].qualified_id, "nt/simple@0.1.0:call_specification:c1")
        finally:
            for path in sorted(scratch.rglob("*"), reverse=True):
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    path.rmdir()

    def test_loader_returns_convention_set_ir_objects(self):
        convention_set = load_convention_set("expert_2over1", BACKEND_DIR)

        self.assertEqual(convention_set.id, "expert_2over1")
        self.assertGreaterEqual(len(convention_set.call_specifications), 1)
        self.assertGreaterEqual(len(convention_set.protocol_frames), 1)
        self.assertGreaterEqual(len(convention_set.bidding_plans), 1)
        self.assertGreaterEqual(len(convention_set.call_selection_policies), 1)

    def test_convention_set_selection_policy_is_reported(self):
        convention_set = load_convention_set("expert_2over1", BACKEND_DIR)
        auction = Auction.parse("", dealer="n", vulnerability="none")
        hand = Hand.parse("SAQ7HKJ8DA762CQ54")

        result = explain(choose_bid(convention_set, auction, hand, {"dealer": "n", "vulnerability": "none"}))

        policy = result["internal_origin"]["selection_policy"]
        self.assertIsNotNone(policy)
        self.assertEqual(policy["object_type"], "call_selection_policy")
        self.assertEqual(policy["object_id"], "policy_1")

    def test_system_notes_are_generated_from_ir(self):
        convention_set = load_convention_set("expert_2over1", BACKEND_DIR)

        notes = generate_system_notes(convention_set)

        self.assertIn("# Expert 2/1", notes)
        self.assertIn("## Four-Way Jacoby Transfer", notes)
        self.assertIn("### Bidding Plans", notes)
        self.assertIn("Workflow nodes", notes)
        self.assertIn("`policy_1`", notes)
        self.assertIn("`alertable`=`false`", notes)
        self.assertIn('`auction_pattern`=`""`', notes)

    def test_system_notes_app_entrypoint_returns_markdown(self):
        result = system_notes({"convention_set": {"id": "expert_2over1"}})

        self.assertEqual(result["format"], "markdown")
        self.assertEqual(result["convention_set"]["id"], "expert_2over1")
        self.assertIn("1N opening shows 15-17 HCP", result["content"])

    def test_meow_named_evaluator_is_loaded_and_reported(self):
        convention_set = load_convention_set("meow_2over1", BACKEND_DIR)

        notes = generate_system_notes(convention_set)

        self.assertIn("eval_minor_honor_third", [item.id for item in convention_set.named_evaluators])
        self.assertIn("### Named Evaluators", notes)
        self.assertIn("Minor-transfer superaccept support requires honor-third", notes)


def _mapping_contains(actual: dict, expected: dict) -> bool:
    return all(actual.get(key) == value for key, value in expected.items())


if __name__ == "__main__":
    unittest.main()
