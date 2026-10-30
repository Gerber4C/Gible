# Ordinary RKCB Continuations Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Complete Daqiush ordinary RKCB with useful-void answers, ambiguity-safe decisions, the conditional `5S -> 5NT` relay, and direct high-answer grand-slam continuations without changing Voidwood, NFRKCB, or quantitative 4NT.

**Architecture:** Keep public RKCB state in replayed `keycard_context` records and private commitment in the asker's serializable `Purpose`. A focused `rkcb_continuation.py` module owns state parsing, useful-void classification, legal continuation exposure, deterministic safety decisions, and the narrow DDS sampling hooks; the Daqiush gadget authors wildcard calls and public meanings, while `selector.py` generates authored candidates before the Purpose filters them.

**Tech Stack:** Python 3, Python-BSL profile definitions, `unittest`, existing deal sampler/DDS contract evaluator, immutable dataclasses.

**Approved specification:** `docs/superpowers/specs/2026-10-30-ordinary-rkcb-continuations-design.md`

**Workspace guardrail:** Work directly in the main workspace as explicitly requested. Before every commit, stage only files named by that task. Preserve the pre-existing uncommitted changes in `five_card_major_inquiry`, `jacoby_major_transfers`, `one_notrump_invitations`, and `test_daqiush_one_notrump_expansion.py`.

---

## File map

- Create `backend/engine/rkcb_continuation.py`: pure ordinary-RKCB frame parsing, useful-void classification, answer interpretation, legality, and relay/high-answer geometry. It must reject every method other than `rkcb_1430`.
- Create `backend/engine/rkcb_simulation.py`: partner-hand category filtering and narrow DDS comparisons for ambiguous answers, rescue, and 6/7 decisions.
- Modify `backend/engine/memory.py`: add serializable RKCB Purpose stage and relay intent while retaining compatibility with old saved memories.
- Modify `backend/engine/purpose_axiom.py`: turn `keycard_slam` into a multi-turn state machine that filters already-generated authored candidates.
- Modify `backend/engine/selector.py`: generate and resolve authored candidates before Purpose selection; retain a narrow compatibility fallback for existing `response_plan` purposes.
- Modify `backend/partnership_profiles/daqiush_2over1/gadgets/confirmed_keycard/gadget.bsl.py`: replace per-prefix answer continuations with wildcard ordinary-RKCB answer/relay/invitation calls and public state transitions.
- Modify the Daqiush gadgets that feed an ordinary ask, initially `backend/partnership_profiles/daqiush_2over1/gadgets/jacoby_major_transfers/gadget.bsl.py`: publish `minimum_length` on every natural suit meaning that guarantees at least four cards, so useful-void exclusion is replayable rather than guessed from action names.
- Create `backend/tests/test_rkcb_continuation.py`: pure state, legality, ambiguity, useful-void, relay, and high-answer policy tests.
- Expand `backend/tests/test_daqiush_keycard.py`: profile/replay integration tests.
- Expand `backend/tests/test_purpose_axiom.py`: multi-turn private Purpose and selector-order tests.
- Modify `docs/15_daqiush_slam.md`: document implemented ordinary RKCB behavior and its separation from Voidwood/NFRKCB.

## Chunk 1: State and authored response surface

### Task 1: Characterize current ordinary RKCB and add the public frame reader

**Files:**
- Create: `backend/engine/rkcb_continuation.py`
- Create: `backend/tests/test_rkcb_continuation.py`
- Test: `backend/tests/test_daqiush_keycard.py`

- [ ] **Step 1: Write failing characterization tests**

Add tests that construct traces containing several `keycard_context` records and assert that only the most recent ordinary record is active:

