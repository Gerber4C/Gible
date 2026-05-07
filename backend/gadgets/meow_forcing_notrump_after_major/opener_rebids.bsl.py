Call(
    id='fn_9',
    when=Auction('1HP1NP'),
    bid=Bid('2C'),
    selection=Selection(criteria=[Criterion('three_clubs', condition=self.C >= 3)]),
    meaning=Meaning(nature=['natural'], acts=['descriptive'], action='forcing_notrump_opener_rebid', target_suit=C, shown_length_min=3, alertable=False),
    effects=[State('opener.length.C', owner='opener', min_value=3, source='forcing_notrump_rebid')],
)

Call(
    id='fn_10',
    when=Auction('1HP1NP'),
    bid=Bid('2D'),
    selection=Selection(criteria=[Criterion('three_diamonds', condition=self.D >= 3)]),
    meaning=Meaning(nature=['natural'], acts=['descriptive'], action='forcing_notrump_opener_rebid', target_suit=D, shown_length_min=3, alertable=False),
    effects=[State('opener.length.D', owner='opener', min_value=3, source='forcing_notrump_rebid')],
)

Call(
    id='fn_11',
    when=Auction('1HP1NP'),
    bid=Bid('2H'),
    selection=Selection(criteria=[Criterion('six_hearts', condition=self.H >= 6)]),
    meaning=Meaning(nature=['natural'], acts=['descriptive'], action='forcing_notrump_opener_rebid', target_suit=H, shown_length_min=6, alertable=False),
    effects=[State('opener.length.H', owner='opener', min_value=6, source='forcing_notrump_rebid')],
)

Call(
    id='fn_12',
    when=Auction('1HP1NP'),
    bid=Bid('2S'),
    selection=Selection(criteria=[
        Criterion('reverse_values', condition=self.hcp >= 16),
        Criterion('four_spades', condition=self.S >= 4),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'forcing'], action='forcing_notrump_reverse', target_suit=S, shown_length_min=4, alertable=False),
    effects=[State('opener.length.S', owner='opener', min_value=4, source='forcing_notrump_reverse')],
)

Call(
    id='fn_13',
    when=Auction('1HP1NP'),
    bid=Bid('2N'),
    selection=Selection(criteria=[
        Criterion('eighteen_nineteen', condition=18 <= self.hcp <= 19),
        Criterion('balanced', condition=self.balanced == True),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'invitational'], action='forcing_notrump_opener_notrump_rebid', target_suit=N, hcp_range=[18, 19], alertable=False),
    effects=[
        State('opener.hcp', owner='opener', min_value=18, max_value=19, source='forcing_notrump_2n'),
        State('opener.shape', owner='opener', value='balanced', source='forcing_notrump_2n'),
    ],
)

Call(
    id='fn_14',
    when=Auction('1SP1NP'),
    bid=Bid('2C'),
    selection=Selection(criteria=[Criterion('three_clubs', condition=self.C >= 3)]),
    meaning=Meaning(nature=['natural'], acts=['descriptive'], action='forcing_notrump_opener_rebid', target_suit=C, shown_length_min=3, alertable=False),
    effects=[State('opener.length.C', owner='opener', min_value=3, source='forcing_notrump_rebid')],
)

Call(
    id='fn_15',
    when=Auction('1SP1NP'),
    bid=Bid('2D'),
    selection=Selection(criteria=[Criterion('three_diamonds', condition=self.D >= 3)]),
    meaning=Meaning(nature=['natural'], acts=['descriptive'], action='forcing_notrump_opener_rebid', target_suit=D, shown_length_min=3, alertable=False),
    effects=[State('opener.length.D', owner='opener', min_value=3, source='forcing_notrump_rebid')],
)

Call(
    id='fn_16',
    when=Auction('1SP1NP'),
    bid=Bid('2H'),
    selection=Selection(criteria=[Criterion('four_hearts', condition=self.H >= 4)]),
    meaning=Meaning(nature=['natural'], acts=['descriptive'], action='forcing_notrump_opener_rebid', target_suit=H, shown_length_min=4, alertable=False),
    effects=[State('opener.length.H', owner='opener', min_value=4, source='forcing_notrump_rebid')],
)

Call(
    id='fn_17',
    when=Auction('1SP1NP'),
    bid=Bid('2S'),
    selection=Selection(criteria=[Criterion('six_spades', condition=self.S >= 6)]),
    meaning=Meaning(nature=['natural'], acts=['descriptive'], action='forcing_notrump_opener_rebid', target_suit=S, shown_length_min=6, alertable=False),
    effects=[State('opener.length.S', owner='opener', min_value=6, source='forcing_notrump_rebid')],
)

Call(
    id='fn_18',
    when=Auction('1SP1NP'),
    bid=Bid('2N'),
    selection=Selection(criteria=[
        Criterion('eighteen_nineteen', condition=18 <= self.hcp <= 19),
        Criterion('balanced', condition=self.balanced == True),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'invitational'], action='forcing_notrump_opener_notrump_rebid', target_suit=N, hcp_range=[18, 19], alertable=False),
    effects=[
        State('opener.hcp', owner='opener', min_value=18, max_value=19, source='forcing_notrump_2n'),
        State('opener.shape', owner='opener', value='balanced', source='forcing_notrump_2n'),
    ],
)
