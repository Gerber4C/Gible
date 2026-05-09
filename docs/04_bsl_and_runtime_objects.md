# BSL And Runtime Objects

Platform Version: 0.0.8
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

This document defines the current executable authoring model. Partner source is Python-shaped BSL plus Python Policy Functions. The source should read like bridge code: a Partnership Profile lists Gadgets, each Gadget is a class, and the Gadget builds calls, frames, private routes, and evaluators by assigning fields.

## Language Position

BSL files use:

```text
*.bsl.py
```

The BSL loader executes these files in a constrained namespace. Top-level imports are rejected. The namespace provides the authoring base classes and helper functions:

- `Profile`
- `Gadget`
- `Author`
- `Meaning`
- `State`
- `StepAfterState`
- `StepAfterLastContract`
- `Workflow`
- `WaitForCall`
- `OnCall`
- `MakeCall`
- `EndRoute`
- evaluator helpers such as `state_exists`, `state_attribute`, and `named_evaluator`

Policy files use:

```text
*.policy.py
```

Policy files define ordinary Python functions with signature `(ctx, candidates)` and register them with:

```python
policy_functions = [meow_opening_policy, meow_notrump_response_policy]
```

There is no separate user-facing IR language in the current implementation. The engine loads BSL into runtime dataclasses. Later export formats can serialize those dataclasses, including references to Python evaluator source where needed.

## Partnership Profile

A Partnership Profile is the complete partnership agreement package. It lists the Gadgets in load order and owns profile-level Policy Functions, tests, and generated notes.

```python
class Meow2over1Profile(Profile):
    id = "meow_2over1"
    name = "Meow 2/1 Benchmark"
    version = "0.1.0"
    author = Author("Meow Li")
    gadgets = [
        "meow_two_over_one_core",
        "meow_four_way_transfers_over_1n",
        "meow_rkcb_1430",
    ]
```

The profile file lives at:

```text
backend/partnership_profiles/<profile_id>/profile.bsl.py
```

## Gadget Class

A Gadget is a portable agreement module. It may define Call Specifications, Frames, Private Routes, Named Evaluators, and descriptive text.

```python
class FourWayTransfersOver1n(Gadget):
    id = "meow_four_way_transfers_over_1n"
    namespace = "meow_2over1"
    name = "Meow Four-Way Transfers Over 1N"
    version = "0.1.0"
    author = Author("Meow Li")

    def build(self):
        call = self.call("heart_transfer")
        call.when = "1NP"
        call.seats = [1, 2, 3, 4]
        call.bid = "2D"
        call.applies = has_five_hearts

        call.meaning.nature = ["artificial", "conventional"]
        call.meaning.acts = ["directive", "context_initiating"]
        call.meaning.action = "transfer"
        call.meaning.target_suit = "H"
        call.meaning.alertable = True
        call.meaning.acbl_explanation = "hearts"

        effect = call.effect("transfer")
        effect.target_suit = "H"
        effect.status = "pending"

        call.description = "Responder bids 2D as a transfer to hearts."
        call.system_notes = "After 1N, 2D transfers to hearts."
```

`self.call(id)`, `self.frame(id)`, `self.route(id)`, `self.evaluator(id)`, and `self.relay(id)` create authoring builders. The loader materializes these builders into runtime dataclasses after `build()` runs.

Some bridge agreements are better written as dialogue flows instead of isolated calls. `self.puppet_stayman(id)` is the first flow helper. It lets a Gadget author describe the ask, opener answers, responder continuations, and opener resolutions in bid-addressed pieces. The helper expands those pieces into normal Call Specifications and state effects, so the runtime engine still sees the same object model.

```python
puppet = self.puppet_stayman("puppet_1n")
puppet.over = "1N"
puppet.ask = "3C"
puppet.ask_requires = notrump_focus_active
puppet.ask_applies = responder_starts_puppet_over_1n

answer = puppet.answer("3H", applies=opener_has_five_hearts, target_suit="H")
answer.shows_length("H", min=5)

continuation = puppet.continuation(after="3H", bid="4H", applies=responder_supports_hearts, final=True)
continuation.shows_length("H", min=3)
continuation.records_fit("H", opener_min=5, responder_min=3)
```

