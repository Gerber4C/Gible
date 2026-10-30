"""Private, committed bidding purposes. Public replies are read from replay."""
from __future__ import annotations

from dataclasses import dataclass, replace

from .calls import normalize_call
from .context import CallCandidate
from .legality import SIDE_BY_SEAT, is_call_legal, last_contract_state
from .memory import Purpose, SeatMemory
from .rkcb_continuation import (
    bid_rank, five_spade_role, five_trump_available, high_answer_invitations,
    is_high_answer, lowest_showable_side_king, ordinary_rkcb_frame,
    partner_of_last_bidder, possible_partner_counts, queen_ask_call,
    relay_terminal_call,
)
from .rkcb_simulation import (
    compare_ambiguous_continuations, compare_grand_routes,
    compare_rescue_routes,
)
from .slam_intent import (
    PARTNER_1NT_MIN, PARTNER_DEFAULT_MIN, detect_slam_intent,
)


@dataclass(frozen=True)
class PurposeResolution:
    memory: SeatMemory
    candidate: CallCandidate | None = None
    purpose: Purpose | None = None
    error: str | None = None
    filtered_candidates: tuple[CallCandidate, ...] | None = None
    completes: bool = True


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


def resolve_purpose(auction, trace, memory: SeatMemory, hand=None,
                    candidates=(), profile=None) -> PurposeResolution:
    for purpose in reversed(memory.purposes):
        if purpose.status != 'active' or purpose.owner != auction.actor_to_call:
            continue
        if not _valid_source(auction, purpose):
            return PurposeResolution(memory, error='Saved purpose does not match this auction')
        if _opponent_interfered(auction, purpose):
            return PurposeResolution(memory.replace_purpose(
                purpose, replace(purpose, status='disrupted')))
        if purpose.kind == 'response_plan':
            if len(auction.calls) < purpose.source_index + 4:
                return PurposeResolution(memory)
            if len(auction.calls) != purpose.source_index + 4:
                return PurposeResolution(memory.replace_purpose(
                    purpose, replace(purpose, status='disrupted')))
            call, error = _response_plan(auction, purpose)
            if error:
                return PurposeResolution(memory, purpose=purpose, error=error)
            if not is_call_legal(auction, call):
                return PurposeResolution(memory, purpose=purpose,
                                         error=f'Planned call {call} is illegal in this auction')
            authored = _authored_candidates(candidates, call)
            if authored:
                return PurposeResolution(
                    memory, authored[0], purpose,
                    filtered_candidates=authored)
            return PurposeResolution(memory, _candidate(call, purpose), purpose)
        if purpose.kind != 'keycard_slam':
            return PurposeResolution(memory, purpose=purpose,
                                     error=f'Unknown saved purpose: {purpose.kind}')
        if len(auction.calls) < purpose.source_index + 4:
            return PurposeResolution(memory)
        result = _keycard_slam(auction, trace, purpose, hand, profile,
                               candidates)
        if result.purpose is not None and result.purpose != purpose:
            memory = memory.replace_purpose(purpose, result.purpose)
        resolved = result.purpose or purpose
        if result.error:
            return PurposeResolution(memory, purpose=resolved,
                                     error=result.error)
        if result.call is None:
            return PurposeResolution(memory, purpose=resolved,
                                     completes=False)
        if not is_call_legal(auction, result.call):
            return PurposeResolution(memory, purpose=resolved,
                                     error=f'Planned call {result.call} is illegal in this auction')
        authored = _authored_candidates(candidates, result.call)
        if authored:
            return PurposeResolution(
                memory, authored[0], resolved,
                filtered_candidates=authored, completes=result.completes)
        if result.authored_only:
            return PurposeResolution(
                memory, purpose=resolved,
                error=f'Planned keycard call {result.call} has no authored candidate')
        # Legacy compatibility for already-saved terminal placements.
        return PurposeResolution(memory, _candidate(result.call, resolved),
                                 resolved, completes=result.completes)
    return PurposeResolution(memory)


def _authored_candidates(candidates, call):
    target = normalize_call(call)
    return tuple(candidate for candidate in candidates
                 if candidate.call == target)


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
    intent = detect_slam_intent(
        hand, _partner_minimum(auction, auction.actor_to_call), strain=trump)
    return memory.with_purpose(Purpose(
        kind='keycard_slam', owner=auction.actor_to_call,
        source_index=len(auction.calls), source_call=candidate.call, trump=trump,
        own_keycards=hand.keycard_count(trump),
        owns_trump_queen=hand.contains_rank(trump, 'Q'),
        grand_candidate=intent.grand, combined_min=intent.combined_min,
        rkcb_stage='await_keycard_answer'))


