# Gible Rename Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rename Partner to Gible across local product identity, repository identity, and planned website address while keeping bridge vocabulary and existing user setups intact.

**Architecture:** Change literal product branding and launch detection only where the string denotes the application. Preserve old launch and environment interfaces as aliases. Treat remote GitHub and public DNS/hosting migration as separate verified operations, gated by authenticated access and secure deployment prerequisites.

**Tech Stack:** Python standard-library launcher and HTTP server, React/Vite frontend, Git/GitHub, Windows CMD, Markdown documentation.

**Approved design:** [Gible rename design](../specs/2026-10-23-gible-rename-design.md).

---

## Chunk 1: Local name and compatibility

### Task 1: Test the new local name

**Files:** `tests/test_launcher.py`, `frontend/tests/table.browser.cjs`.

- [ ] Add assertions for `gible.cmd --check`, `python gible.py --check`, the Gible page title and sidebar brand, and `GIBLE_PYTHON` / `GIBLE_NODE` precedence over legacy aliases.
- [ ] Add a targeted launcher test that recognizes the old `PartnerLocalHTTP` backend signature and old HTML title, and leaves those processes running when reused.
- [ ] Run `python -m unittest discover -s tests -v` and the browser check; confirm the new assertions fail for the expected reason.

### Task 2: Rename visible product and package metadata

**Files:** `frontend/index.html`, `frontend/src/App.js`, `frontend/src/api/partnerApi.js`, `frontend/package.json`, `frontend/server.mjs`, `backend/server.py`, `run_local.py`.

- [ ] Change the title, sidebar mark/heading, product error messages, package name, and server product header to Gible. Keep partnership domain language.
- [ ] Teach the launcher to recognize both old and new local response signatures during transition.
- [ ] Run frontend unit/browser and launcher tests; verify the Gible branding.

### Task 3: Update launchers with compatibility aliases

**Files:** `run_local.py`, `run_local.cmd`, new `gible.cmd`, new `gible.py`, `tests/test_launcher.py`.

- [ ] Use `GIBLE_NODE` before `PARTNER_NODE` in Python discovery, and `GIBLE_PYTHON` before `PARTNER_PYTHON` in CMD discovery. Preserve old variable behavior.
- [ ] Add `gible.cmd` (Windows) and `gible.py` (all platforms) as preferred entrypoints; keep both `run_local` entrypoints working.
- [ ] Do not add a frontend-port promise; local ports remain 8765/5173.
- [ ] Verify `--check` from a different working directory and a path with spaces on both new and old entrypoints.

### Task 4: Update docs without rewriting bridge terminology

**Files:** `README.md`, `frontend/README.md`, `docs/00_documentation_map.md`, `docs/01_product_overview.md`, `docs/02_user_guide.md`, `docs/07_frontend_architecture.md`, `docs/08_roadmap_todo.md`, `docs/12_product_vision.md`, and any other product-brand occurrence found by targeted search.

- [ ] Replace product-brand Partner and old planned hostname with Gible and `gible.hogetsu.uk`; preserve historic context, system names, and bridge terms.
- [ ] Document preferred Gible startup command, legacy aliases, and secure public deployment prerequisites.
- [ ] Search remaining literals and review each manually before changing.

### Task 5: Verify local migration

**Files:** no new files unless a regression is found.

- [ ] Run launcher, frontend unit, frontend browser, and relevant backend tests.
- [ ] Smoke-check backend and frontend responses. Do not stop an existing user-owned server merely to refresh the page; if the old process is still running, explain restart.
- [ ] Review `git diff --check` and the exact diff; preserve unrelated simulation changes.

## Chunk 2: External and workspace identity

### Task 6: GitHub repository

**Files:** local Git `origin` configuration only.

- [ ] Check for authenticated GitHub management access. Rename `profthecopyright/Partner` to `profthecopyright/Gible` if available.
- [ ] Set `origin` to the new URL only after the remote rename succeeds; verify `git ls-remote origin`.
- [ ] If account access is absent, give exact web UI steps and leave `origin` at the valid old URL.

### Task 7: Public website prerequisites and cutover

**Files:** `frontend/src/api/partnerApi.js`, `frontend/server.mjs`, `backend/server.py`, deployment-specific configuration/tests, hosting/DNS configuration.

- [ ] Verify whether an existing `partner.hogetsu.uk` deployment exists and identify its hosting/DNS provider.
- [ ] Before public cutover, implement a production API route (same-origin proxy or configurable HTTPS API URL) and test it from the deployed hostname.
- [ ] Decide whether each profile is public or private; add access controls or remove profile listing, source read, write, and delete endpoints for private profiles. Test that an anonymous remote request cannot read or mutate private systems.
- [ ] Configure `gible.hogetsu.uk`, verify TLS and end-to-end use from a remote browser, then redirect the old hostname when supported.
- [ ] If deployment infrastructure, access decision, or credentials are absent, leave the public site untouched and report the exact remaining operator steps; a documentation rename alone does not satisfy the public-site acceptance criterion.

### Task 8: Local checkout directory

**Files:** checkout directory and Codex project registration.

- [ ] After stopping processes rooted at the old path, verify the resolved destination `D:\A0_bridge\BridgeSoftware\test\Gible` is absent and inside the intended parent.
- [ ] Move the checkout only when the Codex project can be reattached to the new path; otherwise provide the safe manual migration steps and retain the working checkout.
- [ ] Re-run launcher check from the final path and confirm Git worktree/history intact.
