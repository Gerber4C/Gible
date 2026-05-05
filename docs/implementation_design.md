# Bridge Bidding Platform Software Engineering Implementation Document

Platform Version: 0.0.6
Author: Meow Li
Copyright: Copyright (c) 2026 Meow Li. All Rights Reserved.

This is the code-reading document for engineers and AI agents. It describes the current implementation file by file, including class fields, important functions, YAML object structure, runtime flow, and known limitations.

## 1. Current Architecture

Partner currently has a Python backend prototype. The backend loads a Convention Set, parses a compact auction and compact hand string, replays prior calls to recover semantic trace data, chooses the next call from active Call Specifications, and returns public meaning plus internal origin.

The runtime is intentionally stateless at the API boundary. A request supplies only visible context: selected Convention Set, auction, own hand, dealer, vulnerability, scoring, and seat. Any hidden context, such as a pending transfer or possible bidding plan, is recovered by replaying the auction through active Conventions.

Current authoring format is YAML. These YAML files are the project's current Intermediate Representation serialization. Future Bridge System Language and GUI editing will compile or validate into the same object model before execution.

## 2. Repository Layout

```text
backend/
  app.py
  convention_sets/
    expert_2over1.yaml
    meow_2over1.yaml
  conventions/
    two_over_one/
      convention.yaml
      default_policy.yaml
      openings_notrump.yaml
      openings_one_level.yaml
      openings_two_level.yaml
      selection_openings.yaml
    four_way_jacoby_transfer/
      convention.yaml
      continuations_hearts.yaml
      notrump_responses.yaml
      protocols_major_transfer.yaml
      selection_after_1nt.yaml
    meow_two_over_one_core/
      convention.yaml
      default_policy.yaml
      openings.yaml
      selection.yaml
    meow_minor_opening_structure/
      convention.yaml
      openings.yaml
      responses.yaml
      rebids.yaml
    meow_inverted_minors/
      convention.yaml
      evaluators.yaml
      raises.yaml
    meow_crisscross_minor_raises/
      convention.yaml
      evaluators.yaml
      raises.yaml
      continuations.yaml
    meow_two_way_nmf_xyz/
      convention.yaml
      checkback.yaml
    meow_preemptive_openings/
      convention.yaml
      evaluators.yaml
      preempts.yaml
    meow_gambling_3nt/
      convention.yaml
      gambling.yaml
    meow_one_notrump_opening/
      convention.yaml
      openings.yaml
    meow_two_notrump_opening/
      convention.yaml
      openings.yaml
    meow_regular_stayman_over_1n/
      convention.yaml
      stayman.yaml
    meow_puppet_stayman_over_1n/
      convention.yaml
      puppet_stayman.yaml
    meow_puppet_stayman_over_2n/
      convention.yaml
      puppet_stayman.yaml
    meow_four_way_transfers_over_1n/
      convention.yaml
      evaluators.yaml
      transfers.yaml
    meow_texas_transfers_over_1n/
      convention.yaml
      texas.yaml
    meow_quantitative_notrump/
      convention.yaml
      quantitative.yaml
    meow_gerber_over_notrump/
      convention.yaml
      gerber.yaml
      protocols.yaml
    meow_control_bidding/
      convention.yaml
      controls.yaml
      protocols.yaml
    meow_kickback_keycard/
      convention.yaml
      kickback.yaml
      protocols.yaml
    meow_minorwood_keycard/
      convention.yaml
      minorwood.yaml
      protocols.yaml
    meow_exclusion_keycard/
      convention.yaml
      exclusion.yaml
      protocols.yaml
    meow_rkcb_1430/
      convention.yaml
      protocols.yaml
      rkcb.yaml
    meow_targeted_king_ask/
      convention.yaml
      targeted_king.yaml
      protocols.yaml
    meow_simple_major_raise/
      convention.yaml
      simple_raise.yaml
    meow_bergen_raises/
      convention.yaml
      bergen_spades.yaml
    meow_two_way_reverse_drury/
      convention.yaml
      drury_spades.yaml
    meow_jacoby_2nt_major_raise/
      convention.yaml
      jacoby_2nt_spades.yaml
    meow_kokish_game_tries/
      convention.yaml
      game_tries_spades.yaml
      selection.yaml
    meow_notrump_response_policy/
      convention.yaml
      selection.yaml
    meow_major_raise_policy/
      convention.yaml
      selection.yaml
  engine/
    __init__.py
    auction.py
    calls.py
    cards.py
    convention.py
    evaluator.py
    explanation.py
    legality.py
    loader.py
    matcher.py
    selector.py
    simulator.py
    system_notes.py
    trace.py
  tests/
    README.md
    test_cases.md
    test_fixture_cases.py
    cases/
      bidding.yaml
      full_auctions.yaml
      hands.yaml
      legality.yaml
      matcher.yaml
docs/
  bridge_system_language_roadmap.md
  documentation_system.md
  implementation_design.md
  ir_language_spec.md
  meow_2over1_benchmark.md
  product_description.md
  semantic_ontology.md
  todo.md
  user_manual.md
frontend/
  README.md
```

## 3. Naming And ID Policy

Human-authored IDs should be short stable handles, such as `cs_1`, `policy_1`, `frame_1`, or `plan_1`. The engine generates fully qualified IDs from namespace, Convention ID, version, object type, and object ID.

Human explanation belongs in explicit fields:

- `description`: project-facing explanation for maintainers and editors.
- `system_notes`: text intended for generated human-readable system notes.
- `meaning`: structured public partnership meaning.
- `selection`, `preconditions`, `workflow`, and `effects`: executable structure.

Executable behavior must not depend on prose or on semantic phrases embedded in IDs.

## 4. Runtime Flow

```text
backend/app.py bid(request)
  -> loader.load_convention_set(convention_set_id)
  -> Auction.parse(request["auction"], dealer, vulnerability)
  -> Hand.parse(request["hand"])
  -> selector.choose_bid(convention_set, auction, hand, environment)
       -> replay_auction(convention_set, auction, hand, environment)
            -> read prior visible calls
            -> match Call Specifications that explain those calls
            -> emit SemanticFact entries and typed AuctionStateVariable entries
            -> recover and advance active ProtocolFrameState entries
            -> recover and advance active PlanState entries
       -> gather current Call Specification candidates
       -> gather executable Bidding Plan entry-call and `make_call` candidates
       -> evaluate semantic `requires`
       -> evaluate applicability and selection criteria
       -> choose with matching Call Selection Policy
       -> use explicit default Call Specification if nothing applies
  -> explanation.explain(selection)
  -> return call, public_meaning, internal_origin, diagnostics
```

