"""Pure ordinary-RKCB frame reading, useful-void classification, and answers.

The module never reads private cards except for the acting hand's own void and
keycard count. Public facts come from replayed meanings and state only.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .cards import Hand
from .legality import is_call_legal, legal_calls


ORDINARY_METHOD = 'rkcb_1430'
STATUSES = ('pending_answer', 'answered', 'relay_pending', 'relay_completed',
            'completed', 'disrupted')
ACTIVE_STATUSES = ('pending_answer', 'answered', 'relay_pending', 'relay_completed')
CALL_ORDER = ('4C', '4D', '4H', '4S', '4NT', '5C', '5D', '5H', '5S', '5NT',
              '6C', '6D', '6H', '6S', '6NT', '7C', '7D', '7H', '7S', '7NT')


@dataclass(frozen=True)
class OrdinaryRKCBFrame:
    trump: str
    status: str
    answer_category: str | None = None
    answer_call: str | None = None
    keycard_counts: tuple[int, ...] = ()
    trump_queen: bool | None = None
    useful_void: str | None = None
    useful_void_category: str | None = None
    not_required_kings: tuple[str, ...] = ()
    disrupted_reason: str | None = None
    continuation_stage: str | None = None
    invitation_call: str | None = None
    shown_king: str | None = None
    counterinvite_count: int = 0

    @property
    def active(self) -> bool:
        return self.status in ACTIVE_STATUSES


@dataclass(frozen=True)
class RKCBResponse:
    call: str
    keycard_counts: tuple[int, ...]
    trump_queen: bool | None = None
    void_suit: str | None = None
    void_category: str | None = None


def bid_rank(call: str) -> int:
    return int(call[0]) * 5 + 'CDHSN'.index(call[1])


def partner_of(seat: str) -> str:
    return {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[seat]


def ordinary_rkcb_frame(trace) -> OrdinaryRKCBFrame | None:
    """The latest public ``rkcb_1430`` frame, or None for other methods."""
    records = [record for record in trace.current_state_records
               if record.key == 'keycard_context']
    if not records:
        return None
    record = records[-1]
    if record.attribute('method') != ORDINARY_METHOD:
        return None
    status = record.attribute('status') or 'pending_answer'
    if status == 'pending':
        status = 'pending_answer'
    if status not in STATUSES:
        return None
    trump = record.attribute('trump_suit')
    if trump not in 'CDHS':
        return None
    counts = record.attribute('keycard_counts') or ()
    return OrdinaryRKCBFrame(
        trump=trump,
        status=status,
        answer_category=record.attribute('answer_category'),
        answer_call=record.attribute('answer_call'),
        keycard_counts=tuple(int(value) for value in counts),
        trump_queen=record.attribute('trump_queen'),
        useful_void=record.attribute('useful_void'),
        useful_void_category=record.attribute('useful_void_category'),
        not_required_kings=tuple(record.attribute('not_required_kings') or ()),
        disrupted_reason=record.attribute('disrupted_reason'),
        continuation_stage=record.attribute('continuation_stage'),
        invitation_call=record.attribute('invitation_call'),
        shown_king=record.attribute('shown_king'),
        counterinvite_count=int(record.attribute('counterinvite_count') or 0),
    )


def public_minimum_length(meaning: dict[str, Any], suit: str) -> int:
    lengths = meaning.get('suit_length_minimums', {}) or {}
    if suit in lengths:
        return int(lengths[suit])
    if meaning.get('target_suit') == suit:
        return int(meaning.get('minimum_length', 0) or 0)
    return 0


def naturally_shown_long_suits(trace, partner: str) -> frozenset[str]:
    result = set()
    for entry in trace.applied_meanings:
        meaning = entry.get('public_meaning', {})
        call = entry.get('call', '')
        if (entry.get('seat') == partner and len(call) == 2
                and call[0] in '1234567' and call[1] in 'CDHS'
                and 'natural' in meaning.get('nature_labels', ())
                and public_minimum_length(meaning, call[1]) >= 4):
            result.add(call[1])
    return frozenset(result)


def useful_voids(trace, responder: str, hand: Hand,
                 trump: str) -> tuple[str, ...]:
    excluded = naturally_shown_long_suits(trace, partner_of(responder))
    return tuple(suit for suit in 'CDHS'
                 if suit != trump and hand.length(suit) == 0
                 and suit not in excluded)


def ordinary_response(hand: Hand, trump: str,
                      voids: Iterable[str] = ()) -> RKCBResponse:
    count = hand.keycard_count(trump)
    queen = hand.contains_rank(trump, 'Q')
    voids = tuple(voids)
    if voids:
        void = voids[0]
        if count in (0, 2, 4):
            return RKCBResponse('5N', (0, 2, 4),
                                void_category='unspecified')
        if bid_rank('6' + void) < bid_rank('6' + trump):
            return RKCBResponse('6' + void, (1, 3), void_suit=void)
        return RKCBResponse('6' + trump, (1, 3),
                            void_category='higher_than_trump')
    if count in (1, 4):
        return RKCBResponse('5C', (1, 4))
    if count in (0, 3):
        return RKCBResponse('5D', (0, 3))
    if not queen:
        return RKCBResponse('5H', (2,), trump_queen=False)
    return RKCBResponse('5S', (2,), trump_queen=True)


def queen_ask_call(auction, frame: OrdinaryRKCBFrame | None) -> str | None:
    """The step above a 5C/5D answer that is not five of trumps."""
    if frame is None or frame.status != 'answered':
        return None
    answer = {'1/4': '5C', '0/3': '5D'}.get(frame.answer_category)
    if answer is None:
        return None
    candidates = [call for call in legal_calls(auction)
                  if call[0] in '567'
                  and call != '5' + frame.trump
                  and bid_rank(answer) < bid_rank(call) < bid_rank('5NT')]
    return min(candidates, key=bid_rank) if candidates else None


def five_spade_role(auction, frame: OrdinaryRKCBFrame | None) -> str:
    """Return ``queen_ask``, ``relay`` or ``unavailable`` for a 5S call."""
    if frame is None or frame.status != 'answered':
        return 'unavailable'
    if frame.trump == 'S':
        return 'unavailable'
    if not is_call_legal(auction, '5S'):
        return 'unavailable'
    ask = queen_ask_call(auction, frame)
    if ask == '5S':
        return 'queen_ask'
    return 'relay'


def five_trump_available(auction, trump: str) -> bool:
    return is_call_legal(auction, '5' + trump)


def lowest_showable_side_king(hand: Hand | None, trump: str, auction,
                              denied: Iterable[str] = ()) -> str | None:
    if hand is None:
        return None
    denied = set(denied)
    calls = [f'6{suit}' for suit in 'CDHS'
             if suit != trump and suit not in denied
             and hand.contains_rank(suit, 'K')
             and is_call_legal(auction, f'6{suit}')
             and bid_rank(f'6{suit}') < bid_rank(f'6{trump}')]
    return min(calls, key=bid_rank) if calls else None


def relay_terminal_call(auction, hand: Hand | None, trump: str) -> str | None:
    small_slam = f'6{trump}'
    return small_slam if is_call_legal(auction, small_slam) else None


def possible_partner_counts(frame: OrdinaryRKCBFrame | None,
                            own_keycards: int) -> tuple[int, ...]:
    if frame is None:
        return ()
    return tuple(count for count in frame.keycard_counts
                 if 0 <= 5 - own_keycards - count <= 5)


def void_category_matches(hand: Hand, frame: OrdinaryRKCBFrame,
                          trump: str) -> bool:
    if frame.useful_void is not None:
        return hand.length(frame.useful_void) == 0
    if frame.useful_void_category == 'higher_than_trump':
        return any(hand.length(suit) == 0
                   for suit in 'CDHS'
                   if suit != trump
                   and 'CDHS'.index(suit) > 'CDHS'.index(trump))
    if frame.useful_void_category == 'unspecified':
        return any(hand.length(suit) == 0 for suit in 'CDHS'
                   if suit != trump)
    return True


def answer_category_filter(frame: OrdinaryRKCBFrame, trump: str):
    def accepts(hand: Hand) -> bool:
        return (hand.keycard_count(trump) in frame.keycard_counts
                and void_category_matches(hand, frame, trump))
    return accepts


HIGH_ANSWER_CATEGORIES = ('0/2/4/void', '1/3/void')


def is_high_answer(frame: OrdinaryRKCBFrame | None) -> bool:
    return frame is not None and frame.answer_category in HIGH_ANSWER_CATEGORIES


def partner_of_last_bidder(auction) -> str | None:
    for index in range(len(auction.calls) - 1, -1, -1):
        if auction.calls[index] not in ('P', 'X', 'R'):
            return partner_of(auction.actor_at(index))
    return None


def skipped_lower_kings(answer: str, invitation: str, trump: str,
                        legal_at_answer: Iterable[str]) -> tuple[str, ...]:
    return tuple(call[1] for call in legal_at_answer
                 if call[0] == '6' and call[1] in 'CDHS'
                 and call[1] != trump
                 and bid_rank(answer) < bid_rank(call)
                 < bid_rank(invitation))


def high_answer_invitations(auction, frame: OrdinaryRKCBFrame | None,
                            answer_call: str | None = None
                            ) -> tuple[str, ...]:
    if not is_high_answer(frame):
        return ()
    answer = answer_call or frame.answer_call
    if answer is None:
        return ()
    rejection = '6' + frame.trump
    if not is_call_legal(auction, rejection):
        return ()
    return tuple(call for call in legal_calls(auction)
                 if call[0] == '6' and call[1] in 'CDHS'
                 and call[1] != frame.trump
                 and bid_rank(answer) < bid_rank(call)
                 < bid_rank(rejection))


def lowest_counterinvite_king(hand: Hand | None,
                              frame: OrdinaryRKCBFrame, auction
                              ) -> str | None:
    if hand is None:
        return None
    calls = [f'6{suit}' for suit in 'CDHS'
             if suit != frame.trump
             and suit not in frame.not_required_kings
             and hand.contains_rank(suit, 'K')
             and is_call_legal(auction, f'6{suit}')
             and bid_rank(f'6{suit}') < bid_rank(f'6{frame.trump}')]
    return min(calls, key=bid_rank) if calls else None
