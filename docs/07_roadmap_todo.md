# Roadmap And TODO

Platform Version: 0.0.7
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

This document holds future work and open design questions. User-facing guides should describe current behavior, not unfinished work.

## Product Roadmap

1. Build a web UI for Partnership Profile selection, hand input, auction stepping, explanations, and system-note generation.
2. Add a deal workspace for random deals, manual hand entry, PBN import, and bidding practice.
3. Add saved profiles, import/export, sharing, copying, and forking.
4. Add LLM-assisted Gadget drafting from natural-language system notes. AI-generated files must be drafts until validated, tested, edited, and approved.
5. Add ACBL alert analysis with versioned regulation data. For now, explicit `alertable` fields remain in Call Specifications.
6. Add shared test pools for training and profile comparison.
7. Build a tournament/inter-user platform on top of the execution engine.

## Engine Roadmap

1. Add schema validation for state records and runtime objects.
2. Expand `StateView` conflict diagnostics for contradictory ranges and values.
3. Expand relative-call support: cheapest bid, jump, new suit, step responses after interference, DOPI/ROPI, Kickback, and relay systems.
4. Make Relay Automata executable for symmetric relay and similar methods.
5. Expand Frames beyond current transfer/keycard slices into general game-force, Lebensohl, control-bidding, and relay contexts.
6. Expand Private Routes with richer branching, route-vs-route comparison, memory expiry, and serialized deal/session IDs.
7. Add projected effects to explanations so users can inspect what the selected call will add to state.
8. Add central legal-call constraints to reusable Gadgets.
9. Add custom evaluator libraries for suit quality, losing trick count, controls, rebid ease, playing strength, and vulnerability style.
10. Add deterministic random-source support for randomized policies.

## Meow 2/1 Benchmark Roadmap

1. Complete minor continuations after inverted and Crisscross raises.
2. Complete 2N structure: Puppet Stayman, transfers, minor-suit Stayman, and follow-ups.
3. Complete Puppet Stayman over 1N and 2N.
4. Add Smolen and Garbage Stayman.
5. Add full Jacoby 2N opener continuations.
6. Add splinters.
7. Expand forcing 1N continuations.
8. Expand 2-way NMF/XYZ trees.
9. Expand slam judgment, control bidding, queen asks, signoffs, and final placement.
10. Add competitive auctions.

## Research Benchmarks

Use real systems to pressure-test expressiveness:

- mainstream 2/1,
- Precision,
- Polish Club,
- Washington Standard,
- Kai-Isaac-Quan Strong Diamond,
- KK or symmetric relay systems.

The goal is not to hard-code those systems. The goal is to make sure the runtime object model, BSL, Frames, Private Routes, Policy Functions, and relative-call machinery can express them.

## Design Principles

1. Public meaning and internal origin are separate.
2. A selected call should identify its producing Gadget and Call Specification.
3. Judgmental choices belong in Policy Functions.
4. Multi-step private motivation belongs in Private Routes.
5. Public auction context belongs in Frames and state records.
6. Broad bridge methods and small bridge tools are both Gadgets.
7. Do not add one-off engine fields for every new bridge idea.
8. Do not encode long dynamic auctions as giant enumerations when state, Frames, relative calls, or policy functions can express the structure.
9. The profile author may define profile-specific state fields. A global shared vocabulary can be added later, but should not block custom systems now.
10. Private route memory is seat-owned.
11. Release-version changes happen only when Meow Li explicitly asks for a new version.