Important behavior: all active Conventions contribute in parallel. For example, the 1N opening can be specified in `two_over_one`, while after-1N responses are specified in `four_way_jacoby_transfer`.

Full-auction simulation uses the same stateless single-call engine one call at a time:

```text
backend/app.py simulate(request)
  -> loader.load_convention_set(convention_set_id)
  -> simulator.simulate_auction(convention_set, hands, dealer, vulnerability, environment)
       -> parse supplied partnership hands
       -> build the visible Auction after each call
       -> ask choose_bid for seats with supplied hands
       -> auto-pass seats without supplied hands
       -> stop after four opening passes or three passes after the last contract
  -> return compact auction, per-call records, and diagnostics
```

The simulator is for benchmark and training-style tests. It is not yet a complete table engine because auction legality and competitive inference are still limited.

## 5. Public Entry Points

### `backend/app.py`

Imports:

- `Auction`
- `Hand`
- `explain`
- `load_convention_set`
- `choose_bid`
- `generate_system_notes`

`bid(request: dict) -> dict`

Expected request:

```json
{
  "convention_set": {"id": "expert_2over1"},
  "seat": "n",
  "auction": "1NP2DP",
  "hand": "SAQ74HKJ83DA62CQ5",
  "environment": {
    "dealer": "n",
    "vulnerability": "none",
    "scoring": "IMP"
  }
}
```

Local variables:

- `convention_set_id`: ID from `request["convention_set"]["id"]`.
- `environment`: optional environment dictionary.
- `dealer`: defaults to `n`.
- `vulnerability`: defaults to `none`.
- `convention_set`: loaded `ConventionSet`.
- `auction`: parsed `Auction`.
- `hand`: parsed `Hand`.
- `selection`: `Selection` returned by `choose_bid`.

Return value is the dictionary from `explain(selection)`.

`system_notes(request: dict) -> dict`

Expected request:

```json
{
  "convention_set": {"id": "expert_2over1"}
}
```

Return shape:

```json
{
  "format": "markdown",
  "convention_set": {
    "id": "expert_2over1",
    "name": "Expert 2/1",
    "version": "0.1.0"
  },
  "content": "# Expert 2/1\n..."
}
```

This is the first programmatic entry point for generated formal system notes.

`simulate(request: dict) -> dict`

Expected request:

```json
{
  "convention_set": {"id": "meow_2over1"},
  "hands": {
    "n": "SAQJ76H82DQ82CAJ3",
    "s": "SK98H74DKJ7CK9852"
  },
  "environment": {
    "dealer": "n",
    "vulnerability": "none",
    "scoring": "IMP"
  },
  "max_calls": 80
}
```

Local variables:

- `convention_set_id`: ID from `request["convention_set"]["id"]`.
- `environment`: optional environment dictionary.
- `dealer`: defaults to `n`.
- `vulnerability`: defaults to `none`.
- `convention_set`: loaded `ConventionSet`.
- `simulation`: `SimulatedAuction` returned by `simulate_auction`.

Return shape:

```json
{
  "auction": "1SP2SP3DP4SPPP",
  "calls": ["1S", "P", "2S", "P", "3D", "P", "4S", "P", "P", "P"],
  "records": [
    {"seat": "n", "call": "1S", "explanation": {"call": "1S"}}
  ],
  "diagnostics": []
}
```

Seats with no supplied hand are represented with `"explanation": null` because they are automatic passes in the current simulator.

## 6. Canonical Calls

### `backend/engine/calls.py`

Constants:

- `SUITS = ("C", "D", "H", "S", "N")`
- `SPECIAL_CALLS = {"P", "X", "R"}`
- `CALL_ALIASES`: maps common text such as `PASS`, `DBL`, `XX`, and `1NT` to canonical form.
- `SUIT_RANK`: numeric order for contract comparison.

`ContractBid`

Frozen dataclass fields:

- `level: int`
- `suit: str`

Methods and properties:

- `parse(call)`: parses a contract call and rejects `P`, `X`, `R`.
- `rank`: numeric rank ordered by level and suit.
- `__str__`: canonical string such as `1N`.

Functions:

- `normalize_call(call)`: strips spaces, uppercases, applies aliases, validates, and returns canonical call text.
- `parse_call_sequence(sequence)`: parses compact strings such as `1NP1SPXR`, allowing spaces anywhere.
- `normalize_pattern(pattern)`: normalizes auction patterns; preserves `*` for default behavior.
- `is_contract_bid(call)`: true for canonical contract calls.
- `compare_contract_bids(left, right)`: compares contract rank.

## 7. Auction Model

### `backend/engine/auction.py`

Constants:

- `SEATS = ("n", "e", "s", "w")`
- `VULNERABILITY_STATES = ("none", "ns", "ew", "both")`

`Auction`

Frozen dataclass fields:

- `calls: tuple[str, ...]`
- `dealer: str`
- `vulnerability: str`

Methods and properties:

- `parse(calls, dealer="n", vulnerability="none")`: normalizes calls, dealer, and vulnerability.
- `actor_to_call`: absolute seat whose turn it is.
- `actor_at(index)`: absolute seat for call index.
- `compact_sequence()`: compact auction string.
- `canonical_key()`: unique string including dealer, vulnerability, and calls.

Current limitation: call tokens are validated, but complete bridge auction legality is not yet enforced.

## 8. Hand Model

### `backend/engine/cards.py`

`Hand`

Frozen dataclass fields:

- `spades: str`
- `hearts: str`
- `diamonds: str`
- `clubs: str`

Each field stores uppercase rank text. `10` becomes `T`; `X` is an unknown small-card placeholder.

Methods and properties:

