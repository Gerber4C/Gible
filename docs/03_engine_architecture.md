# Engine Architecture

Platform Version: 0.0.8
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

This is the backend code-reading guide for engineers and AI agents. Frontend implementation details live in `docs/07_frontend_architecture.md`.

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

`backend/server.py`

- Localhost HTTP wrapper around `app.py`.
- Lists Partnership Profiles and profile files.
- Reads and writes editable profile files inside the selected profile directory.
- Exposes bid, simulation, and generated system-note endpoints for the browser workspace.

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

`backend/engine/bsl.py`

- Restricted Python-shaped BSL loader.
- Rejects unsupported top-level syntax such as imports.
- Executes source in a constrained namespace of authoring base classes and bridge helpers.
- Expands source-level dialogue helpers, currently `self.puppet_stayman(...)`, into normal Call Specifications and state effects before runtime loading.
- Collects class-authored `Profile` and `Gadget` objects, then materializes builders into runtime-object data.

`backend/engine/loader.py`

- Loads `profile.bsl.py` from `backend/partnership_profiles/<profile_id>/`.
- Loads profile-local Gadget directories from `backend/partnership_profiles/<profile_id>/gadgets/`.
- Loads profile-level `*.policy.py` files from the profile root and `policies/`.
- Loads profile-level Named Evaluators from profile BSL files.

`backend/engine/policy_runtime.py`

- Validates and executes restricted `*.policy.py` files.
- Expects policy functions with signature `(ctx, candidates)`.
- Reads the registered `policy_functions = [...]` list.
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

`backend/engine/axioms.py`

Mandatory constraints run in `axioms.py` before Policy and again on its result.
`axiom_facts.py` extracts seat-scoped public evidence; `axiom_validation.py`
checks authored definitions; `hand_quality.py` implements Kaplan–Rubens.
The selector applies the same constraints to fallback candidates. An empty
compliant pool produces a blocked decision with no call; the simulator keeps
the preceding history and returns the structured failure. See `11_axioms.md`.

`backend/engine/zar.py`

- Independent base Zar evaluator and conservative fit-adjustment service, kept
  next to the hand-quality implementation for reuse without coupling it to the
  bidding runtime.
- It is not registered with BSL, profiles, axioms, scanners, or bidding
  selection, and no existing decision path consumes its result.

`backend/engine/decision.py`

- Resolves same-call meaning ambiguity.
- Builds `BridgeContext`.
- Runs Python Policy Functions.
- Falls back only when no policy function selects a candidate.

`backend/engine/context.py`

- `StateView`: queryable view over public state records, active Frames, and active Private Routes.
- `PartnershipKnowledge`, `HandKnowledge`, `SuitKnowledge`, and `FitKnowledge`: typed convenience views over replayed range evidence, such as `ctx.knowledge.opener.S.length` and `ctx.knowledge.fit("S").min_total`.
- `BridgeContext`: read-only decision context for policy functions.
- `CallCandidate`: candidate call with public meaning, origin, score, capabilities, and Private Route origin.
- `CandidatePool`: helpers such as `get()`, `first_available()`, `by_action_type()`, `by_target_suit()`, `by_capability()`, and `features()`.

`backend/engine/evaluator.py`

- Evaluates structured expressions still used by relative helpers and dynamic state materialization.
- Named Evaluators in current BSL source are Python functions, not dictionary scoring records.

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

## Source Layout

Executable bridge agreement source is profile-owned:

```text
backend/partnership_profiles/meow_2over1/
  profile.bsl.py
  gadgets/
  policies/
  tests/
```

Engine code remains shared:

```text
backend/engine/
```

Test-only profiles live separately:

```text
backend/test_profiles/
```

The React browser workspace lives in:

```text
frontend/
```

See `docs/07_frontend_architecture.md` for frontend module ownership, UI state, editor behavior, and browser verification.

## Public State And Private Memory

Public state is recovered by replaying the visible auction. It includes records such as:

- `notrump_focus`
- `transfer`
- `agreed_suit`
- length evidence such as `opener.length.S`
- fit evidence such as `partnership.fit.S` with `opener_min_length`, `responder_min_length`, `min_total`, and `pattern_floor`
- `keycard_context`
- `opener.hcp`
- `opener.length.S`

