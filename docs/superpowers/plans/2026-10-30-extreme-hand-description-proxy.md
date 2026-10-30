# Extreme-Hand Description Proxy Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic, one-decision descriptive-proxy fallback that lets eligible extreme hands reuse authored bidding routes without exposing synthetic cards to controls, simulation, axioms, or later decisions.

**Architecture:** Build the feature in four layers: pure extreme-shape normalization, an exact legal-hand/K–R proxy search, typed context views with audited aggregate-strength access, and a side-effect-free decision-attempt wrapper that retries only genuine TD outcomes. Keep the proxy mechanism profile-independent; the Daqiush Jacoby/Texas family supplies the first authored routes that deliberately defer eligible extreme hands to it.

**Tech Stack:** Python 3 dataclasses, existing Gible BSL/profile runtime, exact dynamic programming with `functools.lru_cache`, `unittest`/pytest-compatible backend tests.

---

## Scope and file map

This is one subsystem with four internal boundaries, not four independently shippable features. Do not enable the retry path until the context-strength audit and real-hand safety tests are complete.

**Create:**

- `backend/engine/extreme_shape.py` — trigger classification, iterative named-shape normalization, canonical tied-path deduplication, termination invariants.
- `backend/engine/descriptive_proxy.py` — legal proxy-hand search, ranking, cache, immutable proxy/evidence/diagnostic types.
- `backend/engine/decision_attempt.py` — side-effect-free attempt result and orchestration helpers; no profile-specific rules.
- `backend/tests/test_extreme_shape.py` — exhaustive shape properties and canonical path fixtures.
- `backend/tests/test_descriptive_proxy_search.py` — exact search, Q/J restrictions, ranking, cache determinism.
- `backend/tests/test_described_hand_context.py` — masked-length facade, aggregate-strength routing, actual-holding safety.
- `backend/tests/test_descriptive_proxy_decision.py` — retry gating, state isolation, projection, failures, later-auction use.
- `backend/tests/test_profile_strength_access.py` — source audit preventing aggregate strength from bypassing `ctx.strength`.

**Modify:**

- `backend/engine/context.py` — add `StrengthView`, `DescribedHandView`, explicit actual/proxy fields, and compatibility facade.
- `backend/engine/candidate_generation.py` — accept an attempt/context factory instead of constructing real-hand-only contexts internally.
- `backend/engine/decision.py` — select against the attempt context without committing state.
- `backend/engine/selector.py` — split attempt from commit/final checks; perform one guarded proxy retry after eligible TD only.
- `backend/engine/axioms.py` — narrowly accept `DescriptiveProxyEvidence` only in strength/shape sufficiency checks; keep control-sensitive checks actual.
- `backend/engine/explanation.py` — serialize proxy provenance.
- `backend/engine/trace.py` — store optional serializable proxy diagnostic on the chosen decision trace.
- `backend/engine/public_evidence.py` — derive explicit partner maximum lengths used to freeze Q/J.
- `backend/partnership_profiles/**/*.py` — migrate aggregate `ctx.hand.hcp` / K–R reads to `ctx.strength`; leave holdings and suit quality actual.
- `backend/partnership_profiles/daqiush_2over1/gadgets/jacoby_major_transfers/gadget.bsl.py` — shared five-plus-major entry and explicit extreme deferral.
- `backend/partnership_profiles/daqiush_2over1/gadgets/south_african_texas/gadget.bsl.py` — shared five-plus-major entry and explicit extreme deferral.
- `backend/tests/test_daqiush_jacoby.py`, `backend/tests/test_daqiush_texas.py` — preserve 5/6/7-card behavior and add extreme end-to-end routes.
- `docs/18_block_scout.md` — document diagnostic provenance exposed to TD/IV Scanner reports.

**Do not reuse:** `hand_quality.shapely_description_proxy`. It is an older route-specific effective-point helper, not a legal proxy hand, not pure K–R, and must remain behaviorally unchanged until callers are deliberately migrated.

**Workspace safety:** the main workspace may contain unrelated user edits in Daqiush gadgets. Re-read `git status` before each task, edit only the named hunks, never amend a commit that may belong to the user, and commit this feature in new linear commits.

---

## Chunk 1: Pure shape normalization and exact proxy construction

### Task 1: Classify and canonically normalize eligible extreme shapes

**Files:**
- Create: `backend/engine/extreme_shape.py`
- Create: `backend/tests/test_extreme_shape.py`

- [ ] **Step 1: Write failing classification and representative-path tests**

Add tests for `8-3-2-0`, `8-2-2-1`, `8-3-1-1`, `7-4-1-1`, `6-5-1-1`, `6-6-1-0`, ordinary `7-3-3-0`, and the iterative `10-3-0-0` case. Use named S/H/D/C mappings and assert trigger class, protected suits, final shape, ordered transitions, and cumulative donations/receipts.

```python
def test_ten_three_zero_zero_normalizes_iteratively():
    result = normalize_extreme_shape({'S': 10, 'H': 3, 'D': 0, 'C': 0})
    assert result[0].final_lengths == (7, 3, 3, 0)
    assert result[0].steps == ((0, 2), (0, 2), (0, 2))
    assert result[0].donations == (3, 0, 0, 0)
    assert result[0].receipts == (0, 0, 3, 0)
```

