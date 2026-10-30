"""Immutable public evidence for derived bidding meanings.

This module never reads private cards or private purposes. It extracts only
what replay has published: natural suits, supports, enemy suits, trump state,
and the legal calls below 4NT.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .legality import SIDE_BY_SEAT, is_call_legal, last_contract_state, legal_calls
from .rkcb_continuation import bid_rank, public_minimum_length


@dataclass(frozen=True)
class ClassifiedCall:
    call: str
    kind: str
    strain: str
    natural: bool = False
    establishes_trump: str | None = None


@dataclass(frozen=True)
class DerivedEvidence:
    actor: str
    side: str
    contract: str | None
    contract_level: int
    contract_strain: str | None
    agreed_trump: str | None
    provisional_trump: str | None
    plausible_trumps: tuple[str, ...]
    natural_suits: dict[str, tuple[str, ...]] = field(default_factory=dict)
    guaranteed_long_suits: dict[str, tuple[str, ...]] = field(default_factory=dict)
    supported_suits: dict[str, tuple[str, ...]] = field(default_factory=dict)
    enemy_suits: tuple[str, ...] = ()
    forcing: bool = False
    three_notrump_available: bool = False
    classified_calls: tuple[ClassifiedCall, ...] = ()
    conflicts: tuple[dict[str, Any], ...] = ()
    explicit_calls: tuple[str, ...] = ()


def collect_evidence(profile, auction, trace) -> DerivedEvidence:
    actor = auction.actor_to_call
    side = SIDE_BY_SEAT[actor]
    entries = [entry for entry in trace.applied_meanings
               if entry.get('index', len(auction.calls)) < len(auction.calls)]
    natural = {name: set() for name in ('ns', 'ew')}
    guaranteed = {name: set() for name in ('ns', 'ew')}
    supported = {name: set() for name in ('ns', 'ew')}
    forcing = False
    for entry in entries:
        meaning = entry.get('public_meaning', {}) or {}
        entry_side = SIDE_BY_SEAT[entry['seat']]
        acts = set(meaning.get('call_act_types', ()) or ())
        labels = set(meaning.get('nature_labels', ()) or ())
        suit = meaning.get('target_suit')
        if 'natural' in labels and suit is not None and suit in 'CDHS':
            natural[entry_side].add(suit)
            if public_minimum_length(meaning, suit) >= 4:
                guaranteed[entry_side].add(suit)
        agreed = meaning.get('agreed_suit') or meaning.get('support_suit')
        if agreed is not None and agreed in 'CDHS':
            supported[entry_side].add(agreed)
        if acts & {'raise', 'support', 'fit'} and suit is not None and suit in 'CDHS':
            supported[entry_side].add(suit)
        if 'forcing' in meaning.get('forcing_status', '') or 'game_forcing' in acts:
            forcing = True

    own_natural = tuple(sorted(natural[side]))
    enemy_suits = tuple(sorted(natural['ew' if side == 'ns' else 'ns']))
    trump_state = trace.trump_state(side)
    agreed = trump_state.suit if trump_state.status == 'agreed' else None
    provisional = trump_state.suit if trump_state.status == 'provisional' else None
    if agreed:
        plausible = (agreed,)
    elif provisional:
        plausible = (provisional,)
    else:
        candidates = set(supported[side]) | set(guaranteed[side])
        plausible = tuple(sorted(candidates, key='CDHS'.index))

    conflicts = []
    if len(plausible) > 2:
        conflicts.append({
            'code': 'TOO_MANY_PLAUSIBLE_TRUMPS',
            'plausible_trumps': list(plausible),
            'message': 'Derived semantics supports at most two plausible trumps',
        })

    contract = last_contract_state(auction)
    level = int(contract.call[0]) if contract is not None else 0
    strain = contract.call[1] if contract is not None else None
    if strain == 'N':
        strain = 'NT'

    below_four_notrump = []
    for call in legal_calls(auction):
        if call in ('P', 'X', 'R') or call[1] not in 'CDHS':
            continue
        if bid_rank(call) >= bid_rank('4NT'):
            continue
        below_four_notrump.append(call)

    classified = tuple(
        _classify(call, side, plausible, agreed, supported[side],
                  natural[side], enemy_suits, own_natural)
        for call in below_four_notrump)

    if is_call_legal(auction, '3NT') or contract is not None and contract.call == '3N':
        three_notrump = True
    else:
        three_notrump = contract is not None and contract.call in ('3N', '3NT')

    explicit = tuple(spec.call for spec in profile.call_specifications
                     if spec.call in {item.call for item in classified})
    return DerivedEvidence(
        actor=actor, side=side,
        contract=contract.call if contract is not None else None,
        contract_level=level, contract_strain=strain,
        agreed_trump=agreed, provisional_trump=provisional,
        plausible_trumps=plausible,
        natural_suits={key: tuple(sorted(value)) for key, value in natural.items()},
        guaranteed_long_suits={key: tuple(sorted(value))
                               for key, value in guaranteed.items()},
        supported_suits={key: tuple(sorted(value)) for key, value in supported.items()},
        enemy_suits=enemy_suits,
        forcing=forcing,
        three_notrump_available=three_notrump,
        classified_calls=classified,
        conflicts=tuple(conflicts),
        explicit_calls=explicit,
    )


def _classify(call, side, plausible, agreed, supported, own_natural,
              enemy_suits, own_natural_order):
    suit = call[1]
    if agreed is None and suit in supported:
        return ClassifiedCall(call, 'raise', suit,
                              establishes_trump=suit)
    if suit in supported or suit == agreed:
        return ClassifiedCall(call, 'raise', suit,
                              establishes_trump=suit)
    if suit in enemy_suits:
        return ClassifiedCall(call, 'enemy_cue', suit)
    if suit in plausible and suit in own_natural:
        return ClassifiedCall(call, 'selector', suit,
                              establishes_trump=suit)
    if suit in 'CDHS':
        return ClassifiedCall(call, 'natural', suit, natural=True)
    return ClassifiedCall(call, 'unresolved', suit)
