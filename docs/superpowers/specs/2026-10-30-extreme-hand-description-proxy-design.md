# Extreme-Hand Description Proxy Design

## Goal

Gible must be able to route an extreme hand through an existing bidding
agreement without requiring a separately authored branch for every unusual
shape. The mechanism is a general engine fallback, not a special case for the
Daqiush 1NT structure.

The real hand always gets the first opportunity to produce a unique acceptable
call. Only when the ordinary decision finishes as TD, including an unresolved
candidate ambiguity, may the engine construct a descriptive proxy and retry
the current decision. The proxy exists for one decision only. Contract
evaluation, controls, simulation, later calls, and all concealed-card work use
the real hand unless a later decision independently needs another proxy.

## Eligible extreme shapes

Sort the four real suit lengths from longest to shortest while retaining suit
identity. A hand is eligible in exactly these cases:

- **eight-plus single suit**: the longest suit has at least eight cards and the
  second-longest suit has at most three;
- **eleven-plus two suit**: the two longest suits each have at least four cards
  and their combined length is at least eleven.

The two-suit classification wins if a hand could otherwise match both labels.
Ordinary hands never invoke this mechanism.

Define `protected_qj_suits` independently from length-order tie breaking:

- for an eight-plus single suit, it contains only the unique eight-plus suit;
- for an eleven-plus two suit, it contains exactly the two suits of length four
  or more whose combined length triggered the classification;
- every real actor suit of length two or fewer is Q/J-frozen regardless of
  rank order or ties.

Thus an 8-2-2-1 hand never arbitrarily chooses one two-card suit as a second
long suit. An 8-3-1-1 hand may change Q/J only in the eight-card suit; the
three-card suit is neither short nor a protected long suit and remains fixed.

Normalize the descriptive shape iteratively:

1. classify the current shape with the same eight-plus-single and eleven-plus-
   two-suit definitions;
2. while it remains extreme, move one card from a current longest suit to a
   current third-longest suit;
3. if either rank is tied, branch over the Cartesian product of tied donors and
   receivers, excluding a pair that names the same suit;
4. stop a branch as soon as its shape is no longer extreme;
5. deduplicate by final named shape plus cumulative per-suit donation and
   receipt counts. If several step sequences reach the same key, retain the
   lexicographically smallest transition sequence, encoding every transition
   as `(donor_suit_index, receiver_suit_index)` in S/H/D/C order;
6. let normal proxy ranking select the least distorted legal hand.

The operation terminates by the integer variant `sum(length ** 2)`. In an
eligible eight-plus single suit, the donor is at least eight and the third suit
is at most three. In an eligible eleven-plus two suit, the two long suits use
at least eleven cards, so the third suit is at most two and a longest donor is
at least six. The same bounds apply after every reclassification that remains
eligible. Therefore every selected donor length `a` and receiver length `b`
satisfy `a - b >= 2`, and one move decreases the variant by
`2 * (a - b - 1)`, at least two. With thirteen cards the variant is at most 169
and at least 43, so every branch has at most 63 moves. It is shape
normalization inside proxy construction, not recursive `choose_bid`
execution. Representative paths are:

- `10-3-0-0 -> 9-3-1-0 -> 8-3-2-0 -> 7-3-3-0`;
- `8-3-2-0 -> 7-3-3-0`;
- `7-4-1-1 -> 6-4-2-1`;
- `6-5-1-1 -> 5-5-2-1`.

Every moved card makes the final evaluation proxy a legal thirteen-card hand
and contributes to its K–R score. Receiver-side additions remain masked when
matching suit-dependent calls. They must not make a new third-suit agreement,
transfer, Stayman action, natural suit, support promise, or other length-
dependent call available.

## Proxy-hand search

The proxy is a legal synthetic thirteen-card hand used only to find a known
route. Represent a hand as a set of thirteen `(suit, rank)` cards. Search
observes these constraints:

1. Every ace and king remains in its real suit.
2. In `protected_qj_suits`, queen/jack membership may independently be
   retained, removed, or added unless the suit is frozen by public partner-
   shortage evidence. With two protected suits, moving a queen or jack is
   represented by its removal from one and addition to the other. Outside
   `protected_qj_suits`, real queen/jack membership is fixed.
