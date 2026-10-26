# Gible: Product Vision And Development Direction

Date: 2026-10-22 (Asia/Shanghai)
Platform version: 0.0.8 (unchanged)
Owner: Meow Li

This document records the owner's long-term goals in English and explains how
they change the project's priorities. Part I is a translation of the requested
goals. Part II contains technical recommendations, not additional approved
requirements. The implementation sequence is maintained in
[the roadmap](08_roadmap_todo.md). This is a product direction document, not a
claim that the capabilities below already exist.

## Part I — The Owner's Goals

### 1. User-defined bidding systems and confidentiality

Users can define their own bidding systems.

Confidentiality of bidding agreements is critical for professional players.
Users should be able to use Gible without having to trust the developer with
their systems: the software architecture should allow a system to remain entirely
on the user's local device, without requiring an upload. Whether to make this
local-only option a firm requirement remains undecided, and advice is welcome.
Users can also choose to upload their systems to the cloud.

### 2. Practice across different systems, with humans and robots

Users can practice bidding against one another while using different bidding
systems. For example, East and North may be human players, with West and South
controlled by Gible robots. Playing out the cards after the auction is optional.

### 3. Simulation-based decisions in the later auction

In the early stages of the project, decisions in the later part of the auction
will be driven by simulation: generate multiple possible deals, use double-dummy
analysis, and estimate which call has the highest expected value.

At a later stage, algorithms will correct the differences between double-dummy
results and results achieved in actual play.

#### Proposed research approach

The initial idea is to use self-supervised learning on the server to learn
representations from a large number of complete four-hand deals. Then train or
obtain a capable card-play AI and have it play deals, without having it conduct
the bidding.

Specifically, if double-dummy analysis indicates a maximum makeable contract of
level A in a particular suit or no-trump, run the card-play AI at levels A and
A+1 with the same declarer. Measure upward deviations, where A+1 succeeds, and
downward deviations, where A fails. Train a model to learn how the deal features
relate to the probabilities of these deviations.

Store the learned representations and correction information, and use the
corrected double-dummy evaluations in bidding decisions. This is a research
proposal; the terminology and experimental design are open to correction.

Owner clarification (2026-10-22): the correction target is whether the particular
contract is made, conditional on that contract's trick target. Do not pool actual
trick counts across different targets. With the same deal and suit, a strategy
aimed at ten tricks might take nine, while one aimed at twelve might take twelve.
The initial correction model should therefore use contract-specific success/failure
labels, not attempt to predict a universal trick-count distribution.

The owner also proposes extending deviation labels to two and three tricks:
upward deviations use completion trials at A+2 and A+3, while downward deviations
use failure trials at A-1 and A-2. These remain separate target-specific trials,
not measurements of overtricks or undertricks while playing level A.

If a downward trial would fall below level one, the owner specifies a level-one
trial with an adjusted failure threshold: a hypothetical level zero becomes
level one down at least two, and a hypothetical level minus one becomes level one
down at least three. This is an explicit low-level exception to the ordinary
contract-completion labels.

### 4. Bidding-system design and comparison

Near the ends of a bidding system's auction branches, users can specify several
alternative meanings for calls, together with the continuations for each
alternative. Gible can compare how often those alternatives reach an
appropriate final contract.

### 5. Natural-language system translation using a large language model

Integrate a large language model, including the option of a locally deployed
model, to translate natural-language bidding-system descriptions into Gible's
executable agreement language. This is an explicit long-term goal added by the
owner on 2026-10-22.

### Delivery requirement: launch a usable subset first

The owner selected **Daqiush 2/1** as the reference profile on 2026-10-22, starting
with its uncontested 1NT family. [The agreement draft](13_daqiush_2over1.md) preserves
the source notes and all open questions; ambiguous agreements require owner
clarification rather than inferred defaults.

An additional requested practice feature is dealing to specified opening calls,
or to a specified opening-and-response combination. The generator must find hands
for which the chosen profile actually selects those calls, allow a chosen or
random opener, and require the target opening when the mode is active. The
roadmap records the information boundary, acceptance checks, and pending UI
semantics. This feature is planned, not currently implemented.

