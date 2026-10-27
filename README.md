# Gible

A bridge bot that plays your bridge agreements.

Current release: `0.0.8`

## Product direction

The long-term goal is a platform for user-defined bidding agreements, practice
between human/robot partnerships using different profiles, simulation-assisted
late-auction decisions, and comparison of alternative agreements.

The owner's goals and technical assessment are recorded in English in
[Product Vision](docs/12_product_vision.md). The local-only privacy commitment is
still a product decision; keeping local execution possible is the recommended
architecture. Cloud storage and execution should be optional.

An information-safe local contract-analysis baseline now samples unseen hands
from authored public promises and reports double-dummy completion rates for
explicitly entered target contracts. It is a review tool, not an automatic
auction continuation or a PASS-versus-keycard decision. Meow 2/1
completion remains paused. Launch a usable bidding-practice subset at
`gible.hogetsu.uk` after that bounded baseline, then add the remaining features
through updates. Natural-language system translation with a locally deployable
LLM is an explicit long-term goal. See the
[prioritized roadmap and first-release gate](docs/08_roadmap_todo.md).

The [Gible migration guide](docs/17_gible_migration.md) records the new fork,
local launch names, and the planned Fly.io/Cloudflare site address.

The selected first-release reference profile is **Daqiush 2/1**, now the default
in the browser. Its [opening preview](docs/13_daqiush_2over1.md) uses the
approved K-R/shape criteria, and the first South African Texas response and
opener reply are executable. Exactly-five-card major hands with at most three
cards in the other major, and the approved six-card slam-interest hands, now
start Jacoby transfers. Opener's ordinary accepts and eight superaccepts are
available; the approved slam-interest hands ask keycards immediately after a
superaccept. Six Jacoby splinter auctions can also be replayed:
the jump immediately agrees the major, and opener's adjusted-strength reply is
available. Automatic splinter initiation and later slam continuations remain
incomplete; unsupported branches stop with a diagnostic.

On the Table page, choose **Opening training** or **Opening + response**,
enter the target calls, choose a fixed opener, either partnership, or Random,
and click **Generate matching deal**. North or South is the default. The
generator deals all 52 cards and accepts a deal only when
the selected profile actually chooses the requested opening and response.
An optional numeric seed reproduces a result. A failed search reports its
attempt limit; it does not change the requested calls. Restart an already
running local backend after updating the source to load this endpoint.

For batch testing, the [block-point scanner](docs/18_block_scout.md) can filter
deals, oversample rare high-HCP partnerships, and save reproducible blocked
auctions for later system review.

## Current checkpoint

This checkpoint includes:

- compact bridge auction and hand parsing,
- directory-based Gadgets,
- an executable Meow 2/1 benchmark Partnership Profile,
- self-contained Partnership Profile directories under `backend/partnership_profiles/`,
- class-authored Python BSL source files for agreement objects,
- restricted Python Policy Functions for whole-pool candidate selection,
- mandatory Axioms above Policy, Kaplan–Rubens quality assessment, and explicit blocked-auction diagnostics,
- reusable Frames and Private Routes for public context and same-seat route memory,
- Python Named Evaluators for reusable bridge calculations,
- a local HTTP backend for browser clients,
- a React browser workspace prototype for editing profiles and trying auctions,
- basic auction legality filtering and same-call ambiguity diagnostics,
- full-auction partnership simulation tests with automatic opponent passes,
- fixture-driven backend tests with a human-readable companion,
- formal Markdown system-note generation.

Documentation starts at:

The Axiom authoring and configuration guide is [docs/11_axioms.md](docs/11_axioms.md).

```text
docs/00_documentation_map.md
```

Frontend engineering details are in:

```text
docs/07_frontend_architecture.md
```

## Run locally

Requirements:

- Python 3.10 or newer.
- Node.js 18 or newer.
- A modern browser with access to `https://esm.sh`, which supplies React.

The application uses Python's standard library and Node's built-in server APIs;
`pip install` and `npm install` are not required to launch it. Backend fixture
tests additionally require PyYAML (`python -m pip install PyYAML`).

The optional **Contract analysis** panel and Daqiush's sampled minor-slam
decisions need a double-dummy solver. For local
Windows use, create a project virtual environment and install the pinned
`endplay` wheel, which bundles DDS:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install endplay==0.5.12
```

`gible.cmd` detects `.venv` automatically. The core Table and training
features still launch without this package; solver-dependent bidding decisions
then block with a diagnostic. On Linux, the adapter can also use the official `dds3`
package built from the [DDS repository](https://github.com/dds-bridge/dds)
at commit `c1dd5e03504f072d74a2c557cd15e43d7573fde6`.

On Windows, double-click `gible.cmd`, or run from PowerShell:

```powershell
.\gible.cmd
```

On macOS/Linux, run from the repository directory:

```sh
python3 gible.py
```

The launcher checks the runtimes, starts the backend on `127.0.0.1:8765` and
frontend on `127.0.0.1:5173`, waits for readiness, and opens the browser.
Keep the terminal open; press **Enter** or **Ctrl+C** to stop services started
by that launcher. Existing Gible servers are reused and are not stopped
when a second launcher exits. Other applications occupying these ports cause
an actionable error instead of being stopped. Reused servers may belong to
another checkout; stop the original launcher first when switching checkouts.

On Windows, `kill.cmd` stops recognized Gible frontend/backend processes on
ports 5173/8765. It leaves unrelated applications using those ports alone.
Run `restart.cmd` to stop the old Gible services and then launch `gible.cmd`:

```powershell
.\kill.cmd
.\restart.cmd
```

Use `kill.cmd -DryRun` to list the processes it would stop.

Check the environment without starting services:

```bat
gible.cmd --check
```

Use `--no-browser` to start without opening a browser. On macOS/Linux, pass
the same options to `python3 gible.py`.

Windows Python discovery checks `GIBLE_PYTHON`, then `PARTNER_PYTHON` for older
setups, then repository `.venv`/`venv`,
then `py -3`, `python`, and `python3`. Node is located through `PATH` and common
Windows installation directories. If necessary, set executable paths (without
command-line arguments) before launching:

```powershell
$env:GIBLE_PYTHON = 'C:\path to Python\python.exe'
$env:GIBLE_NODE = 'C:\path to Node\node.exe'
.\gible.cmd
```

On macOS/Linux, choose Python directly when invoking the launcher;
`GIBLE_NODE` also works there. The older `run_local.cmd`, `run_local.py`,
`PARTNER_PYTHON`, and `PARTNER_NODE` names remain compatible. If an environment check fails, install the
reported runtime and reopen the terminal. Runtimes are not downloaded automatically.

The workspace URL is:

```text
http://127.0.0.1:5173
```