- [ ] **Step 2: Run the focused test and verify it fails**

Run: `python -m pytest backend/tests/test_extreme_shape.py -q`

Expected: FAIL because `engine.extreme_shape` does not exist.

- [ ] **Step 3: Implement immutable classification and normalization types**

Implement these public interfaces:

```python
SUITS = ('S', 'H', 'D', 'C')

@dataclass(frozen=True)
class ExtremeShape:
    trigger: Literal['eight_plus_single', 'eleven_plus_two_suit']
    protected_qj_suits: tuple[str, ...]

@dataclass(frozen=True)
class NormalizedShape:
    trigger: str
    initial_lengths: tuple[int, int, int, int]
    final_lengths: tuple[int, int, int, int]
    steps: tuple[tuple[int, int], ...]
    donations: tuple[int, int, int, int]
    receipts: tuple[int, int, int, int]

def classify_extreme_shape(lengths: Mapping[str, int]) -> ExtremeShape | None: ...
def normalize_extreme_shape(lengths: Mapping[str, int]) -> tuple[NormalizedShape, ...]: ...
```

At every state, reclassify; enumerate all tied current longest donors and tied current third-longest receivers; reject donor==receiver; stop when the state is no longer eligible; deduplicate by `(final_lengths, donations, receipts)`; retain the lexicographically smallest complete transition sequence.

- [ ] **Step 4: Add an exhaustive partition property test**

Enumerate all ordered quadruples of nonnegative integers summing to 13. For every eligible state and every emitted transition assert:

```python
before_variant - after_variant == 2 * (donor_length - receiver_length - 1)
assert before_variant - after_variant >= 2
assert len(path.steps) <= 63
assert classify_extreme_shape(dict(zip(SUITS, path.final_lengths))) is None
```

Also run normalization with reversed internal frontier order through a private test hook and assert byte-for-byte identical serialized results.

- [ ] **Step 5: Run tests and commit**

Run: `python -m pytest backend/tests/test_extreme_shape.py -q`

Expected: PASS.

```powershell
git add backend/engine/extreme_shape.py backend/tests/test_extreme_shape.py
git commit -m "feat: normalize extreme hand shapes"
```

### Task 2: Build an exact legal proxy-hand dynamic program

**Files:**
- Create: `backend/engine/descriptive_proxy.py`
- Create: `backend/tests/test_descriptive_proxy_search.py`
- Reference: `backend/engine/hand_quality.py`
- Reference: `backend/engine/cards.py`

- [ ] **Step 1: Write failing tests for legal proxies and frozen honors**

Cover: A/K never move; Q/J only change in protected suits; real actor length<=2 freezes Q/J; public partner max<=2 freezes Q/J; proxy has 13 unique cards; pure K–R delta <=0.15; no-solution result is explicit.

```python
result = find_descriptive_proxy(
    Hand.parse('SAKQ98765HKQ2D32C-'),
    (normalization,),
    partner_short_suits=frozenset(),
)
assert result is not None
assert result.evaluation_hand.ace_count() == real.ace_count()
assert abs(result.proxy_kr - result.real_kr) <= .15
assert sum(result.evaluation_hand.length(s) for s in 'SHDC') == 13
```

- [ ] **Step 2: Run the focused tests and verify they fail**

Run: `python -m pytest backend/tests/test_descriptive_proxy_search.py -q`

Expected: FAIL because the search API is absent.

- [ ] **Step 3: Implement proxy result and evidence types**

```python
@dataclass(frozen=True)
class DescriptiveProxyEvidence:
    hcp: int
    kr_points: float
    lengths: tuple[int, int, int, int]
    donations_by_suit: tuple[int, int, int, int]
    receipts_by_suit: tuple[int, int, int, int]

@dataclass(frozen=True)
class ProxySearchResult:
    evaluation_hand: Hand
    evidence: DescriptiveProxyEvidence
    real_kr: float
    proxy_kr: float
    changed_card_count: int
    preserved_qj_count: int
    changed_qj_locations: tuple[str, ...]
    normalization: NormalizedShape

def find_descriptive_proxy(
    actual_hand: Hand,
    normalizations: tuple[NormalizedShape, ...],
    partner_short_suits: frozenset[str],
) -> ProxySearchResult | None: ...
```

The public API receives every canonical normalization branch and returns the
single globally best legal proxy. Auction logic must never be run once per
branch. Add a fixture in which a later canonical branch beats the first branch
and assert that it is returned.

- [ ] **Step 4: Implement and test exact per-suit holding enumeration**

For each suit, enumerate legal holdings of the target length after applying fixed A/K and allowed Q/J membership. Record HCP, K–R suit twentieths, real-card intersection, preserved Q/J, and canonical holding. Test each restriction independently, including exact `(suit, rank)` equality for every real A/K rather than merely comparing ace/king counts.

- [ ] **Step 5: Run the per-suit tests**

