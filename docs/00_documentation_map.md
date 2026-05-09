# Partner Documentation Map

Platform Version: 0.0.8
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

This is the first document to read when entering the Partner repository. It explains which document owns which layer of truth.

Markdown is the editable source of truth. PDF files are not maintained for intermediate edits. When Meow Li explicitly says "release a new version" or "make a new version", update platform version references consistently, run the checks, and publish the current repository state to GitHub. Otherwise keep the version number unchanged.

When Meow Li gives new design information, update the document that owns that topic in the same checkpoint as the code or test change. Do not let important design decisions live only in chat history.

## Document Set

- `docs/00_documentation_map.md`
  - Map of the documentation system.
  - Versioning and documentation-maintenance rules.

- `docs/01_product_overview.md`
  - Highest-level product description.
  - Written for bridge players, teachers, organizers, users, and possible investors.
  - No programming background assumed beyond ordinary computer use.

- `docs/02_user_guide.md`
  - Beginner guide for running the platform.
  - Practical guide for advanced users who want to author Gadgets and Partnership Profiles.
  - Uses examples, but keeps unfinished engineering work out of the manual.

- `docs/03_engine_architecture.md`
  - Software engineering implementation guide.
  - Explains backend files, runtime flow, core classes, context/state, candidate generation, policy functions, frames, private routes, simulation, local HTTP API, and system-note generation.

- `docs/04_bsl_and_runtime_objects.md`
  - Formal authoring and runtime object model.
  - Defines Python-shaped BSL, Call Specifications, Frames, Private Routes, Evaluators, and policy functions.
  - The engine has a Runtime Object Model; there is no separate user-facing IR language in the current implementation.

- `docs/05_meow_2over1_benchmark.md`
  - Current Meow 2/1 benchmark Partnership Profile.
  - Describes implemented Gadgets, policy functions, and the current bridge assumptions.

- `docs/06_testing.md`
  - Test workflow, fixture layout, full-auction simulation, and human-readable fixture companion rules.

- `docs/07_frontend_architecture.md`
  - Frontend engineering guide.
  - Explains the local browser workspace, React module layout, editor modes, file tree CRUD, bridge table, API client, styling, diagnostics, and frontend verification.

- `docs/08_roadmap_todo.md`
  - Product roadmap, engineering backlog, and design questions.
  - Anything not yet implemented belongs here, not in the user guide.

- `docs/09_meow_1nt_technical_design.md`
  - Technical system note and refactor audit for the Meow 2/1 1N response structure.
  - Maps each major 1N branch to Gadget, Policy Function, Frame, Private Route, context evidence, and later connections.

- `docs/10_meow_opening_technical_design.md`
  - Technical system note and refactor audit for Meow 2/1 opening families beyond 1N.
  - Covers root opening choice, 1M, 1m, 2C, 2N, preempts, default behavior, context evidence, and continuation connections.

The generated fixture companion is separate:

- `backend/partnership_profiles/meow_2over1/tests/test_cases.md`
  - Human-readable translation of YAML fixtures.
  - Must be updated whenever fixture YAML changes.

## Maintenance Rules

1. Keep documentation current with code in the same checkpoint.
2. Keep product-facing documents free of internal churn.
3. Keep user-facing manuals focused on what the user can do now.
4. Keep backend implementation details in `03_engine_architecture.md` and `04_bsl_and_runtime_objects.md`.
5. Keep frontend implementation details in `07_frontend_architecture.md`.
6. Keep future work in `08_roadmap_todo.md`.
7. Avoid historical compatibility notes. State the current correct term and behavior.
8. Use current terms:
   - Partner Platform
   - Partnership Profile
   - Gadget
   - Call Specification
   - Policy Function
   - Frame
   - Private Route
   - Named Evaluator
   - Runtime Object Model
9. Avoid formal use of ambiguous terms such as "system", "convention", "rule", "protocol", and "IR" unless bridge English or code compatibility requires them.
10. In bridge terminology, use suit, not strain.
11. The input auction and hand notation are compact strings.
12. PDF generation is not part of normal checkpoints.