```python
def test_latest_ordinary_frame_ignores_stale_pending_record(self):
    trace = AuctionTrace()
    add_context(trace, method='rkcb_1430', status='pending_answer', trump='H')
    add_context(trace, method='rkcb_1430', status='answered', trump='H')
    frame = ordinary_rkcb_frame(trace)
    self.assertEqual((frame.method, frame.status, frame.trump),
                     ('rkcb_1430', 'answered', 'H'))

def test_nonordinary_method_is_never_read_as_ordinary_rkcb(self):
    add_context(trace, method='voidwood', status='pending_answer', trump='H')
    self.assertIsNone(ordinary_rkcb_frame(trace))
```

Retain the four existing 1430 answer tests as a baseline.

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```powershell
$env:PYTHONPATH='backend'; python -m unittest tests.test_rkcb_continuation tests.test_daqiush_keycard -v
```

Expected: import failure for `engine.rkcb_continuation`; existing four 1430 tests still pass.

- [ ] **Step 3: Implement the immutable frame reader**

Create these public types/functions in `rkcb_continuation.py`:

```python
@dataclass(frozen=True)
class OrdinaryRKCBFrame:
    trump: str
    status: str
    answer_category: str | None = None
    keycard_counts: tuple[int, ...] = ()
    trump_queen: bool | None = None
    useful_void: str | None = None
    useful_void_category: str | None = None
    not_required_kings: tuple[str, ...] = ()
    disrupted_reason: str | None = None

def ordinary_rkcb_frame(trace) -> OrdinaryRKCBFrame | None:
    records = [r for r in trace.current_state_records
               if r.key == 'keycard_context']
    if not records or records[-1].attribute('method') != 'rkcb_1430':
        return None
    return _frame_from_record(records[-1])
```

Validate trump/status/category values while parsing. Completed/disrupted frames remain inspectable but are not active.

- [ ] **Step 4: Run the focused tests and verify GREEN**

Run the command from Step 2. Expected: all tests pass.

- [ ] **Step 5: Commit the frame reader**

```powershell
git add backend/engine/rkcb_continuation.py backend/tests/test_rkcb_continuation.py backend/tests/test_daqiush_keycard.py
git commit -m "feat: add ordinary rkcb public frame reader"
```

### Task 2: Implement useful-void classification and high answers

**Files:**
- Modify: `backend/engine/rkcb_continuation.py`
- Modify: `backend/partnership_profiles/daqiush_2over1/gadgets/confirmed_keycard/gadget.bsl.py`
- Modify: `backend/partnership_profiles/daqiush_2over1/gadgets/jacoby_major_transfers/gadget.bsl.py`
- Modify: `backend/tests/test_rkcb_continuation.py`
- Modify: `backend/tests/test_daqiush_keycard.py`

- [ ] **Step 1: Write failing unit and integration tests**

Cover:

1. a void outside trumps and partner's natural 4+ suit is useful;
2. a void in partner's naturally shown 4+ suit is not useful;
3. artificial/control calls do not exclude a void;
4. two useful voids choose the lowest in `CDHS` order;
5. `5NT` shows `0/2/4 + useful void` without naming its suit;
6. six of the lower void shows `1/3 + exact void`;
7. six of trumps shows `1/3 + a higher void`;
8. an unusable void falls back to the ordinary answer;
9. every answer writes a new `keycard_context(status='answered')` record and retains `method='rkcb_1430'`;
10. hand-free `replay_auction()` reconstructs one unique wildcard meaning and expected context record for every ordinary/high answer.
11. a real Daqiush `natural_second_minor` replay publishes
    `minimum_length=4`, causing a void in that suit to be non-useful.

Use a small trace builder rather than full profile calls for pure tests. In integration tests use a Texas ask and at least one minor-trump ask.

- [ ] **Step 2: Run tests and verify RED**

```powershell
$env:PYTHONPATH='backend'; python -m unittest tests.test_rkcb_continuation tests.test_daqiush_keycard -v
```

Expected: useful-void and high-answer assertions fail; the old test that expected a blocked void must be replaced, not retained.

- [ ] **Step 3: Add pure classification helpers**

Implement:

