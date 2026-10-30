# Ordinary RKCB Continuations Design

**Date:** 2026-10-30  
**Status:** Approved design; implementation in this cycle  
**Scope:** Daqiush ordinary Roman keycard asks only. Voidwood and NFRKCB keep
their own methods and are not aliases of this feature.

## 1. Goal

Ordinary RKCB should provide its standard continuations from public keycard
state rather than from a growing list of complete auction prefixes. This
cycle adds:

- useful-void answers;
- sampled handling of the `0/2/4` and `1/3` ambiguity;
- the `5S -> 5NT` relay when `5S` is not a trump-queen ask;
- a private choice between stopping in 5NT and showing the asker's lowest
  king after the forced 5NT;
- grand-slam invitations after direct `5NT`/six-level void answers, including
  the rule that a skipped lower suit's king is not required.

The existing ordinary 1430 answers remain unchanged.

## 2. Precedence and method identity

Every keycard frame has a method. This feature applies only when the method is
ordinary RKCB (`rkcb_1430`). It must not reinterpret:

- Voidwood answers or continuations;
- quantitative 4NT;
- NFRKCB, whose 4NT is initially a nonforcing suggestion rather than an ask;
- an explicitly authored profile meaning.

Within ordinary RKCB, interpretation priority is:

1. an explicitly authored continuation;
2. the active ordinary-RKCB Purpose filtering calls exposed by the public frame;
3. a legal trump-queen ask;
4. the generic `5S -> 5NT` relay;
5. another generic ordinary-RKCB continuation;
6. TD when the available evidence cannot choose safely.

Thus `5S` after a `5D` answer with hearts agreed is structurally a queen ask.
It remains a queen ask even when the asker privately owns the queen: the
responder cannot reconstruct a private holding from the auction. The relay is
available only in frames where public auction geometry does not assign `5S`
to the queen ask. This keeps replay and both players' interpretation identical.

## 3. State model

The public `keycard_context` continues to identify:

- agreed trump;
- ask call;
- method `rkcb_1430`;
- one of `pending_answer`, `answered`, `relay_pending`, `relay_completed`,
  `completed`, or `disrupted`;
- an optional continuation stage such as `queen_ask`, `grand_invitation`, or
  `counterinvited`, without inventing additional top-level statuses;
- the public answer category;
- a useful-void category: exact suit, one-of-higher-than-trump, or unspecified;
- publicly known trump-queen information;
- kings that a later grand invitation explicitly does not require.

Grand-invitation state also records the invitation call and a counter-invite
count. The count begins at zero and may advance to one; it prevents a second
counter-invitation while retaining top-level status `answered`.

The asker's private `Purpose` retains only private information needed for a
decision:

- the asker's own keycards;
- whether the asker owns the trump queen;
- the current continuation stage;
- whether a `5S` relay is intended as a 5NT signoff or as preparation to show
  the asker's own lowest king.

Private counts never appear in replay or explanations.

The private stages are `await_keycard_answer`, `choose_continuation`,
`await_relay_completion`, and `place_after_5nt`. Selecting a queen ask or relay
advances the existing Purpose; it does not replace or complete it. The Purpose
completes only on a final placement, a final grand decision, or disruption.

Candidate generation runs before private-purpose filtering. Exact profile
calls are generated first; the Purpose then selects or filters those calls.
This replaces the current shortcut that resolves a Purpose before it can see
authored candidates, while retaining a compatibility path for existing
one-reply purposes.

After relay selection, the responder's public frame exposes exactly one forced
`5NT`. That call changes the frame to `relay_completed`; the original asker's
Purpose remains active and chooses Pass, a king show, or a safe terminal
fallback. Enemy interference disrupts the Purpose. An illegal forced 5NT, or
a position in which neither a king nor a legal small-slam return is available,
produces a structured TD.

Interference, an illegal forced continuation, or a terminal TD also changes
the public frame to `disrupted` and records the reason. No later generic RKCB
continuation may use a completed or disrupted frame.

## 4. Useful void

A void is useful when all of the following hold:

- it is not the agreed trump suit;
- it is not a suit that partner has naturally shown as a long suit;
- it is an actual zero-card holding.

“Partner naturally showed a long suit” requires replayed public evidence of a
natural suit call whose length evidence guarantees at least four cards.
Artificial calls and inferred controls do not exclude a void.

If more than one useful void exists, the responder uses the lowest useful
void in bridge call order. This makes the response deterministic and preserves
space. A void in partner's known natural long suit is not shown through the
special void answers; the responder uses the applicable ordinary 1430 answer.
A legal useful-void answer replaces, rather than competes with, the ordinary
1430 answer.

## 5. Responses

The existing ordinary answers remain:

| Call | Meaning |
|---|---|
| 5C | 1 or 4 keycards |
| 5D | 0 or 3 keycards |
| 5H | 2 keycards without the trump queen |
| 5S | 2 keycards with the trump queen |

When a useful void is available, the additional answers are:

| Call | Meaning |
|---|---|
| 5NT | 0, 2, or 4 keycards plus a useful void |
| Six of the void suit | 1 or 3 keycards plus that useful void, when the void suit is lower than trumps |
| Six of trumps | 1 or 3 keycards plus a useful void higher than trumps |

Only six of the void suit publishes an exact void. `5NT` publishes merely
“some useful void”; six of trumps publishes “some useful void higher than
trumps.” Sampling ranges over every suit compatible with the category.

