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


@dataclass(frozen=True)
class AmbiguousDecision:
    call: str | None
    reason: str
    unavailable: bool = False


def compare_ambiguous_continuations(profile, auction, trace, hand: Hand,
                                    frame, calls, *, deals=None,
                                    evaluator=None, solve=None,
                                    ) -> AmbiguousDecision:
    """Compare the exposed continuations over a category-consistent mixture.

    ``calls`` must already be the authored, legal continuation set. A single
    exposed call is a deterministic result and never reaches the solver.
    """
    from .legality import legal_calls

    legal = set(legal_calls(auction))
    exposed = tuple(call for call in calls if call in legal)
    if not exposed:
        return AmbiguousDecision(None, 'no exposed continuation is legal',
                                 unavailable=True)
    if len(exposed) == 1:
        return AmbiguousDecision(exposed[0], 'only one continuation is exposed')
    if evaluator is not None:
        try:
            selected = evaluator(exposed)
        except (DDSUnavailableError, RuntimeError, ValueError, TypeError) as exc:
            return AmbiguousDecision(None, f'ambiguous comparison unavailable: {exc}',
                                     unavailable=True)
        if selected in exposed:
            return AmbiguousDecision(selected, 'injected mixture comparison')
        return AmbiguousDecision(None, 'comparison returned an unexpected call',
                                 unavailable=True)
    if deals is None:
        if profile is None:
            return AmbiguousDecision(None, 'ambiguous comparison needs samples',
                                     unavailable=True)
        try:
            deals = _sample_answer_deals(profile, auction, trace, hand, frame,
                                         frame.trump)
        except (DDSUnavailableError, RuntimeError, ValueError) as exc:
            return AmbiguousDecision(None, f'ambiguous comparison unavailable: {exc}',
                                     unavailable=True)
    if not deals:
        return AmbiguousDecision(None, 'no sampled hands match the answer category',
                                 unavailable=True)
    actor = auction.actor_to_call
    partner = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[actor]
    targets = tuple(_target_for_call(call, frame.trump, actor, partner)
                    for call in exposed)
    try:
        estimates = compare_contract_targets(
            deals, targets, solve_table=solve or calculate_available_table)
    except (DDSUnavailableError, RuntimeError, ValueError, TypeError) as exc:
        return AmbiguousDecision(None, f'ambiguous comparison unavailable: {exc}',
                                 unavailable=True)
    vulnerable = _vulnerable(auction, actor)
    scored = [((estimate.completion_rate,
                _expected_contract_score(estimate, vulnerable)),
               estimate.contract)
              for estimate in estimates]
    scored.sort(key=lambda item: item[0], reverse=True)
    best = scored[0][1]
    selected = next(call for call, target in zip(exposed, targets)
                    if target.contract == best)
    if len(scored) > 1 and scored[0][0] == scored[1][0] and 'P' in exposed:
        selected = 'P'
    return AmbiguousDecision(selected, 'sampled mixture comparison')


def _sample_answer_deals(profile, auction, trace, hand, frame, trump):
    from .cue_slam_policy import sample_process_hands
    from .rkcb_continuation import answer_category_filter

    actor = auction.actor_to_call
    partner = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[actor]
    return sample_process_hands(
        profile, auction, trace, hand, partner,
        extra_filter=answer_category_filter(frame, trump))


def _target_for_call(call: str, trump: str, actor: str, partner: str):
    if call == 'P':
        return ContractTarget(5, 'NT', partner)
    level = int(call[0])
    suit = call[-1]
    strain = suit if suit in 'CDHS' else 'NT'
    return ContractTarget(level, strain, actor)


def _expected_contract_score(estimate, vulnerable: bool) -> float:
    level = int(estimate.contract[0])
    if estimate.contract.endswith('NT'):
        made = 330 if not vulnerable else 460
    else:
        major = 30 if estimate.contract[-1] in 'HS' else 20
        made = level * major + (500 if vulnerable else 300)
        if level == 6:
            made += 750 if vulnerable else 500
        elif level == 7:
            made += 1500 if vulnerable else 1000
    down = -100 if vulnerable else -50
    return estimate.completion_rate * made + (1 - estimate.completion_rate) * down


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
