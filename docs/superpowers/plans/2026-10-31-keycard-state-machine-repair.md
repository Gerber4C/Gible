# Keycard State-Machine Repair Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Voidwood and ordinary RKCB retain a replayable keycard state, so effective trump-queen rules, king inquiries, and final placements cannot create false grand-slam routes or TD.

**Architecture:** An effective Voidwood trump Q is derived from route-specific public length facts, not a universal Voidwood length. The responder treats Q as effective when the asker's guaranteed trump length plus the responder's actual length reaches nine; if the auction had already shown a nine-card fit before the ask, the threshold is ten. Direct unilateral trump agreement after a 1NT transfer must therefore publicly promise six trumps. Voidwood answers advance a *latest-frame* public state from `pending` to `answered` and retain answer facts, so earlier records cannot remain eligible. King inquiries and final placements read that same state in live bidding and replay. Ordinary RKCB's ten-trump convention is deliberately excluded from this repair unless its own public fit predicate and tests are implemented in a later slice.

**Tech Stack:** Python 3, unittest, Gible BSL gadget DSL, public auction replay state.

---

## Chunk 1: Voidwood answer facts and king-inquiry gate

### Task 1: Effective-Q answer

**Files:**
- Modify: `backend/tests/test_daqiush_owner_routes.py`
- Modify: `backend/tests/test_voidwood.py`
- Modify: `backend/partnership_profiles/daqiush_2over1/gadgets/voidwood/gadget.bsl.py`

- [ ] Write a failing owner-route test for South `S-HAKJ972DAQJT3CKQ`, North `SAKH843DK76542CAJ`, and `1NP2DP2HP4SP`; the direct 1NT-transfer Voidwood ask publicly promises six hearts, so North must bid `5D`, the `1/4 + effective Q` answer. Add a distinct already-nine-fit fixture proving its threshold is ten.
- [ ] Run `cd backend; ..\\.venv\\Scripts\\python.exe -m unittest tests.test_daqiush_owner_routes` and confirm it fails because current code returns `5C`.
- [ ] Publish each asker's route-specific minimum trump length into the Voidwood frame. The reported direct-transfer route requires/publishes six; other routes preserve their own existing promises. This prevents a responder from reading a private sixth trump.
- [ ] Add a Voidwood-only effective-Q helper: true when public asker-minimum plus responder actual length reaches nine, or ten if a nine-card fit was already public before the ask. It must not infer unseen cards.
- [ ] Use that helper in legacy and state-driven answer maps, and record the effective result in the public answer state.
- [ ] Run `cd backend; ..\\.venv\\Scripts\\python.exe -m unittest tests.test_daqiush_owner_routes tests.test_voidwood`; confirm PASS.
- [ ] Commit only this test and Voidwood change as `fix: apply effective queen to Voidwood answers`.

### Task 2: King inquiry gate

**Files:**
- Modify: `backend/tests/test_daqiush_owner_routes.py`
- Modify: `backend/partnership_profiles/daqiush_2over1/gadgets/voidwood/gadget.bsl.py`

- [ ] Write a failing genuine-no-effective-Q test proving that the next call is not a king inquiry, and retain an effective-Q fixture that remains eligible.
- [ ] Run the single test and confirm RED: `index == 1` presently admits the inquiry whenever a hand exists.
- [ ] Replace unconditional king-ask predicates with a requirement for complete effective keycards and effective Q from the answered public frame. Implement the same next-step king inquiry after the `1/4 + effective Q` response; preserve direct six-level placements.
- [ ] Run the two focused test modules; confirm PASS.
- [ ] Commit as `fix: gate Voidwood king inquiries on queen facts`.

## Chunk 2: Voidwood progression and completion

### Task 3: Advance frames and remove replay ambiguity

**Files:**
- Modify: `backend/tests/test_voidwood.py`
- Modify: `backend/partnership_profiles/daqiush_2over1/gadgets/voidwood/gadget.bsl.py`

- [ ] Write a failing replay test for `1NP2HP2SP3HP4HP6CP6S`; it must have no `Ambiguous prior call 6S` diagnostic and the frame after `6C` must be `answered`.
- [ ] Run it and confirm RED.
- [ ] Migrate legacy transfer routes and state-driven routes to the same `voidwood` frame representation, then introduce one latest-Voidwood-frame reader over that representation. Do not use `state_exists(... status='pending')`, because historical pending records remain in `AuctionTrace`.
- [ ] Make answer, queen-answer, king-answer, and final-placement effects advance `pending → answered → queen_pending / king_pending → completed`. Restrict every state-driven specification to its precise latest-frame stage; no active frame may start a new Voidwood ask.
- [ ] Run `tests.test_voidwood tests.test_daqiush_owner_routes`; confirm PASS.
- [ ] Commit as `fix: advance Voidwood public frames`.

### Task 4: Complete valid post-king routes

**Files:**
- Modify: `backend/tests/test_daqiush_owner_routes.py`
- Modify: `backend/partnership_profiles/daqiush_2over1/gadgets/voidwood/gadget.bsl.py`

- [ ] Write a failing test with all effective keycards/Q: a legal king inquiry, correct lowest-king or no-king answer, then authored `6<trump>` or `7<trump>` and partner Pass—not TD.
- [ ] Run it and confirm RED.
- [ ] Author only legal final `6<trump>`/`7<trump>` placements after a valid king answer; mark `signoff`, `final_placement`, `purpose_completed=True`, and write a completed public frame so replay and scanner results agree with live bidding.
- [ ] Run the focused Voidwood and owner-route suites; confirm PASS.
- [ ] Commit as `fix: complete Voidwood king continuations`.

## Chunk 3: Ordinary RKCB and suggested-signoff endpoint

### Task 5: Implement approved final-placement semantics

**Files:**
- Modify: `backend/engine/purpose_axiom.py`
- Modify: `backend/engine/derived_replay.py`
- Modify: `backend/partnership_profiles/daqiush_2over1/gadgets/one_notrump_invitations/gadget.bsl.py`
- Modify: `backend/tests/test_purpose_axiom.py`
- Modify: `backend/tests/test_derived_semantics.py`
- Modify: `backend/tests/test_daqiush_owner_routes.py`

- [ ] Write failing endpoint/control tests for `1NT–2S–3C–3NT–4D–4NT–5H–6C–Pass`: replay marks `6C` as `keycard_final_placement`; partner Passes. Queen asks, 5S relay, 5NT/king calls, and new suits remain nonterminal.
- [ ] Run the focused tests and confirm RED.
- [ ] Derive terminal semantics only for an agreed-trump 5/6/7 bid by the original ordinary-RKCB asker after a public answered `rkcb_1430` frame. Mark it complete and replayable.
- [ ] For only `stayman_*_after_*_shortage_stop`, remove `purpose_completed`, author explicit Pass/ordinary 4NT, and suppress the route-local competing Voidwood candidate. Leave no-shortage refusals unchanged.
- [ ] Run `tests.test_voidwood tests.test_daqiush_owner_routes tests.test_purpose_axiom tests.test_derived_semantics tests.test_daqiush_resample_followups`; confirm PASS.
- [ ] Commit as `fix: make keycard placements replayable`.