- `parse(data, validate_count=True)`: accepts only compact hand strings.
- `from_compact(text, validate_count=True)`: parses raw strings such as `H8763SK10C2DAKQ987`.
- `validate(validate_count=True)`: checks card count and repeated known physical cards.
- `hcp`: computes standard high-card points.
- `suits`: returns a dictionary by long suit name.
- `length(suit)`: returns suit length for long suit names or short symbols `S`, `H`, `D`, `C`.
- `holding(suit)`: returns the normalized rank string for a suit.
- `honor_count(suit, ranks=("A","K","Q","J"))`: counts listed honor ranks in a suit.
- `contains_rank(suit, rank)`: true when the hand contains that known card.
- `ace_count(excluded_suit=None)`: counts aces, optionally excluding one suit for Exclusion-style asks.
- `king_count(excluded_suit=None)`: counts kings, optionally excluding one suit.
- `keycard_count(trump_suit, excluded_suit=None)`: counts aces plus the trump king for keycard tests; the optional excluded suit supports Exclusion/Voidwood-style keycard asks.
- `balanced`: true for 5332, 4432, or 4333 shape.

Parser behavior:

- Suit markers are `S H D C`.
- Suit order is flexible.
- Repeated suit sections concatenate.
- Missing suits are voids if total count remains valid.
- `-` marks a void section.
- `10` and `T` both mean ten.
- `x` or `X` means an unknown small card.
- Wrong count, repeated known card, unknown symbol, rank before suit, isolated `1`, and `-` mixed with cards raise exceptions.

`normalize_suit_name(suit)`

Accepts short suit symbols and long lowercase names. This keeps YAML expressions compact while preserving long internal field names.

## 9. Convention Object Model

### `backend/engine/convention.py`

This file defines typed IR objects loaded from YAML.

Constants:

- `PLAN_NODE_KINDS`: allowed Bidding Plan workflow node kinds: `make_call`, `wait_for_call`, `branch`, `select_by_policy`, `enter_protocol`, `update_plan_state`, `end_plan`, `fail_plan`.
- `PLAN_BRANCH_PREDICATE_KINDS`: allowed branch predicate kinds: `call_is`, `call_act_type_is`, `protocol_frame_matches`, `state_has`, `state_missing`, `hand_predicate`, `environment_predicate`, `interference_level`, `obligation_status`.
- `PLAN_GOALS`: allowed plan goals: `signoff`, `invite_game`, `force_game`, `explore_slam`, `ask_keycards`, `resolve_shape`, `show_feature`, `compete`, `escape`, `place_contract`.

`Author`

Fields:

- `name`
- `contact`
- `organization`

Methods:

- `from_dict(data)`
- `to_dict()`

`Convention`

Fields:

- `id`
- `namespace`
- `name`
- `version`
- `author`
- `call_specifications`
- `protocol_frames`
- `bidding_plans`
- `call_selection_policies`
- `named_evaluators`
- `relay_automata`
- `description`
- `system_notes`

Methods and properties:

- `from_parts(...)`: builds a Convention from metadata plus object lists.
- `qualified_id`: `namespace/id@version`.

`ConventionSet`

Fields:

- `id`
- `name`
- `version`
- `author`
- `conventions`
- `description`
- `system_notes`

Computed properties flatten active Convention objects:

- `call_specifications`
- `protocol_frames`
- `bidding_plans`
- `call_selection_policies`
- `named_evaluators`
- `relay_automata`

`CallSpecification`

Fields:

- `id`
- `context`
- `call`
- `convention_id`
- `convention_namespace`
- `convention_version`
- `convention_name`
- `author`
- `call_act_types`
- `requires`
- `applicability`
- `selection`
- `meaning`
- `effects`
- `default_policy`
- `description`
- `system_notes`

Methods and properties:

- `from_dict(data, convention, inherited_author)`: normalizes context and call text.
- `auction_pattern`: reads `context.auction_pattern`.
- `has_selection`: true when selection data exists.
- `has_meaning`: true when meaning data exists.
- `qualified_id`: `namespace/convention@version:call_specification:id`.
- `origin_dict()`: provenance used by public meaning and internal origin.

Field meanings:

- `context`: visible auction matching data, mainly `auction_pattern` and optional `seat_positions`.
- `requires`: semantic conditions evaluated against replay-derived trace before a call can be selected or used to explain a prior call.
- `applicability`: conditions that may apply to both replay and current selection.
- `selection`: current-hand criteria for choosing this call.
- `meaning`: public agreement meaning and alertability.
- `effects`: semantic facts or typed auction-state variables emitted during replay.
- `description` and `system_notes`: human-readable text for editors and generated notes.

`ProtocolFrame`

Fields:

- `id`
- `frame_type`
- `context`
- source Convention metadata
- `author`
- `description`
- `system_notes`
- `variables`
- `stages`
- `allowed_continuations`
- `break_conditions`
- `source_call`

Methods:

- `from_dict(...)`
- `origin_dict()`

Current execution: Protocol Frames are loaded and recovered into trace state when their `source_call` and context match a prior call. The first executable stage behavior is implemented: a frame records `current_stage`, transfer completion or superaccept advances a transfer frame from `opener_rebid` to `responder_continuation`, and replayed final-placement Call Specifications can close active transfer frames.

`BiddingPlan`

Fields:

- `id`
- `owner`
- `goal`
- `context`
- `preconditions`
- `entry_call`
- `selection`
- `entry_candidate`
- `entry_score`
- `workflow`
- source Convention metadata
- `author`
- `description`
- `system_notes`

Methods:

- `from_dict(...)`: validates plan goal and workflow structure.
- `start_node`: `workflow["start"]`.
- `origin_dict()`

Workflow validation requires:

- non-empty `start`,
- non-empty `nodes`,
- start node exists,
- every node kind is in `PLAN_NODE_KINDS`,
- every branch has a typed predicate,
- every branch target exists when a target is declared.

Current execution: plans can generate an entry-call candidate when `entry_candidate: true`, the plan context matches, preconditions pass, and the entry call has an eligible Call Specification. Plans are also loaded and recovered as active `PlanState` objects after their entry call appears. The first executable workflow behavior is implemented: `wait_for_call` nodes advance through `call_is`, `call_act_type_is`, `state_has`, and `state_missing` branches, and a current `make_call` node can generate a candidate call when the plan preconditions match the current hand. If a plan-generated call is implemented by an eligible Call Specification, public meaning comes from that Call Specification and private route provenance is stored as `plan_origin`.

