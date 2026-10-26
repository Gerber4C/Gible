# Daqiush reviewed 1NT follow-ups design

## Goal

Complete the executable portions of the reviewed Daqiush 1NT system for the
named groups in the audit while preserving `missing_call_behavior = 'block'`
for decisions that the review does not define precisely.

## Scope

The work covers two related but independently testable areas:

1. **Slam follow-ups:** G001–G003, G006–G009, G012–G013, G016, G022,
   G032, G040, G049, G059, G061, G068, G071, G081.
2. **Invitation and shape routing:** G018, G021, G030, G039, G051, G069,
   G072, G084, G085.

The audit JSON is the source of truth. A rejected proposal is not implemented.
Pending or investigative notes are implemented only where an existing public
auction convention makes the behavior unambiguous. “Simulation” is used only
to choose among publicly legal alternatives; private sampled-deal information
must not appear as a public meaning or condition.

## Design

### Slam follow-ups

Keep the existing separation between:

- `one_notrump_invitations`: Stayman, major-fit shortage probes, and
  post-answer control/keycard decisions;
- `jacoby_major_transfers`: ordinary transfer continuations, second-minor
  game-forcing routes, and major-fit placement;
- `jacoby_splinter`: confirmed shortness, adjusted-strength cues, and
  keycard asks;
- `south_african_texas`: game-only versus slam-keycard Texas;
- `confirmed_keycard`: public keycard answers and final placement.

Add missing continuation states rather than broadening unrelated predicates.
After a denied slam try, the system must explicitly choose the agreed-major
game or pass according to the reviewed strength class. After a confirmed
shortage, remove the short-suit waste before selecting pass/game, a cue bid, or
4NT. For G003/G012/G081, only hands classified as slam-interest may issue
4NT; game-only Texas or ordinary transfer hands must stop in the major game.
G016 is intentionally split: the artificial 4H convention may be added only
if the audit's target auction supplies a complete public trigger; its
continuation remains blocked because the review does not define the later
auction. No rule may infer a hidden three-card fit from the call alone.

### Invitation and shape routing

Use the existing quality helpers and public partner constraints:

- ordinary five-card-major invitations distinguish weak, invitational, and
  game values after the opener’s 2NT response;
- long-minor routes distinguish direct game, 3NT-oriented solid suits, and
  control-based invitations;
- 6-5 minor hands use effective control points and choose 4NT only at the
  reviewed threshold, otherwise the reviewed lower-level probe;
- super-shaped hands may bypass an invitation when the audit explicitly says
  the shape itself is game-forcing;
- five-card-major and minor fits remain natural unless a reviewed convention
  explicitly reserves the call for a slam probe.

No new convention is introduced for a reviewer note that lacks a complete
auction and a public trigger. Such cases receive regression coverage for the
existing blocked behavior and remain documented as follow-up work.

The audit source for this work is
`D:\A0_bridge\]crtb-b\gible-review-a22163d59b5ee620d5b9.json`; its final
reviewer note controls conflicts with an earlier proposal.

## Testing

Every implemented rule gets a selector-level test for:

- the intended final auction;
- a nearby weaker or stronger hand that takes the adjacent branch;
- a negative case proving the new rule does not steal an existing call;
- public-information safety where a simulation helper is involved.

Relevant suites are `test_daqiush_resample_followups.py`,
`test_daqiush_jacoby.py`, `test_daqiush_splinter.py`,
`test_daqiush_minor_invitations.py`, `test_daqiush_minor_slam_simulation.py`,
and `test_daqiush_opening.py`. Run targeted tests with `PYTHONPATH=backend`
before the broader Daqiush suite.

## Documentation

Update `docs/13_daqiush_2over1.md` and `docs/15_daqiush_slam.md` only for
rules that have executable tests. Do not edit the external audit JSON.