This avoids turning Puppet into a flat list of unrelated `Call(...)` records. The source says: ask, answer, continue, resolve.

## Call Specification

A Call Specification defines one possible public call.

Important fields:

- `id`: short stable object ID inside the Gadget.
- `when`: visible compact auction context such as `"1NP"` or `"*"`.
- `seats`: optional opening-seat expansion list, using `1`, `2`, `3`, `4`.
- `bid`: absolute call such as `"2D"` or relative helper such as `StepAfterState(...)`.
- `requires`: optional Python function or expression for public context requirements.
- `applies`: optional Python function for hand/environment eligibility.
- `meaning`: structured public meaning fields.
- `effects`: state records emitted during auction replay.
- `capabilities`: optional tags used by policies, such as `keycard_ask` or `place_contract`.
- `description`: maintainer-facing explanation.
- `system_notes`: human-facing generated notes text.

The Call Specification source model has no `selection` field. Candidate eligibility belongs in `requires` and `applies`; judgment among eligible candidates belongs in Policy Functions.

## Meaning

`call.meaning` becomes a `CallMeaning` runtime object. It is public information: what the system can explain to opponents or show in generated system notes.

Common fields:

- `action`: formal action label such as `transfer`, `opening`, `control_bid`, or `rkcb_1430`.
- `target_suit`: suit or notrump target when relevant.
- `nature`: labels such as `natural`, `artificial`, or `conventional`.
- `acts`: structural call acts such as `context_initiating`, `forcing`, `relay_response`, or `final_placement`.
- `forcing`: forcing status such as `forcing_one_round` or `game_forcing`.
- `alertable`: current profile-level alert flag.
- `acbl_explanation`: short disclosure text.

Additional assigned attributes are preserved in `details`:

```python
call.meaning.raise_strength = "limit"
call.meaning.shown_length_min = 5
```

## Effects And State

Effects create public state records during replay.

```python
effect = call.effect("agreed_suit")
effect.suit = "S"
effect.source = "simple_raise"

effect = call.effect("control")
effect.suit = "D"
effect.agreed_suit = "H"
effect.round = "first_or_second"
effect.status = "shown"
```

State records are profile-defined evidence, not a fixed global ontology. A profile can use its own keys and values. Policy Functions read them through `ctx.state`:

```python
ctx.state.exists("agreed_suit", suit="H")
ctx.state.records_matching("opener.hcp")
ctx.state.estimate("opener.length.S")
```

For bridge judgment over inferred hand information, Policy Functions should prefer the typed knowledge view:

```python
ctx.knowledge.opener.S.length
ctx.knowledge.responder.suit("H").length
ctx.knowledge.fit("S").min_total
ctx.knowledge.opener.hcp
```

The knowledge view is a convenience layer over the same replayed records. It does not impose one global semantic vocabulary on every profile; it gives this profile a clean way to ask standard bridge questions about length, HCP, and fit evidence.

Expression dictionaries assigned to `requires`, `applies`, or effect attributes are wrapped by the builder into the runtime expression form automatically.

Fit evidence should not start as a boolean. A Gadget should record the actual length evidence that produced the agreement:

```python
resolution.records_fit("S", opener_min=4, responder_min=4, basis="puppet_1n_4_4_spade_fit")
```

The emitted state includes `partnership.fit.S`, `min_total=8`, and `pattern_floor="4-4"`. This lets later policies value 4-4, 5-3, 5-4, 4-3, and 5-2 fits differently instead of treating every fit as the same fact.

## Named Evaluator

A Named Evaluator is a reusable Python function registered from a Gadget.