```python
def public_minimum_length(meaning: dict, suit: str) -> int:
    lengths = meaning.get('suit_length_minimums', {}) or {}
    if suit in lengths:
        return int(lengths[suit])
    if meaning.get('target_suit') == suit:
        return int(meaning.get('minimum_length', 0) or 0)
    return 0

def naturally_shown_long_suits(trace, partner: str) -> frozenset[str]:
    result = set()
    for entry in trace.applied_meanings:
        meaning = entry.get('public_meaning', {})
        call = entry.get('call', '')
        if (entry.get('seat') == partner and len(call) == 2
                and call[0] in '1234567' and call[1] in 'CDHS'
                and 'natural' in meaning.get('nature_labels', ())
                and public_minimum_length(meaning, call[1]) >= 4):
            result.add(call[1])
    return frozenset(result)

def useful_voids(trace, responder: str, hand: Hand, trump: str) -> tuple[str, ...]:
    excluded = naturally_shown_long_suits(trace, partner_of(responder))
    return tuple(s for s in 'CDHS'
                 if s != trump and hand.length(s) == 0 and s not in excluded)

def ordinary_response(hand: Hand, trump: str, voids: tuple[str, ...]) -> RKCBResponse:
    count = hand.keycard_count(trump)
    if voids:
        void = voids[0]
        if count in (0, 2, 4):
            return RKCBResponse('5N', (0, 2, 4), void_category='unspecified')
        if bid_rank('6' + void) < bid_rank('6' + trump):
            return RKCBResponse('6' + void, (1, 3), void_suit=void)
        return RKCBResponse('6' + trump, (1, 3), void_category='higher_than_trump')
    count = hand.keycard_count(trump)
    queen = hand.contains_rank(trump, 'Q')
    if count in (1, 4):
        return RKCBResponse('5C', (1, 4))
    if count in (0, 3):
        return RKCBResponse('5D', (0, 3))
    if count == 2 and not queen:
        return RKCBResponse('5H', (2,), trump_queen=False)
    return RKCBResponse('5S', (2,), trump_queen=True)
```

Do not expose the private selected void on a `5NT` or six-trump answer.

- [ ] **Step 4: Refactor the BSL gadget to wildcard state-driven answers**

Keep the existing ask declarations. Replace the per-ask answer loop with one wildcard answer family per trump/call:

```python
answer.when = '*'
answer.requires = lambda ctx, t=trump: ordinary_frame_pending(ctx, t)
answer.applies = lambda ctx, t=trump, b=bid: response_matches(ctx, t, b)
```

Each answer must publish `keycard_counts`, optional `trump_queen`, the permitted void category, and a fresh `keycard_context` effect with status `answered`. Remove the historical placement loop only after replacement continuations exist in later tasks.

- [ ] **Step 5: Run focused profile tests**

```powershell
$env:PYTHONPATH='backend'; python -m unittest tests.test_rkcb_continuation tests.test_daqiush_keycard tests.test_daqiush_resample_followups -v
```

Expected: all pass; four ordinary answers remain unchanged.

- [ ] **Step 6: Commit useful-void answers**

```powershell
git add backend/engine/rkcb_continuation.py backend/partnership_profiles/daqiush_2over1/gadgets/confirmed_keycard/gadget.bsl.py backend/partnership_profiles/daqiush_2over1/gadgets/jacoby_major_transfers/gadget.bsl.py backend/tests/test_rkcb_continuation.py backend/tests/test_daqiush_keycard.py
git commit -m "feat: add useful void rkcb answers"
```

## Chunk 2: Private continuation state and the 5S relay

### Task 3: Extend Purpose serialization into a multi-turn RKCB state machine

**Files:**
- Modify: `backend/engine/memory.py`
- Modify: `backend/engine/purpose_axiom.py`
- Modify: `backend/tests/test_purpose_axiom.py`

- [ ] **Step 1: Write failing round-trip and transition tests**

Test legacy dictionaries without new fields, every new stage, replacement without duplication, enemy disruption, and completion only on terminal placement:

