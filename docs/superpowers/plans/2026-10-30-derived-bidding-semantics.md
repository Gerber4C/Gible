# Derived Bidding Semantics Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an explainable, profile-respecting derivation layer for undefined 4NT, trump selection/control bidding, NFRKCB, three-level fits, natural 6NT placement, and terminal Pass.

**Architecture:** Build one immutable public-evidence object, then run small independent inference families after explicit profile candidate generation and before fallback/TD. Derived candidates carry their rule/evidence/conflicts in metadata; deterministic meaning classification precedes any simulation, and ambiguity returns structured TD rather than a guessed bridge call.

**Tech Stack:** Python 3, existing replay/trump/frame/candidate systems, Python-BSL profile metadata, `unittest`, existing sampling/DDS evaluation.

**Approved specification:** `docs/superpowers/specs/2026-10-30-derived-bidding-semantics-design.md`

**Execution boundary:** Do not execute this plan in the ordinary-RKCB cycle. It is a future implementation plan only.

---

## File map

- Create `backend/engine/derived_evidence.py`: immutable evidence extraction and call classification.
- Create `backend/engine/derived_semantics.py`: inference dispatcher and structured TD result.
- Create `backend/engine/derived_replay.py`: hand-free reconstruction of a historical derived meaning and its public effects from the same evidence/rule functions.
- Create `backend/engine/derived_four_notrump.py`: 4NT/trump selector mappings and NFRKCB offer creation.
- Create `backend/engine/derived_fit_calls.py`: symmetric three-level major/minor fit classification.
- Create `backend/engine/nfrkcb_policy.py`: single-suit offer decision and method state.
- Modify `backend/engine/candidate_generation.py`: insert derived candidates only for otherwise undefined calls after explicit generation.
- Modify `backend/engine/selector.py`: run derivation before fallback/TD and route simulation-only decisions after meaning classification.
- Modify `backend/engine/replay.py`: when no authored definition owns a historical call, invoke `derived_replay` and apply exactly one reconstructed meaning/effect set.
- Modify `backend/engine/trump_state.py`: apply derived selector/agreement transitions.
- Modify `backend/engine/trace.py`: expose structured derivation evidence and TD conflicts.
- Modify `backend/engine/hand_quality.py`: add the shared `has_good_five_card_suit` K-R predicate used by 6NT derivation.
- Create `backend/tests/test_derived_evidence.py`, `test_derived_four_notrump.py`, `test_derived_fit_calls.py`, `test_nfrkcb_policy.py`.
- Modify `docs/15_daqiush_slam.md` and create `docs/19_derived_semantics.md`.

## Chunk 1: Evidence and priority

### Task 1: Build immutable public evidence

**Files:**
- Create: `backend/engine/derived_evidence.py`
- Create: `backend/tests/test_derived_evidence.py`

- [ ] Write table-driven failing tests for natural suits, 4+ guaranteed long suits, enemy suits, unset/provisional/agreed trump, 0/1/2/3 plausible trumps, legal calls below 4NT, raises, enemy cues, selectors, unresolved calls, and 3NT availability.
- [ ] Run `$env:PYTHONPATH='backend'; python -m unittest tests.test_derived_evidence -v`; expect import failure for `engine.derived_evidence`.
- [ ] Implement frozen `DerivedEvidence` and `ClassifiedCall` dataclasses plus `collect_evidence(profile, auction, trace)`; use replay meaning/state, never private cards.
- [ ] Make classification semantic: preserve explicit natural meaning; classify a non-natural own/non-enemy suit as selector only when natural is impossible.
- [ ] Return a structured conflict when plausible trumps exceed two.
- [ ] Rerun `$env:PYTHONPATH='backend'; python -m unittest tests.test_derived_evidence -v`; expect every evidence table case to pass.
- [ ] Commit only evidence files with `git commit -m "feat: collect derived bidding evidence"`.

