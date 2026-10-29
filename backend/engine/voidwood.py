"""Pure Voidwood (void-showing keycard) helpers.

The gadget owns only authored meanings and state effects. All legal-call
arithmetic, the five-step answer map, and the worst-case landing-level safety
check live here so the same rules can be tested without a profile and reused
from any confirmed-trump auction.
"""

from __future__ import annotations

from dataclasses import dataclass

from .call_space import contract_at_rank, contract_rank
from .cards import Hand
from .legality import is_call_legal, legal_calls


TOTAL_EFFECTIVE_KEYCARDS = 4
SMALL_SLAM_MINIMUM = 3


@dataclass(frozen=True)
class VoidwoodContext:
    trump: str
    void: str
    ask: str
    own_effective_keycards: int


@dataclass(frozen=True)
class VoidwoodSafety:
    safe: bool
    reason: str
    forced_six_answers: tuple[str, ...] = ()


def effective_keycards(hand: Hand, trump: str, void: str) -> int:
    """Keycards excluding the void suit's ace, counting the trump king."""
    return hand.keycard_count(trump, excluded_suit=void)


def answer_bids(ask: str) -> tuple[str, ...]:
    """The next five contract bids after the ask, or an empty tuple."""
    rank = contract_rank(ask)
    answers = tuple(contract_at_rank(rank + step)
                    for step in range(1, 6))
    if any(answer is None for answer in answers):
        return ()
    return answers  # type: ignore[return-value]


def voidwood_jump(auction, *, trump: str, void: str) -> str | None:
    """The legal one-level jump in the void suit, or None.

    The jump is one full level above the cheapest legal call in the void
    strain. It must be 4S or higher and leave five answer steps.
    """
    if trump not in 'CDHS' or void not in 'CDHS' or void == trump:
        return None
    cheapest = _cheapest_call(auction, void)
    if cheapest is None:
        return None
    level = int(cheapest[0]) + 1
    if level > 7:
        return None
    jump = str(level) + void
    if not is_call_legal(auction, jump):
        return None
    if contract_rank(jump) < contract_rank('4S'):
        return None
    if len(answer_bids(jump)) != 5:
        return None
    return jump


def is_safe_voidwood_ask(
    ask: str,
    *,
    trump: str,
    own_effective_keycards: int,
    total_effective: int = TOTAL_EFFECTIVE_KEYCARDS,
) -> VoidwoodSafety:
    """Reject an ask whose forced-six answers can leave two keycards missing."""
    answers = answer_bids(ask)
    if len(answers) != 5:
        return VoidwoodSafety(False, 'Fewer than five answer steps remain')
    remaining = total_effective - own_effective_keycards
    if remaining < 0:
        return VoidwoodSafety(False, 'Own keycard count exceeds the total')
    categories = (
        (0, 3),
        (1, 4),
        (1, 4),
        (2,),
        (2,),
    )
    five_trump = contract_rank('5' + trump)
    forced = []
    for bid, counts in zip(answers, categories):
        possible = tuple(sorted(count for count in counts if 0 <= count <= remaining))
        if not possible:
            continue
        if contract_rank(bid) <= five_trump:
            continue
        forced.append(bid)
        for partner in possible:
            if own_effective_keycards + partner < SMALL_SLAM_MINIMUM:
                return VoidwoodSafety(
                    False,
                    f'Answer {bid} forces six with as few as '
                    f'{own_effective_keycards + partner} effective keycards',
                    tuple(forced))
    return VoidwoodSafety(True, 'Every forced-six answer guarantees three keycards',
                          tuple(forced))


def context_validation(
    *,
    trump_state,
    keycard_pending: bool,
    hand: Hand | None,
    trump: str,
    void: str,
) -> str | None:
    """Return a named ineligibility reason, or None when Voidwood is legal."""
    if keycard_pending:
        return 'A keycard inquiry is already pending'
    if trump_state is None or getattr(trump_state, 'status', None) != 'agreed':
        return 'No confirmed trump suit'
    if getattr(trump_state, 'suit', None) != trump:
        return 'Confirmed trump conflicts with the requested trump'
    if trump not in 'CDHS' or void not in 'CDHS':
        return 'Voidwood suits must be C, D, H or S'
    if void == trump:
        return 'The void suit cannot be trumps'
    if hand is None or hand.length(void) != 0:
        return 'The asker is not void in the bid suit'
    return None


def _cheapest_call(auction, strain: str) -> str | None:
    for call in legal_calls(auction):
        if call == 'P' or call in ('X', 'R'):
            continue
        if call[1:] == strain:
            return call
    return None
