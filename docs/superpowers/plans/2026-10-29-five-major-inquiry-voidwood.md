# Five-Major Inquiry and Voidwood Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete the Daqiush `1NT-3C` continuations for 3-1-major/5-4-minor hands and replace the prefix-specific exclusion-keycard gadget with safe, confirmed-trump-driven Voidwood.

**Architecture:** Keep authored meanings and state effects in focused Daqiush gadgets, but move auction-independent decision arithmetic into two small engine policy modules. `five_major_inquiry_policy.py` owns structural fallback and sampled final-contract selection; `voidwood.py` owns jump construction, four-effective-keycard answer mapping, and worst-case landing-level safety. `selector.py` only dispatches to those policies and records their explanations.

**Tech Stack:** Python 3, Gible Python-BSL gadgets, `unittest`, existing sampled-deal/DDS adapters, immutable `Auction` and `Hand` engine models.

**Specification:** `docs/superpowers/specs/2026-10-29-five-major-inquiry-voidwood-design.md`

**Isolated worktree:** `D:\A0_bridge\BridgeSoftware\test\Gible\.worktrees\five-major-voidwood`

---

## File map

- Create `backend/engine/five_major_inquiry_policy.py`: pure route recognition, exact deterministic predicates, sampled contract comparison, and structured decisions for the new `3C` branches.
- Create `backend/engine/voidwood.py`: legal one-level jump discovery, answer-step construction, four-effective-keycard disambiguation, and worst-case safety checks.
- Modify `backend/engine/hand_quality.py` and `backend/engine/bsl.py`: expose one shared `minor_slam_interest` predicate so the existing profile and the new engine policy cannot drift.
- Modify `backend/engine/selector.py`: dispatch only at the authored `3C` choice points; use sampled result, then deterministic fallback, then ordinary TD behavior.
- Modify `backend/partnership_profiles/daqiush_2over1/gadgets/five_card_major_inquiry/gadget.bsl.py`: author all calls, state effects, finality, and symmetric relative-suit meanings.
- Rename `backend/partnership_profiles/daqiush_2over1/gadgets/exclusion_keycard/` to `backend/partnership_profiles/daqiush_2over1/gadgets/voidwood/` and replace fixed prefixes with confirmed-trump-state requirements.
- Modify `backend/partnership_profiles/daqiush_2over1/profile.bsl.py`: register `voidwood`.
- Modify `backend/engine/memory.py` and `backend/engine/purpose_axiom.py`: retain the asker's effective keycard count and excluded suit in private seat memory; never publish private hand-derived counts.
- Modify `backend/engine/replay.py` only if old serialized `exclusion_keycard` action/method strings need read-only aliases; do not emit old names.
- Create `backend/tests/test_daqiush_five_major_inquiry.py`: route, symmetry, fallback, simulation, state, and final-placement tests.
- Create `backend/tests/test_voidwood.py`: pure safety arithmetic plus end-to-end gadget tests.
- Modify `backend/tests/test_daqiush_owner_routes.py`: remove/redirect the old exclusion-specific tests while retaining unrelated owner-route and grand-slam tests.
- Modify `docs/13_daqiush_2over1.md` and `docs/15_daqiush_slam.md`: document implemented `3C` continuations and the Voidwood name/safety rule.

## Chunk 1: Implement and verify the feature

### Task 1: Pure five-major-inquiry deterministic policy

**Files:**
- Create: `backend/engine/five_major_inquiry_policy.py`
- Modify: `backend/engine/hand_quality.py`
- Modify: `backend/engine/bsl.py`
- Modify: `backend/partnership_profiles/daqiush_2over1/gadgets/one_notrump_invitations/gadget.bsl.py`
- Create: `backend/tests/test_daqiush_five_major_inquiry.py`
- Modify: `backend/tests/test_hand_quality.py`
- Reference: `backend/engine/hand_quality.py`
- Reference: `backend/engine/simulation_decision.py`