```python
purpose = Purpose(kind='keycard_slam', owner='s', source_index=6,
                  source_call='4N', trump='H', own_keycards=3,
                  owns_trump_queen=True,
                  rkcb_stage='await_relay_completion',
                  relay_intent='show_lowest_king')
self.assertEqual(Purpose.from_dict(purpose.to_dict()), purpose)
```

- [ ] **Step 2: Run tests and verify RED**

```powershell
$env:PYTHONPATH='backend'; python -m unittest tests.test_purpose_axiom -v
```

- [ ] **Step 3: Add compatible private fields**

Add to `Purpose`:

```python
rkcb_stage: str | None = None
relay_intent: str | None = None
answer_category: str | None = None
not_required_kings: tuple[str, ...] = ()
```

Extend `PurposeResolution` with
`filtered_candidates: tuple[CallCandidate, ...] | None = None`; a stage handler
returns only candidates already present in that tuple, except for the documented
legacy `response_plan` compatibility path.

`from_dict` must accept missing fields and convert JSON lists to tuples. New 4NT asks start at `await_keycard_answer`; old saved `keycard_slam` purposes with no stage are normalized to that stage at resolution time.

- [ ] **Step 4: Replace fixed-offset resolution with stage-based resolution**

Split `_keycard_slam` into stage handlers. The handler must use the latest ordinary frame and never infer private counts from partner cards:

```python
if stage == 'await_keycard_answer':
    result = choose_after_answer(auction, trace, hand, purpose, frame, candidates)
    return replace(result, purpose=replace(
        purpose, rkcb_stage='choose_continuation',
        answer_category=frame.answer_category))
if stage == 'choose_continuation':
    return choose_continuation(auction, trace, hand, purpose, frame, candidates)
if stage == 'await_relay_completion':
    return observe_relay_completion(frame)
if stage == 'place_after_5nt':
    return choose_king_or_small_slam(auction, hand, purpose, candidates)
```

`choose_continuation` either selects a terminal placement, leaves the Purpose
active while a direct high-answer grand invitation is pending, or changes the
stage to `await_relay_completion` when the relay is selected. The responder,
not the asker, selects forced `5NT` from public status
`relay_pending`. On the asker's next turn, `observe_relay_completion` requires
public status `relay_completed`, advances the same Purpose to
`place_after_5nt`, and selects among authored king/small-slam candidates.
Retain `response_plan` compatibility and structured `PURPOSE_UNRESOLVED` errors.

- [ ] **Step 5: Verify GREEN and commit**

```powershell
$env:PYTHONPATH='backend'; python -m unittest tests.test_purpose_axiom -v
git add backend/engine/memory.py backend/engine/purpose_axiom.py backend/tests/test_purpose_axiom.py
git commit -m "refactor: make rkcb purpose multi turn"
```

### Task 4: Generate authored candidates before Purpose filtering

**Files:**
- Modify: `backend/engine/selector.py`
- Modify: `backend/engine/purpose_axiom.py`
- Modify: `backend/tests/test_purpose_axiom.py`

- [ ] **Step 1: Write failing ordering tests**

Create a tiny profile with two authored continuations after an answer. Assert
that the Purpose selects the authored candidate and preserves its public
meaning/effects. Add two same-call `5S` fixtures with mutually exclusive
public predicates and assert replay selects one before ambiguity handling.
Also assert that an old `response_plan` still works when its exact planned
call has no authored candidate.

- [ ] **Step 2: Run tests and verify RED**

```powershell
$env:PYTHONPATH='backend'; python -m unittest tests.test_purpose_axiom -v
```

- [ ] **Step 3: Reorder the selector pipeline**

Change `resolve_purpose` to accept the resolved candidate pool:

```python
generated = generate_candidates(profile, auction, hand, trace,
                                active_environment, actor_memory)
generated = _apply_keycard_restrictions(auction, hand, generated, trace)
purpose = resolve_purpose(auction, trace, actor_memory, generated)
purpose_visible = purpose.filtered_candidates or generated
candidates = _resolve_same_call_meanings(purpose_visible, trace)
```

