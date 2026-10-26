# Gible name migration

The application is named **Gible**. Daqiush 2/1 and Meow 2/1 are names of
bidding systems, while "partner", "partnership", and "Partnership Profile" are
bridge concepts; they are not renamed.

## Local launch

- Windows: run `gible.cmd` from the repository, or double-click it.
- macOS/Linux: run `python3 gible.py` from the repository.
- `run_local.cmd`, `run_local.py`, `PARTNER_PYTHON`, and `PARTNER_NODE` remain
  compatibility aliases. Prefer `GIBLE_PYTHON` and `GIBLE_NODE` for new setups.
- The local frontend/backend still use ports 5173/8765. Restart existing
  servers after changing backend code; an older local server is safely reused
  until stopped.

## GitHub fork

The owner-controlled repository is [Gerber4C/Gible](https://github.com/Gerber4C/Gible),
forked from [profthecopyright/Partner](https://github.com/profthecopyright/Partner).
In a checkout, `origin` should point to the Gible fork and `upstream` to the
original. Verify with `git remote -v` and `git ls-remote --heads origin`.

The working checkout contains uncommitted feature work. A fork does not include
those changes automatically. Review and commit that work deliberately before
pushing; the fork's README will retain the old title until a commit containing
the branding edits is pushed.

## Local directory

The checkout is still stored in a directory named `Partner` while this Codex
project and running servers refer to that path. Stop those servers first,
close apps and terminals using this checkout, verify that a sibling `Gible`
directory does not exist, move the checkout from its parent directory, and
update or reattach the Codex project to the new path. Windows will reject the
move while any process keeps the directory open; close this Codex project before
retrying if stopping local servers is insufficient. Do not keep two writable
copies of the checkout as a substitute for a move.

## Public hostname

`gible.hogetsu.uk` is the intended public address. Cloudflare manages DNS for
`hogetsu.uk`, and Fly.io is the chosen application host. The application has not
yet been deployed. First deploy and verify a production-safe Gible application
on its Fly.io address, then attach `gible.hogetsu.uk` and configure its DNS and
TLS. After the site works over HTTPS, redirect `partner.hogetsu.uk` to the new
hostname if the old hostname is active.

For the later cutover, add the hostname to the Fly.io app first and use the DNS
and ownership records that Fly.io gives for that app. Its
[custom-domain guide](https://fly.io/docs/networking/custom-domain/) covers
Cloudflare proxying and certificate checks. There is no Fly app, `fly.toml`, or
Cloudflare record to update in this checkout yet.

The current frontend calls `127.0.0.1:8765`, and the backend exposes profile
source reads and edits without user access control. Before making the app
public, add a production API route and decide which profiles are public versus
private; protect private reads and edits. A DNS-only change would neither fix
the browser API connection nor secure the editor. See the deployment workstream
in [the roadmap](08_roadmap_todo.md).
