# Meow 2/1 Practical Benchmark

Platform Version: 0.0.6
Author: Meow Li
Copyright: Copyright (c) 2026 Meow Li. All Rights Reserved.

This document defines the first practical benchmark Convention Set for Partner. It is based on Meow Li's working 2/1 agreements and should be used to test whether the IR language, engine, generated notes, and tests can handle a realistic but still mainstream partnership structure.

The benchmark is partly executable now. The current code includes `backend/convention_sets/meow_2over1.yaml` and standalone Convention directories for openings, Stayman, Puppet Stayman stubs, transfers, Texas, slam tools, simple major raises, Bergen, Drury, Jacoby 2N, Kokish game tries, and integration policies. This first implementation slice is intentionally narrow but includes full-auction tests that have to make bridge sense.

## 1. Benchmark Purpose

The benchmark should pressure-test these platform abilities:

- short Call Specification IDs with structured meaning and notes,
- semantic state instead of full auction enumeration,
- Bidding Plans for long route logic,
- Protocol Frames for transfers, Stayman, game forces, raises, and slam asks,
- Call Selection Policies for judgment among alternatives,
- generated system notes,
- pair-hand simulation where both hands are available and the engine can continue to a final contract.

The benchmark should expose engine gaps. It is acceptable for early tests to mark some sequences as expected future behavior, as long as the missing engine feature is documented.

## 2. Proposed Convention Breakdown

Current Convention directories:

```text
backend/conventions/meow_two_over_one_core/
backend/conventions/meow_minor_opening_structure/
backend/conventions/meow_inverted_minors/
backend/conventions/meow_crisscross_minor_raises/
backend/conventions/meow_two_way_nmf_xyz/
backend/conventions/meow_preemptive_openings/
backend/conventions/meow_gambling_3nt/
backend/conventions/meow_one_notrump_opening/
backend/conventions/meow_two_notrump_opening/
backend/conventions/meow_regular_stayman_over_1n/
backend/conventions/meow_puppet_stayman_over_1n/
backend/conventions/meow_puppet_stayman_over_2n/
backend/conventions/meow_four_way_transfers_over_1n/
backend/conventions/meow_texas_transfers_over_1n/
backend/conventions/meow_quantitative_notrump/
backend/conventions/meow_gerber_over_notrump/
backend/conventions/meow_control_bidding/
backend/conventions/meow_kickback_keycard/
backend/conventions/meow_minorwood_keycard/
backend/conventions/meow_exclusion_keycard/
backend/conventions/meow_rkcb_1430/
backend/conventions/meow_targeted_king_ask/
backend/conventions/meow_simple_major_raise/
backend/conventions/meow_bergen_raises/
backend/conventions/meow_two_way_reverse_drury/
backend/conventions/meow_jacoby_2nt_major_raise/
backend/conventions/meow_kokish_game_tries/
backend/conventions/meow_notrump_response_policy/
backend/conventions/meow_major_raise_policy/
```

Recommended Convention Set:

```text
backend/convention_sets/meow_2over1.yaml
```

Rationale:

- Each bridge method should be portable and selectable by a Convention Set.
- 1N opening, 2N opening, regular Stayman, Puppet Stayman, transfers, and Texas are separate so a partnership can choose one without the others.
- Minor opening structure, inverted minors, Crisscross, checkback/XYZ, preemptive openings, and Gambling 3N are separate so a partnership can replace one layer without rewriting the others.
- Texas creates transfer/agreed-suit state but does not own RKCB.
- Quantitative notrump is separate from RKCB and requires notrump focus without an agreed suit.
- Slam tools consume semantic state and remain reusable: quantitative notrump requires notrump focus without an agreed suit; RKCB, Kickback, Minorwood, and Exclusion consume agreed-suit/keycard state; control bidding consumes agreed-suit and slam-interest state; targeted king asks consume keycard-response state.
- Bergen, Drury, Jacoby 2N, and Kokish game tries are separate methods, coordinated by a Convention Set policy.
- Judgment thresholds and route selection should be reusable across the set.

## 3. General Judgment Benchmarks

Simple game thresholds for early testing:

- Major-suit game and notrump game: combined 25 HCP.
- Minor-suit game: combined 27 HCP.
- Suit contracts require at least an eight-card fit.

These are deliberately simple. Later judgment can use controls, shape, suit quality, fit quality, vulnerability, and scoring.

