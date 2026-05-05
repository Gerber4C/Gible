# Semantic Ontology

Platform Version: 0.0.6
Author: Meow Li
Copyright: Copyright (c) 2026 Meow Li. All Rights Reserved.

This document defines the system-level bridge ontology for Partner. It is the formal vocabulary that Conventions, Call Specifications, explanations, alert analysis, UI, tests, and future LLM-assisted Convention generation should share.

The ontology is needed because many bridge calls cannot be interpreted by auction-pattern enumeration alone. For example, `4N` may be quantitative, RKCB, old-style Blackwood, natural, or competitive/takeout depending on semantic context. A portable Convention must be able to ask the engine for formal bridge state such as agreed trump, pending transfer, forcing status, competitive pressure, or notrump focus instead of relying on private strings.

The current Python prototype has a simple `SemanticFact` trace plus a first typed `AuctionStateVariable` list. Facts remain useful for discrete bridge events, while auction-state variables carry scalar and range-like inference such as `opener.hcp`, `opener.length.S`, `partnership.force_status`, and private route-purpose state. Both are temporary implementation details on the path to an ontology-backed semantic state with explicit merge, query, conflict, and explanation behavior.

The ontology also supplies the vocabulary and type system for the future Bridge System Language. BSL keywords should compile into ontology-backed Intermediate Representation effects and queries, not into arbitrary private strings.

The concrete YAML/IR language that uses this vocabulary is specified in `docs/ir_language_spec.md`.

## 1. Design Principles

### 1.1 Pattern Matching Is Local

`auction_pattern` identifies the visible auction shape needed by a Call Specification.

Pattern matching should answer:

- Did this local auction shape happen?
- Whose turn is it?
- Which call is being interpreted or selected?

Pattern matching should not be forced to encode every possible path to a bridge concept. A Convention should not need to enumerate every auction where `4N` is RKCB.

Portable Conventions should be organized around bridge methods, not around one bundled auction family. For example, Texas transfers should create transfer and agreed-suit state, while a standalone RKCB Convention consumes agreed-suit/keycard state. Likewise, Bergen raises, Drury, Jacoby 2N, Puppet Stayman, and regular Stayman should be independently selectable by a Convention Set.

The current prototype now has a first executable version of this idea: a Call Specification can use wildcard visible context plus semantic `requires`, expressions can read fact attributes with `fact_attribute`, effects can write attributes computed from those expressions, and typed auction-state variables can record scalar/range inference. This allows the same RKCB Convention to read `agreed_suit` after either Texas or a natural simple raise, and lets checkback/XYZ reason about forcing-route choices after minor-opening auctions.

### 1.2 Semantic State Is Derived

The client submits visible bridge information:

- system,
- auction,
- hand,
- dealer,
- vulnerability,
- scoring,
- seat.

The engine derives semantic state by replaying the auction through active Conventions. Clients should not submit hidden state such as "heart transfer pending" or "hearts agreed".

### 1.3 Ontology Terms Are Executable

Every formal ontology term must define expected engine behavior:

- how a Call Specification writes it,
- how another Call Specification queries it,
- how conflicts are detected,
- how it appears in internal origin,
- how public meaning can be generated from it when appropriate.

Natural-language labels are display text. They are not the source of truth.

### 1.4 Public Meaning And Internal State Are Different

Public meaning is partnership disclosure.

Internal semantic state is for execution, training, debugging, and later AI/LLM workflows.

Example: a Call Specification may publicly explain `2D` as "transfer to hearts". Internally, the same call may set a formal transfer object, mark responder as the owner of the shown heart length, and create an obligation for opener to accept, superaccept, or handle interference.

Another example: after `1C-1H-1S`, opener's `1S` publicly shows spades. It does not mean "denies a four-card major"; it creates state such as `opener.length.S >= 4`. Depending on the Convention Set's policy it may also imply that opener did not make the normal minimum heart raise. A later responder call such as artificial `2D` can be selected because it establishes a game force before responder safely rebids a long heart suit.

### 1.5 Conventions Share One Vocabulary

Portable Conventions must not invent private semantic strings that other Conventions cannot understand. If a Convention needs a new concept, the concept should be added to this ontology or namespaced as an explicit extension with documented executable behavior.

Practical bridge agreements can be complicated, but not every convention detail deserves a new ontology term. Prefer composing general reusable concepts:

- force level,
- invitation,
- game try,
- help-suit game try,
- slam interest,
- agreed suit,
- fit,
- control,
- stopper,
- shortness,
- honor support,
- transfer,
- relay,
- ask/answer obligation.

Judgmental calculations, such as whether a minor-transfer hand can superaccept, whether responder has help for a help-suit game try, or whether a suit can run opposite king-empty-sixth, should be written as IR evaluator expressions or Named Evaluators. Do not add one-off fields such as `can_superaccept` or `has_help` to the language just because one Convention needs that decision.

### 1.6 Bridge Bidding Is Protocol Execution

Many calls are not only descriptions of the bidder's hand. They can start a transfer, require partner to relay, ask a question, establish a game force, create a captain, or begin a multi-step plan.

