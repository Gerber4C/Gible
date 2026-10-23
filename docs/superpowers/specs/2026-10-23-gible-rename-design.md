# Gible rename design

## Goal and scope

Rename the product and project from Partner to Gible, including the local app,
GitHub repository, and intended public hostname `gible.hogetsu.uk`. Preserve
bridge terms such as "partner", "partnership", and "Partnership Profile", and
preserve system names such as Daqiush 2/1 and Meow 2/1.

## Migration sequence

1. Update visible branding, package metadata, documentation, and launcher
   diagnostics. Prefer `GIBLE_PYTHON`, `GIBLE_NODE`, and `GIBLE_FRONTEND_PORT`;
   retain the current `PARTNER_*` variables as compatibility aliases for existing
   local setups. Give the launcher the Gible name while keeping the existing
   entrypoint as a compatibility alias. Ensure it recognizes an already running
   old server so an upgrade does not report a misleading port conflict.
2. Check launcher, backend, frontend, and browser tests. Do not rename bridge
   domain concepts, profile IDs, API routes, or private `partner_hand` data
   solely because they contain the word "partner".
3. Rename the GitHub repository `profthecopyright/Partner` to
   `profthecopyright/Gible` through an authenticated management surface, then
   update and verify the local `origin` URL. Preserve the existing Git history.
4. Point the public website at `gible.hogetsu.uk` through the actual hosting and
   DNS provider, verify HTTPS and application behavior, then redirect the old
   hostname if the provider permits. Do not claim the public move is complete
   until both DNS and hosting are verified.

## Boundaries and risks

The checkout currently contains extensive uncommitted simulation work. Rename
edits must preserve it and avoid a broad replacement of every occurrence of
"partner". Existing launchers and environment variables need compatibility
while the new name becomes primary. GitHub and DNS changes depend on account
access; local code and documentation can be prepared independently.

## Acceptance

- UI title, app heading, and general product docs say Gible.
- Fresh launch uses the Gible command and `GIBLE_*` configuration; existing
  `run_local` and `PARTNER_*` flows still work.
- Tests and smoke checks pass without changing the selected Daqiush profile.
- `origin` resolves to the renamed GitHub repository after its management-side
  rename.
- The public site is reachable over HTTPS at `gible.hogetsu.uk`, with the old
  address redirected or explicitly documented if redirect control is absent.