def _partner_minimum(auction, owner: str) -> int:
    partner = {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[owner]
    for index, call in enumerate(auction.calls):
        if auction.actor_at(index) == partner and normalize_call(call) == '1N':
            return PARTNER_1NT_MIN
    return PARTNER_DEFAULT_MIN


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


@dataclass(frozen=True)
class _StageResult:
    call: str | None = None
    error: str | None = None
    purpose: Purpose | None = None
    completes: bool = False
    authored_only: bool = False


def _keycard_slam(auction, trace, purpose, hand=None, profile=None,
                  candidates=()) -> _StageResult:
    if purpose.own_keycards is None or purpose.owns_trump_queen is None:
        return _StageResult(error='Keycard purpose lacks the asker\'s saved private count')
    stage = purpose.rkcb_stage or 'await_keycard_answer'
    frame = ordinary_rkcb_frame(trace)
    if stage == 'await_keycard_answer':
        return _choose_after_answer(auction, trace, purpose, hand, frame, profile,
                                    candidates)
    if stage == 'choose_continuation':
        return _choose_continuation(auction, trace, purpose, hand, frame, profile)
    if stage == 'await_relay_completion':
        return _observe_relay_completion(auction, purpose, hand, frame)
    if stage == 'place_after_5nt':
        return _choose_king_or_small_slam(auction, purpose, hand, frame)
    return _StageResult(error=f'Unknown RKCB continuation stage: {stage}')


def _choose_after_answer(auction, trace, purpose, hand, frame, profile=None,
                         candidates=()):
    meaning = _answer_meaning(trace, purpose)
    if not meaning or 'keycard_counts' not in meaning:
        return _StageResult(
            error='Partner keycard answer has no unambiguous public meaning',
            purpose=replace(purpose, rkcb_stage='choose_continuation'))
    category = ((frame.answer_category if frame is not None else None)
                or meaning.get('answer_category'))
    with_stage = replace(purpose, rkcb_stage='choose_continuation',
                         answer_category=category)
    if frame is not None and is_high_answer(frame):
        return _choose_high_answer(auction, purpose, with_stage, frame)
    if frame is not None and frame.keycard_counts:
        possible_counts = list(possible_partner_counts(
            frame, purpose.own_keycards))
    else:
        possible_counts = [count for count in meaning['keycard_counts']
                           if 0 <= 5 - purpose.own_keycards - count <= 5]
    missing = {5 - purpose.own_keycards - count for count in possible_counts
               if 0 <= 5 - purpose.own_keycards - count <= 5}
    if not missing:
        return _StageResult(
            error='Partner keycard answer is impossible with the asker\'s cards',
            purpose=with_stage)
    if len(missing) > 1:
        return _choose_ambiguous_continuation(
            auction, trace, purpose, hand, frame, with_stage, profile,
            candidates)
    missing_count = missing.pop()
    game, slam = f'5{purpose.trump}', f'6{purpose.trump}'
    if missing_count >= 2:
        return _game_or_rescue(auction, trace, purpose, hand, frame,
                               with_stage, profile)
    queen_known = (purpose.owns_trump_queen is True
                   or meaning.get('trump_queen') is True)
    if missing_count == 0 and queen_known and purpose.grand_candidate:
        return _StageResult(f'7{purpose.trump}', purpose=_completed(with_stage))
    if missing_count == 0 or queen_known:
        return _StageResult(slam, purpose=_completed(with_stage))
    if meaning.get('trump_queen') is False:
        return _game_or_rescue(auction, trace, purpose, hand, frame,
                               with_stage, profile)
    ask = queen_ask_call(auction, frame)
    if ask is not None:
        return _StageResult(ask, purpose=with_stage, authored_only=True)
    if not is_call_legal(auction, game):
        return _game_or_rescue(auction, trace, purpose, hand, frame,
                               with_stage, profile)
    return _StageResult(slam, purpose=_completed(with_stage))


def _choose_high_answer(auction, purpose, with_stage, frame):
    possible = possible_partner_counts(frame, purpose.own_keycards)
    all_keycards = any(purpose.own_keycards + count == 5
                       for count in possible)
    if all_keycards and purpose.owns_trump_queen and purpose.grand_candidate:
        invitations = high_answer_invitations(auction, frame)
        if invitations:
            return _StageResult(invitations[0], purpose=with_stage,
                                authored_only=True)
        seven = f'7{purpose.trump}'
        if is_call_legal(auction, seven):
            return _StageResult(seven, purpose=_completed(with_stage),
                                authored_only=True)
    return _StageResult('P', purpose=_completed(with_stage), authored_only=True)


def _choose_ambiguous_continuation(auction, trace, purpose, hand, frame,
                                   with_stage, profile, candidates):
    game = f'5{purpose.trump}'
    slam = f'6{purpose.trump}'
    proposed = [call for call in (game, slam) if is_call_legal(auction, call)]
    last = _last_non_pass_call(auction)
    if last is not None and (last == '5NT' or last.startswith('6')):
        proposed.append('P')
    if not proposed:
        return _StageResult(
            error='Partner keycard answer is ambiguous and no safe continuation is legal',
            purpose=with_stage)
    decision = compare_ambiguous_continuations(
        profile, auction, trace, hand, frame, tuple(proposed))
    if decision.unavailable or decision.call is None:
        return _StageResult(
            error=('Partner keycard answer leaves the number of missing '
                   'keycards ambiguous: ' + decision.reason),
            purpose=with_stage)
    return _StageResult(decision.call, purpose=_completed(with_stage))


def _last_non_pass_call(auction):
    for call in reversed(auction.calls):
        if call not in ('P', 'X', 'R'):
            return call
    return None


def _game_or_rescue(auction, trace, purpose, hand, frame, with_stage, profile):
    game = f'5{purpose.trump}'
    if five_trump_available(auction, purpose.trump):
        return _StageResult(game, purpose=_completed(with_stage))
    role = five_spade_role(auction, frame)
    if role != 'relay':
        return _StageResult(
            error='Five of trumps is unavailable and the five-spade relay is unavailable',
            purpose=with_stage)
    decision = compare_rescue_routes(
        profile, auction, trace, hand, purpose.trump, frame)
    if decision.unavailable or decision.call is None:
        return _StageResult(
            error='Rescue relay is unavailable: ' + decision.reason,
            purpose=with_stage)
    if decision.call == '5S':
        return _StageResult(
            '5S', purpose=replace(with_stage,
                                  rkcb_stage='await_relay_completion',
                                  relay_intent='rescue'),
            authored_only=True)
    return _StageResult(decision.call, purpose=_completed(with_stage),
                        authored_only=True)


def _choose_continuation(auction, trace, purpose, hand, frame, profile=None):
    if frame is None:
        return _StageResult(error='Ordinary keycard frame is unavailable')
    if frame.trump != purpose.trump:
        return _StageResult(error='Ordinary keycard frame changed the agreed trump')
    if frame.status == 'disrupted':
        return _StageResult(
            purpose=replace(purpose, status='disrupted',
                            answer_category=frame.answer_category))
    if frame.status == 'completed':
        return _StageResult(
            purpose=replace(purpose, status='completed',
                            answer_category=frame.answer_category))
    if frame.status == 'relay_completed':
        return _observe_relay_completion(auction, purpose, hand, frame)
    if frame.status == 'relay_pending':
        return _StageResult(
            error='Relay is awaiting partner\'s forced five notrump',
            purpose=purpose)
    if frame.continuation_stage == 'queen_ask':
        return _StageResult(
            error='QUEEN_ASK_CONTINUATION_UNAUTHORED: the queen-ask answer table is not authored',
            purpose=purpose)
    if frame.continuation_stage == 'counterinvited':
        if frame.counterinvite_count > 1:
            return _StageResult(
                error='No second counter-invitation is allowed',
                purpose=purpose)
        decision = compare_grand_routes(
            profile, auction, trace, hand, purpose.trump, frame)
        call = decision.call or f'6{purpose.trump}'
        return _StageResult(call, purpose=_completed(purpose),
                            authored_only=True)
    return _StageResult(
        error='No authored continuation matches this keycard frame',
        purpose=purpose)


def _observe_relay_completion(auction, purpose, hand, frame):
    if frame is None:
        return _StageResult(error='Ordinary keycard frame is unavailable')
    if frame.status == 'relay_pending':
        return _StageResult(
            error='Partner has not completed the forced five notrump relay',
            purpose=purpose)
    if frame.status != 'relay_completed':
        return _StageResult(
            error='The five spade relay is not awaiting completion',
            purpose=purpose)
    advanced = replace(purpose, rkcb_stage='place_after_5nt')
    return _choose_king_or_small_slam(auction, advanced, hand, frame)


def _choose_king_or_small_slam(auction, purpose, hand, frame):
    if frame is None or frame.status != 'relay_completed':
        return _StageResult(
            error='The five notrump relay has not been completed',
            purpose=purpose)
    if purpose.relay_intent == 'rescue':
        return _StageResult('P', purpose=_completed(purpose))
    if purpose.relay_intent != 'show_lowest_king':
        return _StageResult(error='Saved keycard relay intent is missing',
                            purpose=purpose)
    king = lowest_showable_side_king(
        hand, purpose.trump, auction, denied=purpose.not_required_kings)
    if king is not None:
        return _StageResult(king, purpose=_completed(purpose))
    small_slam = relay_terminal_call(auction, hand, purpose.trump)
    if small_slam is not None:
        return _StageResult(small_slam, purpose=_completed(purpose))
    return _StageResult(
        error='No legal king or small-slam return is available after the relay',
        purpose=purpose)


def _completed(purpose):
    return replace(purpose, status='completed')


def _answer_meaning(trace, purpose):
    answer_index = purpose.source_index + 2
    return next((entry['public_meaning'] for entry in trace.applied_meanings
                 if entry['index'] == answer_index
                 and entry['seat'] != purpose.owner), None)


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
