# BSL source for Partner bidding agreements.
# Opener-rebid candidates that need policy comparison after a one-minor opening.

Call(
    id='cs_31',
    when=Auction('1CP1DP', seats=[1, 2, 3, 4]),
    bid=Bid('2N'),
    selection=Selection(criteria=[
        Criterion('eighteen_to_nineteen', condition=18 <= self.hcp <= 19),
        Criterion('balanced', condition=self.balanced),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'invitational'], action='opener_notrump_rebid', target_suit=N, hcp_range=[18, 19], alertable=False),
    effects=[
        State('opener.hcp', owner='opener', min_value=18, max_value=19, source='jump_notrump_rebid'),
        State('opener.shape', owner='opener', value='balanced', source='jump_notrump_rebid'),
    ],
    description='Opener rebids 2N after 1C-1D with an 18-19 balanced hand when no one-level major is chosen.',
    system_notes='After 1C-1D, 2N shows about 18-19 balanced values.',
)

Call(
    id='cs_32',
    when=Auction('1CP1HP', seats=[1, 2, 3, 4]),
    bid=Bid('2N'),
    selection=Selection(criteria=[
        Criterion('eighteen_to_nineteen', condition=18 <= self.hcp <= 19),
        Criterion('balanced', condition=self.balanced),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'invitational'], action='opener_notrump_rebid', target_suit=N, hcp_range=[18, 19], alertable=False),
    effects=[
        State('opener.hcp', owner='opener', min_value=18, max_value=19, source='jump_notrump_rebid'),
        State('opener.shape', owner='opener', value='balanced', source='jump_notrump_rebid'),
    ],
    description='Opener rebids 2N after 1C-1H with 18-19 balanced values.',
    system_notes='After 1C-1H, 2N shows about 18-19 balanced values.',
)

Call(
    id='cs_33',
    when=Auction('1CP1SP', seats=[1, 2, 3, 4]),
    bid=Bid('2N'),
    selection=Selection(criteria=[
        Criterion('eighteen_to_nineteen', condition=18 <= self.hcp <= 19),
        Criterion('balanced', condition=self.balanced),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'invitational'], action='opener_notrump_rebid', target_suit=N, hcp_range=[18, 19], alertable=False),
    effects=[
        State('opener.hcp', owner='opener', min_value=18, max_value=19, source='jump_notrump_rebid'),
        State('opener.shape', owner='opener', value='balanced', source='jump_notrump_rebid'),
    ],
    description='Opener rebids 2N after 1C-1S with 18-19 balanced values.',
    system_notes='After 1C-1S, 2N shows about 18-19 balanced values.',
)

Call(
    id='cs_34',
    when=Auction('1DP1HP', seats=[1, 2, 3, 4]),
    bid=Bid('2N'),
    selection=Selection(criteria=[
        Criterion('eighteen_to_nineteen', condition=18 <= self.hcp <= 19),
        Criterion('balanced', condition=self.balanced),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'invitational'], action='opener_notrump_rebid', target_suit=N, hcp_range=[18, 19], alertable=False),
    effects=[
        State('opener.hcp', owner='opener', min_value=18, max_value=19, source='jump_notrump_rebid'),
        State('opener.shape', owner='opener', value='balanced', source='jump_notrump_rebid'),
    ],
    description='Opener rebids 2N after 1D-1H with 18-19 balanced values.',
    system_notes='After 1D-1H, 2N shows about 18-19 balanced values.',
)

Call(
    id='cs_35',
    when=Auction('1DP1SP', seats=[1, 2, 3, 4]),
    bid=Bid('2N'),
    selection=Selection(criteria=[
        Criterion('eighteen_to_nineteen', condition=18 <= self.hcp <= 19),
        Criterion('balanced', condition=self.balanced),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'invitational'], action='opener_notrump_rebid', target_suit=N, hcp_range=[18, 19], alertable=False),
    effects=[
        State('opener.hcp', owner='opener', min_value=18, max_value=19, source='jump_notrump_rebid'),
        State('opener.shape', owner='opener', value='balanced', source='jump_notrump_rebid'),
    ],
    description='Opener rebids 2N after 1D-1S with 18-19 balanced values.',
    system_notes='After 1D-1S, 2N shows about 18-19 balanced values.',
)

