"""Construct high-HCP partnership deals for deliberate test oversampling.

These deals are synthetic test inputs. Their frequency in a scan is controlled
by a quota and must not be interpreted as the frequency of such hands in play.
"""

from __future__ import annotations

from functools import cache
import random

from .cards import SUITS
from .deal_sampler import _hand_from_cards
from .training_deals import PARTNER, SEATS


HONORS = tuple((suit, rank, points) for rank, points in
               (('A', 4), ('K', 3), ('Q', 2), ('J', 1)) for suit in SUITS)
LOW_CARDS = tuple((suit, rank) for suit in SUITS for rank in 'T98765432')
SUFFIX_POINTS = tuple(sum(card[2] for card in HONORS[index:])
                      for index in range(len(HONORS) + 1))


def _bounds(value, name):
    if (not isinstance(value, (tuple, list)) or len(value) != 2
            or any(isinstance(item, bool) or not isinstance(item, int)
                   or not 0 <= item <= 37 for item in value)
            or value[0] > value[1]):
        raise ValueError(f'{name} must be an inclusive HCP pair from 0 to 37')
    return tuple(value)


class HcpPairSampler:
    """Deal with chosen HCP ranges for a dealer and that dealer's partner."""

    def __init__(self, opener_hcp, responder_hcp):
        self.opener_hcp = _bounds(opener_hcp, 'opener_hcp')
        self.responder_hcp = _bounds(responder_hcp, 'responder_hcp')

        @cache
        def count(index, opener_left, responder_left, opener_cards, responder_cards):
            if (opener_left < 0 or responder_left < 0 or opener_cards > 13
                    or responder_cards > 13
                    or opener_left + responder_left > SUFFIX_POINTS[index]):
                return 0
            if index == len(HONORS):
                return int(opener_left == responder_left == 0)
            points = HONORS[index][2]
            return (count(index + 1, opener_left - points, responder_left,
                          opener_cards + 1, responder_cards)
                    + count(index + 1, opener_left, responder_left - points,
                            opener_cards, responder_cards + 1)
                    + count(index + 1, opener_left, responder_left,
                            opener_cards, responder_cards))

        self._count = count
        self._feasible = tuple(
            (opener, responder)
            for opener in range(self.opener_hcp[0], self.opener_hcp[1] + 1)
            for responder in range(self.responder_hcp[0], self.responder_hcp[1] + 1)
            if count(0, opener, responder, 0, 0)
        )
        if not self._feasible:
            raise ValueError('no feasible honor allocation for requested HCP ranges')

    def deal(self, rng: random.Random, dealer: str):
        if dealer not in SEATS:
            raise ValueError('dealer must be n, e, s, or w')
        partner = PARTNER[dealer]
        opponents = [seat for seat in SEATS if seat not in (dealer, partner)]
        opener_left, responder_left = rng.choice(self._feasible)
        opener_count = responder_count = 0
        cards = {seat: [] for seat in SEATS}
        other_honors = []
        for index, (suit, rank, points) in enumerate(HONORS):
            options = (
                (dealer, self._count(index + 1, opener_left - points,
                                     responder_left, opener_count + 1,
                                     responder_count)),
                (partner, self._count(index + 1, opener_left,
                                      responder_left - points, opener_count,
                                      responder_count + 1)),
                (None, self._count(index + 1, opener_left, responder_left,
                                   opener_count, responder_count)),
            )
            pick = rng.randrange(sum(weight for _, weight in options))
            for seat, weight in options:
                if pick < weight:
                    break
                pick -= weight
            if seat == dealer:
                opener_left -= points
                opener_count += 1
                cards[dealer].append((suit, rank))
            elif seat == partner:
                responder_left -= points
                responder_count += 1
                cards[partner].append((suit, rank))
            else:
                other_honors.append((suit, rank))

        rng.shuffle(other_honors)
        split = rng.randint(max(0, len(other_honors) - 13), min(13, len(other_honors)))
        cards[opponents[0]].extend(other_honors[:split])
        cards[opponents[1]].extend(other_honors[split:])
        empty_slots = [seat for seat in SEATS for _ in range(13 - len(cards[seat]))]
        rng.shuffle(empty_slots)
        low_cards = list(LOW_CARDS)
        rng.shuffle(low_cards)
        for seat, card in zip(empty_slots, low_cards):
            cards[seat].append(card)
        return {seat: _hand_from_cards(cards[seat]) for seat in SEATS}
