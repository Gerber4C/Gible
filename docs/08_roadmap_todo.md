# Roadmap And TODO

Platform Version: 0.0.8
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

This document holds future work and open design questions. User-facing guides should describe current behavior, not unfinished work.

## Product Roadmap

1. Build the web UI into a durable Partnership Profile workspace for editing, file management, hand input, auction stepping, explanations, and system-note generation.
2. Add a deal workspace for random deals, manual hand entry, PBN import, and bidding practice.
3. Add saved profiles, import/export, sharing, copying, and forking.
4. Add LLM-assisted Gadget drafting from natural-language system notes. AI-generated files must be drafts until validated, tested, edited, and approved.
5. Add ACBL alert analysis with versioned regulation data. For now, explicit `alertable` fields remain in Call Specifications.
6. Add shared test pools for training and profile comparison.
7. Build a tournament/inter-user platform on top of the execution engine.

## Frontend Roadmap

1. Add backend-backed BSL and Policy Function validation so the code editor can show real compile errors.
2. Improve guide-mode editing for class-authored `call.meaning`, `call.effect(...)`, `self.frame(...)`, `self.route(...)`, and `self.evaluator(...)` blocks.
3. Add safer structured editors for Policy Function registration and source-block movement.
4. Add profile-level system-note preview and export.
5. Add deal import and hand-dealing controls.
6. Add a visual auction explainer that shows public meaning, internal origin, state changes, active Frames, and Private Routes.
7. Add comparison view for multiple Partnership Profiles bidding the same deal.
8. Add browser tests for file CRUD, save/discard behavior, code editor behavior, and table simulation.
9. Move from no-build React to a normal frontend build pipeline when dependency management is stable.
10. Prepare the UI structure for later desktop and mobile shells.

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

1. Refactor the 1N response layer according to `docs/09_meow_1nt_technical_design.md`: split terminal, major-search, transfer, two-suiter, and slam route policies.
2. Refactor the non-1N opening families according to `docs/10_meow_opening_technical_design.md`: split 1m response/rebid, 2C rebid, checkback/XYZ, and game-try route policies.
3. Complete Regular Stayman: opener `2H/2S`, garbage Stayman, Smolen, invite/game continuations, and slam continuations after a fit.
4. Complete transfer continuations after 1N: weak signoffs, invites, game placement, second suits, superaccept follow-ups, and slam routes.
5. Complete minor-transfer continuations and minor-slam routing.
6. Complete minor continuations after inverted and Crisscross raises.
7. Complete 2N structure: transfers, minor-suit Stayman, and follow-ups beyond the current Puppet dialogue.
8. Extend Puppet Stayman beyond current game-placement branches, including slam continuations and strong-2C notrump adapter reuse.
9. Add full Jacoby 2N opener continuations and splinters.
10. Expand forcing 1N continuations, 2-way NMF/XYZ trees, slam judgment, control bidding, queen asks, signoffs, final placement, and competitive auctions.

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
