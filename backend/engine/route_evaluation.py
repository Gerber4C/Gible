"""Information-safe, analysis-only comparison of authored bidding routes.

The caller fixes one candidate first call. Every later partnership decision uses
that seat's sampled hand and the public auction, never the full deal. Opponents
Pass in this first uncontested experiment. A missing continuation is coverage
failure, not a made or defeated contract.
"""

from __future__ import annotations

from collections import Counter
from math import sqrt

from .auction import Auction
from .legality import SIDE_BY_SEAT, auction_is_complete, last_contract_state
from .memory import SeatMemory
from .matcher import matches_context
from .purpose_axiom import remember_selected_purpose
from .replay import replay_auction
from .selector import choose_bid


MAX_ROLLOUT_CALLS = 28


def compare_authored_routes(profile, auction, acting_hand, samples, first_calls, *, solve_table):
    """Return route coverage and contract success on the *same* sampled deals."""
    decision = choose_bid(profile, auction, acting_hand)
    eligible = {candidate.call: candidate for candidate in decision.candidate_pool.candidates}
    partnership = SIDE_BY_SEAT[auction.actor_to_call]
    opening_meanings = replay_auction(profile, auction).applied_meanings
    summaries = []
    for first_call in first_calls:
        candidate = eligible.get(first_call)
        reason = None if candidate is not None else _unavailable_reason(profile, auction, first_call)
        summaries.append({
            'first_call': first_call,
            'status': 'evaluated' if candidate is not None else 'unavailable',
            'reason': reason,
            'completed': 0, 'blocked': 0, 'made': 0, 'failed': 0,
            'contracts': {}, 'block_reasons': Counter(),
            'example_auction': None,
        })
    for deal in samples:
        table = None
        for summary in summaries:
            candidate = eligible.get(summary['first_call'])
            if candidate is None:
                summary['blocked'] += 1
                summary['block_reasons'][summary['reason']] += 1
                continue
            result = _rollout(profile, auction, deal, candidate,
                              partnership, opening_meanings)
            if summary['example_auction'] is None:
                summary['example_auction'] = ''.join(result['calls'])
            if result['status'] != 'complete':
                summary['blocked'] += 1
                summary['block_reasons'][result['reason']] += 1
                continue
            if table is None:
                table = solve_table(deal)
            strain, declarer, level = result['strain'], result['declarer'], result['level']
            tricks = table.get(strain, {}).get(declarer)
            if isinstance(tricks, bool) or not isinstance(tricks, int) or not 0 <= tricks <= 13:
                raise ValueError(f'Solver table lacks valid {strain}/{declarer} tricks')
            made = tricks >= level + 6
            summary['completed'] += 1
            summary['made' if made else 'failed'] += 1
            key = (f'{level}{strain}', declarer)
            count, successes = summary['contracts'].get(key, (0, 0))
            summary['contracts'][key] = (count + 1, successes + int(made))
    count = len(samples)
    return tuple(_report(summary, count) for summary in summaries)


def _unavailable_reason(profile, auction, call):
    specs = [spec for spec in profile.call_specifications
             if spec.call == call and matches_context(spec.context, auction)]
    if any(spec.meaning.to_dict().get('historical_only') for spec in specs):
        return 'Meaning is recorded, but this route has no automatic selection rule yet'
    return 'No Axiom-compliant authored call matches this hand and auction'


def _rollout(profile, prefix, deal, first, partnership, opening_meanings):
    calls = list(prefix.calls)
    natural = [(entry['seat'], entry['call'], entry['public_meaning'])
               for entry in opening_meanings]
    memories = {seat: SeatMemory() for seat in 'nesw' if SIDE_BY_SEAT[seat] == partnership}
    actor = prefix.actor_to_call
    memories[actor] = memories[actor].remember_candidate(first)
    memories[actor] = remember_selected_purpose(memories[actor], prefix, deal[actor], first)
    natural.append((actor, first.call, first.public_meaning))
    calls.append(first.call)
    for _ in range(MAX_ROLLOUT_CALLS):
        auction = Auction(tuple(calls), prefix.dealer, prefix.vulnerability)
        if auction_is_complete(auction):
            return _final_contract(auction, natural, partnership)
        seat = auction.actor_to_call
        if SIDE_BY_SEAT[seat] != partnership:
            calls.append('P')
            continue
        choice = choose_bid(profile, auction, deal[seat],
                            {'seat': seat, 'dealer': prefix.dealer,
                             'vulnerability': prefix.vulnerability, 'scoring': 'IMP'},
                            memories[seat])
        memories[seat] = choice.private_memory
        if choice.call is None:
            return {'status': 'blocked', 'reason':
                    choice.trace.diagnostics[-1] if choice.trace.diagnostics else
                    'No authored continuation', 'calls': tuple(calls)}
        natural.append((seat, choice.call, choice.selected_candidate.public_meaning))
        calls.append(choice.call)
    return {'status': 'blocked', 'reason': 'Rollout call limit reached', 'calls': tuple(calls)}


def _final_contract(auction, meanings, partnership):
    state = last_contract_state(auction)
    if state is None or state.side != partnership:
        return {'status': 'blocked', 'reason': 'No partnership contract reached',
                'calls': auction.calls}
    strain = 'NT' if state.call[1] == 'N' else state.call[1]
    declarer = next((seat for seat, call, meaning in meanings
                     if SIDE_BY_SEAT[seat] == partnership and call[0] in '1234567'
                     and call[1] == state.call[1]
                     and 'natural' in meaning.get('nature_labels', ())), None)
    if declarer is None:
        return {'status': 'blocked', 'reason': 'Final declarer is not established by a natural call',
                'calls': auction.calls}
    return {'status': 'complete', 'calls': auction.calls,
            'level': int(state.call[0]), 'strain': strain, 'declarer': declarer}


def _report(summary, sample_count):
    completed = summary['completed']
    return {
        'first_call': summary['first_call'], 'status': summary['status'],
        'reason': summary['reason'], 'completed': completed,
        'blocked': summary['blocked'], 'made': summary['made'],
        'failed': summary['failed'],
        'coverage_rate': completed / sample_count,
        'completion_rate': summary['made'] / completed if completed else None,
        'completion_interval_95': _wilson(summary['made'], completed) if completed else None,
        'contracts': [
            {'contract': contract, 'declarer': declarer, 'count': count, 'made': made}
            for (contract, declarer), (count, made) in sorted(summary['contracts'].items())
        ],
        'block_reasons': [
            {'reason': reason, 'count': count}
            for reason, count in sorted(summary['block_reasons'].items())
        ],
        'example_auction': summary['example_auction'],
    }


def _wilson(made, total):
    p = made / total
    z = 1.959963984540054
    denominator = 1 + z * z / total
    center = (p + z * z / (2 * total)) / denominator
    width = z * sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    return [max(0.0, center - width), min(1.0, center + width)]
