"""Public reference-suit state for each partnership.

This state describes the suit used to interpret later conventions.  It does
not choose a final contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .legality import SIDE_BY_SEAT


SUITS = frozenset(('C', 'D', 'H', 'S'))


@dataclass(frozen=True)
class TrumpState:
    status: str = 'unset'
    suit: str | None = None
    proposed_by: str | None = None
    origin: dict[str, Any] | None = None
    attributes: dict[str, Any] | None = None


def is_transition_effect(effect: Any) -> bool:
    if hasattr(effect, 'to_dict'):
        effect = effect.to_dict()
    if 'state' in effect:
        effect = effect['state']
    if 'state_update' in effect:
        effect = effect['state_update']
    return effect.get('key') == 'trump_state' and effect.get('transition') in ('maintain', 'replace')


def partner_turn(state: TrumpState, seat: str) -> bool:
    return (state.status == 'provisional' and state.proposed_by is not None
            and seat != state.proposed_by and SIDE_BY_SEAT[seat] == SIDE_BY_SEAT[state.proposed_by])


def promote(state: TrumpState, seat: str) -> TrumpState:
    if partner_turn(state, seat):
        return TrumpState('agreed', state.suit, None, state.origin, state.attributes)
    return state


def transition(state: TrumpState, effect: dict[str, Any], seat: str, origin: dict[str, Any]) -> TrumpState:
    action = effect.get('transition')
    if action == 'maintain':
        if state.status != 'provisional':
            raise ValueError('maintain requires provisional trump state')
        return state
    status = 'agreed' if effect.get('key') == 'agreed_suit' else effect.get('status')
    if status not in ('unset', 'provisional', 'agreed'):
        raise ValueError(f'Invalid trump status: {status}')
    suit = effect.get('suit')
    if status != 'unset' and suit not in SUITS:
        raise ValueError(f'Invalid trump suit: {suit}')
    if action == 'replace' and state.status == 'unset':
        raise ValueError('replace requires existing trump state')
    attributes = {key: value for key, value in effect.items()
                  if key not in ('key', 'transition') and (key != 'status' or effect.get('key') == 'agreed_suit')}
    return TrumpState(status, suit if status != 'unset' else None,
                      seat if status == 'provisional' else None, origin, attributes)