Call(
    id='cs_36',
    when=Auction('1CP1DP', seats=[1, 2, 3, 4]),
    bid=Bid('2C'),
    selection=Selection(criteria=[Criterion('five_clubs', condition=self.C >= 5)]),
    meaning=Meaning(nature=['natural'], acts=['descriptive'], action='opener_minor_rebid', target_suit=C, shown_length_min=5, alertable=False),
    effects=[State('opener.length.C', owner='opener', min_value=5, source='opener_minor_rebid')],
    description='Opener rebids 2C after 1C-1D with at least five clubs when no major or notrump rebid is preferred.',
    system_notes='After 1C-1D, 2C is natural and usually shows at least five clubs.',
)

Call(
    id='cs_37',
    when=Auction('1CP1HP', seats=[1, 2, 3, 4]),
    bid=Bid('2C'),
    selection=Selection(criteria=[Criterion('five_clubs', condition=self.C >= 5)]),
    meaning=Meaning(nature=['natural'], acts=['descriptive'], action='opener_minor_rebid', target_suit=C, shown_length_min=5, alertable=False),
    effects=[State('opener.length.C', owner='opener', min_value=5, source='opener_minor_rebid')],
    description='Opener rebids 2C after 1C-1H with at least five clubs.',
    system_notes='After 1C-1H, 2C is natural and usually shows at least five clubs.',
)

Call(
    id='cs_38',
    when=Auction('1CP1SP', seats=[1, 2, 3, 4]),
    bid=Bid('2C'),
    selection=Selection(criteria=[Criterion('five_clubs', condition=self.C >= 5)]),
    meaning=Meaning(nature=['natural'], acts=['descriptive'], action='opener_minor_rebid', target_suit=C, shown_length_min=5, alertable=False),
    effects=[State('opener.length.C', owner='opener', min_value=5, source='opener_minor_rebid')],
    description='Opener rebids 2C after 1C-1S with at least five clubs.',
    system_notes='After 1C-1S, 2C is natural and usually shows at least five clubs.',
)

Call(
    id='cs_39',
    when=Auction('1DP1HP', seats=[1, 2, 3, 4]),
    bid=Bid('2D'),
    selection=Selection(criteria=[Criterion('five_diamonds', condition=self.D >= 5)]),
    meaning=Meaning(nature=['natural'], acts=['descriptive'], action='opener_minor_rebid', target_suit=D, shown_length_min=5, alertable=False),
    effects=[State('opener.length.D', owner='opener', min_value=5, source='opener_minor_rebid')],
    description='Opener rebids 2D after 1D-1H with at least five diamonds.',
    system_notes='After 1D-1H, 2D is natural and usually shows at least five diamonds.',
)

Call(
    id='cs_40',
    when=Auction('1DP1SP', seats=[1, 2, 3, 4]),
    bid=Bid('2D'),
    selection=Selection(criteria=[Criterion('five_diamonds', condition=self.D >= 5)]),
    meaning=Meaning(nature=['natural'], acts=['descriptive'], action='opener_minor_rebid', target_suit=D, shown_length_min=5, alertable=False),
    effects=[State('opener.length.D', owner='opener', min_value=5, source='opener_minor_rebid')],
    description='Opener rebids 2D after 1D-1S with at least five diamonds.',
    system_notes='After 1D-1S, 2D is natural and usually shows at least five diamonds.',
)

Call(
    id='cs_41',
    when=Auction('1DP1HP', seats=[1, 2, 3, 4]),
    bid=Bid('2C'),
    selection=Selection(criteria=[Criterion('four_clubs', condition=self.C >= 4)]),
    meaning=Meaning(nature=['natural'], acts=['descriptive'], action='opener_second_suit_rebid', target_suit=C, shown_length_min=4, alertable=False),
    effects=[State('opener.length.C', owner='opener', min_value=4, source='opener_second_suit_rebid')],
    description='Opener rebids 2C after 1D-1H as a natural lower-ranking second suit.',
    system_notes='After 1D-1H, 2C is natural and shows clubs.',
)