- [ ] **Step 1: Write failing tests for route recognition and exact fallback predicates**

Add tests for both singleton-major orientations and both 5-4 minor orientations. Test the desired public API before it exists:

```python
from engine.five_major_inquiry_policy import deterministic_after_singleton
from engine.hand_quality import minor_slam_interest

def test_minor_slam_interest_uses_named_profile_threshold(self):
    self.assertFalse(minor_slam_interest(Hand.parse('SKQ5H2DAJ954C8765')))
    self.assertTrue(minor_slam_interest(Hand.parse('SAK5H2DKQJ54C8765')))

def test_four_four_minors_good_controls_set_diamonds(self):
    result = deterministic_after_singleton(
        Hand.parse('SAJ4HA2DKQ76CQJ84'), singleton_major='H')
    self.assertEqual(result.call, '4H')
    self.assertEqual(result.agreed_suit, 'D')
```

Include negative cases for major waste, control points below `14.5`, two
ambiguous four-card minors, a unique four-card minor, a unique 4-3 `oM`
candidate, exact 3-3 minors, stopper plus no structurally eligible suit route
choosing 3NT, stopper plus an eligible suit route returning TD without DDS,
and any other unresolved overlap returning an inconclusive decision rather
than guessing.

- [ ] **Step 2: Run the new test module and verify RED**

Run from `backend`:

```powershell
python -m unittest tests.test_daqiush_five_major_inquiry -v
```

Expected: import failure for `engine.five_major_inquiry_policy`.

- [ ] **Step 3: Implement immutable decision data and deterministic helpers**

First move the existing `14.0` threshold out of the BSL gadget into
`hand_quality.py`:

```python
MINOR_SLAM_KR = 14.0

def minor_slam_interest(hand: Hand) -> bool:
    return assess_quality(hand)['kr_points'] >= MINOR_SLAM_KR
```

Expose the predicate in the BSL environment, replace the local
`MINOR_SLAM_KR` use in `one_notrump_invitations`, and add a regression test
showing the old route and the new policy call the same predicate. Do not define
a second threshold in `five_major_inquiry_policy.py`.

Create the focused policy module with interfaces shaped like:

```python
@dataclass(frozen=True)
class InquiryDecision:
    call: str | None
    source: str
    reason: str
    agreed_suit: str | None = None
    final: bool = False

def deterministic_after_singleton(
    opener: Hand, *, singleton_major: str
) -> InquiryDecision:
    ...
```

Reuse `stopper`, `minor_game_control_points`, and `shapely_control_points`; do not duplicate their honor tables. Implement the spec's exact eligibility rules. Select only a unique structural candidate; return `call=None, source='inconclusive'` on unresolved overlaps.

- [ ] **Step 4: Run the focused tests and verify GREEN**

Run:

```powershell
python -m unittest tests.test_daqiush_five_major_inquiry -v
```

Expected: all Task 1 tests pass.

- [ ] **Step 5: Commit the pure policy**

```powershell
git add backend/engine/five_major_inquiry_policy.py backend/engine/hand_quality.py backend/engine/bsl.py backend/partnership_profiles/daqiush_2over1/gadgets/one_notrump_invitations/gadget.bsl.py backend/tests/test_daqiush_five_major_inquiry.py backend/tests/test_hand_quality.py
git commit -m "feat: add five-major inquiry fallback policy"
```

### Task 2: Author all `1NT-3C` calls and trump effects

**Files:**
- Modify: `backend/partnership_profiles/daqiush_2over1/gadgets/five_card_major_inquiry/gadget.bsl.py`
- Modify: `backend/tests/test_daqiush_five_major_inquiry.py`
- Reference: `backend/engine/trump_state.py`
- Reference: `backend/partnership_profiles/daqiush_2over1/gadgets/confirmed_trump_prefixes/gadget.bsl.py`

- [ ] **Step 1: Add failing end-to-end tests for authored candidates**

