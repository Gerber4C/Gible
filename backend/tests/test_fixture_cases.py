import shutil
import unittest
from pathlib import Path

import yaml

from engine.auction import Auction
from engine.bsl import BSLValidationError, load_bsl_files
from engine.call_space import relation_to_last_contract, steps_after, steps_between
from engine.cards import Hand
from engine.context import BridgeContext, StateView, UNDEFINED
from engine.explanation import explain
from app import simulate, system_notes
from engine.legality import auction_is_complete, is_call_legal, legal_calls
from engine.loader import load_profile
from engine.matcher import matches_context
from engine.memory import SeatMemory
from engine.selector import choose_bid, replay_auction
from engine.system_notes import generate_system_notes
from engine.trace import AuctionTrace, StateRecord


BACKEND_DIR = Path(__file__).resolve().parents[1]
PROFILE_TESTS_DIR = BACKEND_DIR / "partnership_profiles" / "meow_2over1" / "tests"
CASES_DIR = PROFILE_TESTS_DIR / "cases"
_PROFILE_CACHE = {}


def _read_cases(file_name: str) -> list[dict]:
    return _read_yaml(file_name).get("cases", [])


def _read_yaml(file_name: str) -> dict:
    return yaml.safe_load((CASES_DIR / file_name).read_text(encoding="utf-8").lstrip("\ufeff")) or {}


class FixtureBiddingTests(unittest.TestCase):
    def test_bidding_cases(self):
        for case in _read_cases("bidding.yaml"):
            with self.subTest(case=case["name"]):
                result = self._run_bidding_case(case)
                self._assert_bidding_expectations(result, case.get("expected", {}))

    def _run_bidding_case(self, case: dict) -> dict:
        environment = case.get("environment", {})
        profile = _load_fixture_profile(case["profile"])
        auction = Auction.parse(
            case.get("auction", []),
            dealer=environment.get("dealer", "n"),
            vulnerability=environment.get("vulnerability", "none"),
        )
        hand = Hand.parse(case["hand"])
        return explain(choose_bid(profile, auction, hand, environment))

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
            actual_calls = [candidate["call"] for candidate in result["internal_origin"]["compared_candidates"]]
            self.assertEqual(actual_calls[0], expected["compared_candidate_calls"][0])
            for call in expected["compared_candidate_calls"]:
                self.assertIn(call, actual_calls)

        if "selected_source_kind" in expected:
            self.assertEqual(result["internal_origin"]["selected"]["source_kind"], expected["selected_source_kind"])

        selected_private_route_origin = expected.get("selected_private_route_origin", {})
        actual_selected_private_route_origin = result["internal_origin"]["selected"].get("private_route_origin") or {}
        for key, value in selected_private_route_origin.items():
            self.assertEqual(actual_selected_private_route_origin.get(key), value)

        selection_policy = expected.get("selection_policy", {})
        actual_policy = result["internal_origin"]["selection_policy"] or {}
        for key, value in selection_policy.items():
            self.assertEqual(actual_policy.get(key), value)

        if "diagnostics" in expected:
            self.assertEqual(result["diagnostics"], expected["diagnostics"])

        for text in expected.get("diagnostics_include", []):
            self.assertTrue(any(text in diagnostic for diagnostic in result["diagnostics"]), result["diagnostics"])

        if "state_keys" in expected:
            self.assertEqual(
                [state["key"] for state in result["internal_origin"]["state_records"]],
                expected["state_keys"],
            )

        for state_expected in expected.get("state_records_include", []):
            self.assertTrue(
                any(_mapping_contains(actual, state_expected) for actual in result["internal_origin"]["state_records"]),
                {
                    "expected": state_expected,
                    "actual": result["internal_origin"]["state_records"],
                },
            )

        for index, fact_origin in enumerate(expected.get("state_origins", [])):
            actual = result["internal_origin"]["state_records"][index]["origin"]
            for key, value in fact_origin.items():
                self.assertEqual(actual.get(key), value)

        for index, frame_expected in enumerate(expected.get("frame_states", [])):
            actual = result["internal_origin"]["frame_states"][index]
            for key, value in frame_expected.items():
                self.assertEqual(actual.get(key), value)

        for index, route_expected in enumerate(expected.get("private_route_states", [])):
            actual = result["internal_origin"]["private_route_states"][index]
            for key, value in route_expected.items():
                self.assertEqual(actual.get(key), value)

        selected_criteria = {
            item["criterion_id"]
            for item in result["internal_origin"]["selected"].get("criteria_results", [])
        }
        if selected_criteria:
            for criterion_id in expected.get("selected_criteria_include", []):
                self.assertIn(criterion_id, selected_criteria)


