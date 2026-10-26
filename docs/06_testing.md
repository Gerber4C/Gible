# Testing

## Daqiush opening and training slice

From `backend`, run:

```powershell
python -m unittest tests.test_daqiush_opening tests.test_daqiush_texas tests.test_daqiush_splinter tests.test_training_deals tests.test_honor_quality -q
```

Coverage includes all 13 owner-labelled hands (B/D rejected, G accepted),
approved threshold inclusivity, shape exclusions, honor singletons, public
opening meaning, actor-only evidence, missing-branch blocking in selection and
simulation, the separate Q/J HCP-discount model, the first 4C/4D Texas response
and opener reply, the six historical Jacoby splinters with immediate trump
agreement and adjusted opener replies, and seeded exact-call training deals.
Automatic splinter initiation and later slam branches remain drafts. Browser
coverage for generating and replaying an East
opening with a target response is in `frontend/tests/training.browser.py`.

## Axiom checks

The Axiom layer has independent tests in `test_axioms.py`,
`test_axiom_integration.py`, and `test_hand_quality.py`. Run these from
`backend` with `python -m unittest tests.test_axioms tests.test_axiom_integration tests.test_hand_quality -q`.
Browser blocked-auction checks are in `frontend/tests/axioms.browser.cjs`.
See `11_axioms.md` for authoring/configuration. Meow 2/1 case migration is
currently deferred by user decision; its original assertions remain visible
and are not rewritten to hide conflicts with the new constraints.

Platform Version: 0.0.8
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

Run backend tests from:

```text
backend/
```

Command:

```powershell
python -m unittest tests.test_fixture_cases -q
```

## Fixture Files

```text
backend/partnership_profiles/meow_2over1/tests/cases/bidding.yaml
backend/partnership_profiles/meow_2over1/tests/cases/full_auctions.yaml
backend/partnership_profiles/meow_2over1/tests/cases/hands.yaml
backend/partnership_profiles/meow_2over1/tests/cases/legality.yaml
backend/partnership_profiles/meow_2over1/tests/cases/matcher.yaml
```

Current fixture coverage:

- 177 curated single-call bidding cases.
- 29 full-auction simulations.
- 3 valid hand parser cases.
- 7 invalid hand parser cases.
- 5 legality cases.
- 1 matcher case.

## Human-Readable Companion

`backend/partnership_profiles/meow_2over1/tests/test_cases.md` is the readable translation of the YAML fixtures. It uses suit symbols for hand readability.

When a fixture changes, update `backend/partnership_profiles/meow_2over1/tests/test_cases.md` in the same checkpoint.

## What The Tests Cover

Single-call bidding fixtures check:

- selected call,
- selected Gadget and Call Specification,
- public meaning fields,
- selected Policy Function,
- compared candidate calls,
- route/provenance details when a Private Route is selected,
- diagnostics,
- recovered state,
- active Frames,
- Private Routes.

Full-auction fixtures check:

- whole partnership auctions,
- final compact auction string,
- controlled-seat calls,
- absence or presence of diagnostics.

Multi-call agreements should be tested until the route naturally resolves. For opening-family routes, the benchmark target is at least opener's third meaningful turn and responder's third meaningful turn when the route has not already placed a contract. Shorter auctions are acceptable only when the agreement itself ends earlier, such as a direct game placement or a signoff accepted by pass.

Infrastructure tests check:

- compact auction parsing,
- compact hand parsing,
- BSL loading,
- restricted policy functions,
- same-seat private memory,
- frame obligations,
- Puppet dialogue replay and length-specific fit evidence,
- relative-call helpers,
- system-note generation,
- current BSL source shape and policy-function loading.

## Test Design Rules

### Hidden partner-hand regression

Run `python -m unittest tests.test_information_boundary -v` from `backend/`.
These six infrastructure tests cover all four dealer seats, normal bid/simulation
entry points, direct environment injection, replay/candidate conditions, and
explicit rejection of legacy real-partner expressions. Public partner evidence
and unrelated environment settings remain available. The tests first reproduced
the leak before the fix; 77 targeted backend tests pass after the fix (2026-10-22).
The separate Meow benchmark still has its 14 known failing cases and no fixture
expectations were changed for this repair.

### General rules

1. Do not hide test cases inside implementation code.
2. Put user-visible test examples in fixture files.
3. Keep expected results bridge-sensible.
4. Prefer full-auction tests when the agreement is about a multi-call route.
5. For every new Gadget branch, add at least one direct fixture.
6. For major profile changes, add pair-hand full-auction coverage.
7. If a hard fallback pass is expected, assert the fallback diagnostic. If pass is an explicit Call Specification, expect no fallback diagnostic.
8. Do not let fixture loading silently skip cases. The loader strips UTF-8 BOM before YAML parsing.
9. Do not inflate coverage with repetitive generated cases. A small set of bridge-distinct judgment cases is more valuable than many mechanically similar hands.

## Launcher Verification

From the repository root, run `python -m unittest discover -s tests -v`.
These checks cover runtime discovery, invalid runtime overrides, repository
paths containing spaces, startup and reuse, shutdown, and cleanup when a port
is occupied. The integration checks use ports 8765 and 5173 and skip when
those ports are already in use. On Windows, startup is exercised through
`gible.cmd`; on other systems it uses `gible.py`.

## Frontend Verification

Frontend syntax and browser verification steps live in `docs/07_frontend_architecture.md`. Keep frontend-specific checks there so this document remains focused on backend fixtures and bridge behavior tests.