Required engine feature:

- When both hands are available, the platform should simulate both sides of the partnership and continue until a final contract or diagnostic.

Current implementation:

- `backend/app.py` exposes `simulate(request)`.
- `backend/engine/simulator.py` can run a full auction from supplied partnership hands.
- Opponents without supplied hands automatically pass.
- The first full-auction tests verify spade and heart game-try routes plus RKCB grand-slam routes after both Texas and a natural simple raise.

### Opening Selection Policy

The benchmark uses an explicit Call Selection Policy for opening choices. Individual Call Specifications define whether `1N`, `1S`, or `1H` is eligible; the policy defines the partnership judgment between those eligible choices.

Current opening policy:

- Prefer `1N` with 15-17 HCP and balanced shape, even when a five-card major opening is also eligible.
- Otherwise choose `1S` with opening values and at least five spades.
- Otherwise choose `1H` with opening values and at least five hearts.
- Otherwise choose `1D` with opening values, no five-card major, at least four diamonds, and diamonds at least as long as clubs.
- Otherwise choose `1C` with opening values, no five-card major, and at least three clubs.
- Fall back to highest-score candidate if no ordered choice applies.

This policy is intentionally outside the individual opening Call Specifications. A Convention Set can replace this policy without rewriting the meanings of those calls.

### Minor Openings And Responses

Current executable agreements:

- `1C` is natural, may be three cards, and denies a five-card major.
- `1D` is natural, usually four or more diamonds, denies a five-card major, and is preferred over `1C` when diamonds are at least as long as clubs.
- After `1C`, `1D` is natural with 4+ diamonds and no four-card major.
- One-level major responses often bypass diamonds: after one of a minor, `1H`/`1S` show the major with constructive values; with 4-4 majors, hearts are bid first; with 5S4H, spades are bid first.
- `1N` response shows 6-10.
- `2N` response shows 11-12 balanced.
- `3N` response shows 13-15 balanced and is a placement to game.
- Two-level major jump shifts after a minor opening are weak and natural, not Soloway-style strong jump shifts. These are alertable in the current benchmark metadata.

### Inverted Minors

Current executable agreements:

- `1C P 2C` and `1D P 2D` are inverted minor raises.
- They are invitational or better, deny a four-card major, are alertable, and are forcing to `2N` or three of the agreed minor.
- The raise creates `minor_raise`, `agreed_suit`, and `forcing_status` semantic facts.
- Opener may rebid `2N` with a minimum balanced hand and side-suit stoppers.
- Otherwise opener shows stoppers up the line where practical.
- Responder passes `2N` with invitational values and bids `3N` with game-going values.

The stopper decision is executable through a reusable Named Evaluator, not through a hard-coded field. The current stopper definition is ace, king, guarded queen, or jack-third/longer style support where implemented.

### Crisscross Minor Raises

Current executable agreements:

- `1C P 2D` is a game-forcing club raise.
- `1D P 3C` is a game-forcing diamond raise.
- Both are alertable and create `minor_raise`, `agreed_suit`, and `forcing_status: game_forcing`.
- The current continuation slice lets opener choose `3N` with a balanced hand and side-suit stoppers, or fall back to the agreed minor when notrump is unattractive.

### Two-Way NMF And XYZ

Current executable agreements:

- After opener rebids `1N`, two-way New Minor Forcing is on.
- After a three-call one-level auction, XYZ is on.
- `2C` is an artificial relay to `2D`, used for invitational hands and weak diamond drop-dead routes.
- `2D` is artificial and game forcing.
- `2N` transfers opener to `3C` for weak club drop-dead routes.
- Natural `3C`/`3D` slam tries are represented as explicit slam-interest calls, separate from the weak `2N` relay.

Implementation note: the current executable slice uses semantic facts from `opener_rebid` and `opener_notrump_rebid` instead of listing every possible `1X-1Y-1Z` pattern. This is a feasibility test for semantic-context matching, but the language still needs stronger lifecycle controls for large checkback trees.

### Preemptive Openings And Gambling 3N

Current executable agreements:

- Weak `2D`, `2H`, and `2S` are natural, six-card, and style-adjusted by seat and vulnerability.
- Three-level preempts are natural, seven-card, and style-adjusted by seat and vulnerability.
- Fourth-seat weak preempts are not opened in the current benchmark slice.
- `3N` is Gambling, alertable, and shows a solid seven-card or longer minor with no outside ace or king.

