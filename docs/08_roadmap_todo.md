# Roadmap And TODO

Platform Version: 0.0.8
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

This document holds future work and open design questions. User-facing guides should describe current behavior, not unfinished work.

## Direction Update — 2026-10-22

The owner's [Product Vision](12_product_vision.md) now governs priorities. The
main product is customizable agreements, mixed-profile human/robot practice,
simulation-assisted later bidding, and experiments comparing agreements. Meow
2/1 is a paused benchmark, not the driver of near-term feature work.

Implemented checkpoint: Daqiush's 1NT opening preview, approved numerical
cutoffs, reusable honor evidence, and explicit blocking of unsupported profile
decisions. A–M all match the owner's final labels. The complete response/slam
practice loop remains part of the release gate below.

Local-only profile confidentiality is still an open product commitment. Preserve
local execution as an architectural option now; do not equate local file storage,
encrypted cloud backup, or the existing browser prototype with a verified privacy
guarantee. The detailed tradeoffs and learning proposal are in the vision document.

## Prioritized Delivery Sequence

These are proposed milestones, not implemented features. Each substantial stage
needs its own bounded implementation design; the vision is not a mandate to build
all stages at once.

## First Website Release — Required Checkpoint

Owner instruction (2026-10-22): deploy a basically usable subset to
`gible.hogetsu.uk`, then continue development through updates. Do not postpone
the first release until multiplayer rooms, learned corrections, agreement
comparison, or LLM translation are complete.

Recommended first release: an authenticated early-access bidding workspace for
the owner and invited testers. Initial server execution uses owner-reviewed
profiles; anonymous upload/execution of arbitrary Python profiles is out of scope.
User-defined profiles remain a core goal, starting with the existing local editor
and a tested save/export/import workflow. Broader cloud authoring requires its
own storage ownership and execution isolation before being enabled.

### Release order and acceptance criteria

1. **Finish a usable local practice loop.** Keep the four-suit editor, validation,
   random deals, fill-E/W, and reveal controls. Add a mode where the user bids one
   partnership seat and Gible bids the other, initially with opponents passing.
   Support restart/undo, replay, and understandable meanings/errors. Ship one small
   documented reference profile with complete supported auction branches: the
   owner has selected **Daqiush 2/1**, beginning with its uncontested 1NT family.
   Resolve the questions in [the agreement draft](13_daqiush_2over1.md) before
   implementing ambiguous meanings; identify unsupported situations.
   Implement the [slam framework](15_daqiush_slam.md) alongside the 1NT family,
   per the owner's follow-up: supported 1NT training must cover its slam routes,
   not stop at game. Competitive/preemptive slam methods can be tested from
   defined prefixes without requiring complete opening/competition profiles.
   Do not require completion of Meow 2/1 or claim full competitive coverage.
   Include specified-opening / opening-and-response training deals as described
   below, initially for the supported Daqiush branches.
2. **Complete the bounded P0/P1 evaluation slice.** Keep seat-private information
   out of ordinary decisions, sample unknown hands using public evidence, and
   compare a small declared set of late-auction choices with DDS and scoring.
   Expose why a call was selected and distinguish a missing continuation from a
   completed auction. Limit compute time and show failures/timeouts explicitly.
   Broad per-partnership room support from P0 can follow after launch.
3. **Make profiles and sessions durable enough for practice.** Validate saves,
   provide profile export/import and a replayable deal/auction record, and verify
   that restarting/updating the service does not overwrite saved profile data.
   First-release sharing is limited to the stated trusted preview audience; do
   not present it as private multi-tenant hosting.
4. **Prepare hosting and publish the first release.** Remove the localhost-only
   API assumption, serve through HTTPS with a production runtime, protect editing
   and expensive evaluation endpoints, bundle frontend dependencies, and provide
   repeatable deployment, backup, and rollback. Confirm the target hosting and DNS
   access during that implementation stage; neither is assumed configured here.

Launch gate: an invited tester on another computer can open the site, select a
supported profile, enter/deal hands, take a bidding turn with a robot partner,
reach and review supported final contracts, and receive clear diagnostics for
unsupported input. An owner can validate/save/export a profile through the
supported authoring workflow and use the reviewed version in practice. Verify
hidden-hand regression tests, the supported profile fixtures, the browser flow,
and an update/rollback rehearsal. These checks gate launch, not every legacy Meow
fixture or the entire long-term roadmap.

