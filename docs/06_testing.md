# Testing

Platform Version: 0.0.8
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

Run backend tests from:

```text
backend/
```

Command:

```powershell
C:\Users\paw_l\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest tests.test_fixture_cases -q
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

- 159 curated single-call bidding cases.
- 27 full-auction simulations.
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

1. Do not hide test cases inside implementation code.
2. Put user-visible test examples in fixture files.
3. Keep expected results bridge-sensible.
4. Prefer full-auction tests when the agreement is about a multi-call route.
5. For every new Gadget branch, add at least one direct fixture.
6. For major profile changes, add pair-hand full-auction coverage.
7. If a hard fallback pass is expected, assert the fallback diagnostic. If pass is an explicit Call Specification, expect no fallback diagnostic.
8. Do not let fixture loading silently skip cases. The loader strips UTF-8 BOM before YAML parsing.
9. Do not inflate coverage with repetitive generated cases. A small set of bridge-distinct judgment cases is more valuable than many mechanically similar hands.

## Frontend Verification

Frontend syntax and browser verification steps live in `docs/07_frontend_architecture.md`. Keep frontend-specific checks there so this document remains focused on backend fixtures and bridge behavior tests.