Use `load_profile`, `Auction.parse`, `choose_bid`, and `replay_auction`. Cover:

- `3D-3H` and `3D-3S` singleton reports;
- stopper plus no structurally eligible suit candidate producing `3NT` final
  placement, and stopper plus an eligible suit candidate remaining
  inconclusive/TD without DDS;
- special `4M` setting diamonds;
- `4C` and `4D` setting the bid minor;
- `4oM` and responder Pass versus lowest legal five-card minor;
- 3-3-minor `4NT`, followed by `5m` final fallback;
- opener `3H` and `3S`, each with responder's three-card support and singleton;
- `4C` meaning 5C4D and `4D` meaning 5D4C;
- all mappings `4C-4D/4H/4S/5C` and `4D-4H/4S`;
- every trump-setting call replaying an `agreed_suit` state;
- every specified signoff carrying `final_placement` and `purpose_completed`.

Assert symmetric results by looping over heart/spade-swapped fixtures instead of copying one suit's assertions.

- [ ] **Step 2: Run the tests and verify RED**

Run:

```powershell
python -m unittest tests.test_daqiush_five_major_inquiry -v
```

Expected: current block/wrong-placement failures at the newly specified auctions.

- [ ] **Step 3: Add shared BSL helpers and authored calls**

Extend the gadget with small helpers rather than one large `build` block:

```python
def other_major(suit):
    return 'S' if suit == 'H' else 'H'

def five_four_minor(ctx, five, four):
    return (ctx.hand is not None and ctx.hand.length(five) == 5
            and ctx.hand.length(four) == 4
            and sorted(ctx.hand.length(s) for s in 'HS') == [1, 3])
```

Generate heart/spade and club/diamond cases from tables. Add `agreed_suit`
effects exactly where the spec says “sets” or “establishes” trumps. Keep
descriptive strength-showing calls non-final; mark final contracts explicitly.
Do not attach control-showing meaning to the trump-selector calls.

- [ ] **Step 4: Run focused profile tests and existing expansion tests**

Run:

```powershell
python -m unittest tests.test_daqiush_five_major_inquiry tests.test_daqiush_one_notrump_expansion -v
```

Expected: all pass.

- [ ] **Step 5: Commit authored routes**

```powershell
git add backend/partnership_profiles/daqiush_2over1/gadgets/five_card_major_inquiry/gadget.bsl.py backend/tests/test_daqiush_five_major_inquiry.py
git commit -m "feat: author five-major inquiry continuations"
```

### Task 3: Add sampled decisions and selector fallback order

**Files:**
- Modify: `backend/engine/five_major_inquiry_policy.py`
- Modify: `backend/engine/selector.py`
- Modify: `backend/tests/test_daqiush_five_major_inquiry.py`
- Reference: `backend/engine/simulation_decision.py`
- Reference: `backend/engine/dds_adapter.py`

- [ ] **Step 1: Write failing tests for DDS-first, fallback-second, TD-last**

Patch only the DDS table boundary, not the policy under test. Add a
table-driven singleton-report matrix whose authored non-3NT alternatives are
the special `4M`/diamonds route, unique `4C`, unique `4D`, `4oM`, and
three-three-minor `4NT`. For every row assert all of:

- DDS prefers 3NT, so 3NT is selected;
- DDS prefers that exact authored alternative, so that route is selected;
- DDS is unavailable and the deterministic structural facts uniquely select
  that route, so the same route is selected;
- DDS is unavailable while both 3NT and the route remain structurally
  plausible, so the result is inconclusive/TD rather than a guess.

Also test:

- after opener's `3H` and `3S`, sampled game-versus-slam classification for
  both three-card-support and singleton-in-`M` responders;
- DDS-unavailable fallback to the shared `minor_slam_interest` predicate in
  both of those responder branches;
- three-card support choosing `4M` without interest or lowest legal `oM` with
  interest, with the next unsupported exploration point producing an explicit
  inconclusive/TD diagnostic rather than an invented continuation;
