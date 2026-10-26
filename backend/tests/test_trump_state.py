import unittest

from engine.auction import Auction
from engine.cards import Hand
from engine.model import Author, Gadget, PartnershipProfile
from engine.replay import replay_auction
from engine.selector import choose_bid


def profile(*specs):
    gadget = Gadget.from_parts({'id': 'trump_contract', 'author': {'name': 'Test'}}, list(specs))
    return PartnershipProfile('trump_contract', 'Trump Contract', '1', Author('Test'), (gadget,),
                              missing_call_behavior='block')


def spec(id, when, call, *, effects=(), requires=None, applies=None, priority=None):
    result = {'id': id, 'context': {'auction_pattern': when}, 'call': call,
              'meaning': {'action_type': id}, 'effects': list(effects)}
    if requires is not None:
        result['requires'] = requires
    if applies is not None:
        result['applicability'] = applies
    if priority is not None:
        result['priority'] = priority
    return result


class TrumpStateTests(unittest.TestCase):
    hand = Hand.parse('SKJT5HATDAQ92C652')

    def test_each_side_has_independent_unset_provisional_and_agreed_state(self):
        system = profile(
            spec('ns_propose', '', '1C', effects=[{'key': 'trump_state', 'status': 'provisional', 'suit': 'C'}]),
            spec('ew_propose', '1C', '1D', effects=[{'key': 'trump_state', 'status': 'provisional', 'suit': 'D'}]),
        )
        empty = replay_auction(system, Auction.parse(''))
        self.assertEqual(empty.trump_state('ns').status, 'unset')
        self.assertEqual(empty.trump_state('ew').status, 'unset')

        before_partner = replay_auction(system, Auction.parse('1C1D'))
        self.assertEqual(before_partner.trump_state('ns').status, 'provisional')
        self.assertEqual(before_partner.trump_state('ew').status, 'provisional')

        after_ns_partner = replay_auction(system, Auction.parse('1C1DP'))
        self.assertEqual(after_ns_partner.trump_state('ns').status, 'agreed')
        self.assertEqual(after_ns_partner.trump_state('ns').suit, 'C')
        self.assertEqual(after_ns_partner.trump_state('ew').status, 'provisional')

        after_both_partners = replay_auction(system, Auction.parse('1C1DPP'))
        self.assertEqual(after_both_partners.trump_state('ew').status, 'agreed')
        self.assertEqual(after_both_partners.trump_state('ew').suit, 'D')

    def test_maintain_and_replace_override_partner_default(self):
        system = profile(
            spec('propose', '', '1C', effects=[{'key': 'trump_state', 'status': 'provisional', 'suit': 'C'}]),
            spec('maintain', '1CP', '1D', effects=[{'key': 'trump_state', 'transition': 'maintain'}]),
            spec('replace', '1CP1DPPP', '1H', effects=[{'key': 'trump_state', 'transition': 'replace',
                                                     'status': 'provisional', 'suit': 'H'}]),
        )
        maintained = replay_auction(system, Auction.parse('1CP1D'))
        self.assertEqual((maintained.trump_state('ns').status, maintained.trump_state('ns').suit),
                         ('provisional', 'C'))
        replaced = replay_auction(system, Auction.parse('1CP1DPPP1H'))
        self.assertEqual((replaced.trump_state('ns').status, replaced.trump_state('ns').suit),
                         ('provisional', 'H'))

    def test_partner_pass_after_enemy_intervention_promotes_and_is_visible_to_next_call(self):
        system = profile(
            spec('propose', '', '1C', effects=[{'key': 'trump_state', 'status': 'provisional', 'suit': 'C'}]),
            spec('after_pass', '1C1DPP', '1H', requires={'state_exists': {'key': 'agreed_suit', 'suit': 'C'}}),
        )
        trace = replay_auction(system, Auction.parse('1C1DPP'))
        self.assertEqual(trace.trump_state('ns').status, 'agreed')
        self.assertTrue(trace.state_exists({'key': 'agreed_suit', 'suit': 'C'}))
        self.assertEqual(choose_bid(system, Auction.parse('1C1DPP'), self.hand).call, '1H')

    def test_partner_call_uses_promoted_state_for_its_own_meaning(self):
        system = profile(
            spec('propose', '', '1C', effects=[{'key': 'trump_state', 'status': 'provisional', 'suit': 'C'}]),
            spec('agreed_continuation', '1C1D', '4N',
                 requires={'state_exists': {'key': 'agreed_suit', 'suit': 'C'}}),
        )
        self.assertEqual(choose_bid(system, Auction.parse('1C1D'), self.hand).call, '4N')
        trace = replay_auction(system, Auction.parse('1C1D4N'))
        self.assertEqual(trace.applied_meanings[-1]['public_meaning']['action_type'], 'agreed_continuation')
        self.assertEqual(trace.trump_state('ns').status, 'agreed')

    def test_replaced_agreement_hides_old_and_opponent_suit_from_current_readers(self):
        system = profile(
            spec('first', '', '1C', effects=[{'key': 'agreed_suit', 'suit': 'C'}]),
            spec('enemy', '1C', '1D', effects=[{'key': 'agreed_suit', 'suit': 'D'}]),
            spec('replace', '1C1D', '1H', effects=[{'key': 'agreed_suit', 'suit': 'H'}]),
        )
        trace = replay_auction(system, Auction.parse('1C1D1HP'))
        self.assertEqual([record.attribute('suit') for record in trace.matching_state({'key': 'agreed_suit'})], ['H'])
        self.assertFalse(trace.state_exists({'key': 'agreed_suit', 'suit': 'C'}))
        self.assertFalse(trace.state_exists({'key': 'agreed_suit', 'suit': 'D'}))
        self.assertEqual(len([record for record in trace.state_records if record.key == 'agreed_suit']), 3)
        self.assertEqual(trace.trump_state('ew').suit, 'D')

    def test_current_deciding_hand_cannot_change_prior_public_meanings_or_effects(self):
        system = profile(spec('opening', '', '1C', requires={'self.hcp': {'min': 10}},
                              effects=[{'key': 'public_hcp', 'value': {'expr': {'var': 'self.hcp'}}}]))
        low = replay_auction(system, Auction.parse('1CP'), Hand.parse('S9876H9876D987C98'))
        high = replay_auction(system, Auction.parse('1CP'), self.hand)
        self.assertEqual(low.applied_meanings, high.applied_meanings)
        self.assertEqual(low.state_records, high.state_records)
        self.assertEqual(low.applied_meanings[0]['public_meaning']['action_type'], 'opening')
        self.assertFalse(low.state_exists({'key': 'public_hcp'}))

    def test_private_applicability_only_filters_current_candidates(self):
        system = profile(spec('opening', '', '1C', applies={'self.hcp': {'min': 10}}))
        low = Hand.parse('S9876H9876D987C98')
        self.assertIsNone(choose_bid(system, Auction.parse(''), low).call)
        self.assertEqual(choose_bid(system, Auction.parse(''), self.hand).call, '1C')
        self.assertEqual(len(replay_auction(system, Auction.parse('1C'), low).applied_meanings), 1)

    def test_explicit_replacement_wins_before_same_call_agreed_trump_meaning(self):
        system = profile(
            spec('propose', '', '1C', effects=[{'key': 'trump_state', 'status': 'provisional', 'suit': 'C'}]),
            spec('generic_4nt', '1C1D', '4N', requires={'state_exists': {'key': 'agreed_suit', 'suit': 'C'}}),
            spec('replace_4nt', '1C1D', '4N', priority=10,
                 requires={'state_exists': {'key': 'trump_state', 'status': 'provisional', 'suit': 'C'}},
                 effects=[{'key': 'trump_state', 'transition': 'replace', 'status': 'agreed', 'suit': 'D'}]),
        )
        prior = Auction.parse('1C1D')
        self.assertEqual(choose_bid(system, prior, self.hand).selected_candidate.source_id, 'replace_4nt')
        trace = replay_auction(system, Auction.parse('1C1D4N'))
        self.assertEqual(trace.applied_meanings[-1]['public_meaning']['action_type'], 'replace_4nt')
        self.assertEqual(trace.trump_state('ns').suit, 'D')

    def test_unresolved_same_call_overlap_blocks_selection_and_replay(self):
        system = profile(spec('meaning_a', '', '1C'), spec('meaning_b', '', '1C'))
        decision = choose_bid(system, Auction.parse(''), self.hand)
        self.assertIsNone(decision.call)
        self.assertTrue(any('Ambiguous meaning' in d for d in decision.trace.diagnostics))
        replay = replay_auction(system, Auction.parse('1C'))
        self.assertEqual(replay.applied_meanings, [])
        self.assertTrue(any('Ambiguous prior call' in d for d in replay.diagnostics))


if __name__ == '__main__':
    unittest.main()
