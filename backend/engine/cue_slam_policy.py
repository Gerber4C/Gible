"""Owner-specified cue-bid continuation policy for slam exploration.

At a cue-bid continuation where partner's strength range is still unknown:

* If the slam qualifies even when partner brings no extra strength, provided
  the partnership keycards are sufficient (never missing two aces, never one
  ace together with the trump queen), ask 4NT for keycards.
* If the slam fails even when partner brings the extra-strength threshold
  (the tenth percentile of the sampled process hands plus two K-R points),
  place the game contract.  That game carries signoff meaning, and partner
  may still override it by simulating a qualifying slam.
* Otherwise continue cue-bidding.

DDS is only consulted when no cheaper deterministic test decides (the owner
rule: fall back to DDS only when no other means is available).  With a major
trump, cueing above 4M is allowed only when the sampled expected score beats
stopping in 4M/5M/6M.  With a minor trump, cueing above 5m to hunt for a
small slam is forbidden.

This module is intentionally information-safe: it only sees the acting hand
plus partner hands sampled from public evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence

from .cards import Hand
from .contract_evaluation import ContractTarget, compare_contract_targets
from .dds_adapter import calculate_available_table
from .hand_quality import assess_quality

CUE_ACT_TYPES = frozenset({'control_showing', 'slam_try'})
EXTRA_KR = 2.0
EXTRA_KR_MARGIN = 1.95
SLAM_QUALIFY_RATE = 0.5
_LEVEL_ORDER = 'CDHSN'


def _bid_rank(call: str) -> int:
    return int(call[0]) * 5 + _LEVEL_ORDER.index(call[1])


def cue_continuation(trace) -> tuple[dict, str] | None:
    """Return ``(partner_cue_entry, trump)`` when the last non-pass call is a cue."""

    last = None
    for entry in trace.applied_meanings:
        if entry['call'] != 'P':
            last = entry
    if last is None:
        return None
    meaning = last.get('public_meaning') or {}
    if not CUE_ACT_TYPES.intersection(meaning.get('call_act_types', ())):
        return None
    trump = meaning.get('agreed_suit') or meaning.get('target_suit')
    if not isinstance(trump, str) or trump not in 'CDHS':
        return None
    return last, trump


def strength_is_unknown(hcp_range: tuple[int, int] | None, *,
                        has_cue_bid: bool = False) -> bool:
    """Report whether partner's strength range is still unknown.

    A single exact HCP value is always known.  A one-point band (for example
    15-16) is known only after the player has already shown extra strength
    with a voluntary cue; before that it is still unknown.  Anything wider is
    unknown.
    """

    if hcp_range is None:
        return True
    low, high = hcp_range
    width = high - low
    if width <= 0:
        return False
    if width == 1:
        return not has_cue_bid
    return True


def cue_public_kr(previous: tuple[float, float | None],
                  *, forced_by_serious_3nt: bool = False
                  ) -> tuple[float, float | None]:
    """Derive the K-R range a cue-bid publishes.

    A cue forced by serious 3NT carries no new information, so its range is
    the player's previous range.  A voluntary cue promises two K-R points more
    than the previous call, raising the floor by two.  When the previous band
    is narrower than those two points (the ceiling sits below the raised
    floor), the cue instead publishes the upper half of the original band.
    """

    low, high = previous
    if forced_by_serious_3nt:
        return previous
    raised = low + EXTRA_KR
    if high is None:
        return raised, None
    if raised <= high:
        return raised, high
    return (low + high) / 2.0, high


def partner_promised_kr(trace, partner: str) -> float | None:
    """Return the largest K-R floor partner's calls published, if any."""

    best = None
    for entry in trace.applied_meanings:
        if entry.get('seat') != partner or entry.get('call') == 'P':
            continue
        value = (entry.get('public_meaning') or {}).get('min_kr')
        if value is not None and (best is None or value > best):
            best = value
    return best


def extra_kr_threshold(partner_kr: Sequence[float]) -> float:
    """Return the tenth-percentile process K-R plus two points."""

    if not partner_kr:
        return EXTRA_KR
    ordered = sorted(partner_kr)
    index = max(0, min(len(ordered) - 1, int(round(0.1 * (len(ordered) - 1)))))
    return ordered[index] + EXTRA_KR


