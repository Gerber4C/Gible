# BSL source for Partner bidding agreements.
# Edit this file as the source of truth for this Gadget object set.

Frame(
    id='frame_1',
    frame_type='rkcb_1430',
    context={'auction_pattern': '*'},
    source_call='4N',
    description='Active RKCB 1430 keycard-asking frame after 4N is interpreted as RKCB.',
    system_notes='A 4N RKCB ask opens a keycard-answer frame using 1430 responses.',
    variables={'method': '1430', 'trump_suit_source': 'agreed_suit', 'asker': 'actor', 'responder': 'partner'},
    obligation={'actor': 'responder', 'action': 'answer_frame', 'capabilities': ['answer_frame', 'keycard_response']},
    stages=['keycard_response', 'queen_or_king_continuation', 'final_placement'],
    allowed_continuations=['keycard_response', 'queen_ask', 'specific_king_ask', 'signoff', 'slam_placement'],
    break_conditions=['undefined_interference_without_policy'],
    closes=['*'],
    close_on_actions=['place_contract', 'pass_final_contract', 'signoff'],
    close_on_act_types=['final_placement', 'signoff'],
)
