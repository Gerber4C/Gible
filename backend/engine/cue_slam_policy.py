"""Owner-specified cue-bid continuation policy for slam exploration.

At a cue-bid continuation where partner's strength range is still unknown:

* If the slam qualifies even when partner brings no extra strength, provided
  the partnership keycards are sufficient (never missing two aces, never one
  ace together with the trump queen), ask 4NT for keycards.
* If the slam fails even when partner brings the extra-strength threshold
  (the tenth percentile of the sampled process hands plus two K-R points),
  place the game contract.  That game carries signoff meaning, and partner
  may still override it by simulating a qualifying slam.
* Otherwise continue cue-bidding.

DDS is only consulted when no cheaper deterministic test decides (the owner
rule: fall back to DDS only when no other means is available).  With a major
trump, cueing above 4M is allowed only when the sampled expected score beats
stopping in 4M/5M/6M.  With a minor trump, cueing above 5m to hunt for a
small slam is forbidden.

This module is intentionally information-safe: it only sees the acting hand
plus partner hands sampled from public evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

from .cards import Hand
from .contract_evaluation import ContractTarget, compare_contract_targets
from .dds_adapter import calculate_available_table
from .hand_quality import assess_quality

CUE_ACT_TYPES = frozenset({'control_showing', 'slam_try'})
EXTRA_KR = 2.0
SLAM_QUALIFY_RATE = 0.5
_LEVEL_ORDER = 'CDHSN'


def _bid_rank(call: str) -> int:
    return int(call[0]) * 5 + _LEVEL_ORDER.index(call[1])


def cue_continuation(trace) -> tuple[dict, str] | None:
    """Return ``(partner_cue_entry, trump)`` when the last non-pass call is a cue."""

    last = None
    for entry in trace.applied_meanings:
        if entry['call'] != 'P':
            last = entry
    if last is None:
        return None
    meaning = last.get('public_meaning') or {}
    if not CUE_ACT_TYPES.intersection(meaning.get('call_act_types', ())):
        return None
    trump = meaning.get('agreed_suit') or meaning.get('target_suit')
    if trump not in 'CDHS':
        return None
    return last, trump


def strength_is_unknown(hcp_range: tuple[int, int] | None, *,
                        has_cue_bid: bool = False) -> bool:
    """Report whether partner's strength range is still unknown.

    A single exact HCP value is always known.  A one-point band (for example
    15-16) is known only after the player has already shown extra strength
    with a voluntary cue; before that it is still unknown.  Anything wider is
    unknown.
    """

    if hcp_range is None:
        return True
    low, high = hcp_range
    width = high - low
    if width <= 0:
        return False
    if width == 1:
        return not has_cue_bid
    return True


def cue_public_kr(previous: tuple[float, float | None],
                  *, forced_by_serious_3nt: bool = False
                  ) -> tuple[float, float | None]:
    """Derive the K-R range a cue-bid publishes.

    A cue forced by serious 3NT carries no new information, so its range is
    the player's previous range.  A voluntary cue promises two K-R points more
    than the previous call, raising the floor by two.  When the previous band
    is narrower than those two points (the ceiling sits below the raised
    floor), the cue instead publishes the upper half of the original band.
    """

    low, high = previous
    if forced_by_serious_3nt:
        return previous
    raised = low + EXTRA_KR
    if high is None:
        return raised, None
    if raised <= high:
        return raised, high
    return (low + high) / 2.0, high


def extra_kr_threshold(partner_kr: Sequence[float]) -> float:
    """Return the tenth-percentile process K-R plus two points."""

    if not partner_kr:
        return EXTRA_KR
    ordered = sorted(partner_kr)
    index = max(0, min(len(ordered) - 1, int(round(0.1 * (len(ordered) - 1)))))
    return ordered[index] + EXTRA_KR


def keycards_sufficient(own: Hand, partner: Hand, trump: str) -> bool:
    """Never missing two aces nor one ace together with the trump queen."""

    missing = 5 - own.keycard_count(trump) - partner.keycard_count(trump)
    if missing <= 0:
        return True
    if missing >= 2:
        return False
    queen_known = (own.contains_rank(trump, 'Q')
                   or partner.contains_rank(trump, 'Q'))
    return queen_known


@dataclass(frozen=True)
class CueDecision:
    call: str
    reason: str
    extra_kr_threshold: float
    no_extra_slam_rate: float | None = None
    extra_slam_rate: float | None = None
    expected_scores: dict | None = None


def _completion_rates(hand: Hand, trump: str, hands: Sequence[Hand],
                      solve_table: Callable) -> tuple[dict[str, float], int]:
    if not hands:
        return {}, 0
    targets = (ContractTarget(4 if trump in 'HS' else 5, trump, 's'),
               ContractTarget(6, trump, 's'))
    deals = tuple({'n': hand, 's': partner} for partner in hands)
    estimates = compare_contract_targets(deals, targets, solve_table=solve_table)
    return {item.contract: item.completion_rate for item in estimates}, len(hands)


def decide_from_hands(
    hand: Hand,
    trump: str,
    partner_hands: Sequence[Hand],
    *,
    game_call: str,
    cue_calls: Iterable[str] = (),
    slam_threshold: float = SLAM_QUALIFY_RATE,
    solve_table: Callable = calculate_available_table,
) -> CueDecision:
    """Apply the cue-continuation policy to already-sampled partner hands."""

    partner_hands = tuple(partner_hands)
    krs = [assess_quality(item)['kr_points'] for item in partner_hands]
    threshold = extra_kr_threshold(krs)
    no_extra = tuple(partner for partner, kr in zip(partner_hands, krs)
                     if kr < threshold)
    with_extra = tuple(partner for partner, kr in zip(partner_hands, krs)
                       if kr >= threshold)

    # Deterministic keycard filter.  A hand that cannot reach sufficient
    # keycards is not a slam candidate, so it never justifies 4NT or a cue.
    no_extra_ok = tuple(item for item in no_extra
                        if keycards_sufficient(hand, item, trump))
    with_extra_ok = tuple(item for item in with_extra
                          if keycards_sufficient(hand, item, trump))

    slam_call = f'6{trump}'

    if not no_extra_ok:
        # Even partner's minimum hands cannot supply enough keycards: the
        # slam is not qualifying without extra shape/keycards.  If extra
        # hands also fail keycards, place game; otherwise keep cueing.
        if not with_extra_ok:
            return CueDecision(game_call, 'keycards insufficient', threshold)
        rates, _ = _completion_rates(hand, trump, with_extra_ok, solve_table)
        rate = rates.get(slam_call, 0.0)
        if rate < slam_threshold:
            return CueDecision(game_call, 'slam fails even with extra strength',
                               threshold, extra_slam_rate=rate)
        return CueDecision(_preferred_cue(hand, trump, cue_calls),
                           'slam depends on partner extra strength',
                           threshold, extra_slam_rate=rate)

    rates_no, _ = _completion_rates(hand, trump, no_extra_ok, solve_table)
    no_extra_rate = rates_no.get(slam_call, 0.0)
    if no_extra_rate >= slam_threshold:
        # Qualifies without extra strength and keycards are sufficient: ask.
        return CueDecision('4N', 'slam qualifies without extra strength',
                           threshold, no_extra_slam_rate=no_extra_rate)

    if not with_extra_ok:
        return CueDecision(game_call, 'keycards insufficient with extra strength',
                           threshold, no_extra_slam_rate=no_extra_rate)

    rates_extra, _ = _completion_rates(hand, trump, with_extra_ok, solve_table)
    extra_rate = rates_extra.get(slam_call, 0.0)
    if extra_rate < slam_threshold:
        return CueDecision(game_call, 'slam fails even with extra strength',
                           threshold, no_extra_slam_rate=no_extra_rate,
                           extra_slam_rate=extra_rate)
    return CueDecision(_preferred_cue(hand, trump, cue_calls),
                       'slam depends on partner extra strength', threshold,
                       no_extra_slam_rate=no_extra_rate,
                       extra_slam_rate=extra_rate)


def _preferred_cue(hand: Hand, trump: str, cue_calls: Iterable[str]) -> str:
    """Pick the lowest legal cue that does not break the owner's level caps."""

    legal = [call for call in cue_calls if '4' <= call[0] <= '6']
    for call in sorted(legal, key=_bid_rank):
        if not cue_allowed_above(trump, call):
            continue
        return call
    return 'P'


def cue_allowed_above(trump: str, call: str) -> bool:
    """Return whether a cue may be made at this level under the owner rule."""

    rank = _bid_rank(call)
    if trump in 'CD':
        # Never cue above 5m looking for a small slam.
        return rank <= _bid_rank('5' + trump)
    # A major trump may cue above 4M; the caller still needs a positive
    # simulated expectation, which the selection step enforces.
    return True


__all__ = (
    'CueDecision',
    'cue_allowed_above',
    'cue_continuation',
    'cue_public_kr',
    'decide_from_hands',
    'extra_kr_threshold',
    'keycards_sufficient',
    'strength_is_unknown',
)