Rules:

- explicit profile calls are visible to Purpose filtering;
- RKCB Purpose may only select an exposed authored call;
- the legacy `response_plan` may synthesize its exact legal call when absent;
- mutually exclusive public predicates separate replay meanings first;
- an active Purpose may filter otherwise-equivalent same-call candidates
  before unresolved same-call ambiguity is reported;
- axioms still evaluate the final candidate set;
- no-purpose paths retain byte-for-byte decision ordering where practical.

- [ ] **Step 4: Run selector and purpose tests**

```powershell
$env:PYTHONPATH='backend'; python -m unittest tests.test_purpose_axiom tests.test_route_analysis tests.test_daqiush_owner_routes -v
```

- [ ] **Step 5: Commit the ordering change**

```powershell
git add backend/engine/selector.py backend/engine/purpose_axiom.py backend/tests/test_purpose_axiom.py
git commit -m "refactor: filter authored calls through private purposes"
```

### Task 5: Implement queen-ask precedence and the 5S relay

**Files:**
- Modify: `backend/engine/rkcb_continuation.py`
- Create: `backend/engine/rkcb_simulation.py`
- Modify: `backend/engine/purpose_axiom.py`
- Modify: `backend/partnership_profiles/daqiush_2over1/gadgets/confirmed_keycard/gadget.bsl.py`
- Modify: `backend/tests/test_rkcb_continuation.py`
- Modify: `backend/tests/test_purpose_axiom.py`

- [ ] **Step 1: Write the relay decision table as failing tests**

Cover:

- after `5D` with hearts agreed, `5S` is structurally a queen ask even when
  the asker privately owns the queen;
- only frames where public auction geometry does not reserve `5S` for the
  queen ask may expose the relay;
- rescue relay is forbidden while legal five-trump remains;
- rescue relay is exposed only when five-trump is unavailable;
- forced `5NT` advances the public frame from `relay_pending` to `relay_completed`;
- rescue intent Passes after forced 5NT;
- grand intent shows the asker's lowest legal side king;
- no king returns to legal six-trump; no safe terminal call TDs;
- enemy action and illegal forced 5NT disrupt both public frame and Purpose.

- [ ] **Step 2: Run tests and verify RED**

```powershell
$env:PYTHONPATH='backend'; python -m unittest tests.test_rkcb_continuation tests.test_purpose_axiom -v
```

- [ ] **Step 3: Implement pure precedence/legality helpers**

Add:

```python
def five_spade_role(auction, frame) -> Literal['queen_ask', 'relay', 'unavailable']
def five_trump_available(auction, trump) -> bool
def lowest_showable_side_king(hand, trump, auction, denied=()) -> str | None
def relay_terminal_call(auction, hand, trump) -> str | None
```

Queen-ask geometry wins regardless of the asker's private queen holding. A
relay result includes `relay_intent` privately but only `relay_to_5nt`
publicly. Queen-ask response mechanics are not invented in this task: a
structural queen ask keeps `status='answered'`, writes
`continuation_stage='queen_ask'`, and produces a precise
`QUEEN_ASK_CONTINUATION_UNAUTHORED` TD on the next turn until its response
table is separately specified.

- [ ] **Step 4: Author wildcard queen/relay/forced-response calls**

In the BSL gadget expose:

- structural queen asks with one replay-safe public meaning and pending status;
- `5S` relay only when the frame says it is not a queen ask;
- exactly one forced `5NT` from `relay_pending`;
- king-show and six-trump terminal meanings from `relay_completed`.

The queen and relay `5S` specifications have mutually exclusive public
requirements so hand-free replay sees exactly one meaning. Every call writes
a new `keycard_context` status. Add hand-free replay tests for queen `5S`,
relay `5S`, and forced `5NT`. Do not update Voidwood or create NFRKCB aliases.

- [ ] **Step 5: Add deterministic and sampled rescue selection**

