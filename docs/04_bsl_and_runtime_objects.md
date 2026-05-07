# BSL And Runtime Objects

Platform Version: 0.0.7
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

This document defines the current authoring language and runtime object model.

## Current Language Position

Partner currently uses Python-shaped BSL files:

```text
*.bsl.py
```

These files are not executed as ordinary Python. They are parsed with Python's `ast` module, checked against a whitelist, and compiled into runtime objects.

Policy files are separate:

```text
*.policy.py
```

Policy files are restricted Python modules. They define functions that receive `(ctx, candidates)` and return an actual candidate.

There is no separate user-facing IR language in the current implementation. The engine has a runtime object model. Future export formats can serialize that model, but source authoring is BSL plus Policy Functions.

## Profile

```python
Profile(
    id='meow_2over1',
    name='Meow 2/1 Benchmark',
    version='0.1.0',
    author={'name': 'Meow Li'},
    gadgets=['meow_one_notrump_opening', 'meow_rkcb_1430'],
)
```

A Profile lists Gadgets and profile-level policy files.

## Gadget

```python
Gadget(
    id='meow_rkcb_1430',
    namespace='meow_2over1',
    name='Meow RKCB 1430',
    version='0.1.0',
    author={'name': 'Meow Li'},
)
```

A Gadget is the portable unit of bridge agreement source.

## Call Specification

```python
Call(
    id='cs_1',
    when=Auction('1NP'),
    bid=Bid('2D'),
    selection=Selection(criteria=[
        Criterion('five_hearts', condition=self.hearts >= 5),
    ]),
    meaning=Meaning(action='transfer', target_suit=H, alertable=True),
    effects=[State('transfer', target_suit=H, status='pending')],
)
```

Important fields:

- `id`: short stable object ID inside a Gadget.
- `when` or `context`: visible auction context.
- `bid`: absolute call or relative-call template.
- `requires`: public state requirement.
- `selection`: hand/environment criteria for candidate generation.
- `meaning`: public partnership meaning.
- `effects`: public state records created when the call is replayed.
- `description`: maintainer-facing prose.
- `system_notes`: generated-notes prose.

## Selection Criteria

BSL supports concise Python-like expressions:

```python
Criterion('game_values', condition=self.hcp >= 10)
Criterion('five_five_majors', condition=self.spades >= 5 and self.hearts >= 5)
Criterion('has_diamond_control', condition=HasRank(D, 'A') or HasRank(D, 'K'))
```

Expressions compile to structured evaluator trees.

## Named Evaluator

Named Evaluators are reusable structured calculations:

```python
Evaluator(
    id='eval_minor_honor_third',
    returns=Honors(target_suit, top=3) >= 1 and Length(target_suit) >= 3,
)
```

The current evaluator system is intentionally limited. More bridge calculations should be added as reusable helpers or safe policy functions, not as one-off engine fields.

## Policy Function

Policy Functions make whole-pool judgment.

```python
def meow_major_raise_route(ctx, candidates):
    opening = ctx.state.records_matching('major_opening')[-1]
    suit = opening.attributes['target_suit']
    if ctx.hand.length(suit) >= 4 and ctx.hand.hcp >= 13:
        return _candidate_with(candidates, action_type='jacoby_2n', target_suit=suit)
    return None

selection_policies = [meow_major_raise_route]
```

This is where the profile decides among alternatives such as simple raise, Bergen, Jacoby 2N, splinter, direct game, or slam exploration.

## Frame

A Frame records an active public auction context.

Examples:

- major transfer
- RKCB 1430
- Gerber
- control bidding
- targeted king ask

A Frame can carry:

- `frame_type`
- variables
- current stage
- obligation
- close behavior

Frames are public auction state. They are not the same as private route motivation.

## Private Route

A Private Route records why the same seat selected an entry call.

Example: over `1N`, responder may bid `2D` as:

- weak transfer and pass route,
- invitational route,
- game route,
- slam route.

The public call meaning is still transfer to hearts. The private route is internal training and continuation memory for the bidder.

Current route node kinds include:

- `wait_for_call`
- `make_call`
- `end_route`
- `fail_route`

## Relative Calls

The current engine supports first relative-call helpers in `call_space.py`, including steps after a stored ask call or the last contract. Future work should expand this for relay systems, Kickback, DOPI/ROPI, cheapest bid, jumps, and new-suit relationships.

## State Records

State records are flexible evidence. Examples:

```python
State('agreed_suit', suit=S, source='simple_raise')
State('opener.hcp', owner='opener', min_value=15, max_value=17)
State('opener.length.S', owner='opener', min_value=5)
```

`StateView` combines range evidence and exposes safe undefined values. The engine does not require every user to share a global semantic variable list. A profile author can define profile-specific state fields and policy functions.

## Same-Call Ambiguity

The same visible call can have different meanings. The engine diagnoses ambiguous same-call candidates unless a Private Route candidate clearly maps to an implemented Call Specification. This is how `4N` can be quantitative in one context and RKCB in another.
