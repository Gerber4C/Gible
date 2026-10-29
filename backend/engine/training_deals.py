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
MAX_SECONDS = 20


def _authored_call(profile: PartnershipProfile, auction: Auction, call: str) -> bool:
    from .candidate_generation import _condition_passes
    from .replay import active_environment_for, replay_auction

    trace = None
    environment = None
    for spec in profile.call_specifications:
        if spec.call != call or spec.default_policy:
            continue
        if spec.meaning.to_dict().get('historical_only'):
            continue
        if not matches_context(spec.context, auction):
            continue
        if spec.requires:
            if trace is None:
                trace = replay_auction(profile, auction)
                environment = active_environment_for(profile, None, auction)
            if not _condition_passes(spec.requires, auction, None,
                                     trace, environment):
                continue
        return True
    return False


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


SuitRanges = dict[str, tuple[int, int]]


def _length_ranges(raw, field: str) -> SuitRanges:
    """Normalise per-suit length ranges from letters or full suit names."""

    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ValueError(f'{field} must be an object of suit ranges')
    ranges: SuitRanges = {}
    for key, value in raw.items():
        suit = {'spades': 'S', 'hearts': 'H', 'diamonds': 'D', 'clubs': 'C'}.get(
            str(key).lower(), str(key).upper())
        if suit not in 'SHDC':
            raise ValueError(f'unknown suit in {field}: {key!r}')
        if isinstance(value, (list, tuple)) and len(value) == 2:
            low, high = value
        elif isinstance(value, int) and not isinstance(value, bool):
            low = high = value
        else:
            raise ValueError(f'{field} values must be an integer or a [min, max] pair')
        if (isinstance(low, bool) or isinstance(high, bool)
                or not isinstance(low, int) or not isinstance(high, int)
                or not 0 <= low <= high <= 13):
            raise ValueError(f'invalid {field} range for {suit}: {value!r}')
        ranges[suit] = (low, high)
    return ranges


def _responder_constraints(raw):
    """Validate responder HCP and four-suit length bounds, or return None."""

    if raw is None:
        return None
    if not isinstance(raw, dict):
        raise ValueError('responder must be an object')
    low = raw.get('min_hcp', 0)
    high = raw.get('max_hcp', 37)
    if (isinstance(low, bool) or isinstance(high, bool)
            or not isinstance(low, int) or not isinstance(high, int)
            or not 0 <= low <= high <= 37):
        raise ValueError('responder HCP bounds must be integers from 0 to 37')
    min_lengths = _length_ranges(raw.get('min_lengths'), 'responder min_lengths')
    max_lengths = _length_ranges(raw.get('max_lengths'), 'responder max_lengths')
    for suit in set(min_lengths) & set(max_lengths):
        if min_lengths[suit][0] > max_lengths[suit][0]:
            raise ValueError(f'responder {suit} min length exceeds max length')
    return {'min_hcp': low, 'max_hcp': high,
            'min_lengths': min_lengths, 'max_lengths': max_lengths}


def _responder_matches(hand: Hand, responder) -> bool:
    if responder is None:
        return True
    if not responder['min_hcp'] <= hand.hcp <= responder['max_hcp']:
        return False
    for suit in 'SHDC':
        length = hand.length(suit)
        low, _ = responder['min_lengths'].get(suit, (0, 13))
        _, high = responder['max_lengths'].get(suit, (0, 13))
        if not low <= length <= high:
            return False
    return True


def generate_training_deal(
    profile: PartnershipProfile,
    *,
    opening: str,
    response: str | None = None,
    opener: str = 'ns',
    vulnerability: str = 'none',
    responder: dict | None = None,
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
    responder = _responder_constraints(responder)
    if responder is None and profile.id == 'daqiush_2over1' and response in ('4C', '4D'):
        # South African Texas needs a six-card major; pre-constrain the
        # search instead of relying on a lucky random deal.
        suit = 'H' if response == '4C' else 'S'
        responder = {'min_hcp': 0, 'max_hcp': 37,
                     'min_lengths': {suit: (6, 13)}, 'max_lengths': {}}

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
        if not _responder_matches(hands[PARTNER[chosen_opener]], responder):
            continue
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
            'responder': responder,
            'dealer': chosen_opener, 'vulnerability': vulnerability, 'seed': seed,
            'attempts': attempts, 'calls': calls,
            'hands': {seat: _compact(hand) for seat, hand in hands.items()},
        }
    return {
        'status': 'not_found', 'profile': profile.id, 'profile_version': profile.version,
        'opening': opening, 'response': response, 'opener': chosen_opener,
        'responder': responder,
        'dealer': chosen_opener, 'vulnerability': vulnerability, 'seed': seed,
        'attempts': attempts, 'calls': [], 'hands': None,
        'message': 'No matching deal was found within the attempt/time budget; the requested calls were not relaxed.',
    }