The target ontology must therefore model bridge bidding as protocol execution:

```text
auction + environment + own hand + derived semantic state + random source
  -> candidate calls and candidate bidding plans
  -> Call Selection Policy
  -> selected call
  -> updated Semantic State and Protocol Frames
  -> public meaning and internal provenance
```

The ontology must support both ordinary natural systems, such as Washington Standard 2/1, and highly artificial systems, such as strong diamond, KK/Symmetric Relay, and other relay-heavy structures.

## 2. Core Semantic State Object

The target engine should derive a `SemanticState` while replaying the auction.

Expected top-level domains:

```yaml
semantic_state:
  auction_context: {}
  roles: {}
  shown_hands: {}
  range_state: {}
  scalar_state: {}
  private_state: {}
  call_history: []
  call_act_history: []
  suit_state: {}
  notrump_state: {}
  transfer_state: []
  relay_state: []
  protocol_frames: []
  bidding_plans: []
  forcing_state: {}
  obligations: []
  selection_history: []
  competitive_state: {}
  slam_state: {}
  alert_state: []
  diagnostics: []
```

The exact Python class names can evolve, but the domains above should remain conceptually stable.

Current executable bridge toward this target:

```yaml
effects:
  - state:
      key: opener.hcp
      namespace: public
      owner: opener
      min_value: 12
      max_value: 14
  - state:
      key: responder.route_purpose
      namespace: private
      owner: responder
      value: establish_force_before_describing_long_suit_or_shape
```

State variable policy:

- `public` namespace variables are intended for shared Convention interoperability and generated explanations.
- `private` namespace variables are allowed for Convention Set-specific policy, route, and training/debug information.
- Values may be booleans, strings, numbers, scores, ranges, or small structured records.
- The engine records origin for every variable so internal output can explain which Call Specification inferred it.
- Future validation should detect incompatible ranges and contradictory values instead of merely appending variables.

## 3. Auction Context

Auction context terms describe where the auction is, independent of hand meaning.

### `seat_number`

Values: `1`, `2`, `3`, `4`.

Executable behavior:

- Derived from the number of initial passes before the first non-pass call.
- Can be used by Call Specifications that differ by opening position, passed-hand status, or Drury-style auctions.
- It is a representation of the same visible auction prefix, not a separate concept from `P`, `PP`, or `PPP`.

Examples:

- `1N` has `seat_number: 1`.
- `P1N` has `seat_number: 2`.
- `PP1H` has `seat_number: 3`.
- `PPP1S` has `seat_number: 4`.

### `auction_phase`

Recommended values:

- `opening`
- `response`
- `opener_rebid`
- `responder_rebid`
- `competitive`
- `balancing`
- `slam`
- `passed_hand`
- `forced_action`

Executable behavior:

- Derived from auction history and semantic state.
- Call Specifications may require a phase, but should not use phase as a substitute for more precise concepts when precision is needed.
- Multiple phase tags may be true at once. For example, an auction can be both `competitive` and `slam`.

### `auction_status`

Recommended values:

- `live`
- `complete`
- `illegal`
- `undefined`

Executable behavior:

- The engine should eventually validate auction legality before call selection.
- Undefined means legal or possibly legal, but no loaded Call Specification describes it.

## 4. Side, Seat, And Role Ontology

The raw input uses absolute seats `n e s w`. Analysis often needs relative concepts.

### `absolute_seat`

Values: `n`, `e`, `s`, `w`.

Executable behavior:

- Always derived from dealer plus auction index.
- Used for table state and display.

### `side`

Values:

- `ours`
- `theirs`

Executable behavior:

- Derived from the acting seat relative to the requested user's side.
- Used for internal analysis, candidate generation, and explanations.

### `partnership`

Values:

- `ns`
- `ew`

Executable behavior:

- Derived from absolute seat.
- Used with vulnerability and opponent/partner relationships.

### `role`

Recommended values:

- `opener`
- `responder`
- `overcaller`
- `advancer`
- `intervenor`
- `doubler`
- `redoubler`
- `balancer`
- `captain`
- `describer`

Executable behavior:

- Roles are derived from the auction and can change or accumulate.
- A Call Specification may assign a role to a seat after a call.
- Role queries must specify whose role is being queried when ambiguity is possible.

Example:

```yaml
effects:
  - assign_role:
      subject: actor
      role: opener
```

## 5. Vulnerability And Scoring

### `vulnerability_state`

Raw values: `none`, `ns`, `ew`, `both`.

Executable behavior:

- Stored from board environment.
- Used to derive relative vulnerability.

### `vulnerability_relation`

Values:

- `favorable`
- `unfavorable`
- `none`
- `both`

Executable behavior:

- Derived from `vulnerability_state` and partnership.
- Used by evaluator algorithms, not by auction-pattern matching.
- Current engine value names are `none`, `both`, `favorable`, and `unfavorable`.

### `scoring`

Recommended values:

- `MP`
- `IMP`
- `rubber`
- `practice`

