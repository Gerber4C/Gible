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
from .rkcb_continuation import public_minimum_length


TOTAL_EFFECTIVE_KEYCARDS = 4
SMALL_SLAM_MINIMUM = 3
PARTNER = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}


def current_voidwood_trump(trace, actor: str) -> str | None:
    """Return the latest reference trump, agreed or provisional.

    A provisional support cue may be converted to agreed by the Voidwood ask
    itself; a historical agreement must never be used.
    """
    side = 'ns' if actor in 'ns' else 'ew'
    state = trace.trump_state(side)
    if state.status in ('agreed', 'provisional'):
        return state.suit
    return None


def inferred_voidwood_trump(auction, trace) -> tuple[str, int] | None:
    """Infer a global Voidwood trump and partner's likely minimum length.

    The default is partner's last natural suit.  If partner's last non-pass
    call was notrumps, use the acting side's own last natural suit instead.
    The caller must still combine this with its own length to decide whether
    the likely fit is playable.
    """
    actor = auction.actor_to_call
    partner = PARTNER.get(actor)
    if partner is None:
        return None

    last_partner = _last_non_pass(auction, partner)
    if last_partner is not None and last_partner[1][1:] == 'N':
        own = _last_natural_suit(auction, trace, actor)
        if own is None:
            return None
        suit = own[1][1]
        return suit, _partner_guaranteed_length(trace, partner, suit)

    natural = _last_natural_suit(auction, trace, partner)
    if natural is None:
        return None
    _, call, meaning = natural
    suit = call[1]
    return suit, _guaranteed_length(meaning, suit, call)


def _last_non_pass(auction, seat: str):
    for index in range(len(auction.calls) - 1, -1, -1):
        call = auction.calls[index]
        if call in ('P', 'X', 'R'):
            continue
        if auction.actor_at(index) == seat:
            return index, call
    return None


def _last_natural_suit(auction, trace, seat: str):
    for index in range(len(auction.calls) - 1, -1, -1):
        call = auction.calls[index]
        if auction.actor_at(index) != seat:
            continue
        if (call in ('P', 'X', 'R') or len(call) != 2
                or call[1] not in 'CDHS'):
            continue
        meaning = _meaning_at(trace, index)
        if 'natural' in meaning.get('nature_labels', ()):
            return index, call, meaning
    return None


def _meaning_at(trace, index: int) -> dict:
    for entry in trace.applied_meanings:
        if entry.get('index') == index:
            return entry.get('public_meaning', {}) or {}
    return {}


def _guaranteed_length(meaning: dict, suit: str, call: str) -> int:
    length = public_minimum_length(meaning, suit)
    if length > 0:
        return length
    if meaning.get('target_suit') == suit:
        for key in ('minimum_length', 'support_length_min'):
            value = meaning.get(key)
            if isinstance(value, int) and value > 0:
                return value
    if 'natural' in meaning.get('nature_labels', ()) and len(call) == 2:
        if int(call[0]) >= 3:
            return 4
        return 3 if suit in 'HS' else 4
    return 0


def _partner_guaranteed_length(trace, partner: str, suit: str) -> int:
    best = 0
    for entry in trace.applied_meanings:
        if entry.get('seat') != partner:
            continue
        meaning = entry.get('public_meaning', {}) or {}
        if (meaning.get('target_suit') != suit
                and meaning.get('agreed_suit') != suit
                and public_minimum_length(meaning, suit) <= 0):
            continue
        best = max(best, _guaranteed_length(
            meaning, suit, entry.get('call', '')))
    return best



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
