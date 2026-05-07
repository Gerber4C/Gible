# Testing

Platform Version: 0.0.7
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
backend/tests/cases/bidding.yaml
backend/tests/cases/full_auctions.yaml
backend/tests/cases/hands.yaml
backend/tests/cases/legality.yaml
backend/tests/cases/matcher.yaml
```

Current fixture coverage:

- 128 single-call bidding cases.
- 11 full-auction simulations.
- 3 valid hand parser cases.
- 7 invalid hand parser cases.
- 5 legality cases.
- 1 matcher case.

## Human-Readable Companion

`backend/tests/test_cases.md` is the readable translation of the YAML fixtures. It uses suit symbols for hand readability.

When a fixture changes, update `backend/tests/test_cases.md` in the same checkpoint.

## What The Tests Cover

Single-call bidding fixtures check:

- selected call,
- selected Gadget and Call Specification,
- public meaning fields,
- selected Policy Function,
- compared candidate calls,
- selected criteria,
- diagnostics,
- recovered state,
- active Frames,
- Private Routes.

Full-auction fixtures check:

- whole partnership auctions,
- final compact auction string,
- controlled-seat calls,
- absence or presence of diagnostics.

Infrastructure tests check:

- compact auction parsing,
- compact hand parsing,
- BSL loading,
- restricted policy functions,
- same-seat private memory,
- frame obligations,
- relative-call helpers,
- system-note generation,
- absence of structured route-policy declarations in current BSL sources.

## Test Design Rules

1. Do not hide test cases inside implementation code.
2. Put user-visible test examples in fixture files.
3. Keep expected results bridge-sensible.
4. Prefer full-auction tests when the agreement is about a multi-call route.
5. For every new Gadget branch, add at least one direct fixture.
6. For major profile changes, add pair-hand full-auction coverage.
7. If a fallback pass is expected, assert the fallback diagnostic unless a real Call Specification places the contract.
8. Do not let fixture loading silently skip cases. The loader strips UTF-8 BOM before YAML parsing.
