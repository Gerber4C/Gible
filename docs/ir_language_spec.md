# IR/YAML Language Specification

Platform Version: 0.0.6
Author: Meow Li
Copyright: Copyright (c) 2026 Meow Li. All Rights Reserved.

This document is the technical language manual for Partner's current YAML Intermediate Representation. The engine executes this IR. Bridge System Language and GUI forms are future authoring surfaces that should compile or validate into this IR before execution.

## 1. Language Purpose

The IR/YAML language describes a bridge Convention Set as executable objects.

It must answer five questions:

1. What visible auction context are we in?
2. What semantic context has been derived by replaying the auction?
3. What calls are legal, meaningful, and selectable now?
4. What public meaning and alert/disclosure data should be attached to each call?
5. What internal plan, protocol, or selection policy caused the call to be chosen?

The IR should avoid full auction enumeration when semantic context can represent the same idea. For example, an RKCB Call Specification should usually require an agreed trump suit and slam interest, not list every possible auction where `4N` is RKCB.

## 2. Object Model

Top-level IR object types:

- `ConventionSet`: complete playable agreement.
- `Convention`: portable agreement module.
- `CallSpecification`: one possible call in one context.
- `ProtocolFrame`: active agreement procedure created by the auction.
- `BiddingPlan`: bidder's internal route through a multi-step auction.
- `CallSelectionPolicy`: algorithm that chooses among candidate calls or plans.
- `NamedEvaluator`: reusable hand/environment/semantic calculation.
- `RelayAutomaton`: step-based relay mechanism.

Current YAML files store these objects in directories:

```text
backend/convention_sets/
backend/conventions/
```

## 3. Convention Set

A Convention Set imports active Conventions.

```yaml
id: expert_2over1
name: Expert 2/1
version: 0.1.0
description: >
  Prototype Convention Set for 2/1 and after-1N methods.
author:
  name: Partner Prototype
conventions:
  - two_over_one
  - four_way_jacoby_transfer
```

Fields:

- `id`: stable Convention Set ID.
- `name`: display name.
- `version`: Convention Set version.
- `description`: maintainer-facing explanation.
- `system_notes`: optional generated-notes text.
- `author`: author metadata.
- `conventions`: ordered list of Convention directory IDs.

The current engine loads Conventions in listed order but searches their Call Specifications globally.

## 4. Convention

Each Convention directory contains `convention.yaml`.

```yaml
id: four_way_jacoby_transfer
namespace: notrump_response
name: Four-Way Jacoby Transfer
version: 0.1.0
description: >
  After-1N transfer structure.
system_notes: >
  Four-way transfers are used after 1N.
author:
  name: Partner Prototype
```

Fields:

- `id`: stable Convention ID.
- `namespace`: origin namespace used in generated qualified IDs.
- `name`: display name.
- `version`: Convention version.
- `description`: maintainer-facing explanation.
- `system_notes`: human-readable system-note text.
- `author`: author metadata inherited by contained objects unless overridden.

Design policy:

- A Convention should be a portable bridge method, not a large bundle of unrelated agreements.
- Use separate Conventions for methods such as regular Stayman, Puppet Stayman, four-way transfers, Texas transfers, RKCB, Bergen, Drury, Jacoby 2N, splinters, and game tries.
- A Convention Set may add integration-policy Conventions when several portable Conventions need one shared selection policy.
- Communicate across Conventions through formal semantic state. For example, a transfer Convention may create `agreed_suit`, and a standalone RKCB Convention may require that state.

## 5. Call Specification

A Call Specification defines one possible call in a context. It is the atomic object for bidding, explanation, alerting, and semantic effects.

