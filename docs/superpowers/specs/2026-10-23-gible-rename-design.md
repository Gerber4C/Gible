# Gible rename design

## Goal and scope

Rename the product and project from Partner to Gible, including the local app,
GitHub repository, and intended public hostname `gible.hogetsu.uk`. Preserve
bridge terms such as "partner", "partnership", and "Partnership Profile", and
preserve system names such as Daqiush 2/1 and Meow 2/1.

## Migration sequence

1. Update visible branding, package metadata, documentation, and launcher
   diagnostics. Prefer `GIBLE_PYTHON` and `GIBLE_NODE`; retain the current
   `PARTNER_*` variables as compatibility aliases for existing local setups.
   Keep the current fixed local ports for now. Give the launcher the Gible name
   while keeping the existing entrypoint as a compatibility alias. Ensure it
   recognizes an already running old server so an upgrade does not report a
   misleading port conflict.
2. Check launcher, backend, frontend, and browser tests. Do not rename bridge
   domain concepts, profile IDs, API routes, or private `partner_hand` data
   solely because they contain the word "partner".
3. Rename the GitHub repository `profthecopyright/Partner` to
   `profthecopyright/Gible` through an authenticated management surface, then
   update and verify the local `origin` URL. Preserve the existing Git history.
4. Rename the planned public hostname in the project documents to
   `gible.hogetsu.uk`. Before pointing public DNS at this app, provide a
   production frontend-to-backend API route and decide which profiles are
   public. Protect private profile listing and source reads, and protect or
   remove unauthenticated profile file write/delete endpoints. Then change the
   hostname in the actual hosting and DNS provider, verify HTTPS and an end-to-
   end remote browser flow, and redirect the old hostname if possible. Do not
   claim the public move is complete until those gates are met.
5. The on-disk checkout directory `Partner` is part of the local migration, but
   move it only after stopping processes rooted there and checking that the
   destination `Gible` is absent. Reattach/update the Codex project workspace
   path afterward. The code and Git repository identity can be updated before
   that final local path cutover.

## Boundaries and risks

The checkout currently contains extensive uncommitted simulation work. Rename
edits must preserve it and avoid a broad replacement of every occurrence of
"partner". Existing launchers and environment variables need compatibility
while the new name becomes primary. GitHub and DNS changes depend on account
access; local code and documentation can be prepared independently. A DNS-only
cutover would leave the current browser calling its own `127.0.0.1` and would
expose unauthenticated profile source reads and editing if the backend were
published. These are deployment prerequisites, not rename substitutions.

## Acceptance

- UI title, app heading, and general product docs say Gible.
- Fresh launch uses the Gible command and `GIBLE_PYTHON` / `GIBLE_NODE`;
  existing `run_local` and `PARTNER_*` flows still work.
- Tests and smoke checks pass without changing the selected Daqiush profile.
- `origin` resolves to the renamed GitHub repository after its management-side
  rename.
- After a secure public deployment is available, the public site is reachable
  over HTTPS at `gible.hogetsu.uk`, with the old address redirected or
  explicitly documented if redirect control is absent.
- The local checkout resides in a `Gible` directory after the running servers
  and Codex project path are migrated safely.