Call(
    id='cs_42',
    when=Auction('1DP1SP', seats=[1, 2, 3, 4]),
    bid=Bid('2C'),
    selection=Selection(criteria=[Criterion('four_clubs', condition=self.C >= 4)]),
    meaning=Meaning(nature=['natural'], acts=['descriptive'], action='opener_second_suit_rebid', target_suit=C, shown_length_min=4, alertable=False),
    effects=[State('opener.length.C', owner='opener', min_value=4, source='opener_second_suit_rebid')],
    description='Opener rebids 2C after 1D-1S as a natural lower-ranking second suit.',
    system_notes='After 1D-1S, 2C is natural and shows clubs.',
)

Call(
    id='cs_43',
    when=Auction('1CP1HP', seats=[1, 2, 3, 4]),
    bid=Bid('2D'),
    selection=Selection(criteria=[
        Criterion('reverse_values', condition=self.hcp >= 16),
        Criterion('four_diamonds', condition=self.D >= 4),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'forcing'], action='opener_reverse', target_suit=D, shown_length_min=4, alertable=False),
    effects=[
        State('opener.length.D', owner='opener', min_value=4, source='opener_reverse'),
        State('opener.hcp', owner='opener', min_value=16, source='opener_reverse'),
        State('partnership.force_status', owner='partnership', value='one_round_forcing', source='opener_reverse'),
    ],
    description='Opener reverses into diamonds after 1C-1H, showing extras.',
    system_notes='After 1C-1H, 2D is a reverse and shows extra values.',
)

Call(
    id='cs_44',
    when=Auction('1CP1SP', seats=[1, 2, 3, 4]),
    bid=Bid('2D'),
    selection=Selection(criteria=[
        Criterion('reverse_values', condition=self.hcp >= 16),
        Criterion('four_diamonds', condition=self.D >= 4),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'forcing'], action='opener_reverse', target_suit=D, shown_length_min=4, alertable=False),
    effects=[
        State('opener.length.D', owner='opener', min_value=4, source='opener_reverse'),
        State('opener.hcp', owner='opener', min_value=16, source='opener_reverse'),
        State('partnership.force_status', owner='partnership', value='one_round_forcing', source='opener_reverse'),
    ],
    description='Opener reverses into diamonds after 1C-1S, showing extras.',
    system_notes='After 1C-1S, 2D is a reverse and shows extra values.',
)

Call(
    id='cs_45',
    when=Auction('1CP1SP', seats=[1, 2, 3, 4]),
    bid=Bid('2H'),
    selection=Selection(criteria=[
        Criterion('reverse_values', condition=self.hcp >= 16),
        Criterion('four_hearts', condition=self.H >= 4),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'forcing'], action='opener_reverse', target_suit=H, shown_length_min=4, alertable=False),
    effects=[
        State('opener.length.H', owner='opener', min_value=4, source='opener_reverse'),
        State('opener.hcp', owner='opener', min_value=16, source='opener_reverse'),
        State('partnership.force_status', owner='partnership', value='one_round_forcing', source='opener_reverse'),
    ],
    description='Opener reverses into hearts after 1C-1S, showing extras.',
    system_notes='After 1C-1S, 2H is a reverse and shows extra values.',
)

Call(
    id='cs_46',
    when=Auction('1DP1SP', seats=[1, 2, 3, 4]),
    bid=Bid('2H'),
    selection=Selection(criteria=[
        Criterion('reverse_values', condition=self.hcp >= 16),
        Criterion('four_hearts', condition=self.H >= 4),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'forcing'], action='opener_reverse', target_suit=H, shown_length_min=4, alertable=False),
    effects=[
        State('opener.length.H', owner='opener', min_value=4, source='opener_reverse'),
        State('opener.hcp', owner='opener', min_value=16, source='opener_reverse'),
        State('partnership.force_status', owner='partnership', value='one_round_forcing', source='opener_reverse'),
    ],
    description='Opener reverses into hearts after 1D-1S, showing extras.',
    system_notes='After 1D-1S, 2H is a reverse and shows extra values.',
)