def keycards_sufficient(own: Hand, partner: Hand, trump: str) -> bool:
    """Never missing two aces nor one ace together with the trump queen."""

    missing = 5 - own.keycard_count(trump) - partner.keycard_count(trump)
    if missing <= 0:
        return True
    if missing >= 2:
        return False
    queen_known = (own.contains_rank(trump, 'Q')
                   or partner.contains_rank(trump, 'Q'))
    return queen_known


@dataclass(frozen=True)
class CueDecision:
    call: str
    reason: str
    extra_kr_threshold: float
    no_extra_slam_rate: float | None = None
    extra_slam_rate: float | None = None
    expected_scores: dict | None = None


def _completion_rates(hand: Hand, trump: str, hands: Sequence[Hand],
                      solve_table: Callable,
                      deals: Sequence[dict] | None = None
                      ) -> tuple[dict[str, float], int]:
    if not hands:
        return {}, 0
    if deals is None:
        deals = tuple({'n': hand, 's': partner} for partner in hands)
    targets = (ContractTarget(4 if trump in 'HS' else 5, trump, 's'),
               ContractTarget(6, trump, 's'))
    estimates = compare_contract_targets(tuple(deals), targets,
                                         solve_table=solve_table)
    return {item.contract: item.completion_rate for item in estimates}, len(hands)


def decide_from_hands(
    hand: Hand,
    trump: str,
    partner_hands: Sequence[Hand],
    *,
    game_call: str,
    cue_calls: Iterable[str] = (),
    slam_threshold: float = SLAM_QUALIFY_RATE,
    solve_table: Callable = calculate_available_table,
    deals: Sequence[dict] | None = None,
    promised_kr: float | None = None,
) -> CueDecision:
    """Apply the cue-continuation policy to already-sampled partner hands."""

    partner_hands = tuple(partner_hands)
    if deals is not None:
        deals = tuple(deals)
    krs = [assess_quality(item)['kr_points'] for item in partner_hands]
    if promised_kr is not None:
        # Owner rule: extra strength means 1.95 K-R above the promised floor.
        threshold = promised_kr + EXTRA_KR_MARGIN
    else:
        threshold = extra_kr_threshold(krs)
    no_extra_index = [index for index, kr in enumerate(krs) if kr < threshold]
    with_extra_index = [index for index, kr in enumerate(krs) if kr >= threshold]

    # Deterministic keycard filter.  A hand that cannot reach sufficient
    # keycards is not a slam candidate, so it never justifies 4NT or a cue.
    no_extra_ok = [index for index in no_extra_index
                   if keycards_sufficient(hand, partner_hands[index], trump)]
    with_extra_ok = [index for index in with_extra_index
                     if keycards_sufficient(hand, partner_hands[index], trump)]

    def rates(indices):
        subset_hands = [partner_hands[index] for index in indices]
        subset_deals = ([deals[index] for index in indices]
                        if deals is not None else None)
        return _completion_rates(hand, trump, subset_hands, solve_table,
                                 deals=subset_deals)

    slam_call = f'6{trump}'

    if not no_extra_ok:
        # Even partner's minimum hands cannot supply enough keycards: the
        # slam is not qualifying without extra shape/keycards.  If extra
        # hands also fail keycards, place game; otherwise keep cueing.
        if not with_extra_ok:
            return CueDecision(game_call, 'keycards insufficient', threshold)
        rates_extra, _ = rates(with_extra_ok)
        extra_rate = rates_extra.get(slam_call, 0.0)
        if extra_rate < slam_threshold:
            return CueDecision(game_call, 'slam fails even with extra strength',
                               threshold, extra_slam_rate=extra_rate)
        return CueDecision(_preferred_cue(hand, trump, cue_calls),
                           'slam depends on partner extra strength',
                           threshold, extra_slam_rate=extra_rate)

    rates_no, _ = rates(no_extra_ok)
    no_extra_rate = rates_no.get(slam_call, 0.0)
    if no_extra_rate >= slam_threshold:
        # Qualifies without extra strength and keycards are sufficient: ask.
        return CueDecision('4N', 'slam qualifies without extra strength',
                           threshold, no_extra_slam_rate=no_extra_rate)

    if not with_extra_ok:
        return CueDecision(game_call, 'keycards insufficient with extra strength',
                           threshold, no_extra_slam_rate=no_extra_rate)

    rates_extra, _ = rates(with_extra_ok)
    extra_rate = rates_extra.get(slam_call, 0.0)
    if extra_rate < slam_threshold:
        return CueDecision(game_call, 'slam fails even with extra strength',
                           threshold, no_extra_slam_rate=no_extra_rate,
                           extra_slam_rate=extra_rate)
    return CueDecision(_preferred_cue(hand, trump, cue_calls),
                       'slam depends on partner extra strength', threshold,
                       no_extra_slam_rate=no_extra_rate,
                       extra_slam_rate=extra_rate)