### Task 2: Add a priority-safe derivation dispatcher

**Files:**
- Create: `backend/engine/derived_semantics.py`
- Create: `backend/engine/derived_replay.py`
- Modify: `backend/engine/candidate_generation.py`
- Modify: `backend/engine/selector.py`
- Modify: `backend/engine/replay.py`
- Create: `backend/tests/test_derived_semantics.py`

- [ ] Write failing selector tests proving priority: explicit profile meaning > committed private purpose > derived meaning > fallback > TD. Assert an active unresolved Purpose TDs before derivation rather than silently escaping through a derived call.
- [ ] Add a fixture where the same call has an authored definition for the public context but its private applicability is false; assert the call remains reserved and no second derived meaning is created.
- [ ] Add hand-free replay tests: select a derived call, append it to the auction, call `replay_auction(profile, Auction((*prefix.calls, selected.call)), hand=None)`, and assert its meaning/effects are reconstructed once without rerunning private selection.
- [ ] Run `$env:PYTHONPATH='backend'; python -m unittest tests.test_derived_semantics -v`; expect the priority/reservation/replay tests to fail because no dispatcher exists.
- [ ] Extend candidate generation to return both eligible explicit candidates and `reserved_calls`: every call whose authored definition matches public context/requires is reserved even when private `applicability` rejects the current hand.
- [ ] Implement `derive_candidates(profile, auction, trace, evidence, reserved_calls) -> DerivationResult` only for legal calls absent from `reserved_calls`.
- [ ] Implement the selector order exactly: generate explicit eligible candidates/reservations; resolve an active Purpose against explicit candidates and TD if unresolved; derive unreserved calls only when no Purpose controls the turn; combine explicit and derived candidates; then run ordinary policy/axiom selection.
- [ ] Attach `derived_rule`, public evidence, plausible trumps, competing interpretations, and confidence to every derived candidate's metadata.
- [ ] Implement `derive_historical_call(profile, prior_auction, call, trace)`: use only public evidence and the actual historical call, return one meaning/effect set or a structured replay conflict. In `replay.py`, invoke it only when no authored definition reserves the call; apply its effects through the existing effect machinery and add one applied meaning.
- [ ] Produce no candidate/meaning when a rule is ambiguous; return a structured conflict consumed by selector/replay diagnostics.
- [ ] Rerun `$env:PYTHONPATH='backend'; python -m unittest tests.test_derived_semantics -v`; expect priority, reservation, and hand-free replay tests to pass.
- [ ] Commit only named files with `git add backend/engine/derived_semantics.py backend/engine/derived_replay.py backend/engine/candidate_generation.py backend/engine/selector.py backend/engine/replay.py backend/tests/test_derived_semantics.py; git commit -m "feat: add derived meaning dispatcher"`.

## Chunk 2: 4NT and NFRKCB

### Task 3: Implement the complete derived-4NT mapping

**Files:**
- Create: `backend/engine/derived_four_notrump.py`
- Create: `backend/tests/test_derived_four_notrump.py`
- Modify: `backend/engine/trump_state.py`

- [ ] Write one failing case for every specification branch: agreed trump; ordinary three-level quantitative; exceptional sole-trump three-level ask; all four-level raise/selector count cases; sole candidate; mismatched counts; three candidates.
- [ ] Assert selectors use `trump_selector`, never `control_showing`, and that selecting a suit produces provisional/agreed trump state as specified.
- [ ] Add hand-free replay cases for quantitative 4NT, trump-setting/keycard 4NT, and every selector case; assert reconstructed trump state and method on the next turn.
- [ ] Run `$env:PYTHONPATH='backend'; python -m unittest tests.test_derived_four_notrump -v`; expect all derived/replay cases to fail before implementation.
- [ ] Implement pinned raises first, then ascending selector-to-candidate pairing; never infer a keycard ask merely because it is convenient.
- [ ] Make 4NT quantitative/nonforcing when all candidates are already covered below it; do not manufacture the call when no plausible hand meaning exists.
- [ ] Emit structured TD conflicts for non-unique mappings.
- [ ] Rerun `$env:PYTHONPATH='backend'; python -m unittest tests.test_derived_four_notrump -v`; expect every mapping and hand-free replay case to pass.
- [ ] Commit the exact files with `git add backend/engine/derived_four_notrump.py backend/engine/trump_state.py backend/tests/test_derived_four_notrump.py; git commit -m "feat: derive four notrump meanings"`.

