"""Deterministic fallbacks for the Daqiush five-major inquiry."""

from __future__ import annotations

from dataclasses import dataclass

from .cards import Hand, normalize_suit_name
from .cue_slam_policy import sample_process_hands
from .call_space import contract_rank
from .hand_quality import (
    assess_quality, inquiry_stopper, minor_game_control_points,
    minor_slam_interest, shapely_control_points,
)


@dataclass(frozen=True)
class InquiryDecision:
    call: str | None
    source: str
    reason: str
    agreed_suit: str | None = None
    final: bool = False


def deterministic_after_singleton(
        opener: Hand, *, singleton_major: str) -> InquiryDecision:
    """Choose an exact no-DDS fallback after responder shows a singleton major."""
    reported = _major_code(singleton_major)
    other_major = 'S' if reported == 'H' else 'H'
    minor_lengths = {suit: opener.length(suit) for suit in 'CD'}

    if (_both_minor_special(opener, reported, minor_lengths)):
        return InquiryDecision(
            call='4' + reported,
            source='deterministic',
            reason='Both minors, sufficient controls, and no waste in the reported major',
            agreed_suit='D',
        )

    candidates: list[tuple[str, str | None, str]] = []
    long_minors = [suit for suit in 'CD' if minor_lengths[suit] >= 4]
    ambiguous_minors = len(long_minors) == 2
    if len(long_minors) == 1:
        minor = long_minors[0]
        candidates.append(('4' + minor, minor, 'Unique four-card-or-longer minor'))

    other_major_candidate = (opener.length(other_major) == 4
                             and all(length < 4 for length in minor_lengths.values()))
    if other_major_candidate:
        candidates.append(('4' + other_major, other_major,
                           'Unique possible four-three fit in the other major'))
    elif minor_lengths == {'C': 3, 'D': 3}:
        candidates.append(('4NT', None, 'Exact three-three minors'))

    has_stopper = inquiry_stopper(opener, reported)
    if (has_stopper and opener.length('C') >= 3
            and opener.length('D') >= 3):
        return InquiryDecision(
            call='3NT', source='deterministic',
            reason='Reported shortage is stopped; retain room for responder to show minors')
    if has_stopper and not candidates and not ambiguous_minors:
        return InquiryDecision(
            call='3NT', source='deterministic',
            reason='Reported singleton major is stopped and no suit route is eligible',
            final=True,
        )
    if not has_stopper and len(candidates) == 1:
        call, agreed_suit, reason = candidates[0]
        return InquiryDecision(call=call, source='deterministic', reason=reason,
                               agreed_suit=agreed_suit)

    reason = ('Both four-card minors require simulation' if ambiguous_minors
              else 'Notrump and a suit route overlap' if has_stopper and candidates
              else 'Structural routes do not identify one unique call')
    return InquiryDecision(call=None, source='inconclusive', reason=reason)


def _major_code(suit: str) -> str:
    normalized = normalize_suit_name(suit)
    if normalized not in ('hearts', 'spades'):
        raise ValueError('Singleton report must name a major')
    return normalized[0].upper()


def _both_minor_special(opener: Hand, reported: str,
                        minor_lengths: dict[str, int]) -> bool:
    if not all(length >= 4 for length in minor_lengths.values()):
        return False
    if minor_game_control_points(
            opener, 'D', partner_long_suits=('C',)) < 14.5:
        return False
    holding = opener.holding(reported)
    side_honors = {rank for rank in 'KQJ' if rank in holding}
    return not side_honors or (side_honors == {'K'} and 'A' in holding)


def _good_16_17_3c_family(hand: Hand) -> bool:
    if hand is None or hand.hcp not in (16, 17) or not assess_quality(hand)['good']:
        return False
    lengths = sorted(hand.length(s) for s in 'SHDC')
    max_major = max(hand.length(s) for s in 'HS')
    max_minor = max(hand.length(s) for s in 'CD')
    return ((max_major <= 3 and max_minor <= 4)
            or (lengths == [3, 3, 3, 4] and max_major == 4))