Call(
    id='cs_47',
    when=Auction('1CP1HP', seats=[1, 2, 3, 4]),
    bid=Bid('3H'),
    selection=Selection(criteria=[
        Criterion('strong_raise_values', condition=self.hcp >= 16),
        Criterion('four_heart_support', condition=self.H >= 4),
    ]),
    meaning=Meaning(nature=['natural'], acts=['support_showing', 'invitational'], action='opener_jump_raise', target_suit=H, alertable=False),
    effects=[
        State('partnership.agreed_suit', owner='partnership', value='H', source='opener_jump_raise'),
        State('opener.hcp', owner='opener', min_value=16, source='opener_jump_raise'),
        State('opener.length.H', owner='opener', min_value=4, source='opener_jump_raise'),
    ],
    description='Opener jump-raises hearts after 1C-1H with extras and four-card support.',
    system_notes='After 1C-1H, 3H is a strong raise with four-card support.',
)

Call(
    id='cs_48',
    when=Auction('1CP1SP', seats=[1, 2, 3, 4]),
    bid=Bid('3S'),
    selection=Selection(criteria=[
        Criterion('strong_raise_values', condition=self.hcp >= 16),
        Criterion('four_spade_support', condition=self.S >= 4),
    ]),
    meaning=Meaning(nature=['natural'], acts=['support_showing', 'invitational'], action='opener_jump_raise', target_suit=S, alertable=False),
    effects=[
        State('partnership.agreed_suit', owner='partnership', value='S', source='opener_jump_raise'),
        State('opener.hcp', owner='opener', min_value=16, source='opener_jump_raise'),
        State('opener.length.S', owner='opener', min_value=4, source='opener_jump_raise'),
    ],
    description='Opener jump-raises spades after 1C-1S with extras and four-card support.',
    system_notes='After 1C-1S, 3S is a strong raise with four-card support.',
)

Call(
    id='cs_49',
    when=Auction('1DP1HP', seats=[1, 2, 3, 4]),
    bid=Bid('3H'),
    selection=Selection(criteria=[
        Criterion('strong_raise_values', condition=self.hcp >= 16),
        Criterion('four_heart_support', condition=self.H >= 4),
    ]),
    meaning=Meaning(nature=['natural'], acts=['support_showing', 'invitational'], action='opener_jump_raise', target_suit=H, alertable=False),
    effects=[
        State('partnership.agreed_suit', owner='partnership', value='H', source='opener_jump_raise'),
        State('opener.hcp', owner='opener', min_value=16, source='opener_jump_raise'),
        State('opener.length.H', owner='opener', min_value=4, source='opener_jump_raise'),
    ],
    description='Opener jump-raises hearts after 1D-1H with extras and four-card support.',
    system_notes='After 1D-1H, 3H is a strong raise with four-card support.',
)

Call(
    id='cs_50',
    when=Auction('1DP1SP', seats=[1, 2, 3, 4]),
    bid=Bid('3S'),
    selection=Selection(criteria=[
        Criterion('strong_raise_values', condition=self.hcp >= 16),
        Criterion('four_spade_support', condition=self.S >= 4),
    ]),
    meaning=Meaning(nature=['natural'], acts=['support_showing', 'invitational'], action='opener_jump_raise', target_suit=S, alertable=False),
    effects=[
        State('partnership.agreed_suit', owner='partnership', value='S', source='opener_jump_raise'),
        State('opener.hcp', owner='opener', min_value=16, source='opener_jump_raise'),
        State('opener.length.S', owner='opener', min_value=4, source='opener_jump_raise'),
    ],
    description='Opener jump-raises spades after 1D-1S with extras and four-card support.',
    system_notes='After 1D-1S, 3S is a strong raise with four-card support.',
)