3. Every real actor suit of length two or fewer has frozen Q/J membership.
   Public partner-shortage evidence means an explicit public maximum length of
   two cards in that suit. Such a suit freezes its real Q/J membership: proxy
   search may neither add, remove, nor move a Q/J there.
4. After fixing A/K/Q/J membership, choose T-through-2 cards to fill each
   target suit length. A suit cannot contain duplicate ranks, and the proxy
   contains thirteen distinct cards.
5. Pure Kaplan–Rubens points must differ from the real hand by at most 0.15.
6. Search is an exact finite dynamic program over suit holdings, not a random
   or budget-limited walk. It returns the globally best legal proxy or proves
   that none lies within tolerance.

Rank eligible proxies lexicographically by:

1. number of changed cards;
2. absolute K–R difference;
3. number of real queen/jack locations preserved, descending;
4. a stable canonical holding key in S/H/D/C and A-to-2 order.

Only the first proxy is used. Exact ties therefore remain reproducible and do
not introduce random bidding decisions.

Define changed-card count exactly as
`13 - len(real_card_set & proxy_card_set)`. Thus moving a physical rank between
suits, replacing a spot with an honor, or adding/removing Q/J is measured by
the number of real card positions no longer preserved. Define preserved Q/J
locations as the count of real Q/J cards present with the same suit and rank in
the proxy. These formulas are shared by search, diagnostics, and tests.

Precompute every legal suit holding for the requested target length and fixed
A/K/Q/J membership. Each holding records K–R twentieths, HCP, intersection
count, preserved Q/J count, and canonical text. Combine the four suits with a
dynamic program keyed by accumulated K–R twentieths and card count. Whole-hand
shape adjustment is then applied, and only totals within three twentieths
(0.15) of the real K–R survive. For each state retain the lexicographically
best objective tuple above. This avoids an arbitrary search ceiling.

## Two views of the proxy

The search result contains three explicit immutable objects:

- **actual hand**: the original legal `Hand`, used for holdings, controls,
  shortages, stoppers, keycards, legality, simulation, and final evaluation;
- **evaluation proxy**: the complete legal synthetic `Hand`, used only to
  establish proxy K–R and proxy HCP;
- **description view**: a typed `DescribedHandView` used only while evaluating
  call applicability. It exposes proxy HCP/K–R, reports each suit as its real
  length minus the cumulative number of cards donated by that suit, and hides
  every receiver-side addition. It exposes the actual holding for every suit,
  `unexpressed_fillers_by_suit`, and the total `unexpressed_filler_count`.

The description lengths intentionally total thirteen minus the number of
receiver-side additions, with that many explicit unexpressed fillers. They are
not a `Hand` and must never enter card validation or any helper that infers one
suit as thirteen minus the others. Every route-shape query reads all four
explicit `length(suit)` values. This makes receiver-suit masking an interface
guarantee rather than a candidate filter based on incomplete public meanings.

During proxy candidate generation, `BridgeContext.hand` is a compatibility
facade over `DescribedHandView`: `.length()` returns descriptive values, while
`.holding()` and raw-card access return the actual hand. The context also
exposes `actual_hand`, `description`, and `proxy_evaluation` explicitly.

Aggregate strength has one authoritative interface, `ctx.strength`, containing
`hcp`, `kr_points`, and `kr_delta`. It reads proxy aggregate values during a
descriptive attempt and real values otherwise. Applicability code must not
recompute HCP or K–R from holdings. Before enabling proxy retry, audit and move
every aggregate-strength predicate to this interface. The compatibility
facade's `.hcp` delegates to `ctx.strength.hcp` only for existing predicates
during migration.

Suit-specific quality and every holding-specific predicate use the actual
hand. Synthetic Q/J positions prove that the descriptive aggregate strength is
plausible; they never become suit-quality evidence. `ctx.hand_quality` remains
the actual quality record, while `ctx.strength` is the only descriptive
aggregate. Any helper classified as control-sensitive receives `actual_hand`;
this includes shortages, controls, stoppers, keycards, cue eligibility, and
simulation. An implementation audit must move such helpers to the explicit
actual-hand interface before proxy retry is enabled.

