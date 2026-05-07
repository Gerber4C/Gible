# BSL source for Partner bidding agreements.
# Edit this file as the source of truth for this Gadget object set.

Frame(
    id='frame_1',
    frame_type='control_bidding',
    context={'auction_pattern': '1NP2DP3HP', 'seat_positions': [1, 2, 3, 4]},
    source_call='4D',
    description='Cooperative control-bidding frame after a diamond control bid in the heart-transfer route.',
    system_notes=('A control bid opens a cooperative slam frame; later calls may sign off, continue controls, or '
     'ask keycards.'),
    variables={'agreed_suit': 'H', 'control_suit': 'D', 'initiator': 'actor', 'responder': 'partner'},
    stages=['cooperation', 'keycard_or_signoff', 'final_placement'],
    allowed_continuations=['control_showing', 'keycard_asking', 'signoff', 'slam_placement'],
    break_conditions=['undefined_interference_without_policy'],
    closes=['major_transfer', 'minor_transfer', 'transfer'],
    close_on_actions=['place_contract', 'pass_final_contract', 'signoff'],
    close_on_act_types=['final_placement', 'signoff'],
)