- singleton-in-`M` choosing `3NT` without interest or the four-level five-card
  minor with interest;
- after both `4C` (5C4D) and `4D` (5D4C), sampled selection among the authored
  trump-setting calls, deterministic length/control tie-break, and TD only if
  neither method decides;
- an unavailable solver selecting the deterministic call;
- an unauthored sampled call falling through to deterministic selection;
- an inconclusive deterministic result leaving no accepted candidate so normal TD occurs;
- `4oM` Pass versus five-card-minor continuation;
- post-`5m` final candidates `5m`, cheapest legal `5oM`, `6m`, `6oM`;
- post-`4NT` final candidates `5m` and `6m`;
- trace `simulation_decision.source` identifying `dds`, `deterministic`, or `inconclusive`.

- [ ] **Step 2: Run and verify RED**

Run:

```powershell
python -m unittest tests.test_daqiush_five_major_inquiry -v
```

Expected: sampled decision functions/selector dispatch are missing.

- [ ] **Step 3: Implement sampled decision functions**

Add explicit recognizers for the no-five-major and five-card-major families
instead of a catch-all hook:

```python
def inquiry_decision_kind(profile_id: str, auction: Auction) -> str | None:
    ...

def decide_five_major_inquiry(
    profile, auction: Auction, hand: Hand
) -> InquiryDecision:
    ...
```

Use the existing public-information deal sampler and DDS scoring helpers.
Return only one of the candidates authored for that exact decision kind. The
decision kinds must include singleton-major placement after `3D`, responder
slam classification after `3M`, opener's strain selection after responder's
`4C/4D`, post-`4oM` continuation, and final placement after `4NT`/`5m`. If DDS
is unavailable, call the corresponding pure deterministic helper. If DDS
returns a call outside the authored set, record that reason and fall through
to the helper.

- [ ] **Step 4: Integrate one narrow selector dispatch**

Import the recognizer/decision function in `selector.py`. Insert the dispatch
beside the existing specialized simulation branches, before generic policy
ranking. Match the returned call to the already generated candidates. Do not
manufacture a candidate in the selector.

- [ ] **Step 5: Run focused and selector regression tests**

Run:

```powershell
python -m unittest tests.test_daqiush_five_major_inquiry tests.test_daqiush_minor_slam_simulation tests.test_daqiush_resample_followups -v
```

Expected: new tests pass; existing simulation decisions retain their results.

- [ ] **Step 6: Commit simulation integration**

```powershell
git add backend/engine/five_major_inquiry_policy.py backend/engine/selector.py backend/tests/test_daqiush_five_major_inquiry.py
git commit -m "feat: simulate five-major inquiry placements"
```

### Task 4: Build pure Voidwood call and safety arithmetic

**Files:**
- Create: `backend/engine/voidwood.py`
- Create: `backend/tests/test_voidwood.py`
- Reference: `backend/engine/legality.py`
- Reference: `backend/engine/cards.py`

- [ ] **Step 1: Write failing pure-unit tests**

Define the desired API in tests:

```python
from engine.voidwood import (
    VoidwoodContext,
    answer_bids,
    is_safe_voidwood_ask,
    voidwood_jump,
)

def test_diamond_trump_club_void_jump_is_five_clubs(self):
    auction = Auction.parse('1NP2HP2SP3DP3HP')
    self.assertEqual(voidwood_jump(auction, trump='D', void='C'), '5C')
    self.assertEqual(answer_bids('5C'), ('5D', '5H', '5S', '5N', '6C'))
```

Cover:

- call-order stepping across NT;
- a table-driven answer map for every generic ask boundary the profile can
  expose: `4S`, `5C`, `5D`, `5H`, `5S`, `6C`, `6D`, `6H`, and `6S`;
- rejection below `4S`;
- rejection of non-jumps and trump-suit asks;
- rejection at `7C`, the first suit-call boundary without five remaining
  answer steps, and at every higher suit call;