The preempt evaluator reads `env.seat_position` and `env.vulnerability_relation`, which are derived by the engine from absolute NESW dealer/vulnerability and the current auction.

## 4. 1N Opening And Responses

### 1N Opening

Agreement:

- `1N` opening shows 15-17 HCP, balanced.

IR expectations:

- `CallSpecification` for `1N`.
- Effect sets notrump focus and shown hand range.
- Active notrump-response Protocol Frame after `1N P`.

### 2C Stayman

Agreement:

- `2C` is Stayman.
- Use ordinary Stayman, Garbage Stayman, and Smolen.
- Sequence `1N P 2C P 2D/H/S P 2N` is invitational.
- Alert/explain the `2N` rebid as may or may not include a four-card major.

IR expectations:

- `2C` creates a Stayman Protocol Frame.
- Opener continuations show no major, hearts, spades, or both depending on chosen style.
- Responder's `2N` continuation is a Call Specification requiring active Stayman frame and invitational values.
- Garbage Stayman is represented as a Bidding Plan, not as a public meaning leak.
- Smolen is represented as a Bidding Plan plus Call Specifications for responder's jump continuations after a no-major response.

Open implementation choice:

- Exact opener response style after Stayman must be fixed before full tests. A common simple style is `2D` no four-card major, `2H` four hearts, `2S` four spades.

### Four-Way Transfers

Agreement:

- `2D` transfers to hearts.
- `2H` transfers to spades.
- `2S` transfers to clubs.
- `2N` transfers to diamonds.

Major transfers:

- Opener completes at the target major.
- Opener superaccepts with four-card support and maximum values.
- `3H` over a heart transfer and `3S` over a spade transfer are superaccepts.

Minor transfers:

- Responder uses a minor transfer only with at least a six-card suit.
- Superaccept requires honor-third or stronger support in the target minor.
- Bidding the gap is the superaccept.

Confirmed minor-transfer gap style:

- After `1N P 2S`, `2N` is the gap superaccept for clubs and `3C` is normal acceptance.
- After `1N P 2N`, `3C` is the gap superaccept for diamonds and `3D` is normal acceptance.

Confirmed minor-support standard:

- `Axx`, `Kxx`, `Qxx`, or stronger holdings such as `KQx` qualify.
- The current slice implements this as the reusable expression-type Named Evaluator `eval_minor_honor_third`, not as a hard-coded field named `can_superaccept`.

Current executable plan/frame slice:

- The heart-transfer Call Specification now uses `state_has.transfer` for its pending-transfer requirement.
- `2D` over `1N` opens a `major_transfer` Protocol Frame with stages `opener_rebid` and `responder_continuation`.
- Opener's normal heart-transfer completion advances that frame to `responder_continuation`.
- A weak heart-transfer signoff Bidding Plan is executable: with 5+ hearts and 0-6 HCP, responder can transfer with `2D`; after opener completes with `2H`, the active plan generates `P` as final placement.
- The heart-transfer superaccept `3H` is executable with four-card support and maximum-style notrump values. It records `transfer_superaccept` and `agreed_suit: H`.
- A strong heart-transfer slam Bidding Plan is executable as an entry route and a later continuation. It can choose `2D` as the public heart-transfer Call Specification, then after `3H` superaccept compete among reusable slam tools. Public meaning still comes from the selected standalone Call Specification; private route provenance is recorded separately when a Bidding Plan caused the route.

### Slam Continuations After A Fit

Current executable slam slices:

- `meow_control_bidding`: after `1N P 2D P 3H P`, `4D` can show diamond control and active heart-slam interest.
- `meow_rkcb_1430`: `4N` asks keycards for the agreed suit when no other keycard frame is pending.
- `meow_kickback_keycard`: with hearts agreed, `4S` asks heart keycards using Kickback steps.
- `meow_minorwood_keycard`: after a diamond-transfer superaccept creates `agreed_suit: D`, `4D` asks diamond keycards.
- `meow_exclusion_keycard`: with hearts agreed and a diamond void, `5D` asks heart keycards excluding the diamond ace.
- `meow_gerber_over_notrump`: with notrump focus and no agreed suit, `4C` asks for aces.
- `meow_targeted_king_ask`: after heart RKCB information, `5N` can ask for the diamond king; `6D` confirms it; `7H` can be placed from the positive response.