Executable behavior:

- Environment input.
- Can affect judgmental selection algorithms, risk, game tries, and preempt style.

## 6. Call Act Type

Call Act Type describes the structural role of a call in the auction. It answers the lower-level question: "what kind of protocol move is this call?"

Call Act Type is different from public display text. Opponents may hear "transfer to hearts"; internally the call may be a directive, a context initiator, a forcing action, and the first step of a private Bidding Plan.

Recommended core values:

- `descriptive`: shows hand features, such as a natural `1H` opening.
- `directive`: asks or requires partner to take a kind of action, such as accepting a transfer.
- `inquiry`: asks partner a question, such as Stayman, keycard, or a feature ask.
- `relay_ask`: the asking side makes a relay ask, often the cheapest available step.
- `relay_response`: the describing side answers a relay ask by step.
- `puppet`: asks partner to bid or deny a suit/shape in a controlled way.
- `context_initiating`: starts a live Protocol Frame, such as 2/1 game force or strong `1D`.
- `context_setting`: sets trump focus, notrump focus, captaincy, force level, or similar shared context.
- `forcing`: creates a force, pass-forcing situation, or partner obligation.
- `preemptive`: obstructive or space-consuming.
- `competitive`: takeout, penalty, responsive, support, cue, two-suited, or similar competitive action.
- `preference`: chooses among partner's possible suits or strains of action.
- `invitation`: asks partner to accept or decline a higher contract.
- `signoff`: attempts to end the constructive auction at a contract.
- `control_showing`: shows first- or second-round control for slam exploration.
- `keycard_asking`: asks for keycards or related slam assets.
- `ace_asking`: asks for aces outside a trump-keycard structure, such as Gerber over notrump.
- `honor_asking`: asks for a named honor or honor class, such as a specific king ask.
- `shortness_showing`: shows void or singleton information as part of splinter or exclusion logic.
- `multivalent`: intentionally carries multiple possible meanings to be resolved later.
- `resolution`: narrows or resolves a previous multivalent context.
- `escape`: runout, scramble, pass-or-correct, or other rescue action.
- `final_placement`: places the contract unless partner has an explicit override.

Auxiliary nature labels may still be stored for disclosure and alert analysis:

- `natural`
- `artificial`
- `conventional`
- `penalty`
- `takeout`
- `negative_double`
- `support_double`
- `responsive`
- `redouble`
- `pass`

Executable behavior:

- A Call Specification may have one or more Call Act Types.
- Public meaning may display a readable version of Call Act Type, but the type itself is structured data.
- Alert analysis may query Call Act Type together with public meaning and regulatory regulations.
- Protocol Frames and Bidding Plans are created from Call Act Types plus explicit effects.
- Later Call Specifications may require a Call Act Type, but should prefer precise semantic objects when the exact context matters.

Example:

```yaml
meaning:
  public_text: "Transfer to hearts."
  nature_labels: [artificial, conventional]
  call_act_types: [directive, context_initiating]
effects:
  - open_protocol_frame:
      type: transfer
      target_suit: H
      initiator: actor
      acceptor: partner
```

## 7. Shown Hand Attributes

Shown hand attributes describe what the auction says about a player.

### `hcp_range`

Fields:

- `min`
- `max`
- `source`
- `confidence`

Executable behavior:

- Multiple Call Specifications can narrow a range.
- Conflicting ranges should generate diagnostics.
- The state must preserve Call Specification origins for training/debug output.

Example:

```yaml
shows:
  - subject: actor
    hcp:
      min: 15
      max: 17
```

### `suit_length`

Fields:

- `suit`: `C D H S`
- `min`
- `max`
- `exact`
- `subject`

Executable behavior:

- Used for later selection and explanation.
- Multiple facts should merge by tightening ranges when possible.
- Impossible intersections create conflict diagnostics.

Example:

```yaml
shows:
  - subject: actor
    suit: H
    length:
      min: 5
```

### `shape_class`

Recommended values:

- `balanced`
- `semibalanced`
- `unbalanced`
- `single_suiter`
- `two_suiter`
- `three_suiter`
- `minor_two_suiter`
- `major_two_suiter`

Executable behavior:

- Used as a broad descriptor.
- Should not replace explicit suit-length constraints when exact behavior matters.

### `stopper`

Fields:

- `suit`
- `status`: `shown`, `denied`, `asked`, `unknown`
- `quality`: optional structured metric

Executable behavior:

- Used by notrump decisions, competitive auctions, and Lebensohl-style structures.

### `control`

Fields:

- `suit`
- `agreed_suit`
- `round`: `first`, `second`, `first_or_second`
- `status`: `shown`, `denied`, `asked`

Executable behavior:

- Used in slam auctions and control-bidding Conventions.
- Does not by itself define the whole slam route. A control bid normally also creates or updates `slam_interest` and may open a `control_bidding` Protocol Frame.

## 8. Suit, Trump, And Notrump State

This project uses the term **suit** for `C D H S N`. For bridge trump, only `C D H S` can become a trump suit; `N` means notrump.