Implement a basically usable subset and deploy it to `gible.hogetsu.uk`, then
continue through tested updates. Full multiplayer, calibration research,
agreement-comparison tooling, and LLM translation need not precede the first
release. The [roadmap](08_roadmap_todo.md) defines the proposed first-release scope
and observable acceptance criteria.

## Part II — Technical Assessment And Recommended Direction

### 6. Preserve local execution as an architectural option

Recommendation: keep the engine usable locally and make cloud services optional.
The final commitment to a professional-grade local-only privacy mode remains
pending. Three deployment choices have different tradeoffs:

| Choice | Benefit | Cost or limitation |
| --- | --- | --- |
| Cloud execution | Simple access and centrally managed computation | The server must be trusted with any plaintext profile it executes |
| Local execution with optional online rooms | Profile evaluation can remain on the user's device | Local installation, updates, compute availability, and room connectivity must be managed |
| Browser-local execution | No separate installation | Requires a compatible engine/solver runtime; remotely delivered scripts and updates remain part of the trust model |

Prefer the second option as the initial design assumption, building on the current
local Python engine. Do not require a browser port or promise that the existing
browser prototype already provides developer-independent confidentiality.

Keeping a file on disk is insufficient if its contents, derived constraints,
diagnostics, or training examples are sent to a service. A local-only mode must
keep profile evaluation, hidden inference, and profile-sensitive simulation local
as well. Optional remote analysis and LLM-assisted authoring need explicit data
sharing choices. Cloud storage and cloud execution are separate choices:
client-encrypted backup does not enable ordinary server execution without access
to plaintext.

A stronger "do not trust the developer" claim requires inspectable code,
verifiable/pinned builds and dependencies, controlled updates, and auditable
network behavior. A web page served afresh by that developer alone cannot provide
that guarantee. The current frontend loads dependencies from a remote CDN, and
the current API returns detailed explanations; neither has been audited for this
privacy promise.

Online play necessarily shares calls and agreed public explanations. Confidential
source, unpublished branches, and private decision traces are distinct from the
agreement disclosures opponents need. Observed auctions can still reveal parts
of a system. No promise should imply that opponents cannot infer agreements.

### 7. Separate the table, the player's knowledge, and the profile

Recommended responsibilities:

- **Table/session service:** owns turn order, legal actions, dealer, vulnerability,
  deal identity, reconnect state, and optional play progression. A first online
  version may trust this service with the deal; distrust of the service for deal
  secrecy or anti-cheating is a separate, stronger requirement.
- **Seat controller:** human or robot. Receives only that seat's permitted view
  and produces a call or play. Private route memory remains seat-owned.
- **Partnership Profile:** defines agreements for one partnership. North/South
  and East/West may use different profiles. Each human/robot pair must agree on
  its profile; arbitrary conflicting agreements within a pair are not implied.
- **Local or cloud engine adapter:** runs the same decision contract in the
  selected execution location. Uploaded executable profiles require actual
  isolation, resource limits, and tenant boundaries; current Python syntax
  restrictions are not a production security sandbox.
- **Public explanation interface:** communicates disclosed meanings without
  exposing source code, private routes, or the actual hand behind a call.

Mixed-profile replay must interpret each call using the calling partnership's
public explanation, not reinterpret every call through one profile. A private
profile can provide that explanation from its local engine. The room should not
need to receive the entire profile to relay an auction.

For real decisions, inputs should contain the acting hand, public auction and
explanations, public play information when applicable, and the acting seat's own
private memory. Actual hidden hands belong only to the deal controller and
offline evaluation harness. Training-table reveal controls must not alter what
the decision engine knows.

### 8. Build simulation before learning a correction

The initial deliverable should be a measurable local decision pipeline:

1. Recover public bidding evidence and distinguish hard constraints from
   uncertain tendencies. Version the profile and evidence used.
2. Sample complete possible deals consistent with the acting hand and available
   evidence. Sample partner and opponents jointly, respecting all 52 cards.
   Do not complete the deal using the real hidden partner hand.
