# Meow Opening Technical Design

Platform Version: 0.0.8
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

This document is the technical system note and refactor audit for Meow 2/1 opening bids and their first major continuation layers. It extends the 1N technical design into the rest of the uncontested opening structure.

The guiding principle is the same: a bridge profile is not a flat table of strings. A call is selected because a hand and auction context make one route better than other available routes. The profile must separate static agreements from judgment, public dialogue frames, private route memory, and range evidence.

## Executable Depth Standard

For an opening family to count as benchmark-usable, at least one representative branch should be executable through the natural third partnership turn when the auction still has bridge work to do:

- opener bid 1: opening call;
- responder bid 1: first response;
- opener bid 2: opener rebid or first answer;
- responder bid 2: responder rebid, answer, or placement;
- opener bid 3: accept, decline, place, answer, or pass after a placed contract;
- responder bid 3: final pass or further placement when the route naturally requires it.

Some branches legitimately finish earlier: a direct final contract, a weak signoff accepted by pass, or a preempt passed out does not need artificial extra calls. The important rule is that a route must not stop merely because the profile has no continuation. If a forcing, invitational, inquiry, or game-forcing route is started, the current benchmark should either continue it to a sensible contract or document the missing continuation explicitly.

The full-auction fixture suite now includes representative third-turn routes for forcing 1N invitation, 2/1 major and side-suit rebid placement, simple-raise game tries, Bergen accept/decline, Drury accept/decline, Jacoby 2N shortness placement, 1m XYZ/drop-dead, Crisscross minor fallback, Puppet over 1N and 2N, strong 2C second-negative placement, and weak-two Ogust placement.

## Root Opening Choice

Opening-bid selection is a Policy Function problem. The Gadgets define possible calls:

- natural five-card major openings,
- natural minor openings,
- 1N opening,
- 2N opening,
- artificial strong 2C,
- weak-two openings,
- three-level preempts,
- Gambling 3N,
- pass.

The opening policy decides among them.

### Current Policy Families

The root selector is split into these route-family functions:

- `meow_opening_strong_policy`
- `meow_opening_notrump_policy`
- `meow_opening_fourth_seat_pass_policy`
- `meow_opening_one_level_seat_1_2_policy`
- `meow_opening_one_level_seat_3_sound_policy`
- `meow_opening_preempt_policy`
- `meow_opening_one_level_seat_3_light_policy`
- `meow_opening_one_level_seat_4_policy`
- `meow_opening_pass_policy`

This means a test can now say whether a hand opened because it was a strong-opening hand, a notrump hand, a normal one-level hand, a preemptive hand, a fourth-seat Rule-of-15 hand, or a pass.

### Root Judgments

Strong route:

- Layer: Policy Function chooses; `meow_strong_two_club` and `meow_two_notrump_opening` Gadgets define calls.
- Context change: 2C creates a strong artificial opening context; 2N creates a high-range notrump context.
- Connections: 2C connects to waiting response, natural rebids, second negative, and notrump-system adapter; 2N connects to Puppet, transfers, minor-suit Stayman, notrump placement, and slam tools.

Notrump route:

- Layer: 1N Gadget plus opening Policy Function.
- Context change: opener HCP and balanced-shape evidence should be available to policies.
- Connections: full 1N structure in `docs/09_meow_1nt_technical_design.md`.

One-level natural route:

- Layer: natural opening Gadgets plus seat-aware opening Policy Functions.
- Context change: major openings record `major_opening` and major length evidence; minor openings record `minor_opening`, minor length evidence, and denial of a five-card major.
- Connections: 1M raises, 1M new-suit responses, forcing 1N, 2/1 game force, 1m responses, minor raises, checkback, opener rebids, and slam tools.

Preempt route:

- Layer: preemptive-opening Gadget plus opening Policy Function.
- Context change: preempt suit, expected length, seat/vulnerability style, and suit quality.
- Connections: Ogust, forcing new suit, raises, game placement, and pass.