def deterministic_after_major(opener_major: str,
                              responder: Hand) -> InquiryDecision:
    """Responder's fallback after opener shows a five-card major."""
    major = _major_code(opener_major)
    family = _good_16_17_3c_family(responder)
    threshold = (4 if sorted(responder.length(s) for s in 'SHDC') == [3, 3, 3, 4]
                 else 3)
    # The new good 16-17 family counts any three-card fit and uses the
    # lowest other-major call to show it; without a fit it invites 6NT.
    if family:
        if responder.length(major) >= 3:
            call = '3S' if major == 'H' else '4H'
            return InquiryDecision(
                call=call, source='deterministic',
                reason='Good 16-17 with three-card support: lowest other-major fit show',
                agreed_suit=major)
        return InquiryDecision(
            call='4NT', source='deterministic',
            reason='Good 16-17 without three-card support: quantitative 4NT')
    if (responder.hcp >= 14 and responder.length(major) < 3
            and responder.length('C') == 5 and responder.length('D') == 4
            and (responder.length('H'), responder.length('S')) in ((2, 2), (3, 1), (1, 3))):
        return InquiryDecision(
            call='4C', source='deterministic',
            reason='Five clubs and four diamonds with slam interest and no major fit')
    support = responder.length(major) >= threshold
    singleton_shape = (responder.length(major) == 1
                       and sorted(responder.length(s) for s in 'CD') == [4, 5])
    if support:
        if minor_slam_interest(responder):
            call = '3S' if major == 'H' else '4H'
            return InquiryDecision(
                call=call, source='deterministic',
                reason='Three-card support with slam interest: lowest other-major strength show',
                agreed_suit=major)
        return InquiryDecision(
            call='4' + major, source='deterministic',
            reason='Three-card support without slam interest',
            agreed_suit=major, final=True)
    if singleton_shape:
        if minor_slam_interest(responder):
            five = 'C' if responder.length('C') == 5 else 'D'
            return InquiryDecision(
                call='4' + five, source='deterministic',
                reason='Singleton in opener major with slam interest: show the five-card minor')
        return InquiryDecision(
            call='3NT', source='deterministic',
            reason='Singleton in opener major without slam interest',
            final=True)
    return InquiryDecision(
        call='3NT', source='deterministic',
        reason='No major support and no five-four minor shape',
        final=True)


def deterministic_after_minor(opener: Hand,
                              shown_minor: str) -> InquiryDecision:
    """Opener's fallback after responder shows a five-four minor shape."""
    shown = _minor_code(shown_minor)
    other = 'D' if shown == 'C' else 'C'
    if shown == 'C':
        candidates = (('4D', 'D', 4 + opener.length('D')),
                      ('4H', 'C', 5 + opener.length('C')),
                      ('4S', 'C', 5 + opener.length('C')))
    else:
        candidates = (('4H', 'C', 4 + opener.length('C')),
                      ('4S', 'D', 5 + opener.length('D')))
    best_fit = max(fit for _, _, fit in candidates)
    tied = [item for item in candidates if item[2] == best_fit]
    if len(tied) > 1:
        scored = [(call, trump,
                   minor_game_control_points(opener, trump,
                                             partner_long_suits=(other,)))
                  for call, trump, _ in tied]
        best_control = max(score for _, _, score in scored)
        tied = [item for item in scored if item[2] == best_control]
    if len(tied) > 1:
        tied = sorted(tied, key=lambda item: contract_rank(item[0]))
    call, trump, _ = tied[0]
    return InquiryDecision(
        call=call, source='deterministic',
        reason='Longest known minor fit, then control points, then lowest call',
        agreed_suit=trump)


