# Engine Architecture

Platform Version: 0.0.7
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

This is the code-reading guide for engineers and AI agents.

## Runtime Flow

The bidding flow is:

1. `app.bid()` receives a request.
2. `loader.load_profile()` loads the Partnership Profile and its Gadgets.
3. `Auction.parse()` and `Hand.parse()` normalize inputs.
4. `selector.choose_bid()` replays the prior auction.
5. `replay.replay_auction()` applies prior Call Specification meanings and effects.
6. `candidate_generation.generate_candidates()` gathers eligible Call Specification and Private Route candidates.
7. `decision.choose_candidate()` resolves same-call ambiguity, builds `BridgeContext`, and runs Python Policy Functions.
8. `explanation.explain()` returns public meaning and internal origin.

## Backend Files

`backend/app.py`

- Public backend entry points:
  - `bid(request)`
  - `simulate(request)`
  - `system_notes(request)`

`backend/engine/auction.py`

- `Auction` dataclass.
- Parses compact auction strings.
- Tracks dealer, vulnerability, calls, actor to call, and canonical key.

`backend/engine/cards.py`

- `Hand` dataclass.
- Parses compact hand strings.
- Exposes HCP, lengths, holdings, balancedness, honor count, ace/king/keycard helpers.

`backend/engine/calls.py`

- Normalizes calls and auction patterns.
- Enforces `N`, `C`, `D`, `H`, `S`, `P`, `X`, `R` notation.

`backend/engine/model.py`

- Runtime object model:
  - `Author`
  - `SourceInfo`
  - `Gadget`
  - `PartnershipProfile`
  - `CallSpec`
  - `FrameSpec`
  - `PrivateRouteSpec`
  - `PolicyFunction`
  - `EvaluatorSpec`
  - `RelaySpec`
- `RoutePolicy` is no longer part of the current runtime.

`backend/engine/bsl.py`

- Restricted Python-shaped BSL compiler.
- Uses `ast` parsing and a constructor whitelist.
- Compiles source objects into dictionaries consumed by `model.py`.

`backend/engine/loader.py`

- Loads `profile.bsl.py`.
- Loads each Gadget directory.
- Loads `*.policy.py` files as restricted Policy Functions.
- Loads profile-level Named Evaluators from profile BSL files.

`backend/engine/policy_runtime.py`

- Validates and executes restricted `*.policy.py` files.
- Expects policy functions with signature `(ctx, candidates)`.
- Exposes a limited safe builtin set.

`backend/engine/replay.py`

- Replays prior calls from the visible auction.
- Applies effects.
- Recovers public state, Frames, and Private Routes.
- Builds active environment fields such as actor seat, dealer, vulnerability, seat position, and vulnerability relation.

`backend/engine/effects.py`

- Materializes Call Specification effects.
- Writes `StateRecord` objects into the trace.

`backend/engine/frame_runtime.py`

- Opens, advances, and closes Frames.
- Current executable frames include transfer and keycard-style contexts.

`backend/engine/private_route_runtime.py`

- Recovers and advances Private Route states during replay.
- Current route nodes support entry, wait-for-call, make-call, end, and fail behavior.

`backend/engine/candidate_generation.py`

- Generates eligible candidates from Call Specifications.
- Generates entry and continuation candidates from active Private Routes.
- Applies legality filtering.
- Handles relative-call templates through `call_space.py`.

`backend/engine/decision.py`

- Resolves same-call meaning ambiguity.
- Builds `BridgeContext`.
- Runs Python Policy Functions.
- Falls back to candidate score only when no policy function selects a candidate.

`backend/engine/context.py`

- `StateView`: queryable view over public state records, active Frames, and active Private Routes.
- `BridgeContext`: read-only decision context for policy functions.
- `CallCandidate`: candidate call with public meaning, origin, score, capabilities, and Private Route origin.
- `CandidatePool`: helpers such as `get()`, `first_available()`, `by_action_type()`, `by_target_suit()`, `by_capability()`, and `features()`.

`backend/engine/evaluator.py`

- Evaluates selection criteria, structured expressions, state queries, named evaluators, and partner-hand expressions during simulation.

`backend/engine/legality.py`

- Basic legal-call filtering.
- Handles contract order, pass, double, and redouble legality.

`backend/engine/matcher.py`

- Matches Call Specification context against current auction.
- Supports seat-position context.

`backend/engine/memory.py`

- `SeatMemory` records same-seat selected Private Routes.
- This allows one seat to continue its own route later in the same deal.

`backend/engine/trace.py`

- `AuctionTrace` stores state records, applied meanings, frame states, private route states, and diagnostics.

`backend/engine/simulator.py`

- Simulates an auction for supplied partnership hands while uncontrolled seats pass.
- Maintains separate private memory per controlled seat.

`backend/engine/system_notes.py`

- Generates Markdown system notes from loaded runtime objects.

## Public State And Private Memory

Public state is recovered by replaying the visible auction. It includes records such as:

- `notrump_focus`
- `transfer`
- `agreed_suit`
- `keycard_context`
- `opener.hcp`
- `opener.length.S`

Private memory belongs to one controlled seat. If responder chose a `2D` transfer as a weak signoff route, responder can later remember that private route. Opener cannot read responder's private reason.

## Selection Model

The current selection model is deliberately simple:

1. Call Specifications create eligible candidates.
2. Private Routes may add route-aware candidates.
3. Same-call ambiguity is diagnosed unless one route candidate clearly implements the same public call.
4. Policy Functions choose from the candidate pool.
5. Score fallback is used only when no policy function applies.

This avoids hidden priority fields. Judgment belongs in Policy Functions, not inside one candidate.