### Task 4: Implement single-suit NFRKCB without contaminating two-suit auctions

**Files:**
- Create: `backend/engine/nfrkcb_policy.py`
- Create: `backend/tests/test_nfrkcb_policy.py`
- Modify: `backend/engine/derived_four_notrump.py`
- Modify: `backend/engine/selector.py`

- [ ] Write canonical failing tests for `1NT-2C-2D-3C-3NT-4C-4NT` (single-suit offer) and `1NT-2H-2S-3C-3NT-4C-4NT` (two-suit natural 5C).
- [ ] Test Pass acceptance, actual 1430 answer rejection, transition `nfrkcb_offer -> nfrkcb_answered`, and no simultaneous Pass/answer without a decision rule.
- [ ] Add hand-free replay assertions for `nfrkcb_offer`, accepting Pass completion, `nfrkcb_answered`, and the two-suit natural 5C. The single/two-suit distinction must come entirely from prior public natural-suit evidence.
- [ ] Add an injected sample with identical deals for both choices: fake scoring gives 4NT the higher expected score, so the expected call is Pass. Add the reverse fixture where the best legal six-trump route has higher expected score, so the expected call is the hand's actual 1430 answer. On an exact EV tie, expect Pass.
- [ ] Run `$env:PYTHONPATH='backend'; python -m unittest tests.test_nfrkcb_policy -v`; expect policy/replay fixtures to fail before implementation.
- [ ] Implement deterministic gates exactly: Pass without DDS when optimistic public strength cannot support a small slam or ordinary keycard restrictions prohibit asking; continue without DDS only when the responder itself holds all five keycards and the trump queen. All other non-sampled cases return typed `sampling_unavailable` and TD.
- [ ] Sample partner hands consistent with the single-suit provisional auction and compare playing 4NT with every legal small-slam route using the project's duplicate-score/IMP expected-score evaluator; choose a 1430 answer only when the best slam route is strictly higher EV, otherwise Pass.
- [ ] After continuing is selected, map the responder's actual hand to ordinary 1430. Never offer an answer candidate in the two-suit context.
- [ ] Prove ordinary RKCB, NFRKCB, Voidwood, and quantitative 4NT remain distinct methods.
- [ ] Rerun `$env:PYTHONPATH='backend'; python -m unittest tests.test_nfrkcb_policy tests.test_derived_four_notrump -v`; expect all deterministic/sampled/replay/method-isolation cases to pass.
- [ ] Commit exact files with `git add backend/engine/nfrkcb_policy.py backend/engine/derived_four_notrump.py backend/engine/selector.py backend/tests/test_nfrkcb_policy.py backend/tests/test_derived_four_notrump.py; git commit -m "feat: derive single suit nfrkcb"`.

## Chunk 3: Three-level fits and natural terminals

### Task 5: Derive symmetric three-level major-fit continuations

**Files:**
- Create: `backend/engine/derived_fit_calls.py`
- Modify: `backend/engine/selector.py`
- Create: `backend/tests/test_derived_fit_calls.py`

