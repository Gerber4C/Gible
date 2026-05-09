# Partner

A bridge bot that plays your bridge agreements.

Current release: `0.0.8`

This checkpoint includes:

- compact bridge auction and hand parsing,
- directory-based Gadgets,
- an executable Meow 2/1 benchmark Partnership Profile,
- self-contained Partnership Profile directories under `backend/partnership_profiles/`,
- class-authored Python BSL source files for agreement objects,
- restricted Python Policy Functions for whole-pool candidate selection,
- reusable Frames and Private Routes for public context and same-seat route memory,
- Python Named Evaluators for reusable bridge calculations,
- a local HTTP backend for browser clients,
- a React browser workspace prototype for editing profiles and trying auctions,
- basic auction legality filtering and same-call ambiguity diagnostics,
- full-auction partnership simulation tests with automatic opponent passes,
- fixture-driven backend tests with a human-readable companion,
- formal Markdown system-note generation.

Documentation starts at:

```text
docs/00_documentation_map.md
```

Frontend engineering details are in:

```text
docs/07_frontend_architecture.md
```

Run the local browser workspace:

```bat
run_local.cmd
```

Then open:

```text
http://127.0.0.1:5173
```