After this gate, deploy before proceeding to P2/P3/P4/P5. A smaller infrastructure
preview may be deployed earlier, but it does not count as the usable first release.

### Specified-opening and opening/response training deals

Owner requirement (2026-10-22): generate deals of a requested bidding type, with
an optional target response as well as target opening, and a chosen or random
opener. When this mode is enabled, the opening call must be the selected target.

Current local slice (2026-10-23): Table has opening and opening/response
training, compass-seat or random opener, optional reproducible seed, an
attempt/time-bounded generator, and a complete legal deal accepted by the
normal bidder's exact selections. The chosen opener is dealer, so the target
opening is the first call; opponents pass during replay. Supported targets
currently include Daqiush 1NT and its 4C/4D Texas responses. The search
checks for an authored target before dealing and reports unsupported calls
separately from exhausted searches. The browser can cancel waiting for the
result; a server search already in progress finishes within its own budget.
Human bidding roles, preceding passes, broader targets, and fully persisted
training sessions remain future work. The first Texas selection is provisional:
simulation must distinguish game-only, keycard-dependent slam, and cases
that require Jacoby, rather than a crude point ceiling. The owner allows
point-based judgment for a balanced, poorly fitting 6NT attempt at **33
combined raw HCP**; that exception does not replace simulation for suit slams.

- Bind the request to a selected profile/version, opening call, optional response,
  opener selection, and actual auction environment. Validate that the target
  branch is supported before searching.
- Generate legal, complete deals and invoke the ordinary bidder with only the
  acting hand and permitted information. Accept a deal only if its **selected**
  opening matches the target; mere candidate eligibility or an HCP/shape filter
  is insufficient.
- In opening/response mode, also evaluate the partner after the actual opening
  and intervening passes and require its selected response to match. Do not pass
  real partner cards into either decision. Public opening evidence is available
  to responder normally.
- Lock the training opening to the requested call. Confirm with the owner whether
  it is automatically inserted or presented as the only permitted first action,
  and whether a targeted response is also locked or left for the learner to find.
  Constraint matching must happen before this lock; never force a mismatching hand
  to bid the target merely to satisfy the training request.
- Support choosing the opener or randomizing it. Before UI implementation clarify
  whether this means compass seat, human/robot role, or both, and how dealer / any
  preceding passes are set. Evaluate the exact resulting prefix, since seat and
  passed-hand status can affect system choice.
- Provide reproducible seeds, cancellation and a bounded attempt/time budget.
  Failure means no matching deal was found within budget, not proof that no such
  hand exists. Unsupported targets, blocked bidding and impossible card constraints
  receive distinct diagnostics; do not silently relax the requested calls.
- Candidate prefilters may accelerate generation, but final acceptance always
  uses the actual profile decision. This is separate from belief sampling for
  choosing a bid: the training generator may own the full deal, the bidder may not.

Acceptance tests: re-evaluate generated openings/responses with the same profile
and environment; confirm exact targets, all 52 unique cards, no hidden-hand input,
repeatability, seat handling, first-call locking, cancellation and bounded failure.

### P0 — Information boundaries and reusable decision interfaces

- Separate the table's complete deal from each seat's permitted view. The identified
  `partner_hand` path was removed on 2026-10-22: the runner no longer injects it,
  normal decision/replay environments discard it, and real-partner expressions
  fail explicitly. Broader permitted-view interfaces remain to be built; any future
  oracle analysis must have a separate, labeled interface.
- Define human/robot seat controllers and per-partnership profile bindings.
  Replay opposing calls from disclosed meanings rather than through our profile.
- Separate public explanations from private traces, source files, and seat memory.
- Keep engine interfaces usable locally and remotely. Cloud execution of uploaded
  Python-based profiles needs isolation beyond the existing AST checks.
- Use small neutral fixtures for these capabilities; do not wait for Meow 2/1.

Exit evidence: changing real hidden cards cannot change an actor's decision when
its permitted view and random seed are unchanged. The actor may reason about
sampled possibilities, but cannot inspect the actual hidden hands or another
seat's private memory. The same interface can represent two different partnership
profiles without requiring their private source to be public.

### P1 — First local simulation baseline (next vertical slice)

2026-10-23: The first analysis-only route experiment is available at the
first response to 1NT. It reuses paired sampled deals, follows authored
continuations with seat-private hands, and reports coverage plus DDS contract
completion. Daqiush Texas game-only can complete; the Jacoby route remains
unavailable until its rules are authored. Scoring, stronger uncertainty checks,
and automatic selection remain in this milestone.

