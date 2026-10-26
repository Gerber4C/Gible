"""Private, committed bidding purposes. Public replies are read from replay."""
from __future__ import annotations

from dataclasses import dataclass, replace

from .calls import normalize_call
from .context import CallCandidate
from .legality import SIDE_BY_SEAT, is_call_legal, last_contract_state
from .memory import Purpose, SeatMemory


@dataclass(frozen=True)
class PurposeResolution:
    memory: SeatMemory
    candidate: CallCandidate | None = None
    purpose: Purpose | None = None
    error: str | None = None


def terminal_pass_candidate(auction, trace) -> CallCandidate | None:
    """Honor an explicitly completed public purpose after partner places it."""
    if len(auction.calls) < 2 or auction.calls[-1] != 'P':
        return None
    index = len(auction.calls) - 2
    actor = auction.actor_to_call
    if auction.actor_at(index) != {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[actor]:
        return None
    contract = last_contract_state(auction)
    if contract is None or contract.index != index or contract.side != SIDE_BY_SEAT[actor]:
        return None
    entry = next((item for item in trace.applied_meanings if item.get('index') == index), None)
    meaning = entry['public_meaning'] if entry else {}
    if meaning.get('purpose_completed') is not True or 'final_placement' not in meaning.get('call_act_types', ()):
        return None
    origin = {'namespace': 'axiom', 'object_type': 'purpose',
              'object_id': 'terminal_pass', 'qualified_id': 'axiom/purpose:terminal_pass'}
    return CallCandidate(
        call='P', origin=origin,
        public_meaning={'nature_labels': ['natural'], 'call_act_types': ['signoff'],
                        'action_type': 'purpose_complete_pass', 'target_suit': contract.call[1]},
        source_kind='purpose_axiom', source_id='terminal_pass',
        implementation_origin=origin, score=1000,
        criterion_results=(), capabilities=('place_contract',),
        metadata={'source_index': index, 'purpose_kind': 'terminal_pass'})


def resolve_purpose(auction, trace, memory: SeatMemory) -> PurposeResolution:
    for purpose in reversed(memory.purposes):
        if purpose.status != 'active' or purpose.owner != auction.actor_to_call:
            continue
        if not _valid_source(auction, purpose):
            return PurposeResolution(memory, error='Saved purpose does not match this auction')
        if _opponent_interfered(auction, purpose):
            return PurposeResolution(memory.replace_purpose(purpose, replace(purpose, status='disrupted')))
        if len(auction.calls) < purpose.source_index + 4:
            return PurposeResolution(memory)
        if len(auction.calls) != purpose.source_index + 4:
            return PurposeResolution(memory.replace_purpose(purpose, replace(purpose, status='disrupted')))
        if purpose.kind == 'response_plan':
            call, error = _response_plan(auction, purpose)
        elif purpose.kind == 'keycard_slam':
            call, error = _keycard_slam(auction, trace, purpose)
        else:
            call, error = None, f'Unknown saved purpose: {purpose.kind}'
        if error:
            return PurposeResolution(memory, purpose=purpose, error=error)
        if not is_call_legal(auction, call):
            return PurposeResolution(memory, purpose=purpose,
                                     error=f'Planned call {call} is illegal in this auction')
        return PurposeResolution(memory, _candidate(call, purpose), purpose)
    return PurposeResolution(memory)


def remember_selected_purpose(memory: SeatMemory, auction, hand, candidate) -> SeatMemory:
    meaning = candidate.public_meaning
    private = candidate.private_purpose
    if private is not None:
        if not isinstance(private, dict):
            raise ValueError('Selected private purpose must be a mapping')
        kind = private.get('kind')
        trump = private.get('trump')
        if kind != 'response_plan' or trump not in ('C', 'D', 'H', 'S', 'N'):
            raise ValueError('Unsupported private purpose on selected call')
        skip_if = private.get('skip_if')
        if skip_if is not None:
            if not isinstance(skip_if, dict) or set(skip_if) != {'min_hcp', 'side_lengths'}:
                raise ValueError('Invalid private purpose skip condition')
            side_lengths = sorted(hand.length(suit) for suit in 'SHDC' if suit != trump)
            if hand.hcp >= skip_if['min_hcp'] and side_lengths == list(skip_if['side_lengths']):
                return memory
        responses = private.get('responses', {})
        if not isinstance(responses, dict) or not responses:
            raise ValueError('Response plan requires partner replies and planned calls')
        return memory.with_purpose(Purpose(
            kind=kind, owner=auction.actor_to_call, source_index=len(auction.calls),
            source_call=candidate.call, trump=trump,
            responses={normalize_call(reply): normalize_call(next_call)
                       for reply, next_call in responses.items()}))
    if candidate.call != '4N' or 'keycard_asking' not in meaning.get('call_act_types', ()):
        return memory
    trump = meaning.get('agreed_suit') or meaning.get('target_suit')
    if not isinstance(trump, str) or trump not in 'CDHS':
        return memory
    return memory.with_purpose(Purpose(
        kind='keycard_slam', owner=auction.actor_to_call,
        source_index=len(auction.calls), source_call=candidate.call, trump=trump,
        own_keycards=hand.keycard_count(trump),
        owns_trump_queen=hand.contains_rank(trump, 'Q')))


def complete_purpose(memory: SeatMemory, purpose: Purpose | None) -> SeatMemory:
    if purpose is None:
        return memory
    return memory.replace_purpose(purpose, replace(purpose, status='completed'))


def _valid_source(auction, purpose):
    i = purpose.source_index
    return (isinstance(i, int) and 0 <= i < len(auction.calls)
            and auction.actor_at(i) == purpose.owner
            and auction.calls[i] == normalize_call(purpose.source_call)
            and isinstance(purpose.trump, str) and purpose.trump in 'CDHSN')


def _opponent_interfered(auction, purpose):
    side = SIDE_BY_SEAT[purpose.owner]
    return any(call != 'P' and SIDE_BY_SEAT[auction.actor_at(i)] != side
               for i, call in enumerate(auction.calls[purpose.source_index + 1:],
                                        start=purpose.source_index + 1))


def _response_plan(auction, purpose):
    response = auction.calls[purpose.source_index + 2]
    if response not in purpose.responses:
        return None, f'Unexpected partner reply {response} to saved purpose'
    return normalize_call(purpose.responses[response]), None


def _keycard_slam(auction, trace, purpose):
    if purpose.own_keycards is None or purpose.owns_trump_queen is None:
        return None, 'Keycard purpose lacks the asker\'s saved private count'
    answer_index = purpose.source_index + 2
    meaning = next((entry['public_meaning'] for entry in trace.applied_meanings
                    if entry['index'] == answer_index and entry['seat'] != purpose.owner), None)
    if not meaning or 'keycard_counts' not in meaning:
        return None, 'Partner keycard answer has no unambiguous public meaning'
    possible_counts = [count for count in meaning['keycard_counts']
                       if 0 <= 5 - purpose.own_keycards - count <= 5]
    # The partnership may state a preferred interpretation of an ambiguous
    # answer. Apply it only when that count is still possible from the asker's
    # own cards; otherwise keep the mathematically possible interpretation.
    preferred = meaning.get('preferred_keycard_count')
    if preferred in possible_counts:
        possible_counts = [preferred]
    missing = {5 - purpose.own_keycards - count for count in possible_counts
               if 0 <= 5 - purpose.own_keycards - count <= 5}
    if len(missing) != 1:
        return None, 'Partner keycard answer leaves the number of missing keycards ambiguous'
    missing_count = missing.pop()
    game, slam = f'5{purpose.trump}', f'6{purpose.trump}'
    if missing_count >= 2:
        return game, None
    if missing_count == 0 or purpose.owns_trump_queen or meaning.get('trump_queen') is True:
        return slam, None
    if meaning.get('trump_queen') is False:
        return game, None
    # An unknown queen must be asked when a legal non-trump step remains below
    # the five-level trump signoff. Its exact call/answers belong to the profile.
    if _queen_ask_space(auction, game):
        return None, 'Trump queen ask has space but no authored continuation'
    return slam, None


def _queen_ask_space(auction, game):
    from .legality import legal_calls
    return any(call != game and call[0] == '5' and call[1] != game[1]
               and _bid_rank(call) < _bid_rank(game) for call in legal_calls(auction))


def _bid_rank(call):
    return int(call[0]) * 5 + 'CDHSN'.index(call[1])


def _candidate(call: str, purpose: Purpose) -> CallCandidate:
    origin = {'namespace': 'axiom', 'object_type': 'purpose',
              'object_id': purpose.kind, 'qualified_id': f'axiom/purpose:{purpose.kind}'}
    final = call == 'P' or call[0] in '56'
    return CallCandidate(
        call=call, origin=origin,
        public_meaning={'nature_labels': ['natural'],
                        'call_act_types': ['final_placement' if final else 'signoff'],
                        'action_type': 'planned_purpose_continuation',
                        'target_suit': purpose.trump},
        source_kind='purpose_axiom', source_id=purpose.kind,
        implementation_origin=origin, score=1000,
        criterion_results=(), capabilities=('place_contract',),
        metadata={'source_index': purpose.source_index, 'purpose_kind': purpose.kind})