```python
def eval_stopper(ctx, target_suit):
    return (
        ctx.hand.contains_rank(target_suit, "A")
        or ctx.hand.contains_rank(target_suit, "K")
        or (ctx.hand.contains_rank(target_suit, "Q") and ctx.hand.length(target_suit) >= 2)
        or (ctx.hand.contains_rank(target_suit, "J") and ctx.hand.length(target_suit) >= 3)
    )


class NotrumpTools(Gadget):
    id = "notrump_tools"
    author = Author("Meow Li")

    def build(self):
        evaluator = self.evaluator("eval_stopper")
        evaluator.function = eval_stopper
        evaluator.description = "Stopper evaluator for notrump exploration."
```

Named Evaluators are appropriate for reusable bridge metrics: stopper quality, good preempt suit, honor-third support, losing trick count, or profile-specific hand evaluation.

## Policy Function

Policy Functions make whole-pool judgment. They do not attach hidden priority numbers to individual Call Specifications; they inspect eligible candidates and return the candidate they choose.

```python
def meow_major_raise_route(ctx, candidates):
    opening = ctx.state.records_matching("major_opening")[-1]
    suit = opening.attributes["target_suit"]
    support = ctx.hand.length(suit)
    hcp = ctx.hand.hcp

    if support >= 4 and hcp >= 13:
        return candidates.by_action_type("jacoby_2n").by_target_suit(suit).first()
    if support >= 4 and hcp >= 10:
        return candidates.first_available("3D", "3C")
    if support == 3 and 6 <= hcp <= 10:
        return candidates.by_action_type("simple_raise").by_target_suit(suit).first()
    return None


policy_functions = [meow_major_raise_route]
```

The policy layer decides among alternatives such as 1M versus 1N, simple raise versus Bergen versus Jacoby 2N, control bid versus RKCB, or pass versus game.

## Frame

A Frame records an active public auction context. It is visible from the auction and replayable without private memory.

```python
frame = self.frame("rkcb_1430")
frame.frame_type = "rkcb_1430"
frame.when = "*"
frame.source_call = "4N"
frame.variables = {
    "method": "1430",
    "trump_suit_source": "agreed_suit",
}
frame.close_on_act_types = ["final_placement", "signoff"]
```

Examples include major transfer, control bidding, RKCB 1430, Gerber, Kickback, Minorwood, and targeted king ask.

## Private Route

A Private Route records the bidder's own reason for entering a path when the public call could be reused by several plans.

```python
route = self.route("weak_heart_transfer_signoff")
route.owner = "responder"
route.goal = "signoff"
route.when = "1NP"
route.seats = [1, 2, 3, 4]
route.preconditions = weak_heart_signoff
route.entry_call = "2D"
route.workflow = Workflow(
    "wait_for_acceptance",
    WaitForCall("wait_for_acceptance", OnCall("2H", "pass_acceptance"), actor="opener"),
    MakeCall("pass_acceptance", "P", meaning=Meaning(action="final_placement", target_suit="H")),
)
```

The public meaning of `2D` remains "transfer to hearts." The Private Route can distinguish "transfer and pass" from "transfer then ask keycards" for the same bidder in the same deal.

## Relative Calls

Some Gadgets depend on relative calls rather than fixed calls:

```python
call.bid = StepAfterState("keycard_context", method="1430", status="pending", step=1)
call.bid = StepAfterLastContract(1)
```

Relative calls are used for keycard responses and future relay or interference structures. Extend this mechanism when a convention is step-based instead of enumerating every absolute call.

## Runtime Dataclasses

`backend/engine/model.py` defines the loaded object model:

- `PartnershipProfile`
- `Gadget`
- `CallSpec`
- `CallMeaning`
- `StateEffect`
- `FrameSpec`
- `PrivateRouteSpec`
- `PolicyFunction`
- `EvaluatorSpec`
- `RelaySpec`

`backend/engine/context.py` defines decision-time objects:

- `BridgeContext`
- `StateView`
- `CallCandidate`
- `CandidatePool`

This split is intentional. Source files describe agreements; runtime context describes the current auction, hand, recovered state, private memory, and candidate pool.