Run: `python -m pytest backend/tests/test_descriptive_proxy_search.py -q -k "holding or honor"`

Expected: PASS.

- [ ] **Step 6: Implement and test four-suit DP combination**

Combine four suit tables by accumulated HCP/K–R/card count; add whole-hand K–R shape adjustment using the existing pure K–R implementation; retain only totals within three twentieths of actual K–R. Test a hand with exactly one feasible DP total and a hand with none.

Use the exact objective tuple:

```python
(
    13 - intersection_count,
    abs(proxy_kr_twentieths - real_kr_twentieths),
    -preserved_qj_count,
    canonical_hand_key,
)
```

Do not add a random search, visit budget, tolerance relaxation, or synthetic `X` ranks.

- [ ] **Step 7: Add global branch ranking and determinism tests**

Construct small fixtures with multiple feasible proxies across one and multiple normalization branches. Assert changed cards wins before K–R delta, K–R wins before preserved Q/J, and canonical S/H/D/C holdings break the final tie. Instrument the caller and prove only that one globally selected proxy reaches auction evaluation.

- [ ] **Step 8: Add a versioned global-result cache without caching calls**

Cache only the globally ranked search result by canonical actual hand, trigger/protected suits, the complete canonical normalization set and move data, public partner-short suits, and `PROXY_ALGORITHM_VERSION`. Add cache-clear/cache-info test hooks. Assert cold and warm results serialize identically.

- [ ] **Step 9: Run tests and commit**

Run: `python -m pytest backend/tests/test_extreme_shape.py backend/tests/test_descriptive_proxy_search.py -q`

Expected: PASS.

```powershell
git add backend/engine/descriptive_proxy.py backend/tests/test_descriptive_proxy_search.py
git commit -m "feat: search exact descriptive hand proxies"
```

---

## Chunk 2: Typed hand views, strength routing, and safety audit

### Task 3: Add the masked description view and authoritative strength interface

**Files:**
- Modify: `backend/engine/context.py`
- Modify: `backend/engine/candidate_generation.py`
- Modify: `backend/engine/decision.py`
- Create: `backend/tests/test_described_hand_context.py`

- [ ] **Step 1: Write failing context-boundary tests**

Assert in descriptive mode:

- `ctx.hand.length(suit)` returns actual length minus donations, never receipts;
- all four explicit description lengths may total below 13;
- `ctx.hand.holding`, `contains_rank`, `honor_count`, raw suit strings, controls, keycards, and stoppers use the actual hand;
- `ctx.actual_hand` is the real `Hand`;
- `ctx.proxy_evaluation` is available only as explicit diagnostic input;
- `ctx.strength` returns proxy HCP/K–R/delta;
- `ctx.hand_quality` and `ctx.honor_texture` remain actual holding-quality records.

- [ ] **Step 2: Run the focused test and verify it fails**

Run: `python -m pytest backend/tests/test_described_hand_context.py -q`

Expected: FAIL because the view and strength fields do not exist.

- [ ] **Step 3: Implement immutable context view types**

```python
@dataclass(frozen=True)
class StrengthView:
    hcp: int
    kr_points: float
    kr_delta: float

@dataclass(frozen=True)
class DescribedHandView:
    actual: Hand
    strength: StrengthView
    descriptive_lengths: Mapping[str, int]
    unexpressed_fillers_by_suit: Mapping[str, int]

    @property
    def hcp(self) -> int: return self.strength.hcp
    @property
    def unexpressed_filler_count(self) -> int:
        return sum(self.unexpressed_fillers_by_suit.values())
    def length(self, suit: str) -> int: ...
    def holding(self, suit: str) -> str: return self.actual.holding(suit)
```

Implement the full typed compatibility surface explicitly: `spades`, `hearts`,
`diamonds`, `clubs`, `suits`, `holding`, `contains_rank`, `honor_count`,
`ace_count`, `king_count`, `keycard_count`, and `balanced`. Every raw-card or
honor method delegates to `actual`; `balanced` is computed only from all four
descriptive lengths. Do not use `__getattr__`, because an unreviewed future
`Hand` method must fail visibly rather than silently cross the safety boundary.

Extend `BridgeContext` with `actual_hand`, `description`, `proxy_evaluation`, `strength`, and `attempt_mode`. Provide one `BridgeContext.from_trace(...)` path that constructs either a real or descriptive context; do not monkey-patch or temporarily replace a global hand.

- [ ] **Step 4: Thread an explicit context factory through candidate generation and policy selection**

Change `generate_candidates`, `_condition_passes`, `_candidate`, private-route helpers, and `choose_candidate` to receive an immutable `AttemptContext`/factory. Every candidate/policy `BridgeContext` in the same attempt must expose the same real hand, description, and strength.

- [ ] **Step 5: Prove receiver additions cannot unlock calls**

Use an instrumented applicability predicate that reads every suit length. Give a proxy whose receiver grows from three to four in the legal evaluation hand and assert the context still reports the masked real-minus-donations length and does not create a Stayman/support/second-suit candidate.

- [ ] **Step 6: Run tests and commit**

