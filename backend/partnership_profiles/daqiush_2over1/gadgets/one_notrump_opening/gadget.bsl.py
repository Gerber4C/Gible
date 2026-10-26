# Author-approved initial cutoffs (2026-10-22); tune against further examples.
# Pure K-R and the HCP discount model are separate evaluations.
OPENING_LIMITS = {
    'upgrade_14_min_kr': 15.0,
    'five_major_17_max_kr_exclusive': 17.0,
    'five_major_four_minor_22_max_delta': -1.5,
    'five_major_four_minor_31_max_delta': -0.5,
    'soft_18_max_kr': 16.0,
}


def opening_assessment(ctx):
    if ctx.hand is None:
        return {'eligible': False, 'reasons': ['hand_unavailable']}
    hand = ctx.hand
    quality = ctx.hand_quality
    lengths = {suit: hand.length(suit) for suit in 'SHDC'}
    shape = sorted(lengths.values(), reverse=True)
    reasons = []
    soft_18 = (hand.hcp == 18 and shape == [4, 4, 3, 2]
               and any(hand.length(suit) == 2 and set(hand.holding(suit)) == {'Q', 'J'}
                       for suit in 'SHDC')
               and quality['kr_points'] <= OPENING_LIMITS['soft_18_max_kr'])
    if not 14 <= hand.hcp <= 17 and not soft_18:
        reasons.append('hcp_range')
    allowed_shapes = ([4, 3, 3, 3], [4, 4, 3, 2], [5, 3, 3, 2],
                      [6, 3, 2, 2], [5, 4, 2, 2], [4, 4, 4, 1], [5, 4, 3, 1])
    if shape not in allowed_shapes or max(lengths['S'], lengths['H']) >= 6:
        reasons.append('shape')
    if max(lengths['S'], lengths['H']) >= 5 and min(lengths['S'], lengths['H']) >= 4:
        reasons.append('two_majors')
    if any(lengths[suit] == 1 and hand.holding(suit) not in ('A', 'K', 'Q') for suit in 'SHDC'):
        reasons.append('singleton')
    if hand.hcp == 14:
        if shape != [5, 3, 3, 2]:
            reasons.append('upgrade_shape')
        if quality['kr_points'] < OPENING_LIMITS['upgrade_14_min_kr']:
            reasons.append('upgrade_quality')
    five_major = max(lengths['S'], lengths['H']) == 5
    four_minor = max(lengths['D'], lengths['C']) == 4
    if five_major and hand.hcp == 17 and quality['kr_points'] >= OPENING_LIMITS['five_major_17_max_kr_exclusive']:
        reasons.append('five_major_upper_quality')
    if five_major and four_minor:
        if shape == [5, 4, 2, 2] and quality['kr_delta'] > OPENING_LIMITS['five_major_four_minor_22_max_delta']:
            reasons.append('five_major_four_minor_not_very_soft')
        if shape == [5, 4, 3, 1] and quality['kr_delta'] > OPENING_LIMITS['five_major_four_minor_31_max_delta']:
            reasons.append('five_major_four_minor_singleton_not_soft')
    return {
        'eligible': not reasons, 'reasons': reasons,
        'hcp': hand.hcp, 'kr_points': quality['kr_points'],
        'kr_delta': quality['kr_delta'], 'lengths': lengths,
        'limits': dict(OPENING_LIMITS),
    }


def opens_one_notrump(ctx):
    return opening_assessment(ctx)['eligible']


def absolute_maximum(ctx, trump):
    # Only meaningful with an explicitly supplied agreed trump. Unsupported
    # lengths are unknown, not a negative classification.
    if ctx.hand is None:
        return None
    thresholds = {4: 16, 5: 15}
    threshold = thresholds.get(ctx.hand.length(trump))
    if threshold is None:
        return None
    return ctx.honor_texture['adjusted_hcp'] >= threshold


def maximum_hearts(ctx):
    return absolute_maximum(ctx, 'H')


def maximum_spades(ctx):
    return absolute_maximum(ctx, 'S')


class DaqiushOneNotrumpOpening(Gadget):
    id = 'one_notrump_opening'
    namespace = 'daqiush_2over1'
    name = 'Daqiush 1NT opening'
    version = '0.1.0'
    author = Author('Daqiush')

    def build(self):
        self.evaluator('opening_assessment', opening_assessment)
        self.evaluator('absolute_maximum_H', maximum_hearts)
        self.evaluator('absolute_maximum_S', maximum_spades)
        call = self.call('open_1nt')
        call.seats = [1, 2, 3, 4]
        call.bid = '1N'
        call.applies = opens_one_notrump
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'context_initiating']
        call.meaning.action = 'opening'
        call.meaning.target_suit = 'N'
        call.meaning.hcp_min = 14
        call.meaning.hcp_max = 18
        call.meaning.shape_class = 'daqiush_notrump'
        # Machine-readable public promise used when sampling unseen hands.
        call.meaning.public_evidence = {
            'evaluator': 'opening_assessment', 'truth_key': 'eligible',
            'bounds': {'min_hcp': 14, 'max_hcp': 18},
        }
        effect = call.effect('notrump_opening')
        effect.actor_role = 'opener'
        effect.target_suit = 'N'
        effect.hcp_min = 14
        effect.hcp_max = 18
        effect.shape_class = 'daqiush_notrump'
        call.effect('notrump_focus').status = 'active'
        call.description = 'Opens 1NT with the approved Daqiush shape and K-R criteria.'
        call.system_notes = 'Normally 15–17 HCP, with qualifying 14-point 5332 upgrades and very soft 18-point 4432 with QJ doubleton and K-R at most 16.0; may contain five-card majors, six-card minors or a singleton Q/K/A in permitted shapes. Not restricted to balanced hands.'