def _preferred_cue(hand: Hand, trump: str, cue_calls: Iterable[str]) -> str:
    """Pick the lowest legal cue that does not break the owner's level caps."""

    legal = [call for call in cue_calls if '4' <= call[0] <= '6']
    for call in sorted(legal, key=_bid_rank):
        if not cue_allowed_above(trump, call):
            continue
        return call
    return 'P'


def cue_three_way(auction, trace) -> tuple[str, str] | None:
    """Return ``(trump, partner)`` when the general policy may override.

    The policy applies only after partner's cue, when partner's public HCP
    interval is still wide enough to be unknown.  A narrow band that partner
    has already narrowed by cueing counts as known and keeps the authored
    continuation.
    """

    context = cue_continuation(trace)
    if context is None:
        return None
    entry, trump = context
    partner = entry.get('seat')
    if partner not in 'nsew':
        return None
    low, high = partner_hcp_bounds(trace, partner)
    if not strength_is_unknown((low, high), has_cue_bid=True):
        return None
    return trump, partner


def signoff_override(trace, actor: str) -> tuple[str, str, str] | None:
    """Return ``(trump, signoff_bidder, signoff_call)`` after a cue signoff.

    The signoff is the game bid that follows the actor's own cue.  Partner may
    reject it when fresh simulation still shows a qualifying slam.
    """

    entries = [entry for entry in trace.applied_meanings
               if entry.get('call') != 'P']
    if len(entries) < 2:
        return None
    last, previous = entries[-1], entries[-2]
    last_meaning = last.get('public_meaning') or {}
    previous_meaning = previous.get('public_meaning') or {}
    if last.get('seat') == actor:
        return None
    if not {'signoff', 'final_placement'}.intersection(
            last_meaning.get('call_act_types', ())):
        return None
    if previous.get('seat') != actor:
        return None
    if not CUE_ACT_TYPES.intersection(
            previous_meaning.get('call_act_types', ())):
        return None
    trump = (previous_meaning.get('agreed_suit')
             or previous_meaning.get('target_suit'))
    if not isinstance(trump, str) or trump not in 'CDHS':
        return None
    return trump, last['seat'], last['call']


def cue_allowed_above(trump: str, call: str) -> bool:
    """Return whether a cue may be made at this level under the owner rule."""

    rank = _bid_rank(call)
    if trump in 'CD':
        # Never cue above 5m looking for a small slam.
        return rank <= _bid_rank('5' + trump)
    # A major trump may cue above 4M; the caller still needs a positive
    # simulated expectation, which the selection step enforces.
    return True


def partner_hcp_bounds(trace, partner: str) -> tuple[int, int]:
    """Collect the public HCP interval a seat has promised so far."""

    bounds = partner_constraints(trace, partner)
    return bounds['min_hcp'], bounds['max_hcp']