```yaml
call_specifications:
  - id: cs_1
    description: Responder bids 2D over 1N as a transfer to hearts with at least five hearts.
    system_notes: After 1N, 2D is artificial and transfers to hearts.
    context:
      auction_pattern: "1NP"
      seat_positions: [1, 2, 3, 4]
    requires:
      semantic_state:
        notrump_focus:
          status: active
    call: 2D
    applicability:
      all:
        - self.hearts:
            min: 5
    selection:
      algorithm: weighted_score
      criteria:
        - criterion_id: heart_length
          evaluator: min_value
          input: self.hearts
          min: 5
          weight: 60
    meaning:
      nature_labels: [artificial, conventional]
      call_act_types: [directive, context_initiating, forcing]
      action_type: transfer
      target_suit: H
      alertable: true
      acbl_explanation: hearts
    effects:
      - fact_type: transfer
        source_role: responder
        target_role: opener
        target_suit: H
        status: pending
```

Current executable fields:

- `id`
- `description`
- `system_notes`
- `context`
- `requires`
- `call`
- `applicability`
- `selection`
- `meaning`
- `effects`
- `default_policy`

Target fields not fully implemented yet:

- `shows`
- `clears`
- ontology-backed effect operations such as `create_transfer`, `update_transfer`, and `set_agreed_suit`

## 6. Visible Context

`context` matches visible auction shape.

```yaml
context:
  auction_pattern: "1NP"
  seat_positions: [1, 2, 3, 4]
```

Fields:

- `auction_pattern`: compact visible auction immediately before the call.
- `seat_positions`: shorthand for initial-pass variants.

Examples:

```yaml
context:
  auction_pattern: ""
  seat_positions: [1, 2, 3, 4]
```

Matches:

```text
""    seat 1
"P"   seat 2
"PP"  seat 3
"PPP" seat 4
```

```yaml
context:
  auction_pattern: "1NP"
  seat_positions: [3]
```

Matches:

```text
PP1NP
```

Visible context should not carry vulnerability, game/slam judgment, or private plan logic. Those belong in environment evaluation, semantic requirements, Bidding Plans, or Call Selection Policies.

## 7. Semantic Requirements

Semantic requirements ask what is true after replaying the auction. They avoid enumerating every full sequence that creates the same state.

Current executable shape:

```yaml
requires:
  fact_exists:
    fact_type: transfer
    target_suit: H
    status: pending
```

Preferred typed-facing executable shape:

```yaml
requires:
  state_has:
    transfer:
      target_suit: H
      status: pending
```

To require absence:

```yaml
requires:
  state_missing:
    agreed_suit: {}
```

Another current executable example:

```yaml
requires:
  all:
    - fact_exists:
        fact_type: agreed_suit
        suit: S
    - expr:
        op: fact_exists
        query:
          fact_type: keycard_context
          trump_suit: S
          status: pending
```

`requires` uses the same condition evaluator as `applicability`: `all`, `any`, `not`, `fact_exists`, `state_has`, `state_missing`, `auction_state_exists`, `auction_state_missing`, `auction_state_compare`, `expr`, and direct comparisons. In practical use today, `requires` should be used for trace-derived semantic state, while hand-dependent conditions usually belong in `applicability` or `selection`.

Typed auction-state variables are the current executable bridge between flexible facts and the future ontology-backed state object:

```yaml
requires:
  auction_state_exists:
    key: opener.length.S
    owner: opener
    min_value: 4
```

```yaml
requires:
  auction_state_compare:
    query:
      key: opener.hcp
      owner: opener
    attribute: max_value
    min: 14
```

Target ontology-backed shape:

```yaml
requires:
  transfer:
    target_suit: H
    status: pending
```

```yaml
requires:
  agreed_suit:
    suit: S
  slam_interest:
    min: try
```

The target shape is cleaner but depends on replacing flexible `SemanticFact` data with a typed ontology-backed semantic state.

## 8. Applicability

`applicability` evaluates hand, trace, and environment conditions.

```yaml
applicability:
  all:
    - self.hearts:
        min: 5
    - env.scoring:
        in: [IMP, MP]
```

Supported current inputs:

- `self.hcp`
- `self.balanced`
- `self.spades`
- `self.hearts`
- `self.diamonds`
- `self.clubs`
- `env.<key>`
- `expr`, which can read `self`, `partner`, `env`, parameters, and trace facts through the expression language.

