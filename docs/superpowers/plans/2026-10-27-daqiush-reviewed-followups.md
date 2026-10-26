# Daqiush reviewed follow-ups Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement and test the executable portions of the reviewed Daqiush 1NT follow-up and invitation rules without exposing private simulation information.

**Architecture:** Extend the existing Daqiush gadgets at their current auction-state boundaries. Keep slam follow-ups in the Stayman/Jacoby/Keycard gadgets and keep invitation/shape predicates in the 1NT invitation and minor-shape gadgets; add only narrow predicates and explicit continuation calls. Preserve blocking for underspecified audit notes.

**Tech Stack:** Python BSL profile gadgets, `unittest`, auction selector/replay/simulation helpers.

---

## Files and responsibilities

- Modify `backend/partnership_profiles/daqiush_2over1/gadgets/one_notrump_invitations/gadget.bsl.py` for Stayman, ordinary invitation, major-fit shortage, and minor invitation predicates.
- Modify `backend/partnership_profiles/daqiush_2over1/gadgets/jacoby_major_transfers/gadget.bsl.py` for transfer, superaccept, second-minor, and post-invitation continuations.
- Modify `backend/partnership_profiles/daqiush_2over1/gadgets/jacoby_splinter/gadget.bsl.py` for confirmed-shortness strength branches.
- Modify `backend/partnership_profiles/daqiush_2over1/gadgets/south_african_texas/gadget.bsl.py` for game-only versus slam-keycard Texas.
- Modify `backend/partnership_profiles/daqiush_2over1/gadgets/confirmed_keycard/gadget.bsl.py` for reviewed answer/placement states.
- Modify `backend/partnership_profiles/daqiush_2over1/gadgets/minor_shortage_invitation/gadget.bsl.py` and `minor_two_suit_game/gadget.bsl.py` only when the reviewed low-minor route is not already owned by the 1NT gadget.
- Modify `backend/partnership_profiles/daqiush_2over1/gadgets/five_card_major_inquiry/gadget.bsl.py` only for the exact G016 convention if its public trigger is confirmed by tests.
- Modify `backend/partnership_profiles/daqiush_2over1/gadgets/confirmed_trump_prefixes/gadget.bsl.py` only for reviewed historical-prefix metadata or an exact public continuation that belongs to its existing prefix states.
- Add focused tests to the existing Daqiush test modules; do not create a second test harness.
- Update `docs/13_daqiush_2over1.md` and `docs/15_daqiush_slam.md` after behavior is verified.

## Chunk 1: Audit extraction and baseline

- [ ] **Step 1: Extract the final reviewer notes for all named groups**

Read the audit JSON and record, in the implementation notes or test names,
the final reviewer direction for G001–G003, G006–G009, G012–G013, G016,
G022, G032, G040, G049, G059, G061, G068, G071, G081, G018, G021, G030,
G039, G051, G069, G072, G084, and G085. Exclude rejected proposals.

Source: `D:\A0_bridge\]crtb-b\gible-review-a22163d59b5ee620d5b9.json`.
Record accepted behavior in test names and leave a short comment in the
nearest gadget only when the audit wording would otherwise be ambiguous; do
not copy the external JSON into the repository.

- [ ] **Step 2: Run the current targeted baseline**

Run:

```powershell
$env:PYTHONPATH=(Resolve-Path backend).Path
python -m unittest backend.tests.test_daqiush_resample_followups backend.tests.test_daqiush_jacoby backend.tests.test_daqiush_splinter backend.tests.test_daqiush_minor_invitations backend.tests.test_daqiush_minor_slam_simulation
```

Expected: existing tests pass, with any failures recorded as baseline rather
than silently folded into this change.

## Chunk 2: Stayman shortage and no-shortage slam follow-ups

**Files:** `one_notrump_invitations/gadget.bsl.py`,
`confirmed_keycard/gadget.bsl.py`,
`backend/tests/test_daqiush_resample_followups.py`.

- [ ] **Step 1: Add failing tests for G001/G013/G049/G059/G061**

Cover the reviewed sequence after a major-fit shortage answer:

1. weak adjusted strength returns to the agreed-major game;
2. intermediate adjusted strength shows the first available control;
3. sufficient adjusted strength asks 4NT;
4. after a denied no-shortage probe, a strong hand continues only when the
   public strength class permits it;
5. a weak hand does not issue 4NT.

- [ ] **Step 2: Run only the new tests and confirm failure**

Run the selected test methods with `python -m unittest ... -v`.
Expected: the new assertions fail on the current continuation or remain
blocked, proving the tests exercise missing behavior.

- [ ] **Step 3: Implement the narrow continuation predicates**

Reuse `shortage_adjusted_points`, `shortage_has_control`, and
`shortage_first_cue`. Ensure all continuation predicates derive from the
responder’s hand and the public auction only. Do not inspect sampled deals.

- [ ] **Step 4: Add reviewed keycard placement coverage**

Test the 1430 answer branches and final agreed-major placement for the
shortage and no-shortage prefixes. Preserve the existing queen-ask
uncertainty behavior.

- [ ] **Step 5: Run the focused suite**

Run `test_daqiush_resample_followups.py`,
`test_daqiush_keycard.py`, and `test_daqiush_splinter.py`.
Expected: PASS.

## Chunk 3: Jacoby, Texas, and splinter continuations

**Files:** `jacoby_major_transfers/gadget.bsl.py`,
`jacoby_splinter/gadget.bsl.py`, `south_african_texas/gadget.bsl.py`,
`confirmed_keycard/gadget.bsl.py`, and their existing tests.