3. Generate legal candidate calls with defined meanings; apply Axiom obligations.
4. Evaluate candidate continuations using the profiles/behavior models available
   for each side. Every future decision uses that actor's information, not the
   sampled world's full layout. Use a bounded search with an explicit unresolved
   result when a continuation is missing.
5. Evaluate resulting contracts with a double-dummy solver, tracking declarer,
   suit/no-trump, level, doubling, and vulnerability.
6. Convert results to the chosen scoring objective and compare candidates on the
   same sampled deals. Record uncertainty, failures, seeds, and runtime budget.
7. Let Policy select among Axiom-compliant candidates using these evaluations.

[DDS](https://github.com/dds-bridge/dds) is a candidate solver dependency; its
platform support, interface version, redistribution terms, and performance must
be checked before integration. Solver output is a trick estimate under complete
information, not a direct recommendation for the next call.

Initially, restrict this to explicit late-auction decision points, such as
choosing between a signoff and a game continuation. An artificial call cannot be
scored as if it were the final contract. A switch to simulation needs a declared
entry condition and candidate semantics, rather than an arbitrary auction length
or a silent escape from a missing agreement.

Expected value must name its objective. Raw duplicate score is a useful first
baseline. IMP comparisons require a specified reference result, and matchpoint
comparisons require a reference field model. Compute the expectation of the
score/utility over outcomes; do not score only the mean number of tricks. Making
probability alone misses bonuses, overtricks, penalties, and sacrifices.

Uniform sampling over hard constraints is an initial approximation, not a claim
to recover the true posterior distribution. Later, account for the likelihood
that a player with a sampled hand would choose the observed calls. Contradictory
constraints or insufficient samples must produce diagnostics rather than silently
discarding evidence or reverting to the known full deal.

**Axiom compatibility:** simulation must not silently bypass forcing, game-force,
invitation, game, or signoff obligations. The present strength-based Axioms need
an explicit future design for accepting evidence from a probabilistic evaluator;
fixed HCP thresholds and simulated contract utility can disagree. Until that
design is agreed, keep mandatory filtering and report conflicts. Do not turn
simulation into permission to reinterpret authored calls.

### 9. Refine the proposed double-dummy correction experiment

#### 9.1 Two learning tasks

Learning a deal representation through, for example, masked-card reconstruction
can be self-supervised: training targets come from the deal itself. Masked
reconstruction is an established approach in other domains, but its usefulness
for bridge requires measurement; [the MAE paper](https://arxiv.org/abs/2111.06377)
does not establish that it will work here.

Predicting contract success from AI-play outcomes is supervised learning
with automatically generated labels. Training the card-play agent itself through
self-play may use reinforcement learning, but that is a separate task. A useful
first comparison is raw DDS versus simple feature-based calibration versus
representation-based calibration. Expensive pretraining should earn its place
through held-out improvements.

#### 9.2 Define upward and downward deviations precisely

Let T_DD be the double-dummy number of tricks for a fixed complete deal, declarer,
and suit/no-trump. If A = T_DD - 6 is a legal level (1 through 7), the proposed
labels are:

- Downward deviation: play at level A yields fewer than 6+A tricks.
- Upward deviation: play at level A+1 yields at least 7+A tricks, when A+1 is legal.

For the extended labels, let k be 1, 2, or 3:

| Label | Contract tested | Play target | Positive label |
| --- | --- | --- | --- |
| Upward k | A+k | 6+A+k tricks | That contract is made |
| Downward k | A-(k-1) | 6+A-(k-1) tricks | That contract fails |

Thus downward 1 tests failure at A; downward 2 tests failure at A-1; downward 3
tests failure at A-2. Keep the deal, declarer, and suit/no-trump fixed, but set the
agent's target separately for every tested contract.

For downward k, let L = A-(k-1). If L >= 1, test failure at L normally. If L < 1,
play a level-one contract with the objective of making seven tricks, and label
whether it goes down at least `2-L` tricks (equivalently, actual tricks < 6+L).
The threshold is "at least", not "exactly"; a worse failure also satisfies it.

| Baseline A | Downward 1 | Downward 2 | Downward 3 |
| --- | --- | --- | --- |
| 1 | Fail at level 1 | Level 1 down at least 2 | Level 1 down at least 3 |
| 2 | Fail at level 2 | Fail at level 1 | Level 1 down at least 2 |
| 3 | Fail at level 3 | Fail at level 2 | Fail at level 1 |

Only this boundary exception uses a margin of defeat at the clamped level-one
target. It does not substitute an A-level play for ordinary A-1/A-2 trials.
Upward trials still require a legal tested level of 1 through 7; out-of-range
upward trials are unavailable labels, not successes or failures. Each label's
reported rate must identify its eligible trial population and count.

These are different experiments, not complementary probabilities. The contract
can change the players' objectives and choices. If A=7, there is no level-8 trial.
For T_DD<7, A is not a legal contract level: downward labels use the same explicit
level-one boundary rule, while upward trials are generated only when A+k is legal.
Store the baseline, tested contract, play target, and binary-label threshold
separately so the boundary substitution cannot silently change the definition.

Actual play can outperform the double-dummy result when defenders make mistakes,
and underperform when declarer lacks information or makes mistakes. The learned
correction therefore depends on both declarer and defender strength and behavior.
It is not a universal correction to a deal independent of the players.

#### 9.3 Train on legal information and relevant conditions

The experiment controller may know all four hands to calculate DDS and record
labels. Card-play agents must receive only their legal information: no hidden
defender cards, no future cards, and dummy only when exposed. The declarer
controller can subsequently play both declarer and dummy.

Although the agents need not bid, their play may depend on the auction and public
explanations. Supply a consistent auction context or clearly label an experiment
as having no auction information. Record the contract, declarer, vulnerability,
doubling, scoring objective, opening-lead policy, player versions, compute budgets,
and random seeds. Do not manufacture an auction that discloses the full deal.

Repeated deterministic play of one deal gives the same outcome, not independent
evidence of a probability. Estimate rates across a defined deal population and,
where relevant, varied stochastic policies, seeds, or player populations.
[BEN](https://github.com/lorserker/ben) is one possible card-play engine to assess;
this is not a claim of suitability, strength, or license compatibility for this
project without evaluation.

#### 9.4 Predict completion for each contract and target

The agreed research target is:

`P(contract made | sampled deal, contract, trick target, public context, player model)`.

For each trial, set the play objective to the tested contract's required tricks
and record success/failure. Trials at A and A+1 remain separate, even with the same
deal, declarer, and suit. Do not infer success at one level from the trick count
achieved while targeting another level, or force cross-level monotonicity for
agents that use different target-dependent strategies. The level-one boundary
labels above are an explicit exception: their binary outcomes require observing
whether the specified undertrick threshold is reached in a level-one-target trial.

Start with the proposed A/A+1 experiments and expand to other legal contracts
including the specified A+2/A+3 and A-1/A-2 deviation trials. Actual trick count is not a required
learning target. Binary completion probabilities alone do not identify exact
expected duplicate scores with variable overtricks and undertricks: any utility
calculation based on them must state its assumed success/failure payoffs. The
initial raw-DDS score baseline and the later completion-calibration model must
remain distinguishable; do not describe the latter as a full score distribution.

These rates are separate conditional outcomes under different play targets, not
mutually exclusive bins of one random variable. Do not sum them to one or subtract
ordinary cross-target rates to derive exact deviation counts. Boundary labels
sharing the same level-one trial can share its result and have nested thresholds;
that does not justify reusing the trial for different contract targets.

At bidding time, the model may evaluate each *sampled* complete deal, then average
over those samples. It must not take the actual unknown layout as input. The
simulation controller owns the sampled worlds; the player-facing decision API
still exposes only legal information.

Saving model weights and a versioned feature encoder is essential so new deals
can be evaluated. Store selected deal embeddings, labels, and provenance for
research and reproducibility; do not attempt to precompute embeddings for every
possible deal. Representation coordinates are features, not automatically
interpretable or causal explanations of why a contract succeeds.

Use held-out deals with all related contracts, repeat plays, and equivalent
augmentations kept in the same split. Compare probability calibration and
decision utility against raw DDS and simple baselines. Test multiple player
versions and report whether claims apply only to those AIs or also to held-out
human data. Train initially on synthetic/publicly usable deals; do not assume
permission to train on private profiles, room logs, or user uploads.

Finally, an outcome correction does not resolve all imperfect-information
search errors. Averaging perfect-information solutions can implicitly select
different strategies in indistinguishable worlds (strategy fusion). This is a
known issue studied in [the alpha-mu bridge search work](https://arxiv.org/abs/1911.07960).
Calibration and information-respecting continuation search address different
parts of the problem.

### 10. Compare agreements through matched experiments

A comparison experiment should freeze the common auction prefix, relevant deal
population, baseline profile, opponent behavior, scoring objective, and evaluator
version. Each alternative includes both its call meanings and subsequent
continuations; replay the shared prefix under the common agreements and branch
only at the declared comparison point.

Use the same hidden deals and paired random seeds across alternatives. Each bot
observes only its permitted information. Evaluate two or more alternatives, not
just the numeric value of one candidate call.

Report expected score/IMP/MP under the declared reference model, making rate,
game/slam frequency, wrong-suit or wrong-side contracts, missing-continuation
rate, and paired uncertainty. Include representative successes and failures.
Do not drop blocked auctions without reporting them; that would favor incomplete
alternatives. Give coverage and conditional performance separately when a full
comparison cannot be completed.

"Correct contract" requires a declared benchmark. A double-dummy best contract
is an oracle reference, not necessarily attainable from the auction information
or against competition. Allow near-ties and report expected-utility regret
relative to an explicitly defined feasible comparison set. Separate performance
on the affected branch from overall system performance, which also depends on
how often that branch is reached.

## Part III — Current State And Next Milestone

As inspected on 2026-10-22:

| Capability | Repository status |
| --- | --- |
| Editable executable Partnership Profiles | Present in the local prototype |
| Axioms, public evidence, K-R quality, blocked diagnostics | Initial implementation present; profile coverage remains incomplete |
| Four-suit editor, random deal, filling E/W, reveal controls | Present |
| Auction runner | Supplied hands and one profile; absent seats pass |
| Unknown-hand sampling from bidding evidence | Not implemented |
| Double-dummy solver / expected-score decision evaluator | Not implemented |
| Multi-user mixed-profile rooms / card play | Not implemented |
| Learned DDS correction / convention experiment UI | Not implemented |
| Audited local-only privacy / cloud profile isolation | Not implemented |

The runner no longer supplies `partner_hand` to individual bidders. Normal bidding
and replay discard a caller-supplied `partner_hand`, and legacy expressions that
read the real partner hand fail explicitly. Public partner evidence remains
available through state/knowledge. This fixes the identified path; it is not a
general sandbox or a completed multi-user information-isolation architecture.

**Next milestone:** an information-safe local late-auction simulation slice,
using small purpose-built profiles and reproducible deals: permitted seat views,
evidence-constrained sampling, a DDS adapter, score calculation, explicit candidate
continuations, and a comparison report. Establish the seat/profile interfaces so
mixed-profile rooms can follow without rewriting the engine. Do not begin a large
training run before this baseline is measurable.

Meow 2/1-specific completion remains paused. Its fixtures remain useful evidence
and must not be rewritten to hide failures. Deployment of `gible.hogetsu.uk`
is now a required checkpoint after a usable practice loop and bounded simulation
baseline, before the remaining long-term features. The first release is proposed
as authenticated early access. Cloud deployment must not force all profile execution onto the
server or imply that upload, isolation, or privacy guarantees already exist.

Open product decisions are the strength of the local-only privacy commitment,
the first scoring objective (raw duplicate score is recommended for the baseline),
the initial card-play population for calibration, and when to support public
cloud execution of user-supplied profiles. These do not prevent documenting the
direction or building a local baseline.