`CallSelectionPolicy`

Fields:

- `id`
- `algorithm`
- source Convention metadata
- `author`
- `scope`
- `candidate_filter`
- `tie_breaker`
- `same_call_resolution`
- `choices`
- `fallback`
- `evaluators`
- `random_source`
- `description`
- `system_notes`

Methods and properties:

- `from_dict(...)`
- `qualified_id`
- `origin_dict()`

Current supported selection algorithms are `highest_score`, `weighted_score_highest`, and `ordered_condition`. `same_call_resolution` currently supports the default `diagnose` behavior and explicit highest-score resolution values such as `highest_score`.

`choices` is used by `ordered_condition`. Each choice has:

- `choose_call`: canonical call to choose if the choice applies and that call is already an eligible candidate.
- `when`: condition evaluated with the same evaluator used by `applicability`, so it can read hand, trace, and environment.

`fallback` declares what to do if no ordered choice selects an eligible candidate. The current executable fallback is highest-score selection.

`NamedEvaluator`

Fields:

- `id`
- `evaluator_type`
- source Convention metadata
- `author`
- `definition`
- `description`
- `system_notes`

Current execution: expression-type Named Evaluators are collected into the active environment and can be used from selection criteria with `evaluator: named_evaluator`, `evaluator_id`, and optional `params`. Other evaluator types are loaded but not executable yet.

`RelayAutomaton`

Fields:

- `id`
- source Convention metadata
- `author`
- `asker`
- `describer`
- `current_stage`
- `next_relay_call`
- `response_decoder`
- `step_table`
- `reserved_calls`
- `break_conditions`
- `interference_policy`
- `description`
- `system_notes`

Current execution: loaded but not executable yet.

Current Bidding Plan detail: when replay sees a call that matches an active `make_call` node, the plan moves to the node named by `goto` or `then`; if no next node is declared, the plan closes. This prevents a completed private route from generating stale candidates later in the same stateless replay.

Private helpers:

- `_normalize_context(context)`: normalizes `auction_pattern`.
- `_normalize_scope(scope)`: normalizes nested policy context.
- `_validate_plan_workflow(workflow)`: validates Bidding Plan node graph.
- `_validate_branch_predicate(predicate, node_id)`: validates branch predicate type.
- `_ir_origin(...)`: builds consistent provenance dictionaries.

## 10. Loader

### `backend/engine/loader.py`

Optional dependency:

- Uses PyYAML when installed.
- Falls back to JSON parsing if PyYAML is unavailable.

`load_convention_set(convention_set_id, base_dir=None) -> ConventionSet`

Behavior:

1. Reads `backend/convention_sets/<id>.yaml`.
2. Reads `conventions`.
3. Loads each Convention directory under `backend/conventions/`.
4. Returns a `ConventionSet`.

`_load_convention(convention_path) -> Convention`

Behavior:

1. Reads `convention.yaml`.
2. Reads every other YAML file in the directory.
3. Collects top-level arrays:
   - `call_specifications`
   - `protocol_frames`
   - `bidding_plans`
   - `call_selection_policies`
   - `named_evaluators`
   - `relay_automata`
4. Calls `Convention.from_parts(...)`.

`_read_yaml(path) -> dict`

Reads UTF-8 text and returns a dictionary. Empty YAML becomes `{}`.

## 11. Matcher

### `backend/engine/matcher.py`

Functions:

- `matches_context(context, auction)`: matches a context dictionary against the current auction.
- `matches_pattern(pattern, auction, seat_positions=None)`: normalizes and compares auction patterns.
- `historical_pattern_for(calls, index)`: returns compact calls before an index.

Important behavior:

- `context.auction_pattern` is exact after canonical normalization.
- `context.seat_positions` expands initial-pass variants.
- Example: `auction_pattern: ""` with `seat_positions: [1,2,3,4]` matches empty auction, `P`, `PP`, and `PPP`.
- Example: `auction_pattern: "1NP"` with `seat_positions: [3]` matches `PP1NP`.
- `*` is used only for explicit default behavior.

## 12. Evaluation

### `backend/engine/evaluator.py`

`evaluate(condition, hand, trace, environment=None) -> bool`

Supported logical forms:

- `all`
- `any`
- `not`
- `fact_exists`
- `state_has`
- `state_missing`
- `auction_state_exists`
- `auction_state_missing`
- `auction_state_compare`
- `expr`
- direct comparisons against resolved values

Resolved direct-comparison inputs:

- `self.hcp`
- `self.balanced`
- `self.spades`
- `self.hearts`
- `self.diamonds`
- `self.clubs`
- `env.<key>`

Direct-comparison operators:

- `min`
- `max`
- `eq`
- `in`

`evaluate_selection(selection, hand, trace, environment=None) -> dict`

Current algorithm:

- `weighted_score`

Return dictionary:

- `algorithm`
- `eligible`
- `score`
- `criteria_results`

`evaluate_criterion(criterion, hand, trace, environment) -> dict`

Supported evaluator names:

- `range_contains`
- `min_value`
- `equals`
- `fact_exists`
- `expression`
- `named_evaluator`

Criteria are required by default. A criterion with `required: false` can add weight without disqualifying the Call Specification when it fails.

`evaluate_expression(expr, hand, trace, environment, params=None) -> Any`

The expression interpreter is the current executable calculation layer for bridge judgment. It is deliberately small and deterministic.

Literal and reference nodes:

- `{const: value}` returns the literal value.
- `{var: self.hcp}` and `{var: self.balanced}` read current-hand values.
- `{var: self.S.length}`, `{var: self.hearts.length}`, and equivalent suit names read suit length.
- `{var: partner.hcp}` and `{var: partner.S.length}` require `environment["partner_hand"]`.
- `{var: env.scoring}` reads environment values. Current derived environment values include `env.seat`, `env.dealer`, `env.vulnerability`, `env.vulnerability_relation`, and `env.seat_position`.
- `{param: target_suit}` reads a parameter passed by the criterion.

Supported expression operators:

- Boolean: `and`, `or`, `not`.
- Comparison: `eq`, `neq`, `lt`, `lte`, `gt`, `gte`, `in`.
- Arithmetic: `add`, `sub`, `mul`, `div`, `min`, `max`, `abs`.
- Conditional: `if`.
- Hand features: `length`, `honor_count`, `contains_rank`, `ace_count`, `king_count`, `keycard_count`.
- Trace query: `fact_exists`, `state_has`, `state_missing`, `auction_state_exists`, `auction_state_missing`, `auction_state_compare`.
- Trace value read: `fact_attribute`, `auction_state_attribute`.

`keycard_count` accepts optional `excluded_suit`. This lets a Call Specification count keycards for ordinary RKCB, Kickback, Minorwood, and Exclusion keycard without adding a separate hard-coded evaluator for each Convention.

`fact_attribute` reads an attribute from a recovered semantic fact. It takes `query`, `attribute`, optional `which`, and optional `default`. The current implementation uses `which: last` by default, so a reusable Call Specification can read the latest agreed suit or keycard context without knowing the exact auction that created it.

`auction_state_attribute` reads an attribute from a recovered `AuctionStateVariable`. It takes the same `query`, `attribute`, optional `which`, and optional `default` shape. This is the first executable path for range-like and scalar internal state such as `opener.hcp`, `opener.length.S`, `partnership.force_status`, and private route-purpose variables.

Named evaluator execution:

1. `selector._active_environment` collects expression-type `NamedEvaluator` objects from the active Convention Set.
2. A criterion with `evaluator: named_evaluator` reads `evaluator_id`.
3. `params` are supplied to the expression through `{param: ...}` nodes.
4. The expression result is converted to boolean for pass/fail and is also reported as the criterion value.

## 13. Semantic Trace

### `backend/engine/trace.py`

`SemanticFact`

Fields:

- `fact_type`
- `attributes`
- `origin`

Methods:

- `from_dict(data, origin)`
- `matches(query)`
- `to_dict()`

`AuctionStateVariable`

Fields:

- `key`: dotted state path such as `opener.hcp`, `opener.length.S`, or `partnership.force_status`.
- `namespace`: state namespace. `public` is intended for portable shared state; `private` is intended for Convention Set-specific internal route logic.
- `owner`: optional bridge owner such as `opener`, `responder`, or `partnership`.
- `attributes`: scalar or range data such as `value`, `min_value`, `max_value`, `source`, or Convention-specific typed attributes.
- `origin`: provenance of the Call Specification that emitted the state variable.

Methods:

- `from_dict(data, origin)`
- `matches(query)`
- `attribute(name)`
- `to_dict()`

`ProtocolFrameState`

Fields:

- `frame_id`
- `frame_type`
- `status`
- `current_stage`
- `variables`
- `origin`

Method:

- `to_dict()`

`PlanState`

Fields:

- `plan_id`
- `goal`
- `owner`
- `current_node`
- `status`
- `origin`

Method:

- `to_dict()`

`SemanticTrace`

Mutable fields:

- `facts`
- `auction_state`
- `applied_meanings`
- `protocol_frames`
- `plan_states`
- `diagnostics`

Methods:

- `add_fact(fact)`
- `add_auction_state(variable)`
- `fact_exists(query)`
- `matching_facts(query)`
- `auction_state_exists(query)`
- `matching_auction_state(query)`
- `auction_state_compare(query)`
- `add_applied_meaning(entry)`
- `add_protocol_frame(frame)`
- `add_plan_state(plan_state)`
- `warn(text)`

Current limitation: `AuctionStateVariable` is still a lightweight typed variable store, not a full conflict-resolving ontology. It is the first executable bridge from flexible `SemanticFact` entries toward the target typed semantic state.

## 14. Auction Legality

### `backend/engine/legality.py`

This file provides central bridge-call legality helpers used by bidding selection and simulation.

Constants:

- `SIDE_BY_SEAT`: maps absolute seats to `ns` or `ew`.

Dataclasses:

- `ContractState`: current contract call, auction index, seat, side, doubled flag, and redoubled flag.
- `IllegalCall`: illegal historical call, index, and reason.

Functions:

- `auction_is_complete(auction)`: true after four passes or after a contract followed by three passes.
- `legal_calls(auction)`: returns currently legal calls.
- `is_call_legal(auction, call)`: checks a single candidate call.
- `illegal_calls_in_auction(auction)`: validates historical calls one by one.
- `last_contract_state(auction)`: returns the latest contract plus double/redouble state.

Current legality scope:

- contract bids must outrank the current contract,
- `P` is legal until the auction is complete,
- `X` requires an undoubled contract by the opposing side,
- `R` requires a doubled contract by our side,
- completed auctions accept no further calls.

## 15. Selection

### `backend/engine/selector.py`

`Candidate`

Frozen dataclass fields:

- `call`
- `origin`
- `public_meaning`
- `algorithm`
- `call_specification_id`
- `score`
- `criteria_results`
- `plan_origin`

`origin` is the public executable origin for the selected call, normally a Call Specification. `plan_origin` is optional private provenance for a Bidding Plan that selected that public call. For example, transfer-slam `4N` can publicly originate from the standalone RKCB Call Specification while internally reporting that it was selected by a transfer-slam Bidding Plan.

`Selection`

Frozen dataclass fields:

- `call`
- `selected`
- `candidates`
- `trace`
- `selection_policy`

`choose_bid(convention_set, auction, hand, environment=None) -> Selection`

Selection steps:

1. Replays the auction into `SemanticTrace`.
2. Validates historical calls and records diagnostics for illegal prior calls.
3. Iterates active Call Specifications.
4. Skips default Call Specifications and objects without selection data.
5. Requires context match.
6. Evaluates top-level `requires` against replayed trace and active environment.
7. Evaluates top-level applicability.
8. Evaluates `selection.applicability`.
9. Evaluates selection criteria.
10. Builds Call Specification candidates.
11. Builds executable Bidding Plan candidates from declared entry-call plans and active `make_call` nodes.
12. Filters illegal candidate calls.
13. Finds the first matching Call Selection Policy.
14. Resolves or diagnoses same-call meaning collisions.
15. Applies `ordered_condition` choices when the matching policy uses that algorithm.
16. Otherwise sorts candidates by score.
17. Reports a tie diagnostic when top scores tie under score selection.
18. Falls back to explicit default Call Specification when no normal or plan candidate applies.

