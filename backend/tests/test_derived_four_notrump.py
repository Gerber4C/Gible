import unittest

from engine.auction import Auction
from engine.derived_evidence import ClassifiedCall, DerivedEvidence
from engine.derived_four_notrump import derive


def evidence(**overrides):
    values = dict(
        actor='n', side='ns', contract='4S', contract_level=4,
        contract_strain='S', agreed_trump=None, provisional_trump=None,
        plausible_trumps=(), forcing=False, three_notrump_available=False,
        classified_calls=(), conflicts=())
    values.update(overrides)
    return DerivedEvidence(**values)


def raise_(call, suit):
    return ClassifiedCall(call, 'raise', suit, establishes_trump=suit)


def selector(call, suit):
    return ClassifiedCall(call, 'selector', suit, establishes_trump=suit)


class DerivedFourNotrumpTests(unittest.TestCase):
    def calls(self, ev, auction='4SP', allowed=None):
        result = derive(None, Auction.parse(auction), None, ev,
                        allowed or {'4N'})
        return {candidate.call: candidate for candidate in result.candidates}, result

    def test_agreed_trump_makes_4nt_keycard(self):
        candidates, _ = self.calls(evidence(agreed_trump='H'))
        meaning = candidates['4N'].public_meaning
        self.assertEqual((meaning['action_type'], meaning['agreed_suit']),
                         ('rkcb_1430', 'H'))

    def test_three_level_defaults_to_quantitative(self):
        candidates, _ = self.calls(evidence(
            contract='3S', contract_level=3, contract_strain='S',
            plausible_trumps=('H',)))
        self.assertEqual(candidates['4N'].public_meaning['action_type'],
                         'quantitative_4nt')

    def test_three_level_exception_asks_when_forcing_and_sole_trump(self):
        candidates, _ = self.calls(evidence(
            contract='3S', contract_level=3, contract_strain='S',
            plausible_trumps=('H',), forcing=True))
        self.assertEqual(candidates['4N'].public_meaning['action_type'],
                         'rkcb_1430')

    def test_one_raise_plus_selector_makes_4nt_quantitative(self):
        candidates, _ = self.calls(evidence(
            plausible_trumps=('H', 'S'),
            classified_calls=(raise_('4H', 'H'), selector('4D', 'S'))))
        self.assertEqual(candidates['4N'].public_meaning['action_type'],
                         'quantitative_4nt')

    def test_one_raise_and_no_selector_asks_the_other_suit(self):
        candidates, _ = self.calls(evidence(
            plausible_trumps=('H', 'S'),
            classified_calls=(raise_('4H', 'H'),)))
        self.assertEqual(candidates['4N'].public_meaning['agreed_suit'], 'S')

    def test_one_selector_and_no_raise_asks_the_higher_suit(self):
        candidates, _ = self.calls(evidence(
            plausible_trumps=('H', 'S'),
            classified_calls=(selector('4D', 'H'),)))
        self.assertEqual(candidates['4N'].public_meaning['agreed_suit'], 'S')

    def test_two_selectors_cover_both_suits_and_4nt_is_quantitative(self):
        candidates, _ = self.calls(evidence(
            plausible_trumps=('H', 'S'),
            classified_calls=(selector('4D', 'H'), selector('4C', 'H'))))
        self.assertEqual(candidates['4N'].public_meaning['action_type'],
                         'quantitative_4nt')

    def test_three_plausible_trumps_td(self):
        _, result = self.calls(evidence(plausible_trumps=('C', 'D', 'H')))
        self.assertEqual(result.conflicts[0]['code'],
                         'FOUR_NOTRUMP_TOO_MANY_TRUMPS')

    def test_selector_uses_trump_selector_not_control_showing(self):
        candidates, _ = self.calls(evidence(
            plausible_trumps=('H', 'S'),
            classified_calls=(selector('4D', 'H'),)), allowed={'4N', '4D'})
        meaning = candidates['4D'].public_meaning
        self.assertIn('trump_selector', meaning['call_act_types'])
        self.assertNotIn('control_showing', meaning['call_act_types'])


if __name__ == '__main__':
    unittest.main()