These are intentionally separate Conventions. The point of the benchmark is that a partnership can choose, remove, or replace one of these methods without editing the transfer or opening files.

### Responder Major-Suit Weak/Invite Logic

Agreement:

- With a five-card major and `<= 6` HCP, transfer and pass.
- With a five-card major and 7-8 HCP, pass 1N instead of inviting.

Implementation note:

- The 7-8 HCP pass style is nonstandard enough that it should be recorded as a declared Call Selection Policy, not hidden inside transfer Call Specifications.

### 3-Level Over 1N

Agreement:

- `3C` = Puppet Stayman.
- `3D` = 5-5 minors, game forcing.
- `3H` = 5-5 majors, invitational.
- `3S` = 5-5 majors, game forcing.

IR expectations:

- `3C` creates a Puppet Stayman Protocol Frame.
- `3D`, `3H`, `3S` are descriptive/context-initiating Call Specifications.
- Major/minor two-suiter continuations should use semantic state rather than enumerated strings.

Open implementation choice:

- The exact Puppet Stayman responses over 1N must be selected. A common benchmark can mirror 2N Puppet style if no partnership-specific style is provided.

### Texas Transfers

Agreement:

- Four-level Texas transfers to majors are on over 1N.
- Subsequent `4N` may be RKCB for the transferred major when the standalone RKCB Convention applies.

IR expectations:

- Texas transfer creates transfer state and agreed/trump candidate state.
- Completion sets agreed suit or RKCB-eligible trump context.
- `4N` belongs to the standalone RKCB Convention. It requires semantic trump context, not ownership by the Texas file.

### Quantitative 4N

Agreement:

- With notrump focus and no agreed suit, `4N` is quantitative.
- Quantitative `4N` must not fire while a transfer, Stayman, or Puppet Stayman context is pending.

IR expectations:

- Quantitative notrump is its own Convention.
- It competes with other possible `4N` meanings through semantic requirements and the same-call resolver.
- If both quantitative and RKCB are eligible, the engine should diagnose ambiguity unless an explicit policy resolves it.

## 5. 2N Opening And Responses

### 2N Opening

Agreement:

- `2N` opening shows 20-21 HCP, balanced.

### Responses

Agreement:

- `3C` = Puppet Stayman.
- `3D` transfers to hearts.
- `3H` transfers to spades.
- `3S` = minor suit Stayman.
- `3N` = to play.

IR expectations:

- 2N creates notrump focus with higher strength.
- Puppet Stayman and transfers use separate Protocol Frames from 1N methods, even if they share object templates.
- Minor Suit Stayman requires semantic continuation objects.

## 6. RKCB 1430 Structure

Agreement:

- RKCB uses 1430.
- `5N` asks for specific kings.
- `+1` asks for trump queen and guarantees all keycards.

Required semantic state:

- agreed suit,
- asker,
- responder,
- keycard method `1430`,
- keycard response,
- trump queen status,
- all-keycards-known status,
- specific-king ask.

1430 response structure:

- `5C` = 1 or 4 keycards.
- `5D` = 0 or 3 keycards.
- `5H` = 2 or 5 keycards without trump queen.
- `5S` = 2 or 5 keycards with trump queen.

Implementation policy:

- RKCB Call Specifications require semantic trump agreement and should not enumerate every auction where `4N` could be keycard.
- In the current executable slice, RKCB is in its own `meow_rkcb_1430` Convention. It uses `auction_pattern: "*"`, `requires.fact_exists`, `fact_attribute`, and dynamic effects so it can read the agreed suit from Texas, from a natural simple raise, or from a major-transfer superaccept.
- A `rkcb_1430` Protocol Frame opens when `4N` is replayed as RKCB. This frame is separate from the Bidding Plan that decided to bid `4N`.
- Remaining engine work is not RKCB-specific matching; it is general bridge legality and ambiguity resolution for future cases where more than one valid meaning of `4N` is present.

Example target benchmark:

```text
1N P 4H P 4S P 4N P 5C P 5N P 6D P 7S
```

This sequence requires pair-hand simulation, Texas transfer state, RKCB state, king-showing state, and grand-slam judgment.

## 7. Major Opening Structure

### 1 Major Opening

Agreement:

- Natural five-card majors.
- 2/1 framework.
- `1M-1N` forcing.
- Natural `1M-2M` simple raises are available with exactly three-card support in the current benchmark.

IR expectations:

- Opening Call Specifications for `1H` and `1S`.
- Simple-raise Call Specifications for both hearts and spades set `agreed_suit` and `major_raise`.
- Forcing notrump Protocol Frame after `1M P 1N`.
- Later responder and opener rebids should use semantic state.

### Bergen Raises

Agreement:

- Bergen Raises are on by unpassed responder in seat 1 or 2 openings.
- Normal Bergen style:
  - `3C` = constructive four-card raise.
  - `3D` = limit four-card raise.
  - `3M` = preemptive raise.
- Current executable slice covers both hearts and spades.

### Drury

Agreement:

- Drury is used by passed hand after seat 3 or 4 major opening.
- Two-way reverse Drury is used.
- Passed-hand `2C` shows a limit raise with exactly three-card support.
- Passed-hand `2D` shows a limit raise with four-card or longer support.
- Opener's rebid of the opened major shows a weak/light opening.
- Other opener rebids show a full opening or better, subject to later partnership detail.

### Jacoby 2N

Agreement:

- Jacoby 2N is used as a game-forcing major raise.
- Opener responses use the common structure:
  - New suit at the three level shows shortness.
  - New suit at the four level below game shows a second five-card suit.
  - `3M`, `3N`, and `4M` show strength/shape according to the standard Jacoby 2N structure.

IR expectations:

- Creates major-raise game-force Protocol Frame.
- Sets agreed major.
- Opener continuation Call Specifications describe shortness, strength, or shape depending on selected style.

### Splinters

Agreement:

- Splinters are on over major openings.

IR expectations:

- Call Specifications show support, game force, singleton/void in bid suit.
- Effects set agreed major and shortness.

### Kokish And Help-Suit Game Tries

Agreement:

- After `1S P 2S`, `2N` asks responder where help is available.
- After `1S P 2S`, `3C`, `3D`, and `3H` ask for help in the bid suit.
- After `1S P 2S`, `3S` asks whether responder has help in trump because opener lacks spade honors.
- After `1H P 2H`, `2S` asks responder where help is available.
- After `1H P 2H`, responder's `2N` response shows help in spades.
- After `1H P 2H`, `2N` by opener is a help-suit game try in hearts.
- Suit-specific help-suit game tries envision opener holding a holding such as `Qxx` in the asked suit and needing fitting help from responder.

IR expectations:

- Asking bids create a general `game_try` or `help_suit_game_try` Protocol Frame.
- Responder continuations answer the active game-try frame.
- These are not new one-off ontology families. They should reuse general concepts:
  - invitation,
  - help suit,
  - trump help,
  - responder cooperation,
  - game acceptance or signoff.
- Evaluating "help" must be written through the limited YAML expression language. Examples include honor holding, shortness, fitting cards, and lack of wasted values.

## 8. 1 Minor Opening Gap

The benchmark is not complete without 1-minor openings and continuations.

Required future coverage:

- `1C` and `1D` opening style,
- minor-suit length and better-minor rules,
- inverted minors or natural raises,
- 1M responses,
- notrump responses,
- 2/1 auctions after a minor opening,
- competitive agreements.

The first implementation can include placeholder natural minor openings with diagnostics identifying incomplete continuations.

## 9. Required Engine Enhancements

To make this benchmark genuinely executable, the engine needs:

1. Pair-hand auction simulation. First slice implemented for supplied partnership hands and auto-pass opponents.
2. Contract-ending logic.
3. Basic auction legality validation. First slice implemented for contracts, pass, double, redouble, and completed auctions.
4. Ontology-backed semantic state. First typed-facing query slice implemented through `state_has` and `state_missing` over replayed semantic facts, plus `AuctionStateVariable` records for scalar/range inference such as opener HCP range, denied suit length, force status, and private route purpose.
5. Dedicated `requires` evaluation. First slice implemented through the current condition evaluator.
6. Protocol Frame stage execution. First transfer-frame stage advancement implemented for completion, superaccept, and final placement.
7. Bidding Plan candidate generation. First entry-call, `wait_for_call` branch, and `make_call` candidate paths implemented for weak transfer signoff and transfer-slam RKCB entry.
8. Call Selection Policies that compare plans, not only isolated calls. First plan-selected calls report private `plan_origin`, but full plan-vs-plan policy comparison is still future work.
9. RKCB keycard evaluator over actual hand. First slice implemented through `keycard_count`.
10. Suit-fit evaluator over both partnership hands.
11. Generated system notes from all benchmark Conventions. First slice includes Call Specifications, policies, plans, frames, and Named Evaluators.
12. Limited YAML expression language for style judgments. First slice implemented for boolean logic, arithmetic, suit length, honor count, rank containment, and keycard count.
13. Expression-type Named Evaluators. First slice uses `eval_minor_honor_third` for minor-transfer gap superaccepts.
14. Generic semantic-context matching for reusable Conventions such as RKCB. First slice implemented through wildcard visible context plus semantic requirements, dynamic effect attributes, and typed auction-state variables.
15. Same-call meaning resolution. First slice diagnoses ambiguous `4N` meanings, supports explicit policy-based resolution hooks, and suppresses false ambiguity when a plan-generated call is implemented by the same public Call Specification candidate.
16. Force-route reasoning after minor openings. First slice records public inferred state after one-level responses and opener rebids; artificial `2D` checkback can gain explicit internal provenance when it is used to establish a game force before responder later describes a long suit.

## 10. Test Design

Tests should be split into layers.

### Unit Fixture Tests

Single-call tests:

- 1N opening with 15-17 balanced.
- 2N opening with 20-21 balanced.
- 2D transfer to hearts with five hearts.
- 2S transfer to clubs with six clubs.
- 2N transfer to diamonds with six diamonds.
- Major-transfer superaccept with four-card support and maximum.
- Minor-transfer gap superaccept with honor-third support.
- Stayman invitational `2N` continuation.
- 3D 5-5 minors game-forcing.
- 3H 5-5 majors invitational.
- 3S 5-5 majors game-forcing.
- 3C Puppet Stayman.
- Texas transfer followed by RKCB context.

### Semantic Replay Tests

Replay tests:

- Transfer creates pending transfer state.
- Completion updates transfer state.
- Superaccept updates transfer state.
- Texas transfer establishes RKCB-eligible trump context.
- Jacoby 2N sets agreed major and game force.
- Splinter sets agreed major and shortness.
- Forcing notrump creates forcing state.

### Plan Tests

Plan tests:

- Weak five-card major over 1N chooses transfer-pass plan.
- 7-8 HCP five-card major over 1N chooses pass-1N plan.
- Smolen route starts with Stayman and later shows 5-4 major shape.
- Garbage Stayman chooses Stayman for escape.
- Texas transfer route chooses game placement.
- RKCB route continues through response, queen/king ask, and final placement.

### Pair-Hand Simulation Tests

Current executable tests:

```text
1S P 2S P 3D P 4S P P P
```

```text
1N P 4H P 4S P 4N P 5C P 5N P 6D P 7S P P P
```

```text
1S P 2S P 4N P 5C P 5N P 6D P 7S P P P
```

```text
1H P 2H P 2S P 2N P 4H P P P
```

These tests are stored in `backend/tests/cases/full_auctions.yaml`. They use both partnership hands. The current simulator supplies the partner hand through the environment and auto-passes the opponents.

## 11. Clarifications Needed Before Full Benchmark Completion

Confirmed in the current benchmark:

1. Minor-transfer gap style: `1N-2S-2N` is club superaccept and `1N-2N-3C` is diamond superaccept.
2. Minor-transfer superaccept holding: `Axx`, `Kxx`, `Qxx`, or stronger in the target minor.
3. Bergen raise meanings: `3C` constructive, `3D` limit, `3M` preemptive.
4. Drury style: two-way reverse Drury.
5. Jacoby 2N response family: three-level shortness, four-level side suit, strength-showing `3M`, `3N`, `4M`.
6. Kokish/help-suit game try structure after single raises of a major, as described above.

Still to confirm or select by common default:

1. Stayman response style over 1N.
2. Smolen exact structure and strength threshold.
3. Garbage Stayman exact shapes and escape continuations.
4. Puppet Stayman response style over 1N and over 2N.
5. Splinter ranges and exact splinter calls.
6. 1-minor opening style.

When a detail is not confirmed, implementation may use a common bridge default but must document the assumption in Convention descriptions and tests. The current executable slice documents assumptions locally in the relevant Convention files and fixture descriptions.