Supported current operators:

- `min`
- `max`
- `eq`
- `in`
- `all`
- `any`
- `not`
- `fact_exists`
- `expr`

Design policy: use `applicability` only for conditions that belong to the current Call Specification. Use a Call Selection Policy when several valid alternatives must be compared.

## 9. Selection

`selection` says how strongly this call competes for the current hand.

```yaml
selection:
  applicability:
    all:
      - self.hearts:
          min: 5
  algorithm: weighted_score
  criteria:
    - criterion_id: heart_length
      evaluator: min_value
      input: self.hearts
      min: 5
      weight: 60
    - criterion_id: game_values
      evaluator: range_contains
      input: self.hcp
      min: 10
      max: 40
      weight: 20
```

Current evaluator names:

- `range_contains`
- `min_value`
- `equals`
- `fact_exists`
- `expression`
- `named_evaluator`

Current selection algorithm:

- `weighted_score`

Selection should not be used as hidden priority. If `1S` and `1N` are both possible, a Call Selection Policy should declare how to choose.

## 10. Limited Expression Language

Some bridge judgments require calculation. The language should express those calculations through a small safe expression tree, not by inventing one field for every bridge idea.

The expression tree is deliberately explicit because it is the engine IR. It is not the ideal final human authoring syntax. Bridge System Language and GUI editors should allow compact forms such as `hcp 15..17 and balanced` or `length(S) >= 5`, then compile those forms into this structured IR. Direct condition blocks such as `self.hcp: {min: 15, max: 17}` remain acceptable for simple predicates.

Design goals:

- executable in YAML,
- deterministic,
- no arbitrary Python or shell code,
- elementary arithmetic and boolean logic only,
- explicit inputs from hand, partnership hand when available, auction, environment, and semantic state,
- reusable through Named Evaluators.

Target expression shape:

```yaml
expr:
  op: and
  args:
    - op: gte
      left: {var: self.clubs.length}
      right: {const: 3}
    - op: gte
      left:
        op: honor_count
        suit: C
        ranks: [A, K, Q]
      right: {const: 1}
```

Allowed target scalar values:

- integer,
- decimal,
- boolean,
- string enum,
- suit symbol,
- rank symbol,
- call symbol.

Allowed target variable roots:

- `self`: current hand.
- `partner`: partner hand, only in pair-hand simulation or double-dummy benchmark tests.
- `partnership`: derived combined features when both hands are available.
- `auction`: visible auction features.
- `env`: environment.
- `state`: ontology-backed semantic state.
- `random`: declared random source.

Allowed target operators:

- Boolean: `and`, `or`, `not`.
- Comparison: `eq`, `neq`, `lt`, `lte`, `gt`, `gte`, `in`.
- Arithmetic: `add`, `sub`, `mul`, `div`, `min`, `max`, `abs`.
- Counting: `count`, `length`, `honor_count`, `loser_count` once defined.
- Suit/rank access: `holding`, `contains_rank`, `top_honor_count`.
- Conditional: `if`.

Example: minor-transfer superaccept support.

```yaml
named_evaluators:
  - id: eval_minor_honor_third
    evaluator_type: expression
    description: Target minor has at least three cards and at least one of A, K, Q.
    parameters:
      target_suit: suit
    definition:
      op: and
      args:
        - op: gte
          left:
            op: length
            hand: self
            suit: {param: target_suit}
          right: {const: 3}
        - op: gte
          left:
            op: honor_count
            hand: self
            suit: {param: target_suit}
            ranks: [A, K, Q]
          right: {const: 1}
```

Example: stronger holdings such as `KQx` naturally pass because the honor count is at least one and the length is at least three.

Example: eight-card fit in pair-hand simulation.

```yaml
op: gte
left:
  op: add
  args:
    - op: length
      hand: self
      suit: S
    - op: length
      hand: partner
      suit: S
right: {const: 8}
```

Example: major-suit game threshold.

