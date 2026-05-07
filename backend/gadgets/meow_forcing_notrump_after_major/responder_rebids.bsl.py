Call(
    id='fn_19',
    when=Auction('1SP1NP2CP'),
    bid=Bid('P'),
    selection=Selection(criteria=[
        Criterion('weak_club_preference', condition=self.C >= 4),
        Criterion('minimum_response', condition=self.hcp <= 10),
    ]),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='pass_final_contract', target_suit=C, level=2, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=C, level=2, source='forcing_notrump')],
)

Call(
    id='fn_20',
    when=Auction('1SP1NP2DP'),
    bid=Bid('P'),
    selection=Selection(criteria=[
        Criterion('weak_diamond_preference', condition=self.D >= 4),
        Criterion('minimum_response', condition=self.hcp <= 10),
    ]),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='pass_final_contract', target_suit=D, level=2, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=D, level=2, source='forcing_notrump')],
)

Call(
    id='fn_21',
    when=Auction('1HP1NP2CP'),
    bid=Bid('P'),
    selection=Selection(criteria=[
        Criterion('weak_club_preference', condition=self.C >= 4),
        Criterion('minimum_response', condition=self.hcp <= 10),
    ]),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='pass_final_contract', target_suit=C, level=2, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=C, level=2, source='forcing_notrump')],
)

Call(
    id='fn_22',
    when=Auction('1HP1NP2DP'),
    bid=Bid('P'),
    selection=Selection(criteria=[
        Criterion('weak_diamond_preference', condition=self.D >= 4),
        Criterion('minimum_response', condition=self.hcp <= 10),
    ]),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='pass_final_contract', target_suit=D, level=2, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=D, level=2, source='forcing_notrump')],
)

Call(
    id='fn_23',
    when=Auction('1SP1NP2CP'),
    bid=Bid('2S'),
    selection=Selection(criteria=[
        Criterion('two_spade_preference', condition=self.S >= 2),
        Criterion('minimum_response', condition=self.hcp <= 10),
    ]),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='major_preference', target_suit=S, level=2, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=S, level=2, source='forcing_notrump')],
)

Call(
    id='fn_24',
    when=Auction('1SP1NP2DP'),
    bid=Bid('2S'),
    selection=Selection(criteria=[
        Criterion('two_spade_preference', condition=self.S >= 2),
        Criterion('minimum_response', condition=self.hcp <= 10),
    ]),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='major_preference', target_suit=S, level=2, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=S, level=2, source='forcing_notrump')],
)

Call(
    id='fn_25',
    when=Auction('1HP1NP2CP'),
    bid=Bid('2H'),
    selection=Selection(criteria=[
        Criterion('two_heart_preference', condition=self.H >= 2),
        Criterion('minimum_response', condition=self.hcp <= 10),
    ]),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='major_preference', target_suit=H, level=2, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=H, level=2, source='forcing_notrump')],
)

Call(
    id='fn_26',
    when=Auction('1HP1NP2DP'),
    bid=Bid('2H'),
    selection=Selection(criteria=[
        Criterion('two_heart_preference', condition=self.H >= 2),
        Criterion('minimum_response', condition=self.hcp <= 10),
    ]),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='major_preference', target_suit=H, level=2, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=H, level=2, source='forcing_notrump')],
)

Call(
    id='fn_27',
    when=Auction('1SP1NP2CP'),
    bid=Bid('2N'),
    selection=Selection(criteria=[Criterion('balanced_invite', condition=11 <= self.hcp <= 12)]),
    meaning=Meaning(nature=['natural'], acts=['invitational'], action='notrump_invite', target_suit=N, hcp_range=[11, 12], alertable=False),
    effects=[State('notrump_contract_interest', owner='partnership', level=2, source='forcing_notrump')],
)

Call(
    id='fn_28',
    when=Auction('1SP1NP2DP'),
    bid=Bid('2N'),
    selection=Selection(criteria=[Criterion('balanced_invite', condition=11 <= self.hcp <= 12)]),
    meaning=Meaning(nature=['natural'], acts=['invitational'], action='notrump_invite', target_suit=N, hcp_range=[11, 12], alertable=False),
    effects=[State('notrump_contract_interest', owner='partnership', level=2, source='forcing_notrump')],
)

Call(
    id='fn_29',
    when=Auction('1SP1NP2SP'),
    bid=Bid('P'),
    selection=Selection(criteria=[Criterion('minimum_response', condition=self.hcp <= 10, weight=80)]),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='pass_final_contract', target_suit=S, level=2, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=S, level=2, source='forcing_notrump')],
)

Call(
    id='fn_30',
    when=Auction('1HP1NP2HP'),
    bid=Bid('P'),
    selection=Selection(criteria=[Criterion('minimum_response', condition=self.hcp <= 10, weight=80)]),
    meaning=Meaning(nature=['natural'], acts=['final_placement'], action='pass_final_contract', target_suit=H, level=2, alertable=False),
    effects=[State('final_contract', owner='partnership', target_suit=H, level=2, source='forcing_notrump')],
)
