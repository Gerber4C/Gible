# BSL source for Partner bidding agreements.
# Edit this file as the source of truth for this Gadget object set.

Frame(
    id='frame_1',
    frame_type='gerber',
    context={'auction_pattern': '1NP', 'seat_positions': [1, 2, 3, 4]},
    source_call='4C',
    description='Gerber ace-asking frame after 4C in a notrump-focused auction.',
    system_notes='4C Gerber opens an ace-answer frame, with possible later king asks or placement.',
    variables={'method': 'gerber', 'target_suit': 'N', 'asker': 'actor', 'responder': 'partner'},
    obligation={'actor': 'responder', 'action': 'answer_frame', 'capabilities': ['answer_frame', 'ace_response']},
    stages=['ace_response', 'king_or_placement', 'final_placement'],
    allowed_continuations=['ace_ask_response', 'king_ask', 'signoff', 'slam_placement'],
    break_conditions=['undefined_interference_without_policy'],
    closes=['*'],
    close_on_actions=['place_contract', 'pass_final_contract', 'signoff'],
    close_on_act_types=['final_placement', 'signoff'],
)