Run: `python -m pytest backend/tests/test_described_hand_context.py backend/tests/test_daqiush_jacoby.py backend/tests/test_daqiush_texas.py -q`

Expected: PASS; existing decisions unchanged because production still creates real-mode contexts only.

```powershell
git add backend/engine/context.py backend/engine/candidate_generation.py backend/engine/decision.py backend/tests/test_described_hand_context.py
git commit -m "refactor: separate descriptive and actual hand views"
```

### Task 4: Restrict axiom evidence and lock down actual-hand helpers

**Files:**
- Create: `backend/tests/test_profile_strength_access.py`
- Modify: `backend/engine/bsl.py`
- Modify: `backend/engine/axioms.py`
- Modify as identified by audit: control-sensitive helpers under `backend/engine/`

- [ ] **Step 1: Write failing axiom-signature and actual-hand safety tests**

Permit `alternative_description` in exactly these functions:

```python
ALTERNATIVE_DESCRIPTION_CONSUMERS = {
    'certified_game_strength',
    'certified_shape_invitation',
}
```

The source/signature audit must fail if any other axiom helper accepts or reads
`DescriptiveProxyEvidence`. Runtime tests must show forcing, Pass semantics,
control quality, stoppers, keycards, cue eligibility, invitation response, and
contract evaluation use the actual hand only.

- [ ] **Step 2: Run the focused safety tests and verify they fail**

Run: `python -m pytest backend/tests/test_profile_strength_access.py backend/tests/test_axioms.py -q`

Expected: FAIL because typed alternative evidence is not wired yet.

- [ ] **Step 3: Add the narrow axiom API**

Add optional `alternative_description: DescriptiveProxyEvidence | None` to
`evaluate_axioms`, but pass it onward only to `certified_game_strength` and
`certified_shape_invitation`. Their HCP/K–R/shape sufficiency reads may use the
alternative values; all invitation range consistency, actual `hand.hcp`,
control, forcing, Pass, keycard, and legality logic remains unchanged.

- [ ] **Step 4: Audit BSL/engine control-sensitive helper calls**

Change every helper classified as control-sensitive to receive
`ctx.actual_hand` explicitly. Add runtime spies around void, stopper, keycard,
cue, and DDS entry points and assert the object identity is the original hand.

- [ ] **Step 5: Run tests and commit only explicit paths/hunks**

Run: `python -m pytest backend/tests/test_profile_strength_access.py backend/tests/test_axioms.py backend/tests/test_axiom_integration.py -q`

Expected: PASS.

Stage only the changed engine files and exact new test file; use `git add -p`
for any file containing unrelated user changes.

```powershell
git commit -m "feat: restrict descriptive evidence to strength axioms"
```

### Task 5: Migrate every profile aggregate-strength read

**Files:**
- Modify: `backend/partnership_profiles/daqiush_2over1/**/*.py`
- Modify: `backend/partnership_profiles/meow_2over1/**/*.py`
- Modify: `backend/test_profiles/**/*.py` if the audit finds aggregate reads
- Modify: `backend/tests/test_profile_strength_access.py`

- [ ] **Step 1: Add an AST-based failing source audit**

Parse loaded profile Python/BSL sources with `ast` and reject aggregate
bypasses even when quote style, `.get()`, or formatting differs. The visitor
must recognize `ctx.hand.hcp`, subscript access to aggregate keys on
`ctx.hand_quality`, and `.get('kr_points'/'kr_delta')` on that mapping; include
one fixture for every syntax:

```python
FORBIDDEN = (
    'ctx.hand.hcp',
    "ctx.hand_quality['kr_points']",
    'ctx.hand_quality["kr_points"]',
    "ctx.hand_quality['kr_delta']",
    'ctx.hand_quality["kr_delta"]',
)
```

Allow actual holding/shape reads and explicitly documented test fixtures. Also add a runtime test showing proxy aggregate strength changes an applicability result while actual suit quality does not change.

- [ ] **Step 2: Run the audit and capture the complete failure list**

Run: `python -m pytest backend/tests/test_profile_strength_access.py -q`

Expected: FAIL and list every source location requiring migration. Save the list in the test failure output; do not silently exclude legacy profiles.

- [ ] **Step 3: Migrate Daqiush files in small groups**

Migrate one gadget/policy file at a time. After each file, run its focused
tests plus the AST audit. For the two currently dirty Daqiush gadget files,
stage only feature-owned hunks with `git add -p`; never stage the entire file.

- [ ] **Step 4: Commit the Daqiush migration**

Run:

```powershell
$daqiushTests = Get-ChildItem backend/tests/test_daqiush_*.py | ForEach-Object FullName
python -m pytest backend/tests/test_profile_strength_access.py @daqiushTests -q
```

Expected: PASS. Commit only the reviewed Daqiush hunks and the audit test.

```powershell
git commit -m "refactor: use context strength in Daqiush profile"
```

- [ ] **Step 5: Migrate Meow and test-profile files in small groups**

Replace HCP/K–R aggregate comparisons with:

```python
ctx.strength.hcp
ctx.strength.kr_points
ctx.strength.kr_delta
```

Keep these actual:

```python
ctx.actual_hand.holding(...)
ctx.actual_hand.contains_rank(...)
ctx.actual_hand.keycard_count(...)
ctx.hand_quality['suit_evaluations'][...]
ctx.honor_texture
```

For predicates combining length and strength, use `ctx.hand.length(...)` for the descriptive applicability shape and `ctx.strength` for aggregate points. For control/stoppers/keycards/shortages, use `ctx.actual_hand` explicitly. Run the relevant profile tests after each group.

- [ ] **Step 6: Commit the Meow/test-profile migration**

Run: `python -m pytest backend/tests/test_profile_strength_access.py backend/tests -q`

Expected: PASS.

```powershell
git commit -m "refactor: use context strength in remaining profiles"
```

- [ ] **Step 7: Run the final source audit and full backend tests**

Run:

```powershell
python -m pytest backend/tests/test_profile_strength_access.py backend/tests/test_described_hand_context.py backend/tests/test_axioms.py backend/tests/test_axiom_integration.py -q
python -m pytest backend/tests -q
```

Expected: all PASS.

---

## Chunk 3: Side-effect-free decision retry and diagnostics

### Task 6: Extract a non-committing decision attempt

**Files:**
- Create: `backend/engine/decision_attempt.py`
- Modify: `backend/engine/selector.py`
- Modify: `backend/engine/memory.py` only if a copy/serialization helper is needed
- Create: `backend/tests/test_descriptive_proxy_decision.py`

- [ ] **Step 1: Characterize the existing real decision pipeline**

Before refactoring, add tests for: authored candidate, derived candidate, purpose-controlled candidate, ambiguous meaning, axiom rejection, simulation selector, private-route memory, and selected-purpose creation. Assert call, diagnostics, trace state, candidate ordering, and memory.

- [ ] **Step 2: Run characterization tests**

Run: `python -m pytest backend/tests/test_descriptive_proxy_decision.py -q`

Expected: PASS for real-mode characterization and FAIL only for the not-yet-created attempt API tests.

- [ ] **Step 3: Introduce explicit attempt outcomes**

```python
@dataclass(frozen=True)
class AttemptResult:
    mode: Literal['real', 'descriptive_proxy']
    selected: CallCandidate | None
    ordered: tuple[CallCandidate, ...]
    policy_origin: dict[str, Any] | None
    decision_context: BridgeContext | None
    block_kind: str | None
    block_reason: str | None
    rejection_codes: frozenset[str]
    memory_after_purpose_resolution: SeatMemory
    resolved_purpose: PurposeResolution | None
    trace: AuctionTrace
    candidates: tuple[CallCandidate, ...]

    @property
    def retryable_td(self) -> bool:
        return self.selected is None and retry_allowed(self)
```

Extract the current pipeline so an attempt starts from `SeatMemory.coerce(private_memory)` and a fresh `replay_auction(...)` trace, and returns proposed state without mutating caller-owned objects. Tag nonretryable blocks separately: illegal prior auction, purpose error, forcing/keycard/universal obligation, simulation failure, illegal projected call.

`AttemptResult` is deliberately not a public `BidDecision`: its memory has only
purpose-resolution changes, never selected-candidate route/purpose completion.
The outer commit wrapper is the sole owner of `remember_candidate`,
`complete_purpose`, `remember_selected_purpose`, and construction of the final
`BidDecision.private_memory`.

- [ ] **Step 4: Move commit logic to the outer wrapper**

Only after a selected attempt succeeds should the wrapper apply `remember_candidate`, `complete_purpose`, `remember_selected_purpose`, selected trace effects, and return memory. Failed real-attempt memory/diagnostics must not leak into a successful proxy result; retain only a concise `real_td_reason` in proxy provenance.

- [ ] **Step 5: Test state isolation**

Create a failed real attempt that would propose a purpose/route mutation before blocking, then a successful proxy attempt. Assert the final memory contains exactly one selected route/purpose, the failed trace is not the final trace, and repeating the decision with the same inputs yields identical memory and diagnostics.

- [ ] **Step 6: Run full backend tests and commit**

Run: `python -m pytest backend/tests -q`

Expected: all PASS with no proxy retry enabled yet.

```powershell
git add backend/engine/decision_attempt.py backend/engine/selector.py backend/engine/memory.py backend/tests/test_descriptive_proxy_decision.py
git commit -m "refactor: isolate bidding decision attempts"
```

### Task 7: Enable one guarded proxy retry after genuine TD

**Files:**
- Modify: `backend/engine/selector.py`
- Modify: `backend/engine/public_evidence.py`
- Modify: `backend/engine/trace.py`
- Modify: `backend/engine/explanation.py`
- Modify: `backend/engine/block_report_viewer.py` if report serialization is explicit there
- Modify: `backend/engine/block_scout.py`
- Modify: `backend/tests/test_descriptive_proxy_decision.py`
- Modify: `backend/tests/test_block_scout.py`
- Modify: `backend/tests/test_block_report_viewer.py`

- [ ] **Step 1: Write failing retry-gate and failure-mode tests**

Cover all of these:

1. ordinary hand never invokes proxy search;
2. successful real decision wins without proxy search;
3. no candidate and candidate ambiguity may retry; no-compliant-call retries only when its entire rejection-code set is strength/shape-sufficiency-only;
4. purpose/forcing/keycard/universal errors never retry;
5. `attempt_mode='descriptive_proxy'` cannot recurse;
6. no legal proxy, masked no-candidate, proxy ambiguity, illegal projection, and final actual-axiom rejection produce distinct TD diagnostics;
7. a later-auction authored route can be rescued.

- [ ] **Step 2: Run the focused tests and verify failures**

Run: `python -m pytest backend/tests/test_descriptive_proxy_decision.py -q`

Expected: FAIL on retry behavior.

- [ ] **Step 3: Derive public partner-short suits**

Add a helper that scans public applied meanings for the actor's partner and returns only suits with an explicit `max_lengths[suit] <= 2`. Do not infer shortage from absence, shape arithmetic, simulation constraints, or private knowledge. Test seat orientation and multiple meanings using the tightest public maximum.

- [ ] **Step 4: Define the exact retry-code table**

```python
RETRYABLE_BLOCK_KINDS = {'no_candidate', 'candidate_ambiguity'}
RETRYABLE_AXIOM_REJECTIONS = {
    'SIGNOFF_REQUIRED', 'INVITATION_REQUIRED', 'GAME_REQUIRED'
}
NONRETRYABLE_AXIOM_CODES = {
    'FORCING_PASS', 'GAME_FORCE_UNFULFILLED', 'PASS_SEMANTICS',
    'INVITATION_RESPONSE_REQUIRED', 'ACCEPTANCE_BELOW_GAME',
    'ILLEGAL_CALL', 'CONFLICTING_TAGS', 'INVALID_AXIOM_CONFIGURATION',
    'UNKNOWN_INVITATION_RANGE', 'HAND_OUTSIDE_SHOWN_RANGE'
}
```

A `no_compliant_call` is retryable only when it has at least one rejection,
every rejection is in `RETRYABLE_AXIOM_REJECTIONS`, and neither errors nor
active obligations contain any nonretryable code/category. Add one test per
code family.

- [ ] **Step 5: Split descriptive and actual-only pipeline stages**

Implement and test this explicit boundary:

| Stage | View |
|---|---|
| authored/private-route applicability | described shape + `ctx.strength`, actual holdings |
| derived semantics and ordinary priority/policy choice | same described context |
| keycard restrictions and purpose obligation validation | actual hand |
| legality and projected authored meaning | actual auction/hand |
| DDS/simulation selectors, cue gate, signoff override | actual hand |
| final universal axioms | actual hand, plus restricted alternative description only for the two sufficiency helpers |
| memory/trace commit | selected attempt only |

Move the current selector sections into named helpers reflecting this table;
do not leave proxy-sensitive stages interleaved in one large function.

- [ ] **Step 6: Implement the guarded retry flow**

Pseudocode for the outer wrapper:

```python
real = run_decision_attempt(mode='real', actual_hand=hand, ...)
if real.selected is not None or not real.retryable_td:
    return commit(real)
shape = classify_extreme_shape(real_lengths(hand))
if shape is None:
    return block(real)
proxy = find_descriptive_proxy(
    hand, normalize_extreme_shape(real_lengths(hand)), partner_short_suits)
if proxy is None:
    return proxy_failure('no_legal_proxy', real)
attempt = run_decision_attempt(
    mode='descriptive_proxy', actual_hand=hand,
    description=proxy.evidence, proxy_evaluation=proxy.evaluation_hand, ...)
return finalize_with_actual_hand(attempt) if attempt.selected else proxy_failure(...)
```

Use only the globally best legal proxy from search; call `run_decision_attempt`
at most twice per `choose_bid` (one real, one proxy) and never try a worse proxy
because the best proxy's auction meaning is inconvenient. Project its selected
authored call/meaning/private purpose, then run the actual-only stages in the
table above. Pass only `DescriptiveProxyEvidence` to the two explicitly allowed
shape/strength sufficiency helpers.

- [ ] **Step 7: Add versioned diagnostic and failure provenance**

Implement serializable `ProxyDiagnostic` with every field in the design spec
for a selected call. For unsuccessful searches/attempts implement a separate
`ProxyFailureDiagnostic` containing schema version, trigger, real shape,
canonical normalizations tried, best proxy fields when one existed, failure
code/message, and real-TD reason. Type the trace field as
`ProxyDiagnostic | ProxyFailureDiagnostic | None`; expose it in `explain()` and
TD/IV Scanner JSON. Never append either type to public meanings/state records.
Extend `block_scout` with a bounded `proxy_cases` collection for completed
auctions whose chosen decision has `ProxyDiagnostic`; keep ordinary completed
auctions out of this collection. The report viewer renders these separately
from TD cases. Add scanner tests proving a rescued completion is retained and
that existing blocked/summary counts do not change.

- [ ] **Step 8: Add cold/warm and serialization tests**

Run the same rescued decision before and after warming the proxy cache. Assert identical call, selected authored origin, memory, normalization steps, selected proxy holding, explanation JSON, and diagnostics.