- [ ] Write mirrored heart/spade test tables for explicit conventional priority, serious/non-serious relay, unique-critical-control protection, genuine cue calls, game, continued cueing, and keycard entry.
- [ ] Run `$env:PYTHONPATH='backend'; python -m unittest tests.test_derived_fit_calls -v`; expect classification, selection, and replay cases to fail before implementation.
- [ ] Implement classification first and route selection second; simulation may choose among classified routes but may not define a call's meaning.
- [ ] In `selector.py`, add a post-classification filter that receives only the already-derived major-fit candidates plus their unchanged meanings; deterministic gates filter first, then existing sampling/DDS compares their resulting contracts and returns one of those candidate identities.
- [ ] Verify the hearts space-saving `3S` case preserves `3NT` as a spade control when the profile says so.
- [ ] Test no one-suit literal prefix is embedded in the algorithm.
- [ ] Add hand-free replay tests for a serious relay and both heart/spade control cues, including the resulting agreed-trump/control state.
- [ ] Rerun `$env:PYTHONPATH='backend'; python -m unittest tests.test_derived_fit_calls -v`; expect all mirrored selection and replay cases to pass.
- [ ] Commit exact files with `git add backend/engine/derived_fit_calls.py backend/engine/selector.py backend/tests/test_derived_fit_calls.py; git commit -m "feat: derive three level major fits"`.

### Task 6: Derive minor stopper inquiries and crossing-3NT decisions

**Files:**
- Modify: `backend/engine/derived_fit_calls.py`
- Modify: `backend/engine/selector.py`
- Modify: `backend/tests/test_derived_fit_calls.py`

- [ ] Write failing cases for natural new suit, sole unshown/unstopped-suit inquiry while 3NT is live, control cue after slam interest, and unresolved ambiguity.
- [ ] Run `$env:PYTHONPATH='backend'; python -m unittest tests.test_derived_fit_calls -v`; expect new minor-fit cases to fail.
- [ ] Implement the exact precedence in the specification; keep 3NT space before labeling a cue.
- [ ] Add injected-solver tests proving selector simulation receives only already-classified 3NT/minor candidates, compares their final contracts whenever a route crosses 3NT, and returns the original candidate unchanged.
- [ ] Assert missing simulation plus no deterministic rule returns structured TD.
- [ ] Add hand-free replay cases for a stopper inquiry and a minor control cue; assert distinct reconstructed meanings/effects.
- [ ] Rerun `$env:PYTHONPATH='backend'; python -m unittest tests.test_derived_fit_calls -v`; expect all major/minor classification, selection, and replay cases to pass.
- [ ] Commit exact files with `git add backend/engine/derived_fit_calls.py backend/engine/selector.py backend/tests/test_derived_fit_calls.py; git commit -m "feat: derive minor fit contract choices"`.

### Task 7: Derive 6NT placement and terminal Pass

**Files:**
- Modify: `backend/engine/derived_semantics.py`
- Modify: `backend/engine/hand_quality.py`
- Create or modify: `backend/tests/test_derived_semantics.py`
- Modify: `backend/tests/test_hand_quality.py`

- [ ] Write failing hand-quality tests for `has_good_five_card_suit(hand)`: it returns true when at least one 5+ suit's K-R suit points exceed that suit's raw HCP by at least 0.5, and false otherwise. Keep this definition in `hand_quality.py`, not the inference engine.
- [ ] Write failing 6NT matrix tests: 32 qualifies only with `has_good_five_card_suit`; every total 33, 34, and 35 qualifies without it; 32 without it and 36 never derive 6NT; every qualifying case also requires no known fit.
- [ ] Write failing Pass tests that first require the immediately preceding call to be partner's. Cover ordinary willingness after partner, a negative case after an opponent call, and suppression by forcing/game force, committed purpose, unresolved inquiry, pending trump selection, NFRKCB response, and explicit forcing Pass.
- [ ] Run `$env:PYTHONPATH='backend'; python -m unittest tests.test_hand_quality tests.test_derived_semantics -v`; expect good-five, 6NT, Pass, and replay cases to fail.
- [ ] Implement `has_good_five_card_suit` from existing `_kr_suit` evidence, export it from `hand_quality.py`, and call that shared function from derivation.
- [ ] Implement derived natural 6NT placement and natural final-placement Pass with public explanations.
- [ ] Add hand-free replay coverage for 6NT placement and derived Pass, including final-placement effects and suppression of derived Pass where an obligation remains.
- [ ] Rerun `$env:PYTHONPATH='backend'; python -m unittest tests.test_hand_quality tests.test_derived_semantics -v`; expect all matrix, Pass, and replay cases to pass.
- [ ] Commit exact files with `git add backend/engine/hand_quality.py backend/engine/derived_semantics.py backend/tests/test_hand_quality.py backend/tests/test_derived_semantics.py; git commit -m "feat: derive natural slam and pass calls"`.