Use deterministic legality first. Only if both 5NT and forced six-trump are viable, call `rkcb_simulation.compare_rescue_routes`, a narrow adapter that:

1. uses `sample_process_hands(profile, auction, trace, hand, partner,
   extra_filter=answer_category_filter(frame, purpose.trump))`;
2. compares 5NT and six-trump through `compare_contract_targets`;
3. chooses the relay only when 5NT is not worse;
4. returns a typed unavailable result on DDS/sampling failure so the Purpose TDs unless a safe deterministic call exists.

Tests must inject fake deals/solver results; they must not require a local DDS installation.

- [ ] **Step 6: Run focused tests and commit**

```powershell
$env:PYTHONPATH='backend'; python -m unittest tests.test_rkcb_continuation tests.test_purpose_axiom tests.test_daqiush_keycard -v
git add backend/engine/rkcb_continuation.py backend/engine/rkcb_simulation.py backend/engine/purpose_axiom.py backend/partnership_profiles/daqiush_2over1/gadgets/confirmed_keycard/gadget.bsl.py backend/tests/test_rkcb_continuation.py backend/tests/test_purpose_axiom.py backend/tests/test_daqiush_keycard.py
git commit -m "feat: add rkcb queen precedence and five notrump relay"
```

## Chunk 3: Ambiguous answers and grand invitations

### Task 6: Sample ambiguous `0/2/4` and `1/3` answer mixtures

**Files:**
- Modify: `backend/engine/rkcb_continuation.py`
- Modify: `backend/engine/rkcb_simulation.py`
- Modify: `backend/engine/purpose_axiom.py`
- Modify: `backend/tests/test_rkcb_continuation.py`
- Modify: `backend/tests/test_purpose_axiom.py`

- [ ] **Step 1: Write failing mathematical-pruning tests**

Assert that impossible counts are removed using the asker's own keycards, but no preferred count turns a genuinely ambiguous high answer into a false exact count. Test a mixture whose fake DDS outcome differs between interpretations.

- [ ] **Step 2: Run tests and verify RED**

```powershell
$env:PYTHONPATH='backend'; python -m unittest tests.test_rkcb_continuation tests.test_purpose_axiom -v
```

- [ ] **Step 3: Implement category filters and mixed evaluation**

Implement:

```python
def possible_partner_counts(frame, own_keycards) -> tuple[int, ...]:
    return tuple(count for count in frame.keycard_counts
                 if 0 <= count <= 5 - own_keycards)

def answer_category_filter(frame, trump):
    def accepts(hand):
        return (hand.keycard_count(trump) in frame.keycard_counts
                and void_category_matches(hand, frame, trump))
    return accepts
```

Sample partner hands satisfying the entire category and evaluate exposed continuation contracts over the complete mixture. Keep exact deterministic outcomes when pruning leaves one safe result. If samples/DDS are unavailable and more than one result remains materially possible, return structured TD rather than using `preferred_keycard_count`.

The injected mixture fixture contains one partner hand with 0 and one with 2
keycards under a `5NT` category. Its fake solver makes 5NT on both layouts and
six-trump only on the 2-keycard layout; the expected combined choice is 5NT.
A second fixture with one mathematically possible count chooses
deterministically and asserts that the solver was not called.

- [ ] **Step 4: Run focused tests and commit**

```powershell
$env:PYTHONPATH='backend'; python -m unittest tests.test_rkcb_continuation tests.test_purpose_axiom -v
git add backend/engine/rkcb_continuation.py backend/engine/rkcb_simulation.py backend/engine/purpose_axiom.py backend/tests/test_rkcb_continuation.py backend/tests/test_purpose_axiom.py
git commit -m "feat: resolve ambiguous rkcb answers by sampling"
```

### Task 7: Implement direct high-answer grand invitations

