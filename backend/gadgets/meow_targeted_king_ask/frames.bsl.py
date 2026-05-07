# BSL source for Partner bidding agreements.
# Edit this file as the source of truth for this Gadget object set.

Frame(
    id='frame_1',
    frame_type='targeted_king_ask',
    context={'auction_pattern': '1NP2DP3HP4NP5DP', 'seat_positions': [1, 2, 3, 4]},
    source_call='5N',
    description='Targeted diamond-king ask frame after 5N in the benchmark heart RKCB route.',
    system_notes='5N asks for a named king, responder answers, and the asker places the final contract.',
    variables={'trump_suit': 'H',
     'target_suit': 'D',
     'target_rank': 'K',
     'asker': 'actor',
     'responder': 'partner'},
    obligation={'actor': 'responder', 'action': 'answer_frame', 'capabilities': ['answer_frame', 'specific_king_response']},
    stages=['targeted_response', 'final_placement'],
    allowed_continuations=['targeted_king_response', 'signoff', 'slam_placement'],
    break_conditions=['undefined_interference_without_policy'],
    closes=['*'],
    close_on_actions=['place_contract', 'pass_final_contract', 'signoff'],
    close_on_act_types=['final_placement', 'signoff'],
)
