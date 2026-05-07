# BSL source for Partner bidding agreements.
# Edit this file as the source of truth for this Gadget object set.

Frame(
    id='frame_1',
    frame_type='exclusion_1430',
    context={'auction_pattern': '1NP2DP3HP', 'seat_positions': [1, 2, 3, 4]},
    source_call='5D',
    description='Exclusion keycard frame after 5D asks for heart keycards excluding diamonds.',
    system_notes='5D opens a keycard-answer frame for hearts while excluding the diamond ace.',
    variables={'method': 'exclusion_1430',
     'trump_suit': 'H',
     'excluded_suit': 'D',
     'asker': 'actor',
     'responder': 'partner'},
    obligation={'actor': 'responder', 'action': 'answer_frame', 'capabilities': ['answer_frame', 'keycard_response']},
    stages=['keycard_response', 'queen_or_king_continuation', 'final_placement'],
    allowed_continuations=['keycard_response', 'queen_ask', 'specific_king_ask', 'signoff', 'slam_placement'],
    break_conditions=['undefined_interference_without_policy'],
    closes=['*'],
    close_on_actions=['place_contract', 'pass_final_contract', 'signoff'],
    close_on_act_types=['final_placement', 'signoff'],
)
