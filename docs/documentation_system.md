# Documentation System

Platform Version: 0.0.6
Author: Meow Li
Copyright: Copyright (c) 2026 Meow Li. All Rights Reserved.

This document explains how Partner documentation is organized. It is the first file a new human contributor or AI agent should read when entering the repository from a fresh start.

## Documentation Goals

The documentation has four jobs:

1. Explain the product clearly to bridge players, potential users, and potential investors.
2. Teach users how to use the platform and how advanced users author custom Conventions.
3. Give engineers and AI agents enough technical detail to recover the project logic from code and docs alone.
4. Preserve open questions and future ideas without mixing them into active specs.

## Current Documents

Markdown is the editable source of truth. PDF copies are not maintained by default.

### `docs/product_description.md`

Audience:

- Bridge players.
- Teachers and partnership coaches.
- Club or tournament organizers.
- Potential investors or business partners.
- Users who can use software tools but do not need programming knowledge.

Purpose:

- Describe the product.
- Explain the layered architecture: Convention authoring/execution first, tournament/inter-user play second.
- Explain strict agreement execution, generated system notes, and future LLM-assisted authoring.

### `docs/user_manual.md`

Audience:

- New users.
- Intermediate bridge players configuring agreements.
- Advanced players writing custom Conventions.
- Power users testing bidding methods.

Purpose:

- Beginner guide.
- Convention Set usage guide.
- Explanation-output guide.
- Advanced Convention-authoring guide.

Planned or missing work belongs in `docs/todo.md`, not in the manual.

### `docs/implementation_design.md`

Audience:

- Software engineers.
- AI coding agents.
- Technical maintainers.

Purpose:

- File-by-file implementation guide.
- Class, field, function, and variable-level explanation.
- Current schemas and output contracts.
- Known technical limitations.

This is the primary code-reading guide.

### `docs/semantic_ontology.md`

Audience:

- Software engineers.
- AI coding agents.
- Advanced Convention authors.
- LLM-assisted authoring tooling.

Purpose:

- Define the formal bridge-domain vocabulary shared by Conventions and engine code.
- Specify executable expectations for transfers, agreed suits, forcing status, competitive state, keycard context, bidding plans, and relay machinery.
- Prevent portable Conventions from depending on arbitrary private prose.

### `docs/bridge_system_language_roadmap.md`

Audience:

- Product owner.
- Software engineers.
- AI coding agents.
- Future GUI and compiler implementers.

Purpose:

- Define the roadmap from direct YAML authoring toward Bridge System Language, strict IR, and GUI authoring.
- Clarify that BSL is a formal authoring language, while the engine executes validated IR.
- Preserve the design policy that forms, BSL, and IR/YAML are different authoring surfaces for different users and tasks.

### `docs/ir_language_spec.md`

Audience:

- Software engineers.
- AI coding agents.
- Advanced Convention authors.
- Future BSL and GUI compiler implementers.

Purpose:

- Define the current YAML Intermediate Representation as a language.
- Specify Convention Set, Convention, Call Specification, Protocol Frame, Bidding Plan, Call Selection Policy, Named Evaluator, and Relay Automaton syntax.
- Explain how visible context, semantic requirements, plans, effects, and generated system notes relate.
- Distinguish what is executable now from target language features.

### `docs/meow_2over1_benchmark.md`

Audience:

- Product owner.
- Engineers.
- AI coding agents.
- System authors.

Purpose:

- Define Meow Li's 2/1 agreements as the first practical benchmark Convention Set.
- Record current implementation slice, assumptions, and clarification points before full benchmark completion.
- Drive tests for notrump methods, major raises, game/slam judgment, RKCB, plans, and pair-hand auction simulation.

### `docs/todo.md`

Audience:

- Product owner.
- Engineers.
- AI agents.

Purpose:

- Future ideas.
- Open problems.
- User notes that should not be lost in chat history.

When the user says to put something in the TODO list, update this file.

## Documentation Authority Order

When documents conflict, use this order:

1. Current code and tests.
2. `docs/semantic_ontology.md` for formal bridge-domain vocabulary.
3. `docs/ir_language_spec.md` for the executable YAML/IR language.
4. `docs/bridge_system_language_roadmap.md` for authoring-language and GUI decisions.
5. `docs/meow_2over1_benchmark.md` for the first practical benchmark Convention Set.
6. `docs/implementation_design.md` for technical implementation.
7. `docs/documentation_system.md` for documentation organization.
8. `docs/product_description.md` for product framing.
9. `docs/user_manual.md` for user-facing behavior and examples.
10. `docs/todo.md` for planned but unresolved items.

