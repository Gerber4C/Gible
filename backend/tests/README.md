# Backend Test Workflow

Run the maintained backend regression suite from `backend/`:

```powershell
python -m pytest -q tests
```

The legacy Meow 2/1 fixture suite and its generated companion were removed
because their historical system expectations were no longer maintained.
Profile-specific maintained coverage belongs in the relevant `test_*.py` file
under `backend/tests/`.

## Run Tests

From the project root:

```text
$env:PYTHONPATH='backend'; C:\Users\paw_l\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe -m unittest discover backend\tests
```