These high answers do not by themselves promise the trump queen. Existing
public evidence and the asker's own holding determine whether the queen is
known. Because these answers consume queen-asking space, the asker does not
start a separate queen or side-king inquiry after them.

## 6. Ambiguous counts and sampling

The asker first removes interpretations that are mathematically impossible
given its own keycards. If more than one of `0/2/4` or `1/3` remains possible,
the engine does not guess the hidden count and does not publish a false exact
count.

Instead, it samples partner hands that satisfy all public auction evidence and
the answer category, then evaluates the legal continuations over the complete
mixture. Contract selection uses the project's existing completion/expected-
score machinery. A sampled continuation must be one of the calls that the
ordinary-RKCB frame exposes.

When DDS or sampling is unavailable, a deterministic conclusion may still be
used if the asker's cards and public evidence leave only one safe result.
Otherwise the auction TDs.

## 7. The `5S -> 5NT` relay

`5S` is a relay only when it is legal and public auction geometry does not
make it the queen ask. Private ownership of the queen cannot change the public
meaning of the call.

The same public relay supports two private purposes:

### 7.1 Rescue to 5NT

The rescue purpose is considered only when five of the agreed trump is no
longer a legal stopping contract. If five of trumps remains available, the
engine must not choose 5NT as a rescue.

The sampler compares 5NT with the forced six-of-trump route. The relay is
chosen as a rescue only when 5NT is not worse under the configured contract
evaluation. If the comparison is unavailable and no deterministic result is
safe, the decision TDs.

After partner's forced 5NT, the asker Passes.

### 7.2 Prepare to show the asker's king

When all partnership keycards and the trump queen are known to be present,
the asker may use the same relay for grand-slam exploration. Partner bids the
forced 5NT. The asker then bids its lowest side-suit king that:

- is not the agreed trump king;
- has not already been denied;
- is legally showable at the six level.

If there is no showable king, the asker uses the agreed-trump small slam as
the negative/final placement when legal. If neither a king nor that placement
is legal, the auction TDs. The public explanation identifies the shown king;
it does not expose the private reason that selected the relay.

## 8. Direct high-answer continuations

After an ordinary 4NT ask receives `5NT`, a six-level void-suit answer, or a
six-level trump answer:

- Pass places the current contract (including natural 5NT) and is not a grand
  invite;
- every non-Pass six-level continuation exposed by this frame is a grand-slam
  invitation; a seven-level call is a final placement;
- no later call is a specific queen ask or specific king ask;
- every legally available lower six-level side-suit call strictly between the
  answer and the invitation is recorded publicly in `not_required_kings`;
  calls already below the answer do not count as skips;
- higher suits not yet passed remain unknown requirements rather than implied
  requirements.

The public frame exposes six-level non-Pass continuations only when a safe
small-slam rejection remains. A seven-level call is a final placement, never
an invitation. A suit continuation is a grand invitation, not a specific king
ask. The responder proceeds as follows:

1. accept with seven of the agreed trump when controls and the existing
   grand-slam policy/simulation qualify;
2. if acceptance is not yet justified but the responder owns a still-unknown
   higher king, show the lowest such king as a counter-invitation, but only
   when that six-level call remains below six of trumps so rejection is legal;
3. otherwise reject with six of the agreed trump when legal;
4. when six of trumps is no longer legal, Pass may reject only over a playable
   six-level agreed-trump or notrump invitation;
5. if no safe rejection, acceptance, or counter-invitation exists, TD.

After a higher-K counter-invitation, the original asker has exactly two
candidates: seven of trumps and six of trumps. Sampling chooses seven when the
grand qualifies; otherwise six of trumps rejects. If six of trumps has somehow
become illegal, the counter-invitation must not have been exposed and the
trace TDs. No second counter-invitation is allowed.

The frame stays active through the single counter-invitation and completes on
Pass, six/seven of trumps, or disruption. Grand acceptance must not require a
king explicitly recorded as unnecessary.

## 9. Failure behavior and explanations

No ordinary-RKCB continuation may be invented merely to avoid a TD. The trace
must distinguish at least:

- ordinary answer/category ambiguity;
- queen ask taking precedence over the 5S relay;
- five of trumps still being available;
- sampling/DDS unavailable;
- no legal king display;
- an unsupported or conflicting keycard method.

## 10. Verification

Tests must cover:

1. all four existing 1430 answers unchanged;
2. useful versus non-useful voids, including partner's natural long suit;
3. all three high-answer forms and multiple-void tie-breaking;
4. mathematical pruning and sampled `0/2/4`, `1/3` mixtures;
5. `5S` as queen ask taking precedence;
6. rescue relay prohibited while five of trumps is available;
7. rescue relay to forced 5NT and Pass when five of trumps is unavailable;
8. complete-keycard/queen relay, forced 5NT, and the asker's lowest-K display;
9. direct high-answer Pass versus grand invitation;
10. skipped lower suits entering `not_required_kings`;
11. acceptance, six-trump rejection, playable Pass rejection, higher-K
    counter-invitation, and no-safe-rejection TD;
12. counter-invitation followed by the asker's sampled 6/7-trump decision;
13. seven-level calls treated as final rather than Pass-rejectable invitations;
14. enemy interference and illegal forced-call closing the public frame as
    disrupted;
15. DDS/sampling failure producing a deterministic safe call or TD;
16. ordinary RKCB, Voidwood, quantitative 4NT, and NFRKCB remaining distinct.