- rejection when a keycard inquiry is already pending;
- rejection with a named diagnostic when confirmed trump is absent,
  provisional, or conflicts with the requested trump;
- rejection with a named diagnostic when the void suit equals trumps or the
  hand is not actually void;
- exactly four effective keycards after excluding the void ace;
- 0/3 and 1/4 interpretations pruned by the asker's own count;
- the `5C`/diamond example: zero can stop at `5D`, nonzero cannot;
- unsafe own counts rejected when a nonzero answer can force six while leaving two missing;
- safe own counts accepted when every forced-six branch has at least three of four;
- ordinary lower Voidwood whose answers still permit a five-level trump stop.

- [ ] **Step 2: Run and verify RED**

Run:

```powershell
python -m unittest tests.test_voidwood -v
```

Expected: import failure for `engine.voidwood`.

- [ ] **Step 3: Implement pure immutable helpers**

Use canonical contract order from `legality.py`; do not keep a second divergent
order table in the gadget. Suggested structures:

```python
@dataclass(frozen=True)
class VoidwoodContext:
    trump: str
    void: str
    ask: str
    own_effective_keycards: int

@dataclass(frozen=True)
class VoidwoodSafety:
    safe: bool
    reason: str
    forced_six_answers: tuple[str, ...]
```

`is_safe_voidwood_ask` must enumerate all answer categories compatible with
the asker's private count and apply the three-of-four small-slam threshold.
Keep Q information out of the small-slam safety result.

Add a separate context validator that accepts the current `TrumpState`,
pending-keycard flag, requested void, and actual hand. It returns a structured
ineligibility reason used verbatim in selection diagnostics. This keeps
missing/conflicting state tests independent of BSL lambdas.

- [ ] **Step 4: Run pure tests and verify GREEN**

Run:

```powershell
python -m unittest tests.test_voidwood -v
```

Expected: all pure helper tests pass.

- [ ] **Step 5: Commit the Voidwood engine**

```powershell
git add backend/engine/voidwood.py backend/tests/test_voidwood.py
git commit -m "feat: add safe voidwood policy"
```

### Task 5: Rename and generalize the Daqiush Voidwood gadget

**Files:**
- Rename: `backend/partnership_profiles/daqiush_2over1/gadgets/exclusion_keycard/gadget.bsl.py` → `backend/partnership_profiles/daqiush_2over1/gadgets/voidwood/gadget.bsl.py`
- Modify: `backend/partnership_profiles/daqiush_2over1/profile.bsl.py`
- Modify: `backend/tests/test_voidwood.py`
- Modify: `backend/tests/test_daqiush_owner_routes.py`
- Modify: `backend/engine/memory.py`
- Modify: `backend/engine/purpose_axiom.py`
- Modify: `backend/engine/selector.py`
- Modify if required: `backend/engine/replay.py`

- [ ] **Step 1: Add failing profile and end-to-end tests**

Test that:

- the profile registers `voidwood` and not `exclusion_keycard`;
- new meanings/state emit `voidwood_ask`, `voidwood_answer`, and method
  `voidwood` only;
- the gadget/profile description visible to explanations is exactly
  `Voidwood（缺门关键张）`;
- an old serialized state may replay through a read-only alias if an existing
  persisted-report fixture requires it;
- the transfer examples still work;
- `1NT-2H-2S-3D-3H` replays diamonds as agreed, and a safe club-void hand can
  choose `5C`;
- the same confirmed diamond state reached by a second authored auction family
  exposes the same `5C` call without adding another complete prefix;
- an unsafe hand does not receive `5C` as a candidate;
- no candidate is exposed with a pending keycard context, absent/provisional
  trump, conflicting agreed trump, or non-void bid suit; each trace contains
  the structured diagnostic from the pure validator;
- all five answers and Q/K continuations use the dynamic ask context;
- one complete multi-round private-purpose sequence for each continuation
  family: `0/3 -> Q ask -> Q answer -> final`, `0/3 -> K ask -> K answer ->
  final`, and `5NT+ answer -> grand invitation -> public accept/decline`;
