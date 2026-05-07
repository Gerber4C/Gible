Call(
    id='sp_1',
    when=Auction('1CP1HP2HP'),
    bid=Bid('2N'),
    selection=Selection(criteria=[Criterion('invitational_plus', condition=self.hcp >= 11)]),
    meaning=Meaning(nature=['artificial'], acts=['inquiry'], action='spiral_3344_query', target_suit=H, alertable=True),
    effects=[State('spiral_3344_query', owner='responder', target_suit=H, status='pending')],
    description='Responder asks whether opener raised hearts with three or four-card support and minimum or maximum values.',
)

Call(
    id='sp_2',
    when=Auction('1CP1SP2SP'),
    bid=Bid('2N'),
    selection=Selection(criteria=[Criterion('invitational_plus', condition=self.hcp >= 11)]),
    meaning=Meaning(nature=['artificial'], acts=['inquiry'], action='spiral_3344_query', target_suit=S, alertable=True),
    effects=[State('spiral_3344_query', owner='responder', target_suit=S, status='pending')],
)

Call(
    id='sp_3',
    when=Auction('1DP1HP2HP'),
    bid=Bid('2N'),
    selection=Selection(criteria=[Criterion('invitational_plus', condition=self.hcp >= 11)]),
    meaning=Meaning(nature=['artificial'], acts=['inquiry'], action='spiral_3344_query', target_suit=H, alertable=True),
    effects=[State('spiral_3344_query', owner='responder', target_suit=H, status='pending')],
)

Call(
    id='sp_4',
    when=Auction('1DP1SP2SP'),
    bid=Bid('2N'),
    selection=Selection(criteria=[Criterion('invitational_plus', condition=self.hcp >= 11)]),
    meaning=Meaning(nature=['artificial'], acts=['inquiry'], action='spiral_3344_query', target_suit=S, alertable=True),
    effects=[State('spiral_3344_query', owner='responder', target_suit=S, status='pending')],
)

Call(
    id='sp_5',
    when=Auction('1CP1HP2HP2NP'),
    bid=Bid('3C'),
    selection=Selection(criteria=[
        Criterion('minimum_values', condition=12 <= self.hcp <= 14),
        Criterion('three_hearts', condition=self.H == 3),
    ]),
    meaning=Meaning(nature=['artificial'], acts=['descriptive'], action='spiral_3344_answer', target_suit=H, support_length=3, opener_strength='minimum', alertable=True),
    effects=[State('spiral_3344_answer', owner='opener', target_suit=H, support_length=3, opener_strength='minimum')],
)

Call(
    id='sp_6',
    when=Auction('1CP1HP2HP2NP'),
    bid=Bid('3D'),
    selection=Selection(criteria=[
        Criterion('maximum_values', condition=self.hcp >= 15),
        Criterion('three_hearts', condition=self.H == 3),
    ]),
    meaning=Meaning(nature=['artificial'], acts=['descriptive'], action='spiral_3344_answer', target_suit=H, support_length=3, opener_strength='maximum', alertable=True),
    effects=[State('spiral_3344_answer', owner='opener', target_suit=H, support_length=3, opener_strength='maximum')],
)

Call(
    id='sp_7',
    when=Auction('1CP1HP2HP2NP'),
    bid=Bid('3H'),
    selection=Selection(criteria=[
        Criterion('minimum_values', condition=12 <= self.hcp <= 14),
        Criterion('four_hearts', condition=self.H >= 4),
    ]),
    meaning=Meaning(nature=['artificial'], acts=['descriptive'], action='spiral_3344_answer', target_suit=H, support_length=4, opener_strength='minimum', alertable=True),
    effects=[State('spiral_3344_answer', owner='opener', target_suit=H, support_length=4, opener_strength='minimum')],
)

