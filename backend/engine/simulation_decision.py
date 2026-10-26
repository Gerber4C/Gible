"""Information-safe sampled-deal decisions for explicitly authored auctions.

Only the actor's hand is fixed.  Every other hand comes from public auction
constraints; the actual Table partner and opponents never enter the solver.
"""

from __future__ import annotations

from hashlib import sha256
from types import SimpleNamespace

from .auction import Auction
from .cards import Hand
from .contract_evaluation import ContractTarget, compare_contract_targets
from .dds_adapter import calculate_available_table
from .deal_sampler import sample_deals
from .hand_quality import assess_quality, shapely_combined_effective_points
from .honor_quality import assess_honor_texture


MINOR_5422_AUCTION = ('1N', 'P', '3C', 'P', '3D', 'P', '4N', 'P')
TWO_MAJOR_SPADE_SLAM_AUCTION = ('1N', 'P', '2H', 'P', '2S', 'P',
                                '3H', 'P', '3S', 'P')
TWO_MAJOR_SPADE_SUPERACCEPTS = {
    ('1N', 'P', '2H', 'P', '2N', 'P'): 'H',
    ('1N', 'P', '2H', 'P', '3C', 'P'): 'C',
    ('1N', 'P', '2H', 'P', '3D', 'P'): 'D',
    ('1N', 'P', '2H', 'P', '3S', 'P'): None,
}
SAMPLE_COUNT = 20
MIN_GOOD_SAMPLES = 12


def is_minor_5422_decision(profile_id: str, auction: Auction) -> bool:
    return profile_id == 'daqiush_2over1' and auction.calls == MINOR_5422_AUCTION


def is_minor_major_74_decision(profile_id: str, auction: Auction, hand: Hand) -> bool:
    return (profile_id == 'daqiush_2over1'
            and auction.calls in (('1N', 'P', '2C', 'P', '2H', 'P'),
                                  ('1N', 'P', '2C', 'P', '2S', 'P'))
            and hand.length(auction.calls[4][-1]) == 4
            and hand.hcp >= 13 and assess_quality(hand)['kr_points'] >= 14
            and max(hand.length(suit) for suit in 'CD') >= 7)


def is_two_major_spade_slam_decision(profile_id: str, auction: Auction, hand: Hand) -> bool:
    return (profile_id == 'daqiush_2over1'
            and (auction.calls == TWO_MAJOR_SPADE_SLAM_AUCTION
                 or auction.calls in TWO_MAJOR_SPADE_SUPERACCEPTS)
            and min(hand.length('H'), hand.length('S')) >= 5
            and shapely_combined_effective_points(hand) >= 9)


def decide_two_major_spade_slam(profile, auction: Auction, hand: Hand) -> dict:
    """Use only the responder hand and publicly promised opener range/support."""
    if not is_two_major_spade_slam_decision(profile.id, auction, hand):
        raise ValueError('Expected the authored game-forcing two-major spade fit')
    actor = auction.actor_to_call
    partner = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[actor]
    superaccept = auction.calls in TWO_MAJOR_SPADE_SUPERACCEPTS
    shown_doubleton = TWO_MAJOR_SPADE_SUPERACCEPTS.get(auction.calls)
    min_lengths = {'S': 4 if superaccept else 3}
    max_lengths = {}
    if shown_doubleton:
        min_lengths[shown_doubleton] = 2
        max_lengths[shown_doubleton] = 2
    elif superaccept:
        max_lengths = {suit: (4 if suit == 'S' else 3) for suit in 'SHDC'}
        min_lengths.update({suit: (4 if suit == 'S' else 3) for suit in 'SHDC'})
    constraints = {partner: {'min_hcp': 16, 'max_hcp': 18,
                             'min_lengths': min_lengths, 'max_lengths': max_lengths}}
    sampled = sample_deals(actor, hand, public_constraints=constraints,
                           sample_count=72 if superaccept else 24,
                           seed=_seed(auction, hand),
                           max_attempts=90000, max_seconds=12.0)
    opening = next((item.definition for item in profile.named_evaluators
                    if item.id == 'opening_assessment'), None)
    if opening is None:
        raise ValueError('Profile lacks the public 1NT opening predicate')
    deals = tuple(deal for deal in sampled.deals
                  if opening(SimpleNamespace(hand=deal[partner],
                                             hand_quality=assess_quality(deal[partner])))['eligible']
                  and (not superaccept or
                       assess_honor_texture(deal[partner])['adjusted_hcp'] >= 16))
    if len(deals) < 8:
        raise ValueError(f'Only {len(deals)} sampled hands matched the public 1NT promise')
    estimates = compare_contract_targets(
        deals, (ContractTarget(4, 'S', partner), ContractTarget(6, 'S', partner)),
        solve_table=calculate_available_table)
    rates = {item.contract: item.completion_rate for item in estimates}
    vulnerable = _vulnerable(auction)
    def expected(contract):
        item = next(value for value in estimates if value.contract == contract)
        made = _binary_contract_score(contract, True, vulnerable)
        failed = _binary_contract_score(contract, False, vulnerable)
        return item.completion_rate * made + (1-item.completion_rate) * failed
    call = '4N' if expected('6S') > expected('4S') else '4S'
    return {'call': call, 'sample_count': len(deals),
            'seed': sampled.seed, 'attempts': sampled.attempts,
            'completion_rates': rates,
            'expected_scores': {s: expected(s) for s in ('4S', '6S')},
            'comparison': 'game and slam completion on the same publicly compatible deals'}


