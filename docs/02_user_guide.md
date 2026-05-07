# Partner User Guide

Platform Version: 0.0.7
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

This guide explains how to use the current backend prototype and how advanced users can start authoring Gadgets.

## Basic Notation

Calls use compact notation:

- `N` means notrump.
- `C`, `D`, `H`, `S` mean clubs, diamonds, hearts, spades.
- `P` means pass.
- `X` means double.
- `R` means redouble.

Examples:

- `1N P 2D P` can be written as `1NP2DP`.
- `1S P 2S P 3D P 4S` can be written as `1SP2SP3DP4S`.

Hands are compact strings containing suits and ranks:

- `SAQ7HKJ8DA762CQ54`
- `S-HAKQJ87D53CKQ2`

The parser accepts compact bridge rank notation with `T` for ten. The internal representation is structured after parsing.

## Asking For A Bid

The backend entry point is `backend/app.py`.

Example request shape:

```json
{
  "profile": {"id": "meow_2over1"},
  "auction": "1NP2DP3HP",
  "hand": "SA2HAKQJ87DA3CKQ2",
  "environment": {
    "dealer": "n",
    "vulnerability": "none",
    "scoring": "IMP"
  }
}
```

The response includes:

- `call`: selected call.
- `public_meaning`: the partnership meaning of the selected call.
- `internal_origin`: compared candidates, selected Policy Function, state records, Frames, and Private Routes.
- `diagnostics`: ambiguity or fallback messages.
- `private_memory`: same-seat private route memory for later calls in the same deal.

## Partnership Profiles

A Partnership Profile is the selected bridge agreement package. Current profiles live in:

```text
backend/profiles/<profile_id>/
  profile.bsl.py
  policies/
    *.policy.py
```

The current main profile is:

```text
backend/profiles/meow_2over1/profile.bsl.py
```

It lists the Gadgets that make up the profile and loads profile-level Policy Functions.

## Gadgets

Each Gadget lives in its own directory:

```text
backend/gadgets/<gadget_id>/
  gadget.bsl.py
  *.bsl.py
  *.policy.py
```

A Gadget can define:

- Call Specifications.
- Frames.
- Private Routes.
- Named Evaluators.
- Gadget-local Policy Functions.

The current source style is Python-shaped BSL. It is parsed by the platform, not executed as normal Python.

## Minimal Call Specification Example

```python
Call(
    id='cs_1',
    when=Auction('1NP'),
    bid=Bid('2D'),
    selection=Selection(criteria=[
        Criterion('five_hearts', condition=self.hearts >= 5),
    ]),
    meaning=Meaning(
        nature=['artificial', 'conventional'],
        acts=['directive', 'context_initiating'],
        action='transfer',
        target_suit=H,
        alertable=True,
        acbl_explanation='hearts',
    ),
    effects=[
        State('transfer', target_suit=H, status='pending'),
    ],
    description='Responder bids 2D as a transfer to hearts.',
    system_notes='After 1N, 2D transfers to hearts.',
)
```

The call is eligible only when the auction context matches and the selection criteria pass. The public meaning says what the partnership agreement is. Effects create public state records used by later calls.

## Policy Functions

Call Specifications decide what calls are eligible. Policy Functions decide among eligible candidates.

Example shape:

```python
def meow_notrump_response_route(ctx, candidates):
    if ctx.auction.calls[-2:] != ('1N', 'P'):
        return None
    if ctx.hand.length('H') >= 6 and ctx.hand.hcp >= 10:
        return candidates.get('4D')
    if ctx.hand.length('H') >= 5:
        return candidates.get('2D')
    return candidates.first_available('3N', 'P')

selection_policies = [meow_notrump_response_route]
```

The function receives:

- `ctx`: auction, hand, environment, recovered public state, active Frames, active Private Routes, and private memory for this seat.
- `candidates`: the eligible candidate pool.

It returns the selected candidate or `None`.

## Generated System Notes

The platform can generate Markdown notes from loaded runtime objects. Text from `description` and `system_notes` improves readability, but executable behavior comes from structured fields.

## Testing A Profile

Run:

```powershell
C:\Users\paw_l\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest tests.test_fixture_cases -q
```

from:

```text
backend/
```

The human-readable fixture companion is:

```text
backend/tests/test_cases.md
```

When test fixtures change, update that document too.
