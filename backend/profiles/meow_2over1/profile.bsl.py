# BSL source for Partner bidding agreements.
# Edit this file as the source of truth for this Partnership Profile.

Profile(
    id='meow_2over1',
    name='Meow 2/1 Benchmark',
    version='0.1.0',
    description=("Practical benchmark Partnership Profile for Meow Li's 2/1 agreements. This executable slice is "
     'organized as portable Gadgets plus profile-level Python policy functions: notrump openings, regular Stayman, Puppet Stayman stubs, '
     'four-way transfers, Texas transfers, standalone slam tools, simple major raises, Bergen, Drury, '
     'Jacoby 2N, and Kokish game tries, minor opening continuations, checkback/XYZ, and '
     'seat/vulnerability-sensitive preempts, and a strong 2C skeleton.\n'),
    author={'name': 'Meow Li'},
    gadgets=['meow_two_over_one_core',
     'meow_minor_opening_structure',
     'meow_strong_two_club',
     'meow_preemptive_openings',
     'meow_gambling_3nt',
     'meow_one_notrump_opening',
     'meow_two_notrump_opening',
     'meow_inverted_minors',
     'meow_crisscross_minor_raises',
     'meow_two_way_nmf_xyz',
     'meow_spiral_3344',
     'meow_notrump_response_basics',
     'meow_regular_stayman_over_1n',
     'meow_puppet_stayman_over_1n',
     'meow_puppet_stayman_over_2n',
     'meow_four_way_transfers_over_1n',
     'meow_texas_transfers_over_1n',
     'meow_quantitative_notrump',
     'meow_gerber_over_notrump',
     'meow_control_bidding',
     'meow_kickback_keycard',
     'meow_minorwood_keycard',
     'meow_exclusion_keycard',
     'meow_rkcb_1430',
     'meow_targeted_king_ask',
     'meow_simple_major_raise',
     'meow_forcing_notrump_after_major',
     'meow_bergen_raises',
     'meow_two_way_reverse_drury',
     'meow_jacoby_2nt_major_raise',
     'meow_kokish_game_tries'],
)