- Add deterministic sampling of unseen hands from public evidence, with joint
  card consistency, hard/soft evidence distinctions, and contradiction diagnostics.
- Integrate a versioned DDS adapter and duplicate scoring with declarer, contract,
  doubling, and vulnerability handled explicitly.
- At a small set of declared late-auction entry points, compare Axiom-compliant
  calls through defined continuations; report missing branches instead of treating
  artificial calls as final contracts or inventing a Pass.
- Keep future actors' decisions constrained by their own information. Report
  sample count, seed, uncertainty, evaluator version, and budget exhaustion.
- Start with a documented raw-score objective; add IMP/reference-result and
  MP/reference-field evaluation deliberately. Do not silently replace current
  HCP-based Axiom conditions with simulation scores.

Exit evidence: a reproducible report comparing late-auction choices on the same
sampled deals, with legality, information-boundary, solver, scoring, and error-path
checks. This is a decision experiment, not merely replay of supplied hands.

### P2 — Local agreement-comparison experiment

- Accept multiple call-meaning alternatives plus each alternative's continuations.
- Freeze the common prefix, deal population, opponent behavior, objective, and
  evaluator version; use matched deals/seeds and held-out evaluation deals.
- Report expected utility, making rate, coverage/blocked rate, paired uncertainty,
  and representative failures. Define the target behind "correct contract" and
  distinguish branch-local results from full-system results.
- Begin with an engine/report interface; add a comparison workspace once that
  experiment is reproducible.

### P3 — Online mixed-profile practice, bidding first

- Add authenticated rooms, turn authority, seat ownership, reconnects, and session
  persistence. Support North/East humans with South/West robots and different
  profiles for the two partnerships.
- Route permitted seat views and public explanations; never distribute the full
  deal or private profile source to all clients for convenience.
- Add profile persistence/import/export/versioning and optional cloud storage with
  explicit access controls. Decide the local-only privacy promise before marketing
  it. Do not silently upload profiles for remote inference or assistance.
- Keep card play optional. A play controller and legal-information card-play agent
  can be prototyped earlier offline for research without blocking bidding rooms.

Exit evidence: two clients can complete and replay an auction with the selected
profiles and no cross-seat/private-trace disclosure in normal participant views.

### P4 — Card play and empirical DDS correction

- Assess a card-play engine and generate synthetic/public-data trials under legal
  information, recording both declarer and defender models and auction context.
- Pilot A/A+1 trials with legal-level edge cases and contract-specific success/failure
  labels. Set each trial's play target to its tested contract; never reuse results
  from a different target as that trial's label. Extend upward 1/2/3 to completion
  at A+1/A+2/A+3 and downward 1/2/3 to failure at A/A-1/A-2. For a downward
  tested level L<1, play level one targeting seven tricks and label down at least
  2-L; level zero/minus one therefore become one down at least two/three.
  Skip illegal upward levels and report eligible counts; ordinary cross-target
  rates are not bins of one distribution.
  Keep all
  contracts, repeat trials, and equivalent variants of a deal in one dataset split.
- Compare raw DDS with a simple calibrated baseline before costly self-supervised
  pretraining. Outcome prediction from AI-play labels is supervised learning.
- Evaluate calibrated completion probabilities, decision utility under explicitly
  stated success/failure payoffs, and held-out
  player populations; document limits on claims about human play.
- Save the encoder/model and versioned research datasets, not an exhaustive lookup
  table of all possible deals. Downloadable correction models should preserve the
  option of local inference; private user data is not a default training source.

### P5 — Natural-language-to-Gible translation with an LLM

This is an explicit long-term product goal, added by the owner on 2026-10-22.
The milestone number groups the work; it does not require waiting for all P4
research if authoring interfaces become stable earlier. It is not a launch gate.

- Accept natural-language system notes and incremental descriptions of agreements.
  Generate Gible's existing BSL/Gadget/Profile objects and, where needed,
  Policy Functions, Frames, and Private Routes; do not invent a new target language.
- Support a locally deployed model as well as an optional remote provider through
  a replaceable model interface. A local workflow must keep prompts, retrieved
  examples, profile contents, and logs local; do not silently fall back to a remote
  service. A model running on Gible's server is not the same as one running on
  the user's device for confidentiality purposes.