## Chunk 4: Integration and documentation

### Task 8: Integrate, document, and verify the derivation layer

**Files:**
- Modify: `backend/engine/selector.py`
- Modify: `backend/engine/replay.py`
- Modify: `backend/engine/derived_replay.py`
- Modify: `backend/engine/trace.py`
- Modify: `docs/15_daqiush_slam.md`
- Create: `docs/19_derived_semantics.md`
- Modify: `backend/tests/test_derived_semantics.py`
- Modify: `backend/tests/test_derived_four_notrump.py`
- Modify: `backend/tests/test_derived_fit_calls.py`
- Modify: `backend/tests/test_nfrkcb_policy.py`

- [ ] Add failing end-to-end tests that explicit calls still win, a committed Purpose suppresses derivation, derived calls appear before fallback, ambiguity produces TD with evidence, and no generic “reasonable call” is fabricated.
- [ ] Add a multi-turn replay matrix covering derived 4NT, selector, NFRKCB, major cue, minor stopper inquiry, 6NT, and Pass. Every row calls `replay_auction(profile, later_prefix, hand=None)` and asserts exactly one reconstructed meaning/effect set.
- [ ] Run `$env:PYTHONPATH='backend'; python -m unittest tests.test_derived_semantics tests.test_derived_four_notrump tests.test_derived_fit_calls tests.test_nfrkcb_policy -v`; expect the new cross-family trace/replay assertions to fail.
- [ ] In `derived_replay.py`, dispatch to the same pure family rule used for live derivation and require one public interpretation. In `replay.py`, apply returned effects and diagnostics exactly once. In `selector.py`, keep the established explicit/Purpose/derived/fallback order.
- [ ] Add trace serialization for `derived_rule`, public evidence, conflicts, and confidence; assert serialized output contains no private cards, private Purpose fields, or sampled hidden counts.
- [ ] Rerun `$env:PYTHONPATH='backend'; python -m unittest tests.test_derived_semantics tests.test_derived_four_notrump tests.test_derived_fit_calls tests.test_nfrkcb_policy -v`; expect every integration/replay/serialization test to pass.
- [ ] Document priority, each rule family, NFRKCB distinction, simulation boundary, replay reconstruction, and TD diagnostics in the two exact documentation files.
- [ ] Run the full suite with `$env:PYTHONPATH='backend'; python -m unittest discover -s backend/tests -p "test_*.py" -v`; require all tests green and record count/duration.
- [ ] Run `git diff --check` and `git status --short`; require no whitespace errors and preserve unrelated dirty files.
- [ ] Stage exact integration files with `git add backend/engine/selector.py backend/engine/replay.py backend/engine/derived_replay.py backend/engine/trace.py backend/tests/test_derived_semantics.py backend/tests/test_derived_four_notrump.py backend/tests/test_derived_fit_calls.py backend/tests/test_nfrkcb_policy.py docs/15_daqiush_slam.md docs/19_derived_semantics.md`; commit with `git commit -m "docs: explain derived bidding semantics"`.
- [ ] Use `superpowers:requesting-code-review`, address findings with `superpowers:receiving-code-review`, rerun focused/full suites, and use `superpowers:verification-before-completion` before reporting success.