Policy functions may read the raw records with `ctx.state`, but bridge judgment should prefer the knowledge view when the question is about inferred hand information:

```python
ctx.knowledge.opener.S.length
ctx.knowledge.responder.H.length
ctx.knowledge.fit("S").min_total
ctx.knowledge.opener.hcp
```

This keeps a 4-4 fit, 5-3 fit, 5-4 fit, and 4-3 fit distinct instead of collapsing them into a generic agreement flag.

Private memory belongs to one controlled seat. If responder chose a `2D` transfer as a weak signoff route, responder can later remember that private route. Opener cannot read responder's private reason.

## Selection Model

The current selection model is deliberately simple:

1. Call Specifications create eligible candidates.
2. Private Routes may add route-aware candidates.
3. Same-call ambiguity is diagnosed unless one route candidate clearly implements the same public call.
4. Policy Functions choose from the candidate pool.
5. If candidates exist but no Policy Function selects one, the existing score ordering is used.
6. If no eligible candidates exist, use the profile's default candidate. Before a default Pass, try the cheapest legal bid in the latest public `agreed_suit`.

The agreed-trump fallback does not raise a contract already held by our side
in that denomination, including a doubled contract. If no suit is agreed,
the auction is complete, or no legal return exists, retain the original
fallback. Explicit candidates and non-Pass profile defaults take precedence.
This is a minimum-contract heuristic, not a strength or trick evaluator.

Its source is `heuristic_fallback`, its meaning action is
`fallback_return_to_agreed_trump`, and its metadata includes the agreement
evidence. Missing-rule diagnostics are retained. Replaying a heuristic bid
may still report an undefined prior call because it is not a new authored
Call Specification; this keeps profile coverage gaps visible.

Authored bidding judgment belongs in Policy Functions. The engine heuristic
only supplies this limited recovery when authored candidates are absent.

## Simulation Scope

`public_evidence.py` replays only authored public meanings, then binds their
declared evidence to the seat that made each call. `deal_sampler.py` keeps the
acting hand fixed and rejects hypothetical full deals that contradict those
promises. `dds_adapter.py` converts each accepted deal to PBN for official
`dds3` or the optional endplay DDS wheel; `contract_evaluation.py` counts each
explicit target's make/fail result separately. `/api/analysis/contracts` returns
only counts, rates, seed, and public evidence labels. It rejects concealed
hands and caller-supplied meaning objects. This path is analysis-only and does
not feed a candidate to the bidding selector.

`simulate_auction` plays supplied hands through the bidding engine, passing
for seats without supplied hands. The runner retains the hands and supplies only
the acting seat's hand to each decision. It does not inject `partner_hand`.
Normal bidding and replay also remove that key from caller-supplied environments
before conditions, effects, evaluators, and policies run. Public environment
settings and public partner evidence in state/knowledge remain available.

Legacy expressions `partner.hcp`, `partner.<suit>.length`, and operations with
`hand: partner` raise an explicit hidden-hand error. They must be replaced with
inference from public auction evidence, not given a fabricated zero or empty hand.
This is not inference or sampling, and is not a sandbox against arbitrary authored
Python code or other caller-provided custom data. A comprehensive permitted-view
interface remains future work.

The Table's random-deal generator shuffles all 52 cards without auction
constraints. There is currently no sampler that generates possible partner
hands consistent with public bidding evidence, and no Monte Carlo contract
evaluation or double-dummy solver integration.

### Direction after the 2026-10-22 product update

The identified `partner_hand` path has been removed from normal bidding. No
separate oracle mode has been added. The broader seat-information boundary still
needs explicit interfaces before multi-user practice or statistical simulation.

Future responsibilities include permitted seat views, per-partnership profile
bindings, public explanations for mixed-profile replay, evidence-constrained deal
sampling, bounded continuation evaluation, and a replaceable contract evaluator
(initially DDS, later contract-specific completion probabilities). Private memory remains seat-owned;
full deals remain with the table/evaluation controller. See
[Product Vision](12_product_vision.md) for the proposed boundaries and
[Roadmap](08_roadmap_todo.md) for milestones. The local and cloud execution
locations should share decision interfaces without making profile upload a
prerequisite for all use.
