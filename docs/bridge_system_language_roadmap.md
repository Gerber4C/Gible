# Bridge System Language Roadmap

Platform Version: 0.0.6
Author: Meow Li
Copyright: Copyright (c) 2026 Meow Li. All Rights Reserved.

This document defines the roadmap for moving from current direct YAML authoring toward a layered authoring system with a Bridge System Language, a strict Intermediate Representation, and GUI tools.

The current YAML/IR language itself is specified in `docs/ir_language_spec.md`. This roadmap describes how BSL, GUI forms, compiler tooling, and validation should grow around that executable language.

## 1. Core Decision

Partner should separate human authoring from engine execution.

Target architecture:

```text
Guided GUI controls  <->  Bridge System Language source  <->  IR/YAML inspector
        |                         |                              |
        v                         v                              v
      IR draft              Compiler and validator          IR validation
        \                         |                              /
         \                        v                             /
          ----------------> Intermediate Representation <-------
                                  |
                                  v
                    Engine interpreter and executor
```

The engine executes the strict Intermediate Representation. The Bridge System Language is an authoring layer, not the runtime object. The GUI may generate Bridge System Language or direct IR depending on the task; direct IR editing remains a first-class advanced workflow.

YAML remains useful as the current file format for the Intermediate Representation. In the future, YAML can continue as the readable serialization format for compiled objects, tests, import/export, and debugging.

## 1A. Python-Native Static Source Option

A later authoring layer may use Python syntax as a static source format instead of inventing every surface grammar from scratch. This does not mean executing user Python at bidding time.

The safe version is:

- users write Python-like expressions, dataclass literals, or declarative class objects for Conventions, Call Specifications, Bidding Plans, Protocol Frames, Named Evaluators, and Call Selection Policies;
- the platform parses the source with a restricted Python AST;
- only whitelisted constructs are accepted: literals, dataclass construction, class attributes with approved base classes, boolean/comparison/arithmetic expressions, and references such as `self.hcp`, `self.length(H)`, `env.vulnerability_relation`, and `state.has(...)`;
- imports, arbitrary function calls, mutation, loops, comprehensions, file/network/process access, reflection, and runtime execution are rejected;
- accepted source compiles to the same typed IR object model that YAML currently serializes.

This option may reduce burden because YAML/JSON is essentially static data, while Python syntax can express static data and limited formulas more compactly. It also supports richer editor tooling and type checking. The boundary remains the same: the engine executes validated IR, not arbitrary user code.

Open design question: whether the long-term advanced source format should be BSL, restricted Python-source dataclasses, or both synchronized through the same IR inspector. The current checkpoint documents the option only; it does not change runtime architecture.

## 2. Definitions

### Bridge System Language

Bridge System Language, or BSL, is a formal domain-specific language for describing bridge bidding agreements.

BSL should feel closer to bridge writing than raw YAML, but it must not be free English. It needs grammar, keywords, validation, and a compiler.

Example style:

```text
after 1N P:
  call 2D:
    transfer to H
    applies when responder.length(H) >= 5
    creates transfer target H status pending
    opener must accept_transfer_or_superaccept H
    alertable ACBL
```

BSL should use the ontology vocabulary from `docs/semantic_ontology.md`.

BSL expression syntax may be Python-like, but BSL must not execute Python. The recommended path is:

1. Parse a small expression grammar or a restricted Python AST.
2. Accept only whitelisted names such as `self`, `partner`, `env`, `state`, `length`, `hcp`, `ace_count`, `keycard_count`, `has`, boolean operators, comparisons, and elementary arithmetic.
3. Reject function calls, imports, attribute access outside the whitelist, mutation, loops, comprehensions, I/O, and any runtime evaluation.
4. Compile the accepted expression into the structured IR expression tree used by YAML.

Example BSL-style predicate:

```text
applies when self.hcp >= 16 and self.length(H) >= 6 and self.has(D, A)
```

Compiled IR shape:

```yaml
expr:
  op: and
  args:
    - op: gte
      left: {var: self.hcp}
      right: {const: 16}
    - op: gte
      left:
        op: length
        hand: self
        suit: H
      right: {const: 6}
    - op: contains_rank
      hand: self
      suit: D
      rank: A
```

This gives users a familiar writing surface while preserving deterministic, inspectable IR.

### Intermediate Representation

The Intermediate Representation, or IR, is the strict structured form that the engine can execute.

Current YAML Call Specification files are an early version of this IR.

Example IR shape:

```yaml
context:
  auction_pattern: "1NP"
call: 2D
applies_when:
  hand:
    H:
      min_length: 5
meaning:
  nature_labels: [artificial, conventional]
  call_act_types: [directive, context_initiating]
  public_text: "Transfer to hearts."
effects:
  - create_transfer:
      target_suit: H
      status: pending
```

