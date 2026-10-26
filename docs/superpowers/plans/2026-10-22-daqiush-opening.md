# Daqiush opening implementation plan

**Goal:** Execute the confirmed Daqiush 1NT opening slice and expose reusable
honor-quality evidence without treating missing continuations as Pass.

**Architecture:** Generic hand evidence belongs in the engine and is available
through BridgeContext. Daqiush eligibility and adjustable numerical boundaries
belong in its BSL gadget. Existing profiles retain their fallback behavior;
this incomplete profile opts into blocking when no authored call matches.

**Tech stack:** Python, Python-BSL, unittest; existing web profile discovery.

The user explicitly requested implementation and approved these initial values:
14 HCP upgrades require K-R >= 15; 17 HCP with a five-card major requires
K-R < 17; 5M4m22 requires delta <= -1.5; 5M4m31 requires delta <= -0.5.
The preceding discussion and docs/13 and docs/14 are the approved design input.
No new interpretation of unresolved Stayman/slam branches is included.

## Chunk 1: Evidence and executable opening

- [x] Add failing tests for generic honor counts, per-suit Q/J deductions,
  preservation of HCP/K-R and actor-only BridgeContext access.
- [x] Add engine/honor_quality.py and BridgeContext properties. The named
  deduction model reports raw HCP minus doubleton Q=1.5/J=1 and unsupported
  Q/J=0.5 in suits of length >=3. It is not an extra K-R adjustment.
- [x] Add failing profile tests using all A–M labels, boundary comparisons,
  invalid shapes/singletons, genuine selection, replay and hidden-hand isolation.
- [x] Add partnership_profiles/daqiush_2over1/profile.bsl.py and a 1NT gadget.
  Its opening assessment returns eligibility, reasons and evidence; no hand
  identities are hardcoded. Store the four thresholds in the gadget source.
- [x] Add opt-in missing-call behavior `block` across model, BSL metadata,
  loader and selector, with tests for unchanged legacy fallback and simulation.
- [x] Verify new tests, existing quality/information-boundary/axiom/infrastructure
  regression tests; identify pre-existing Meow fixture failures separately.
- [x] Update implementation status, usage, approved thresholds and limitations.

Unknown alternative openings and response-selection agreements remain absent.
The profile label and documentation explicitly identify the opening-only slice.
Preserve all earlier uncommitted work; do not deploy or commit unrelated changes.