The engine must expose the distinction explicitly; it must not temporarily
replace a global hand and hope every caller restores it. `DescribedHandView`
does not expose evaluation-proxy holdings, so an applicability predicate cannot
accidentally turn a synthetic Q/J into an actual stopper or control.

## Decision flow

Split selection into a side-effect-free `DecisionAttempt` and a committing
wrapper. A `DecisionAttempt` receives an immutable auction, trace snapshot, and
copy of private memory, and returns candidates, diagnostics, and a proposed
memory value. It cannot mutate caller-owned memory or trace. Only the attempt
whose decision is returned commits its proposed memory and trace effects.

For every `choose_bid` call:

1. Run the existing candidate generation, purpose handling, derived semantics,
   ambiguity resolution, axioms, and selectors with the real hand.
2. Return the real-hand decision whenever it produces one unique acceptable
   call.
3. If the result would be TD because no unique acceptable call survived, test
   whether the real hand has an eligible extreme shape. Prior-auction
   illegality remains diagnostic; the proxy cannot override a purpose error,
   forcing obligation, keycard obligation, or other universal-axiom error.
4. Build or retrieve the ranked proxy search result for the real hand and the
   auction's public short-suit evidence.
5. Retry candidate generation and derived semantics through a guarded proxy
   `DecisionAttempt`. An explicit attempt mode (`real` or `descriptive_proxy`)
   prevents recursive proxy construction. Both attempts start from the same
   immutable input snapshot.
6. All applicability checks receive `DescribedHandView`, whose receiver length
   is already masked. There is no post-hoc guess about which public promise
   depended on the third suit.
7. Resolve candidates through the ordinary priority and ambiguity machinery.
   A genuine ambiguity in the selected proxy still returns TD.
8. Project the selected call, authored public meaning, and private purpose
   onto the real decision. Attach proxy provenance, but do not retain the
   synthetic hand as the actor's hand or as public evidence.
9. Run legality, purpose completion, selectors, simulations, and final
   universal-axiom checks with the actual hand. The only proxy input available
   at this stage is typed `DescriptiveProxyEvidence` containing descriptive
   shape, HCP, and K–R. Strength/shape sufficiency checks may consume these
   three fields. Forcing, Pass, control, shortage, stopper, keycard, cue, and
   contract-evaluation checks are prohibited from consuming proxy evidence.

Jacoby and South African Texas expose a shared five-plus-major route family,
but their ordinary predicates retain current real-hand behavior for
non-extreme hands. When an eligible extreme hand reaches either family, direct
extreme-length classification returns `defer_to_description` rather than a
call. This allows the mandatory real attempt to reach TD and the proxy attempt
to classify the hand as its shortened description. Other explicitly authored
real-hand routes remain free to succeed first and therefore suppress proxy
search. The same generic retry applies to later auctions and future systems
without adding another extreme-shape clause to each gadget.

## State and explanation

The selected decision records a serializable `ProxyDiagnostic` object with a
versioned schema:

- trigger class (`eight_plus_single` or `eleven_plus_two_suit`);
- real and descriptive named shapes;
- ordered normalization steps and cumulative donor/receiver counts;
- real K–R, proxy K–R, and absolute difference;
- changed-card count;
- preserved and changed queen/jack locations;
- selected proxy holding;
- selected call and originating authored rule;
- reason the real-hand pass reached TD.

`ProxyDiagnostic` is for explanations, traces, IV Scanner, and TD reports. Its
ordered normalization steps are always the canonical transition sequence
retained during deduplication, so traversal order and cache warming cannot
change serialized provenance. It
is never passed to axioms or call applicability. Candidate generation also
projects a separate immutable `DescriptiveProxyEvidence` containing only
descriptive HCP, K–R, four description lengths, and cumulative
`donations_by_suit` / `receipts_by_suit`. It does not expose synthetic
holdings, changed Q/J locations, synthetic controls, or a `Hand` interface.

Universal axioms receive only `DescriptiveProxyEvidence` through an optional
`alternative_description` parameter. Code review and tests enforce that
control-sensitive axiom functions have no such parameter. The two types cannot
be substituted for one another.