- [ ] **Step 9: Run focused tests and commit**

Run:

```powershell
python -m pytest backend/tests/test_descriptive_proxy_decision.py backend/tests/test_block_scout.py backend/tests/test_block_report_viewer.py -q
```

Expected: PASS.

```powershell
git add backend/engine/selector.py backend/engine/public_evidence.py backend/engine/trace.py backend/engine/explanation.py backend/engine/block_scout.py backend/engine/block_report_viewer.py backend/tests/test_descriptive_proxy_decision.py backend/tests/test_block_scout.py backend/tests/test_block_report_viewer.py
git commit -m "feat: retry TD decisions with descriptive proxies"
```

---

## Chunk 4: Daqiush route family integration and end-to-end verification

### Task 8: Make Jacoby/Texas share five-plus-major structural entry behavior

**Files:**
- Modify: `backend/partnership_profiles/daqiush_2over1/gadgets/jacoby_major_transfers/gadget.bsl.py`
- Modify: `backend/partnership_profiles/daqiush_2over1/gadgets/south_african_texas/gadget.bsl.py`
- Modify: `backend/tests/test_daqiush_jacoby.py`
- Modify: `backend/tests/test_daqiush_texas.py`

- [ ] **Step 1: Preserve the current dirty-worktree versions**

Run `git diff --` for both gadget files and save the output outside the repository or in the implementation notes. Rebase edits onto the current file contents; do not restore, overwrite, or format unrelated user changes.

- [ ] **Step 2: Write failing shared-family tests**

Assert:

- every normal five-, six-, and seven-card existing fixture retains its current call;
- route-family structural eligibility is `>=5` for both majors;
- eligible 8+ single-suit and 11+ two-suit route applicability returns `DEFER_TO_DESCRIPTION`; candidate generation omits that individual call and records the deferred origin, so the overall real attempt reaches retryable TD only when no other real route succeeds;
- the proxy attempt sees the shortened donated lengths and selects the authored Jacoby/Texas route;
- hearts/spades are symmetric;
- receiver-side third-suit additions cannot enable another route.

- [ ] **Step 3: Run focused tests and verify failures**

Run: `python -m pytest backend/tests/test_daqiush_jacoby.py backend/tests/test_daqiush_texas.py -q`

Expected: existing tests PASS; new extreme tests FAIL.

- [ ] **Step 4: Add a typed tri-state applicability result**

Define:

```python
class ApplicabilityResult(Enum):
    MATCH = 'match'
    NO_MATCH = 'no_match'
    DEFER_TO_DESCRIPTION = 'defer_to_description'

@dataclass(frozen=True)
class CandidateGenerationResult:
    candidates: tuple[CallCandidate, ...]
    deferred_origins: tuple[dict[str, Any], ...]
```

`_condition_outcome` maps `None` to `NO_MATCH` for compatibility with existing
callable predicates, converts literal booleans and this enum, and raises
`TypeError` for every other arbitrary truthy/falsy object. Candidate generation includes
only `MATCH`, omits `NO_MATCH`, and omits plus records the call origin for
`DEFER_TO_DESCRIPTION`. A real attempt with another successful authored route
returns that real route and never constructs a proxy.

Expose attempt mode and extreme classification through engine context, not by duplicating trigger rules in each gadget. The route predicate should behave as follows:

```python
if ctx.attempt_mode == 'real' and ctx.extreme_description_eligible:
    return ApplicabilityResult.DEFER_TO_DESCRIPTION
return ctx.hand.length(target_major) >= 5 and existing_strength_and_route_tests(ctx)
```

Keep all existing 5/6/7 route-priority logic. Do not give the enum public meaning or expose it as a call. Add tests that `None` remains an ordinary no-match, `bool(DEFER_TO_DESCRIPTION)` is never consulted, and a defer alone becomes ordinary no-candidate TD metadata rather than a new decision block kind.

- [ ] **Step 5: Add the reported 8-3-2-0 fourteen-HCP end-to-end fixtures**

For heart and spade analogues, assert the previously TD `1NT-Pass` decision now equals the route selected by the best legal seven-card description, records the real 8-3-2-0 shape and descriptive 7-3-3-0 shape, and leaves actual void/control/keycard evidence unchanged.

- [ ] **Step 6: Add 6-5/7-4 generic two-suit fixtures**

Assert both use the same engine proxy mechanism, not new hand-coded special branches, and that a later auction can independently create a fresh ephemeral proxy without retaining the earlier synthetic hand.

- [ ] **Step 7: Run focused and profile regression tests**

Run:

```powershell
python -m pytest backend/tests/test_daqiush_jacoby.py backend/tests/test_daqiush_texas.py backend/tests/test_daqiush_owner_routes.py backend/tests/test_daqiush_resample_followups.py -q
```

Expected: PASS.

- [ ] **Step 8: Commit without absorbing unrelated changes**

Stage only reviewed hunks with `git add -p` if the gadget files still contain unrelated user edits.

```powershell
git commit -m "feat: describe extreme hands through major routes"
```

### Task 9: Full verification, scanner documentation, and cleanup