### `proposed_suit`

Meaning: a suit suggested by a call but not necessarily agreed.

Executable behavior:

- Can be overwritten or accumulated.
- Does not by itself make later `4N` RKCB.

### `target_suit`

Meaning: the intended suit in a transfer, relay, or puppet action.

Executable behavior:

- Used by transfer and puppet Call Specifications.
- May become proposed or agreed later depending on the convention.

### `agreed_suit`

Meaning: partnership has agreed a trump suit.

Executable behavior:

- Can be set explicitly by raise, fit-showing call, Texas transfer agreement, or another convention-specific effect.
- Later slam Conventions may query it.
- A call that merely completes Jacoby transfer does not automatically agree trump unless the active Call Specification says so.

### `minor_raise`

Meaning: responder has raised opener's minor through a formal minor-raise structure.

Fields:

- `target_suit`: `C` or `D`.
- `strength`: `invitational_plus`, `game_force`, or another declared partnership range.
- `method`: `inverted_minor`, `crisscross`, or another named method.

Executable behavior:

- Usually creates or confirms `agreed_suit`.
- May set `forcing_status`, such as `forcing_to_2N_or_3m` or `game_forcing`.
- Can be consumed by stopper-showing continuations, notrump-placement decisions, Minorwood-style slam tools, or later signoff/default policy.

### `trump_candidate`

Meaning: likely future trump suit but not fully agreed.

Executable behavior:

- Useful for auctions where a suit is strongly implied but still negotiable.
- RKCB Call Specifications should normally require `agreed_suit`, not only `trump_candidate`, unless a Convention explicitly allows that style.

### `notrump_focus`

Meaning: the auction is oriented around notrump.

Executable behavior:

- Supports quantitative 4N, stopper asks, and notrump game/slam decisions.
- Conflicts with an agreed trump suit only if a Call Specification declares them mutually exclusive.

Example:

```yaml
effects:
  - set_notrump_focus:
      subject: partnership
      status: active
```

### `notrump_contract_interest`

Meaning: the partnership is investigating or proposing notrump as the practical destination.

Fields:

- `level`
- `source`

Executable behavior:

- Used by inverted-minor and stopper-bidding continuations.
- Does not place the final contract by itself; a later `final_contract` fact should do that.

## 9. Transfer State

Transfers need formal state because later calls may accept, superaccept, decline, retransfer, or define special behavior after interference.

### `transfer`

Fields:

- `owner`: player who made the transfer call.
- `acceptor`: partner expected to act.
- `bid_suit`: suit actually bid.
- `target_suit`: intended suit.
- `status`: `pending`, `accepted`, `superaccepted`, `declined`, `retransfer_requested`, `completed`
- `interference`: optional structured object
- `origin`: Call Specification origin

Executable behavior:

- A transfer-creating Call Specification writes `status: pending`.
- Completion changes status to `accepted` or `completed`.
- Superaccept changes status to `superaccepted`.
- Interference can modify obligations without destroying the transfer.
- Later Call Specifications query the transfer object by target suit, owner, acceptor, and status.

Example transfer creation:

```yaml
effects:
  - create_transfer:
      owner: actor
      acceptor: partner
      bid_suit: D
      target_suit: H
      status: pending
```

Example normal completion:

```yaml
requires:
  transfer:
    target_suit: H
    status: pending
effects:
  - update_transfer:
      target_suit: H
      status: completed
  - set_proposed_suit:
      suit: H
      source: transfer_completion
```

Example doubled transfer retransfer:

```yaml
context:
  auction_pattern: "1NP2DXP"
call: R
requires:
  transfer:
    target_suit: H
    status: pending
  interference:
    over_call: X
    over: transfer_bid
effects:
  - update_transfer:
      target_suit: H
      status: retransfer_requested
```

The exact auction above is an example only. The important design policy is that the retransfer Call Specification should query formal transfer and interference state.

## 10. Relay And Puppet State

### `relay`

Fields:

- `asker`
- `describer`
- `topic`
- `status`: `pending`, `answered`, `broken`

Executable behavior:

- Relay systems create obligations for the describer.
- The reply consumes or advances relay state.
- Relay state may be backed by a Relay Automaton when responses are defined by steps instead of fixed auction strings.
- A relay can survive interference if its Protocol Frame declares continuation policies. For example, a Convention may use pass, double, and redouble as relay steps over interference.

### `checkback_relay`

Meaning: a two-way NMF/XYZ-style relay is active.

Fields:

- `relay_call`: requested partner call, such as `2D` or `3C`.
- `status`: `pending`, `completed`, `cancelled`.
- `strength_band`: optional tag such as `invitational_or_weak_diamonds`.

Executable behavior:

- Responder's artificial checkback call creates the relay fact.
- Opener's forced relay completion creates a completion fact, such as `checkback_relay_completion` or `checkback_club_drop_dead_completion`.
- Later calls can distinguish weak drop-dead routes, invitational routes, game-forcing checkback, and slam-interest continuations without relying on a prose meaning string.

