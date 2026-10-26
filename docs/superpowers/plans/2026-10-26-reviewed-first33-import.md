# Reviewed 1NT groups G001–G033: implementation plan

> Execute directly in the existing checkout. This checkout contains the user's ongoing Gible work and the approved review JSON; do not recreate or overwrite the review.

**Goal:** Move the user's reviewed 1NT agreements into executable Daqiush calls without treating rejected draft suggestions as approved rules.

**Architecture:** The reviewed JSON is the source for decisions and reviewer notes. Small, pure hand-evaluation functions compute strength; profile gadgets declare the actual calls; selector-level simulations are used only where the review requires sampled deals. Replays verify public-information boundaries and full auction completion.

**Tech stack:** Python BSL profile, `unittest`, sampled DDS adapter.

---

## Stage 1: deterministic rules in this turn

- [x] Update side-suit control valuation for the G033 replacement table. Keep trump raw HCP, and retain the existing 14.5 adjusted acceptance threshold until a new threshold is specified. Test all named honor combinations and a 4♣ invitation replay. The owner's later clarification extends raw HCP to every publicly known 4+ partner suit, even when it is not trump.
- [x] Resolve a 5♦ 0/3 keycard answer according to G002: assume partner has three keycards unless the asker holds three, when three would be impossible. Do not read partner's actual cards. Test both cases and preserve existing queen-ask blocking where appropriate.
- [x] Apply G031's revised poor-eight gate: a raw eight with K–R at most 6.5, or 4–3–3–3, does not invite; other eights may invite. Test the response to 1NT on representative hands.
- [x] Add definite-strength responses after a Stayman shortage answer: revalue opener's honors in the shown short suit, sign off at game or ask keycards at the upper end, and start a control cue in the middle band. The middle cue's later follow-up remains separate. Test spade- and heart-trump cases.
- [x] Apply the later G015 clarification: with a seven-card minor, four-card major, and 7–8 whole-hand effective points, use Stayman, then four of a fitting major or five of the long minor.

## Stage 2: sampled-deal decisions and new continuations

- [ ] Replace remaining G010/G021/G023/G027/G030/G033 shape decisions with publicly constrained sampled-deal choices where the user requested simulation. Keep the reviewer's direct 5m and major-game calls available as candidates.
- [ ] Add G016's artificial 4♥ after `1NT–3♣–3♠`, establishing a spade slam try, and author its continuation without inferring the responder's three spades from public information.
- [ ] Complete invitation/cue continuations for G001/G013/G018/G022/G032 and re-run every G001–G033 representative deal with the current profile. Audit the resulting contracts and remaining blocks.

## Verification

- [x] Run the focused Daqiush and purpose tests after each deterministic rule.
- [ ] Replay the reviewed samples and compare auctions to the accepted calls.
- [ ] Run the broader backend suite, document any unrelated pre-existing failures, and update implementation states in the review JSON only for behavior actually verified.