- the same `Purpose` remains active through intermediate Q/K asks and advances
  its named stage. It becomes completed on a final placement; for a grand
  invitation it becomes completed when the invitation is selected because no
  further asker-private information is needed and a declining Pass may end the
  auction before the asker acts again. The partner's accept/decline remains a
  normal public BSL response. Assert both the pre-response completed memory and
  the declined terminal auction;
- a grand invitation that skips a lower side suit records in its public meaning
  that the skipped suit's king is not required; partner acceptance/decline must
  not depend on holding that king, while higher unpassed suits remain unknown;
- the initiating candidate writes `own_keycards` (the effective count) and
  `excluded_suit` only into the asker's `SeatMemory` Purpose; replay without a
  private hand does not expose either value publicly, and the partner's memory
  does not receive them;
- the void ace counts as that suit's king in the king-answer branch;
- ordinary 1430 remains unchanged.

- [ ] **Step 2: Run and verify RED**

Run:

```powershell
python -m unittest tests.test_voidwood tests.test_daqiush_owner_routes tests.test_daqiush_keycard -v
```

Expected: old gadget name/fixed prefixes and missing safety gate fail.

- [ ] **Step 3: Rename the gadget and generate state-driven calls**

Move the directory with Git-aware rename. In the gadget:

- use `when='*'` plus `ctx.state.exists('agreed_suit', suit=...)` requirements;
- generate each legal trump/void pairing from a shared table of suits;
- obtain the expected jump and answer bids from `engine.voidwood` through
  registered safe evaluators rather than copying arithmetic into lambdas;
- require the pure safety verdict before offering the ask;
- save public trump, void, ask call, and method `voidwood` in frame state;
- attach a callable `private_purpose` to the ask candidate and extend
  `Purpose` with `excluded_suit`, `stage`, and `pending_call_index`; store the
  effective count in the existing private `own_keycards` field owned by the
  asker. The initial stage is `keycard_answer`, and `pending_call_index` is the
  selected Voidwood ask's auction index;
- extend `remember_selected_purpose` with a `kind='voidwood'` branch before its
  ordinary-4NT logic. It must write the Purpose only to the initiating seat's
  `SeatMemory`;
- replace the current unconditional `complete_purpose` call with an
  `advance_or_complete_purpose(memory, purpose, selected_candidate,
  auction)` operation. Ordinary existing purposes retain their current
  one-reply completion behavior. For Voidwood, a selected Q ask or K ask
  carries `purpose_continues=True`; the operation updates `stage` and
  `pending_call_index` to that newly selected ask instead of completing the
  Purpose. A signoff, small-slam placement, or grand invitation completes it.
  The invitation's later accept/decline is public and must not attempt to
  mutate the initiator's already-completed private memory;
- extend `resolve_purpose` so Voidwood waits for the partner reply exactly four
  calls after the current `pending_call_index`, validates the original source
  plus the current stage, and uses the saved effective count/excluded suit to
  disambiguate public 0/3 or 1/4 answers. It then returns the stage-appropriate
  private follow-up candidate. It must not apply the ordinary rule that any
  turn later than `source_index + 4` automatically disrupts the purpose;
- keep partner answers as ordinary public BSL candidates driven by the
  partner's hand and public `voidwood` frame. Asker-only Q/K/grand follow-ups
  come from `resolve_purpose`, so BSL applicability never needs access to
  another seat's private memory;
- generate answer/Q/K/grand continuations from the saved ask instead of a
  fixed transfer prefix.

If the BSL loader cannot import the pure helper directly, register named
evaluators in the gadget and keep each evaluator as a thin adapter. Do not
move safety arithmetic back into the gadget.

- [ ] **Step 4: Add the confirmed-diamond prefix effect**