`ProxyDiagnostic` is diagnostic provenance, not partnership knowledge. Neither
proxy type is added to public auction facts. The user-facing explanation says
that the call was selected by describing the extreme hand as the recorded
proxy. IV Scanner and TD reports include the same provenance when a proxy was
tried.

Private purposes created by the selected authored call are retained because
they describe the chosen route. The successful proxy attempt's proposed
memory is committed exactly once; the failed real attempt's proposed memory is
discarded. Later purpose execution evaluates the actor's real hand. No
synthetic card or synthetic length survives in seat memory.

## Caching and determinism

Proxy search may be expensive, so cache it by:

- canonical real hand;
- trigger class and `protected_qj_suits`;
- normalized target shape and cumulative donor/receiver identities;
- suits carrying an explicit public partner maximum of two cards;
- proxy algorithm version.

The cache stores ranked search results, not a bidding decision. Public partner-
short suits freeze Q/J membership and are therefore part of the key. Tied
donor/receiver choices are stored in objective order. The same proxy may be
reused at another compatible auction, while the call is always solved against
the current auction and profile. Cache state cannot change the result for a
fixed hand and auction.

## Failure behavior

The proxy pass returns TD with specific diagnostics when:

- no legal proxy lies within 0.15 K–R;
- the exact dynamic program has no legal state;
- the masked description produces no candidate;
- the selected proxy still yields no candidate;
- ordinary candidate resolution finds a genuine ambiguity;
- the projected call is illegal or violates a real-hand universal axiom.

It never falls back to an arbitrary Pass, random proxy, relaxed K–R tolerance,
or newly enabled third-suit call.

## Verification

Tests must be written before implementation and demonstrate:

1. ordinary hands never enter proxy search;
2. a real-hand call always wins over a possible proxy call;
3. eight-card heart and spade 8-3-2-0 fourteen-HCP examples that currently TD
   select the route obtained from their best seven-card descriptive proxy;
4. 10-3-0-0 normalizes through three finite steps to 7-3-3-0 and invokes only
   one proxy decision attempt;
5. the shared Jacoby/Texas route family recognizes every five-plus length,
   preserves established five-, six-, and seven-card decisions, and defers
   eligible extreme lengths to the descriptive attempt;
6. 6-5, 7-4, and other eleven-plus two-suit hands use the same generic path;
7. A/K never move;
8. Q/J changes occur only in `protected_qj_suits`; all Q/J membership is
   frozen in real actor suits of length two or fewer and in suits where partner
   has a public maximum of two;
9. every selected proxy is a legal thirteen-card hand and has K–R error no
   greater than 0.15;
10. ranking minimizes changed cards, then K–R error, then maximizes preserved
   Q/J locations, and remains deterministic under cache warming;
11. instrumented applicability reads prove every receiver-side increased
    length is
    never observable; increasing it from three to four does not unlock
    Stayman, a second-suit bid, support, or any other third-suit route;
12. real voids, controls, stoppers, keycards, and DDS inputs remain unchanged;
13. applicability reads proxy aggregate strength only through `ctx.strength`,
    while suit quality and holding-specific evidence remain actual;
14. a failed real attempt leaves private memory and trace unchanged; the
    selected proxy purpose commits once and uses the real hand next turn;
15. proxy search can rescue an authored later-auction route, proving the
    implementation is not tied to `1NT-Pass`;
16. no legal DP result, illegal projection, and ambiguity each produce the
    specified TD diagnostic;
17. existing backend tests remain green.

Shape-boundary fixtures include 8-2-2-1 and 8-3-1-1 single-suit hands as well
as tied 6-6-1-0 two-suit donor choices. Multi-step tied fixtures assert the
canonical deduplicated transition sequence, final target shape, cumulative
donation and receipt counts, masked description lengths, selected proxy, and
serialized multi-donor evidence. Run each fixture against cold and warm caches
and require byte-for-byte equal normalization provenance.

## Non-goals

- Estimating the best contract directly with DDS.
- Making the descriptive proxy public partnership information.
- Letting a proxy invent aces, kings, controls, keycards, or partner knowledge.
- Using the enlarged third suit to unlock a call.
- Replacing normal authored or derived decisions that already work with the
  real hand.
- Relaxing the 0.15 K–R tolerance dynamically.
