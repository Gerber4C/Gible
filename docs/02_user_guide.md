# Gible User Guide

Platform Version: 0.0.8
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

This guide explains how to use the current local prototype and how advanced users can start authoring Gadgets.

## Browser Workspace

Start the local browser workspace from the repository root:

```bat
gible.cmd
```

Keep that CMD window open while using Gible. Press Enter or Ctrl+C to stop services started by this launcher. See the root README for prerequisites, runtime discovery, and macOS/Linux startup. It starts the backend on port `8765` and the frontend on port `5173`.

On Windows, use `kill.cmd` to stop existing recognized Gible services, or
`restart.cmd` to stop them and start a new `gible.cmd` session. The normal
`gible.cmd` continues to reuse an already running service.

Manual startup is also available:

Backend:

```powershell
python backend\server.py
```

Frontend:

```powershell
node frontend\server.mjs
```

Open:

```text
http://127.0.0.1:5173
```

The browser workspace can list Partnership Profiles, open profile files, edit and save BSL/policy/test documents, display hands and auctions, ask for one bid, and simulate a partnership auction with controlled North/South hands.

Frontend engineering details live in `docs/07_frontend_architecture.md`.

## Table: Entering And Dealing Hands

Each visible hand has four separate inputs, ordered spades, hearts, diamonds,
clubs. Enter ranks only: `AKQJT98765432`. Lowercase, spaces, and `10` for ten
are accepted and normalized when leaving the field. Leave a field blank or
enter `-` for a void. Unknown-card placeholders such as `X` are not accepted
in the concrete four-hand deal editor.

At the left edge, Left Arrow moves to the previous suit's end; at the right
edge, Right Arrow moves to the next suit's beginning. Ordinary movement and
text selection remain unchanged. The first and last suits do not wrap.
Tab and Shift+Tab also work normally.

Validation checks invalid ranks, repeated cards within a hand, cards shared
by different seats, and exactly 13 cards per seat. Errors appear beside the
hand and invalid suit fields are highlighted. Playback is disabled until all
four hands are valid, including hidden East/West hands. Correcting the hands
refreshes a previously requested auction automatically.

**Random deal** replaces all four hands with a shuffled 52-card deck, deals
13 unique cards per seat, sorts each suit, and clears the previous auction.
Dealer and vulnerability stay as selected. **Show E/W hands** and **Hide E/W
hands** reveal or conceal editable opponents' holdings without changing them.
Narrow windows allow vertical scrolling within the table area.

**Fill E/W hands** keeps North and South unchanged and randomly distributes
the remaining 26 cards to East and West, 13 each. Click again to generate
another distribution. North and South must each contain 13 valid cards with
no duplicates between them. Existing East/West cards are replaced, even if
empty or invalid. Their visibility, dealer, and vulnerability are preserved.

The current auction remains North/South partnership practice; East and West
automatically pass. Revealing their cards does not change the bidding mode.

## Basic Notation

The Table also has an optional **Contract analysis** panel. Step to a North or
South turn, enter explicit targets such as `4HN, 6HN` (four/six hearts by
North), and choose **Analyze**. The result shows how often each target was
made in sampled deals consistent with the visible auction. This is a review
tool; it does not choose the next bid. The panel requires an optional DDS
solver installation described in the repository README. If a public call has
no coded sampling meaning, analysis reports that gap rather than silently
ignoring the call.

At the first response to 1NT, **Compare bidding routes** accepts one to three
first calls, such as `4C, 2D`. The routes use the same sampled possible deals;
each later partnership call sees only that bidder's hand and the public auction.
The report separates completed auctions, made/failed final contracts, and
blocked or unavailable continuations. East and West pass in this first
experiment. A fixed seed reproduces the report. A route with no authored
continuation is marked unavailable or blocked; it is not scored as a failure.
This report does not choose a bid. Daqiush's game-only South African Texas
branch can finish, while Jacoby remains unavailable until its selection and
continuations are authored.

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
python -m unittest tests.test_fixture_cases -q
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