def decide_minor_major_74(profile, auction: Auction, hand: Hand) -> dict:
    """Compare six in a seven-card minor with six in a four-four major fit."""
    if not is_minor_major_74_decision(profile.id, auction, hand):
        raise ValueError('This simulation requires the authored seven-four Stayman position')
    actor = auction.actor_to_call
    partner = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[actor]
    major = auction.calls[4][-1]
    minor = max('CD', key=lambda suit: hand.length(suit))
    constraints = {partner: {
        'min_hcp': 14, 'max_hcp': 18,
        'min_lengths': {major: 4},
        'max_lengths': {'H': 3} if major == 'S' else {},
    }}
    sampled = sample_deals(actor, hand, public_constraints=constraints,
                           sample_count=60, seed=_seed(auction, hand),
                           max_attempts=50000, max_seconds=8.0)
    opening = next((item.definition for item in profile.named_evaluators
                    if item.id == 'opening_assessment'), None)
    if opening is None:
        raise ValueError('Profile lacks the public 1NT opening predicate')
    deals = tuple(deal for deal in sampled.deals
                  if opening(SimpleNamespace(hand=deal[partner],
                                             hand_quality=assess_quality(deal[partner])))['eligible'])
    if len(deals) < 8:
        raise ValueError(f'Only {len(deals)} sampled hands matched the public 1NT promise')
    estimates = compare_contract_targets(
        deals, (ContractTarget(6, minor, actor), ContractTarget(6, major, partner)),
        solve_table=calculate_available_table)
    rates = {item.contract: item.completion_rate for item in estimates}
    # An equal rate does not justify suppressing the known four-four major fit.
    use_minor = rates['6' + minor] > rates['6' + major]
    return {
        'call': '3' + minor if use_minor else '3' + ('S' if major == 'H' else 'H'),
        'sample_count': len(deals), 'attempts': sampled.attempts,
        'seed': sampled.seed, 'completion_rates': rates,
        'comparison': 'six-level completion on the same publicly compatible sampled deals',
    }


def _seed(auction: Auction, hand: Hand) -> int:
    serial = auction.canonical_key() + ':' + '.'.join(hand.holding(s) for s in 'SHDC')
    return int.from_bytes(sha256(serial.encode('ascii')).digest()[:8], 'big')


def _vulnerable(auction: Auction) -> bool:
    side = 'ns' if auction.actor_to_call in 'ns' else 'ew'
    return auction.vulnerability in ('both', side)


def _binary_contract_score(contract: str, made: bool, vulnerable: bool) -> int:
    """Duplicate score with one-down proxy on failure and no overtricks."""
    if not made:
        return -100 if vulnerable else -50
    level = int(contract[0])
    trick_score = level * 20
    game_bonus = 500 if vulnerable else 300
    slam_bonus = (750 if vulnerable else 500) if level == 6 else 0
    return trick_score + game_bonus + slam_bonus


def decide_minor_5422(auction: Auction, hand: Hand) -> dict:
    """Choose among 5m/6m by completion on sampled public-compatible deals."""
    if auction.calls != MINOR_5422_AUCTION:
        raise ValueError('Minor 5-4-2-2 simulation requires its authored 4NT auction')
    actor = auction.actor_to_call
    partner = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[actor]
    constraints = {partner: {
        'min_hcp': 14, 'max_hcp': 15,
        'min_lengths': {'S': 2, 'H': 2, 'C': 4, 'D': 4},
        'max_lengths': {'S': 2, 'H': 2, 'C': 5, 'D': 5},
    }}
    sampled = sample_deals(actor, hand, public_constraints=constraints,
                           sample_count=SAMPLE_COUNT, seed=_seed(auction, hand),
                           max_attempts=50000, max_seconds=8.0)
    deals = tuple(deal for deal in sampled.deals if assess_quality(deal[partner])['good'])
    if len(deals) < MIN_GOOD_SAMPLES:
        raise ValueError(f'Only {len(deals)} sampled responder hands matched the public good-hand promise')
    targets = tuple(ContractTarget(level, suit, actor)
                    for level in (5, 6) for suit in 'CD')
    estimates = compare_contract_targets(deals, targets,
                                         solve_table=calculate_available_table)
    vulnerable = _vulnerable(auction)
    choices = []
    for estimate in estimates:
        made_score = _binary_contract_score(estimate.contract, True, vulnerable)
        failed_score = _binary_contract_score(estimate.contract, False, vulnerable)
        expected = (estimate.made * made_score
                    + (estimate.sample_count - estimate.made) * failed_score)
        choices.append((expected, -int(estimate.contract[0]),
                        hand.length(estimate.contract[1]), estimate.contract,
                        estimate.completion_rate))
    best = max(choices)
    return {
        'call': best[3], 'sample_count': len(deals),
        'attempts': sampled.attempts, 'seed': sampled.seed,
        'completion_rates': {item.contract: item.completion_rate for item in estimates},
        'expected_scores': {choice[3]: choice[0] / len(deals) for choice in choices},
        'scoring': 'duplicate, no overtricks, one-down failure proxy',
    }