## Terminology Policy

Use current formal terms:

- **Partner Platform**: the software product.
- **Convention Set**: a complete playable partnership agreement selected by a user.
- **Convention**: a portable bridge agreement module. A foundational 2/1 opening structure is technically a Convention even when the UI calls it a base agreement.
- **Call Specification**: one executable call definition in a context, including applicability, public meaning, selection criteria, and effects.
- **Call Act Type**: the structural role of a call, such as descriptive, directive, inquiry, relay ask, signoff, control showing, keycard asking, or final placement.
- **Protocol Frame**: live auction context created by calls, such as a transfer, 2/1 game force, Lebensohl relay, keycard ask, or relay sequence.
- **Bidding Plan**: a bidder's internal route through multiple possible future calls.
- **Call Selection Policy**: an explicit algorithm that compares candidate calls or candidate plans.
- **Named Evaluator**: a reusable limited calculation for hand, auction, environment, and semantic state.
- **Relay Automaton**: step-based relay machinery for cheapest-step asks, response decoding, shape resolution, and relay breakoffs.
- **Bridge System Language**: the future formal authoring language.
- **Intermediate Representation**: the strict executable object model serialized as YAML in the current prototype.
- **System notes**: human-readable partnership notes generated from structured objects.

Notation terms:

- Use **suit** for the formal call field `C D H S N`.
- Use `N` for notrump.
- Use `P`, `X`, and `R` for pass, double, and redouble.
- Use lowercase `n e s w` for absolute seats.
- Use `1`, `2`, `3`, and `4` for seat number.

File layout terms:

- Convention Sets live under `backend/convention_sets/`.
- Conventions live under `backend/conventions/`.
- Each Convention has a `convention.yaml` metadata file plus one or more YAML files for IR objects.

ID policy:

- Keep object IDs short and stable.
- Put human explanation in `description`, `system_notes`, and structured `meaning`.
- Do not make executable logic depend on prose or on long semantic phrases embedded in IDs.

## Maintenance Policies

1. Any code change must update `docs/implementation_design.md` if structure, behavior, schemas, output, or limitations changed.
2. Any product-level change should update `docs/product_description.md`.
3. Any user workflow or Convention-authoring change should update `docs/user_manual.md`.
4. Any semantic vocabulary change should update `docs/semantic_ontology.md`.
5. Any IR/YAML language change should update `docs/ir_language_spec.md`.
6. Any BSL, GUI-authoring, compiler, or IR-roadmap change should update `docs/bridge_system_language_roadmap.md`.
7. Any benchmark-system change should update `docs/meow_2over1_benchmark.md`.
8. Any new open question, future feature, or deferred idea should update `docs/todo.md`.
9. Any new design instruction from the user must be reflected in the appropriate active documents in the same checkpoint.
10. Route new design information by audience: product framing to `product_description.md`, user-facing workflows to `user_manual.md`, technical behavior to `implementation_design.md`, semantic vocabulary to `semantic_ontology.md`, IR syntax to `ir_language_spec.md`, benchmark agreements to `meow_2over1_benchmark.md`, and planned/deferred work to `todo.md`.
11. Any change to documentation organization should update this file.
12. For each platform version update, review all active Markdown documents and update platform version metadata when needed.
13. Do not regenerate PDFs during releases unless the user separately asks for PDFs.
14. The platform version number changes only when the user explicitly says to make or release a new version.
15. When the user says to make or release a new version, update platform version metadata, review docs, run tests, commit, and push to the configured GitHub `Partner` project when GitHub access is available.

## Fresh-Start Recovery Path

A new AI agent or engineer should read in this order:

1. `docs/documentation_system.md`
2. `docs/product_description.md`
3. `docs/user_manual.md`
4. `docs/semantic_ontology.md`
5. `docs/ir_language_spec.md`
6. `docs/bridge_system_language_roadmap.md`
7. `docs/meow_2over1_benchmark.md`
8. `docs/implementation_design.md`
9. `docs/todo.md`
10. Relevant code files referenced by `implementation_design.md`

After reading those files, the agent should understand the product, object model, notation, stateless execution approach, explanation layers, authoring roadmap, implemented behavior, and open work.