```yaml
op: and
args:
  - op: gte
    left:
      op: add
      args:
        - {var: self.hcp}
        - {var: partner.hcp}
    right: {const: 25}
  - op: gte
    left:
      op: add
      args:
        - op: length
          hand: self
          suit: H
        - op: length
          hand: partner
          suit: H
    right: {const: 8}
```

Example: help in a suit for a help-suit game try. This is only a starter definition; partnership style may refine it.

```yaml
named_evaluators:
  - id: eval_help_in_suit
    evaluator_type: expression
    description: Responder has useful help in the asked suit.
    parameters:
      target_suit: suit
    definition:
      op: or
      args:
        - op: gte
          left:
            op: honor_count
            hand: self
            suit: {param: target_suit}
            ranks: [A, K, Q]
          right: {const: 1}
        - op: lte
          left:
            op: length
            hand: self
            suit: {param: target_suit}
          right: {const: 1}
```

Language policy:

- Do not add fields such as `can_superaccept`, `has_help`, or `accept_game_try` as primitive language features.
- Define those judgments as Named Evaluators or inline expressions.
- Add ontology terms only when the concept is reusable semantic state, not because one Convention needs a convenient label.

Current engine ability:

- Implemented literal nodes: `const`, `var`, and `param`.
- Implemented variable roots: `self`, `partner`, and `env`.
- Implemented boolean operators: `and`, `or`, `not`.
- Implemented comparison operators: `eq`, `neq`, `lt`, `lte`, `gt`, `gte`, `in`.
- Implemented arithmetic operators: `add`, `sub`, `mul`, `div`, `min`, `max`, `abs`.
- Implemented conditional operator: `if`.
- Implemented hand operators: `length`, `honor_count`, `contains_rank`, `ace_count`, `king_count`, `keycard_count`.
- Implemented trace operators: `fact_exists`, `state_has`, `state_missing`, `fact_attribute`, `auction_state_exists`, `auction_state_missing`, `auction_state_compare`, `auction_state_attribute`.
- Implemented reusable calculations: expression-type `NamedEvaluator` through `evaluator: named_evaluator` and `evaluator_id`.

Current environment variables used by executable YAML:

- `env.dealer`: absolute dealer, `n/e/s/w`.
- `env.seat`: absolute seat currently choosing a call.
- `env.vulnerability`: absolute vulnerability, `none/ns/ew/both`.
- `env.vulnerability_relation`: derived actor relation, one of `none`, `both`, `favorable`, or `unfavorable`.
- `env.seat_position`: opening seat number `1`, `2`, `3`, or `4` when the current auction is still only initial passes; otherwise `null`.
- `env.scoring`: scoring label when supplied by the request, such as `IMP`.
- `env.partner_hand`: optional parsed or compact partner hand in pair-hand simulation.

Example: weak two style by seat and vulnerability.

```yaml
named_evaluators:
  - id: eval_weak_two_opening
    evaluator_type: expression
    definition:
      op: and
      args:
        - op: gte
          left:
            op: length
            hand: self
            suit: {param: target_suit}
          right: {const: 6}
        - op: lte
          left: {var: self.hcp}
          right: {const: 10}
        - op: or
          args:
            - op: and
              args:
                - op: eq
                  left: {var: env.seat_position}
                  right: {const: 3}
                - op: gte
                  left: {var: self.hcp}
                  right: {const: 4}
            - op: and
              args:
                - op: eq
                  left: {var: env.vulnerability_relation}
                  right: {const: unfavorable}
                - op: gte
                  left: {var: self.hcp}
                  right: {const: 7}
```

This remains a limited expression tree. Users should not need to hand-write this much structure in the final product; BSL or Python-like static source can compile a compact predicate into this IR.

`keycard_count` accepts optional `excluded_suit` for Exclusion/Voidwood-style methods:

```yaml
op: keycard_count
hand: self
trump_suit: H
excluded_suit: D
```

`fact_attribute` is the current bridge between semantic replay and reusable Conventions. It reads a field from the first or last fact matching a query:

```yaml
op: fact_attribute
query:
  fact_type: agreed_suit
attribute: suit
which: last
```

