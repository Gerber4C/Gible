import unittest

from engine.auction import Auction
from engine.cards import Hand
from engine.model import Author, Gadget, PartnershipProfile
from engine.selector import choose_bid
from engine.slam_conventions import keycard_ask_restricted


def profile_with_keycard_ask(trump='H'):
    gadget = Gadget.from_parts(
        {'id': 'ask', 'namespace': 'test', 'name': 'Ask',
         'author': {'name': 'Test'}},
        [{
            'id': 'ask', 'context': {'auction_pattern': ''}, 'call': '4NT',
            'meaning': {
                'nature_labels': ['artificial'],
                'call_act_types': ['inquiry', 'keycard_asking'],
                'agreed_suit': trump, 'target_suit': trump,
            },
        }])
    return PartnershipProfile('test', 'Test', '1', Author('Test'),
                              (gadget,), missing_call_behavior='block')


class KeycardRestrictionTests(unittest.TestCase):
    def test_heart_one_keycard_without_queen_is_restricted(self):
        hand = Hand.parse('SA2H976D432CQ5432')
        self.assertEqual(hand.keycard_count('H'), 1)
        self.assertFalse(hand.contains_rank('H', 'Q'))
        self.assertTrue(keycard_ask_restricted(hand, 'H'))
        with_queen = Hand.parse('SA2HQ76D432CK5432')
        self.assertTrue(with_queen.contains_rank('H', 'Q'))
        self.assertFalse(keycard_ask_restricted(with_queen, 'H'))
        two_keycards = Hand.parse('SA2HK76D432CQ5432')
        self.assertEqual(two_keycards.keycard_count('H'), 2)
        self.assertFalse(keycard_ask_restricted(two_keycards, 'H'))

    def test_diamond_one_keycard_is_restricted_even_with_queen(self):
        hand = Hand.parse('SA2HK76D432CQ5432')
        self.assertEqual(hand.keycard_count('D'), 1)
        self.assertTrue(keycard_ask_restricted(hand, 'D'))
        two_keycards = Hand.parse('SA2HK76DA32CQ5432')
        self.assertEqual(two_keycards.keycard_count('D'), 2)
        self.assertFalse(keycard_ask_restricted(two_keycards, 'D'))

    def test_club_three_keycards_without_grand_intent_is_restricted(self):
        hand = Hand.parse('SA32HA32DA32CQ432')
        self.assertEqual(hand.keycard_count('C'), 3)
        self.assertTrue(keycard_ask_restricted(hand, 'C', grand_candidate=False))
        self.assertFalse(keycard_ask_restricted(hand, 'C', grand_candidate=True))
        two_keycards = Hand.parse('SA32HA32D432CQ432')
        self.assertEqual(two_keycards.keycard_count('C'), 2)
        self.assertFalse(keycard_ask_restricted(two_keycards, 'C'))

    def test_selector_drops_a_restricted_four_notrump_ask(self):
        profile = profile_with_keycard_ask('H')
        restricted = Hand.parse('SA2H976D432CQ5432')
        self.assertIsNone(choose_bid(profile, Auction.parse(''), restricted).call)

        allowed = Hand.parse('SA2HK76D5432CQ432')
        self.assertEqual(allowed.keycard_count('H'), 2)
        self.assertEqual(choose_bid(profile, Auction.parse(''), allowed).call, '4N')



if __name__ == '__main__':
    unittest.main()
