# Partner User Guide

Platform Version: 0.0.8
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

This guide explains how to use the current local prototype and how advanced users can start authoring Gadgets.

## Browser Workspace

Start the local browser workspace from the repository root:

```bat
run_local.cmd
```

Keep that CMD window open while using Partner. It starts the backend on port `8765` and the frontend on port `5173`.

Manual startup is also available:

Backend:

```powershell
C:\Users\paw_l\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe backend\server.py
```

Frontend:

```powershell
C:\Users\paw_l\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe frontend\server.mjs
```

Open:

```text
http://127.0.0.1:5173
```

The browser workspace can list Partnership Profiles, open profile files, edit and save BSL/policy/test documents, display hands and auctions, ask for one bid, and simulate a partnership auction with controlled North/South hands.

Frontend engineering details live in `docs/07_frontend_architecture.md`.

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
backend/partnership_profiles/<profile_id>/
  profile.bsl.py
  gadgets/
    <gadget_id>/
  policies/
    *.policy.py
  tests/
    cases/
    test_cases.md
```

The current main profile is:

```text
backend/partnership_profiles/meow_2over1/profile.bsl.py
```

It lists the Gadgets that make up the profile and loads profile-level Policy Functions.

## Gadgets

Each Gadget lives in its own directory:

```text
backend/partnership_profiles/<profile_id>/gadgets/<gadget_id>/
  gadget.bsl.py
  *.policy.py
```

A Gadget can define:

- Call Specifications.
- Frames.
- Private Routes.
- Named Evaluators.
- Gadget-local Policy Functions.

The current source style is class-authored Python BSL. Each Gadget is a class derived from `Gadget`; its `build()` method creates calls, frames, routes, and evaluators with simple field assignments.

## Minimal Call Specification Example

```python
def cs_1_applies(ctx):
    return ctx.hand.length('H') >= 5


class ExampleTransferGadget(Gadget):
    id = 'example_transfer'
    namespace = 'meow_2over1'
    name = 'Example Transfer'
    version = '0.1.0'
    author = Author('Meow Li')

    def build(self):
        call = self.call('cs_1')
        call.when = '1NP'
        call.bid = '2D'
        call.applies = cs_1_applies

        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['directive', 'context_initiating']
        call.meaning.action = 'transfer'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.acbl_explanation = 'hearts'

        effect = call.effect('transfer')
        effect.target_suit = 'H'
        effect.status = 'pending'

        call.description = 'Responder bids 2D as a transfer to hearts.'
        call.system_notes = 'After 1N, 2D transfers to hearts.'
```

The call is eligible only when the auction context matches and the Python `applies` function returns true. The public meaning says what the partnership agreement is. Effects create public state records used by later calls.

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

policy_functions = [meow_notrump_response_route]
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
backend/partnership_profiles/meow_2over1/tests/test_cases.md
```

When test fixtures change, update that document too.
