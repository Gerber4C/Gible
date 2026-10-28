import random
import os
import time
import unittest
from types import SimpleNamespace

from engine.auction import Auction
from engine.hand_quality import assess_quality
from engine.joint_deal_sampler import (
    JointConstraintError,
    JointPartnershipPlan,
    OpenerModeConstraints,
    joint_suit_buckets,
    sample_conditioned_partnership,
)
from engine.loader import load_profile
from engine.opener_coverage import (
    allocate_opener_strata,
    rotate_responder_shape,
)
from engine.selector import choose_bid


COVERAGE_SHAPES = (
    (4, 4, 3, 2), (5, 3, 3, 2), (5, 4, 3, 1), (5, 4, 2, 2),
    (4, 3, 3, 3), (6, 3, 2, 2), (6, 4, 2, 1), (6, 3, 3, 1),
    (5, 5, 2, 1), (4, 4, 4, 1), (7, 3, 2, 1), (6, 4, 3, 0),
    (5, 4, 4, 0), (5, 5, 3, 0), (6, 5, 1, 1), (6, 5, 2, 0),
    (7, 2, 2, 2), (7, 4, 1, 1), (7, 4, 2, 0), (7, 3, 3, 0),
    (8, 2, 2, 1), (8, 3, 1, 1), (8, 3, 2, 0),
)


def opening_assessment():
    profile = load_profile('daqiush_2over1')
    definition = next(item.definition for item in profile.all_evaluator_specs
                      if item.id == 'opening_assessment')

    def assess(hand):
        return definition(SimpleNamespace(hand=hand,
                                          hand_quality=assess_quality(hand)))
    return assess


def cards(hand):
    return {(suit, rank) for suit in 'SHDC' for rank in hand.holding(suit)}


class BoundaryRandom(random.Random):
    def __init__(self, boundary):
        super().__init__(0)
        self.boundary = boundary

    def randrange(self, stop):
        value, self.boundary = self.boundary, 0
        if value >= stop:
            raise AssertionError((value, stop))
        return value


