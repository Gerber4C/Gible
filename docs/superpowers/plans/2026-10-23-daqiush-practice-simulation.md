# Daqiush Practice and Simulation Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let confirmed Daqiush 1NT auctions preserve the correct trump reference and provide reviewable contract analysis over sampled deals. Later, simulation may help choose the initial Texas/Jacoby response route, while a Texas route's private game-only versus keycard-dependent slam intent governs its subsequent Pass or 4NT.

**Architecture:** Keep partnership-visible trump state separate from the eventual contract. Replay derives state only from authored public meanings; the bidder sees its own hand plus public auction evidence. A bounded evaluator samples unknown hands, asks a replaceable DDS adapter whether each separately declared contract succeeds, and reports estimates; it never invents a conventional meaning. Missing branches remain blocked until a declared continuation or evaluator exists.

**Tech Stack:** Python backend/BSL, unittest, React frontend, official `dds-bridge/dds` Python or C API behind a narrow adapter.

---

## Chunk 1: Trump-state foundation and confirmed prefixes

### Task 1: Three-state public semantics

**Files:** `backend/engine/trump_state.py` (new), `backend/engine/replay.py`, `backend/engine/trace.py`, `backend/engine/bsl.py`, `backend/tests/test_trump_state.py` (new).

- [ ] Write failing tests: unset/provisional/agreed for **each partnership side**; partner's next call promotes provisional unless its authored transition maintains or replaces it; an intervening enemy call does not consume the pending transition; enemy-call then partner Pass promotes; an explicit replacing 4NT is interpreted before generic agreed-trump 4NT. Existing `agreed_suit` consumers must see only their side's final agreement, never a stale superseded state or an opponent's agreement.
- [ ] Add replay-invariance tests: changing the current deciding hand cannot alter any earlier seat's public meanings/state when the visible auction is unchanged. Distinguish public historical meaning recognition from private hand-based candidate eligibility; do not evaluate historical conditions/effects against the wrong seat's hand.
- [ ] Test same-call overlaps in replay and selection. Explicit convention overrides must win by declared context/priority; unresolved overlap blocks with an ambiguity diagnostic instead of taking the first loaded gadget.
- [ ] Run the targeted tests and confirm expected failures.
- [ ] Implement a small transition function and invoke it during public replay without reading hidden cards. Preserve event history but expose a canonical current state per side; do not infer trump from bid appearance.
- [ ] Run targeted and existing axiom/replay tests.

### Task 2: Daqiush confirmed agreement effects

**Files:** `backend/partnership_profiles/daqiush_2over1/gadgets/` (new focused gadget as needed), `backend/partnership_profiles/daqiush_2over1/profile.bsl.py`, `backend/tests/test_daqiush_trump.py` (new).

- [ ] Write historical-prefix tests for Texas direct major agreement, the six Jacoby splinters, `1NT–2C–2D–4C–4D–4S` agreeing clubs, `…–4D–4H–4S` agreeing diamonds, and `1NT–2D–2H–3D–3S` agreeing diamonds while subsequent responder `4H` remains natural and opener `4NT` asks diamond keycards.
- [ ] Run tests red, then add only confirmed public meanings and state effects. Do not automatically initiate an underspecified Stayman/Jacoby route or guess other minor-Stayman answers.
- [ ] Verify historical replay, current Texas/splinter tests, and that unrelated profiles retain behavior.

## Chunk 2: Confirmed uncontested keycard prefix

### Task 3: Basic RKCB 1430 inquiry and answers

**Files:** focused Daqiush gadget(s), `backend/tests/test_daqiush_keycard.py` (new), relevant profile docs.

- [ ] Write tests for **explicitly scoped** 4NT asking keycards with the agreed trump and four ordinary response steps (`5C=1/4`, `5D=0/3`, `5H=2 without Q`, `5S=2 with Q`). Test that direct/quantitative/nonforcing 4NT contexts retain their own meanings and that unresolved overlaps block rather than silently becoming RKCB.
- [ ] Run tests red. Implement no-interference branches first, with accurate asker/responder roles, legal calls, and state effects. Leave void answers, unspecified follow-ups and final Pass blocked.
- [ ] Run targeted tests and full Daqiush tests. Demonstrate the confirmed RKCB inquiry/answer prefixes without claiming a complete auction before the owner defines a legal signoff continuation.