Call(
    id='cs_51',
    when=Auction('1CP1DP', seats=[1, 2, 3, 4]),
    bid=Bid('2H'),
    selection=Selection(criteria=[
        Criterion('jump_shift_values', condition=self.hcp >= 18),
        Criterion('five_clubs', condition=self.C >= 5),
        Criterion('four_hearts', condition=self.H >= 4),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'game_forcing'], action='opener_jump_shift', target_suit=H, shown_length_min=4, alertable=False),
    effects=[
        State('opener.length.C', owner='opener', min_value=5, source='opener_jump_shift'),
        State('opener.length.H', owner='opener', min_value=4, source='opener_jump_shift'),
        State('opener.hcp', owner='opener', min_value=18, source='opener_jump_shift'),
        State('partnership.force_status', owner='partnership', value='game_forcing', source='opener_jump_shift'),
    ],
    description='Opener jump-shifts to 2H after 1C-1D with a strong 5+ club and 4+ heart hand.',
    system_notes='After 1C-1D, 2H is a strong natural jump shift showing clubs and hearts, game forcing.',
)

Call(
    id='cs_52',
    when=Auction('1CP1DP', seats=[1, 2, 3, 4]),
    bid=Bid('2S'),
    selection=Selection(criteria=[
        Criterion('jump_shift_values', condition=self.hcp >= 18),
        Criterion('five_clubs', condition=self.C >= 5),
        Criterion('four_spades', condition=self.S >= 4),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'game_forcing'], action='opener_jump_shift', target_suit=S, shown_length_min=4, alertable=False),
    effects=[
        State('opener.length.C', owner='opener', min_value=5, source='opener_jump_shift'),
        State('opener.length.S', owner='opener', min_value=4, source='opener_jump_shift'),
        State('opener.hcp', owner='opener', min_value=18, source='opener_jump_shift'),
        State('partnership.force_status', owner='partnership', value='game_forcing', source='opener_jump_shift'),
    ],
    description='Opener jump-shifts to 2S after 1C-1D with a strong 5+ club and 4+ spade hand.',
    system_notes='After 1C-1D, 2S is a strong natural jump shift showing clubs and spades, game forcing.',
)

Call(
    id='cs_53',
    when=Auction('1CP1HP', seats=[1, 2, 3, 4]),
    bid=Bid('2S'),
    selection=Selection(criteria=[
        Criterion('jump_shift_values', condition=self.hcp >= 18),
        Criterion('five_clubs', condition=self.C >= 5),
        Criterion('four_spades', condition=self.S >= 4),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'game_forcing'], action='opener_jump_shift', target_suit=S, shown_length_min=4, alertable=False),
    effects=[
        State('opener.length.C', owner='opener', min_value=5, source='opener_jump_shift'),
        State('opener.length.S', owner='opener', min_value=4, source='opener_jump_shift'),
        State('opener.hcp', owner='opener', min_value=18, source='opener_jump_shift'),
        State('partnership.force_status', owner='partnership', value='game_forcing', source='opener_jump_shift'),
    ],
    description='Opener jump-shifts to 2S after 1C-1H with a strong 5+ club and 4+ spade hand.',
    system_notes='After 1C-1H, 2S is a strong natural jump shift showing clubs and spades, game forcing.',
)

Call(
    id='cs_54',
    when=Auction('1DP1HP', seats=[1, 2, 3, 4]),
    bid=Bid('2S'),
    selection=Selection(criteria=[
        Criterion('jump_shift_values', condition=self.hcp >= 18),
        Criterion('five_diamonds', condition=self.D >= 5),
        Criterion('four_spades', condition=self.S >= 4),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'game_forcing'], action='opener_jump_shift', target_suit=S, shown_length_min=4, alertable=False),
    effects=[
        State('opener.length.D', owner='opener', min_value=5, source='opener_jump_shift'),
        State('opener.length.S', owner='opener', min_value=4, source='opener_jump_shift'),
        State('opener.hcp', owner='opener', min_value=18, source='opener_jump_shift'),
        State('partnership.force_status', owner='partnership', value='game_forcing', source='opener_jump_shift'),
    ],
    description='Opener jump-shifts to 2S after 1D-1H with a strong 5+ diamond and 4+ spade hand.',
    system_notes='After 1D-1H, 2S is a strong natural jump shift showing diamonds and spades, game forcing.',
)