class JointDealSamplerTests(unittest.TestCase):
    def test_real_allocated_strata_cover_every_five_card_major_inquiry_reply(self):
        profile = load_profile('daqiush_2over1')
        authored = opening_assessment()
        inquiry = Auction.parse('1NP3CP')
        evidence = (
            # (South HCP, base-shape index, joint-sampler seed, expected reply)
            (0, 0, 0, '3D'),
            (0, 1, 0, '3S'),
            (0, 3, 0, '3H'),
        )
        cells = [
            {'target_hcp': hcp, 'base_shape_index': index,
             'base_shape': shape}
            for hcp in range(23)
            for index, shape in enumerate(COVERAGE_SHAPES)
        ]
        assignments = allocate_opener_strata(cells)['assignments']
        replies = {}
        for hcp, shape_index, seed, expected in evidence:
            identity = (hcp, shape_index)
            stratum = assignments[identity]
            south_shape = rotate_responder_shape(
                COVERAGE_SHAPES[shape_index], hcp, shape_index)
            plan = JointPartnershipPlan(
                OpenerModeConstraints(stratum.shape, stratum.mode,
                                      (0.0, 37.0)),
                south_shape, hcp, (0.0, 37.0),
            )
            north = sample_conditioned_partnership(
                plan, seed=seed, opening_assessment=authored)['n']
            reply = choose_bid(profile, inquiry, north).call
            replies[expected] = {
                'actual': reply, 'identity': identity, 'seed': seed,
                'north': str(north),
            }
            self.assertEqual(reply, expected, replies[expected])

        self.assertEqual(set(replies), {'3D', '3H', '3S'}, replies)

    def test_suit_bucket_boundaries_preserve_six_concrete_allocations(self):
        buckets = joint_suit_buckets('AKQ', 1, 1)

        self.assertEqual(buckets.total, 6)
        self.assertEqual(sum(group.count for group in buckets.groups), 6)
        selected = [buckets.sample(BoundaryRandom(draw)) for draw in range(6)]
        self.assertEqual(len(set(selected)), 6)
        self.assertEqual(set(selected), {
            ((north,), (south,))
            for north in 'AKQ' for south in 'AKQ' if north != south
        })

    def test_arbitrary_precision_layer_count_is_stable_after_cache_reuse(self):
        first = [joint_suit_buckets('AKQJT98765432', 4, 4) for _ in range(4)]
        second = [joint_suit_buckets('AKQJT98765432', 4, 4) for _ in range(4)]
        total = 1
        for buckets in first:
            total *= buckets.total

        self.assertGreater(total, 2 ** 63)
        self.assertEqual(total, 90090 ** 4)
        self.assertEqual(first, second)

    def test_representative_modes_are_exact_and_cache_deterministic(self):
        authored = opening_assessment()
        cases = (
            (OpenerModeConstraints((4, 3, 3, 3), 'normal', (14.0, 19.0)),
             (5, 3, 3, 2), 10, (7.0, 15.0)),
            (OpenerModeConstraints((5, 3, 3, 2), 'upgrade_14', (15.0, 18.0)),
             (4, 4, 3, 2), 10, (7.0, 15.0)),
            (OpenerModeConstraints((4, 4, 3, 2), 'soft_18', (13.0, 16.0)),
             (5, 3, 3, 2), 8, (5.0, 13.0)),
            (OpenerModeConstraints((4, 4, 4, 1), 'normal', (14.0, 19.0)),
             (5, 3, 3, 2), 9, (6.0, 14.0)),
        )
        for index, (north, south_shape, south_hcp, south_kr) in enumerate(cases):
            with self.subTest(mode=north.mode, shape=north.shape):
                plan = JointPartnershipPlan(north, south_shape, south_hcp,
                                            south_kr)
                first = sample_conditioned_partnership(
                    plan, seed=100 + index, opening_assessment=authored)
                second = sample_conditioned_partnership(
                    JointPartnershipPlan(north, south_shape, south_hcp,
                                         south_kr),
                    seed=100 + index, opening_assessment=authored)
                self.assertEqual(first, second)
                n, s = first['n'], first['s']
                self.assertEqual(len(cards(n)), 13)
                self.assertEqual(len(cards(s)), 13)
                self.assertFalse(cards(n) & cards(s))
                self.assertEqual(tuple(n.length(suit) for suit in 'SHDC'),
                                 north.shape)
                self.assertEqual(tuple(s.length(suit) for suit in 'SHDC'),
                                 south_shape)
                self.assertEqual(s.hcp, south_hcp)
                expected_hcp = {'normal': range(15, 18), 'upgrade_14': (14,),
                                'soft_18': (18,)}[north.mode]
                self.assertIn(n.hcp, expected_hcp)
                self.assertTrue(authored(n)['eligible'])
                north_kr = assess_quality(n)['kr_points']
                south_actual_kr = assess_quality(s)['kr_points']
                self.assertTrue(north.kr[0] <= north_kr <= north.kr[1])
                self.assertTrue(south_kr[0] <= south_actual_kr <= south_kr[1])
                if north.mode == 'soft_18':
                    self.assertTrue(any(n.length(suit) == 2
                                        and set(n.holding(suit)) == {'Q', 'J'}
                                        for suit in 'SHDC'))
                for suit in 'SHDC':
                    if n.length(suit) == 1:
                        self.assertIn(n.holding(suit), ('A', 'K', 'Q'))

    def test_impossible_constraints_raise_complete_diagnostics_without_draw(self):
        plan = JointPartnershipPlan(
            OpenerModeConstraints((4, 3, 3, 3), 'normal', (30.0, 31.0)),
            (4, 3, 3, 3), 0, (0.0, 1.0),
        )
        with self.assertRaises(JointConstraintError) as caught:
            sample_conditioned_partnership(plan, seed=2,
                                           opening_assessment=lambda hand: {'eligible': True})
        message = str(caught.exception)
        for expected in ('north_shape=(4, 3, 3, 3)', 'mode=normal',
                         'south_shape=(4, 3, 3, 3)', 'south_hcp=0',
                         'north_kr=(30.0, 31.0)', 'south_kr=(0.0, 1.0)',
                         'completion_count=0'):
            self.assertIn(expected, message)

    def test_authored_invariant_failure_is_immediate_and_diagnostic(self):
        calls = []

        def reject(hand):
            calls.append(hand)
            return {'eligible': False, 'reasons': ['injected']}

        plan = JointPartnershipPlan(
            OpenerModeConstraints((4, 3, 3, 3), 'normal', (14.0, 19.0)),
            (5, 3, 3, 2), 10, (7.0, 15.0),
        )
        with self.assertRaises(JointConstraintError) as caught:
            sample_conditioned_partnership(plan, seed=3,
                                           opening_assessment=reject)
        self.assertEqual(len(calls), 1)
        self.assertIn("predicate_result={'eligible': False, 'reasons': ['injected']}",
                      str(caught.exception))
        self.assertIn(f'completion_count={plan.total}', str(caught.exception))

    def test_hardest_5242_normal_generates_ten_pairs_within_budget(self):
        plan = JointPartnershipPlan(
            OpenerModeConstraints((5, 2, 4, 2), 'normal', (13.0, 19.0)),
            (4, 4, 3, 2), 10, (6.0, 15.0),
        )
        authored = opening_assessment()
        started = time.perf_counter()
        samples = [sample_conditioned_partnership(
            plan, seed=seed, opening_assessment=authored)
                   for seed in range(10)]
        self.assertEqual(len(samples), 10)
        self.assertLess(time.perf_counter() - started, 30.0)

    @unittest.skipUnless(
        os.environ.get('GIBLE_RUN_SLOW_COVERAGE'),
        'slow exact-counter verification; run with GIBLE_RUN_SLOW_COVERAGE=1')
    def test_all_default_allocations_have_an_exact_joint_completion(self):
        cells = [
            {'target_hcp': hcp, 'base_shape_index': index, 'base_shape': shape}
            for hcp in range(23)
            for index, shape in enumerate(COVERAGE_SHAPES)
        ]
        allocation = allocate_opener_strata(cells)
        self.assertEqual(len(allocation['assignments']), 529)
        by_identity = {(cell['target_hcp'], cell['base_shape_index']): cell
                       for cell in cells}
        for identity, stratum in allocation['assignments'].items():
            with self.subTest(identity=identity, stratum=stratum):
                cell = by_identity[identity]
                south_shape = rotate_responder_shape(
                    cell['base_shape'], identity[0], identity[1])
                plan = JointPartnershipPlan(
                    OpenerModeConstraints(
                        stratum.shape, stratum.mode, (0.0, 37.0)),
                    south_shape, identity[0], (0.0, 37.0),
                )
                self.assertGreater(
                    plan.total, 0,
                    {'identity': identity, 'stratum': stratum,
                     'south_shape': south_shape,
                     'diagnostics': plan.diagnostics(
                         f'completion_count={plan.total}')})


if __name__ == '__main__':
    unittest.main()
