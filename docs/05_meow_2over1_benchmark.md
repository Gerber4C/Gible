# Meow 2/1 Benchmark

Platform Version: 0.0.8
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

The Meow 2/1 benchmark is the first practical Partnership Profile used to pressure-test the engine.

Profile source:

```text
backend/partnership_profiles/meow_2over1/profile.bsl.py
```

Policy functions:

```text
backend/partnership_profiles/meow_2over1/policies/
```

## Implemented Gadget Areas

The profile currently includes Gadgets for:

- natural 2/1 core openings and default pass behavior,
- two-over-one game-force continuations after opener rebids a six-card major or a side suit,
- natural minor opening structure and opener rebids,
- strong 2C with 2D waiting, natural rebids, second negative, and system-on notrump continuations,
- seat/vulnerability-sensitive preemptive openings with Ogust, Ogust placement, and forcing new-suit continuations,
- Gambling 3N,
- 1N opening, 2N opening, and direct notrump responses,
- regular Stayman and Puppet Stayman dialogue flows,
- four-way transfers over 1N,
- Texas transfers over 1N,
- quantitative notrump,
- Gerber,
- RKCB 1430,
- Kickback,
- Minorwood,
- Exclusion keycard,
- targeted king ask,
- control bidding,
- simple major raises,
- forcing 1N after a major,
- Bergen raises,
- two-way reverse Drury,
- Jacoby 2N major raises,
- Kokish/help-suit game tries,
- inverted minors,
- Crisscross minor raises,
- 2-way NMF/XYZ,
- Spiral 3344.

## Profile Policy Functions

Current profile-level policy functions include:

- `meow_opening_strong_policy`
- `meow_opening_notrump_policy`
- `meow_opening_fourth_seat_pass_policy`
- `meow_opening_one_level_seat_1_2_policy`
- `meow_opening_one_level_seat_3_sound_policy`
- `meow_opening_preempt_policy`
- `meow_opening_one_level_seat_3_light_policy`
- `meow_opening_one_level_seat_4_policy`
- `meow_opening_pass_policy`
- `meow_slam_tool_route`
- `meow_transfer_completion_route`
- `meow_1n_private_route_policy`
- `meow_1n_two_suiter_policy`
- `meow_1n_weak_partscore_policy`
- `meow_1n_major_transfer_policy`
- `meow_1n_major_search_policy`
- `meow_1n_terminal_notrump_policy`
- `meow_major_response_spade_over_heart_policy`
- `meow_major_response_two_over_one_policy`
- `meow_major_response_forcing_notrump_policy`
- `meow_two_over_one_opener_major_rebid`
- `meow_two_over_one_opener_side_suit_rebid`
- `meow_two_over_one_responder_placement`
- `meow_two_over_one_responder_after_side_suit`
- `meow_major_raise_jacoby_policy`
- `meow_major_raise_bergen_policy`
- `meow_major_raise_simple_policy`
- `meow_bergen_opener_continuation_policy`
- `meow_drury_opener_continuation_policy`
- `meow_jacoby_opener_continuation_policy`
- `meow_jacoby_responder_placement_policy`
- `meow_control_bidding_policy`
- `meow_minor_response_route`
- `meow_inverted_minor_continuation_route`
- `meow_crisscross_minor_continuation_route`
- `meow_strong_two_club_response`
- `meow_strong_two_club_opener_rebid`
- `meow_strong_two_club_responder_rebid`
- `meow_strong_two_club_after_second_negative`
- `meow_weak_two_responder_route`
- `meow_ogust_answer_route`
- `meow_ogust_responder_placement`
- `meow_new_suit_forcing_rebid`
- `meow_game_try_route`
- `meow_forcing_notrump_opener_rebid`
- `meow_minor_opener_rebid`
- `meow_minor_responder_rebid`
- `meow_puppet_stayman_route`

These functions are the current home for judgmental bridge choices. They receive the complete eligible candidate pool and return the selected candidate.

## Reference Basis

The benchmark is not trying to be universal. The current choices follow mainstream 2/1 and Standard American teaching patterns:

- Rule of 20 for light first- and second-seat one-level openings: `https://blueberrybridge.com/bridge-bidding/the-rule-of-20/`
- Longer-suit and equal-length higher-ranking opening style: `https://www.bridge7.com/xbric2.aspx`
- Walsh responses over 1C: `https://www.acblunit390.org/Simon/walsh1club.htm`
- Weak-two shape and seat style: `https://bridge.fandom.com/wiki/Weak_two_bid`
- Ogust over weak twos: `https://www.bridgebum.com/ogust.php`
- New suits forcing after weak twos / RONF style: `https://bridge.fandom.com/wiki/Weak_two_bid`
- Strong 2C with 2D waiting, 2N/3N rebids, and second negative: `https://www.bridgebum.com/strong_2c.php`
- 2/1 game forcing and forcing 1N: `https://www.bridgebum.com/two_over_one.php`
- Jacoby 2N as a game-forcing major raise: `https://loebbridge.com/index.php/learning/jacoby-2nt`

## Judgment Style

The benchmark now has explicit policies for several common judgment calls:

- First- and second-seat one-level openings use a practical Rule-of-20 gate. A flat 11-count can pass; a shapely 10- or 11-count can open when HCP plus the two longest suit lengths reaches 20.
- With 5-5 majors, opener chooses spades. With unequal 6-5 major shapes, opener chooses the longer suit, so 6 hearts and 5 spades opens 1H.
- Weak-two openings are seat and vulnerability sensitive. First and second seat avoid side 4-card majors, side 5-card suits, side voids, and 7-card suits. Third seat is more permissive.
- Seven-card weak preempt hands use the three level rather than a weak two when the preempt policy allows it.
- After a two-level preempt, responder can pass, raise, bid game, bid 2N Ogust, or bid a forcing new suit. The Policy Function chooses among those routes from the whole candidate pool.
- Ogust answers use the benchmark structure: 3C minimum/poor suit, 3D minimum/good suit, 3H maximum/poor suit, 3S maximum/good suit, and 3N solid suit.
- After an Ogust answer, responder places the contract. Minimum answers can be signed off at three of the preempt suit; stronger answers and stronger responder hands continue to game.
- A forcing new suit over a weak two asks opener to describe further. The current executable layer supports raising responder's suit with support or rebidding the preempt suit without a better action.
- Over 1C, the minor-response policy uses Walsh-style judgment: below game-forcing values, responder usually bids a 4-card major before diamonds; with game-forcing values and 5+ diamonds, responder can bid 1D first and show the major later.
- Over one of a minor, direct weak jump shifts in majors are weak and natural, while inverted minors and Crisscross minor raises handle stronger support hands without a 4-card major.
- After a 2/1 game-forcing response and opener's six-card-major rebid, responder places game in the major with a 6-2 or better fit and places 3N without that fit.
- After a 2/1 game-forcing response and opener's side-suit rebid, responder places game in that side major with four-card support or places 3N over a side-minor rebid.

## Strong 2C

The deep technical design and refactor audit for opening families lives in:

```text
docs/10_meow_opening_technical_design.md
```

The benchmark uses 2C as an artificial strong opening.

Executable agreements:

- 2C is selected for balanced hands above the direct 2N opening range and for sufficiently strong unbalanced hands.
- 2D is the normal waiting response. Immediate positive suit responses are not active in this benchmark profile.
- After 2C-2D:
  - 2N shows 22-24 balanced or near-balanced.
  - 3N shows 25-27 balanced or near-balanced.
  - 2H, 2S, 3C, and 3D are natural and forcing.
- Second negative is available after opener's natural suit rebid:
  - 2C-2D-2H-3C,
  - 2C-2D-2S-3C,
  - 2C-2D-3C-3D,
  - 2C-2D-3D-3N.
- After a second negative over a major rebid, opener can place four of the major with enough playing strength or stop lower with a less self-sufficient hand.
- After 2C-2D-2N, the benchmark has an adapter for notrump continuations:
  - pass with a true bust,
  - 3C Puppet Stayman,
  - 3D transfer to hearts,
  - 3H transfer to spades,
  - 3S minor suit Stayman,
  - 3N natural to play.

This adapter is intentionally executable now. A later engine refactor should make "system-on after notrump rebid" a reusable profile mechanism rather than repeated context entries.