**Files:**
- Modify: `docs/18_block_scout.md`
- Modify: tests above as needed for final coverage
- Optional modify: `backend/engine/hand_quality.py` only to deprecate/document the old route-specific helper; do not silently redirect it

- [ ] **Step 1: Add the named design-spec verification matrix**

Create this executable mapping and ensure every named method exists:

| Spec | Exact test method |
|---|---|
| 1 | `test_ordinary_hand_never_searches_proxy` |
| 2 | `test_real_decision_suppresses_available_proxy` |
| 3 | `test_eight_card_heart_and_spade_routes_use_best_proxy` |
| 4 | `test_ten_three_zero_zero_is_one_iterative_proxy_attempt` |
| 5 | `test_five_plus_route_family_preserves_five_six_seven_and_defers_extreme` |
| 6 | `test_six_five_and_seven_four_use_generic_proxy_path` |
| 7 | `test_aces_and_kings_keep_exact_suit_locations` |
| 8 | `test_qj_changes_only_in_unfrozen_protected_suits` |
| 9 | `test_selected_proxy_is_legal_and_within_three_twentieths` |
| 10 | `test_global_objective_and_cache_warming_are_deterministic` |
| 11 | `test_receiver_growth_cannot_unlock_length_route` |
| 12 | `test_controls_stoppers_keycards_and_dds_use_actual_hand` |
| 13 | `test_strength_is_proxy_but_suit_quality_is_actual` |
| 14 | `test_failed_real_attempt_state_is_discarded_and_proxy_commits_once` |
| 15 | `test_later_auction_authored_route_can_be_rescued` |
| 16 | `test_proxy_failure_codes_cover_no_result_illegal_projection_and_ambiguity` |
| 17 | full `python -m pytest backend/tests -q` run |

Items 1–16 require executable assertions, not documentation-only references.

- [ ] **Step 2: Run all focused tests twice, cold and warm**

Run:

```powershell
python -m pytest backend/tests/test_extreme_shape.py backend/tests/test_descriptive_proxy_search.py backend/tests/test_described_hand_context.py backend/tests/test_descriptive_proxy_decision.py backend/tests/test_profile_strength_access.py backend/tests/test_daqiush_jacoby.py backend/tests/test_daqiush_texas.py -q
python -m pytest backend/tests/test_extreme_shape.py backend/tests/test_descriptive_proxy_search.py backend/tests/test_descriptive_proxy_decision.py -q
```

Expected: all PASS both times with identical deterministic assertions.

- [ ] **Step 3: Run the full backend regression suite**

Run: `python -m pytest backend/tests -q`

Expected: all PASS; record exact pass count and duration in the implementation handoff.

- [ ] **Step 4: Run a representative IV Scanner/TD report smoke test**

First add `backend/tests/fixtures/extreme_proxy_scan_constraints.json`:

```json
{
  "s": {
    "min_hcp": 14,
    "max_hcp": 14,
    "min_lengths": {"hearts": 8},
    "max_lengths": {"spades": 3, "diamonds": 3, "clubs": 3}
  }
}
```

Then run from `backend/`:

```powershell
..\.venv\Scripts\python.exe -m engine.block_scout --profile daqiush_2over1 --dealer n --opening 1NT --attempts 5000 --max-seconds 120 --max-cases 50 --seed 83020 --constraints tests/fixtures/extreme_proxy_scan_constraints.json --output ../reports/block_scans/extreme-proxy-seed83020.json
..\.venv\Scripts\python.exe -m engine.block_report_viewer ../reports/block_scans/extreme-proxy-seed83020.json
```

Expected: at least one matching auction; rescued cases serialize
`proxy_diagnostic`; any remaining TD proxy failures serialize a distinct
failure code; viewer output is
`reports/block_scans/extreme-proxy-seed83020.html`. If this exact seed produces
zero matches after implementation, choose and document one replacement seed
once, add it as a deterministic regression fixture, and update this plan/doc
before claiming verification.

- [ ] **Step 5: Update documentation**

Document:

- eligibility rules and iterative shortening;
- why receiver additions are hidden;
- pure K–R tolerance 0.15;
- real-hand safety boundary;
- diagnostic fields and scanner interpretation;
- cache version/determinism;
- how an authored route opts into `defer_to_description`;
- the distinction from `shapely_description_proxy`.

- [ ] **Step 6: Check diff scope and commit**

Run:

```powershell
git status --short
git diff --check
git diff --stat
```

Expected: no whitespace errors; no unrelated scanner/profile changes staged.

Stage explicit paths only, including the new fixture and the exact modified
test files. Run `git diff --cached --name-only` and verify the pre-existing
`backend/tests/test_daqiush_resample_followups.py` is absent unless a reviewed
feature-owned hunk was intentionally added.

```powershell
git commit -m "docs: explain extreme hand proxy decisions"
```

- [ ] **Step 7: Final verification evidence**

Run: `python -m pytest backend/tests -q`

Expected: PASS. Report the exact command/output, the final commit list, any pre-existing unstaged user files left untouched, and whether the branch is ahead of its remote. Do not claim completion from an earlier test run.