Call(
    id='sp_8',
    when=Auction('1CP1HP2HP2NP'),
    bid=Bid('3S'),
    selection=Selection(criteria=[
        Criterion('maximum_values', condition=self.hcp >= 15),
        Criterion('four_hearts', condition=self.H >= 4),
    ]),
    meaning=Meaning(nature=['artificial'], acts=['descriptive'], action='spiral_3344_answer', target_suit=H, support_length=4, opener_strength='maximum', alertable=True),
    effects=[State('spiral_3344_answer', owner='opener', target_suit=H, support_length=4, opener_strength='maximum')],
)

Call(
    id='sp_9',
    when=Auction('1CP1SP2SP2NP'),
    bid=Bid('3C'),
    selection=Selection(criteria=[
        Criterion('minimum_values', condition=12 <= self.hcp <= 14),
        Criterion('three_spades', condition=self.S == 3),
    ]),
    meaning=Meaning(nature=['artificial'], acts=['descriptive'], action='spiral_3344_answer', target_suit=S, support_length=3, opener_strength='minimum', alertable=True),
    effects=[State('spiral_3344_answer', owner='opener', target_suit=S, support_length=3, opener_strength='minimum')],
)

Call(
    id='sp_10',
    when=Auction('1CP1SP2SP2NP'),
    bid=Bid('3D'),
    selection=Selection(criteria=[
        Criterion('maximum_values', condition=self.hcp >= 15),
        Criterion('three_spades', condition=self.S == 3),
    ]),
    meaning=Meaning(nature=['artificial'], acts=['descriptive'], action='spiral_3344_answer', target_suit=S, support_length=3, opener_strength='maximum', alertable=True),
    effects=[State('spiral_3344_answer', owner='opener', target_suit=S, support_length=3, opener_strength='maximum')],
)

Call(
    id='sp_11',
    when=Auction('1CP1SP2SP2NP'),
    bid=Bid('3H'),
    selection=Selection(criteria=[
        Criterion('minimum_values', condition=12 <= self.hcp <= 14),
        Criterion('four_spades', condition=self.S >= 4),
    ]),
    meaning=Meaning(nature=['artificial'], acts=['descriptive'], action='spiral_3344_answer', target_suit=S, support_length=4, opener_strength='minimum', alertable=True),
    effects=[State('spiral_3344_answer', owner='opener', target_suit=S, support_length=4, opener_strength='minimum')],
)

Call(
    id='sp_12',
    when=Auction('1CP1SP2SP2NP'),
    bid=Bid('3S'),
    selection=Selection(criteria=[
        Criterion('maximum_values', condition=self.hcp >= 15),
        Criterion('four_spades', condition=self.S >= 4),
    ]),
    meaning=Meaning(nature=['artificial'], acts=['descriptive'], action='spiral_3344_answer', target_suit=S, support_length=4, opener_strength='maximum', alertable=True),
    effects=[State('spiral_3344_answer', owner='opener', target_suit=S, support_length=4, opener_strength='maximum')],
)

Call(
    id='sp_13',
    when=Auction('1CP1HP2HP2NP3DP'),
    bid=Bid('4H'),
    selection=Selection(criteria=[
        Criterion('game_values', condition=self.hcp >= 13),
        Criterion('five_hearts', condition=self.H >= 5),
    ]),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='place_contract', target_suit=H, level=4, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=H, level=4, source='spiral_3344')],
)

Call(
    id='sp_14',
    when=Auction('1CP1SP2SP2NP3HP'),
    bid=Bid('4S'),
    selection=Selection(criteria=[
        Criterion('game_values', condition=self.hcp >= 13),
        Criterion('five_spades', condition=self.S >= 5),
    ]),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='place_contract', target_suit=S, level=4, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=S, level=4, source='spiral_3344')],
)

Call(
    id='sp_15',
    when=Auction('1DP1HP2HP2NP'),
    bid=Bid('3C'),
    selection=Selection(criteria=[Criterion('minimum_three_hearts', condition=12 <= self.hcp <= 14 and self.H == 3)]),
    meaning=Meaning(nature=['artificial'], acts=['descriptive'], action='spiral_3344_answer', target_suit=H, support_length=3, opener_strength='minimum', alertable=True),
    effects=[State('spiral_3344_answer', owner='opener', target_suit=H, support_length=3, opener_strength='minimum')],
)

