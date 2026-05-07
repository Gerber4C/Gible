# BSL source for Partner bidding agreements.
# Natural responder rebids after a one-minor opening and opener's first rebid.

Call(
    id='cs_55',
    when=Auction('1CP1HP1SP', seats=[1, 2, 3, 4]),
    bid=Bid('2H'),
    selection=Selection(criteria=[
        Criterion('six_hearts', condition=self.H >= 6),
        Criterion('signoff_values', condition=self.hcp <= 10),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'signoff'], action='responder_major_rebid', target_suit=H, shown_length_min=6, alertable=False),
    effects=[
        State('responder.length.H', owner='responder', min_value=6, source='responder_major_rebid'),
        State('responder.hcp', owner='responder', max_value=10, source='responder_major_rebid'),
    ],
    description='Responder rebids 2H after 1C-1H-1S with long hearts and signoff values.',
    system_notes='After 1C-1H-1S, 2H is natural and non-forcing, usually six or more hearts.',
)

Call(
    id='cs_56',
    when=Auction('1CP1HP1NP', seats=[1, 2, 3, 4]),
    bid=Bid('2H'),
    selection=Selection(criteria=[
        Criterion('six_hearts', condition=self.H >= 6),
        Criterion('signoff_values', condition=self.hcp <= 10),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'signoff'], action='responder_major_rebid', target_suit=H, shown_length_min=6, alertable=False),
    effects=[
        State('responder.length.H', owner='responder', min_value=6, source='responder_major_rebid'),
        State('responder.hcp', owner='responder', max_value=10, source='responder_major_rebid'),
    ],
    description='Responder rebids 2H after 1C-1H-1N with long hearts and signoff values.',
    system_notes='After 1C-1H-1N, 2H is natural and non-forcing, usually six or more hearts.',
)

Call(
    id='cs_57',
    when=Auction('1DP1HP1SP', seats=[1, 2, 3, 4]),
    bid=Bid('2H'),
    selection=Selection(criteria=[
        Criterion('six_hearts', condition=self.H >= 6),
        Criterion('signoff_values', condition=self.hcp <= 10),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'signoff'], action='responder_major_rebid', target_suit=H, shown_length_min=6, alertable=False),
    effects=[
        State('responder.length.H', owner='responder', min_value=6, source='responder_major_rebid'),
        State('responder.hcp', owner='responder', max_value=10, source='responder_major_rebid'),
    ],
    description='Responder rebids 2H after 1D-1H-1S with long hearts and signoff values.',
    system_notes='After 1D-1H-1S, 2H is natural and non-forcing, usually six or more hearts.',
)

Call(
    id='cs_58',
    when=Auction('1DP1HP1NP', seats=[1, 2, 3, 4]),
    bid=Bid('2H'),
    selection=Selection(criteria=[
        Criterion('six_hearts', condition=self.H >= 6),
        Criterion('signoff_values', condition=self.hcp <= 10),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'signoff'], action='responder_major_rebid', target_suit=H, shown_length_min=6, alertable=False),
    effects=[
        State('responder.length.H', owner='responder', min_value=6, source='responder_major_rebid'),
        State('responder.hcp', owner='responder', max_value=10, source='responder_major_rebid'),
    ],
    description='Responder rebids 2H after 1D-1H-1N with long hearts and signoff values.',
    system_notes='After 1D-1H-1N, 2H is natural and non-forcing, usually six or more hearts.',
)

Call(
    id='cs_59',
    when=Auction('1CP1SP1NP', seats=[1, 2, 3, 4]),
    bid=Bid('2S'),
    selection=Selection(criteria=[
        Criterion('six_spades', condition=self.S >= 6),
        Criterion('signoff_values', condition=self.hcp <= 10),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'signoff'], action='responder_major_rebid', target_suit=S, shown_length_min=6, alertable=False),
    effects=[
        State('responder.length.S', owner='responder', min_value=6, source='responder_major_rebid'),
        State('responder.hcp', owner='responder', max_value=10, source='responder_major_rebid'),
    ],
    description='Responder rebids 2S after 1C-1S-1N with long spades and signoff values.',
    system_notes='After 1C-1S-1N, 2S is natural and non-forcing, usually six or more spades.',
)

Call(
    id='cs_60',
    when=Auction('1DP1SP1NP', seats=[1, 2, 3, 4]),
    bid=Bid('2S'),
    selection=Selection(criteria=[
        Criterion('six_spades', condition=self.S >= 6),
        Criterion('signoff_values', condition=self.hcp <= 10),
    ]),
    meaning=Meaning(nature=['natural'], acts=['descriptive', 'signoff'], action='responder_major_rebid', target_suit=S, shown_length_min=6, alertable=False),
    effects=[
        State('responder.length.S', owner='responder', min_value=6, source='responder_major_rebid'),
        State('responder.hcp', owner='responder', max_value=10, source='responder_major_rebid'),
    ],
    description='Responder rebids 2S after 1D-1S-1N with long spades and signoff values.',
    system_notes='After 1D-1S-1N, 2S is natural and non-forcing, usually six or more spades.',
)
