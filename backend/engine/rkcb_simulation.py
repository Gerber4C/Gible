"""Narrow sampled decisions for ordinary-RKCB continuations.

The deterministic legality checks live in ``rkcb_continuation``. This module
only compares two already-legal routes over sampled partner hands and never
invents a call. Every public-facing function returns a typed unavailable result
when sampling or DDS is missing, so the caller can choose a deterministic
fallback or TD.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from .cards import Hand
from .contract_evaluation import ContractTarget, compare_contract_targets
from .dds_adapter import DDSUnavailableError, calculate_available_table
from .legality import is_call_legal


@dataclass(frozen=True)
class RescueDecision:
    call: str | None
    reason: str
    unavailable: bool = False


def compare_rescue_routes(profile, auction, trace, hand: Hand, trump: str,
                          frame, *, evaluator: Callable[..., str] | None = None,
                          ) -> RescueDecision:
    """Choose between the 5S->5NT rescue and a direct six-trump placement."""
    relay = '5S'
    fallback = f'6{trump}'
    relay_legal = is_call_legal(auction, relay)
    fallback_legal = is_call_legal(auction, fallback)
    if not relay_legal and not fallback_legal:
        return RescueDecision(None, 'neither the relay nor six of trumps is legal',
                              unavailable=True)
    if not relay_legal:
        return RescueDecision(fallback, 'only six of trumps is legal')
    if not fallback_legal:
        return RescueDecision(relay, 'only the five-spade relay is legal')
    if profile is None and evaluator is None:
        return RescueDecision(
            None, 'rescue comparison needs a profile for sampling',
            unavailable=True)
    try:
        selected = ((evaluator or _default_evaluator)(
            profile, auction, trace, hand, trump, frame))
    except (DDSUnavailableError, RuntimeError, ValueError, TypeError) as exc:
        return RescueDecision(
            None, f'rescue comparison unavailable: {exc}', unavailable=True)
    if selected not in (relay, fallback):
        return RescueDecision(
            None, f'rescue comparison returned an unexpected call: {selected}',
            unavailable=True)
    return RescueDecision(selected, 'sampled contract comparison')


def _default_evaluator(profile, auction, trace, hand: Hand, trump: str,
                       frame) -> str:
    from .cue_slam_policy import sample_process_hands

    actor = auction.actor_to_call
    partner = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[actor]
    deals = sample_process_hands(profile, auction, trace, hand, partner)
    if not deals:
        raise ValueError('no sampled partner hands satisfy the auction')
    targets = (ContractTarget(5, 'NT', partner),
               ContractTarget(6, trump, actor))
    estimates = compare_contract_targets(deals, targets,
                                         solve_table=calculate_available_table)
    vulnerable = _vulnerable(auction, actor)
    expected = {
        estimate.contract: _expected_score(estimate, vulnerable,
                                           trump=trump)
        for estimate in estimates
    }
    return '5S' if expected['5NT'] >= expected['6' + trump] else '6' + trump


def _vulnerable(auction, seat: str) -> bool:
    side = 'ns' if seat in 'ns' else 'ew'
    return auction.vulnerability in ('both', side)


def _expected_score(estimate, vulnerable: bool, *, trump: str) -> float:
    level = int(estimate.contract[0])
    if estimate.contract == '5NT':
        made = 330 if not vulnerable else 460
    else:
        major = 30 if trump in 'HS' else 20
        game_bonus = 500 if vulnerable else 300
        slam_bonus = 750 if vulnerable else 500
        made = level * major + game_bonus + slam_bonus
    down = -100 if vulnerable else -50
    return estimate.completion_rate * made + (1 - estimate.completion_rate) * down