`replay_auction(convention_set, auction, hand=None, environment=None) -> SemanticTrace`

Replay steps:

1. Iterates prior non-pass calls.
2. Finds matching Call Specifications with public meaning.
3. Evaluates each match's `requires` against trace recovered so far.
4. Materializes dynamic effect values, then emits effects as `SemanticFact` entries or `AuctionStateVariable` entries.
5. Records applied meanings with origin.
6. Advances active Protocol Frames and Bidding Plans using the replayed call.
7. Recovers matching Protocol Frames by `source_call` and context.
8. Recovers matching Bidding Plans by `entry_call` and context.

Current replay detail: plan preconditions are not evaluated during replay because the visible auction may contain another player’s action while the stateless API only supplies the current hand.

Private helpers:

- `_active_environment(...)`: copies request environment, derives `seat`, `dealer`, `vulnerability`, `seat_position`, and `vulnerability_relation`, and installs expression-type Named Evaluators.
- `_candidate(...)`
- `_plan_candidates(...)`
- `_entry_plan_candidates(...)`
- `_evaluate_plan_selection(...)`
- `_matching_candidate_for_call(...)`
- `_plan_state_exists(...)`
- `_select_candidate(...)`
- `_select_by_ordered_condition(...)`
- `_ordered_with_selected_first(...)`
- `_resolve_same_call_meanings(...)`
- `_same_final_pass_action(...)`: treats multiple `P` candidates with `action_type: pass_final_contract` as the same structural action so a generic final-pass policy can coexist with a Convention-specific final pass.
- `_plan_candidate_for_implemented_call(...)`
- `_matching_policy(...)`
- `_recover_protocol_frames(...)`
- `_advance_protocol_frames(...)`
- `_next_protocol_stage(...)`
- `_frame_should_close(...)`
- `_recover_bidding_plans(...)`
- `_advance_bidding_plans(...)`
- `_plan_for_state(...)`
- `_matching_plan_branch_target(...)`
- `_plan_branch_matches(...)`
- `_plan_status_for_node(...)`
- `_default_candidate(...)`
- `_candidate_from_default_call_specification(...)`
- `_hard_fallback_candidate()`
- `_apply_effect(...)`: routes ordinary flat effects to `SemanticFact` and effects shaped as `state:` or `state_update:` to `AuctionStateVariable`.
- `_materialize_effect(...)`
- `_materialize_value(...)`

Dynamic effect values use an `expr` wrapper inside an effect attribute. Example: RKCB writes `keycard_context.trump_suit` by evaluating a `fact_attribute` expression against the current trace. This lets Texas, simple raises, Bergen, Drury, Jacoby 2N, and later other Conventions create `agreed_suit`, while the standalone RKCB Convention consumes it.

Same-call meaning resolution is generic. If two eligible Call Specifications produce the same call, such as two meanings for `4N`, the selector diagnoses an ambiguous meaning unless the matching Call Selection Policy declares a same-call resolution mode. This keeps quantitative `4N`, RKCB, Blackwood, and later competitive meanings as peer Conventions.

## 15. Simulator

### `backend/engine/simulator.py`

Constants:

- `PARTNERS`: maps `n` to `s`, `s` to `n`, `e` to `w`, and `w` to `e`.

`SimulatedCall`

Frozen dataclass fields:

- `seat`: absolute seat that made the call.
- `call`: canonical call text.
- `explanation`: explanation dictionary from `explain(selection)` for supplied partnership hands, or `None` for automatic opponent passes.

`SimulatedAuction`

Frozen dataclass fields:

- `calls`: tuple of canonical calls.
- `call_records`: tuple of `SimulatedCall`.
- `diagnostics`: tuple of diagnostic strings accumulated from each selected partnership call.

Method:

- `compact_sequence()`: returns the compact auction string.

`simulate_auction(convention_set, hands, dealer="n", vulnerability="none", environment=None, max_calls=80) -> SimulatedAuction`

Behavior:

1. Parses each supplied hand by absolute seat.
2. Builds a fresh `Auction` object from visible calls before each turn.
3. Stops when `auction_is_complete` is true.
4. Auto-passes seats without supplied hands.
5. For seats with supplied hands, calls `choose_bid`.
6. Adds `partner_hand` to the environment when the partner hand is supplied.
7. Appends any diagnostics returned by the explanation output.
8. Stops at `max_calls` and reports a diagnostic if the auction has not completed.

`auction_is_complete(auction) -> bool`

Returns true for:

- four passes at the start of the auction,
- or three passes after the last contract call.

Private helper:

- `_last_contract_index(calls)`: finds the last contract bid in a call tuple.

Current limitation: this simulator assumes missing hands are opponent passers. It does not yet validate complete auction legality, doubles, redoubles, claims, scoring, or competitive obligations.

## 16. Explanation Output

### `backend/engine/explanation.py`

`explain(selection) -> dict`

Return fields:

- `call`
- `public_meaning`
- `internal_origin`
- `diagnostics`

`public_meaning` contains:

- selected origin
- structured public meaning

`internal_origin` contains:

- `selected`
- `compared_candidates`
- `applied_meanings`
- `semantic_facts`
- `protocol_frames`
- `plan_states`
- `selection_policy`

Internal origin is for training, debugging, and authoring. It is separate from public disclosure. When a Bidding Plan chooses a call implemented by a Call Specification, `public_meaning.origin` stays with the Call Specification and `internal_origin.selected.plan_origin` records the private plan.

## 17. System Notes Generation

### `backend/engine/system_notes.py`

`generate_system_notes(convention_set) -> str`

Generates formal Markdown from the loaded IR objects.

Rendered sections:

- Convention Set metadata.
- Convention metadata.
- Call Specifications.
- Protocol Frames.
- Bidding Plans.
- Call Selection Policies.
- Named Evaluators.

Important helpers:

- `_render_convention(...)`
- `_render_call_specification(...)`
- `_render_bidding_plan(...)`
- `_format_context(...)`
- `_format_mapping(...)`
- `_format_list(...)`

The generator uses structured IR as the source of truth. `description` and `system_notes` fields provide human explanation, but they do not drive execution.

## 18. Current YAML Structure

### Convention Set

