# User Manual

Platform Version: 0.0.6
Author: Meow Li
Copyright: Copyright (c) 2026 Meow Li. All Rights Reserved.

This manual explains how users think about Partner and how advanced users author Convention Sets and Conventions. Planned work and open questions belong in `docs/todo.md`.

## 1. Product Layers

Partner has two product layers.

The first layer is **Convention Set authoring and execution**. Users define agreements, edit Conventions, share files, generate formal system notes, and ask the engine what a bot partner should bid.

The second layer is **tournament and inter-user play**. Users bring their Convention Sets into human-plus-custom-bot practice, challenges, and analytics.

The current project is focused on the first layer.

## 2. Basic Notation

Canonical calls:

```text
P = Pass
X = Double
R = Redouble
C = Clubs
D = Diamonds
H = Hearts
S = Spades
N = Notrump
```

Contract calls combine level and suit:

```text
1C 1D 1H 1S 1N ... 7N
```

`1NT` is accepted as input and normalized to `1N`.

Seats are absolute and lowercase:

```text
n e s w
```

Vulnerability values:

```text
none ns ew both
```

## 3. Asking For A Bid

A bid request supplies visible bridge context:

```json
{
  "convention_set": {"id": "expert_2over1"},
  "seat": "n",
  "auction": "1NP2DP",
  "hand": "SAQ74HKJ83DA62CQ5",
  "environment": {
    "dealer": "n",
    "vulnerability": "none",
    "scoring": "IMP"
  }
}
```

The API does not accept hidden state. If a transfer, force, or plan is active, the engine reconstructs it from the auction and active Conventions.

## 4. Running A Full Auction Simulation

A simulation request supplies a Convention Set and one or more absolute-seat hands:

```json
{
  "convention_set": {"id": "meow_2over1"},
  "hands": {
    "n": "SAQJ76H82DQ82CAJ3",
    "s": "SK98H74DKJ7CK9852"
  },
  "environment": {
    "dealer": "n",
    "vulnerability": "none",
    "scoring": "IMP"
  }
}
```

The current simulator asks the engine to choose calls for seats with supplied hands. Seats without supplied hands automatically pass. This is enough for early partnership benchmark tests such as:

```text
1S P 2S P 3D P 4S P P P
```

The returned record includes the compact auction, each call, and the normal explanation output for calls selected by the engine.

## 5. Hand Strings

Raw hand input uses one compact string:

```text
H8763SK10C2DAKQ987
```

This means:

```text
H 8763
S K10
C 2
D AKQ987
```

Input behavior:

- Suit markers are `S H D C`.
- Suits can appear in any order.
- A suit can appear more than once; sections are concatenated.
- `10` and `T` both mean ten.
- `x` means an unknown small card placeholder.
- `-` marks a void.
- A complete raw hand should contain 13 cards.

Invalid hands fail clearly, including wrong count, repeated known cards, unknown symbols, rank text before any suit marker, and a void marker mixed with cards.

## 6. Reading An Explanation

Partner separates explanation into two layers.

**Public meaning** is the partnership disclosure layer. It says what the selected call means.

**Internal origin** is the training and debugging layer. It records the selected object, compared candidates, semantic facts, typed auction-state variables, active frames, possible plans, and the selection policy.

When reviewing an engine result, inspect:

- selected call,
- public meaning,
- Convention origin,
- Call Specification origin,
- compared candidates,
- structured criteria,
- recovered auction state such as HCP ranges, denied suit lengths, force status, and private route purpose,
- active Protocol Frames,
- possible Bidding Plans,
- diagnostics.

Diagnostics mean the selected Convention Set may be incomplete, ambiguous, or outside the implemented agreement.

## 7. Convention Sets And Conventions

A **Convention Set** is a complete playable partnership agreement selected by the user.

A **Convention** is a portable agreement module. A Convention may define public meanings, Call Specifications, Protocol Frames, Bidding Plans, Call Selection Policies, alertability data, and system-note text.

A foundational 2/1 opening structure may be called the base agreement in the UI. Technically it is still a Convention.

Keep Conventions modular. For example, minor opening structure, inverted minors, Crisscross raises, two-way NMF/XYZ, regular Stayman, Puppet Stayman, four-way transfers, Texas transfers, quantitative notrump, Gerber, control bidding, RKCB, Kickback, Minorwood, Exclusion keycard, targeted king asks, Bergen raises, Drury, Jacoby 2N, Kokish game tries, preemptive openings, and Gambling 3N should live as separate Conventions so a Convention Set can include or exclude each one independently.

Reusable Conventions should communicate through structured semantic state. For example, Texas transfers, minor-transfer superaccepts, and natural simple raises may set `agreed_suit`, while standalone slam Conventions consume `agreed_suit`; those slam Conventions should not live inside any one source Convention. Quantitative notrump can use the same call, `4N`, but require notrump focus and no agreed suit.