def deterministic_after_4om(opener: Hand, five: str,
                            other_major: str) -> InquiryDecision:
    """Opener's fallback after responder names a five-card minor."""
    five = _minor_code(five)
    other_major = _major_code(other_major)
    minor_fit = 5 + opener.length(five)
    major_fit = 4 + opener.length(other_major)
    if minor_fit > major_fit:
        return InquiryDecision(
            call='P', source='deterministic',
            reason='The known minor fit is the better five-level strain',
            agreed_suit=five, final=True)
    if major_fit > minor_fit:
        return InquiryDecision(
            call='5' + other_major, source='deterministic',
            reason='The known other-major fit is the better five-level strain',
            agreed_suit=other_major, final=True)
    minor_controls = shapely_control_points(opener, (five,))
    major_controls = shapely_control_points(opener, (other_major,))
    if minor_controls > major_controls:
        return InquiryDecision(
            call='P', source='deterministic',
            reason='Equal length; the minor has more controls',
            agreed_suit=five, final=True)
    if major_controls > minor_controls:
        return InquiryDecision(
            call='5' + other_major, source='deterministic',
            reason='Equal length; the other major has more controls',
            agreed_suit=other_major, final=True)
    return InquiryDecision(
        call=None, source='inconclusive',
        reason='Minor and other-major fits tie on length and controls')


def deterministic_after_4nt(responder: Hand, five: str) -> InquiryDecision:
    five = _minor_code(five)
    return InquiryDecision(
        call='5' + five, source='deterministic',
        reason='Without DDS the five-card minor is the safe five-level placement',
        agreed_suit=five, final=True)


def inquiry_decision_kind(profile_id: str, auction) -> str | None:
    if profile_id != 'daqiush_2over1':
        return None
    calls = tuple(auction.calls)
    if (len(calls) == 14 and calls[0] == '1N' and calls[2] == '3C'
            and calls[4] == '3D' and calls[6] == '3H'
            and calls[8] == '3S' and calls[10] in ('4C', '4D')
            and calls[12] == '4N' and calls[13] == 'P'):
        return 'responder_notrump_ladder_after_offer'
    if (len(calls) == 10 and calls[0] == '1N' and calls[2] == '3C'
            and calls[4] == '3D'
            and ((calls[6], calls[8]) in (('3H', '3S'), ('3S', '4H')))
            and calls[9] == 'P'):
        return 'responder_notrump_ladder'
    if (len(calls) == 12 and calls[0] == '1N' and calls[2] == '3C'
            and calls[4] == '3D' and calls[6] in ('3H', '3S')
            and calls[8] == '3N' and calls[10] == '4C'
            and calls[11] == 'P'):
        return 'opener_after_delayed_minor'
    if (len(calls) == 8 and calls[0] == '1N' and calls[2] == '3C'
            and calls[4] == '3D' and calls[6] in ('3H', '3S') and calls[7] == 'P'):
        return 'opener_after_singleton'
    if (len(calls) == 6 and calls[0] == '1N' and calls[2] == '3C'
            and calls[4] in ('3H', '3S') and calls[5] == 'P'):
        return 'responder_after_major'
    if (len(calls) == 8 and calls[0] == '1N' and calls[2] == '3C'
            and calls[4] in ('3H', '3S') and calls[6] in ('4C', '4D')
            and calls[7] == 'P'):
        return 'opener_after_minor'
    if (len(calls) == 10 and calls[0] == '1N' and calls[2] == '3C'
            and calls[4] == '3D' and calls[6] in ('3H', '3S')
            and calls[8] in ('4H', '4S') and calls[9] == 'P'):
        return 'responder_after_4om'
    if (len(calls) == 10 and calls[0] == '1N' and calls[2] == '3C'
            and calls[4] == '3D' and calls[6] in ('3H', '3S')
            and calls[8] == '4NT' and calls[9] == 'P'):
        return 'responder_after_4nt'
    if (len(calls) == 12 and calls[0] == '1N' and calls[2] == '3C'
            and calls[4] == '3D' and calls[6] in ('3H', '3S')
            and calls[8] in ('4H', '4S')
            and calls[10] in ('5C', '5D') and calls[11] == 'P'):
        return 'opener_after_5m'
    return None