def partner_constraints(trace, partner: str) -> dict:
    """Collect public HCP and length bounds a seat has promised so far."""

    from .slam_intent import PARTNER_DEFAULT_MIN

    low, high = 0, 37
    min_lengths: dict[str, int] = {}
    max_lengths: dict[str, int] = {}
    for entry in trace.applied_meanings:
        if entry.get('seat') != partner or entry.get('call') == 'P':
            continue
        meaning = entry.get('public_meaning') or {}
        if meaning.get('hcp_min') is not None:
            low = max(low, meaning['hcp_min'])
        if meaning.get('hcp_max') is not None:
            high = min(high, meaning['hcp_max'])
        acts = meaning.get('call_act_types', ())
        if 'game_forcing' in acts or meaning.get('forcing') == 'game_forcing':
            # A game-forcing call guarantees at least opening values.
            low = max(low, PARTNER_DEFAULT_MIN)
        for suit, length in (meaning.get('min_lengths') or {}).items():
            if suit in 'SHDC':
                min_lengths[suit] = max(min_lengths.get(suit, 0), length)
        for suit, length in (meaning.get('max_lengths') or {}).items():
            if suit in 'SHDC':
                max_lengths[suit] = min(max_lengths.get(suit, 13), length)
    bounds = {'min_hcp': low, 'max_hcp': high}
    if min_lengths:
        bounds['min_lengths'] = min_lengths
    if max_lengths:
        bounds['max_lengths'] = max_lengths
    return bounds


def hand_would_bid_observed(profile, auction, hand: Hand, partner: str) -> bool:
    """Replay the auction and check a candidate hand makes partner's calls."""

    from .auction import Auction
    from .selector import choose_bid

    for index, call in enumerate(auction.calls):
        if call == 'P' or auction.actor_at(index) != partner:
            continue
        prefix = Auction(calls=auction.calls[:index], dealer=auction.dealer,
                         vulnerability=auction.vulnerability)
        if choose_bid(profile, prefix, hand).call != call:
            return False
    return True


def _process_seed(auction, hand: Hand) -> int:
    """Stable seed so a given auction and hand always sample the same deals."""

    from hashlib import sha256

    serial = (auction.canonical_key() + ':'
              + '.'.join(hand.holding(suit) for suit in 'SHDC'))
    return int.from_bytes(sha256(serial.encode('ascii')).digest()[:8], 'big')


def sample_process_hands(profile, auction, trace, actor_hand: Hand,
                         partner: str, *, count: int = 40, seed=None,
                         max_attempts: int = 4000,
                         max_seconds: float = 8.0,
                         extra_filter=None) -> tuple[Hand, ...]:
    """Infer partner's range by simulating what hands would bid this way.

    Candidate hands are drawn inside partner's public HCP and length bounds,
    then kept only when the authored candidates include partner's exact calls.
    The surviving hands replace any hard-coded range for later decisions.
    """

    from .auction import Auction
    from .candidate_generation import generate_candidates
    from .deal_sampler import sample_deals
    from .memory import SeatMemory
    from .replay import active_environment_for, replay_auction

    turns = [(index, auction.calls[index])
             for index in range(len(auction.calls))
             if auction.calls[index] != 'P'
             and auction.actor_at(index) == partner]
    if not turns:
        return ()

    # The prefix trace is public and hand-independent, so prepare it once.
    prepared = []
    for index, call in turns:
        prefix = Auction(calls=auction.calls[:index], dealer=auction.dealer,
                         vulnerability=auction.vulnerability)
        prepared.append((
            prefix,
            replay_auction(profile, prefix, None),
            active_environment_for(profile, None, prefix),
            call,
        ))

    low, high = partner_hcp_bounds(trace, partner)
    if low > high:
        return ()
    if seed is None:
        seed = _process_seed(auction, actor_hand)
    constraints = {partner: partner_constraints(trace, partner)}
    sampled = sample_deals(
        auction.actor_to_call, actor_hand, public_constraints=constraints,
        sample_count=count, seed=seed, max_attempts=max_attempts,
        max_seconds=max_seconds)
    kept = []
    for deal in sampled.deals:
        hand = deal[partner]
        if extra_filter is not None and not extra_filter(hand):
            continue
        if all(any(candidate.call == call
                   for candidate in generate_candidates(
                       profile, prefix, hand, prepared_trace, prepared_env,
                       SeatMemory()))
               for prefix, prepared_trace, prepared_env, call in prepared):
            kept.append(deal)
    return tuple(kept)



__all__ = (
    'CueDecision',
    'cue_allowed_above',
    'cue_continuation',
    'cue_public_kr',
    'cue_three_way',
    'decide_from_hands',
    'extra_kr_threshold',
    'hand_would_bid_observed',
    'keycards_sufficient',
    'partner_hcp_bounds',
    'partner_promised_kr',
    'sample_process_hands',
    'signoff_override',
    'strength_is_unknown',
)