The operator is used by standalone RKCB to discover the trump suit from previously recovered `agreed_suit` state rather than from a hard-coded auction pattern.

`auction_state_attribute` reads from typed auction-state variables. This supports scalar and range-like inference without turning every bridge idea into a boolean fact:

```yaml
op: auction_state_attribute
query:
  key: opener.hcp
  owner: opener
attribute: max_value
default: null
```

Current examples include `opener.hcp` with `min_value`/`max_value`, `opener.length.H` or `opener.length.S` with suit-length bounds, `partnership.force_status` with values such as `game_forcing`, and private route-purpose state used for training/debug provenance.

Not implemented yet:

- `partnership`, `auction`, `state`, and `random` variable roots.
- `count`, `loser_count`, `holding`, and `top_honor_count` operators.
- Full schema validation for expression argument shapes.
- Non-expression Named Evaluator types.

## 11. Meaning

`meaning` is public agreement meaning.

```yaml
meaning:
  nature_labels: [artificial, conventional]
  call_act_types: [directive, context_initiating, forcing]
  action_type: transfer
  target_suit: H
  alertable: true
  acbl_explanation: hearts
```

Common fields:

- `nature_labels`: disclosure labels such as `natural`, `artificial`, `conventional`.
- `call_act_types`: structural role such as `descriptive`, `directive`, `inquiry`, `relay_ask`, `context_initiating`, `forcing`, `signoff`, `final_placement`.
- `action_type`: more specific structured action.
- `target_suit`: relevant suit.
- `alertable`: explicit near-term alert flag.
- `acbl_explanation`: short alert/announcement wording when known.

Public meaning must not expose private Bidding Plan comparisons unless the product is intentionally showing training/debug detail.

## 12. Effects

`effects` update replay-derived semantic state.

Current executable shape:

```yaml
effects:
  - fact_type: transfer
    target_suit: H
    status: pending
```

Effect attributes may also be dynamic by using an `expr` wrapper. During auction replay, the engine evaluates the expression against the current hand, environment, and trace before storing the resulting state.

```yaml
effects:
  - fact_type: keycard_context
    trump_suit:
      expr:
        op: fact_attribute
        query:
          fact_type: agreed_suit
        attribute: suit
    method: "1430"
    status: pending
```

This is how the executable RKCB Convention stays reusable: any Convention that creates `agreed_suit` can feed the same keycard Call Specifications.

Current executable typed-state shape:

```yaml
effects:
  - state:
      key: opener.hcp
      namespace: public
      owner: opener
      min_value: 12
      max_value: 14
      source: notrump_rebid
  - state:
      key: responder.route_purpose
      namespace: private
      owner: responder
      value: establish_force_before_describing_long_suit_or_shape
      source: checkback_game_force
```

`state_update` is accepted as an alias for `state`. `namespace: public` is intended for shareable Convention interoperability. `namespace: private` is available for Convention Set-specific internal policy, route, scoring, or training data. The engine records provenance for both.

Target ontology-backed shape:

```yaml
effects:
  - create_transfer:
      owner: actor
      acceptor: partner
      bid_suit: D
      target_suit: H
      status: pending
  - create_obligation:
      subject: partner
      action_type: accept_transfer_or_superaccept
      target_suit: H
```

Effects should create shared semantic state that other Conventions can query. They should not be private strings that only one file understands.

## 13. Protocol Frame

A Protocol Frame represents an active agreement procedure.

```yaml
protocol_frames:
  - id: frame_1
    frame_type: major_transfer
    description: Live transfer context after 1N P 2D.
    context:
      auction_pattern: "1NP"
      seat_positions: [1, 2, 3, 4]
    source_call: 2D
    variables:
      target_suit: H
      initiator: responder
      acceptor: opener
    stages:
      - opener_rebid
      - responder_continuation
    allowed_continuations:
      - complete_transfer
      - superaccept
      - responder_signoff
      - responder_invite
      - responder_slam_exploration
    break_conditions:
      - undefined_interference_without_policy
```

Fields:

- `id`
- `frame_type`
- `description`
- `system_notes`
- `context`
- `source_call`
- `variables`
- `stages`
- `allowed_continuations`
- `break_conditions`

Current engine ability: loads Protocol Frames and recovers active frame state when the source call appears. The active state includes `current_stage`. The first executable stage behavior advances transfer frames from `opener_rebid` to `responder_continuation` after transfer completion or superaccept, and can close transfer frames when a final-placement Call Specification is replayed.

## 14. Bidding Plan

A Bidding Plan is an internal route. It explains why a player chooses an entry call and how the player expects to continue.

```yaml
bidding_plans:
  - id: plan_1
    description: Transfer to hearts, then sign off if opener completes.
    owner: responder
    goal: signoff
    context:
      auction_pattern: "1NP"
      seat_positions: [1, 2, 3, 4]
    preconditions:
      self.hearts:
        min: 5
      self.hcp:
        max: 6
    entry_candidate: true
    entry_call: 2D
    selection:
      algorithm: weighted_score
      criteria:
        - criterion_id: weak_signoff_shape
          evaluator: min_value
          input: self.hearts
          min: 5
          weight: 60
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
              goto: make_1
            - when:
                kind: call_is
                value: 3H
              goto: make_1
        make_1:
          kind: make_call
          call_reference:
            action_type: final_placement
            target_suit: H
          call: P
```

Plan fields:

- `id`
- `description`
- `system_notes`
- `owner`
- `goal`
- `context`
- `preconditions`
- `entry_candidate`
- `entry_call`
- `selection`
- `entry_score`
- `workflow`

Allowed current goals:

- `signoff`
- `invite_game`
- `force_game`
- `explore_slam`
- `ask_keycards`
- `resolve_shape`
- `show_feature`
- `compete`
- `escape`
- `place_contract`

Allowed current workflow node kinds:

- `make_call`
- `wait_for_call`
- `branch`
- `select_by_policy`
- `enter_protocol`
- `update_plan_state`
- `end_plan`
- `fail_plan`

Allowed current branch predicate kinds:

- `call_is`
- `call_act_type_is`
- `protocol_frame_matches`
- `state_has`
- `state_missing`
- `hand_predicate`
- `environment_predicate`
- `interference_level`
- `obligation_status`

Current engine ability: validates workflow and recovers active plan state after the entry call. A plan can also propose its own entry call when `entry_candidate: true`, its context and preconditions match, and the entry call has an eligible Call Specification. The first executable continuation behavior advances `wait_for_call` nodes through `call_is`, `call_act_type_is`, `state_has`, and `state_missing` branches. A current `make_call` node can generate a bidding candidate when the plan preconditions match the current hand. During replay, a completed `make_call` node moves to `goto` or `then` when declared, otherwise it closes the plan.

## 15. Call Specification And Plan Relationship

Call Specifications and Bidding Plans are not alternatives. They work together.

```text
Call Specification = what this call means and does
Bidding Plan       = why I am taking this route and how I continue
Protocol Frame     = what procedure is active
Semantic State     = what is true now
Selection Policy   = how competing calls or plans are chosen
```

A Bidding Plan should not expand into every full auction string. It should resolve to Call Specifications at each decision point.

Example:

```text
1N P 2D P 2H P ?
```

Replay should recover:

- `2D` created a heart-transfer semantic state.
- `2D` opened a major-transfer Protocol Frame.
- one or more plans beginning with `2D` remain possible.
- `2H` completed the transfer branch.

At the next decision, a plan can propose:

- pass,
- invite,
- bid game,
- show a second suit,
- start slam exploration.

When a plan-generated call has an eligible matching Call Specification, the public origin and public meaning come from the Call Specification while the private plan is recorded as `plan_origin` in internal provenance. This is the current mechanism for "I chose this route because of a plan, but the call itself has a reusable public Convention meaning."

Example:

```text
1N P 2D P 3H P 4N
```

In the current benchmark:

- `2D` publicly comes from the four-way transfer Call Specification.
- the private `plan_origin` can be a transfer-slam Bidding Plan.
- `3H` superaccepts and creates `agreed_suit: H`.
- the active plan may propose `4N`.
- `4N` publicly comes from the standalone RKCB Call Specification when that is the selected call.
- other standalone slam tools, such as control bidding, Kickback, Minorwood, Exclusion, or targeted honor asks, may compete through ordinary candidate selection.
- replaying a selected asking call opens the appropriate Protocol Frame.

Target design: each actual call should resolve to a Call Specification or generated Call Specification so the engine can disclose meaning and update state. Current first-slice execution also allows a `make_call` plan node to generate a candidate directly from its structured `call` and `meaning`; this remains useful for simple continuations such as transfer-and-pass, but reusable Convention calls should prefer matching Call Specifications.

## 16. Long-Sequence Abstraction

Long sequences should be represented by semantic state plus local continuation objects, not by all possible full patterns.

Bad shape:

```yaml
# Do not build hundreds of exact strings like this.
context:
  auction_pattern: "1NP2DP2HP3SP3NP4CP"
call: 6H
```

Preferred shape:

```yaml
context:
  actor_role: responder
requires:
  transfer:
    target_suit: H
    status: completed
  slam_interest:
    min: try
  control_bidding:
    status: active
call: 4C
meaning:
  call_act_types: [control_showing]
  action_type: first_round_control
  target_suit: C
```

Visible pattern may still be used as a local anchor, especially for short agreements. For long auctions, semantic requirements should dominate the abstraction while visible auction legality remains mandatory.

## 17. Call Selection Policy

A Call Selection Policy chooses among candidates.

```yaml
call_selection_policies:
  - id: policy_1
    description: Choose the best opening candidate.
    scope:
      context:
        auction_pattern: ""
        seat_positions: [1, 2, 3, 4]
    algorithm: highest_score
    tie_breaker: diagnose
    same_call_resolution: diagnose
```

Current supported algorithms:

- `highest_score`
- `weighted_score_highest`
- `ordered_condition`

`highest_score` and `weighted_score_highest` choose the eligible candidate with the largest evaluated score.

`ordered_condition` tests policy choices in order. A choice can select only a call that is already an eligible candidate; the policy does not make an ineligible Call Specification legal or meaningful.

```yaml
call_selection_policies:
  - id: policy_1
    description: Prefer 15-17 balanced 1N over a five-card major.
    scope:
      context:
        auction_pattern: ""
        seat_positions: [1, 2, 3, 4]
    algorithm: ordered_condition
    choices:
      - choose_call: 1N
        when:
          all:
            - self.hcp: {min: 15, max: 17}
            - self.balanced: true
      - choose_call: 1S
        when:
          all:
            - self.hcp: {min: 12}
            - self.spades: {min: 5}
      - choose_call: 1H
        when:
          all:
            - self.hcp: {min: 12}
            - self.hearts: {min: 5}
    fallback: highest_score
```

In that example, a 16-count 5332 hand with five spades produces eligible `1N` and `1S` candidates. The policy chooses `1N` because the first choice applies. A non-balanced 5-5 majors hand produces eligible `1S` and `1H` candidates, and the policy chooses `1S` because the spade choice appears first.

Target algorithm families:

- `decision_tree`
- `decision_table`
- `lexicographic_comparator`
- `scoring_evaluator`
- `randomized_choice`
- `external_plugin_evaluator`

If multiple candidates remain and no policy resolves them, the engine should diagnose ambiguity.

`same_call_resolution` is specifically for cases where several eligible Call Specifications produce the same call with different meanings. The default is `diagnose`, which keeps the candidates visible in internal origin and adds a diagnostic. A policy may declare `highest_score` when the Convention Set intentionally wants score-based resolution for same-call meanings.

Example: `4N` may be quantitative notrump or RKCB. Quantitative notrump should require `notrump_focus` and no `agreed_suit`; RKCB should require `agreed_suit`. If both remain eligible, the resolver reports ambiguity rather than silently treating one meaning as correct.

