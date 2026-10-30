"""Single-suit NFRKCB offer policy.

A derived 4NT suggestion creates NFRKCB only when partner has shown exactly
one natural long suit and that suit is the provisional trump. Two-suit
auctions keep natural continuations.
"""

from __future__ import annotations

from dataclasses import dataclass

from .cards import Hand
from .legality import is_call_legal
from .rkcb_continuation import bid_rank, ordinary_response, partner_of
from .slam_conventions import keycard_ask_restricted


@dataclass(frozen=True)
class NFRKCBDecision:
    call: str | None
    reason: str
    unavailable: bool = False


def single_suit_offer(evidence) -> str | None:
    side = evidence.side
    partner_suits = evidence.guaranteed_long_suits.get(side, ())
    if len(partner_suits) != 1:
        return None
    suit = partner_suits[0]
    if evidence.provisional_trump != suit:
        return None
    return suit


def decide_offer(profile, auction, trace, hand: Hand, trump: str, *,
                 evaluator=None) -> NFRKCBDecision:
    """Choose Pass (play 4NT) or the responder's actual 1430 answer."""
    if not is_call_legal(auction, 'P'):
        return NFRKCBDecision(None, 'Pass is not legal over the 4NT offer',
                              unavailable=True)
    answer = ordinary_response(hand, trump).call
    if hand.hcp + 20 < 33:
        return NFRKCBDecision('P', 'optimistic public strength cannot reach slam')
    if keycard_ask_restricted(hand, trump, grand_candidate=False):
        return NFRKCBDecision('P', 'ordinary keycard restrictions prohibit asking')
    if hand.keycard_count(trump) == 5 and hand.contains_rank(trump, 'Q'):
        return NFRKCBDecision(answer, 'responder holds every keycard and the queen')
    if evaluator is not None:
        try:
            selected = evaluator(profile, auction, trace, hand, trump, answer)
        except (RuntimeError, ValueError, TypeError) as exc:
            return NFRKCBDecision(None, f'NFRKCB comparison unavailable: {exc}',
                                  unavailable=True)
        if selected in ('P', answer):
            return NFRKCBDecision(selected, 'sampled NFRKCB comparison')
        return NFRKCBDecision(None, 'NFRKCB comparison returned an unexpected call',
                              unavailable=True)
    return NFRKCBDecision(
        None,
        'NFRKCB needs sampled 4NT-versus-slam evidence',
        unavailable=True)


def offer_effect(trump: str, offerer: str) -> dict:
    return {'key': 'nfrkcb', 'method': 'nfrkcb_offer',
            'trump_suit': trump, 'offerer': offerer}


def answer_effect(trump: str, offerer: str, answer: str) -> dict:
    return {'key': 'nfrkcb', 'method': 'nfrkcb_answered',
            'trump_suit': trump, 'offerer': offerer,
            'answer_call': answer}
