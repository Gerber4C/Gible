"""Reusable honor evidence; classification thresholds belong to profiles.

The Q/J discount model was supplied by the Daqiush author. It starts from HCP,
not K-R. Singleton deductions and a universal hard/soft cutoff are unspecified.
No actual partner or opponent hand is accepted.
"""

from .cards import Hand


def assess_honor_texture(hand: Hand) -> dict:
    suits = {}
    for suit in 'SHDC':
        holding = hand.holding(suit)
        honors = ''.join(rank for rank in 'AKQJ' if rank in holding)
        deductions = []
        for rank, higher in [('Q', 'AK'), ('J', 'AKQ')]:
            if rank not in holding:
                continue
            if len(holding) == 2:
                deductions.append({'rank': rank, 'points': 1.5 if rank == 'Q' else 1.0,
                                   'reason': 'doubleton'})
            elif len(holding) >= 3 and not any(card in holding for card in higher):
                deductions.append({'rank': rank, 'points': .5,
                                   'reason': 'no_higher_honor'})
        suits[suit] = {
            'holding': holding, 'length': len(holding), 'honors': honors,
            'ak_count': sum(rank in holding for rank in 'AK'),
            'qj_count': sum(rank in holding for rank in 'QJ'),
            'deductions': deductions,
            'deduction': sum(item['points'] for item in deductions),
        }
    deduction = sum(item['deduction'] for item in suits.values())
    return {
        'model': 'daqiush_qj_discount_v1',
        'hcp': hand.hcp,
        'ak_count': sum(item['ak_count'] for item in suits.values()),
        'qj_count': sum(item['qj_count'] for item in suits.values()),
        'suits': suits,
        'deduction': deduction,
        'adjusted_hcp': hand.hcp - deduction,
    }
