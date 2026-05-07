# BSL source for Partner bidding agreements.
# Edit this file as the source of truth for this Gadget object set.

Frame(
    id='frame_1',
    frame_type='major_transfer',
    context={'auction_pattern': '1NP', 'seat_positions': [1, 2, 3, 4]},
    source_call='2D',
    description='Live heart-transfer frame after responder bids 2D over 1N.',
    system_notes='A 2D transfer creates a heart-transfer context until responder places or redirects the contract.',
    variables={'target_suit': 'H', 'initiator': 'responder', 'acceptor': 'opener'},
    stages=['opener_rebid', 'responder_continuation'],
    allowed_continuations=['transfer_completion',
     'superaccept',
     'responder_signoff',
     'responder_invite',
     'responder_second_suit',
     'responder_slam_exploration'],
    break_conditions=['undefined_interference_without_policy'],
    close_on_actions=['place_contract', 'pass_final_contract', 'signoff'],
    close_on_act_types=['final_placement', 'signoff'],
)