Some inferred information is scalar or range-like rather than a yes/no fact. For example, `1C-1D-1N` can record opener as `12-14`, balanced, and denying four-card hearts and spades. `1C-1H-1S` records that opener has shown spades; it does not by itself mean "denies a four-card major." A later artificial `2D` can be chosen because responder needs to establish a game force before rebidding a long heart suit.

Slam examples in the current benchmark:

- `4D` can be a diamond control bid after hearts are agreed.
- `4C` can be Gerber when notrump is the focus and no suit is agreed.
- `4S` can be Kickback for hearts.
- `4D` can be Minorwood when diamonds are agreed.
- `5D` can be Exclusion keycard for hearts when the asker has a diamond void.
- `5N` can be a targeted diamond-king ask after heart keycard information.

These examples are deliberately separate Conventions. The engine decides among them by visible auction legality, recovered semantic state, hand expressions, and Call Selection Policies.

Minor-opening examples in the current benchmark:

- After `1C`, a one-level major response may bypass diamonds.
- `1C-2C` and `1D-2D` are inverted minor raises: invitational or better, alertable, and forcing to `2N` or three of the agreed minor.
- `1C-2D` and `1D-3C` are Crisscross game-forcing minor raises.
- After a minor opening, two-level major jump shifts are weak and alertable in the benchmark metadata.
- Two-way NMF/XYZ uses `2C` as a relay to `2D`, `2D` as game forcing, and `2N` as a transfer to `3C` for weak club drop-dead routes.
- Weak two and three-level preempts use seat and vulnerability evaluators.
- Gambling `3N` is alertable and shows a solid long minor with no outside ace or king.

Current file locations:

```text
backend/convention_sets/
backend/conventions/
```

Human-authored files should use real YAML. JSON-compatible YAML remains acceptable for generated artifacts and tooling.

The technical YAML/IR language is specified in:

```text
docs/ir_language_spec.md
```

## 8. Convention Directory Shape

Each Convention lives in its own directory:

```text
backend/conventions/four_way_jacoby_transfer/
  convention.yaml
  notrump_responses.yaml
  continuations_hearts.yaml
  protocols_major_transfer.yaml
  selection_after_1nt.yaml
```

Metadata example:

```yaml
id: four_way_jacoby_transfer
namespace: notrump_response
name: Four-Way Jacoby Transfer
version: 0.1.0
description: >
  Prototype after-1N transfer Convention.
author:
  name: Partner Prototype
```

Call Specification example:

```yaml
call_specifications:
  - id: cs_1
    description: Responder bids 2D over 1N as a transfer to hearts with at least five hearts.
    system_notes: After 1N, 2D is artificial and transfers to hearts. The ACBL explanation is "hearts."
    context:
      auction_pattern: "1NP"
      seat_positions: [1, 2, 3, 4]
    call: 2D
    selection:
      applicability:
        all:
          - self.hearts:
              min: 5
      algorithm: weighted_score
      criteria:
        - criterion_id: jacoby_transfer_heart_length
          evaluator: min_value
          input: self.hearts
          min: 5
          weight: 60
    meaning:
      nature_labels: [artificial, conventional]
      call_act_types: [directive, context_initiating, forcing]
      action_type: transfer
      target_suit: H
      forcing_status: forcing_one_round
      alertable: true
      acbl_explanation: hearts
    effects:
      - fact_type: transfer
        source_role: responder
        target_role: opener
        target_suit: H
        status: pending
```

Key fields:

- `id`: short stable object handle.
- `description`: human editor explanation.
- `system_notes`: generated-notes text.
- `context`: visible auction match.
- `call`: selected or interpreted call.
- `selection`: current-hand criteria.
- `meaning`: public partnership meaning.
- `effects`: machine-readable semantic consequences.

## 9. Seat Positions

The machine always matches visible auction strings. `seat_positions` is shorthand for initial-pass variants.

Example:

```yaml
context:
  auction_pattern: ""
  seat_positions: [1, 2, 3, 4]
```

This covers:

```text
""   = seat 1
"P"  = seat 2
"PP" = seat 3
"PPP" = seat 4
```

For a continuation:

```yaml
context:
  auction_pattern: "1NP"
  seat_positions: [1, 2, 3, 4]
```

This covers after-1N response positions such as `1NP`, `P1NP`, `PP1NP`, and `PPP1NP`.

Vulnerability is not part of the auction pattern. It belongs in selection or evaluator logic.

## 10. Plans, Protocols, And Selection

Many calls are not only descriptions of the bidder's hand.

Example:

```text
1N P 2D
```