- Translate first into a reviewable structured interpretation. Surface ambiguous
  ranges, forcing status, interference treatment, defaults, and missing follow-ups
  as questions or marked gaps; do not fabricate agreements to make code compile.
- Show source-text provenance, generated changes, human-readable system notes,
  and representative test auctions. Compile/validate in an isolated context, run
  Axiom/legality checks and fixtures, then let the user review and apply the draft.
  Syntactic validity alone does not establish semantic fidelity.
- Keep the previous profile intact until the user applies changes; support undo
  and export. The LLM translates agreements, while the executable engine continues
  to enforce them during bidding.

Exit evidence: a user can describe a bounded convention, resolve ambiguities,
review the generated agreement and tests, apply it, and practice with it. The
same workflow works with a configured local model without uploading the notes.

## Deployment Workstream

Deploy `gible.hogetsu.uk` at the first usable-release checkpoint above.
First address the localhost API URL, production serving, editor access, and data
separation/backups. Public cloud execution of uploaded profiles additionally needs
tenant isolation and resource limits. Deployment is an enabling task, not a reason
to force the engine into a cloud-only design. Follow local development and tested
updates after launch; do not make the public server the development workspace.

### Fly.io deployment preparation (not implemented)

The following work is recorded for the Fly.io deployment stage. It must preserve
the existing local `gible.cmd` workflow and local repository-backed data paths.

- [ ] Make the production server listen on `0.0.0.0` and the Fly-provided `PORT`,
  using internal port `8080`, without changing the local backend's default
  `127.0.0.1:8765` binding.
- [ ] Serve the frontend static files from the Python production server so one Fly
  service and hostname provide both the UI and API.
- [ ] Use same-origin `/api/*` requests in production while retaining the local
  frontend connection to `127.0.0.1:8765`.
- [ ] Add a lightweight `/healthz` endpoint for deployment and service checks.
- [ ] Add a configurable `GIBLE_DATA_DIR`: use `/data` on Fly and preserve the
  current repository paths for local execution.
- [ ] On the first start of an empty persistent data directory, copy the bundled
  profiles into `/data/profiles`; subsequent System Editor changes must update
  the persistent copies rather than the image contents.
- [ ] Store IV Scanner output under `/data/reports/block_scans` in production.
- [ ] Add and review `Dockerfile`, `.dockerignore`, and `fly.toml` deployment files.
- [ ] Add pinned production Python dependencies, including `endplay==0.5.12`, and
  verify that DDS-backed analysis works in the deployed Linux image.
- [ ] Mount a Fly Volume at `/data`, keep the first deployment single-machine,
  and test profile/report survival across restart, redeploy, backup, and rollback.
- [ ] Protect the deployed editor and expensive endpoints before public DNS
  cutover; direct access to the Fly origin must not bypass the chosen access layer.

## Supporting Product Backlog

- Improve profile authoring, validation, explanations, and system-note generation
  where they support the prioritized milestones.
- Add PBN import and constrained dealing beyond the existing random deal and
  fill-E/W features.
- Add sharing, copying, and forking with explicit disclosure/access choices.
- LLM-assisted natural-language translation is tracked as explicit milestone P5;
  it is not a prerequisite for the first website release.
- Add versioned alert-regulation analysis and broader tournament features later.

## Frontend Roadmap

Supporting backlog; the priority sequence above takes precedence.

1. Add backend-backed BSL and Policy Function validation so the code editor can show real compile errors.
2. Improve guide-mode editing for class-authored `call.meaning`, `call.effect(...)`, `self.frame(...)`, `self.route(...)`, and `self.evaluator(...)` blocks.
3. Add safer structured editors for Policy Function registration and source-block movement.
4. Add profile-level system-note preview and export.
5. Add deal import and constrained hand-dealing controls beyond the current random full-deal button.
6. Add a visual auction explainer that shows public meaning, internal origin, state changes, active Frames, and Private Routes.
7. Add comparison view for multiple Partnership Profiles bidding the same deal.
8. Add browser tests for file CRUD, save/discard behavior, code editor behavior, and table simulation.
9. Move from no-build React to a normal frontend build pipeline when dependency management is stable.
10. Prepare the UI structure for later desktop and mobile shells.

## Engine Roadmap

Supporting backlog; the priority sequence above takes precedence. Keep mandatory
Axioms above Policy and evaluation preferences. Changes to strength evidence used
by Axioms require an explicit design, not an implicit override by a DDS score.

