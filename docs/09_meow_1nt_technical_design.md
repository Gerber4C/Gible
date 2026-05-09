# Meow 1N Technical Design

Platform Version: 0.0.8
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

This document is the technical system note and refactor audit for the Meow 2/1 notrump structure after a 15-17 1N opening. It is written for engineers and AI agents who need to understand the bridge reasoning before changing code.

The current implementation is executable, but the 1N area is not yet graceful enough. A strong profile must be able to look at any responder hand after `1N P` and select a well-defined route: pass, sign off in a suit, invite, place game, search for a major fit, show a two-suiter, explore slam, ask keycards, or place a final slam. That decision cannot be encoded as a flat list of auction strings.

## Core Separation

The 1N structure needs four layers.

1. Gadget

A Gadget defines a bridge agreement module. It says what calls are available, what public meaning they have, and what public evidence they add when replayed. Examples:

- Stayman
- Puppet Stayman
- four-way transfers
- Texas transfers
- Gerber
- RKCB 1430
- control bidding
- quantitative notrump

A Gadget should not decide whether a hand prefers Stayman, Puppet, a transfer, Texas, or 3N. It only defines usable calls and dialogue branches.

2. Policy Function

A Policy Function decides among available candidates using the hand, environment, candidate pool, and recovered public context. This is where bridge judgment lives. Examples:

- Choose pass versus 2D transfer with a weak heart hand.
- Choose Puppet versus regular Stayman with game values and one or both four-card majors.
- Choose Texas versus low transfer with a six-card major.
- Choose 3N versus Stayman when responder has game values and a flat hand.
- Choose control bidding, RKCB, Gerber, quantitative 4N, direct 6N, or direct 7N when slam is possible.

3. Frame

A Frame is a public dialogue context that can be reconstructed from the visible auction. It exists when a call starts a structured exchange and later calls are interpreted inside that exchange. Examples:

- Regular Stayman frame
- Puppet Stayman frame
- transfer frame
- control-bidding frame
- RKCB frame
- Gerber frame

Frames are normally stacked by public dominance. In an uncontested auction, when RKCB starts during control bidding, the RKCB frame becomes dominant and the control-bidding frame closes. The partnership does not return to control bidding after keycard answers.

4. Private Route

A Private Route is the bidder's own plan when a public call can start multiple paths. For example, `1N P 2D` publicly means transfer to hearts, but the bidder may privately be following one of several routes:

- transfer and pass,
- transfer then invite,
- transfer then bid game,
- transfer then show a second suit,
- transfer then start slam exploration,
- transfer then use RKCB after a superaccept.

The route belongs to the seat that selected it. The opener cannot see responder's private reason for `2D`; opener only sees the public transfer state and his own hand.

## Knowledge Model

Profile state should be evidence over bridge variables, not a bag of arbitrary labels. A later policy should ask structured questions like:

```python
ctx.knowledge.opener.S.length
ctx.knowledge.responder.H.length
ctx.knowledge.fit("S").min_total
ctx.knowledge.opener.hcp
```

The state records underneath remain profile-defined and replayable. The knowledge view gives policies a disciplined way to read them.

Examples:

- `opener.length.S = Range(value=4)` after a Puppet branch proves opener has exactly four spades.
- `responder.length.H = Range(min_value=5)` after a transfer to hearts.
- `partnership.fit.S.min_total = Range(min_value=8)` after a 4-4 or 5-3 spade fit is established.
- `opener.hcp = Range(min_value=15, max_value=17)` after a 1N opening.

Fit evidence must preserve shape quality. A 4-4 fit, 5-3 fit, 5-4 fit, 4-3 fit, and 5-2 fit are not the same for judgment. The profile should record minimum component lengths and the basis of the fit, then policies can value them differently.

## 1N Route Families

The top-level decision after `1N P` should be a route-family decision, not a list of isolated bids.

### Terminal Pass

Layer: Policy Function.

Typical hand: no game interest, no better suit contract route.

Current Meow principle:

- With 7-8 HCP and a five-card major, responder passes 1N rather than transferring and inviting.
- With very weak hands and a five-card or longer major, responder normally transfers and passes.
- With very weak hands and no useful escape route, responder may pass.

Context change: none except the auction call.

Connections: none.

Current implementation: partially present in `meow_notrump_response_route`, but it is mixed with many other unrelated decisions.

### Weak Suit Signoff

Layer: transfer Gadget plus Private Route plus Policy Function.

The Gadget defines `2D` as hearts, `2H` as spades, `2S` as clubs, and `2N` as diamonds. The Policy Function decides whether responder should enter the signoff route.