- [ ] **Step 1: Add failing tests for G002/G003/G006/G007/G008/G009/G012/G022/G032/G040/G068/G071/G081**

Test these public patterns:

- 4D major-fit slam try followed by a refusal does not force pass when the
  opener has the reviewed continuation strength;
- Texas with slam interest asks 4NT, while game-only Texas stops in 4M;
- a 6M-5m hand shows the second minor naturally when the audit requires it;
- a strong long-minor/major-fit hand uses the reviewed natural route before
  any artificial slam route;
- no-shortage major-fit hands use 4D before 4NT;
- the exact artificial convention for G016 is tested only if its auction
  trigger is publicly meaningful.

- [ ] **Step 2: Run the new tests and confirm failure**

Expected: at least one assertion fails or the candidate is blocked on the
current profile.

- [ ] **Step 3: Implement each continuation at the owning gadget boundary**

Use explicit auction prefixes and narrow predicates. Keep candidate priority
consistent with existing call ordering. For every artificial call, populate
`meaning`, `effect`, and agreed-trump/keycard state exactly as neighboring
calls do.

- [ ] **Step 4: Add negative tests**

Verify that ordinary weak transfers, unsupported singleton inferences, and
game-only hands cannot reach the new slam calls.

- [ ] **Step 5: Run the Jacoby/Texas/splinter suites**

Expected: PASS for `test_daqiush_jacoby.py`,
`test_daqiush_splinter.py`, `test_daqiush_texas.py`,
`test_daqiush_keycard.py`, and `test_daqiush_resample_followups.py`.

## Chunk 4: Invitation and shape routing

**Files:** `one_notrump_invitations/gadget.bsl.py`,
`minor_shortage_invitation/gadget.bsl.py`,
`minor_two_suit_game/gadget.bsl.py`, and
`backend/tests/test_daqiush_minor_invitations.py`,
`backend/tests/test_daqiush_one_notrump_expansion.py`.

- [ ] **Step 1: Add failing tests for G018/G021/G030/G039/G051/G069/G072/G084/G085**

Cover:

- 6–8 HCP major-shape invitations, with 8-point hands inviting and 7-point
  hands requiring the reviewed quality/shape guard;
- super-shaped hands bypassing a redundant invitation;
- weak transfer routes that can use a superaccept to reach game;
- five-card-major invitation acceptance split by high/low opener values and
  fit quality;
- excellent six-club hands using the reviewed direct 3C route, otherwise
  the existing natural 3NT/club route;
- seven-card club and 6-5 minor decisions using effective controls;
- G085’s reviewed 7+ effective-point 4NT versus lower 3H branch.

- [ ] **Step 2: Run the new tests and confirm failure**

Expected: failures identify either a stolen candidate, a missing continuation,
or an incorrect threshold.

- [ ] **Step 3: Implement the smallest predicate/continuation changes**

Reuse `INVITATION_QUALITY`, `minor_game_control_points`, effective-point
helpers, and existing public partner constraints. Do not replace a
simulation-selected call with hidden deal knowledge.

- [ ] **Step 4: Add boundary tests**

Test one hand just below and one just above every new threshold. Test both
major fits and no-fit cases where the same auction can otherwise be legal.

- [ ] **Step 5: Run the invitation and shape suites**

Expected: PASS for `test_daqiush_minor_invitations.py`,
`test_daqiush_one_notrump_expansion.py`, and
`test_daqiush_minor_slam_simulation.py`.

## Chunk 5: G016 and underspecified audit notes

**Files:** `five_card_major_inquiry/gadget.bsl.py`,
`confirmed_trump_prefixes/gadget.bsl.py`, relevant tests, and docs.

- [ ] **Step 1: Verify whether G016 has a complete public trigger**

Inspect the audit target auction and current candidate trace. If the proposed
4H meaning would require knowing responder’s hidden three-card spade fit, do
not add it as an automatic rule. The expected outcome for this audit is to
keep the continuation blocked unless the exact public trigger is complete.

- [ ] **Step 2: If the trigger is complete, add a failing replay test**

Assert the exact artificial 4H meaning, agreed spades, and every documented
continuation. Otherwise add a regression test that the incomplete route stays
blocked and document the missing convention; this is the expected path when
the audit does not define the follow-up.

- [ ] **Step 3: Run the replay and selector tests**

Expected: no private-information leak and no change to unrelated 3C/3D/3H
inquiry routes.

## Chunk 6: Documentation and full verification

- [ ] **Step 1: Update the Daqiush docs**

Document only tested calls and explicitly state which audit notes remain
blocked because the review lacks a complete public convention.

- [ ] **Step 2: Run all Daqiush tests**

Run:

```powershell
$env:PYTHONPATH=(Resolve-Path backend).Path
python -m unittest discover -s backend/tests -p "test_daqiush*.py" -v
```

Expected: all relevant tests pass; unrelated pre-existing failures are listed
separately if they occur.

- [ ] **Step 3: Check profile loading and diff hygiene**

Run:

```powershell
$env:PYTHONPATH=(Resolve-Path backend).Path
python -m unittest backend.tests.test_profile_loading
git diff --check
```

Expected: profile loads successfully and `git diff --check` is clean.

- [ ] **Step 4: Commit coherent changes**

Use separate commits for slam follow-ups, invitation/shape routing, and docs,
each including:

```text
Co-authored-by: Copilot App <223556219+Copilot@users.noreply.github.com>
```