class FixtureFullAuctionTests(unittest.TestCase):
    def test_full_auction_cases(self):
        for case in _read_cases("full_auctions.yaml"):
            with self.subTest(case=case["name"]):
                result = simulate(
                    {
                        "profile": {"id": case["profile"]},
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


def _load_fixture_profile(profile_id: str):
    if profile_id not in _PROFILE_CACHE:
        _PROFILE_CACHE[profile_id] = load_profile(profile_id, BACKEND_DIR)
    return _PROFILE_CACHE[profile_id]


def _remove_tree(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path)


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

    def test_loader_accepts_bsl_source(self):
        scratch = BACKEND_DIR / "tmp_bsl_source"
        profile_dir = scratch / "partnership_profiles" / "bsl_style"
        gadget_dir = profile_dir / "gadgets" / "nt" / "simple"
        profile_dir.mkdir(parents=True, exist_ok=True)
        gadget_dir.mkdir(parents=True, exist_ok=True)
        try:
            (profile_dir / "profile.bsl.py").write_text(
                "Profile(id='bsl_style', name='BSL Style', gadgets=['nt.simple'])\n",
                encoding="utf-8",
            )
            (gadget_dir / "gadget.bsl.py").write_text(
                "\n".join(
                    [
                        "Gadget(",
                        "    id='simple',",
                        "    namespace='nt',",
                        "    name='Simple BSL Gadget',",
                        "    version='0.1.0',",
                        "    author={'name': 'Partner Prototype'},",
                        ")",
                        "Call(id='c1', context={'auction_pattern': ''}, bid='1N')",
                    ]
                ),
                encoding="utf-8",
            )

            profile = load_profile("bsl_style", scratch)

            self.assertEqual(len(profile.call_specs), 1)
            self.assertEqual(profile.call_specs[0].qualified_id, "nt/simple@0.1.0:call_spec:c1")
        finally:
            _remove_tree(scratch)

    def test_python_policy_function_selects_from_recovered_state(self):
        scratch = BACKEND_DIR / "tmp_state_policy"
        profile_dir = scratch / "partnership_profiles" / "state_policy"
        gadget_dir = profile_dir / "gadgets" / "test" / "state_policy"
        profile_dir.mkdir(parents=True, exist_ok=True)
        gadget_dir.mkdir(parents=True, exist_ok=True)
        try:
            (profile_dir / "profile.bsl.py").write_text(
                "Profile(id='state_policy', name='State Policy', gadgets=['test.state_policy'])\n",
                encoding="utf-8",
            )
            (gadget_dir / "gadget.bsl.py").write_text(
                "\n".join(
                    [
                        "Gadget(id='state_policy', namespace='test', name='State Policy Demo')",
                        "Call(",
                        "    id='prior_1s',",
                        "    when=Auction(''),",
                        "    bid=Bid('1S'),",
                        "    meaning=Meaning(action='opening', target_suit=S),",
                        "    effects=[State('opener.length.S', owner='opener', min_value=5)],",
                        ")",
                        "Call(",
                        "    id='raise_game',",
                        "    when=Auction('1SP'),",
                        "    bid=Bid('4S'),",
                        "    meaning=Meaning(action='place_contract', target_suit=S),",
                        ")",
                        "Call(",
                        "    id='raise_partscore',",
                        "    when=Auction('1SP'),",
                        "    bid=Bid('2S'),",
                        "    meaning=Meaning(action='simple_raise', target_suit=S),",
                        ")",
                    ]
                ),
                encoding="utf-8",
            )
            (gadget_dir / "raise.policy.py").write_text(
                "\n".join(
                    [
                        "def state_raise_policy(ctx, candidates):",
                        "    spades = ctx.state.estimate('opener.length.S')",
                        "    if spades.min_value >= 5:",
                        "        return candidates.get('4S')",
                        "    return None",
                        "",
                        "policy_functions = [state_raise_policy]",
                    ]
                ),
                encoding="utf-8",
            )

            profile = load_profile("state_policy", scratch)
            result = explain(
                choose_bid(
                    profile,
                    Auction.parse("1SP", dealer="n", vulnerability="none"),
                    Hand.parse("SA2H765D432C98765"),
                    {"dealer": "n", "vulnerability": "none"},
                )
            )

            self.assertEqual(result["call"], "4S")
            self.assertEqual(result["internal_origin"]["selection_policy"]["object_type"], "policy_function")
            self.assertEqual(result["internal_origin"]["selection_policy"]["object_id"], "state_raise_policy")
            self.assertEqual(
                result["internal_origin"]["state_view"]["estimates"]["opener.length.S"]["min_value"],
                5,
            )
        finally:
            _remove_tree(scratch)

    def test_loader_returns_profile_runtime_objects(self):
        profile = load_profile("meow_2over1", BACKEND_DIR)

        self.assertEqual(profile.id, "meow_2over1")
        self.assertGreaterEqual(len(profile.call_specs), 1)
        self.assertGreaterEqual(len(profile.frame_specs), 1)
        self.assertGreaterEqual(len(profile.private_route_specs), 1)
        self.assertGreaterEqual(len(profile.all_policy_functions), 1)

    def test_profile_policy_files_register_policy_functions(self):
        profile_policy_dir = BACKEND_DIR / "partnership_profiles" / "meow_2over1" / "policies"
        policy_files = list(profile_policy_dir.glob("*.policy.py"))

        self.assertGreaterEqual(len(policy_files), 1)
        self.assertTrue(
            all("policy_functions" in path.read_text(encoding="utf-8") for path in policy_files)
        )

    def test_loader_accepts_python_shaped_bsl(self):
        profile = load_profile("test_bsl_demo", BACKEND_DIR)
        auction = Auction.parse("", dealer="n", vulnerability="none")
        hand = Hand.parse("SAKQ87H32D765CK32")

        result = explain(choose_bid(profile, auction, hand, {"dealer": "n", "vulnerability": "none"}))

        self.assertEqual(result["call"], "1S")
        self.assertEqual(result["public_meaning"]["origin"]["gadget_id"], "test_bsl_demo")
        self.assertEqual(result["public_meaning"]["meaning"]["target_suit"], "S")

        trace = replay_auction(profile, Auction.parse("1S", dealer="n", vulnerability="none"), hand)
        self.assertTrue(
            any(
                _mapping_contains(state, {"key": "opener.length.S", "owner": "opener", "min_value": 5})
                for state in [item.to_dict() for item in trace.state_records]
            )
        )

    def test_bsl_rejects_imports(self):
        scratch = BACKEND_DIR / "tmp_bad_bsl.bsl.py"
        scratch.write_text("import os\nGadget(id='bad')\n", encoding="utf-8")
        try:
            with self.assertRaisesRegex(BSLValidationError, "Unsupported top-level syntax"):
                load_bsl_files([scratch])
        finally:
            scratch.unlink()

    def test_bsl_predicate_helpers_compile_as_conditions(self):
        scratch = BACKEND_DIR / "tmp_bsl_condition.bsl.py"
        scratch.write_text(
            "\n".join(
                [
                    "Gadget(id='condition_demo')",
                    "Call(",
                    "    id='cs_1',",
                    "    when=Auction('*'),",
                    "    bid=Bid('4N'),",
                    "    requires=StateExists('agreed_suit', target_suit=S),",
                    ")",
                ]
            ),
            encoding="utf-8",
        )
        try:
            module_data = load_bsl_files([scratch])
        finally:
            scratch.unlink()

        self.assertEqual(
            module_data.call_specs[0]["requires"],
            {"expr": {"op": "state_exists", "query": {"key": "agreed_suit", "target_suit": "S"}}},
        )

    def test_bsl_rejects_call_selection_keyword(self):
        scratch = BACKEND_DIR / "tmp_bsl_criterion.bsl.py"
        scratch.write_text(
            "\n".join(
                [
                    "Gadget(id='condition_demo')",
                    "Call(",
                    "    id='cs_1',",
                    "    when=Auction(''),",
                    "    bid=Bid('1N'),",
                    "    " + "selection" + "=lambda ctx: True,",
                    ")",
                ]
            ),
            encoding="utf-8",
        )
        try:
            with self.assertRaisesRegex(BSLValidationError, "selection"):
                load_bsl_files([scratch])
        finally:
            scratch.unlink()

    def test_bsl_accepts_python_evaluator_functions(self):
        scratch = BACKEND_DIR / "tmp_bsl_evaluator.bsl.py"
        scratch.write_text(
            "\n".join(
                [
                    "Gadget(id='evaluator_demo')",
                    "def balanced_range(ctx):",
                    "    return 15 <= ctx.hand.hcp <= 17 and ctx.hand.balanced",
                    "Evaluator(id='balanced_range', function=balanced_range)",
                ]
            ),
            encoding="utf-8",
        )
        try:
            module_data = load_bsl_files([scratch])
        finally:
            scratch.unlink()

        evaluator = module_data.evaluator_specs[0]
        self.assertEqual(evaluator["evaluator_type"], "python_function")
        self.assertTrue(callable(evaluator["definition"]))

    def test_profile_selection_policy_is_reported(self):
        profile = load_profile("meow_2over1", BACKEND_DIR)
        auction = Auction.parse("", dealer="n", vulnerability="none")
        hand = Hand.parse("SAQ7HKJ8DA762CQ54")

        result = explain(choose_bid(profile, auction, hand, {"dealer": "n", "vulnerability": "none"}))

        policy = result["internal_origin"]["selection_policy"]
        self.assertIsNotNone(policy)
        self.assertEqual(policy["object_type"], "policy_function")
        self.assertEqual(policy["object_id"], "meow_opening_notrump_policy")

    def test_state_view_supports_undefined_estimates(self):
        self.assertFalse(UNDEFINED > 0)
        self.assertEqual(UNDEFINED.or_default(0), 0)

        state = StateView()
        estimate = state.estimate("slam_interest")
        self.assertFalse(estimate.known)
        self.assertIs(state.value("slam_interest"), UNDEFINED)
        self.assertFalse(state.exists("unknown_field"))

    def test_state_view_combines_user_defined_ranges(self):
        origin = {"qualified_id": "test:state"}
        trace = AuctionTrace()
        trace.add_state(
            StateRecord.from_dict(
                {"key": "partner.hcp", "owner": "partner", "min_value": 6, "max_value": 10},
                origin,
            )
        )
        trace.add_state(
            StateRecord.from_dict(
                {"key": "partner.hcp", "owner": "partner", "min_value": 8, "max_value": 9},
                origin,
            )
        )
        trace.add_state(StateRecord.from_dict({"key": "fit", "suit": "S", "min_length": 8}, origin))

        state = StateView.from_trace(trace)
        estimate = state.estimate("partner.hcp")

        self.assertEqual(estimate.min_value, 8)
        self.assertEqual(estimate.max_value, 9)
        self.assertTrue(estimate.contains(8))
        self.assertFalse(estimate.contains(10))
        self.assertEqual(len(estimate.evidence), 2)
        self.assertTrue(state.exists("fit", suit="S"))
        self.assertFalse(state.exists("fit", suit="H"))

    def test_call_space_supports_relative_step_calls(self):
        self.assertEqual(steps_after("4S", 1), "4N")
        self.assertEqual(steps_after("4S", 2), "5C")
        self.assertEqual(steps_between("4S", "5C"), 2)

        relation = relation_to_last_contract(Auction.parse("1NP2DP3HP4S"), "5C")
        self.assertEqual(relation.last_contract, "4S")
        self.assertEqual(relation.steps_over_last_contract, 2)

    def test_decision_context_contains_candidate_pool_and_active_private_routes(self):
        profile = load_profile("meow_2over1", BACKEND_DIR)
        auction = Auction.parse("1NP2DP3HP", dealer="n", vulnerability="none")
        hand = Hand.parse("SA2HAKQJ8DA3CKQ32")

        selection = choose_bid(profile, auction, hand, {"dealer": "n", "vulnerability": "none", "scoring": "IMP"})

        self.assertIsNotNone(selection.context)
        self.assertIn("4N", selection.context.candidates.calls)
        self.assertGreaterEqual(len(selection.context.private_routes), 1)
        self.assertTrue(selection.context.state.exists("agreed_suit", suit="H"))
        self.assertGreaterEqual(len(selection.context.state.active_private_routes()), 1)

    def test_active_private_route_make_call_node_generates_candidate(self):
        profile = load_profile("meow_2over1", BACKEND_DIR)
        auction = Auction.parse("1NP2DP3HP", dealer="n", vulnerability="none")
        hand = Hand.parse("SA2HAKQJ87D53CKQ2")

        selection = choose_bid(profile, auction, hand, {"dealer": "n", "vulnerability": "none", "scoring": "IMP"})

        route_candidates = [
            candidate
            for candidate in selection.candidate_pool.candidates
            if candidate.call == "4N"
            and candidate.source_kind == "private_route_continuation"
            and candidate.private_route_origin is not None
        ]

        self.assertEqual(len(route_candidates), 1)
        self.assertEqual(route_candidates[0].private_route_origin["object_id"], "route_2")
        self.assertEqual(route_candidates[0].implementation_origin["gadget_id"], "meow_rkcb_1430")

    def test_new_frame_closes_prior_procedural_frame_but_keeps_state(self):
        profile = load_profile("meow_2over1", BACKEND_DIR)
        auction = Auction.parse("1NP2DP3HP4DP4N", dealer="n", vulnerability="none")
        hand = Hand.parse("SA2HAKQJ87D53CKQ2")

        trace = replay_auction(profile, auction, hand, {"dealer": "n", "vulnerability": "none"})

        self.assertTrue(trace.state_exists({"key": "agreed_suit", "suit": "H"}))
        frame_statuses = {(frame.frame_type, frame.status) for frame in trace.frame_states}
        self.assertIn(("major_transfer", "closed"), frame_statuses)
        self.assertIn(("control_bidding", "closed"), frame_statuses)
        self.assertIn(("rkcb_1430", "active"), frame_statuses)
        self.assertEqual([frame.frame_type for frame in trace.frame_states if frame.status == "active"], ["rkcb_1430"])
        self.assertEqual(StateView.from_trace(trace).dominant_frame().frame_type, "rkcb_1430")

    def test_puppet_replay_records_length_specific_fit_evidence(self):
        profile = load_profile("meow_2over1", BACKEND_DIR)
        auction = Auction.parse("1NP3CP3DP3HP4S", dealer="n", vulnerability="none")
        hand = Hand.parse("SAQ76HKJ8DA76CQ54")

        trace = replay_auction(profile, auction, hand, {"dealer": "n", "vulnerability": "none"})
        ctx = BridgeContext.from_trace(
            phase="test",
            auction=auction,
            hand=hand,
            environment={"dealer": "n", "vulnerability": "none"},
            trace=trace,
        )
        states = [item.to_dict() for item in trace.state_records]

        self.assertTrue(
            any(
                _mapping_contains(
                    state,
                    {
                        "key": "partnership.fit.S",
                        "suit": "S",
                        "opener_min_length": 4,
                        "responder_min_length": 4,
                        "min_total": 8,
                        "pattern_floor": "4-4",
                    },
                )
                for state in states
            )
        )
        self.assertEqual(ctx.knowledge.opener.S.length.value, 4)
        self.assertEqual(ctx.knowledge.responder.S.length.value, 4)
        self.assertEqual(ctx.knowledge.fit("S").min_total.min_value, 8)
        self.assertEqual(ctx.knowledge.fit("S").pattern_floor, "4-4")
        self.assertTrue(
            any(
                _mapping_contains(
                    state,
                    {
                        "key": "agreed_suit",
                        "suit": "S",
                        "opener_min_length": 4,
                        "responder_min_length": 4,
                        "pattern_floor": "4-4",
                    },
                )
                for state in states
            )
        )

    def test_dominant_frame_obligation_and_answer_capabilities_are_visible(self):
        profile = load_profile("meow_2over1", BACKEND_DIR)
        auction = Auction.parse("1NP2DP3HP4NP", dealer="n", vulnerability="none")
        hand = Hand.parse("SAQ74HKJ83DA62CQ5")

        selection = choose_bid(profile, auction, hand, {"dealer": "n", "vulnerability": "none"})

        self.assertEqual(selection.call, "5D")
        self.assertEqual(selection.context.dominant_frame.frame_type, "rkcb_1430")
        self.assertEqual(selection.context.frame_obligation["action"], "answer_frame")
        self.assertIn("answer_frame", selection.selected_candidate.capabilities)
        self.assertIn("keycard_response", selection.selected_candidate.capabilities)
        self.assertIn("5D", [candidate.call for candidate in selection.context.candidates.by_capability("answer_frame")])
        self.assertEqual([candidate.call for candidate in selection.context.obligation_candidates], ["5D"])

    def test_seat_memory_continues_selected_private_route_only_for_same_seat(self):
        scratch = BACKEND_DIR / "tmp_seat_memory"
        profile_dir = scratch / "partnership_profiles" / "seat_memory"
        gadget_dir = profile_dir / "gadgets" / "test" / "seat_memory"
        profile_dir.mkdir(parents=True, exist_ok=True)
        gadget_dir.mkdir(parents=True, exist_ok=True)
        try:
            (profile_dir / "profile.bsl.py").write_text(
                "Profile(id='seat_memory', name='Seat Memory', gadgets=['test.seat_memory'])\n",
                encoding="utf-8",
            )
            (gadget_dir / "gadget.bsl.py").write_text(
                "\n".join(
                    [
                        "Gadget(id='seat_memory', namespace='test', name='Seat Memory Demo')",
                        "Call(",
                        "    id='open_1n',",
                        "    when=Auction(''),",
                        "    bid=Bid('1N'),",
                        "    meaning=Meaning(action='notrump_opening'),",
                        "    effects=[State('notrump_focus', status='active')],",
                        ")",
                        "Call(",
                        "    id='transfer',",
                        "    when=Auction('1NP'),",
                        "    bid=Bid('2D'),",
                        "    meaning=Meaning(action='transfer', target_suit=H),",
                        ")",
                        "Call(",
                        "    id='complete_transfer',",
                        "    when=Auction('1NP2DP'),",
                        "    bid=Bid('2H'),",
                        "    meaning=Meaning(action='transfer_completion', target_suit=H),",
                        ")",
                        "PrivateRoute(",
                        "    id='route_a',",
                        "    owner='responder',",
                        "    goal='place_contract',",
                        "    context={'auction_pattern': '1NP'},",
                        "    preconditions={},",
                        "    entry_candidate=True,",
                        "    entry_call='2D',",
                        "    entry_score=100,",
                        "    workflow={'start': 'wait_1', 'nodes': {",
                        "        'wait_1': {'kind': 'wait_for_call', 'branches': [",
                        "            {'when': {'kind': 'call_is', 'value': '2H'}, 'goto': 'make_1'},",
                        "        ]},",
                        "        'make_1': {'kind': 'make_call', 'call': '3H', 'score': 300,",
                        "                   'meaning': {'action_type': 'place_contract', 'target_suit': 'H'}},",
                        "    }},",
                        ")",
                        "PrivateRoute(",
                        "    id='route_b',",
                        "    owner='responder',",
                        "    goal='place_contract',",
                        "    context={'auction_pattern': '1NP'},",
                        "    preconditions={},",
                        "    entry_candidate=True,",
                        "    entry_call='2D',",
                        "    entry_score=200,",
                        "    workflow={'start': 'wait_1', 'nodes': {",
                        "        'wait_1': {'kind': 'wait_for_call', 'branches': [",
                        "            {'when': {'kind': 'call_is', 'value': '2H'}, 'goto': 'make_1'},",
                        "        ]},",
                        "        'make_1': {'kind': 'make_call', 'call': '4H', 'score': 100,",
                        "                   'meaning': {'action_type': 'place_contract', 'target_suit': 'H'}},",
                        "    }},",
                        ")",
                    ]
                ),
                encoding="utf-8",
            )

            profile = load_profile("seat_memory", scratch)
            responder_hand = Hand.parse("SA2HAKQJ8D765C432")
            opener_hand = Hand.parse("SK3H765D5432CAKQJ")
            environment = {"dealer": "n", "vulnerability": "none"}

            first_decision = choose_bid(
                profile,
                Auction.parse("1NP", dealer="n", vulnerability="none"),
                responder_hand,
                environment,
            )

            self.assertEqual(first_decision.call, "2D")
            self.assertEqual(first_decision.private_memory.selected_routes[0].route_id, "route_b")

            opener_decision = choose_bid(
                profile,
                Auction.parse("1NP2DP", dealer="n", vulnerability="none"),
                opener_hand,
                environment,
                SeatMemory(),
            )

            self.assertEqual(opener_decision.call, "2H")
            self.assertEqual(opener_decision.context.memory.selected_routes, ())

            public_only_followup = choose_bid(
                profile,
                Auction.parse("1NP2DP2HP", dealer="n", vulnerability="none"),
                responder_hand,
                environment,
            )
            self.assertEqual(
                [candidate.call for candidate in public_only_followup.candidate_pool.candidates],
                ["3H", "4H"],
            )
            self.assertEqual(public_only_followup.call, "3H")

            memory_followup = choose_bid(
                profile,
                Auction.parse("1NP2DP2HP", dealer="n", vulnerability="none"),
                responder_hand,
                environment,
                first_decision.private_memory,
            )

            self.assertEqual(
                [candidate.call for candidate in memory_followup.candidate_pool.candidates],
                ["4H"],
            )
            self.assertEqual(memory_followup.call, "4H")
            self.assertEqual(memory_followup.context.memory.selected_routes[0].route_id, "route_b")
        finally:
            _remove_tree(scratch)

    def test_system_notes_are_generated_from_runtime_objects(self):
        profile = load_profile("meow_2over1", BACKEND_DIR)

        notes = generate_system_notes(profile)

        self.assertIn("# Meow 2/1 Benchmark", notes)
        self.assertIn("## Meow Four-Way Transfers Over 1N", notes)
        self.assertIn("### Private Routes", notes)
        self.assertIn("Workflow nodes", notes)
        self.assertIn("`meow_opening_one_level_seat_1_2_policy`", notes)
        self.assertIn("`alertable`=`false`", notes)
        self.assertIn('`auction_pattern`=`""`', notes)

    def test_system_notes_app_entrypoint_returns_markdown(self):
        result = system_notes({"profile": {"id": "meow_2over1"}})

        self.assertEqual(result["format"], "markdown")
        self.assertEqual(result["profile"]["id"], "meow_2over1")
        self.assertIn("1N opening shows 15-17 HCP", result["content"])

    def test_meow_named_evaluator_is_loaded_and_reported(self):
        profile = load_profile("meow_2over1", BACKEND_DIR)

        notes = generate_system_notes(profile)

        self.assertIn("eval_minor_honor_third", [item.id for item in profile.named_evaluators])
        self.assertIn("### Named Evaluators", notes)
        self.assertIn("Minor-transfer superaccept support requires honor-third", notes)
        self.assertIn("## Profile Policy Functions", notes)
        self.assertIn("`meow_opening_one_level_seat_1_2_policy`", notes)
        self.assertIn("`meow_major_raise_jacoby_policy`", notes)


def _mapping_contains(actual: dict, expected: dict) -> bool:
    return all(actual.get(key) == value for key, value in expected.items())


if __name__ == "__main__":
    unittest.main()


