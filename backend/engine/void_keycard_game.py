"""Reactive game-tree choice for ordinary-RKCB void answers.

After a 5NT/6X useful-void answer the asker should not blindly place a final
contract when an invitation is available.  This adapter feeds the legal
candidate calls, sampled partner hands, and legal partner reactions into
``choose_reactive_continuation``, scoring each final contract with DDS.
"""

from __future__ import annotations

from .auction import Auction
from .cards import Hand
from .contract_evaluation import ContractTarget, compare_contract_targets
from .dds_adapter import calculate_available_table
from .keycard_game_tree import choose_reactive_continuation
from .legality import legal_calls
from .rkcb_continuation import ordinary_rkcb_frame, partner_of_last_bidder


def is_void_keycard_continuation(profile_id: str, auction: Auction,
                                 trace, hand: Hand | None) -> bool:
    if profile_id != 'daqiush_2over1' or hand is None or trace is None:
        return False
    if auction.actor_to_call != partner_of_last_bidder(auction):
        return False
    frame = ordinary_rkcb_frame(trace)
    if frame is None or frame.status != 'answered':
        return False
    return (frame.answer_call in ('5N', '6C', '6D', '6H', '6S')
            and (frame.useful_void is not None
                 or frame.useful_void_category in ('unspecified',
                                                   'higher_than_trump')))


def choose_void_keycard_continuation(
    profile, auction: Auction, trace, hand: Hand,
    candidate_calls,
) -> dict | None:
    """Return the best first call while preserving partner reaction branches."""
    from .cue_slam_policy import sample_process_hands

    frame = ordinary_rkcb_frame(trace)
    if frame is None or frame.status != 'answered':
        return None
    actor = auction.actor_to_call
    partner = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[actor]
    deals = sample_process_hands(profile, auction, trace, hand, partner)
    if not deals:
        return None
    final_calls = {'6C', '6D', '6H', '6S', '6N', '7C', '7D', '7H', '7S', '7N'}
    candidates = tuple(
        call for call in candidate_calls
        if call in final_calls or call in ('6C', '6D', '6H', '6S', '6N'))
    if not candidates:
        return None
    vulnerable = auction.vulnerability in (
        'both', 'ns' if actor in 'ns' else 'ew')

    def responses(candidate, deal):
        next_auction = Auction(
            calls=auction.calls + (candidate,),
            dealer=auction.dealer, vulnerability=auction.vulnerability)
        legal = set(legal_calls(next_auction))
        result = []
        if 'P' in legal:
            result.append('P')
        result.extend(call for call in final_calls if call in legal)
        return tuple(result)

    def final_contract(candidate, response, deal):
        if response == 'P':
            return candidate if candidate in final_calls else None
        return response if response in final_calls else None

    score_cache = {}

    def score(contract, deal):
        key = (contract, id(deal))
        if key in score_cache:
            return score_cache[key]
        level = int(contract[0])
        strain = 'NT' if contract.endswith('N') else contract[1]
        target = ContractTarget(level, strain, actor)
        estimate = compare_contract_targets(
            (deal,), (target,), solve_table=calculate_available_table)[0]
        made = _made_score(contract, vulnerable)
        down = -100 if vulnerable else -50
        value = estimate.completion_rate * made + (1 - estimate.completion_rate) * down
        score_cache[key] = value
        return value

    result = choose_reactive_continuation(
        candidates, deals, responses=responses,
        final_contract=final_contract, score=score)
    if result is None:
        return None
    return {
        'call': result.call,
        'expected_score': result.expected_score,
        'sample_count': len(deals),
        'reactions': [
            {'partner': 'sample', 'response': response, 'final': final}
            for _, response, final in result.reactions
        ],
    }


def _made_score(contract: str, vulnerable: bool) -> int:
    level = int(contract[0])
    if contract.endswith('N'):
        base = 40 + 30 * (level - 1) if level == 1 else 30 * level
        game = 500 if vulnerable else 300
        slam = (750 if vulnerable else 500) if level == 6 else (
            1500 if vulnerable else 1000) if level == 7 else 0
        return base + game + slam
    base = 20 * level
    game = 500 if vulnerable else 300
    slam = (750 if vulnerable else 500) if level == 6 else (
        1500 if vulnerable else 1000) if level == 7 else 0
    return base + game + slam