1. Add schema validation for state records and runtime objects.
2. Expand `StateView` conflict diagnostics for contradictory ranges and values.
3. Expand relative-call support: cheapest bid, jump, new suit, step responses after interference, DOPI/ROPI, Kickback, and relay systems.
4. Make Relay Automata executable for symmetric relay and similar methods.
5. Expand Frames beyond current transfer/keycard slices into general game-force, Lebensohl, control-bidding, and relay contexts.
6. Expand Private Routes with richer branching, route-vs-route comparison, memory expiry, and serialized deal/session IDs.
7. Add projected effects to explanations so users can inspect what the selected call will add to state.
8. Add central legal-call constraints to reusable Gadgets.
9. Add custom evaluator libraries for suit quality, losing trick count, controls, rebid ease, playing strength, and vulnerability style.
10. Add deterministic random-source support for randomized policies.
11. Redesign quantitative 4NT continuations as a reusable method rather than
    auction-by-auction enumerations. Cover Pass, the ambiguous extra-shape 5C
    ace ask, direct ace-showing steps, strain-aware five-level stops, natural
    six-level descriptions (including 6H from a five-card heart suit),
    interference, simulation/fallback, and strict separation from RKCB,
    NFRKCB, Voidwood, and natural 4NT. The bounded Daqiush 1NT routes remain
    explicitly authored until this redesign has its own approved specification.

## Meow 2/1 Benchmark Roadmap

**Paused at the owner's request.** Preserve this backlog and its regression
evidence, but do not make completion a prerequisite for P0/P1. Do not rewrite
fixtures or disable checks to disguise known profile-coverage failures.

1. Refactor the 1N response layer according to `docs/09_meow_1nt_technical_design.md`: split terminal, major-search, transfer, two-suiter, and slam route policies.
2. Refactor the non-1N opening families according to `docs/10_meow_opening_technical_design.md`: split 1m response/rebid, 2C rebid, checkback/XYZ, and game-try route policies.
3. Complete Regular Stayman: opener `2H/2S`, garbage Stayman, Smolen, invite/game continuations, and slam continuations after a fit.
4. Complete transfer continuations after 1N: weak signoffs, invites, game placement, second suits, superaccept follow-ups, and slam routes.
5. Complete minor-transfer continuations and minor-slam routing.
6. Complete minor continuations after inverted and Crisscross raises.
7. Complete 2N structure: transfers, minor-suit Stayman, and follow-ups beyond the current Puppet dialogue.
8. Extend Puppet Stayman beyond current game-placement branches, including slam continuations and strong-2C notrump adapter reuse.
9. Add full Jacoby 2N opener continuations and splinters.
10. Expand forcing 1N continuations, 2-way NMF/XYZ trees, slam judgment, control bidding, queen asks, signoffs, final placement, and competitive auctions.

## Research Benchmarks

Use real systems to pressure-test expressiveness:

- mainstream 2/1,
- Precision,
- Polish Club,
- Washington Standard,
- Kai-Isaac-Quan Strong Diamond,
- KK or symmetric relay systems.

The goal is not to hard-code those systems. The goal is to make sure the runtime object model, BSL, Frames, Private Routes, Policy Functions, and relative-call machinery can express them.

## Design Principles

1. Public meaning and internal origin are separate.
2. A selected call should identify its producing Gadget and Call Specification.
3. Judgmental choices belong in Policy Functions within mandatory Axiom constraints; simulation supplies evaluation evidence.
4. Multi-step private motivation belongs in Private Routes.
5. Public auction context belongs in Frames and state records.
6. Broad bridge methods and small bridge tools are both Gadgets.
7. Do not add one-off engine fields for every new bridge idea.
8. Do not encode long dynamic auctions as giant enumerations when state, Frames, relative calls, or policy functions can express the structure.
9. The profile author may define profile-specific state fields. A global shared vocabulary can be added later, but should not block custom systems now.
10. Private route memory is seat-owned.
11. Release-version changes happen only when Meow Li explicitly asks for a new version.
12. Normal decisions use only the acting seat's permitted information. Full-deal analysis is an explicitly separate mode.
13. Preserve the ability to execute profiles and profile-sensitive evaluation locally; final privacy guarantees remain a product decision.
14. Compare agreement alternatives on matched deals with declared objectives, coverage, uncertainty, and evaluator versions.