Author/replay `1NT-2H-2S-3D-3H` as diamond agreement in the appropriate
existing Daqiush gadget. Assert the `3H` call itself does not promise heart
control unless a separate meaning explicitly says so. Use the already authored
`1NT-2D-2H-3D-3S` diamond-support cue as the second exact auction family in
the state-driven Voidwood regression test; both must expose the same safe
club-void `5C` without two prefix-specific Voidwood rules.

- [ ] **Step 5: Add only necessary legacy aliases**

Search persisted fixtures for old action/method strings. If none are consumed
by runtime replay, omit aliases. If required, translate old strings only on
input in `replay.py`; all newly emitted state remains `voidwood`.

- [ ] **Step 6: Run focused regression tests**

Run:

```powershell
python -m unittest tests.test_voidwood tests.test_daqiush_owner_routes tests.test_daqiush_keycard tests.test_daqiush_jacoby -v
```

Expected: all pass.

- [ ] **Step 7: Commit the rename and generalization**

```powershell
git add -A backend/partnership_profiles/daqiush_2over1/gadgets backend/partnership_profiles/daqiush_2over1/profile.bsl.py backend/engine/memory.py backend/engine/purpose_axiom.py backend/engine/selector.py backend/engine/replay.py backend/tests/test_voidwood.py backend/tests/test_daqiush_owner_routes.py
git commit -m "feat: generalize exclusion asks as voidwood"
```

### Task 6: Documentation and full verification

**Files:**
- Modify: `docs/13_daqiush_2over1.md`
- Modify: `docs/15_daqiush_slam.md`
- Verify: all files changed by Tasks 1–5

- [ ] **Step 1: Update system documentation**

Document:

- the complete `3C` continuation table;
- relative `M/oM/m/om` terminology;
- simulation → deterministic → TD selection order;
- every trump-setting and final-placement call;
- Voidwood's confirmed-trump requirement;
- the public label `Voidwood（缺门关键张）`;
- the one-level-jump-at-`4S`-or-higher definition;
- four effective keycards and the three-of-four small-slam safety threshold;
- the diamond-trump/club-void `5C` example;
- the explicit warning that if nonzero answers force beyond `5D`, the asker
  must already be safe at `6D`.

- [ ] **Step 2: Run formatting and stale-name searches**

Run from repository root:

```powershell
git diff --check
rg -n "exclusion_keycard|exclusion_1430|Exclusion keycard" backend docs
```

Expected: no new emitted Daqiush names remain; only intentional Meow benchmark,
historical text, or documented legacy aliases appear.

- [ ] **Step 3: Run the focused feature suite**

Run from `backend`:

```powershell
python -m unittest tests.test_daqiush_five_major_inquiry tests.test_voidwood tests.test_daqiush_one_notrump_expansion tests.test_daqiush_owner_routes tests.test_daqiush_keycard tests.test_daqiush_minor_slam_simulation tests.test_daqiush_jacoby -v
```

Expected: all pass. The pre-change baseline for the overlapping four modules
was 44 passing tests.

- [ ] **Step 4: Run the complete backend suite**

Run:

```powershell
python -m unittest discover -s tests -v
```

Expected: no failures newly introduced by this branch. If unrelated baseline
failures remain, list each exact test and compare it with a clean `23ea0db`
worktree before proceeding.

- [ ] **Step 5: Inspect the final diff and profile loading**

Run from repository root:

```powershell
git status --short
git diff --check
git diff --stat main...HEAD
```

Load the Daqiush profile once from `backend` and confirm no compiler warning or
duplicate-call ambiguity is introduced.

- [ ] **Step 6: Commit documentation**

```powershell
git add docs/13_daqiush_2over1.md docs/15_daqiush_slam.md
git commit -m "docs: document five-major inquiry and voidwood"
```

- [ ] **Step 7: Request final code review**

Dispatch a fresh reviewer with the specification, this plan, all branch
commits, focused test output, full-suite comparison, and stale-name search.
Fix any correctness issues with a new failing test before production changes.