def decide_five_major_inquiry(profile, auction, hand: Hand, *,
                              trace=None, solve_table=None) -> InquiryDecision:
    """Select the next call for a newly authored 1NT-3C continuation."""
    kind = inquiry_decision_kind(profile.id, auction)
    if kind is None:
        return InquiryDecision(None, 'inconclusive',
                               'Not a five-major inquiry decision point')
    actor = auction.actor_to_call
    partner = _partner(actor)
    if kind in ('responder_notrump_ladder', 'responder_notrump_ladder_after_offer'):
        return _decide_notrump_ladder(profile, auction, hand, trace, solve_table,
                                      after_offer=kind.endswith('after_offer'))
    partner_hcp_cap = None
    if kind == 'opener_after_delayed_minor':
        from .contract_evaluation import ContractTarget
        from .cue_slam_policy import partner_hcp_bounds

        low, _ = partner_hcp_bounds(trace, partner) if trace is not None else (14, 37)
        partner_hcp_cap = low + 2
        targets = [ContractTarget(level, suit, partner if suit == 'C' else actor)
                   for level in (5, 6) for suit in 'CD'
                   if hand.length(suit) >= (3 if suit == 'C' else 4)]
        fallback_suit = _preferred_minor(hand)
        fallback = InquiryDecision(
            '5' + fallback_suit, 'deterministic',
            'No compatible low-range DDS estimate; suggest the better supported minor',
            agreed_suit=fallback_suit)
        mapping = {}
    elif kind == 'opener_after_singleton':
        shortage = auction.calls[6][-1]
        other_major = 'S' if shortage == 'H' else 'H'
        fallback = deterministic_after_singleton(hand, singleton_major=shortage)
        if hand.length(other_major) >= 5:
            return InquiryDecision('4' + other_major, 'deterministic',
                                   'Five cards in the other major take priority',
                                   agreed_suit=other_major)
        if (hand.length(other_major) == 4
                and sorted(hand.length(suit) for suit in 'CD') == [2, 3]):
            from .contract_evaluation import ContractTarget
            targets = (ContractTarget(3, 'NT', actor),
                       ContractTarget(4, other_major, actor))
            mapping = {'3NT': '3NT',
                       '4' + other_major: '3S' if other_major == 'S' else '4H'}
            fallback = InquiryDecision(
                '3NT' if inquiry_stopper(hand, shortage)
                else mapping['4' + other_major],
                'deterministic', 'No DDS estimate for the other-major game')
        elif (inquiry_stopper(hand, shortage)
                and hand.length('C') >= 3 and hand.length('D') >= 3):
            from .contract_evaluation import ContractTarget
            minors = tuple(suit for suit in 'CD' if hand.length(suit) >= 4)
            if not minors:
                minors = ('C', 'D')
            targets = (ContractTarget(3, 'NT', actor), *(
                ContractTarget(5, suit, actor) for suit in minors))
            mapping = {'3NT': '3NT'}
            for suit in minors:
                mapping['5' + suit] = (
                    '4NT' if not any(hand.length(m) >= 4 for m in 'CD')
                    else '4C' if suit == 'C' else '4D')
            if ('D' in minors and _both_minor_special(
                    hand, shortage, {s: hand.length(s) for s in 'CD'})):
                mapping['5D'] = '4' + shortage
        else:
            targets, mapping = _singleton_targets(hand, actor, shortage)
    elif kind == 'responder_after_major':
        major = auction.calls[4][-1]
        fallback = deterministic_after_major(major, hand)
        if _good_16_17_3c_family(hand):
            return fallback
        targets, mapping = _major_targets(hand, actor, partner, major)
    elif kind == 'opener_after_minor':
        shown = auction.calls[6][-1]
        fallback = deterministic_after_minor(hand, shown)
        targets, mapping = _minor_targets(hand, actor, shown)
    elif kind == 'responder_after_4om':
        other_major = auction.calls[8][-1]
        five = _five_minor(hand)
        if minor_slam_interest(hand):
            fallback = InquiryDecision(
                call='5' + five, source='deterministic',
                reason='Slam interest: name the five-card minor',
                agreed_suit=five)
        else:
            fallback = InquiryDecision(
                call='P', source='deterministic',
                reason='No slam interest: pass the other-major game',
                final=True)
        targets, mapping = _four_om_targets(hand, actor, partner, five,
                                            other_major, responder=True)
    elif kind == 'responder_after_4nt':
        five = _five_minor(hand)
        fallback = deterministic_after_4nt(hand, five)
        targets, mapping = _four_nt_targets(hand, actor, five, responder=True)
    else:  # opener_after_5m
        five = auction.calls[10][-1]
        previous = auction.calls[8]
        if previous in ('4H', '4S'):
            fallback = deterministic_after_4om(hand, five, previous[-1])
            targets, mapping = _four_om_targets(
                hand, actor, partner, five, previous[-1], responder=False)
        else:
            fallback = InquiryDecision(
                None, 'inconclusive',
                'The three-three-minor route is decided by responder')
            targets, mapping = (), {}
    if trace is None:
        from .replay import replay_auction
        trace = replay_auction(profile, auction)
    estimates = _sampled_best(profile, auction, hand, trace, partner,
                              targets, solve_table,
                              partner_max_hcp=partner_hcp_cap)
    if estimates:
        if kind == 'opener_after_delayed_minor':
            return _delayed_minor_decision(hand, estimates, _vulnerable(auction))
        if (kind == 'opener_after_singleton' and hand.length(other_major) == 4
                and sorted(hand.length(suit) for suit in 'CD') == [2, 3]):
            best = max(estimates, key=lambda estimate: _game_expected_score(
                estimate, _vulnerable(auction)))
            selected = mapping.get(best.contract)
            if selected is not None:
                return InquiryDecision(
                    selected, 'dds',
                    'Compared three notrump with four of the other major',
                    agreed_suit=other_major if selected != '3NT' else None)
        if (kind == 'opener_after_singleton'
                and targets and targets[0].contract == '3NT'
                and all(target.contract in ('3NT', '5C', '5D')
                        for target in targets)):
            best = max(estimates, key=lambda estimate: _game_expected_score(
                estimate, _vulnerable(auction)))
            selected = mapping.get(best.contract)
            if selected is not None:
                return InquiryDecision(
                    selected, 'dds',
                    'Compared three notrump with the supported minor games',
                    agreed_suit=(mapping[best.contract][1]
                                 if selected in ('4C', '4D') else
                                 'D' if selected == '4' + shortage else None))
        best = _best_estimate(estimates, _vulnerable(auction))
        selected = mapping.get(best.contract)
        if selected is not None:
            return InquiryDecision(
                call=selected, source='dds',
                reason='Sampled final-contract comparison selected ' + best.contract,
                final=selected in ('3NT', '4H', '4S', '5C', '5D', '6C', '6D'))
    return fallback