The IR should be explicit, normalized, validated, and executable. It is acceptable if technical users prefer editing IR directly.

The target IR must contain several executable object types, not only a flat list of call definitions:

- **Convention Set**: the complete selected partnership agreement.
- **Convention**: a portable agreement module.
- **Call Specification**: one call in one context, with applicability, public meaning, and effects.
- **Protocol Frame**: a live auction context such as transfer, game force, relay, or keycard ask.
- **Bidding Plan**: an internal multi-step route such as transfer-then-signoff or relay-until-shape-resolved.
- **Call Selection Policy**: the explicit algorithm that compares candidate calls or plans.
- **Named Evaluator**: a reusable limited hand/environment function.
- **Relay Automaton**: step-based relay asking and response-decoding machinery.

These object types can be serialized in YAML for readability, but the engine should validate them as typed IR.

### Compiler

The compiler converts BSL into IR.

Compiler responsibilities:

- parse BSL syntax,
- resolve bridge keywords against the ontology,
- normalize calls and auction patterns,
- produce IR,
- validate required fields,
- detect ambiguous or unsupported phrases,
- preserve source locations for error messages,
- emit warnings for incomplete agreements.

### Interpreter

The interpreter is the engine layer that executes IR.

Interpreter responsibilities:

- replay auction history,
- build semantic state,
- match Call Specification context,
- evaluate `requires` and `applies_when`,
- create active Protocol Frames,
- generate candidate calls and candidate Bidding Plans,
- compare candidates through Call Selection Policies,
- update semantic state through effects,
- produce public meaning, internal origin, and diagnostics.

## 3. Important Product Policy

BSL is not always easier than IR.

Different users and tasks need different surfaces:

- Casual users may prefer guided forms.
- Bridge writers may prefer BSL.
- Technical users may prefer IR/YAML.
- AI agents may generate BSL first, then compile and validate.
- Test authors may prefer direct IR/YAML fixtures.

Therefore the GUI should support multiple synchronized views instead of forcing one authoring mode.

Target authoring model:

```text
Form View <-> BSL View <-> IR/YAML View
```

The system must make clear which view is authoritative for a given edit. The safest default is:

1. form edits generate or update BSL,
2. BSL compiles to IR,
3. IR is executed by the engine,
4. direct IR edits are allowed only in advanced mode and must be validated.

## 4. GUI Responsibilities

The GUI should be a bridge-system editor, not a raw file editor.

### Form View

Audience:

- casual users,
- teachers,
- system authors who are entering common structures.

Expected behavior:

- provide bridge-aware controls for auction context, call, meaning, hand requirements, obligations, and alertability,
- generate BSL or IR from user selections,
- prevent impossible combinations when possible,
- explain validation errors in bridge language,
- show generated source for review.

Example form fields:

```text
Auction context: after 1N P
Call: 2D
Meaning type: transfer
Target suit: H
Responder requirement: length(H) >= 5
Opener obligation: accept or superaccept
Alert status: ACBL alertable
```

### BSL View

Audience:

- advanced bridge users,
- system designers,
- users editing imported notes,
- LLM-assisted workflows.

Expected behavior:

- provide syntax highlighting,
- autocomplete ontology keywords,
- autocomplete calls and suits,
- show compile errors with source locations,
- show the compiled IR preview,
- support comments and readable organization.

### IR/YAML View

Audience:

- engineers,
- AI agents,
- power users,
- test authors.

Expected behavior:

- show normalized compiled objects,
- allow direct editing in advanced mode,
- validate against the IR schema,
- show Call Specification origins and semantic effects,
- support diffing and debugging.

The IR/YAML view should not be hidden, because some complex objects are clearer when written structurally.

### Protocol And Plan View

Audience:

- advanced bridge users,
- relay-system authors,
- teachers explaining multi-step auctions,
- AI agents validating system notes.

Expected behavior:

- show active Protocol Frames created by earlier calls,
- show Bidding Plans that compete for the current hand,
- show which Call Selection Policy chose the current route,
- let users define branches such as accept, superaccept, deny, relay answer, break relay, ask keycards, sign off, or place contract,
- display relay steps as tables when a Convention uses a Relay Automaton.

This view is necessary for auctions where a first call is chosen because of a later route. For example, after `1N P ?`, `2D` may be the first call of signoff, invitation, slam try, or 5-5 major plans. The user should describe those routes as Bidding Plans and continuations, not as unrelated meanings attached to the same `2D` string.

Example form concept:

```text
Plan: Transfer then show spades with slam interest
Entry call: 2D
Use when: hearts >= 5, spades >= 5, slam interest
If opener completes: bid spades
If opener superaccepts: start control bidding
If opener denies cooperation: place game or sign off by evaluator
```

## 5. Source Of Truth Policy

Each Convention should eventually declare its source mode.

Recommended source modes:

- `bsl_source`: BSL is authoritative; IR is compiled output.
- `ir_source`: IR/YAML is authoritative; BSL may be generated as a readable view when possible.
- `generated_draft`: created by LLM or import tooling and not yet approved.

The engine should only load approved, validated IR.

BSL source and IR output should both preserve author metadata, platform version, Convention version, Call Specification origin, and source locations when possible.

## 6. Relationship To Ontology

The ontology is the type system and vocabulary for BSL and IR.

BSL keywords should map to ontology concepts:

- `transfer` maps to formal transfer state.
- `agreed suit` maps to `agreed_suit`.
- `notrump focus` maps to `notrump_focus`.
- `game forcing` maps to `forcing_status: game_forcing`.
- `keycard ask` maps to `keycard_context`.
- `control bid` maps to `control` plus `slam_interest`.
- `Gerber` maps to `ace_ask_context.method: gerber`.
- `Kickback`, `Minorwood`, and `Exclusion` map to `keycard_context` with distinct `method` values.
- `specific king ask` or `targeted king ask` maps to `targeted_king_ask`.
- `interference` maps to competitive state.
- `must` creates an obligation.

If a BSL phrase cannot map to ontology or validated custom extension terms, the compiler should reject it or mark the generated object as an unapproved draft.

## 7. Roadmap Milestones

### Milestone 0: Current YAML Prototype With Initial IR Objects

Status: current checkpoint.

The platform has:

- compact call and auction notation,
- compact hand strings,
- directory-based Convention files,
- YAML Call Specification files,
- a starter 2/1 Convention,
- a starter four-way Jacoby transfer Convention,
- fixture-driven tests,
- public meaning and internal origin output.
- loadable Protocol Frame, Bidding Plan, Call Selection Policy, Named Evaluator, and Relay Automaton classes.
- named Call Selection Policy reporting for highest-score selection.

YAML is currently both the authoring format and the executable structure. The first IR checkpoint is structural: several target object types load and preserve provenance, while only Call Specifications and simple Call Selection Policies affect bidding behavior.

### Milestone 1: Formal IR Schema

Goal: define the strict executable objects the engine executes.

Work:

- decide final IR object schemas for Convention Set, Convention, Call Specification, Protocol Frame, Bidding Plan, Call Selection Policy, Named Evaluator, and Relay Automaton,
- decide final Call Specification fields such as `context`, `call`, `applies_when`, `requires`, `call_act_types`, `meaning`, `shows`, `effects`, and `clears`,
- define schema validation,
- normalize current YAML into the IR schema,
- define how current `selection`, `meaning`, and `effects` become stricter validated IR fields.

Exit criteria:

- invalid IR files produce clear validation errors,
- every loaded Call Specification has a normalized IR form,
- Convention-level policy files can be loaded as data and simple highest-score policies can be reported as selection provenance,
- tests can inspect normalized IR.

### Milestone 2: Ontology-Backed Semantic State

Goal: replace flexible ad-hoc semantic facts with formal Semantic State and Protocol Frames.

Work:

- implement `SemanticState`,
- implement ontology effect handlers,
- implement ontology query handlers,
- support formal transfer state,
- support agreed-suit/trump and notrump-focus state,
- support forcing and obligation state,
- support competitive interference state,
- support active Protocol Frames,
- support Call Act Type history,
- support ambiguity diagnostics.

Exit criteria:

- Jacoby transfer Call Specifications use formal transfer state,
- `4N` examples can be represented as semantic-resolution candidates,
- diagnostics identify ambiguous or missing semantic state.

### Milestone 2A: Selection Policies And Bidding Plans

Goal: make judgmental choice explicit and portable.

Work:

- implement Bidding Plan loading and validation,
- implement Call Selection Policy loading and validation,
- implement decision-tree and decision-table policies first,
- implement simple scoring evaluators with declared input primitives,
- support deterministic random-source selection for declared randomized policies,
- record Selection Provenance in internal origin output.

Exit criteria:

- opening `1M` versus `1N` can be resolved by a declared policy,
- after-1N routes such as Jacoby transfer, Texas transfer, Smolen, signoff, and invitation can compete as Bidding Plans,
- unresolved candidate conflicts produce diagnostics instead of hidden priority behavior.

### Milestone 2B: Relay Automaton Proof Of Concept

Goal: prove that step-based relay systems fit the architecture.

Work:

- implement cheapest-step ask calculation,
- decode response steps,
- store unresolved and resolved shape/state partitions,
- allow a small declared relay table,
- support declared relay breakoffs,
- model pass/double/redouble as relay steps after interference in a restricted example.

Exit criteria:

- a miniature Symmetric Relay-style sequence can be represented without enumerating every auction string,
- the engine can explain the relay ask, relay response, and updated known description.

### Milestone 3: BSL Grammar Draft

Goal: design a small but real language syntax.

Work:

- define grammar for `after`, `call`, `applies when`, `requires`, `shows`, `creates`, `sets`, `clears`, `must`, and `alertable`,
- choose parser technology,
- implement source-location-aware parser errors,
- compile BSL into normalized IR,
- add BSL examples equivalent to current YAML examples.

Exit criteria:

- current 1N opening and heart-transfer example can be written in BSL,
- BSL compiles to the same normalized IR as hand-written YAML,
- malformed BSL gives useful errors.

### Milestone 4: Round-Trip And Diff Tooling

Goal: make source transformations inspectable.

Work:

- display BSL source beside compiled IR,
- show semantic diff between object versions,
- preserve comments where practical,
- preserve source locations from BSL to IR diagnostics,
- define when IR can be converted back to readable BSL.

Exit criteria:

- users can understand what a GUI or LLM-generated change did,
- tests verify BSL-to-IR compilation output.

### Milestone 5: GUI Form Builder

Goal: support non-programmer authoring for common agreement objects.

Work:

- create forms for auction context, call, meaning, hand requirements, obligations, and alertability,
- generate BSL or IR from form input,
- compile and validate before saving,
- show generated source and diagnostics,
- support common Convention templates.

Exit criteria:

- a user can create a simple transfer Call Specification without writing YAML,
- validation errors are understandable to a bridge player.

### Milestone 6: BSL Editor

Goal: support advanced text authoring.

Work:

- syntax highlighting,
- ontology keyword autocomplete,
- call and suit autocomplete,
- inline errors,
- compiled IR preview,
- test-run button for example hands and auctions.

Exit criteria:

- advanced users can write and validate BSL directly.

### Milestone 7: IR/YAML Inspector And Advanced Editor

Goal: keep precise technical editing available.

Work:

- show normalized IR,
- allow advanced direct IR edits,
- validate schema on every save,
- show origin, semantic effects, and compiled output,
- support exporting IR/YAML.

Exit criteria:

- engineers and AI agents can debug the exact executable IR object.

### Milestone 8: LLM-Assisted Drafting

Goal: convert natural bridge descriptions into draft BSL or IR.

Work:

- use LLM to draft BSL from natural-language system notes,
- compile generated BSL to IR,
- validate against ontology and schema,
- require user review and approval,
- show differences from existing Convention files.

Exit criteria:

- LLM output is never silently activated,
- generated Conventions remain drafts until validated and approved.

### Milestone 9: System Notes Import And Export

Goal: connect formal objects with human-readable system notes.

Work:

- generate readable system notes from IR,
- import or draft BSL from existing notes,
- support examples, warnings, and undefined continuations,
- preserve public disclosure separately from internal training details.

Exit criteria:

- users can move between system notes, BSL, IR, and engine behavior with clear validation.

## 8. Testing Requirements

Each language layer needs tests.

Required test categories:

- BSL parser accepts valid examples,
- BSL parser rejects malformed examples,
- BSL compiler emits expected IR,
- IR schema rejects invalid objects,
- ontology effects produce expected Semantic State,
- GUI-generated objects compile to expected IR,
- LLM-generated drafts must remain unapproved by default,
- BSL and IR examples produce the same bidding behavior.

Human-readable test documentation must be updated whenever test fixtures change.

## 9. Open Design Questions

Questions to resolve before implementation:

1. What parser technology should BSL use?
2. Should BSL be indentation-based, block-based, or line-oriented?
3. How much free-form display text should BSL allow?
4. How should comments survive BSL-to-IR compilation?
5. Can every IR object be represented in BSL, or should some advanced objects remain IR-only?
6. How should source mode be stored per Convention?
7. Should GUI forms generate Bridge System Language first or direct IR first for simple objects?
8. How much of a Relay Automaton should be editable through forms versus tables versus direct IR?
9. Which Named Evaluator primitives should be built in for expert judgment without allowing unsafe arbitrary code?
10. How should Convention Set-level Call Selection Policies override or combine Convention-level policies?
11. What syntax should BSL use for Bidding Plans and contingent branches?

The current recommendation is to make BSL the preferred human-readable source, but to keep direct IR editing as a first-class advanced workflow. Predicate syntax should be Python-like only as parsed source code that compiles to safe IR; the platform should not run user Python.