Publicly, `2D` may mean transfer to hearts. Internally, the bidder may be choosing a route: transfer then pass, transfer then invite, transfer then show a second suit, Texas transfer, Smolen, or slam exploration.

Partner uses these formal object types:

- **Call Specification**: defines one call in a context.
- **Call Act Type**: describes the structural role of the call.
- **Protocol Frame**: live context created by the auction.
- **Bidding Plan**: internal multi-step route.
- **Call Selection Policy**: explicit algorithm for choosing among candidates.
- **Named Evaluator**: reusable calculation.
- **Relay Automaton**: step-based relay machinery.

For judgmental choices such as `1H` versus `1N`, the comparison should live in a Call Selection Policy, not in a hidden priority inside one candidate.

## 11. Bidding Plan Shape

A Bidding Plan has fixed workflow vocabulary.

Example:

```yaml
bidding_plans:
  - id: plan_1
    description: Prototype plan for hands that start with a Jacoby transfer to hearts.
    owner: responder
    goal: place_contract
    context:
      auction_pattern: "1NP"
      seat_positions: [1, 2, 3, 4]
    preconditions:
      self.hearts:
        min: 5
    entry_call: 2D
    workflow:
      start: wait_1
      nodes:
        wait_1:
          kind: wait_for_call
          actor: opener
          branches:
            - when:
                kind: call_is
                value: 2H
              goto: select_1
            - when:
                kind: call_is
                value: 3H
              goto: select_1
        select_1:
          kind: select_by_policy
          policy: policy_2
          terminal_if: final_contract_placed
```

Allowed plan node kinds currently include `make_call`, `wait_for_call`, `branch`, `select_by_policy`, `enter_protocol`, `update_plan_state`, `end_plan`, and `fail_plan`.

Allowed branch predicate kinds currently include `call_is`, `call_act_type_is`, `protocol_frame_matches`, `state_has`, `state_missing`, `hand_predicate`, `environment_predicate`, `interference_level`, and `obligation_status`.

## 12. Generated System Notes

The backend can generate formal Markdown notes from a loaded Convention Set:

```python
from app import system_notes

result = system_notes({"convention_set": {"id": "expert_2over1"}})
print(result["content"])
```

The generated notes are based on structured IR. `description` and `system_notes` text is included for human readability, but executable behavior comes from structured fields.

Target workflow:

```text
Convention Set and Convention YAML -> formal system notes
```

Future workflow:

```text
human notes -> LLM draft -> BSL or IR -> validation -> user approval -> Convention files
```

LLM-generated files should remain drafts until validated, tested, edited, and approved.

## 13. Authoring Principles

Convention authors should:

- Use short stable IDs.
- Put one Convention per directory.
- Put public disclosure in `meaning`.
- Put machine consequences in `effects`.
- Use `state:` effects for scalar/range or private route state that should be recoverable during auction replay.
- Use structured criteria as the source of bid selection.
- Mark alertability explicitly until automated alert analysis exists.
- Use Call Selection Policies for judgment across alternatives.
- Use Bidding Plans for multi-step routes.
- Use Protocol Frames for live auction context.
- Use Relay Automata for step-based relay sequences.
- Keep public meaning separate from internal origin.
- Treat generated notes as output from structured objects, not as the executable source.

## 14. Hand And Deal Workspace

The authoring layer should include a workspace for:

- entering one hand,
- entering a full deal,
- random dealing,
- importing deal files such as PBN,
- choosing Convention Set, seat, dealer, vulnerability, and scoring,
- stepping through the auction,
- asking for the next bid,
- running a shared test-case pool against one or more Convention Sets,
- comparing auction results, final contracts, diagnostics, and explanation traces,
- reviewing expert comments or double-dummy reference results when a test case provides them,
- inspecting public meaning, internal origin, candidates, frames, plans, and diagnostics.

This workspace belongs to Convention Set authoring and training. It is separate from tournament features.

## 15. Test Case Workflow

Behavior examples live in YAML files under `backend/tests/cases/`.

Project tests are currently local fixtures. A future user-facing feature should promote this idea into shared test-case pools: curated or user-created collections of deals and auction contexts that can be run against different Convention Sets. The comparison report should show where systems choose different auctions, where they reach different contracts, where diagnostics appear, and how those results compare with expert or double-dummy references when available.

Add bidding examples to:

```text
backend/tests/cases/bidding.yaml
```

Add matcher examples to:

```text
backend/tests/cases/matcher.yaml
```

Add hand parser examples to:

```text
backend/tests/cases/hands.yaml
```

Add complete partnership simulation examples to:

```text
backend/tests/cases/full_auctions.yaml
```

The readable companion is:

```text
backend/tests/test_cases.md
```

Update the companion document whenever fixture cases change.