Public context:

- major transfer creates a transfer frame and evidence that responder has at least five cards in the target major;
- minor transfer creates a transfer frame and evidence that responder has at least six cards in the target minor.

Private route:

- "transfer and pass completion" belongs to responder memory.

Connections:

- opener can complete normally,
- opener can superaccept,
- responder can pass either acceptance in the signoff route.

Current implementation: major heart signoff route exists as a Private Route example. Other signoff continuations are not consistently modeled as routes.

### Regular Stayman

Layer: Gadget plus Policy Function plus Frame.

Purpose: find a 4-4 major fit or use the Stayman route to make an invitational, garbage, game-forcing, or Smolen-style plan.

Agreement branch:

- `2C` asks for a four-card major.
- `2D` denies a four-card major.
- `2H` shows four or more hearts and may also hold four spades.
- `2S` shows four spades and denies four hearts in the usual style.

Policy routes:

- invite with one or both four-card majors,
- garbage Stayman with a weak three-suited hand,
- game-going 5-4 major hands that may become Smolen,
- hands that need to check a major before placing 3N.

Subsequent connections:

- over `2D`, responder can invite with `2N`, sign off by a garbage route, use Smolen at the three level, place 3N, or use extended Texas if adopted;
- over `2H` or `2S`, responder can pass in garbage Stayman, invite, bid game in the found major, place 3N, or explore slam if values justify it;
- after a major fit is found, control bidding and keycard tools become available.

Current implementation: only `2C`, `2D`, and `2N` after `2D` are implemented. The implementation lacks opener `2H/2S`, garbage Stayman continuations, Smolen, and full game/slam continuations.

### Puppet Stayman

Layer: Gadget dialogue helper plus Policy Function plus Frame.

Purpose: ask for five-card majors first, then four-card majors. Meow currently allows Puppet over 1N for game-forcing hands with at least one four-card major and no five-card major.

Agreement branch:

- `3C` asks.
- `3D` denies a five-card major and shows at least one four-card major.
- `3H` shows five or more hearts.
- `3S` shows five or more spades.
- `3N` denies a four- or five-card major.

Responder continuations:

- after `3H`, raise to `4H` with three-card support, otherwise `3N`;
- after `3S`, raise to `4S` with three-card support, otherwise `3N`;
- after `3D`, show four spades with `3H`, four hearts with `3S`, and both majors with `4D`.

Opener resolutions:

- after responder shows one four-card major, place that major with a fit or place `3N`;
- after responder shows both majors, choose `4S` with spades, otherwise `4H` with hearts.

Context change:

- opener and responder major lengths become explicit range evidence;
- a 4-4 or 5-3 fit records `partnership.fit.<suit>` with component lengths and minimum total.

Connections:

- current executable branch is game placement only;
- future branches should allow slam continuation when a major fit is found and responder has extra values.

Current implementation: this is the best-shaped current 1N component. It uses a dialogue helper instead of a flat list. The helper is still Puppet-specific; the engine needs a generic dialogue-flow builder.

### Major Transfer Game And Invite Routes

Layer: transfer Gadget plus Policy Function plus Private Route.

Purpose: handle five-card or longer majors when responder wants to declare in the major, invite, bid game, show a second suit, or start slam exploration.

Policy families:

- weak five-card major: transfer and pass;
- 7-8 HCP five-card major in this benchmark: pass 1N;
- invitational five-card major: transfer, then invite by agreement;
- game-going five-card major: transfer, then place game or use a descriptive continuation;
- six-card major with game values and no slam interest: Texas;
- six-card major with slam interest: low transfer first, preserve space, then start slam route if fit/support and controls justify it;
- 5-4 majors with game values: usually Stayman first, then Smolen if opener denies a major.

Context change:

- target major length evidence,
- transfer frame,
- possible fit evidence after completion or superaccept,
- private route memory for the bidder's plan.

Connections:

- transfer completion,
- superaccept,
- Stayman/Smolen for 5-4 major hands,
- control bidding,
- RKCB,
- direct game placement.

Current implementation: major transfers, normal completion, and superaccepts exist. Weak heart transfer signoff and one superaccept-to-RKCB route exist. Full invite/game/second-suit/slam route coverage is incomplete.

### Minor Transfer Routes

Layer: four-way transfer Gadget plus Policy Function plus Private Route.

Meow agreement:

- `2S` transfers to clubs and requires a six-card club suit.
- `2N` transfers to diamonds and requires a six-card diamond suit.
- opener bids the gap as a superaccept with honor-third or stronger support.

