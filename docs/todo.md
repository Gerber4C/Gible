# TODO

Platform Version: 0.0.6
Author: Meow Li
Copyright: Copyright (c) 2026 Meow Li. All Rights Reserved.


## Product And Architecture

1. Consider implementing Convention execution logic on the client side as well as the server side, so the platform can hint what to bid during training.
2. Add ACBL alert-regulation support. The platform should eventually auto-analyze whether a call is ACBL-alertable. Since ACBL regulations change over time, this needs versioned/current regulation data. For the near term, each Call Specification can include an explicit `alertable` field in its public meaning.
3. Add an LLM-assisted Convention builder. Users should be able to describe a Convention in natural bridge language, have the platform call an LLM to draft the structured Convention file, then inspect, validate, test, edit, and approve it before use.
4. Treat the product as layered modules. Layer 1 is custom Convention Set editing, file sharing, Convention execution, system-note reports, and LLM conversion between notes and structured files. Layer 2 is the tournament/inter-user platform built on top of Layer 1.
5. Expand formal system-note report generation from structured Convention Set and Convention files, including clearer formatting, section ordering, warnings, and export workflows.
6. Add LLM-driven conversion from human-readable system notes to structured Convention Set and Convention files.
7. Add a hand/deal workspace for manual hand entry, random dealing, PBN import, auction stepping, and bidding against a selected system.
8. Add shared test-case pools for training and Convention Set comparison. Users should be able to run the same pool against multiple Convention Sets, compare resulting auctions, inspect explanation traces, and compare final contracts against expert notes or double-dummy references when available.

## Implementation Backlog

1. Build the web user interface.
2. Add account and saved Convention Set support.
3. Add system sharing, import, export, copying, and forking.
4. Expand the basic auction legality helper into full bridge-law validation, including richer diagnostics and UI-facing legal-call lists.
5. Expand double/redouble handling beyond basic legality into conventional meanings, obligations, and competitive-context state.
6. Add client-side training hints.
7. Add automated ACBL alert analysis.
8. Add LLM-assisted Convention drafting from natural-language descriptions.
9. Add custom evaluator plugin interface.
10. Add partner obligations.
11. Add competitive double library.
12. Add PBN import support and deal validation.
13. Design a systematic Convention-file naming scheme. Each Convention should live in its own directory, and the platform should eventually assign or validate unique Convention IDs so imported Conventions do not conflict. Consider including the Convention ID in filenames where useful.
14. Build the next operable milestone: basic 2/1 plus uncontested after-1NT Conventions. This should include a practical 1NT response and continuation library, not only the current heart-transfer sample.
15. Add structured competition among after-1NT routes such as Jacoby transfers, Texas transfers, Smolen, invitational signoffs, and game-forcing auctions. Selection must evaluate hand, auction, environment, and semantic facts through approved algorithms or plugin hooks.
16. Add central derivation of bridge-relative context: our side, their side, opener, responder, overcaller, advancer, seat number, favorable/unfavorable vulnerability, balancing seat, and related equivalences.
17. Replace the current flexible `SemanticFact` trace and lightweight `AuctionStateVariable` list with an ontology-backed `SemanticState` based on `docs/semantic_ontology.md`.
18. Expand semantic conflict and ambiguity diagnostics beyond the first same-call resolver, including incompatible shown ranges, unresolved obligations, and overlapping Call Specifications.
19. Implement formal transfer, relay, forcing, agreed-suit/trump, notrump-focus, competitive-interference, and slam/keycard state. This should support cases such as doubled-transfer retransfer sequences and RKCB versus quantitative `4N` without enumerating every possible auction path.
20. Define and implement the Bridge System Language roadmap. BSL should be a formal authoring language that compiles to validated IR/YAML; it should not replace direct IR/YAML editing for advanced users.
21. Add a compiler and validator pipeline: BSL source to normalized IR, IR schema validation, source-location-aware diagnostics, and executable engine loading.
22. Add GUI authoring surfaces for form editing, BSL editing, and IR/YAML inspection. The GUI should not assume BSL is always easier than IR; it should support the right surface for the task.
23. Rename the target design vocabulary around Convention Set, Convention, Call Specification, Protocol Frame, Bidding Plan, Call Selection Policy, and Relay Automaton while keeping current code paths accurate during migration.
24. Expand the first IR object schemas into validated schemas with clear required fields, type checks, and diagnostics.
25. Extend Call Selection Policies beyond loadable highest-score policies to decision trees, decision tables, scoring evaluators, and Convention Set-level integration policies.
26. Expand executable Bidding Plans beyond the first entry-call, `wait_for_call`, and `make_call` paths. Add plan-vs-plan comparison, role-aware ownership, `select_by_policy`, branch predicates over hand/environment, and stricter generated Call Specification linkage.
27. Expand active Protocol Frames beyond the first transfer-frame and RKCB-frame slices. Add arbitrary stage rules, obligations, interference policy, nested-frame resolution, and frame-aware continuation matching for 2/1 game forces, Lebensohl, keycard, control-bidding, and relay contexts.
28. Make Relay Automata executable for cheapest-step asking, response decoding, shape resolution, breakoffs, and pass/double/redouble relay steps after interference.
29. Expand Named Evaluators beyond expression-type criteria into richer bridge judgment libraries such as balancedness, suit quality, slam interest, rebid ease, vulnerability style, and opening-choice comparison.
30. Add deterministic random-source support for declared randomized bidding policies.
31. Use benchmark Convention Sets to pressure-test the ontology: Washington Standard, Kai-Isaac-Quan Strong Diamond, KK/Symmetric Relay, Precision, Polish Club, and mainstream 2/1.
32. Add a mathematical design note proving expressive completeness for the defined input subset: auction, environment, own hand, derived semantic state, and declared random source.
33. Expand the Meow 2/1 benchmark Convention Set from `docs/meow_2over1_benchmark.md` beyond the current executable slices, including complete minor continuations after inverted/Crisscross raises, full 2-way NMF/XYZ trees, 2N structure, full Stayman/Smolen/Garbage Stayman, Jacoby 2N, splinters, and more realistic judgment.
34. Expand pair-hand auction simulation beyond supplied partnership hands and automatic opponent passes. Add full legality validation, competitive auctions, and stronger completion diagnostics.
35. Promote ontology-backed `effects` into executable engine behavior. First `state_has`/`state_missing` queries, typed auction-state variables, transfer-frame stage movement, RKCB-frame recovery, and simple Bidding Plan candidate generation exist, but full typed effect operations, merge rules, and semantic-state validation are still needed.
36. Expand the limited YAML expression language from `docs/ir_language_spec.md`, including partnership-level variables, auction-derived features, richer typed semantic-state access, random sources, loser count, suit-quality helpers, and stronger schema validation.
37. Expand expression-based benchmark judgments beyond the current minor-transfer and help-suit examples. Add suit fits, game/slam thresholds, route selection among alternatives, and partnership-style-specific evaluators without adding one-off language fields for those calculations.
38. Design the test-pool data model: deal source, auction context, supplied hands, expected or reference auctions, expert comments, double-dummy contract references, scoring context, tags, difficulty, and comparison/report output.
39. Add a Convention Set comparison runner that executes the same test pool across several Convention Sets and reports auction differences, final contracts, diagnostics, public meanings, internal origins, and unresolved auctions.
40. Add central legal-call constraints to semantic reusable Conventions. RKCB now has a first semantic-context implementation, but the engine still needs legality checks and conflict resolution when several Conventions claim the same call.
41. Add compact authoring syntax for common expressions and policy predicates. The current expression tree is acceptable as safe IR, but BSL and GUI editors should let humans write concise bridge predicates that compile into the structured expression form.
42. Expand the slam Convention library beyond the current executable slices: full Gerber continuations, full Kickback/Minorwood/Exclusion response tables, queen asks, signoffs, control-bidding continuations, interference policies, and final-placement rules.
43. Add expert opening-selection primitives as safe evaluator expressions or Named Evaluators. Examples include rebid ease, reverse risk, expected continuation after partner responds in the shortest suit, suit quality, playing strength, and vulnerability/scoring adjustments. These must not be hard-coded into `1M` or `1N` Call Specifications.
44. Define the BSL predicate parser as Python-like source syntax that compiles to whitelisted IR expression trees without executing user Python.
45. Design conflict/merge rules for auction-state variables. Examples include intersecting HCP ranges, reconciling denied suit lengths with later support, replacing old force-status values with stronger ones, and reporting contradictory state origins.
46. Add projected effects to selected-call explanations so training/debug output can show not only current recovered state, but also the state that the selected call would create if made.