```yaml
id: expert_2over1
name: Expert 2/1
description: >
  Prototype Convention Set for the current 2/1 and after-1N implementation.
conventions:
  - two_over_one
  - four_way_jacoby_transfer
```

The current practical benchmark uses:

```yaml
id: meow_2over1
name: Meow 2/1 Benchmark
description: >
  Practical benchmark Convention Set for Meow Li's 2/1 agreements.
conventions:
  - meow_two_over_one_core
  - meow_minor_opening_structure
  - meow_preemptive_openings
  - meow_gambling_3nt
  - meow_one_notrump_opening
  - meow_two_notrump_opening
  - meow_inverted_minors
  - meow_crisscross_minor_raises
  - meow_two_way_nmf_xyz
  - meow_regular_stayman_over_1n
  - meow_puppet_stayman_over_1n
  - meow_puppet_stayman_over_2n
  - meow_four_way_transfers_over_1n
  - meow_texas_transfers_over_1n
  - meow_quantitative_notrump
  - meow_gerber_over_notrump
  - meow_control_bidding
  - meow_kickback_keycard
  - meow_minorwood_keycard
  - meow_exclusion_keycard
  - meow_rkcb_1430
  - meow_targeted_king_ask
  - meow_simple_major_raise
  - meow_bergen_raises
  - meow_two_way_reverse_drury
  - meow_jacoby_2nt_major_raise
  - meow_kokish_game_tries
  - meow_notrump_response_policy
  - meow_major_raise_policy
```

The Meow benchmark intentionally keeps reusable bridge methods in separate Convention directories. For example, Texas transfers create `agreed_suit`, quantitative notrump requires notrump focus without an agreed suit, and standalone slam Conventions consume semantic state. `meow_rkcb_1430`, `meow_gerber_over_notrump`, `meow_kickback_keycard`, `meow_minorwood_keycard`, `meow_exclusion_keycard`, `meow_control_bidding`, and `meow_targeted_king_ask` are separate so a Convention Set can include or omit them independently. Bergen, Drury, Jacoby 2N, Kokish game tries, minor opening continuations, inverted minors, Crisscross, checkback/XYZ, preemptive openings, and Gambling 3N are also separate Conventions, coordinated by integration policy Conventions and semantic facts.

### Minor Opening Slice

The current executable minor-opening slice is split across six Convention directories.

- `meow_minor_opening_structure` owns natural `1C` and `1D` openings, one-level responses, natural `1N`/`2N`/`3N` responses, weak jump-shift major responses, and simple opener rebids. Its `openings.yaml` creates `minor_opening` facts; `responses.yaml` creates `one_level_response`, `notrump_response`, `weak_jump_shift`, and `final_contract` facts; `rebids.yaml` creates `opener_rebid`, `opener_notrump_rebid`, and `agreed_suit` facts.
- `meow_inverted_minors` owns `1C P 2C` and `1D P 2D`. These calls are alertable, invitational or better, deny a four-card major, create `minor_raise`, `agreed_suit`, and `forcing_status`, and define stopper-showing continuations. `eval_stopper` is a Named Evaluator used by `2N` and stopper-up-the-line rebids.
- `meow_crisscross_minor_raises` owns `1C P 2D` and `1D P 3C` as game-forcing minor raises. It creates `minor_raise`, `agreed_suit`, and `forcing_status` facts, and includes a small `3N`-or-minor fallback continuation for full-auction tests.
- `meow_two_way_nmf_xyz` owns two-way NMF/XYZ checkback after opener's `1N` rebid or a three-call one-level auction. It uses semantic facts from `opener_rebid` and `opener_notrump_rebid` rather than enumerating every sequence. Its executable calls include `2C` relay to `2D`, artificial game-forcing `2D`, `2N` transfer to `3C` for weak club drop-dead routes, forced relay completions, and simple checkback continuations.
- `meow_preemptive_openings` owns weak `2D`, `2H`, `2S` and natural three-level preempts. The active environment supplies `env.seat_position` and `env.vulnerability_relation`; Named Evaluators use those values to make first/second/third-seat and favorable/unfavorable style decisions.
- `meow_gambling_3nt` owns alertable Gambling `3N`, requiring a solid seven-card or longer minor and no outside ace or king. It creates `gambling_3nt` and `running_minor` facts.

Engine support added for this slice:

- `selector._active_environment` now derives `seat_position` for opening auctions and `vulnerability_relation` for the actor from absolute NESW dealer/vulnerability.
- `evaluator._compare` now ignores missing `min`/`max` bounds when `range_contains` supplies only one side.
- same-call resolution treats multiple `P` candidates with `action_type: pass_final_contract` as structurally equivalent, choosing the highest score without an ambiguity diagnostic. This lets a generic default pass coexist with convention-specific final-pass calls.

### Convention Metadata

```yaml
id: four_way_jacoby_transfer
namespace: notrump_response
name: Four-Way Jacoby Transfer
version: 0.1.0
description: >
  Prototype after-1N transfer Convention.
author:
  name: Partner Prototype
```

### Call Specification

```yaml
call_specifications:
  - id: cs_1
    description: Responder bids 2D over 1N as a transfer to hearts with at least five hearts.
    system_notes: After 1N, 2D is artificial and transfers to hearts.
    context:
      auction_pattern: "1NP"
      seat_positions: [1, 2, 3, 4]
    call: 2D
    selection:
      applicability:
        all:
          - self.hearts:
              min: 5
      algorithm: weighted_score
      criteria:
        - criterion_id: jacoby_transfer_heart_length
          evaluator: min_value
          input: self.hearts
          min: 5
          weight: 60
    meaning:
      nature_labels: [artificial, conventional]
      call_act_types: [directive, context_initiating, forcing]
      action_type: transfer
      target_suit: H
      alertable: true
      acbl_explanation: hearts
    effects:
      - fact_type: transfer
        target_suit: H
        status: pending
```

### Bidding Plan

```yaml
bidding_plans:
  - id: plan_1
    description: Prototype plan for hands that start with a Jacoby transfer to hearts.
    owner: responder
    goal: place_contract
    context:
      auction_pattern: "1NP"
      seat_positions: [1, 2, 3, 4]
    preconditions:
      self.hearts:
        min: 5
    entry_call: 2D
    workflow:
      start: wait_1
      nodes:
        wait_1:
          kind: wait_for_call
          actor: opener
          branches:
            - when:
                kind: call_is
                value: 2H
              goto: select_1
        select_1:
          kind: select_by_policy
          policy: policy_2
```

