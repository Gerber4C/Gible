import unittest
from types import SimpleNamespace
from unittest.mock import patch

from engine import cue_slam_policy as policy
from engine.cards import Hand


class CuePolicyHelperTests(unittest.TestCase):
    def test_strength_range_width(self):
        # A single exact value is always known.
        self.assertFalse(policy.strength_is_unknown((15, 15)))
        # A plain 15-16 band is still unknown until a voluntary cue shows extra.
        self.assertTrue(policy.strength_is_unknown((15, 16)))
        self.assertFalse(policy.strength_is_unknown((15, 16), has_cue_bid=True))
        self.assertTrue(policy.strength_is_unknown((14, 18)))
        self.assertTrue(policy.strength_is_unknown(None))

    def test_cue_public_kr(self):
        # A voluntary cue promises two more K-R points than the prior call.
        self.assertEqual(policy.cue_public_kr((9.0, 12.0)), (11.0, 12.0))
        self.assertEqual(policy.cue_public_kr((9.0, None)), (11.0, None))
        # A band narrower than two points cannot rise by two, so the cue
        # publishes the upper half of the original band.
        self.assertEqual(policy.cue_public_kr((11.0, 12.0)), (11.5, 12.0))
        self.assertEqual(policy.cue_public_kr((11.5, 12.0)), (11.75, 12.0))
        # A cue forced by serious 3NT carries no new information.
        self.assertEqual(
            policy.cue_public_kr((9.0, 12.0), forced_by_serious_3nt=True),
            (9.0, 12.0))

    def test_extra_kr_threshold_is_tenth_percentile_plus_two(self):
        krs = [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
        # round(0.1 * 9) == 1 -> sorted[1] == 11, plus two.
        self.assertEqual(policy.extra_kr_threshold(krs), 13.0)
        self.assertEqual(policy.extra_kr_threshold([]), 2.0)

    def test_cue_level_caps(self):
        # For a minor trump, side cues above 5m are forbidden; 5m itself is
        # the trump level, not a cue.
        self.assertTrue(policy.cue_allowed_above('D', '5D'))
        self.assertFalse(policy.cue_allowed_above('D', '5H'))
        self.assertFalse(policy.cue_allowed_above('D', '5S'))
        self.assertFalse(policy.cue_allowed_above('C', '5D'))
        self.assertTrue(policy.cue_allowed_above('C', '5C'))
        self.assertTrue(policy.cue_allowed_above('H', '5C'))
        self.assertTrue(policy.cue_allowed_above('S', '5D'))

    def test_keycards_sufficient(self):
        trump = 'S'
        # Own holds two keycards (spade ace, club ace) and the spade queen.
        own_with_queen = Hand.parse('SAQ82HQJ72DKCA965')
        own_without_queen = Hand.parse('SA832HQJ72DKCA965')
        partner_three = Hand.parse('SK43HA65DA54C5432')   # AS? no: A H, A D, K S
        partner_two = Hand.parse('SK43HA65DQ54C5432')     # A H, K S
        partner_one = Hand.parse('SK43HQ65DQ54C5432')     # K S

        self.assertTrue(policy.keycards_sufficient(
            own_with_queen, partner_three, trump))
        self.assertTrue(policy.keycards_sufficient(
            own_with_queen, partner_two, trump))
        self.assertFalse(policy.keycards_sufficient(
            own_with_queen, partner_one, trump))
        # One keycard missing but the trump queen is unseen and unpromised.
        self.assertFalse(policy.keycards_sufficient(
            own_without_queen, partner_two, trump))

    def test_cue_continuation_detects_partner_cue(self):
        trace = SimpleNamespace(applied_meanings=(
            {'call': 'P', 'public_meaning': {}},
            {'call': '4D', 'seat': 's', 'public_meaning': {
                'call_act_types': ['slam_try', 'game_forcing'],
                'agreed_suit': 'S'}},
        ))
        entry, trump = policy.cue_continuation(trace)
        self.assertEqual(trump, 'S')
        self.assertEqual(entry['call'], '4D')

        plain = SimpleNamespace(applied_meanings=(
            {'call': '4S', 'seat': 's', 'public_meaning': {
                'call_act_types': ['signoff'], 'agreed_suit': 'S'}},
        ))
        self.assertIsNone(policy.cue_continuation(plain))
        # A cue with no agreed suit must not crash the `in` membership test.
        suitless = SimpleNamespace(applied_meanings=(
            {'call': '4D', 'seat': 's', 'public_meaning': {
                'call_act_types': ['slam_try']}},
        ))
        self.assertIsNone(policy.cue_continuation(suitless))


    def test_partner_hcp_bounds(self):
        trace = SimpleNamespace(applied_meanings=(
            {'seat': 'n', 'call': '1N',
             'public_meaning': {'hcp_min': 14, 'hcp_max': 18}},
            {'seat': 's', 'call': '2C', 'public_meaning': {}},
            {'seat': 's', 'call': '4D',
             'public_meaning': {'call_act_types': ['slam_try']}},
        ))
        self.assertEqual(policy.partner_hcp_bounds(trace, 'n'), (14, 18))
        self.assertEqual(policy.partner_hcp_bounds(trace, 's'), (0, 37))

    def test_sample_process_hands_keeps_only_observed_bidders(self):
        from engine.auction import Auction
        actor = Hand.parse('SAQ82HQJ72DKCA965')
        kept = Hand.parse('S5432H5432D5432C5')
        dropped = Hand.parse('SAKQH432D432C5432')
        auction = Auction.parse('1NP2CP2SP4DP')
        trace = SimpleNamespace(applied_meanings=(
            {'seat': 'n', 'call': '1N',
             'public_meaning': {'hcp_min': 14, 'hcp_max': 18}},
            {'seat': 's', 'call': '2C', 'public_meaning': {}},
            {'seat': 's', 'call': '4D',
             'public_meaning': {'call_act_types': ['slam_try']}},
        ))
        kept_deal = {'n': actor, 's': kept}
        dropped_deal = {'n': actor, 's': dropped}
        sampled = SimpleNamespace(
            deals=(kept_deal, dropped_deal), attempts=2, seed=0)

        def fake_candidates(profile, prefix, hand, trace, env, memory):
            calls = [SimpleNamespace(call='2C')]
            if hand is kept:
                calls.append(SimpleNamespace(call='4D'))
            return tuple(calls)

        with patch('engine.deal_sampler.sample_deals', return_value=sampled), \
             patch('engine.replay.replay_auction', return_value=None), \
             patch('engine.replay.active_environment_for', return_value=None), \
             patch('engine.candidate_generation.generate_candidates',
                   side_effect=fake_candidates):
            deals = policy.sample_process_hands(
                SimpleNamespace(), auction, trace, actor, 's',
                partner_count=1, ew_count=1)
        self.assertEqual(len(deals), 1)
        self.assertIs(deals[0]['s'], kept)
        self.assertEqual(set(deals[0]), {'n', 'e', 's', 'w'})


    def test_cue_three_way_requires_unknown_range(self):
        from engine.auction import Auction
        auction = Auction.parse('1NP2CP2SP4DP')
        wide = SimpleNamespace(applied_meanings=(
            {'seat': 'n', 'call': '1N',
             'public_meaning': {'hcp_min': 14, 'hcp_max': 18}},
            {'seat': 's', 'call': '2C', 'public_meaning': {}},
            {'seat': 's', 'call': '4D', 'public_meaning': {
                'call_act_types': ['slam_try'], 'agreed_suit': 'S'}},
        ))
        self.assertEqual(policy.cue_three_way(auction, wide), ('S', 's'))
        # Partner pinned to exactly 15 HCP: strength is known, so no override.
        pinned = SimpleNamespace(applied_meanings=(
            {'seat': 's', 'call': '2C',
             'public_meaning': {'hcp_min': 15, 'hcp_max': 15}},
            {'seat': 's', 'call': '4D', 'public_meaning': {
                'call_act_types': ['slam_try'], 'agreed_suit': 'S'}},
        ))
        self.assertIsNone(policy.cue_three_way(auction, pinned))


    def test_partner_promised_kr(self):
        trace = SimpleNamespace(applied_meanings=(
            {'seat': 's', 'call': '4D', 'public_meaning': {'min_kr': 14.0}},
        ))
        self.assertEqual(policy.partner_promised_kr(trace, 's'), 14.0)
        self.assertIsNone(policy.partner_promised_kr(trace, 'n'))

    def test_signoff_override_detection(self):
        trace = SimpleNamespace(applied_meanings=(
            {'seat': 's', 'call': '2C', 'public_meaning': {}},
            {'seat': 'n', 'call': '2S', 'public_meaning': {}},
            {'seat': 's', 'call': '4D', 'public_meaning': {
                'call_act_types': ['slam_try'], 'agreed_suit': 'S'}},
            {'seat': 'n', 'call': '4S', 'public_meaning': {
                'call_act_types': ['reject', 'signoff', 'final_placement']}},
        ))
        self.assertEqual(policy.signoff_override(trace, 's'), ('S', 'n', '4S'))
        self.assertIsNone(policy.signoff_override(trace, 'n'))

    def test_promised_kr_sets_extra_threshold(self):
        low = Hand.parse('S5432H5432D5432C5')
        with patch.object(policy, 'assess_quality',
                          side_effect=lambda hand: {'kr_points': 15.0}), \
             patch.object(policy, 'keycards_sufficient', return_value=True), \
             patch.object(policy, '_completion_rates',
                          return_value=({'6S': 0.9}, 1)):
            decision = policy.decide_from_hands(
                Hand.parse('SAQ82HQJ72DKCA965'), 'S', [low],
                game_call='4S', promised_kr=14.0)
        self.assertEqual(decision.extra_kr_threshold, 15.95)
        self.assertEqual(decision.call, '4N')


class CueDecisionTests(unittest.TestCase):
    def setUp(self):
        self.low = Hand.parse('S5432H5432D5432C5')      # 13 cards, no HCP
        self.high = Hand.parse('SAKQH432D432C5432')     # 13 cards, 9 HCP
        self.actor = Hand.parse('SAQ82HQJ72DKCA965')

    def _decide(self, rates, cue_calls=('5C',)):
        hands = [self.low, self.low, self.high, self.high]
        with patch.object(policy, 'assess_quality',
                          side_effect=lambda hand: {'kr_points': float(hand.hcp)}), \
             patch.object(policy, 'keycards_sufficient', return_value=True), \
             patch.object(policy, 'extra_kr_threshold', return_value=5.0), \
             patch.object(policy, '_completion_rates', side_effect=rates):
            return policy.decide_from_hands(
                self.actor, 'S', hands, game_call='4S', cue_calls=cue_calls)

    def test_qualifies_without_extra_strength_asks_keycards(self):
        decision = self._decide([({'4S': 0.9, '6S': 0.9}, 2)])
        self.assertEqual(decision.call, '4N')

    def test_fails_even_with_extra_strength_places_game(self):
        decision = self._decide([
            ({'4S': 0.8, '6S': 0.2}, 2),
            ({'4S': 0.8, '6S': 0.2}, 2),
        ])
        self.assertEqual(decision.call, '4S')

    def test_depends_on_extra_strength_continues_cueing(self):
        decision = self._decide([
            ({'4S': 0.8, '6S': 0.2}, 2),
            ({'4S': 0.8, '6S': 0.9}, 2),
        ])
        self.assertEqual(decision.call, '5C')

    def test_minor_trump_never_cues_above_five_of_the_minor(self):
        with patch.object(policy, 'assess_quality',
                          side_effect=lambda hand: {'kr_points': float(hand.hcp)}), \
             patch.object(policy, 'keycards_sufficient', return_value=True), \
             patch.object(policy, 'extra_kr_threshold', return_value=5.0), \
             patch.object(policy, '_completion_rates',
                          side_effect=[({'5D': 0.8, '6D': 0.2}, 2),
                                       ({'5D': 0.8, '6D': 0.9}, 2)]):
            decision = policy.decide_from_hands(
                self.actor, 'D', [self.low, self.low, self.high, self.high],
                game_call='5D', cue_calls=('5H', '5S'))
        # 5H/5S are above 5D, so the policy must decline to cue there and pass.
        self.assertEqual(decision.call, 'P')


if __name__ == '__main__':
    unittest.main()
