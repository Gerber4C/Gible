Call(
    id='fn_1',
    when=Auction('1HP'),
    bid=Bid('1S'),
    selection=Selection(criteria=[
        Criterion('six_plus_hcp', condition=self.hcp >= 6),
        Criterion('four_spades', condition=self.S >= 4),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'forcing'], action='one_level_response', target_suit=S, shown_length_min=4, alertable=False),
    effects=[
        State('responder.length.S', owner='responder', min_value=4, source='one_level_response'),
        State('responder.hcp', owner='responder', min_value=6, source='one_level_response'),
    ],
    description='Responder bids 1S over 1H with at least four spades.',
)

Call(
    id='fn_2',
    when=Auction('1HP'),
    bid=Bid('1N'),
    selection=Selection(criteria=[
        Criterion('forcing_notrump_range', condition=6 <= self.hcp <= 12),
        Criterion('no_heart_raise', condition=self.H <= 2),
        Criterion('no_four_spades', condition=self.S <= 3),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'forcing'], action='forcing_notrump_response', target_suit=N, hcp_range=[6, 12], alertable=False),
    effects=[
        State('forcing_notrump_response', owner='responder', opening_suit=H, hcp_min=6, hcp_max=12),
        State('responder.hcp', owner='responder', min_value=6, max_value=12, source='forcing_notrump'),
        State('responder.length.H', owner='responder', max_value=2, source='forcing_notrump_no_raise'),
        State('responder.length.S', owner='responder', max_value=3, source='forcing_notrump_no_spades'),
    ],
    description='Forcing 1N over 1H: 6-12, no heart raise, and no four-card spade response.',
)

Call(
    id='fn_3',
    when=Auction('1SP'),
    bid=Bid('1N'),
    selection=Selection(criteria=[
        Criterion('forcing_notrump_range', condition=6 <= self.hcp <= 12),
        Criterion('no_spade_raise', condition=self.S <= 2),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'forcing'], action='forcing_notrump_response', target_suit=N, hcp_range=[6, 12], alertable=False),
    effects=[
        State('forcing_notrump_response', owner='responder', opening_suit=S, hcp_min=6, hcp_max=12),
        State('responder.hcp', owner='responder', min_value=6, max_value=12, source='forcing_notrump'),
        State('responder.length.S', owner='responder', max_value=2, source='forcing_notrump_no_raise'),
    ],
    description='Forcing 1N over 1S: 6-12 without a direct spade raise.',
)

Call(
    id='fn_4',
    when=Auction('1HP'),
    bid=Bid('2C'),
    selection=Selection(criteria=[
        Criterion('game_force_values', condition=self.hcp >= 12),
        Criterion('four_clubs', condition=self.C >= 4),
        Criterion('no_four_spades', condition=self.S <= 3),
        Criterion('poor_heart_support', condition=self.H <= 2),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'forcing'], action='two_over_one_game_force', target_suit=C, shown_length_min=4, alertable=False),
    effects=[
        State('partnership.force_status', owner='partnership', value='game_forcing', source='two_over_one'),
        State('responder.length.C', owner='responder', min_value=4, source='two_over_one'),
    ],
)

Call(
    id='fn_5',
    when=Auction('1HP'),
    bid=Bid('2D'),
    selection=Selection(criteria=[
        Criterion('game_force_values', condition=self.hcp >= 12),
        Criterion('four_diamonds', condition=self.D >= 4),
        Criterion('no_four_spades', condition=self.S <= 3),
        Criterion('poor_heart_support', condition=self.H <= 2),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'forcing'], action='two_over_one_game_force', target_suit=D, shown_length_min=4, alertable=False),
    effects=[
        State('partnership.force_status', owner='partnership', value='game_forcing', source='two_over_one'),
        State('responder.length.D', owner='responder', min_value=4, source='two_over_one'),
    ],
)

Call(
    id='fn_6',
    when=Auction('1SP'),
    bid=Bid('2C'),
    selection=Selection(criteria=[
        Criterion('game_force_values', condition=self.hcp >= 12),
        Criterion('four_clubs', condition=self.C >= 4),
        Criterion('poor_spade_support', condition=self.S <= 2),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'forcing'], action='two_over_one_game_force', target_suit=C, shown_length_min=4, alertable=False),
    effects=[
        State('partnership.force_status', owner='partnership', value='game_forcing', source='two_over_one'),
        State('responder.length.C', owner='responder', min_value=4, source='two_over_one'),
    ],
)

Call(
    id='fn_7',
    when=Auction('1SP'),
    bid=Bid('2D'),
    selection=Selection(criteria=[
        Criterion('game_force_values', condition=self.hcp >= 12),
        Criterion('four_diamonds', condition=self.D >= 4),
        Criterion('poor_spade_support', condition=self.S <= 2),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'forcing'], action='two_over_one_game_force', target_suit=D, shown_length_min=4, alertable=False),
    effects=[
        State('partnership.force_status', owner='partnership', value='game_forcing', source='two_over_one'),
        State('responder.length.D', owner='responder', min_value=4, source='two_over_one'),
    ],
)

Call(
    id='fn_8',
    when=Auction('1SP'),
    bid=Bid('2H'),
    selection=Selection(criteria=[
        Criterion('game_force_values', condition=self.hcp >= 12),
        Criterion('five_hearts', condition=self.H >= 5),
        Criterion('poor_spade_support', condition=self.S <= 2),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'forcing'], action='two_over_one_game_force', target_suit=H, shown_length_min=5, alertable=False),
    effects=[
        State('partnership.force_status', owner='partnership', value='game_forcing', source='two_over_one'),
        State('responder.length.H', owner='responder', min_value=5, source='two_over_one'),
    ],
)