## 1N Structure

The deep technical design and refactor audit for the 1N area lives in:

```text
docs/09_meow_1nt_technical_design.md
```

The current benchmark uses:

- 1N opening: 15-17 balanced.
- 2C regular Stayman.
- 2D transfer to hearts.
- 2H transfer to spades.
- 2S transfer to clubs.
- 2N transfer to diamonds.
- 3C Puppet Stayman over 1N, game forcing, normally with at least one four-card major and no five-card major.
- 3D 5-5 minors, game forcing.
- 3H 5-5 majors, invitational.
- 3S 5-5 majors, game forcing.
- 3N natural to play.
- 4D Texas transfer to hearts.
- 4H Texas transfer to spades.
- 4N quantitative when notrump is in focus and no suit is agreed.

Major-suit transfer superaccepts:

- `1N P 2D P 3H` superaccepts hearts with four-card support and maximum values.
- `1N P 2H P 3S` superaccepts spades with four-card support and maximum values.

Minor transfers use the gap as a superaccept when opener has honor-third or better support.

Puppet Stayman over 1N is represented as a dialogue flow rather than one loose `3C` call:

- `1N P 3C` starts the Puppet dialogue.
- `3D` denies a five-card major and shows at least one four-card major.
- `3H` shows five or more hearts.
- `3S` shows five or more spades.
- `3N` denies a four- or five-card major.
- After `3D`, responder can show four spades with `3H`, four hearts with `3S`, or both majors with `4D`.
- Opener then places `3N`, `4H`, or `4S` from exact length evidence.

The Puppet implementation records `opener.length.<suit>`, `responder.length.<suit>`, and `partnership.fit.<suit>` evidence. A 4-4 major fit and a 5-3 major fit are therefore different states, not one generic fit flag.

## Major Raises

After first- or second-seat major openings:

- simple raise uses three-card support and non-forcing values,
- Bergen handles four-card preemptive, constructive, and limit raises,
- Jacoby 2N handles game-forcing four-card support,
- Kokish/help-suit game tries operate after simple raises.

After third- or fourth-seat major openings:

- two-way reverse Drury is available by a passed hand.

Executable continuation coverage:

- Bergen constructive and limit raises now include opener's practical accept/decline placement.
- Preemptive Bergen raises can be passed or raised to game by opener by strength.
- Drury continuations can stop in two of the major or bid game.
- Jacoby 2N continuations can show side shortness, show extras without shortness, place game, or leave room for reusable slam tools when the responder has a slam hand.

## Minor Openings

The profile includes:

- natural 1C and 1D openings,
- one-level responses,
- Walsh-style 1C response judgment,
- weak jump shifts in majors,
- natural 1N, 2N, and 3N responses,
- inverted minors,
- Crisscross game-forcing minor raises,
- opener notrump rebids,
- opener reverse,
- strong jump shift,
- simple and jump raises of responder's major,
- 2-way NMF/XYZ,
- Spiral 3344.

Crisscross minor raises now include both the notrump-game route and a practical fallback route to five of the agreed minor when opener declines notrump.

## Slam Tools

Slam tools are standalone Gadgets and communicate through state such as `agreed_suit`, `notrump_focus`, `keycard_context`, and active Frames.

This keeps RKCB reusable after:

- Texas transfer,
- simple major raise,
- transfer superaccept,
- other future suit-agreement routes.

Control bidding is generated from a compact Python table across agreed suits, with a Policy Function deciding when to show a control before keycard. The current benchmark therefore tests the reusable mechanism instead of hard-coding one isolated `4D` example.

## Test Coverage

The benchmark is covered by:

- 159 curated single-call bidding fixtures,
- 27 full-auction simulations,
- parser, legality, and matcher fixtures,
- infrastructure tests for Policy Functions, Private Route memory, Frames, and generated system notes.

The fixture companion is:

```text
backend/partnership_profiles/meow_2over1/tests/test_cases.md
```

## Roadmap Boundary

The benchmark is the executable reference profile. Open design and coverage work lives in `docs/08_roadmap_todo.md` so this document stays focused on the current profile behavior.