### `checkback_game_force`

Meaning: responder has started the artificial game-forcing branch of two-way NMF/XYZ.

Fields:

- `status`: `pending`, `answered`, `closed`.

Executable behavior:

- Opener continuations may show three-card support, deny support, show stoppers, or make another partnership-defined descriptive move.
- The current benchmark implements only a small support/no-support slice.

### `relay_automaton`

A Relay Automaton is the formal executable object for step-based relay systems such as KK Relay, Symmetric Relay, Precision-style relays, or strong-diamond game-force relays.

Fields:

- `asker`
- `describer`
- `current_stage`
- `known_description`
- `remaining_partitions`
- `next_relay_call`
- `response_decoder`
- `step_table`
- `reserved_calls`
- `break_conditions`
- `interference_policy`

Executable behavior:

- Computes the next relay ask, commonly the cheapest legal asking step.
- Decodes the describer's actual call into a response step.
- Updates known shape, strength, controls, honor location, or other described attributes.
- Determines whether shape or another topic is resolved.
- Advances to later stages such as slam-point asking, denial cuebidding, keycard asking, or final placement.
- Handles declared relay breakoffs and relay continuations after interference.

Relay response steps are relative to the current auction context. They should not be stored only as absolute natural-language meanings.

Example shape-resolution skeleton:

```yaml
relay_automaton:
  id: symmetric_shape_relay
  asker: captain
  describer: partner
  next_relay_call: cheapest_step
  stages:
    shape_family:
      responses:
        step_1: {show: balanced_family}
        step_2: {show: one_suited_family}
        step_3: {show: two_suited_family}
    shape_resolution:
      continue_until: shape_resolved
```

### `puppet`

Fields:

- `asker`
- `describer`
- `requested_suit_or_shape`
- `status`

Executable behavior:

- Similar to relay, but specifically asks partner to bid a suit or describe holding in a controlled way.

## 11. Protocol Frames

A Protocol Frame is a live semantic context created by the auction. It prevents the engine from treating every later call as an isolated pattern.

Examples:

- heart transfer after `1N P 2D`,
- 2/1 game force,
- Lebensohl relay,
- strong `1D` artificial opening,
- provisional game force after `1C-1D`,
- RKCB/keycard context,
- control-bidding context,
- Symmetric Relay shape-resolution context.

Fields:

- `frame_id`
- `frame_type`
- `owner_convention`
- `initiator`
- `responder`
- `captain`
- `topic`
- `status`: `active`, `satisfied`, `broken`, `closed`
- `variables`
- `stages`
- `allowed_continuations`
- `break_conditions`
- `source_call`

Executable behavior:

- Created by Call Specification effects.
- Queried by later Call Specifications and Call Selection Policies.
- Can push another Protocol Frame, such as a transfer frame leading into a slam-control frame.
- Can be satisfied, cancelled, broken by interference, or closed by final placement.
- Must preserve origin so internal provenance can explain why a later call was interpreted in that context.

Example:

```yaml
effects:
  - open_protocol_frame:
      frame_type: major_transfer
      target_suit: H
      initiator: responder
      responder: opener
      stages:
        - opener_rebid
        - responder_continuation
```

## 12. Bidding Plans

A Bidding Plan is the bidder's internal route through a sequence of calls. It is used for selection and training provenance, not ordinary opponent disclosure.

Examples:

- transfer followed by signoff,
- transfer followed by invitation,
- transfer followed by second-suit slam exploration,
- Smolen route,
- Texas transfer to game,
- Lebensohl slow route followed by cuebid,
- 2/1 route followed by splinter,
- relay until shape is resolved, then place the contract,
- keycard route followed by slam placement.

Fields:

- `plan_id`
- `owner`
- `source_convention`
- `entry_call`
- `private_goal`
- `applies_when`
- `expected_frames`
- `branches`
- `continuation_policy`
- `exit_conditions`
- `fallback_policy`

Executable behavior:

- A Call Selection Policy may compare candidate Bidding Plans, then bid the entry call of the selected plan.
- The selected plan should be recorded in internal provenance.
- A plan may be contingent. If partner chooses a different branch, the plan can continue, adapt, or end according to its branches.
- Public meaning should normally disclose the entry call's partnership meaning, not the entire private plan.

Example:

```yaml
bidding_plan:
  id: plan_1
  description: Transfer first, then show spades with slam interest if the continuation permits it.
  entry_call: 2D
  applies_when:
    self.hearts: {min: 5}
    self.spades: {min: 5}
    slam_interest: true
  branches:
    opener_completes_transfer:
      next_action: show_spades
    opener_superaccepts:
      next_action: start_control_bidding
```

## 13. Call Selection Policies

A Call Selection Policy is the explicit algorithm that chooses among candidate calls or candidate Bidding Plans.

The policy may live in a Convention Set or inside a Convention. It is a peer to Call Specification YAML files, not a hidden field inside one competing call.

Fields:

- `policy_id`
- `author`
- `scope`
- `candidate_filter`
- `algorithm`
- `evaluators`
- `tie_breaker`
- `random_source`
- `explanation_template`
- `source_convention`

Allowed algorithm families:

- `decision_tree`
- `decision_table`
- `lexicographic_comparator`
- `scoring_evaluator`
- `randomized_choice`
- `external_plugin_evaluator`

Executable behavior:

1. Call Specifications and active Protocol Frames generate candidate calls and candidate Bidding Plans.
2. The engine removes illegal or inapplicable candidates.
3. The most specific applicable Call Selection Policy compares candidates.
4. The policy returns the selected call or reports ambiguity.
5. The selected call records Selection Provenance, including compared alternatives and evaluator results.

Example opening policy:

```yaml
call_selection_policy:
  id: opening_choice_policy
  scope:
    auction_phase: opening
  algorithm: decision_tree
  steps:
    - if: strong_two_club_condition
      choose: 2C
    - if: notrump_15_17_balanced
      choose: 1N
    - if: five_card_major_opening
      choose: longest_major
    - otherwise: normal_minor_or_pass
```

If `1H` and `1N` are both available and no policy resolves the choice, the engine must emit an ambiguity diagnostic instead of using file order or hidden priority.

## 14. Forcing And Obligation State

### `preemptive_opening`

Meaning: the partnership opened preemptively.

Fields:

- `level`: preempt level.
- `target_suit`: suit opened.
- `style`: optional descriptor such as `seat_and_vulnerability_dependent`.

Executable behavior:

- Created by weak two and three-level preempt Call Specifications.
- Selection should normally use `env.seat_position`, `env.vulnerability_relation`, suit length, HCP, and suit quality evaluators.
- Does not require a special language field for every partnership style; style choices belong in Named Evaluators or Call Selection Policies.

### `gambling_3nt`

Meaning: `3N` opening is Gambling rather than a natural notrump opening.

Fields:

- `status`: `active`, `resolved`, or `cancelled`.

Executable behavior:

- Usually creates `running_minor`.
- Public meaning should normally be alertable.
- Later continuations can ask opener to pass/correct, run to the minor, or clarify outside strength depending on partnership style.

### `running_minor`

Meaning: the opening side has a long solid or nearly solid minor suitable for a Gambling 3N route.

Fields:

- `target_suit`: `C` or `D`.
- optional `quality`.

Executable behavior:

- Can be used by partner's continuations over Gambling 3N.
- Should be produced from card-evaluator logic, not guessed from the auction string alone.

### `final_contract`

Meaning: a call has placed the intended final contract unless partner has an explicit override.

Fields:

- `target_suit`
- `level`
- `source`

Executable behavior:

- Default policy may generate a normal pass when `final_contract` exists.
- Multiple pass candidates with the same `pass_final_contract` action are structurally equivalent; the engine may choose the most specific or highest-scoring origin without treating it as a meaning ambiguity.

### `forcing_status`

Recommended values:

- `not_forcing`
- `forcing_one_round`
- `game_forcing`
- `slam_forcing`
- `pass_forcing`

Executable behavior:

- A Call Specification can set forcing status for a partnership or a seat.
- Default policy should consult forcing status before choosing pass.
- Conflicting forcing statuses should merge toward the strongest active force unless a Call Specification explicitly ends the force.

### `obligation`

Fields:

- `subject`: seat or role expected to act.
- `action_type`: formal expected action.
- `target`: optional suit, level, call type, or semantic object.
- `status`: `active`, `satisfied`, `cancelled`, `failed`
- `source`

Executable behavior:

- Transfer acceptance, relay replies, forced bids, and forcing pass actions should be obligations.
- A selected or historical call can satisfy an obligation.
- Unsatisfied obligations should appear in diagnostics.

Example:

```yaml
effects:
  - create_obligation:
      subject: partner
      action_type: accept_transfer_or_superaccept
      target_suit: H
      status: active
```

## 15. Competitive State

Competitive auctions need formal representation of opponent action.

### `interference`

Fields:

- `actor_side`: `theirs`
- `call`
- `over`: semantic object or call index
- `level`
- `suit`
- `type`: `bid`, `double`, `redouble`, `preempt`, `cuebid`

Executable behavior:

- Created when opponents bid, double, or redouble over an agreement sequence.
- Used to decide whether systems are on, off, modified, or replaced by competitive agreements.

### `double_meaning`

Recommended values:

- `penalty`
- `takeout`
- `negative`
- `responsive`
- `support`
- `lead_directing`
- `card_showing`
- `cooperative`
- `maximal`

Executable behavior:

- A double Call Specification must define which meaning applies under its conditions.
- If multiple double meanings match, the engine should report ambiguity unless a resolver chooses one.

### `systems_status`

Values:

- `on`
- `off`
- `modified`

Executable behavior:

- Applies to a named Convention or convention family.
- Interference Call Specifications can change status.

Example:

```yaml
effects:
  - set_systems_status:
      convention_id: four_way_jacoby_transfer
      status: modified
      reason: transfer_bid_doubled
```

## 16. Slam And Keycard State

