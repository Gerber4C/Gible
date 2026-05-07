Call(
    id='ntb_1',
    when=Auction('1NP', seats=[1, 2, 3, 4]),
    bid=Bid('P'),
    requires=StateExists('notrump_focus', status='active'),
    selection=Selection(criteria=[Criterion('non_invitational_values', condition=self.hcp <= 8)]),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='pass_notrump', level=1, target_suit=N, alertable=False),
    effects=[State('final_contract', owner='partnership', level=1, target_suit=N, source='notrump_response_basics')],
    description='Responder passes 1N with weak or non-invitational values when no preferred escape or constructive route is chosen.',
    system_notes='Responder may pass 1N with weak or non-invitational values.',
)

Call(
    id='ntb_2',
    when=Auction('1NP', seats=[1, 2, 3, 4]),
    bid=Bid('3N'),
    requires=StateExists('notrump_focus', status='active'),
    selection=Selection(
        criteria=[
            Criterion('game_values', condition=10 <= self.hcp <= 15),
            Criterion('no_four_card_major', condition=self.spades <= 3 and self.hearts <= 3),
            Criterion('no_long_minor', condition=self.diamonds <= 4 and self.clubs <= 4),
        ],
    ),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='place_contract', level=3, target_suit=N, alertable=False),
    effects=[State('final_contract', owner='partnership', level=3, target_suit=N, source='direct_notrump_game')],
    description='Responder bids 3N directly over 1N with game values and no major-suit inquiry need.',
    system_notes='After 1N, 3N is natural to play.',
)

Call(
    id='ntb_3',
    when=Auction('1NP', seats=[1, 2, 3, 4]),
    bid=Bid('3D'),
    requires=StateExists('notrump_focus', status='active'),
    selection=Selection(
        criteria=[
            Criterion('five_five_minors', condition=self.diamonds >= 5 and self.clubs >= 5),
            Criterion('game_forcing_values', condition=self.hcp >= 10),
        ],
    ),
    meaning=Meaning(
        nature=['artificial', 'conventional'],
        acts=['descriptive', 'forcing'],
        action='five_five_minors_game_force',
        shape='5-5 minors',
        alertable=True,
    ),
    effects=[
        State('responder.shape', owner='responder', value='5-5 minors', source='direct_1n_response'),
        State('forcing_status', owner='partnership', status='game_forcing', source='direct_1n_response'),
    ],
    description='Responder shows both minors, at least 5-5, game forcing.',
    system_notes='After 1N, 3D shows 5-5 minors and game-forcing values.',
)

Call(
    id='ntb_4',
    when=Auction('1NP', seats=[1, 2, 3, 4]),
    bid=Bid('3H'),
    requires=StateExists('notrump_focus', status='active'),
    selection=Selection(
        criteria=[
            Criterion('five_five_majors', condition=self.spades >= 5 and self.hearts >= 5),
            Criterion('invitational_values', condition=8 <= self.hcp <= 9),
        ],
    ),
    meaning=Meaning(
        nature=['artificial', 'conventional'],
        acts=['descriptive', 'invitation'],
        action='five_five_majors_invitational',
        shape='5-5 majors',
        alertable=True,
    ),
    effects=[
        State('responder.shape', owner='responder', value='5-5 majors', source='direct_1n_response'),
        State('game_interest', owner='partnership', value='invite', source='direct_1n_response'),
    ],
    description='Responder shows both majors, at least 5-5, invitational.',
    system_notes='After 1N, 3H shows 5-5 majors and invitational values.',
)

Call(
    id='ntb_5',
    when=Auction('1NP', seats=[1, 2, 3, 4]),
    bid=Bid('3S'),
    requires=StateExists('notrump_focus', status='active'),
    selection=Selection(
        criteria=[
            Criterion('five_five_majors', condition=self.spades >= 5 and self.hearts >= 5),
            Criterion('game_forcing_values', condition=self.hcp >= 10),
        ],
    ),
    meaning=Meaning(
        nature=['artificial', 'conventional'],
        acts=['descriptive', 'forcing'],
        action='five_five_majors_game_force',
        shape='5-5 majors',
        alertable=True,
    ),
    effects=[
        State('responder.shape', owner='responder', value='5-5 majors', source='direct_1n_response'),
        State('forcing_status', owner='partnership', status='game_forcing', source='direct_1n_response'),
    ],
    description='Responder shows both majors, at least 5-5, game forcing.',
    system_notes='After 1N, 3S shows 5-5 majors and game-forcing values.',
)
