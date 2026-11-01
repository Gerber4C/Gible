import unittest

from engine.keycard_game_tree import choose_reactive_continuation


class KeycardGameTreeTests(unittest.TestCase):
    def test_invitation_branch_can_beat_direct_final(self):
        hands = ('weak', 'strong')

        def responses(candidate, hand):
            if candidate == '6T':
                return ('P', '7T')
            return ('P',)

        def final_contract(candidate, response, hand):
            if candidate == '6T':
                return '6T' if response == 'P' else '7T'
            return '7T'

        def score(contract, hand):
            if hand == 'weak':
                return 100 if contract == '6T' else -100
            return 100 if contract == '7T' else 50

        result = choose_reactive_continuation(
            ('6T', '7T'), hands, responses=responses,
            final_contract=final_contract, score=score)
        self.assertEqual(result.call, '6T')
        self.assertEqual(result.expected_score, 100.0)
        self.assertEqual(
            [(response, final) for _, response, final in result.reactions],
            [('P', '6T'), ('7T', '7T')])

    def test_no_partner_samples_returns_none(self):
        result = choose_reactive_continuation(
            ('6T',), (), responses=lambda *_: ('P',),
            final_contract=lambda *_: '6T', score=lambda *_: 1.0)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
