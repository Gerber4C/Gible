Call(
    id='im_17',
    when=Auction('1CP2CP'),
    bid=Bid('3N'),
    selection={
        'algorithm': 'weighted_score',
        'criteria': [
            {'criterion_id': 'extra_balanced_values', 'evaluator': 'min_value', 'input': 'self.hcp', 'min': 15, 'weight': 80},
            {'criterion_id': 'balanced', 'evaluator': 'equals', 'input': 'self.balanced', 'value': True, 'weight': 40},
            {'criterion_id': 'diamond_stopper', 'evaluator': 'named_evaluator', 'evaluator_id': 'eval_stopper', 'params': {'target_suit': 'D'}, 'weight': 40},
            {'criterion_id': 'heart_stopper', 'evaluator': 'named_evaluator', 'evaluator_id': 'eval_stopper', 'params': {'target_suit': 'H'}, 'weight': 40},
            {'criterion_id': 'spade_stopper', 'evaluator': 'named_evaluator', 'evaluator_id': 'eval_stopper', 'params': {'target_suit': 'S'}, 'weight': 40},
        ],
    },
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='place_contract', target_suit=N, level=3, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=N, level=3, source='inverted_minor')],
    description='Opener places 3N after an inverted club raise with extra balanced values and side stoppers.',
)

Call(
    id='im_18',
    when=Auction('1DP2DP'),
    bid=Bid('3N'),
    selection={
        'algorithm': 'weighted_score',
        'criteria': [
            {'criterion_id': 'extra_balanced_values', 'evaluator': 'min_value', 'input': 'self.hcp', 'min': 15, 'weight': 80},
            {'criterion_id': 'balanced', 'evaluator': 'equals', 'input': 'self.balanced', 'value': True, 'weight': 40},
            {'criterion_id': 'club_stopper', 'evaluator': 'named_evaluator', 'evaluator_id': 'eval_stopper', 'params': {'target_suit': 'C'}, 'weight': 40},
            {'criterion_id': 'heart_stopper', 'evaluator': 'named_evaluator', 'evaluator_id': 'eval_stopper', 'params': {'target_suit': 'H'}, 'weight': 40},
            {'criterion_id': 'spade_stopper', 'evaluator': 'named_evaluator', 'evaluator_id': 'eval_stopper', 'params': {'target_suit': 'S'}, 'weight': 40},
        ],
    },
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='place_contract', target_suit=N, level=3, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=N, level=3, source='inverted_minor')],
    description='Opener places 3N after an inverted diamond raise with extra balanced values and side stoppers.',
)

Call(
    id='im_19',
    when=Auction('1CP2CP2DP'),
    bid=Bid('2N'),
    selection=Selection(criteria=[Criterion('invitational_notrump', condition=10 <= self.hcp <= 12 and self.balanced == True, weight=90)]),
    meaning=Meaning(nature=['natural'], acts=['invitational'], action='notrump_invite', target_suit=N, level=2, alertable=False),
    effects=[State('notrump_contract_interest', owner='partnership', level=2, source='inverted_minor')],
)

Call(
    id='im_20',
    when=Auction('1CP2CP2HP'),
    bid=Bid('2N'),
    selection=Selection(criteria=[Criterion('invitational_notrump', condition=10 <= self.hcp <= 12 and self.balanced == True, weight=90)]),
    meaning=Meaning(nature=['natural'], acts=['invitational'], action='notrump_invite', target_suit=N, level=2, alertable=False),
    effects=[State('notrump_contract_interest', owner='partnership', level=2, source='inverted_minor')],
)

Call(
    id='im_21',
    when=Auction('1CP2CP2SP'),
    bid=Bid('2N'),
    selection=Selection(criteria=[Criterion('invitational_notrump', condition=10 <= self.hcp <= 12 and self.balanced == True, weight=90)]),
    meaning=Meaning(nature=['natural'], acts=['invitational'], action='notrump_invite', target_suit=N, level=2, alertable=False),
    effects=[State('notrump_contract_interest', owner='partnership', level=2, source='inverted_minor')],
)

Call(
    id='im_22',
    when=Auction('1CP2CP2DP'),
    bid=Bid('3N'),
    selection=Selection(criteria=[Criterion('game_notrump', condition=self.hcp >= 13 and self.balanced == True, weight=110)]),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='place_contract', target_suit=N, level=3, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=N, level=3, source='inverted_minor')],
)

Call(
    id='im_23',
    when=Auction('1CP2CP2HP'),
    bid=Bid('3N'),
    selection=Selection(criteria=[Criterion('game_notrump', condition=self.hcp >= 13 and self.balanced == True, weight=110)]),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='place_contract', target_suit=N, level=3, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=N, level=3, source='inverted_minor')],
)

Call(
    id='im_24',
    when=Auction('1CP2CP2SP'),
    bid=Bid('3N'),
    selection=Selection(criteria=[Criterion('game_notrump', condition=self.hcp >= 13 and self.balanced == True, weight=110)]),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='place_contract', target_suit=N, level=3, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=N, level=3, source='inverted_minor')],
)

Call(
    id='im_25',
    when=Auction('1CP2CP2DP'),
    bid=Bid('3C'),
    selection=Selection(criteria=[Criterion('minor_fallback_invite', condition=10 <= self.hcp <= 12 and self.C >= 5, weight=80)]),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='minor_fallback', target_suit=C, level=3, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=C, level=3, source='inverted_minor')],
)

Call(
    id='im_26',
    when=Auction('1DP2DP2HP'),
    bid=Bid('2N'),
    selection=Selection(criteria=[Criterion('invitational_notrump', condition=10 <= self.hcp <= 12 and self.balanced == True, weight=90)]),
    meaning=Meaning(nature=['natural'], acts=['invitational'], action='notrump_invite', target_suit=N, level=2, alertable=False),
    effects=[State('notrump_contract_interest', owner='partnership', level=2, source='inverted_minor')],
)

Call(
    id='im_27',
    when=Auction('1DP2DP2SP'),
    bid=Bid('2N'),
    selection=Selection(criteria=[Criterion('invitational_notrump', condition=10 <= self.hcp <= 12 and self.balanced == True, weight=90)]),
    meaning=Meaning(nature=['natural'], acts=['invitational'], action='notrump_invite', target_suit=N, level=2, alertable=False),
    effects=[State('notrump_contract_interest', owner='partnership', level=2, source='inverted_minor')],
)

Call(
    id='im_28',
    when=Auction('1DP2DP3CP'),
    bid=Bid('3D'),
    selection=Selection(criteria=[Criterion('minor_fallback_invite', condition=10 <= self.hcp <= 12 and self.D >= 4, weight=80)]),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='minor_fallback', target_suit=D, level=3, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=D, level=3, source='inverted_minor')],
)

Call(
    id='im_29',
    when=Auction('1DP2DP2HP'),
    bid=Bid('3N'),
    selection=Selection(criteria=[Criterion('game_notrump', condition=self.hcp >= 13 and self.balanced == True, weight=110)]),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='place_contract', target_suit=N, level=3, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=N, level=3, source='inverted_minor')],
)

Call(
    id='im_30',
    when=Auction('1DP2DP2SP'),
    bid=Bid('3N'),
    selection=Selection(criteria=[Criterion('game_notrump', condition=self.hcp >= 13 and self.balanced == True, weight=110)]),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='place_contract', target_suit=N, level=3, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=N, level=3, source='inverted_minor')],
)