Fourth-seat route:

- Layer: Policy Function.
- Context change: none beyond selected call.
- Current Meow style: fourth seat does not preempt and uses the Rule of 15 gate for one-level openings.

## 1M Openings

Meow 2/1 uses natural five-card major openings.

### 1M Opening Call

Layer: Gadget for the call; Policy Function for selecting the opening.

Meaning:

- `1H`: natural, at least five hearts.
- `1S`: natural, at least five spades.

Policy questions:

- Does the hand have normal first/second-seat opening values?
- In third seat, should a lighter major opening be chosen?
- In fourth seat, does the hand satisfy Rule of 15?
- With 5-5 majors, choose spades.
- With 6-5 majors, choose the longer major.
- With balanced 15-17 and a five-card major, this profile currently prefers 1N.

Context changes:

- `major_opening`
- target suit
- opener length evidence
- seat-style evidence when relevant.

Connections:

- direct major raises,
- new major over 1H,
- forcing 1N,
- 2/1 game force,
- Drury after passed-hand major openings,
- Bergen,
- Jacoby 2N,
- simple raises and game tries,
- splinters,
- control bidding and keycard after fit.

### Direct Major Raise Family

Layer: simple raise, Bergen, Drury, and Jacoby 2N are separate Gadgets. Policy Functions choose among candidates.

Current Policy Functions:

- `meow_major_raise_jacoby_policy`
- `meow_major_raise_bergen_policy`
- `meow_major_raise_simple_policy`
- `meow_bergen_opener_continuation_policy`
- `meow_drury_opener_continuation_policy`
- `meow_jacoby_opener_continuation_policy`
- `meow_jacoby_responder_placement_policy`

Bridge meaning:

- Three-card support and constructive-ish values can use a simple raise.
- Four-card support and game-forcing values use Jacoby 2N.
- Four-card support with invitational or weaker values use Bergen.
- By a passed hand after a third/fourth-seat opening, Drury is available instead of the same first/second-seat raise structure.

Context changes:

- fit evidence should record opener minimum length plus responder support length;
- `partnership.fit.<suit>` is better than a generic agreement flag;
- raise strength can be recorded for later game/slam judgment.

Connections:

- simple raise connects to Kokish/help-suit game tries and direct game decisions;
- Bergen connects to opener's game/pass/slam-try decision;
- Jacoby 2N opens a game-forcing major-raise dialogue;
- Drury opens a passed-hand inquiry dialogue.

Current audit:

- The direct major-raise selector is now split by route family.
- The Gadgets define simple raises, Bergen, Drury, and Jacoby 2N.
- Bergen, Drury, and Jacoby 2N now have practical continuation coverage through accept/decline or game placement.
- Jacoby 2N still needs richer relay, cue-bid, and slam-try continuations beyond the current shortness/extras/game layer.

### New-Suit And Forcing 1N Family

Layer: `meow_two_over_one_core` defines 2/1 and forcing 1N calls; `major_response.policy.py` chooses the route.

Current Policy Functions:

- `meow_major_response_spade_over_heart_policy`
- `meow_major_response_two_over_one_policy`
- `meow_major_response_forcing_notrump_policy`

Bridge meaning:

- After `1H`, `1S` is natural with spades and enough values to respond.
- A 2/1 new-suit response by an unpassed hand is game forcing in the benchmark.
- `1N` over a major is forcing for one round and handles hands that do not fit a raise or 2/1 route.

Context changes:

- responder suit-length evidence,
- force level,
- possible responder hand range.

Connections:

- 2/1 game force connects to opener's shape-description dialogue, serious/non-serious slam tools later, and final game/slam placement.
- Forcing 1N connects to opener's rebid policy: rebid six-card major, bid side suit, reverse with extras, jump notrump with 18-19, or raise later when a fit is discovered.

Current audit:

- The first-response policy is now split into visible route families.
- A practical 2/1 branch now continues after opener rebids a six-card major; responder places 4M with a 6-2 or better fit and 3N without fit.
- A second practical 2/1 branch now continues after opener rebids a side suit; responder places the side major with support or places 3N after a side-minor rebid.
- Forcing 1N now includes opener accept/decline after responder's 2N invitation following a minor rebid.
- The full 2/1 game-force tree is still not complete: opener raises of responder's suit, new-suit rebids, delayed support, cuebids, and slam tries need the same dialogue treatment.

### Game Try Family

Layer: Kokish/help-suit game-try Gadget plus game-try Policy Function.

Bridge meaning:

- After a simple major raise, opener can ask whether responder has help in a suit or trump.
- Game try is a general route, not one auction string. Multiple sequences can lead to a game-try state.

Context changes:

- agreed major fit evidence,
- game-try target,
- responder answer evidence,
- game accepted/declined state.

Connections:

- accept game,
- stop in partscore,
- continue to control bidding or keycard when values exceed game try.

Current audit:

- Current implementation has examples for spade and heart help-suit tries.
- The general route model should be expanded so any established major fit can enter the game-try family.

## 1m Openings

Meow 2/1 uses natural minor openings.

### 1m Opening Call

Layer: Gadget for `1C` and `1D`; opening Policy Function for selection.

Meaning:

- `1D`: natural, usually four or more diamonds, denies a five-card major.
- `1C`: natural, may be three cards, denies a five-card major.

Policy questions:

- Open a five-card major before a minor.
- Open longer minor.
- With equal minors in the current benchmark, use the implemented minor-opening style.
- Prefer 1N with balanced 15-17 if available.
- Consider future policies such as rebid ease, suit quality, and whether opening 1m creates impossible rebid problems.

Context changes:

- opener minor length evidence,
- denial of a five-card major,
- rough HCP/opening-value range,
- opening seat and vulnerability style.

Connections:

- one-level major responses,
- Walsh-style bypass of diamonds,
- natural notrump responses,
- inverted minors,
- Crisscross raises,
- weak jump shifts,
- opener rebids,
- New Minor Forcing / XYZ,
- Spiral 3344.

### Responder's First Bid After 1m

Layer: minor-response Gadget definitions plus `minor_response.policy.py`.

Route families:

- weak jump shift,
- inverted minor raise,
- Crisscross game-forcing minor raise,
- natural 1-level major response,
- Walsh-style diamond response over 1C,
- natural notrump response,
- fallback low response.

Policy questions:

- Does responder have a four-card major?
- Does Walsh style bypass diamonds below game-force values?
- Is responder strong enough to bid diamonds first and later show a major?
- Is there a minor fit with invitational-plus or game-forcing values?
- Does responder have a weak six-card major suitable for a weak jump shift?
- Is a natural notrump response better because responder is balanced and lacks a major?

Context changes:

- responder suit length,
- responder strength band,
- support evidence for opener's minor,
- force level.

Connections:

- inverted-minor continuations,
- Crisscross continuations,
- opener's rebid,
- checkback/XYZ after opener's notrump or suit rebid,
- slam exploration in minor fits.

Current audit:

- The executable policy covers the main route families, but they still live inside one function.
- This should be split later into route-family functions like the opening and 1N layers.

### Opener's Rebid After 1m

Layer: minor-opening call specs plus `minor_opener_rebid.policy.py`.

Route families:

- raise responder's major with support,
- jump raise with extras,
- show an unbid major,
- rebid notrump with balanced ranges,
- reverse with extras,
- strong jump shift,
- rebid long minor,
- show second minor.

Policy questions:

- Has responder shown a major that opener can support?
- Is support three-card or four-card?
- Is opener balanced and in the correct range for 1N or 2N?
- Is a reverse required to show shape and extras?
- Is a strong jump shift available and accurate?
- Does opener still owe partner a description of shape before strength?

Context changes:

- opener HCP range,
- opener shape/length evidence,
- support/fit evidence,
- force level after reverse or strong jump shift,
- denial evidence when choosing notrump.

Connections:

- responder rebid,
- two-way NMF/XYZ,
- Spiral 3344,
- fourth-suit forcing,
- Lebensohl over reverse,
- minor slam tools.

Current audit:

- The policy has practical branches but still has too many decisions in one function.
- Strong jump shift and reverse are present, but the state model needs richer descriptions of what opener has shown and what responder still needs to know.

### Responder's Rebid After 1m

Layer: checkback/XYZ, Spiral, and natural continuation Gadgets plus `minor_responder_rebid.policy.py`.

Route families:

- natural signoff,
- drop-dead relay,
- invitational checkback,
- game-forcing checkback,
- Spiral 3344 after a major fit question,
- natural slam try,
- final placement.

Policy questions:

- Has opener limited the hand?
- Is there a possible major fit?
- Is responder weak and looking for a safe partscore?
- Does responder need to force before showing a long suit?
- Does responder know enough to place game?
- Is slam possible based on combined range and fit?

Context changes:

- responder route intention,
- partnership force level,
- possible fit evidence,
- known opener range,
- signoff or final-contract evidence.

Current audit:

- Current implementation demonstrates the route families but is not yet a complete dialogue system.
- The next refactor should make checkback/XYZ a dialogue-flow helper rather than repeated sequence fragments.

## 2C Opening

The benchmark uses artificial strong 2C with 2D waiting.

### 2C Opening Call

Layer: strong 2C Gadget defines the call; root opening Policy Function selects it.

Policy questions:

- Is the hand above direct 2N range and balanced?
- Is the hand strong and unbalanced enough that game is likely opposite very little?
- Does long-suit playing strength justify 2C with fewer HCP?
- Should a very strong one-suiter open 2C rather than a natural opening?

Context changes:

- strong artificial opening,
- opener strength range,
- possible balanced/notrump rebid plan,
- force level.

Connections:

- 2D waiting,
- natural positive responses in future versions,
- opener notrump rebids,
- opener natural suit rebids,
- second negative,
- system-on notrump adapter.

### 2D Waiting Response

Layer: Gadget plus Policy Function.

Current Meow style:

- `2D` is waiting even with some positive hands.
- Immediate positive suit responses are not active in the benchmark.

Context change:

- responder has not made a natural positive response;
- responder may still have values.

Connections:

- opener rebid describes hand.

Current audit:

- `meow_strong_two_club_response` handles this simple route.
- Future versions should support optional positive responses and control-showing styles as selectable Gadgets.

### Opener's Rebid After 2C-2D

Layer: Gadget definitions plus `strong_two_club.policy.py`.

Route families:

- 2N with 22-24 balanced or near-balanced,
- 3N with 25-27 balanced or near-balanced,
- natural suit rebid with a long suit,
- future Kokish-style route if adopted.

Context changes:

- opener HCP range,
- opener shape,
- possible notrump system-on context,
- natural suit evidence.

Connections:

- after 2N, use notrump response structure with adjusted range;
- after suit rebid, responder may make second negative or describe values;
- slam tools become available later when fit/range justify.

Current audit:

- Current implementation distinguishes notrump rebid and natural suit rebid inside one function.
- The notrump adapter works but should become a reusable "notrump structure after artificial strong opening" mechanism.

### Responder's Second Bid

Layer: second-negative and notrump-adapter Gadgets plus Policy Function.

Route families:

- second negative with a true bust,
- transfer/checkback/Puppet after 2C-2D-2N,
- natural positive continuation after opener's suit rebid,
- final placement when opener's notrump rebid plus responder hand is enough.

Context changes:

- responder strength cap,
- possible suit evidence,
- notrump system-on state,
- force level.

Current audit:

- Current implementation covers second negative and simple system-on responses over 2N.
- After a second negative over a major rebid, opener can now place 4M with enough playing strength or stop lower with a less self-sufficient hand.
- It does not yet fully model positive continuation plans after opener's natural suit rebid.