Call(
    id='sp_16',
    when=Auction('1DP1HP2HP2NP'),
    bid=Bid('3D'),
    selection=Selection(criteria=[Criterion('maximum_three_hearts', condition=self.hcp >= 15 and self.H == 3)]),
    meaning=Meaning(nature=['artificial'], acts=['descriptive'], action='spiral_3344_answer', target_suit=H, support_length=3, opener_strength='maximum', alertable=True),
    effects=[State('spiral_3344_answer', owner='opener', target_suit=H, support_length=3, opener_strength='maximum')],
)

Call(
    id='sp_17',
    when=Auction('1DP1HP2HP2NP'),
    bid=Bid('3H'),
    selection=Selection(criteria=[Criterion('minimum_four_hearts', condition=12 <= self.hcp <= 14 and self.H >= 4)]),
    meaning=Meaning(nature=['artificial'], acts=['descriptive'], action='spiral_3344_answer', target_suit=H, support_length=4, opener_strength='minimum', alertable=True),
    effects=[State('spiral_3344_answer', owner='opener', target_suit=H, support_length=4, opener_strength='minimum')],
)

Call(
    id='sp_18',
    when=Auction('1DP1HP2HP2NP'),
    bid=Bid('3S'),
    selection=Selection(criteria=[Criterion('maximum_four_hearts', condition=self.hcp >= 15 and self.H >= 4)]),
    meaning=Meaning(nature=['artificial'], acts=['descriptive'], action='spiral_3344_answer', target_suit=H, support_length=4, opener_strength='maximum', alertable=True),
    effects=[State('spiral_3344_answer', owner='opener', target_suit=H, support_length=4, opener_strength='maximum')],
)

Call(
    id='sp_19',
    when=Auction('1DP1SP2SP2NP'),
    bid=Bid('3C'),
    selection=Selection(criteria=[Criterion('minimum_three_spades', condition=12 <= self.hcp <= 14 and self.S == 3)]),
    meaning=Meaning(nature=['artificial'], acts=['descriptive'], action='spiral_3344_answer', target_suit=S, support_length=3, opener_strength='minimum', alertable=True),
    effects=[State('spiral_3344_answer', owner='opener', target_suit=S, support_length=3, opener_strength='minimum')],
)

Call(
    id='sp_20',
    when=Auction('1DP1SP2SP2NP'),
    bid=Bid('3D'),
    selection=Selection(criteria=[Criterion('maximum_three_spades', condition=self.hcp >= 15 and self.S == 3)]),
    meaning=Meaning(nature=['artificial'], acts=['descriptive'], action='spiral_3344_answer', target_suit=S, support_length=3, opener_strength='maximum', alertable=True),
    effects=[State('spiral_3344_answer', owner='opener', target_suit=S, support_length=3, opener_strength='maximum')],
)

Call(
    id='sp_21',
    when=Auction('1DP1SP2SP2NP'),
    bid=Bid('3H'),
    selection=Selection(criteria=[Criterion('minimum_four_spades', condition=12 <= self.hcp <= 14 and self.S >= 4)]),
    meaning=Meaning(nature=['artificial'], acts=['descriptive'], action='spiral_3344_answer', target_suit=S, support_length=4, opener_strength='minimum', alertable=True),
    effects=[State('spiral_3344_answer', owner='opener', target_suit=S, support_length=4, opener_strength='minimum')],
)

Call(
    id='sp_22',
    when=Auction('1DP1SP2SP2NP'),
    bid=Bid('3S'),
    selection=Selection(criteria=[Criterion('maximum_four_spades', condition=self.hcp >= 15 and self.S >= 4)]),
    meaning=Meaning(nature=['artificial'], acts=['descriptive'], action='spiral_3344_answer', target_suit=S, support_length=4, opener_strength='maximum', alertable=True),
    effects=[State('spiral_3344_answer', owner='opener', target_suit=S, support_length=4, opener_strength='maximum')],
)