### `slam_interest`

Values:

- `none`
- `invite`
- `try`
- `force`

Executable behavior:

- Created by quantitative tries, control bids, keycard asks, cue bids, or explicit slam tries.
- Can be queried by slam Conventions.

### `keycard_context`

Fields:

- `trump_suit`
- `asker`
- `responder`
- `method`: `0314`, `1430`, `kickback_1430`, `minorwood_1430`, `exclusion_1430`, or Convention-defined
- `excluded_suit`: optional suit whose ace is not counted, used by Exclusion/Voidwood methods
- `status`: `pending`, `answered`

Executable behavior:

- A keycard ask requires a known trump source unless the Convention explicitly defines another Call Specification.
- Answers satisfy the pending keycard context.
- The same semantic structure handles ordinary RKCB, Kickback, Minorwood, and Exclusion when the entry Call Specification supplies the method and any excluded suit.

### `ace_ask_context`

Fields:

- `method`: for example `gerber`
- `target_suit`: usually `N` for notrump focus
- `asker`
- `responder`
- `status`: `pending`, `answered`

Executable behavior:

- Used for ace asks that are not trump-keycard asks.
- Responses count aces through an expression such as `ace_count`.
- Later continuations may ask for kings or place the final contract.

### `targeted_king_ask`

Fields:

- `trump_suit`
- `target_suit`
- `rank`: usually `K`
- `status`: `pending`, `answered`

Executable behavior:

- Created after enough keycard information is known.
- A response Call Specification tests whether responder holds the named card.
- A later final-placement Call Specification may require the positive response.

### Slam Tool Families

The ontology treats slam bidding as several reusable Protocol Frames rather than one monolithic Convention:

- `control_bidding`: cooperative cue/control bidding after an agreed suit and slam interest.
- `rkcb_1430`: ordinary 4N keycard for an agreed suit.
- `gerber`: ace asking in notrump-focused auctions.
- `kickback_1430`: keycard asking with the step above four of the agreed suit.
- `minorwood_1430`: keycard asking by bidding four of the agreed minor.
- `exclusion_1430`: keycard asking while excluding the ace of the asker's void suit.
- `targeted_king_ask`: asks for one named king after keycard information.

Each tool should have its own Convention directory and Call Specifications. They communicate by formal state such as `agreed_suit`, `control`, `slam_interest`, `keycard_context`, `ace_ask_context`, and targeted honor facts.

### `four_notrump_resolution`

`4N` is not a meaning by itself. It is a call that must be resolved against semantic state.

Recommended candidate meanings:

- `quantitative_invite`
- `keycard_ask`
- `blackwood_ask`
- `natural`
- `competitive_takeout`
- `two_suited_takeout`

Executable behavior:

1. Gather all active `4N` meaning candidates from active Conventions.
2. Evaluate each candidate's `requires` block against semantic state.
3. Prefer candidates with the most specific satisfied requirements only when the resolver declares a deterministic policy.
4. If multiple candidates remain equally valid, emit an ambiguity diagnostic.
5. If no candidate matches, the auction is undefined for `4N`.

Current prototype behavior: the selector gathers eligible same-call candidates and diagnoses ambiguous meanings. The Meow benchmark includes separate quantitative notrump and RKCB Conventions. Quantitative `4N` requires notrump focus with no agreed suit or pending transfer/Stayman context; RKCB requires an agreed suit.

Example RKCB candidate:

```yaml
call: 4N
requires:
  agreed_suit:
    exists: true
  slam_interest:
    min: try
meaning:
  nature_labels: [artificial, conventional]
  call_act_types: [inquiry, keycard_asking]
  public_text: "Keycard ask."
effects:
  - create_keycard_context:
      trump_suit: agreed_suit
      method: 1430
      status: pending
```

Example quantitative candidate:

```yaml
call: 4N
requires:
  notrump_focus:
    status: active
  agreed_suit:
    exists: false
meaning:
  nature_labels: [natural]
  call_act_types: [invitation]
  public_text: "Quantitative notrump invitation."
effects:
  - set_slam_interest:
      level: invite
      suit: N
```

## 17. Alert And Disclosure State

### `alertability`

Fields:

- `jurisdiction`: for example `ACBL`
- `regulation_version`: optional date/version
- `status`: `alertable`, `not_alertable`, `announcement`, `delayed_alert`, `unknown`
- `source`: `hard_coded`, `regulation_engine`, `manual_override`

Executable behavior:

- Near-term Call Specifications may hard-code `meaning.alertable`.
- Long-term alert analysis should evaluate current regulatory data for the jurisdiction and version.
- Alertability belongs in public/disclosure output, with Call Specification origin.

### `public_disclosure`

Fields:

- `summary`
- `details`
- `nature_labels`
- `call_act_types`
- `shown_values`
- `alertability`

Executable behavior:

- Generated from `meaning` plus ontology state.
- Must not expose private candidate comparisons unless the product explicitly shows a training/debug layer.

## 18. Intermediate Representation Schema Direction

