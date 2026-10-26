"""Bounded, information-safe deal sampling for offline analysis.

Only the acting hand and explicitly published numeric seat constraints enter
this module. Deriving those constraints from public auction meanings belongs to
the caller; this module must never inspect an actual concealed hand or a
private candidate condition.
"""

from __future__ import annotations

from dataclasses import dataclass
import random
import time
from typing import Mapping

from .cards import Hand, SUITS, normalize_suit_name


SEATS = 'nesw'
RANKS = 'AKQJT98765432'
MAX_ATTEMPTS = 50000
MAX_SECONDS = 8.0
MAX_SAMPLES = 100
_FIELDS = frozenset({'min_hcp', 'max_hcp', 'min_lengths', 'max_lengths'})


@dataclass(frozen=True)
class SamplingResult:
    deals: tuple[dict[str, Hand], ...]
    attempts: int
    seed: int


class SamplingExhausted(RuntimeError):
    """The requested sample count could not be reached within its budget."""

    def __init__(self, attempts: int, found: int):
        self.attempts = attempts
        self.found = found
        super().__init__(f'Sampling exhausted after {attempts} attempts; found {found} deals')


def _bounded_int(value: object, name: str, low: int, high: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
        raise ValueError(f'{name} must be an integer from {low} to {high}')
    return value


def _normalize_constraints(public_constraints: Mapping | None) -> dict[str, dict]:
    if public_constraints is None:
        public_constraints = {}
    if not isinstance(public_constraints, Mapping):
        raise ValueError('public_constraints must be a seat mapping')
    result = {seat: {'min_hcp': 0, 'max_hcp': 40,
                     'min_lengths': {suit: 0 for suit in SUITS},
                     'max_lengths': {suit: 13 for suit in SUITS}}
              for seat in SEATS}
    for seat, raw in public_constraints.items():
        if seat not in SEATS or not isinstance(raw, Mapping):
            raise ValueError(f'unsupported public constraint seat: {seat}')
        unknown = set(raw) - _FIELDS
        if unknown:
            raise ValueError(f'unsupported public constraint: {sorted(unknown)}')
        bounds = result[seat]
        for field in ('min_hcp', 'max_hcp'):
            if field in raw:
                bounds[field] = _bounded_int(raw[field], field, 0, 40)
        for field in ('min_lengths', 'max_lengths'):
            if field not in raw:
                continue
            if not isinstance(raw[field], Mapping):
                raise ValueError(f'{field} must be a suit mapping')
            seen = set()
            for suit, value in raw[field].items():
                normalized = normalize_suit_name(suit)
                if normalized in seen:
                    raise ValueError(f'duplicate public constraint suit: {normalized}')
                seen.add(normalized)
                bounds[field][normalized] = _bounded_int(value, field, 0, 13)
        if bounds['min_hcp'] > bounds['max_hcp']:
            raise ValueError(f'contradictory HCP bounds for {seat}')
        if any(bounds['min_lengths'][suit] > bounds['max_lengths'][suit] for suit in SUITS):
            raise ValueError(f'contradictory suit bounds for {seat}')
        if sum(bounds['min_lengths'].values()) > 13 or sum(bounds['max_lengths'].values()) < 13:
            raise ValueError(f'contradictory total lengths for {seat}')
    return result


def _check_feasibility(bounds: dict[str, dict], acting_seat: str, acting_hand: Hand) -> None:
    actor = bounds[acting_seat]
    if not actor['min_hcp'] <= acting_hand.hcp <= actor['max_hcp']:
        raise ValueError('acting hand contradicts public HCP bounds')
    for suit in SUITS:
        if not actor['min_lengths'][suit] <= acting_hand.length(suit) <= actor['max_lengths'][suit]:
            raise ValueError('acting hand contradicts public suit bounds')
        remainder = 13 - acting_hand.length(suit)
        other_seats = [seat for seat in SEATS if seat != acting_seat]
        if (sum(bounds[seat]['min_lengths'][suit] for seat in other_seats) > remainder
                or sum(bounds[seat]['max_lengths'][suit] for seat in other_seats) < remainder):
            raise ValueError(f'public suit bounds contradict available {suit}')
    remainder_hcp = 40 - acting_hand.hcp
    other_seats = [seat for seat in SEATS if seat != acting_seat]
    if (sum(bounds[seat]['min_hcp'] for seat in other_seats) > remainder_hcp
            or sum(bounds[seat]['max_hcp'] for seat in other_seats) < remainder_hcp):
        raise ValueError('public HCP bounds contradict available points')


def _cards_in(hand: Hand) -> set[tuple[str, str]]:
    return {(suit, rank) for suit in SUITS for rank in hand.holding(suit)}


def _hand_from_cards(cards: list[tuple[str, str]]) -> Hand:
    holdings = {suit: '' for suit in SUITS}
    order = {rank: index for index, rank in enumerate(RANKS)}
    for suit, rank in cards:
        holdings[suit] += rank
    return Hand.from_dict({suit: ''.join(sorted(holdings[suit], key=order.get))
                           for suit in SUITS}, validate_count=True)


def _matches(hand: Hand, bounds: dict) -> bool:
    return (bounds['min_hcp'] <= hand.hcp <= bounds['max_hcp']
            and all(bounds['min_lengths'][suit] <= hand.length(suit) <= bounds['max_lengths'][suit]
                    for suit in SUITS))


def sample_deals(
    acting_seat: str,
    acting_hand: Hand | str,
    *,
    public_constraints: Mapping | None = None,
    public_evidence: object | None = None,
    sample_count: int = 1,
    seed: int | None = None,
    max_attempts: int = 5000,
    max_seconds: float = MAX_SECONDS,
) -> SamplingResult:
    """Sample full deals consistent with the acting hand and public bounds.

    `public_constraints` maps seat letters to optional `min_hcp`, `max_hcp`,
    `min_lengths`, and `max_lengths`. Length mappings use suit names or letters.
    Impossible aggregate bounds raise ValueError; search budget exhaustion raises
    SamplingExhausted. Accepted deals are complete and must stay inside analysis.
    """
    if acting_seat not in SEATS:
        raise ValueError('acting_seat must be one of n, e, s, w')
    if isinstance(acting_hand, str):
        acting_hand = Hand.parse(acting_hand)
    if not isinstance(acting_hand, Hand):
        raise ValueError('acting_hand must be a Hand or compact string')
    acting_hand.validate(validate_count=True)
    if any(rank not in RANKS for suit in SUITS for rank in acting_hand.holding(suit)):
        raise ValueError('acting_hand must contain exact cards from the standard 52-card deck')
    _bounded_int(sample_count, 'sample_count', 1, MAX_SAMPLES)
    _bounded_int(max_attempts, 'max_attempts', 1, MAX_ATTEMPTS)
    if isinstance(seed, bool) or (seed is not None and not isinstance(seed, int)):
        raise ValueError('seed must be an integer')
    if (isinstance(max_seconds, bool) or not isinstance(max_seconds, (int, float))
            or not 0 < max_seconds <= MAX_SECONDS):
        raise ValueError(f'max_seconds must be positive and at most {MAX_SECONDS}')

    if public_evidence is not None:
        if public_constraints is not None:
            raise ValueError('provide public_evidence or public_constraints, not both')
        from .public_evidence import PublicEvidence
        if not isinstance(public_evidence, PublicEvidence):
            raise ValueError('public_evidence must be derived from replay')
        public_constraints = public_evidence.constraints
    bounds = _normalize_constraints(public_constraints)
    _check_feasibility(bounds, acting_seat, acting_hand)
    chosen_seed = random.SystemRandom().randrange(2**63) if seed is None else seed
    rng = random.Random(chosen_seed)
    known_cards = _cards_in(acting_hand)
    remaining = [(suit, rank) for suit in SUITS for rank in RANKS
                 if (suit, rank) not in known_cards]
    unknown_seats = [seat for seat in SEATS if seat != acting_seat]
    deadline = time.monotonic() + max_seconds
    deals = []
    attempts = 0
    while attempts < max_attempts and len(deals) < sample_count and time.monotonic() < deadline:
        attempts += 1
        rng.shuffle(remaining)
        deal = {acting_seat: acting_hand}
        for index, seat in enumerate(unknown_seats):
            deal[seat] = _hand_from_cards(remaining[index * 13:(index + 1) * 13])
        if (all(_matches(deal[seat], bounds[seat]) for seat in unknown_seats)
                and (public_evidence is None or public_evidence.accepts(deal))):
            deals.append(deal)
    if len(deals) < sample_count:
        raise SamplingExhausted(attempts, len(deals))
    return SamplingResult(tuple(deals), attempts, chosen_seed)
