"""Shared keycard-answer classification and five-of-trump stop geometry.

An artificial keycard answer never defines the contract strain or the trump.
The asker may still stop in five of the agreed trump: if the answer itself is
that call, the stop is Pass; otherwise it is the five-level trump bid.  This
module owns only that shared geometry and the non-contractual classification.
"""

from __future__ import annotations

NON_CONTRACTUAL_ACTS = frozenset({
    'keycard_answer', 'queen_answer', 'king_answer', 'relay',
})
NON_CONTRACTUAL_ACTION_MARKERS = (
    'keycard_answer', 'queen_answer', 'king_answer', 'relay_to_five_notrump',
    'forced_relay_completion', 'relay_king_show',
)


def is_non_contractual(meaning: dict | None) -> bool:
    if not isinstance(meaning, dict):
        return False
    if meaning.get('contract_effect') == 'none':
        return True
    if set(meaning.get('call_act_types', ()) or ()) & NON_CONTRACTUAL_ACTS:
        return True
    action = str(meaning.get('action_type') or '')
    return any(marker in action for marker in NON_CONTRACTUAL_ACTION_MARKERS)


def five_of_trump(trump: str) -> str:
    return '5' + trump


def stop_candidate_call(auction, trump: str, last_call: str | None) -> str | None:
    """Pass when five of trumps is already the last call, else bid it."""
    game = five_of_trump(trump)
    if last_call == game:
        return 'P'
    return game


def is_stop_target(call: str, trump: str) -> bool:
    return call in ('P', five_of_trump(trump))


def stop_meaning(trump: str) -> dict:
    return {
        'nature_labels': ['natural'],
        'call_act_types': ['signoff', 'final_placement'],
        'action_type': 'keycard_five_of_trump_signoff',
        'target_suit': trump,
        'agreed_suit': trump,
        'purpose_completed': True,
    }


def small_slam_meaning(trump: str) -> dict:
    return {
        'nature_labels': ['natural'],
        'call_act_types': ['signoff', 'final_placement'],
        'action_type': 'keycard_small_slam_placement',
        'target_suit': trump,
        'agreed_suit': trump,
        'purpose_completed': True,
    }


def last_non_pass(auction) -> str | None:
    for call in reversed(auction.calls):
        if call not in ('P', 'X', 'R'):
            return call
    return None


def possible_missing_counts(own_keycards: int, counts, total_keycards: int
                            ) -> set[int]:
    missing = set()
    for count in counts:
        value = total_keycards - own_keycards - count
        if 0 <= value <= total_keycards:
            missing.add(value)
    return missing


def stop_required(missing: int, trump_queen: bool | None) -> bool:
    """The owner's stopping rule: 2+ keycards, or 1 keycard plus no Q."""
    return missing >= 2 or (missing == 1 and trump_queen is False)


def placement_required(missing: int, trump_queen: bool | None) -> bool:
    if missing == 0:
        return True
    return missing == 1 and trump_queen is True


def keycard_rank(call: str) -> int:
    return bid_rank(call)