## 18. Named Evaluator

A Named Evaluator declares a reusable calculation.

Executable expression example:

```yaml
named_evaluators:
  - id: eval_minor_honor_third
    evaluator_type: expression
    description: Target minor has at least three cards and one of A, K, or Q.
    definition:
      op: and
      args:
        - op: gte
          left:
            op: length
            hand: self
            suit: {param: target_suit}
          right: {const: 3}
        - op: gte
          left:
            op: honor_count
            hand: self
            suit: {param: target_suit}
            ranks: [A, K, Q]
          right: {const: 1}
```

Executable usage:

```yaml
selection:
  criteria:
    - criterion_id: honor_third_club_support
      evaluator: named_evaluator
      evaluator_id: eval_minor_honor_third
      params:
        target_suit: C
      weight: 100
```

Current engine ability: expression-type Named Evaluators execute in selection criteria. Other evaluator types are loaded but not executable.

## 19. Relay Automaton

A Relay Automaton declares step-based asking and response decoding.

Target example:

```yaml
relay_automata:
  - id: relay_1
    asker: captain
    describer: partner
    next_relay_call: cheapest_step
    response_decoder:
      mode: step_table
    step_table:
      shape_family:
        step_1: balanced
        step_2: one_suited
        step_3: two_suited
    break_conditions:
      - asker_places_contract
```

Current engine ability: loads Relay Automata but does not execute them.

## 20. Generated System Notes

`description`, `system_notes`, `meaning`, and structured objects should support reliable system-note generation.

Generated notes should include:

- Convention Set metadata,
- Convention metadata,
- Call Specifications,
- public meanings,
- alertability,
- Protocol Frames,
- Bidding Plans,
- Call Selection Policies.

Human-readable notes are output from structured IR. They are not the executable source of truth.

## 21. Execution Order

Target execution order:

```text
request
  -> parse auction, hand, environment
  -> load Convention Set
  -> replay auction through Call Specifications
  -> derive Semantic State
  -> recover active Protocol Frames
  -> recover possible Bidding Plans
  -> generate candidate calls and candidate plans
  -> apply Call Selection Policy
  -> select a Call Specification
  -> return public meaning, internal origin, diagnostics
```

Current implemented subset:

```text
request
  -> parse auction, hand, environment
  -> load Convention Set
  -> replay auction into flexible SemanticFact trace and typed AuctionStateVariable list
  -> recover and advance ProtocolFrameState and PlanState
  -> validate historical auction legality for diagnostics
  -> evaluate Call Specification `requires`
  -> generate candidate Call Specifications
  -> generate entry-call candidates from Bidding Plans that opt in
  -> generate candidate calls from active Bidding Plan `make_call` nodes
  -> evaluate applicability, expression criteria, and expression-type Named Evaluators
  -> filter illegal candidate calls
  -> diagnose or resolve same-call meaning collisions
  -> choose highest score through matching Call Selection Policy
  -> return public meaning, internal origin, diagnostics
```

Current full-auction simulation repeats that single-call process for supplied partnership hands and auto-passes missing seats until the auction completes.

## 22. Expressive Completeness Target

Within Partner's problem definition, input consists of:

- visible auction,
- environment,
- own hand,
- semantic state derived from replay,
- declared random source.

The target IR is expressively complete for practical bridge bidding if it can represent finite mappings from those inputs to legal calls or probability distributions over legal calls. Compact authoring then depends on abstractions: Protocol Frames, Bidding Plans, Call Selection Policies, Named Evaluators, and Relay Automata.

## 23. Validation Requirements

The IR validator should eventually enforce:

- required fields by object type,
- known call syntax,
- known suit symbols,
- known Call Act Types,
- known plan node kinds,
- known branch predicate kinds,
- valid workflow references,
- valid effect/query vocabulary,
- no unresolved ambiguity between candidates unless a policy resolves it,
- no reliance on arbitrary prose for executable behavior.

The current code validates calls, auction patterns, and Bidding Plan workflow shape. Full schema validation is future work.