### Named Evaluator

```yaml
named_evaluators:
  - id: eval_minor_honor_third
    evaluator_type: expression
    description: Target minor has at least three cards and at least one of A, K, or Q.
    definition:
      op: and
      args:
        - op: gte
          left:
            op: length
            hand: self
            suit: {param: target_suit}
          right: {const: 3}
        - op: gte
          left:
            op: honor_count
            hand: self
            suit: {param: target_suit}
            ranks: [A, K, Q]
          right: {const: 1}
```

Usage from a Call Specification criterion:

```yaml
selection:
  algorithm: weighted_score
  criteria:
    - criterion_id: honor_third_club_support
      evaluator: named_evaluator
      evaluator_id: eval_minor_honor_third
      params:
        target_suit: C
      weight: 100
```

## 19. Test System

### `backend/tests/test_fixture_cases.py`

Test classes:

- `FixtureBiddingTests`
- `FixtureFullAuctionTests`
- `FixtureMatcherTests`
- `FixtureHandParserTests`
- `InfrastructureTests`

Fixture files:

- `backend/tests/cases/bidding.yaml`
- `backend/tests/cases/full_auctions.yaml`
- `backend/tests/cases/hands.yaml`
- `backend/tests/cases/matcher.yaml`

Readable companion:

- `backend/tests/test_cases.md`

Run:

```text
$env:PYTHONPATH='backend'; C:\Users\paw_l\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover backend\tests
```

## 20. Current Implemented Behavior

Implemented examples include:

- compact auction parsing with `P`, `X`, `R`, `N`, suits, and arbitrary spaces,
- central basic call legality for contracts, pass, double, redouble, and completed auctions,
- illegal candidate filtering during bid selection,
- compact hand parsing,
- short suit symbols in hand feature calculations,
- seat-position expansion for initial-pass variants,
- 1N and 2N openings,
- starter one-level and two-level 2/1 opening examples,
- after-1N 2D transfer to hearts,
- opener 2H completion and 3H superaccept,
- major-transfer superaccept setting `agreed_suit` for later slam Conventions,
- executable `requires` checks against replayed semantic trace,
- typed-facing `state_has` and `state_missing` condition checks over replayed semantic facts,
- executable auction-state variables with public/private namespaces, scalar values, ranges, provenance, and query operators `auction_state_exists`, `auction_state_missing`, `auction_state_compare`, and expression `auction_state_attribute`,
- executable expression criteria for suit length, honor count, keycard count, rank containment, semantic fact attributes, partner-hand values, and arithmetic/boolean comparison,
- expression-type Named Evaluators used by selection criteria,
- dynamic semantic effects that copy values from recovered facts or auction-state values,
- same-call meaning diagnostics for cases such as multiple eligible meanings of `4N`,
- Meow 2/1 benchmark slice organized as portable Conventions for 1N, 2N, regular Stayman, Puppet Stayman stubs, four-way transfers, Texas transfers, quantitative notrump, reusable RKCB 1430, simple major raises, Bergen, Drury, Jacoby 2N, and Kokish game tries,
- full-auction partnership simulation tests with automatic opponent passes,
- explicit default pass behavior,
- public meaning and internal origin output,
- active Call Selection Policy provenance,
- explicit ordered-condition opening policy, including the Meow 2/1 benchmark preference for 15-17 balanced 1N over a five-card major,
- first force-route selection provenance after minor openings, including the case where responder uses artificial `2D` to establish a game force before later describing a long major,
- recovered and stage-advanced Protocol Frame state for transfer frames,
- recovered and branch-advanced Bidding Plan state, including entry-call candidates and plan-generated `make_call` candidates,
- private `plan_origin` provenance for plan-selected calls that use a public Call Specification,
- standalone RKCB protocol frame recovery after `4N` is replayed as RKCB,
- generated formal Markdown system notes.

## 21. Current Limitations

Known limitations:

1. Basic bridge auction legality is implemented. Full law-level validation, insufficient-bid handling, alerts, claims, and tournament-procedure details are not implemented.
2. Basic double/redouble legality is implemented. Advanced competitive obligations and conventional double meanings are not centralized yet.
3. Relative roles such as opener, responder, overcaller, advancer, captain, and describer are not centrally derived.
4. Vulnerability relation, scoring style, and seat number are only partially represented.
5. Pattern matching is exact except for seat-position expansion and default `*`.
6. Evaluation supports only the current small expression subset.
7. Call Selection Policies currently support score selection and simple ordered-condition choices; full decision trees, decision tables, comparators, and random-source policies are not implemented.
8. Bidding Plans have a first executable path for entry-call candidates, `wait_for_call` branches, and `make_call` candidates. They do not yet compare plans through a full plan policy, execute `select_by_policy`, derive actor roles, or generate full continuation trees.
9. Protocol Frames have first stage advancement for transfer completion and final placement, and RKCB can open a keycard frame after `4N`. Frames do not yet execute arbitrary stage rules, obligations, interference policies, or nested-frame resolution.
10. Relay Automata are loaded but not executable.
11. `SemanticFact` and `AuctionStateVariable` are both still permissive. They should evolve into ontology-backed state objects with validation, merge rules, and conflict diagnostics.
12. Automated ACBL alert analysis is not implemented; `meaning.alertable` is currently explicit data.
13. System notes generation is formal Markdown from IR; import from natural-language notes is future work.
14. Full-auction simulation is limited to supplied partnership hands and automatic opponent passes.
15. Named Evaluators execute only when `evaluator_type: expression`.
16. Semantic-context matching has a first executable implementation through `auction_pattern: "*"`, `requires.fact_exists`, `state_has`, `fact_attribute`, `auction_state_exists`, `auction_state_compare`, and dynamic effects. It still lacks full typed semantic-state validation and a complete conflict resolver for cases where several Conventions give the same call different valid meanings.

## 22. Maintenance Policy

When code changes structure, schema, output, runtime behavior, or limitations, update this document in the same checkpoint. Do not change the platform version unless the user explicitly asks to make or release a new version.