The target Intermediate Representation is larger than one flat call-definition list. It should contain executable objects for the Convention Set, active Conventions, Call Specifications, Protocol Frames, Bidding Plans, Call Selection Policies, Named Evaluators, and Relay Automata.

Current YAML serializes Call Specifications directly. The target Call Specification model should distinguish these sections:

```yaml
call_specifications:
  - id: example_transfer_call
    context: {}
    call: 2D
    applies_when: {}
    requires: {}
    call_act_types: []
    meaning: {}
    shows: []
    effects: []
    clears: []
```

Expected behavior:

- `context` matches visible auction shape.
- `call` is the selected or interpreted call.
- `applies_when` evaluates the actor's actual hand and environment for bid selection.
- `requires` queries semantic state.
- `call_act_types` records the structural role of the call.
- `meaning` defines public partnership explanation.
- `shows` records what the call says about a hand.
- `effects` updates semantic state.
- `clears` removes or satisfies temporary semantic state such as pending obligations.

Selection belongs primarily in Call Selection Policies and Bidding Plans. A Call Specification may still include local applicability conditions, but it should not own global judgment when multiple plausible calls compete.

Example Convention-level layout:

```yaml
convention:
  id: four_way_jacoby_transfer
  call_specifications: []
  protocol_frames: []
  bidding_plans: []
  call_selection_policies: []
  named_evaluators: []
```

Example Convention Set-level layout:

```yaml
convention_set:
  id: expert_2over1
  conventions:
    - two_over_one
    - four_way_jacoby_transfer
  integration_selection_policies: []
  default_policies: []
```

The current prototype uses `requires`, `selection`, `meaning`, and `effects` inside `call_specifications`. Future schema evolution should make `applies_when`, `requires`, `shows`, and ontology-backed effects stricter and fully validated.

## 19. Conflict And Ambiguity Policy

The engine must diagnose semantic problems instead of silently choosing an arbitrary meaning.

Required diagnostics:

- two matching Call Specifications give incompatible public meanings for the same call,
- two matching candidates or plans cannot be resolved by a Call Selection Policy,
- shown hand ranges are impossible after merging,
- an obligation remains active when the auction moves past it,
- a call asks for a semantic object that does not exist,
- a call has multiple valid semantic interpretations, such as quantitative `4N` and RKCB `4N`.
- two Protocol Frames claim incompatible interpretations of the same continuation.
- a Relay Automaton has no legal next step or an uncovered response step.

Resolvers are allowed, but they must be explicit and documented.

## 20. Ontology Extension Policy

If a Convention needs a concept not listed here:

1. Prefer an existing ontology term if the meaning and executable behavior match.
2. If not, add a new formal term to this document.
3. If the concept is experimental or private, namespace it clearly and document its query/write behavior.
4. Do not rely on arbitrary prose or private strings as the only machine-readable state.

## 21. Implementation Milestone Target

The current semantic milestone is an operable 2/1 plus after-1N benchmark where:

- the 2/1 Convention defines the `1N` opening and other basic openings,
- the four-way Jacoby transfer Convention defines after-1N transfer responses and continuations,
- transfers create formal transfer state,
- completions and superaccepts query and update transfer state,
- later routes such as Texas and Smolen can compete by formal hand/environment/semantic conditions,
- `4N` and other slam tools can be resolved by semantic context instead of auction enumeration. First slices exist for quantitative notrump, ordinary RKCB, control bidding, Gerber, Kickback, Minorwood, Exclusion keycard, and targeted king asks.
- Bidding Plans can represent route choices such as transfer-then-signoff, transfer-then-invite, Texas transfer, and Smolen.
- Call Selection Policies can choose among candidate openings and after-1N plans without hidden priority or file-order behavior.
- Protocol Frames can carry the transfer context across multiple continuation rounds.
- Relay Automata are specified enough to model a small proof-of-concept relay sequence.

## 22. Benchmark Coverage Targets

The ontology should be tested against several representative bridge families:

- **Washington Standard**: mainstream expert five-card-major 2/1, stressing judgmental Call Selection Policies and Named Evaluators.
- **Strong Diamond**: artificial strong `1D`, nebulous `1C`, seat-dependent opening policy, and relay continuations after game forces.
- **KK/Symmetric Relay**: cheapest-step relay asks, step responses, shape-resolution automata, relay breakoffs, and later slam-control stages.
- **Precision/Polish Club families**: strong or nebulous club openings, multivalent meanings, and resolution by later calls.
- **Common Convention library**: Stayman, Jacoby/Texas transfers, Smolen, Lebensohl, Drury, Michaels, Unusual 2N, RKCB, Gerber, splinters, support doubles, negative doubles, and competitive runouts.

Within the problem definition where input is visible auction, environment, own hand, semantic state derived from those inputs, and a declared random source, the target IR is expressively complete if it can represent finite mappings from those inputs to legal calls or probability distributions over legal calls. Practical authoring depends on compressed structures such as Protocol Frames, Bidding Plans, Call Selection Policies, Named Evaluators, and Relay Automata.