## Design Notes To Revisit

1. Public partnership meaning and internal training origin are separate output layers.
2. A selected bid should report which Call Specification and Convention produced it.
3. Judgmental choices should report compared candidate Call Specifications and Bidding Plans, not only the final selected call.
4. Conventions, Call Specifications, Bidding Plans, and Call Selection Policies need author metadata.
5. Human-authored IDs should stay short, with fully qualified origin names generated by the engine.
6. Selection reasoning must be structured and machine-readable. Natural-language display text can be generated from structured criterion results, but it should not be the source of truth.
7. Custom Convention and Call Selection Policy algorithms need a practical plugin interface.
8. LLM-generated Conventions must remain drafts until validated and approved. The structured Convention file is the source of truth, not the natural-language prompt.
9. Keep tournament/inter-user features separated from the system execution engine so the engine remains useful as a standalone authoring, training, and analysis tool.
10. A basic system, such as 2/1, is a user-facing concept. Technically it is just a Convention. Do not add unnecessary backend fields or object types that distinguish "basic system" from other Conventions unless a concrete implementation requirement appears.
11. Call Specification IDs should name what the object does, not generic concepts like `meaning`.
12. Before using any default behavior for an undefined auction, the engine should search all active Conventions globally for matching Call Specifications, Protocol Frames, Bidding Plans, and Call Selection Policies.
13. The ontology is a system-level contract. Convention files, engine code, generated system notes, alert analysis, and LLM-assisted Convention drafting should share the same formal vocabulary.
14. The engine executes validated IR. BSL, natural-language notes, LLM drafts, and GUI forms are authoring layers that must compile or validate before use.
15. A Call Selection Policy is the explicit place for judgmental comparison among alternatives. Do not hide global judgment as priority inside one candidate call.
16. A Bidding Plan is the explicit place for multi-step route motivation. Public meaning should disclose the call agreement, while internal origin may record the private plan and compared alternatives.
17. A Protocol Frame is the explicit place for live auction context. Do not enumerate long dynamic auctions when a frame can carry the state.
18. Relay methods need a Relay Automaton rather than thousands of fixed auction patterns.
19. Convention Set-level policies must be able to integrate and resolve policies shipped by individual Conventions.
