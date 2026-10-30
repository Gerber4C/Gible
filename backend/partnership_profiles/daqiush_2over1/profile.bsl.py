class Daqiush2over1Profile(Profile):
    id = 'daqiush_2over1'
    name = 'Daqiush 2/1 — 1NT practice slice'
    version = '0.1.0'
    author = Author('Daqiush')
    gadgets = ['one_notrump_opening', 'south_african_texas', 'jacoby_major_transfers', 'jacoby_splinter', 'one_notrump_invitations', 'five_card_major_inquiry', 'minor_two_suit_game', 'minor_shortage_invitation', 'confirmed_trump_prefixes', 'confirmed_keycard', 'voidwood']
    missing_call_behavior = 'block'
    derived_semantics = True
    description = 'Confirmed 1NT opening, bounded invitation and Texas routes; Jacoby splinter meanings and opener replies can be replayed. Other routes remain incomplete.'
    system_notes = 'Normally 15–17 HCP; qualifying 14-HCP 5332 upgrades and very soft 18-HCP 4432 with QJ doubleton. Includes specified semibalanced and honor-singleton shapes. Weak responses to 1NT without a transfer or club-shortage garbage Stayman pass; other unsupported decisions remain blocked.'
