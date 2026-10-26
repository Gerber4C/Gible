"""Seeded, bounded deal search using the ordinary profile selector.

The generator owns a full deal. Each bidding decision receives only its actor's
hand and public auction context. A requested call is matched against the actual
selected candidate, never forced into an ineligible hand.
"""

from __future__ import annotations

import random
import time

from .auction import Auction
from .calls import is_contract_bid, normalize_call
from .cards import Hand
from .matcher import matches_context
from .model import PartnershipProfile
from .selector import choose_bid


SEATS = 'nesw'
PARTNER = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}
RANKS = 'AKQJT98765432'
MAX_ATTEMPTS = 5000
MAX_SECONDS = 8


def _authored_call(profile: PartnershipProfile, auction: Auction, call: str) -> bool:
    return any(spec.call == call and not spec.default_policy
               and not spec.meaning.to_dict().get('historical_only')
               and matches_context(spec.context, auction)
               for spec in profile.call_specifications)


def _deal(rng: random.Random) -> dict[str, Hand]:
    cards = [(suit, rank) for suit in 'SHDC' for rank in RANKS]
    rng.shuffle(cards)
    holdings = {seat: {suit: '' for suit in 'SHDC'} for seat in SEATS}
    for index, (suit, rank) in enumerate(cards):
        holdings[SEATS[index % 4]][suit] += rank
    order = {rank: index for index, rank in enumerate(RANKS)}
    return {seat: Hand.from_dict({
        'spades': ''.join(sorted(held['S'], key=order.get)),
        'hearts': ''.join(sorted(held['H'], key=order.get)),
        'diamonds': ''.join(sorted(held['D'], key=order.get)),
        'clubs': ''.join(sorted(held['C'], key=order.get)),
    }, validate_count=True) for seat, held in holdings.items()}


def _compact(hand: Hand) -> str:
    return ''.join(suit + (hand.holding(suit) or '-') for suit in 'SHDC')


def generate_training_deal(
    profile: PartnershipProfile,
    *,
    opening: str,
    response: str | None = None,
    opener: str = 'ns',
    vulnerability: str = 'none',
    seed: int | None = None,
    max_attempts: int = 2000,
    max_seconds: float = MAX_SECONDS,
) -> dict:
    try:
        opening = normalize_call(opening)
        response = normalize_call(response) if response else None
    except ValueError as exc:
        raise ValueError(f'Invalid training call: {exc}') from exc
    if not is_contract_bid(opening):
        raise ValueError('opening must be a contract bid')
    if opener not in (*SEATS, 'ns', 'ew', 'random'):
        raise ValueError('opener must be a seat, ns, ew, or random')
    if isinstance(max_attempts, bool) or not isinstance(max_attempts, int) or not 1 <= max_attempts <= MAX_ATTEMPTS:
        raise ValueError(f'max_attempts must be from 1 to {MAX_ATTEMPTS}')
    if isinstance(seed, bool) or (seed is not None and not isinstance(seed, int)):
        raise ValueError('seed must be an integer')
    if isinstance(max_seconds, bool) or not isinstance(max_seconds, (int, float)) or not 0 < max_seconds <= MAX_SECONDS:
        raise ValueError(f'max_seconds must be positive and at most {MAX_SECONDS}')
    if vulnerability not in ('none', 'ns', 'ew', 'both'):
        raise ValueError('Invalid vulnerability')

    seed = random.SystemRandom().randrange(2**63) if seed is None else seed
    rng = random.Random(seed)
    opener_choices = {'random': SEATS, 'ns': 'ns', 'ew': 'ew'}
    chosen_opener = rng.choice(opener_choices[opener]) if opener in opener_choices else opener
    before = Auction.parse('', dealer=chosen_opener, vulnerability=vulnerability)
    after = Auction.parse((opening, 'P'), dealer=chosen_opener, vulnerability=vulnerability)
    if not _authored_call(profile, before, opening):
        raise ValueError(f'unsupported opening {opening} for this profile and first-seat auction')
    if response is not None and not _authored_call(profile, after, response):
        raise ValueError(f'unsupported response {response} after {opening} for this profile')

    deadline = time.monotonic() + max_seconds
    environment = {'dealer': chosen_opener, 'vulnerability': vulnerability, 'scoring': 'IMP'}
    attempts = 0
    while attempts < max_attempts and time.monotonic() < deadline:
        attempts += 1
        hands = _deal(rng)
        first = choose_bid(profile, before, hands[chosen_opener], environment)
        if first.call != opening or first.selected_candidate is None or first.selected_candidate.source_kind == 'heuristic_fallback':
            continue
        calls = [opening]
        if response is not None:
            partner = PARTNER[chosen_opener]
            second = choose_bid(profile, after, hands[partner], environment)
            if second.call != response or second.selected_candidate is None or second.selected_candidate.source_kind == 'heuristic_fallback':
                continue
            calls.extend(('P', response))
        return {
            'status': 'matched', 'profile': profile.id, 'profile_version': profile.version,
            'opening': opening, 'response': response, 'opener': chosen_opener,
            'dealer': chosen_opener, 'vulnerability': vulnerability, 'seed': seed,
            'attempts': attempts, 'calls': calls,
            'hands': {seat: _compact(hand) for seat, hand in hands.items()},
        }
    return {
        'status': 'not_found', 'profile': profile.id, 'profile_version': profile.version,
        'opening': opening, 'response': response, 'opener': chosen_opener,
        'dealer': chosen_opener, 'vulnerability': vulnerability, 'seed': seed,
        'attempts': attempts, 'calls': [], 'hands': None,
        'message': 'No matching deal was found within the attempt/time budget; the requested calls were not relaxed.',
    }