**Files:**
- Modify: `backend/engine/rkcb_continuation.py`
- Modify: `backend/engine/rkcb_simulation.py`
- Modify: `backend/engine/purpose_axiom.py`
- Modify: `backend/partnership_profiles/daqiush_2over1/gadgets/confirmed_keycard/gadget.bsl.py`
- Modify: `backend/tests/test_rkcb_continuation.py`
- Modify: `backend/tests/test_purpose_axiom.py`
- Modify: `backend/tests/test_daqiush_keycard.py`

- [ ] **Step 1: Add a failing table of high-answer continuations**

Cover all specification cases:

- Pass over playable 5NT/six-level answer is placement, not invitation;
- non-Pass six-level continuation is a grand invite;
- seven-level call is final;
- skipped legally available lower side suits enter `not_required_kings`;
- higher suits remain unknown, not required;
- responder accepts with seven-trump, rejects with six-trump, or Passes only over playable six-level trump/NT when six-trump is illegal;
- lowest higher unknown K may counterinvite only below six-trump;
- no safe rejection TDs;
- after counterinvite the asker gets exactly six/seven-trump candidates and sampling selects one;
- no second counterinvite;
- a skipped king never becomes an acceptance requirement.

Keep the specification's closed status enum. The invitation keeps
`status='answered'` and writes `continuation_stage='grand_invitation'`,
`invitation_call`, `not_required_kings`, and `counterinvite_count=0`; a
counterinvite keeps `status='answered'`, changes
`continuation_stage='counterinvited'`, and sets `counterinvite_count=1`.
Either active stage may then move status to `completed` or `disrupted`. A
frame with `counterinvite_count=1` exposes only final six/seven-trump calls.

The asker's private Purpose remains in `rkcb_stage='choose_continuation'`
through the initial high answer and invitation. When it next sees public
`continuation_stage='counterinvited'`, that same stage selects exactly six or
seven trumps and completes. The responding seat needs no private Purpose; it
acts from the public frame. A partner-selected terminal call completes the
public frame, so stale private memory cannot reopen it.

- [ ] **Step 2: Run tests and verify RED**

```powershell
$env:PYTHONPATH='backend'; python -m unittest tests.test_rkcb_continuation tests.test_purpose_axiom tests.test_daqiush_keycard -v
```

- [ ] **Step 3: Implement public invitation geometry**

Add pure functions:

```python
def skipped_lower_kings(answer: str, invitation: str, trump: str,
                        legal_at_answer: Iterable[str]) -> tuple[str, ...]:
    return tuple(call[1] for call in legal_at_answer
                 if call[0] == '6' and call[1] in 'CDHS'
                 and call[1] != trump
                 and bid_rank(answer) < bid_rank(call) < bid_rank(invitation))

def lowest_counterinvite_king(hand, frame, auction) -> str | None:
    calls = [f'6{suit}' for suit in 'CDHS'
             if suit != frame.trump
             and suit not in frame.not_required_kings
             and hand.contains_rank(suit, 'K')
             and is_call_legal(auction, f'6{suit}')
             and bid_rank(f'6{suit}') < bid_rank(f'6{frame.trump}')]
    return min(calls, key=bid_rank) if calls else None
```

The functions operate only on ordinary frames. Calls below the answer do not
count as skipped. Higher suits remain unknown requirements and enter neither a
required set nor `not_required_kings` without later evidence. A counterinvite
is suppressed unless six-trump remains a legal rejection.

- [ ] **Step 4: Author the generic high-answer call surface**

Expose wildcard Pass, legal six-level invitations, seven-level final calls,
six/seven-trump responses, and at most one counterinvite. Each call's effects
carry the exact status/stage attributes above; descriptions call suit bids
“grand invitation/counter-invitation”, never specific king asks. Add hand-free
replay tests for Pass placement, invitation, counterinvite, rejection,
acceptance, seven-level final placement, and disruption.

- [ ] **Step 5: Add the narrow 6/7 simulation decision**

Implement `rkcb_simulation.compare_grand_routes`. Reuse sampled partner hands
and the existing contract evaluator, comparing only six/seven of agreed trump.
A deterministic rejection may avoid DDS; acceptance or an ambiguous choice
without evidence TDs.