## 2N Opening

Layer: 2N opening Gadget plus root strong/notrump opening Policy Function.

Meaning:

- 20-21 balanced or near-balanced.

Connections:

- Puppet Stayman,
- major transfers,
- minor-suit Stayman,
- 3N to play,
- slam tools.

Current audit:

- Opening selection works.
- Puppet over 2N now has a representative full-auction test through opener's answer, responder's clarification, opener's placement, and final pass.
- Response structure is still less complete than the 1N structure and should share the same dialogue abstractions.

## Preemptive Openings

Layer: preemptive-opening Gadget plus opening preempt Policy Function.

Meaning:

- Weak twos show a six-card suit.
- Three-level preempts show a seven-card or longer suit.
- Second seat is sounder.
- Third seat is more tactical.
- Fourth seat preempts are off in the benchmark.

Policy questions:

- Seat and vulnerability relation.
- Suit quality.
- Side voids.
- Side four-card majors.
- Side five-card suits.
- Whether seven-card hands should use three level rather than weak two.

Context changes:

- preempt suit,
- expected length,
- suit-quality evidence,
- seat/vulnerability style.

Connections:

- Ogust,
- forcing new suit,
- raises,
- game placement,
- pass.

Current audit:

- Opening preempt selection is now its own root policy.
- Continuation policies cover Ogust, responder placement after Ogust answers, forcing new suit, and raises at a practical benchmark level.
- Relative-call helpers will be needed for more general preempt structures and interference.

## Default Behavior

Layer: default pass Gadget plus final pass behavior.

The default is intentionally boring: if no agreement and policy selects no bridge action, pass. A serious profile should later replace this with context-sensitive default policies:

- if game force is active, keep bidding to a sensible game;
- if a suit fit is established, return to the fit;
- if a notrump range is limited, place notrump;
- if partner made a forcing bid, do not pass.

This is a policy problem, not a Gadget problem.

## Current Implementation Summary

Good:

- Root opening selection is split into route-family policies.
- Direct major responses are split into spade-over-heart, 2/1 game force, and forcing 1N policies.
- Direct major raises are split into Jacoby, Bergen, and simple-raise policies.
- 1m, 2C, 2N, preempt, checkback, and game-try structures are represented as profile-owned Gadgets plus policy files.
- Representative opening-family routes are now tested to meaningful placement depth instead of stopping at the first or second response.
- Test fixtures now name the selecting route-family policy for the refactored opening and major-response areas.
- Major-raise continuations now cover Bergen, Drury, and Jacoby 2N at practical benchmark depth.
- 2/1 continuations now cover both a six-card-major rebid route and side-suit rebid routes.

Gaps:

- 1m first-response, opener-rebid, and responder-rebid policies still need the same route-family split.
- 2C opener rebid and responder rebid still need route-family names for notrump adapter, natural rebid, second negative, and positive continuation.
- Direct major-raise continuations need more slam-oriented depth, especially Jacoby relays, splinters, and control-bid continuations.
- The 2/1 continuation layer now proves major-rebid and side-suit-rebid routes; opener raises of responder's suit, delayed support, fourth-suit forcing, control bids, and slam tries remain to be built.
- Game-force and slam-try context are still too label-based in places. Later policies should read range/fit/control evidence through `ctx.knowledge`.
- Checkback/XYZ and 2C notrump adapters should use reusable dialogue-flow helpers.

## Reference Bridge Basis

This document uses mainstream bridge references as practical background:

- 2/1 and forcing 1N: `https://www.bridgebum.com/two_over_one.php`
- 2/1 game-force basics: `https://www.bridgebum.com/what_is_two_over_one.php`
- Strong 2C and second negative: `https://www.bridgebum.com/strong_2c.php`
- New Minor Forcing: `https://bridge.fandom.com/wiki/New_minor_forcing`