@dataclass(frozen=True)
class QuantitativeAceDecision:
    branch: str
    reason: str


def quantitative_ace_decision(profile, auction, hand: Hand, *, trace=None):
    """Resolve an ambiguous 1/4 or 0/3 ace answer by sampling."""
    nonpass = tuple(call for call in auction.calls if call != 'P')
    if len(nonpass) < 6 or nonpass[-2] != '5C':
        return None
    if nonpass[-1] not in ('5D', '5H'):
        return None
    prefix = nonpass[:-2]
    if prefix not in (('1N', '2C', '2D', '4N'),
                      ('1N', '2C', '2H', '4N'),
                      ('1N', '3C', '3D', '4N')):
        return None
    answer = nonpass[-1]
    category = (1, 4) if answer == '5D' else (0, 3)
    own = hand.ace_count()
    possible = []
    for partner_aces in category:
        total = own + partner_aces
        if total <= 4:
            possible.append(4 - total < 2)
    if not possible:
        return QuantitativeAceDecision(
            'stop', 'No legal ace total is compatible with this answer')
    if all(possible):
        return QuantitativeAceDecision('slam', 'Every interpretation keeps at most one ace missing')
    if not any(possible):
        return QuantitativeAceDecision('stop', 'Every interpretation is missing at least two aces')
    if trace is None:
        from .replay import replay_auction
        trace = replay_auction(profile, auction)
    partner = _partner(auction.actor_to_call)
    try:
        deals = sample_process_hands(
            profile, auction, trace, hand, partner,
            extra_filter=lambda sampled: sampled.ace_count() in category)
    except (RuntimeError, ValueError):
        return QuantitativeAceDecision(
            'stop', 'Ace-count sampling unavailable; conservative stop')
    if not deals:
        return QuantitativeAceDecision(
            'stop', 'No compatible sampled responder hand; conservative stop')
    compatible = [deal[partner].ace_count() for deal in deals
                  if deal[partner].ace_count() in category]
    if not compatible:
        return QuantitativeAceDecision(
            'stop', 'No compatible sampled ace answer; conservative stop')
    share = sum(4 - (own + aces) < 2 for aces in compatible) / len(compatible)
    return QuantitativeAceDecision(
        'slam' if share > 0.5 else 'stop',
        f'{share:.1%} of compatible samples are missing fewer than two aces')

