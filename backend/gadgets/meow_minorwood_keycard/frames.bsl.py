# BSL source for Partner bidding agreements.
# Edit this file as the source of truth for this Gadget object set.

Frame(
    id='frame_1',
    frame_type='minorwood_1430',
    context={'auction_pattern': '1NP2NP3CP', 'seat_positions': [1, 2, 3, 4]},
    source_call='4D',
    description='Minorwood 1430 frame after 4D asks for diamond keycards.',
    system_notes='4D opens a diamond keycard-answer frame when diamonds are agreed.',
    variables={'method': 'minorwood_1430', 'trump_suit': 'D', 'asker': 'actor', 'responder': 'partner'},
    obligation={'actor': 'responder', 'action': 'answer_frame', 'capabilities': ['answer_frame', 'keycard_response']},
    stages=['keycard_response', 'queen_or_king_continuation', 'final_placement'],
    allowed_continuations=['keycard_response', 'queen_ask', 'specific_king_ask', 'signoff', 'slam_placement'],
    break_conditions=['undefined_interference_without_policy'],
    closes=['*'],
    close_on_actions=['place_contract', 'pass_final_contract', 'signoff'],
    close_on_act_types=['final_placement', 'signoff'],
)