Policy families:

- weak minor signoff,
- invitational minor route if available by agreement,
- game-forcing minor route,
- slam try in a minor after fit/support evidence.

Context change:

- responder minor length evidence,
- opener support quality evidence after gap superaccept,
- possible minor fit evidence.

Connections:

- minorwood,
- control bidding,
- 3N placement with stoppers and enough combined values,
- minor-suit slam exploration.

Current implementation: entry calls and opener accept/superaccept calls exist. Responder continuations after acceptance or superaccept are not deep enough.

### Direct Descriptive Three-Level Routes

Layer: Gadget plus Policy Function.

Meow agreement:

- `3D` shows 5-5 minors, game forcing.
- `3H` shows 5-5 majors, invitational.
- `3S` shows 5-5 majors, game forcing.
- `3C` is Puppet Stayman in this profile, not a natural or minor-suit route.

Context change:

- responder shape evidence,
- force level evidence,
- possible future fit search.

Connections:

- opener chooses game,
- opener invites or accepts invitation after `3H`,
- minor slam tools after `3D` if values and fit support exist.

Current implementation: entry calls exist, but continuations are thin.

### Texas Transfers

Layer: Texas transfer Gadget plus Policy Function plus transfer-completion frame.

Meow agreement:

- `4D` transfers to hearts.
- `4H` transfers to spades.
- opener completes at `4H` or `4S`.
- following `4N` is RKCB when the transferred major is agreed.

Policy principle:

- use Texas with a six-card major, game-forcing values, and no need to preserve lower-level exploration;
- use low transfer when slam exploration, second-suit description, or superaccept information matters.

Context change:

- target major length evidence,
- agreed suit or expected trump context after completion,
- possible RKCB frame if responder asks.

Connections:

- RKCB,
- direct final placement,
- control bidding if a lower route was chosen instead.

Current implementation: Texas and a full RKCB grand-slam test are executable. The policy still compares Texas against low transfer too crudely.

### Notrump Game, Invite, And Quantitative Routes

Layer: Gadget plus Policy Function.

Branches:

- pass 1N,
- place `3N`,
- invite by Stayman route or explicit notrump route if the profile provides one,
- quantitative `4N`,
- place `6N` or `7N` directly when responder can count enough tricks or combined strength.

Important conflict:

- In four-way transfers, direct `2N` over `1N` is a transfer to diamonds. Therefore a natural invitational 2N cannot also be direct unless the partnership chooses a different agreement. The system must represent this as a profile-level agreement, not a fallback guess.

Context change:

- natural notrump placement does not establish a suit fit;
- quantitative route creates a notrump slam-invite context, not RKCB.

Connections:

- opener accepts or declines quantitative invites;
- Gerber may be available in selected notrump contexts;
- direct 6N/7N should be a terminal placement policy, not a Gadget tree.

Current implementation: `3N` and quantitative `4N` exist. Direct 6N/7N placement and coherent quantitative continuations are not yet complete.

### Slam Exploration

Layer: multiple reusable Gadgets plus Policy Functions plus Frames.

Slam routes after 1N may involve:

- quantitative notrump,
- Gerber,
- control bidding after a suit fit is established,
- RKCB 1430,
- Kickback,
- Minorwood,
- Exclusion keycard,
- targeted king ask,
- direct small or grand slam placement.

Policy principle:

- Do not ask keycards just because keycard is legal.
- First decide whether the hand has slam interest from known strength, fit quality, controls, and source of tricks.
- If no suit is agreed and the issue is combined notrump strength, use quantitative tools or place notrump.
- If a suit is agreed and controls are uncertain, control bidding can precede keycard.
- If keycards and trump queen are enough and a specific king would make grand, a targeted king ask or 5N branch may be used.

Context change:

- fit evidence,
- control evidence,
- keycard context,
- trump queen state,
- specific king evidence,
- final placement.

Connections:

- low transfer or Stayman may establish the suit fit first;
- Texas may establish a major-suit game, then RKCB can start;
- minor transfer may connect to Minorwood or control bidding.

Current implementation: reusable slam tools exist and tests cover some RKCB grand-slam routes. The slam decision policy is still too small compared with the bridge problem.

## 5-4 Major Decision Table

This is a critical pressure test because the same visible call can represent different route intentions.

After `1N P`, with a five-card major and a four-card other major:

- 0-6 HCP: usually transfer to the five-card major and pass. Garbage Stayman is for weak three-suited hands, not a normal five-card-major hand.
- 7-8 HCP in this benchmark: pass 1N with a five-card major, following Meow's stated style.
- Invitational values: needs an explicit profile agreement. Common methods include Stayman followed by an invitational major rebid, or transfer followed by an invitational continuation. Current Meow implementation does not fully define this.
- Game-forcing values: use Stayman first. If opener shows a four-card major, place or raise that major. If opener denies a four-card major, use Smolen by bidding the shorter major at the three level, so opener can declare the long major if fit exists.
- Slam interest: start with the route that best discovers fit and preserves space. Often that means low Stayman/transfer structure rather than Texas.

This table belongs in Policy Functions. Stayman and transfer Gadgets only provide the available calls and dialogue branches.

## Target Architecture For 1N

The next refactor should make these pieces explicit.

1. `meow_1n_terminal_policy`

Handles pass, direct `3N`, direct `6N`, and direct `7N` when no search route is better.

2. `meow_1n_major_search_policy`

Handles regular Stayman, Puppet Stayman, Smolen routes, 5-4 major handling, and major-fit game placement.

3. `meow_1n_transfer_policy`

Handles weak signoffs, invite/game transfer continuations, minor transfers, Texas versus low transfer, and second-suit continuations.

4. `meow_1n_two_suiter_policy`

Handles 5-5 major and 5-5 minor direct three-level routes, including later opener choice.

5. `meow_1n_slam_policy`

Handles quantitative, Gerber, control bidding, keycard family tools, and direct slam placement after the route-family layer establishes that slam is plausible.

These functions should be standalone and readable, but they should share helper functions for bridge calculations:

- combined HCP floor and ceiling,
- game value,
- slam value,
- major fit quality,
- minor fit quality,
- source of tricks,
- control count,
- suit quality,
- route space cost.

The code should not use score fields or hidden priority numbers. A policy should inspect candidates and return the candidate itself.

## Current Implementation Audit

Good foundations:

- 1N opening records a notrump focus.
- Four-way transfers, Texas, quantitative notrump, Gerber, RKCB, Kickback, Minorwood, Exclusion, and control bidding are separate Gadgets.
- Puppet Stayman is represented as a dialogue flow and records length-specific fit evidence.
- Seat-owned Private Route memory exists and can distinguish responder's private plan from opener's public response.
- The candidate pool and Policy Function signature are correct for whole-pool judgment.
- The initial 1N response selector is split into route-family Policy Functions: private-route continuation, two-suiter, weak partscore, major transfer, major search, and terminal notrump.

Main gaps:

- The route-family split is still shallow. The functions preserve current behavior, but they do not yet contain complete bridge plans for invites, Smolen, second suits, minor continuations, direct slams, or nuanced slam exploration.
- Regular Stayman is underdeveloped. It lacks opener `2H/2S`, garbage Stayman, Smolen, and full game/slam continuations.
- Major transfer continuations are incomplete after normal acceptance and superaccept.
- Minor transfer continuations are incomplete.
- Direct `6N` and `7N` placement are missing as terminal routes.
- Slam policy is too narrow. It can demonstrate RKCB but does not yet reason broadly about control bidding versus quantitative versus direct placement.
- State still mixes useful range evidence with older status labels such as `transfer`, `stayman`, and `agreed_suit`. These labels can remain as public dialogue markers, but serious policy should read normalized evidence through `ctx.knowledge`.
- The Puppet helper should become a generic dialogue-flow helper. Puppet is one example of a broader pattern: ask, answer, continuation, resolution, and branch closure.

## Implementation Rule

When adding a 1N branch, write it at the right layer:

- If the branch defines "what a call means," it belongs in a Gadget.
- If it defines "which route should this hand choose," it belongs in a Policy Function.
- If it creates a replayable public exchange, it opens or advances a Frame.
- If the same public call can represent different plans by the same bidder, it needs a Private Route.
- If later judgment depends on inferred hand information, emit range evidence and read it through `ctx.knowledge`.

The objective is not to make every auction hand-coded. The objective is to make each bridge reasoning step explicit enough that the engine can choose a route for any hand after 1N and then continue the auction from the state created by that route.

## Reference Bridge Basis

This document uses mainstream notrump-structure ideas as reference points:

- Stayman and common responder continuations: `https://www.bridgebum.com/stayman.php`
- Garbage Stayman: `https://www.bridgebum.com/garbage_stayman.php`
- Smolen after Stayman: `https://bridge.fandom.com/wiki/Smolen_transfer`
- Puppet Stayman structure: `https://bridge.fandom.com/wiki/Stayman`
- Texas transfers: `https://bridge.fandom.com/wiki/Texas_transfer`