## Chunk 3: Bounded sampled-deal baseline

### Task 4: Information-safe sampling

**Files:** `backend/engine/deal_sampler.py` (new), `backend/tests/test_deal_sampler.py` (new).

- [ ] Write tests for 52 unique cards, preservation of the acting hand, reproducible seed, permitted public evidence only, impossible constraints, and bounded attempts/time. Encode each supported call's publicly promised shape/strength as machine-readable evidence (for example Texas major length and opener reply constraints), rather than attempting to reverse-engineer private `applies` or using actual hidden hands. Verify every sampled hand satisfies the published constraints.
- [ ] Run red, implement the minimal sampler, and run tests green. Keep complete deal objects inside the evaluation boundary; never add `partner_hand` to ordinary bidding context.

### Task 5: DDS adapter and analysis-only contract-success comparison

**Files:** `backend/engine/dds_adapter.py` (new), `backend/engine/contract_evaluation.py` (new), `backend/tests/test_contract_evaluation.py` (new), dependency/setup docs.

- [ ] Inspect the official DDS repository/API and pin an explicit compatible version. Test solver discovery and a known full deal; unavailable solver must produce a clear diagnostic.
- [ ] Write contract-completion tests that evaluate each level/strain/declarer target separately from the solver's table, return made/failed frequencies and sample counts, and do not pass sampled hidden cards to the live bidder.
- [ ] Run red, implement behind a replaceable adapter, then run green with a real DDS smoke test where supported. Bound runtime; report timeout and contradictions explicitly.
- [ ] Expose contract-comparison as an analysis service first. The caller supplies explicit level/strain/declarer target contracts for analysis; validate each target, its declarer/partnership consistency and legality, and label it **analysis only**, not an authored call candidate. Do **not** turn `1NT–4C–4H` into a fresh binary simulation choice between 4H and 6H. The South African Texas route was selected earlier for either game-only or slam-if-keycards intent; preserve that private route and follow it with Pass or 4NT. Comparing Texas against Jacoby belongs to the earlier responder decision and must account for intermediate/exploratory outcomes, keycard information, and the owner's full route definitions. Until then, keep unsupported automatic choices blocked.

## Chunk 4: Table review and release verification

### Task 6: Explain contract analysis in Table

**Files:** `backend/app.py`, `backend/server.py`, `frontend/src/api/partnerApi.js`, `frontend/src/components/BridgeTools.js`, focused browser tests.

- [ ] Write tests for API estimates and UI states: loading, explicitly supplied **analysis targets** (not bidding candidates), each completion rate/sample count, timeout/unavailable/blocked, and hidden cards remaining hidden. Test **information invariance**: changing table-known concealed partner/opponent cards while acting hand, public auction and seed stay fixed cannot change the evaluation request or result. The endpoint accepts only the acting seat/hand, auction, vulnerability, seed and explicit analysis targets; it derives public meanings by server-side replay of the selected profile and must ignore table-known hidden hands or client-supplied meaning objects.
- [ ] Run red, add a bounded evaluation endpoint and a compact review panel, then run targeted backend/browser tests green.
- [ ] Re-run the supported Daqiush auction fixture, backend suite, frontend build, browser flow, and `git diff --check`; document any known pre-existing Meow failures separately.

**Current semantic limits:** Automatic Stayman/Jacoby initiation, superaccepts and complex void-keycard answers remain governed by the owner-supplied meanings in `docs/13_daqiush_2over1.md` and `docs/15_daqiush_slam.md`. After `1NT–4C–4H`, Pass and 4NT are confirmed calls but their choice follows the earlier Texas intent; the terminal action after each keycard answer still needs definition. Implement historical prefixes and complete only paths with explicit meanings. Do not substitute a lowest-legal-suit bid for the agreed final placement.
