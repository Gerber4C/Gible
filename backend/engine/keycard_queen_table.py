"""Ordinary-RKCB queen-ask geometry and five-spade relay roles.

This module is deliberately data-only: it names the calls defined by the
profile instead of guessing from generic tags.

Queen-ask calls by trump and primary category:

    C: 1/4 -> 5D, 0/3 -> 5H
    D: 1/4 -> 5H, 0/3 -> 5H
    H: 1/4 -> 5D, 0/3 -> 5S
    S: 1/4 -> 5D, 0/3 -> 5H

Five-spade role:

* spades are trumps -> 5S is the five-of-trump stop;
* hearts are trumps and the answer was 5D -> 5S is the queen ask;
* the answer itself was 5S -> 5S cannot be used again;
* otherwise -> 5S is the relay to 5NT.

When five of trumps is still available, the relay is "usually unnecessary";
simulation may still prefer 5NT over 5T.  When five of trumps has already
been passed, the relay is available.  A call that is itself a queen ask, a
five-of-trump stop, or the current answer is never a relay.
"""

from __future__ import annotations

from dataclasses import dataclass

from .rkcb_continuation import bid_rank

TRUMPS = 'CDHS'
QUEEN_ASKS = {
    'C': {'1/4': '5D', '0/3': '5H'},
    'D': {'1/4': '5H', '0/3': '5H'},
    'H': {'1/4': '5D', '0/3': '5S'},
    'S': {'1/4': '5D', '0/3': '5H'},
}

RELAY_AVAILABLE = '可用'
RELAY_UNAVAILABLE = '不可用'
RELAY_USUALLY_UNNECESSARY = '通常不必要'


@dataclass(frozen=True)
class QueenAnswerGeometry:
    trump: str
    category: str
    queen_ask: str
    no_queen: str
    side_king_answers: tuple[str, ...]
    queen_no_king_answers: tuple[str, ...]


def queen_ask(trump: str, category: str) -> str | None:
    return QUEEN_ASKS.get(trump, {}).get(category)


def nearest_trump_above(call: str, trump: str) -> str | None:
    candidates = [f'5{trump}', f'6{trump}']
    legal = [item for item in candidates if bid_rank(item) > bid_rank(call)]
    return min(legal, key=bid_rank) if legal else None


def side_king_answers(trump: str, qask: str) -> tuple[str, ...]:
    six_trump = f'6{trump}'
    result = []
    for suit in 'CDHS':
        if suit == trump:
            continue
        call = f'6{suit}'
        if bid_rank(qask) < bid_rank(call) < bid_rank(six_trump):
            result.append(call)
    return tuple(sorted(result, key=bid_rank))


def queen_no_king_answers(trump: str, qask: str) -> tuple[str, ...]:
    no_queen = nearest_trump_above(qask, trump)
    if no_queen == f'6{trump}':
        return ('5N',)
    return (f'6{trump}', '5N')


def queen_answer_geometry(trump: str, category: str) -> QueenAnswerGeometry | None:
    qask = queen_ask(trump, category)
    no_queen = nearest_trump_above(qask, trump) if qask else None
    if qask is None or no_queen is None:
        return None
    return QueenAnswerGeometry(
        trump=trump,
        category=category,
        queen_ask=qask,
        no_queen=no_queen,
        side_king_answers=side_king_answers(trump, qask),
        queen_no_king_answers=queen_no_king_answers(trump, qask),
    )


def five_spade_role(answer: str, trump: str) -> str:
    if trump == 'S':
        return 'stop'
    if answer == '5S':
        return 'unavailable'
    if trump == 'H' and answer == '5D':
        return 'queen_ask'
    return 'relay'


def five_spade_relay_status(answer: str, trump: str,
                            five_trump_available: bool) -> str:
    """Status of 5S->5NT as a rescue, not of 5S as a natural stop."""
    if answer == '5S':
        return RELAY_UNAVAILABLE
    role = five_spade_role(answer, trump)
    if role != 'relay':
        return RELAY_UNAVAILABLE
    return (RELAY_USUALLY_UNNECESSARY if five_trump_available
            else RELAY_AVAILABLE)