- [ ] **Step 6: Run focused tests and commit**

```powershell
$env:PYTHONPATH='backend'; python -m unittest tests.test_rkcb_continuation tests.test_purpose_axiom tests.test_daqiush_keycard -v
git add backend/engine/rkcb_continuation.py backend/engine/rkcb_simulation.py backend/engine/purpose_axiom.py backend/partnership_profiles/daqiush_2over1/gadgets/confirmed_keycard/gadget.bsl.py backend/tests/test_rkcb_continuation.py backend/tests/test_purpose_axiom.py backend/tests/test_daqiush_keycard.py
git commit -m "feat: add rkcb grand invitation continuations"
```

## Chunk 4: Method isolation, documentation, and verification

### Task 8: Prove method isolation and document the feature

**Files:**
- Modify: `backend/tests/test_rkcb_continuation.py`
- Modify: `backend/tests/test_daqiush_keycard.py`
- Modify: `backend/tests/test_purpose_axiom.py`
- Modify: `docs/15_daqiush_slam.md`

- [ ] **Step 1: Add failing cross-method regression tests if absent**

Test that the generic ordinary engine ignores:

- `method='voidwood'`;
- a quantitative 4NT with no keycard frame;
- `method='nfrkcb_offer'` and `method='nfrkcb_answered'` fixtures;
- completed/disrupted ordinary frames;
- explicit profile meanings that conflict with a generic continuation.

- [ ] **Step 2: Run the new cross-method tests and verify RED**

```powershell
$env:PYTHONPATH='backend'; python -m unittest tests.test_rkcb_continuation tests.test_daqiush_keycard tests.test_voidwood tests.test_purpose_axiom -v
```

Expected: completed/disrupted-frame and explicit-conflict fixtures fail if
generic continuation logic still leaks. The explicit-conflict fixture must
eventually select and replay the profile call whose action is
`explicit_wins`; the generic candidate must be absent.

- [ ] **Step 3: Add the exact isolation guards**

In `rkcb_continuation.py`, return inactive for every method other than
`rkcb_1430` and statuses `completed`/`disrupted`. In `selector.py`, retain the
explicit profile candidate whenever its call conflicts with a generic RKCB
candidate. Do not add method aliases.

- [ ] **Step 4: Rerun the cross-method suite and verify GREEN**

```powershell
$env:PYTHONPATH='backend'; python -m unittest tests.test_rkcb_continuation tests.test_daqiush_keycard tests.test_voidwood tests.test_purpose_axiom -v
```

Expected: all named tests pass and hand-free replay selects `explicit_wins`.

- [ ] **Step 5: Update slam documentation**

Document the implemented response table, useful-void definition, queen-ask precedence, conditional 5S relay, ambiguous-category sampling, high-answer grand invitations, TD behavior, and the explicit boundary excluding Voidwood/NFRKCB/quantitative 4NT.

- [ ] **Step 6: Run the complete backend suite**

```powershell
$env:PYTHONPATH='backend'; python -m unittest discover -s backend/tests -p "test_*.py" -v
```

Expected: all tests pass. Record the exact count and duration in the completion report.

- [ ] **Step 7: Run repository checks**

```powershell
git diff --check
git status --short
```

Expected: no whitespace errors; only task files plus the user's pre-existing dirty files are present.

- [ ] **Step 8: Commit docs and final isolation tests**

```powershell
git add backend/tests/test_rkcb_continuation.py backend/tests/test_daqiush_keycard.py backend/tests/test_purpose_axiom.py docs/15_daqiush_slam.md
git commit -m "docs: describe ordinary rkcb continuations"
```

- [ ] **Step 9: Request code review**

Use `superpowers:requesting-code-review` with the approved specification, this plan, the commit range, and the exact test evidence. Address findings through `superpowers:receiving-code-review`, rerun the focused and full suites, then use `superpowers:verification-before-completion` before claiming completion.