def _partner(seat: str) -> str:
    return {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[seat]


def _minor_code(suit: str) -> str:
    normalized = normalize_suit_name(suit)
    if normalized not in ('clubs', 'diamonds'):
        raise ValueError('Minor route must name a minor')
    return normalized[0].upper()


def _five_minor(hand: Hand) -> str:
    if hand is None or sorted(hand.length(s) for s in 'CD') != [4, 5]:
        raise ValueError('Responder does not hold a five-four minor shape')
    return 'C' if hand.length('C') == 5 else 'D'


def _vulnerable(auction) -> bool:
    side = 'ns' if auction.actor_to_call in 'ns' else 'ew'
    return auction.vulnerability in ('both', side)


def _decide_notrump_ladder(profile, auction, hand, trace, solve_table, *, after_offer):
    """Use the opener's public minimum and maximum, never the actual hand."""
    from .contract_evaluation import ContractTarget
    from .cue_slam_policy import SLAM_QUALIFY_RATE, partner_hcp_bounds
    from .grand_slam_policy import GRAND_QUALIFY_RATE
    from .replay import replay_auction

    if not after_offer and auction.calls[8] == '3S' and minor_slam_interest(hand):
        if sorted((hand.length('C'), hand.length('D'))) == [4, 5] and hand.hcp >= 14:
            minor = _five_minor(hand)
            return InquiryDecision('4' + minor, 'deterministic',
                                   'Describe the longer minor with slam interest')
    fallback = 'P' if after_offer or auction.calls[8] == '4H' else '3NT'
    if trace is None:
        trace = replay_auction(profile, auction)
    actor = auction.actor_to_call
    partner = _partner(actor)
    low, high = partner_hcp_bounds(trace, partner)
    targets = (ContractTarget(6, 'NT', actor), ContractTarget(7, 'NT', actor))
    bands = []
    for hcp in (low, high):
        estimates = _sampled_best(
            profile, auction, hand, trace, partner, targets, solve_table,
            partner_min_hcp=hcp, partner_max_hcp=hcp)
        if not estimates:
            return InquiryDecision(fallback, 'deterministic',
                                   'Notrump ladder simulation unavailable')
        bands.append({item.contract: item.completion_rate for item in estimates})
    low_rates, high_rates = bands
    small_low = low_rates.get('6NT', 0.0) >= SLAM_QUALIFY_RATE
    small_high = high_rates.get('6NT', 0.0) >= SLAM_QUALIFY_RATE
    grand_low = low_rates.get('7NT', 0.0) >= GRAND_QUALIFY_RATE
    grand_high = high_rates.get('7NT', 0.0) >= GRAND_QUALIFY_RATE
    if grand_low:
        call = '7NT'
    elif small_low and grand_high:
        call = '5NT'  # Invites seven, never six.
    elif small_low:
        call = '6NT'
    elif small_high and not after_offer:
        call = '4NT'  # Invites the small slam.
    else:
        call = fallback
    return InquiryDecision(call, 'dds',
                           'Compared six and seven notrump at the opener range endpoints',
                           final=call in ('3NT', '6NT', '7NT', 'P'))


def _sampled_best(profile, auction, hand, trace, partner, targets,
                  solve_table, *, partner_max_hcp=None, partner_min_hcp=None):
    if not targets:
        return None
    from .cue_slam_policy import sample_process_hands
    from .contract_evaluation import compare_contract_targets
    from .dds_adapter import DDSUnavailableError, calculate_available_table
    from .deal_sampler import SamplingExhausted
    try:
        if partner_max_hcp is None and partner_min_hcp is None:
            deals = sample_process_hands(profile, auction, trace, hand, partner)
        else:
            deals = sample_process_hands(
                profile, auction, trace, hand, partner,
                partner_count=10, partner_max_hcp=partner_max_hcp,
                partner_min_hcp=partner_min_hcp)
    except (SamplingExhausted, RuntimeError, ValueError):
        return None
    if not deals:
        return None
    table = solve_table or calculate_available_table
    try:
        return compare_contract_targets(deals, targets, solve_table=table)
    except (DDSUnavailableError, RuntimeError, ValueError):
        return None


def _best_estimate(estimates, vulnerable):
    from .simulation_decision import _binary_contract_score
    best = None
    best_score = None
    for estimate in estimates:
        score = (estimate.completion_rate
                 * _binary_contract_score(estimate.contract, True, vulnerable)
                 + (1 - estimate.completion_rate)
                 * _binary_contract_score(estimate.contract, False, vulnerable))
        if best_score is None or score > best_score:
            best, best_score = estimate, score
    return best


def _game_expected_score(estimate, vulnerable: bool) -> float:
    """Score only making the target or going one down, without overtricks."""
    contract = estimate.contract
    level = int(contract[0])
    suit = contract[1:]
    if suit == 'NT':
        tricks = 40 + (level - 1) * 30
    elif suit in 'HS':
        tricks = level * 30
    else:
        tricks = level * 20
    game = 500 if vulnerable else 300
    slam = ((1500 if vulnerable else 1000) if level == 7 else
            (750 if vulnerable else 500) if level == 6 else 0)
    made = tricks + game + slam
    set_one = -100 if vulnerable else -50
    return (estimate.completion_rate * made
            + (1 - estimate.completion_rate) * set_one)


def _preferred_minor(hand: Hand) -> str:
    candidates = [suit for suit in 'CD'
                  if hand.length(suit) >= (3 if suit == 'C' else 4)]
    return max(candidates, key=lambda suit: (
        (5 if suit == 'C' else 4) + hand.length(suit),
        minor_game_control_points(
            hand, suit, partner_long_suits=('D' if suit == 'C' else 'C',)),
        suit == 'D'))


def _delayed_minor_decision(hand: Hand, estimates, vulnerable: bool) -> InquiryDecision:
    available = {item.contract: item for item in estimates}
    games = [available['5' + suit] for suit in 'CD'
             if '5' + suit in available]
    if not games:
        suit = _preferred_minor(hand)
        return InquiryDecision('5' + suit, 'deterministic',
                               'No sampled minor game result; suggest five of the supported minor',
                               agreed_suit=suit)
    best_game = max(games, key=lambda item: _game_expected_score(item, vulnerable))
    slams = [available['6' + suit] for suit in 'CD'
             if '6' + suit in available]
    best_slam = (max(slams, key=lambda item: _game_expected_score(item, vulnerable))
                 if slams else None)
    if (best_slam is not None and
            _game_expected_score(best_slam, vulnerable)
            > _game_expected_score(best_game, vulnerable)):
        suit = best_slam.contract[1]
        if suit == 'D':
            call = '4D'
        else:
            spade_control = (hand.contains_rank('S', 'A')
                             or hand.contains_rank('S', 'K')
                             or hand.length('S') <= 1)
            call = '4S' if spade_control else '4H'
        return InquiryDecision(call, 'dds',
                               'Low-range samples favor investigating ' + best_slam.contract,
                               agreed_suit=suit)
    suit = best_game.contract[1]
    return InquiryDecision('5' + suit, 'dds',
                           'Low-range samples favor suggesting ' + best_game.contract,
                           agreed_suit=suit)


def _singleton_targets(hand: Hand, actor: str, shortage: str):
    from .contract_evaluation import ContractTarget
    other = 'S' if shortage == 'H' else 'H'
    targets = [ContractTarget(3, 'NT', actor),
               ContractTarget(5, 'C', actor),
               ContractTarget(5, 'D', actor),
               ContractTarget(4, other, actor)]
    mapping = {'3NT': '3NT', '5C': '4C', '5D': '4D', '4' + other: '4' + other}
    if _both_minor_special(hand, shortage, {s: hand.length(s) for s in 'CD'}):
        mapping['5D'] = '4' + shortage
    if hand.length('C') == 3 and hand.length('D') == 3:
        mapping['5C'] = '4NT'
        mapping['5D'] = '4NT'
    return targets, mapping


def _major_targets(hand: Hand, actor: str, partner: str, major: str):
    from .contract_evaluation import ContractTarget
    threshold = (4 if sorted(hand.length(s) for s in 'SHDC') == [3, 3, 3, 4]
                 else 3)
    support = hand.length(major) >= threshold
    singleton_shape = (hand.length(major) == 1
                       and sorted(hand.length(s) for s in 'CD') == [4, 5])
    if support:
        targets = [ContractTarget(4, major, partner),
                   ContractTarget(6, major, partner)]
        strength = '3S' if major == 'H' else '4H'
        return targets, {'4' + major: '4' + major, '6' + major: strength}
    if singleton_shape:
        five = 'C' if hand.length('C') == 5 else 'D'
        targets = [ContractTarget(3, 'NT', partner),
                   ContractTarget(5, five, actor),
                   ContractTarget(6, five, actor)]
        mapping = {'3NT': '3NT', '5' + five: '4' + five,
                   '6' + five: '4' + five}
        return targets, mapping
    return [ContractTarget(3, 'NT', partner)], {'3NT': '3NT'}


def _minor_targets(hand: Hand, actor: str, shown: str):
    from .contract_evaluation import ContractTarget
    shown = _minor_code(shown)
    other = 'D' if shown == 'C' else 'C'
    if shown == 'C':
        calls = (('4D', 'D'), ('4H', 'C'), ('4S', 'C'))
    else:
        calls = (('4H', 'C'), ('4S', 'D'))
    targets = []
    mapping = {}
    for call, trump in calls:
        targets.append(ContractTarget(5, trump, actor))
        targets.append(ContractTarget(6, trump, actor))
        mapping['5' + trump] = call
        mapping['6' + trump] = call
    return targets, mapping


def _four_om_targets(hand: Hand, actor: str, partner: str, five: str,
                     other_major: str, *, responder: bool):
    from .contract_evaluation import ContractTarget
    five = _minor_code(five)
    other_major = _major_code(other_major)
    if responder:
        targets = [ContractTarget(4, other_major, partner),
                   ContractTarget(5, five, actor),
                   ContractTarget(6, five, actor)]
        return targets, {'4' + other_major: 'P', '5' + five: '5' + five,
                         '6' + five: '5' + five}
    targets = [ContractTarget(5, five, partner),
               ContractTarget(5, other_major, actor),
               ContractTarget(6, five, partner),
               ContractTarget(6, other_major, actor)]
    return targets, {'5' + five: 'P', '5' + other_major: '5' + other_major,
                     '6' + five: '6' + five,
                     '6' + other_major: '6' + other_major}


def _four_nt_targets(hand: Hand, actor: str, five: str, *, responder: bool):
    from .contract_evaluation import ContractTarget
    five = _minor_code(five)
    return ([ContractTarget(5, five, actor), ContractTarget(6, five, actor)],
            {'5' + five: '5' + five, '6' + five: '6' + five})

