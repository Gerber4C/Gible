# Meow 2/1 Benchmark

Platform Version: 0.0.7
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

The Meow 2/1 benchmark is the first practical Partnership Profile used to pressure-test the engine.

Profile source:

```text
backend/profiles/meow_2over1/profile.bsl.py
```

Policy functions:

```text
backend/profiles/meow_2over1/policies/
```

## Implemented Gadget Areas

The profile currently includes Gadgets for:

- natural 2/1 core openings and default pass behavior,
- natural minor opening structure and opener rebids,
- strong 2C skeleton,
- seat/vulnerability-sensitive preemptive openings,
- Gambling 3N,
- 1N opening, 2N opening, and direct notrump responses,
- regular Stayman and Puppet Stayman stubs,
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

- `meow_opening_seat_1_2`
- `meow_opening_seat_3`
- `meow_opening_seat_4`
- `meow_notrump_response_route`
- `meow_major_response_route`
- `meow_major_raise_route`
- `meow_game_try_route`
- `meow_forcing_notrump_opener_rebid`
- `meow_minor_opener_rebid`
- `meow_minor_responder_rebid`

These functions are the current home for judgmental bridge choices. They receive the complete eligible candidate pool and return the selected candidate.

## 1N Structure

The current benchmark uses:

- 1N opening: 15-17 balanced.
- 2C regular Stayman.
- 2D transfer to hearts.
- 2H transfer to spades.
- 2S transfer to clubs.
- 2N transfer to diamonds.
- 3C Puppet Stayman over 1N.
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

## Major Raises

After first- or second-seat major openings:

- simple raise uses three-card support and non-forcing values,
- Bergen handles four-card preemptive, constructive, and limit raises,
- Jacoby 2N handles game-forcing four-card support,
- Kokish/help-suit game tries operate after simple raises.

After third- or fourth-seat major openings:

- two-way reverse Drury is available by a passed hand.

## Minor Openings

The profile includes:

- natural 1C and 1D openings,
- one-level responses,
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

## Slam Tools

Slam tools are standalone Gadgets and communicate through state such as `agreed_suit`, `notrump_focus`, `keycard_context`, and active Frames.

This keeps RKCB reusable after:

- Texas transfer,
- simple major raise,
- transfer superaccept,
- other future suit-agreement routes.

## Test Coverage

The benchmark is covered by:

- 128 single-call bidding fixtures,
- 11 full-auction simulations,
- parser, legality, and matcher fixtures,
- infrastructure tests for Policy Functions, Private Route memory, Frames, and generated system notes.

The fixture companion is:

```text
backend/tests/test_cases.md
```

## Known Limits

The benchmark is useful but not complete. Future work belongs in `docs/07_roadmap_todo.md`, especially:

- complete minor continuations,
- full 2N response structure,
- full Puppet Stayman continuations,
- full Jacoby 2N continuations,
- splinters,
- Smolen and Garbage Stayman,
- richer slam exploration,
- competitive auctions.
