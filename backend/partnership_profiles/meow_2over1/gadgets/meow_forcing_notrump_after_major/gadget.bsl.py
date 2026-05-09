# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def fn_9_applies(ctx):
    return (ctx.hand.length('C') >= 3)
def fn_10_applies(ctx):
    return (ctx.hand.length('D') >= 3)
def fn_11_applies(ctx):
    return (ctx.hand.length('H') >= 6)
def fn_12_applies(ctx):
    return (ctx.hand.hcp >= 16 and ctx.hand.length('S') >= 4)
def fn_13_applies(ctx):
    return (18 <= ctx.hand.hcp <= 19 and ctx.hand.balanced == True)
def fn_14_applies(ctx):
    return (ctx.hand.length('C') >= 3)
def fn_15_applies(ctx):
    return (ctx.hand.length('D') >= 3)
def fn_16_applies(ctx):
    return (ctx.hand.length('H') >= 4)
def fn_17_applies(ctx):
    return (ctx.hand.length('S') >= 6)
def fn_18_applies(ctx):
    return (18 <= ctx.hand.hcp <= 19 and ctx.hand.balanced == True)
def fn_19_applies(ctx):
    return (ctx.hand.length('C') >= 4 and ctx.hand.hcp <= 10)
def fn_20_applies(ctx):
    return (ctx.hand.length('D') >= 4 and ctx.hand.hcp <= 10)
def fn_21_applies(ctx):
    return (ctx.hand.length('C') >= 4 and ctx.hand.hcp <= 10)
def fn_22_applies(ctx):
    return (ctx.hand.length('D') >= 4 and ctx.hand.hcp <= 10)
def fn_23_applies(ctx):
    return (ctx.hand.length('S') >= 2 and ctx.hand.hcp <= 10)
def fn_24_applies(ctx):
    return (ctx.hand.length('S') >= 2 and ctx.hand.hcp <= 10)
def fn_25_applies(ctx):
    return (ctx.hand.length('H') >= 2 and ctx.hand.hcp <= 10)
def fn_26_applies(ctx):
    return (ctx.hand.length('H') >= 2 and ctx.hand.hcp <= 10)
def fn_27_applies(ctx):
    return (11 <= ctx.hand.hcp <= 12)
def fn_28_applies(ctx):
    return (11 <= ctx.hand.hcp <= 12)
def fn_29_applies(ctx):
    return (ctx.hand.hcp <= 10)
def fn_30_applies(ctx):
    return (ctx.hand.hcp <= 10)
def fn_31_applies(ctx):
    return (ctx.hand.hcp <= 13)
def fn_32_applies(ctx):
    return (ctx.hand.hcp >= 14)
def fn_33_applies(ctx):
    return (ctx.hand.hcp <= 13)
def fn_34_applies(ctx):
    return (ctx.hand.hcp >= 14)
def fn_35_applies(ctx):
    return (ctx.hand.hcp <= 13)
def fn_36_applies(ctx):
    return (ctx.hand.hcp >= 14)
def fn_37_applies(ctx):
    return (ctx.hand.hcp <= 13)
def fn_38_applies(ctx):
    return (ctx.hand.hcp >= 14)
def fn_1_applies(ctx):
    return (ctx.hand.hcp >= 6 and ctx.hand.length('S') >= 4)
def fn_2_applies(ctx):
    return (6 <= ctx.hand.hcp <= 12 and ctx.hand.length('H') <= 2 and ctx.hand.length('S') <= 3)
def fn_3_applies(ctx):
    return (6 <= ctx.hand.hcp <= 12 and ctx.hand.length('S') <= 2)
def fn_4_applies(ctx):
    return (ctx.hand.hcp >= 12 and ctx.hand.length('C') >= 4 and ctx.hand.length('S') <= 3 and ctx.hand.length('H') <= 2)
def fn_5_applies(ctx):
    return (ctx.hand.hcp >= 12 and ctx.hand.length('D') >= 4 and ctx.hand.length('S') <= 3 and ctx.hand.length('H') <= 2)
def fn_6_applies(ctx):
    return (ctx.hand.hcp >= 12 and ctx.hand.length('C') >= 4 and ctx.hand.length('S') <= 2)
def fn_7_applies(ctx):
    return (ctx.hand.hcp >= 12 and ctx.hand.length('D') >= 4 and ctx.hand.length('S') <= 2)
def fn_8_applies(ctx):
    return (ctx.hand.hcp >= 12 and ctx.hand.length('H') >= 5 and ctx.hand.length('S') <= 2)

class MeowForcingNotrumpAfterMajorGadget(Gadget):
    id = 'meow_forcing_notrump_after_major'
    namespace = 'meow_2over1'
    name = 'Meow Forcing Notrump After Major'
    version = '0.1.0'
    description = 'Forcing 1N structure after an uncontested 1H or 1S opening: responder uses 1N as a one-round force, opener rebids naturally, and responder can sign off, invite, or place game.'
    system_notes = 'After 1M-P, 1N is forcing for one round by an unpassed hand, normally 6-12 HCP without a direct raise. Opener rebids a six-card major, a side suit, the longer minor, or 2N with 18-19 balanced.'
    author = Author('Meow Li')

    def build(self):

        call = self.call('fn_9')
        call.when = '1HP1NP'
        call.bid = '2C'
        call.applies = fn_9_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'forcing_notrump_opener_rebid'
        call.meaning.target_suit = 'C'
        call.meaning.shown_length_min = 3
        effect = call.effect('opener.length.C', owner='opener')
        effect.min_value = 3
        effect.source = 'forcing_notrump_rebid'

        call = self.call('fn_10')
        call.when = '1HP1NP'
        call.bid = '2D'
        call.applies = fn_10_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'forcing_notrump_opener_rebid'
        call.meaning.target_suit = 'D'
        call.meaning.shown_length_min = 3
        effect = call.effect('opener.length.D', owner='opener')
        effect.min_value = 3
        effect.source = 'forcing_notrump_rebid'

        call = self.call('fn_11')
        call.when = '1HP1NP'
        call.bid = '2H'
        call.applies = fn_11_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'forcing_notrump_opener_rebid'
        call.meaning.target_suit = 'H'
        call.meaning.shown_length_min = 6
        effect = call.effect('opener.length.H', owner='opener')
        effect.min_value = 6
        effect.source = 'forcing_notrump_rebid'

        call = self.call('fn_12')
        call.when = '1HP1NP'
        call.bid = '2S'
        call.applies = fn_12_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'forcing_notrump_reverse'
        call.meaning.target_suit = 'S'
        call.meaning.shown_length_min = 4
        effect = call.effect('opener.length.S', owner='opener')
        effect.min_value = 4
        effect.source = 'forcing_notrump_reverse'

        call = self.call('fn_13')
        call.when = '1HP1NP'
        call.bid = '2N'
        call.applies = fn_13_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'invitational']
        call.meaning.action = 'forcing_notrump_opener_notrump_rebid'
        call.meaning.target_suit = 'N'
        call.meaning.hcp_range = [18, 19]
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 18
        effect.max_value = 19
        effect.source = 'forcing_notrump_2n'
        effect = call.effect('opener.shape', owner='opener')
        effect.value = 'balanced'
        effect.source = 'forcing_notrump_2n'

        call = self.call('fn_14')
        call.when = '1SP1NP'
        call.bid = '2C'
        call.applies = fn_14_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'forcing_notrump_opener_rebid'
        call.meaning.target_suit = 'C'
        call.meaning.shown_length_min = 3
        effect = call.effect('opener.length.C', owner='opener')
        effect.min_value = 3
        effect.source = 'forcing_notrump_rebid'

        call = self.call('fn_15')
        call.when = '1SP1NP'
        call.bid = '2D'
        call.applies = fn_15_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'forcing_notrump_opener_rebid'
        call.meaning.target_suit = 'D'
        call.meaning.shown_length_min = 3
        effect = call.effect('opener.length.D', owner='opener')
        effect.min_value = 3
        effect.source = 'forcing_notrump_rebid'

        call = self.call('fn_16')
        call.when = '1SP1NP'
        call.bid = '2H'
        call.applies = fn_16_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'forcing_notrump_opener_rebid'
        call.meaning.target_suit = 'H'
        call.meaning.shown_length_min = 4
        effect = call.effect('opener.length.H', owner='opener')
        effect.min_value = 4
        effect.source = 'forcing_notrump_rebid'

        call = self.call('fn_17')
        call.when = '1SP1NP'
        call.bid = '2S'
        call.applies = fn_17_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'forcing_notrump_opener_rebid'
        call.meaning.target_suit = 'S'
        call.meaning.shown_length_min = 6
        effect = call.effect('opener.length.S', owner='opener')
        effect.min_value = 6
        effect.source = 'forcing_notrump_rebid'

        call = self.call('fn_18')
        call.when = '1SP1NP'
        call.bid = '2N'
        call.applies = fn_18_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'invitational']
        call.meaning.action = 'forcing_notrump_opener_notrump_rebid'
        call.meaning.target_suit = 'N'
        call.meaning.hcp_range = [18, 19]
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 18
        effect.max_value = 19
        effect.source = 'forcing_notrump_2n'
        effect = call.effect('opener.shape', owner='opener')
        effect.value = 'balanced'
        effect.source = 'forcing_notrump_2n'

        call = self.call('fn_19')
        call.when = '1SP1NP2CP'
        call.bid = 'P'
        call.applies = fn_19_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'pass_final_contract'
        call.meaning.target_suit = 'C'
        call.meaning.level = 2
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'C'
        effect.level = 2
        effect.source = 'forcing_notrump'

        call = self.call('fn_20')
        call.when = '1SP1NP2DP'
        call.bid = 'P'
        call.applies = fn_20_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'pass_final_contract'
        call.meaning.target_suit = 'D'
        call.meaning.level = 2
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'D'
        effect.level = 2
        effect.source = 'forcing_notrump'

        call = self.call('fn_21')
        call.when = '1HP1NP2CP'
        call.bid = 'P'
        call.applies = fn_21_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'pass_final_contract'
        call.meaning.target_suit = 'C'
        call.meaning.level = 2
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'C'
        effect.level = 2
        effect.source = 'forcing_notrump'

        call = self.call('fn_22')
        call.when = '1HP1NP2DP'
        call.bid = 'P'
        call.applies = fn_22_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'pass_final_contract'
        call.meaning.target_suit = 'D'
        call.meaning.level = 2
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'D'
        effect.level = 2
        effect.source = 'forcing_notrump'

        call = self.call('fn_23')
        call.when = '1SP1NP2CP'
        call.bid = '2S'
        call.applies = fn_23_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'major_preference'
        call.meaning.target_suit = 'S'
        call.meaning.level = 2
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'S'
        effect.level = 2
        effect.source = 'forcing_notrump'

        call = self.call('fn_24')
        call.when = '1SP1NP2DP'
        call.bid = '2S'
        call.applies = fn_24_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'major_preference'
        call.meaning.target_suit = 'S'
        call.meaning.level = 2
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'S'
        effect.level = 2
        effect.source = 'forcing_notrump'

        call = self.call('fn_25')
        call.when = '1HP1NP2CP'
        call.bid = '2H'
        call.applies = fn_25_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'major_preference'
        call.meaning.target_suit = 'H'
        call.meaning.level = 2
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'H'
        effect.level = 2
        effect.source = 'forcing_notrump'

        call = self.call('fn_26')
        call.when = '1HP1NP2DP'
        call.bid = '2H'
        call.applies = fn_26_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'major_preference'
        call.meaning.target_suit = 'H'
        call.meaning.level = 2
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'H'
        effect.level = 2
        effect.source = 'forcing_notrump'

        call = self.call('fn_27')
        call.when = '1SP1NP2CP'
        call.bid = '2N'
        call.applies = fn_27_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['invitational']
        call.meaning.action = 'notrump_invite'
        call.meaning.target_suit = 'N'
        call.meaning.hcp_range = [11, 12]
        effect = call.effect('notrump_contract_interest', owner='partnership')
        effect.level = 2
        effect.source = 'forcing_notrump'

        call = self.call('fn_28')
        call.when = '1SP1NP2DP'
        call.bid = '2N'
        call.applies = fn_28_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['invitational']
        call.meaning.action = 'notrump_invite'
        call.meaning.target_suit = 'N'
        call.meaning.hcp_range = [11, 12]
        effect = call.effect('notrump_contract_interest', owner='partnership')
        effect.level = 2
        effect.source = 'forcing_notrump'

        call = self.call('fn_29')
        call.when = '1SP1NP2SP'
        call.bid = 'P'
        call.applies = fn_29_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'pass_final_contract'
        call.meaning.target_suit = 'S'
        call.meaning.level = 2
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'S'
        effect.level = 2
        effect.source = 'forcing_notrump'

        call = self.call('fn_30')
        call.when = '1HP1NP2HP'
        call.bid = 'P'
        call.applies = fn_30_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'pass_final_contract'
        call.meaning.target_suit = 'H'
        call.meaning.level = 2
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'H'
        effect.level = 2
        effect.source = 'forcing_notrump'

        call = self.call('fn_31')
        call.when = '1SP1NP2CP2NP'
        call.bid = 'P'
        call.applies = fn_31_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'decline_notrump_invite'
        call.meaning.target_suit = 'N'
        call.meaning.level = 2
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'N'
        effect.level = 2
        effect.source = 'forcing_notrump_invite'
        call.description = "Opener declines responder's 2N invitation after 1S-1N-2C with a minimum."
        call.system_notes = 'After 1S-1N-2C-2N, pass declines the notrump invitation.'

        call = self.call('fn_32')
        call.when = '1SP1NP2CP2NP'
        call.bid = '3N'
        call.applies = fn_32_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'accept_notrump_invite'
        call.meaning.target_suit = 'N'
        call.meaning.level = 3
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'N'
        effect.level = 3
        effect.source = 'forcing_notrump_invite'
        call.description = "Opener accepts responder's 2N invitation after 1S-1N-2C with extras."
        call.system_notes = 'After 1S-1N-2C-2N, 3N accepts the notrump invitation.'

        call = self.call('fn_33')
        call.when = '1SP1NP2DP2NP'
        call.bid = 'P'
        call.applies = fn_33_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'decline_notrump_invite'
        call.meaning.target_suit = 'N'
        call.meaning.level = 2
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'N'
        effect.level = 2
        effect.source = 'forcing_notrump_invite'
        call.description = "Opener declines responder's 2N invitation after 1S-1N-2D with a minimum."
        call.system_notes = 'After 1S-1N-2D-2N, pass declines the notrump invitation.'

        call = self.call('fn_34')
        call.when = '1SP1NP2DP2NP'
        call.bid = '3N'
        call.applies = fn_34_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'accept_notrump_invite'
        call.meaning.target_suit = 'N'
        call.meaning.level = 3
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'N'
        effect.level = 3
        effect.source = 'forcing_notrump_invite'
        call.description = "Opener accepts responder's 2N invitation after 1S-1N-2D with extras."
        call.system_notes = 'After 1S-1N-2D-2N, 3N accepts the notrump invitation.'

        call = self.call('fn_35')
        call.when = '1HP1NP2CP2NP'
        call.bid = 'P'
        call.applies = fn_35_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'decline_notrump_invite'
        call.meaning.target_suit = 'N'
        call.meaning.level = 2
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'N'
        effect.level = 2
        effect.source = 'forcing_notrump_invite'
        call.description = "Opener declines responder's 2N invitation after 1H-1N-2C with a minimum."
        call.system_notes = 'After 1H-1N-2C-2N, pass declines the notrump invitation.'

        call = self.call('fn_36')
        call.when = '1HP1NP2CP2NP'
        call.bid = '3N'
        call.applies = fn_36_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'accept_notrump_invite'
        call.meaning.target_suit = 'N'
        call.meaning.level = 3
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'N'
        effect.level = 3
        effect.source = 'forcing_notrump_invite'
        call.description = "Opener accepts responder's 2N invitation after 1H-1N-2C with extras."
        call.system_notes = 'After 1H-1N-2C-2N, 3N accepts the notrump invitation.'

        call = self.call('fn_37')
        call.when = '1HP1NP2DP2NP'
        call.bid = 'P'
        call.applies = fn_37_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'decline_notrump_invite'
        call.meaning.target_suit = 'N'
        call.meaning.level = 2
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'N'
        effect.level = 2
        effect.source = 'forcing_notrump_invite'
        call.description = "Opener declines responder's 2N invitation after 1H-1N-2D with a minimum."
        call.system_notes = 'After 1H-1N-2D-2N, pass declines the notrump invitation.'

        call = self.call('fn_38')
        call.when = '1HP1NP2DP2NP'
        call.bid = '3N'
        call.applies = fn_38_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'accept_notrump_invite'
        call.meaning.target_suit = 'N'
        call.meaning.level = 3
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'N'
        effect.level = 3
        effect.source = 'forcing_notrump_invite'
        call.description = "Opener accepts responder's 2N invitation after 1H-1N-2D with extras."
        call.system_notes = 'After 1H-1N-2D-2N, 3N accepts the notrump invitation.'

        call = self.call('fn_1')
        call.when = '1HP'
        call.bid = '1S'
        call.applies = fn_1_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'one_level_response'
        call.meaning.target_suit = 'S'
        call.meaning.shown_length_min = 4
        effect = call.effect('responder.length.S', owner='responder')
        effect.min_value = 4
        effect.source = 'one_level_response'
        effect = call.effect('responder.hcp', owner='responder')
        effect.min_value = 6
        effect.source = 'one_level_response'
        call.description = 'Responder bids 1S over 1H with at least four spades.'

        call = self.call('fn_2')
        call.when = '1HP'
        call.bid = '1N'
        call.applies = fn_2_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'forcing_notrump_response'
        call.meaning.target_suit = 'N'
        call.meaning.hcp_range = [6, 12]
        effect = call.effect('forcing_notrump_response', owner='responder')
        effect.opening_suit = 'H'
        effect.hcp_min = 6
        effect.hcp_max = 12
        effect = call.effect('responder.hcp', owner='responder')
        effect.min_value = 6
        effect.max_value = 12
        effect.source = 'forcing_notrump'
        effect = call.effect('responder.length.H', owner='responder')
        effect.max_value = 2
        effect.source = 'forcing_notrump_no_raise'
        effect = call.effect('responder.length.S', owner='responder')
        effect.max_value = 3
        effect.source = 'forcing_notrump_no_spades'
        call.description = 'Forcing 1N over 1H: 6-12, no heart raise, and no four-card spade response.'

        call = self.call('fn_3')
        call.when = '1SP'
        call.bid = '1N'
        call.applies = fn_3_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'forcing_notrump_response'
        call.meaning.target_suit = 'N'
        call.meaning.hcp_range = [6, 12]
        effect = call.effect('forcing_notrump_response', owner='responder')
        effect.opening_suit = 'S'
        effect.hcp_min = 6
        effect.hcp_max = 12
        effect = call.effect('responder.hcp', owner='responder')
        effect.min_value = 6
        effect.max_value = 12
        effect.source = 'forcing_notrump'
        effect = call.effect('responder.length.S', owner='responder')
        effect.max_value = 2
        effect.source = 'forcing_notrump_no_raise'
        call.description = 'Forcing 1N over 1S: 6-12 without a direct spade raise.'

        call = self.call('fn_4')
        call.when = '1HP'
        call.bid = '2C'
        call.applies = fn_4_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'two_over_one_game_force'
        call.meaning.target_suit = 'C'
        call.meaning.shown_length_min = 4
        effect = call.effect('partnership.force_status', owner='partnership')
        effect.value = 'game_forcing'
        effect.source = 'two_over_one'
        effect = call.effect('responder.length.C', owner='responder')
        effect.min_value = 4
        effect.source = 'two_over_one'

        call = self.call('fn_5')
        call.when = '1HP'
        call.bid = '2D'
        call.applies = fn_5_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'two_over_one_game_force'
        call.meaning.target_suit = 'D'
        call.meaning.shown_length_min = 4
        effect = call.effect('partnership.force_status', owner='partnership')
        effect.value = 'game_forcing'
        effect.source = 'two_over_one'
        effect = call.effect('responder.length.D', owner='responder')
        effect.min_value = 4
        effect.source = 'two_over_one'

        call = self.call('fn_6')
        call.when = '1SP'
        call.bid = '2C'
        call.applies = fn_6_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'two_over_one_game_force'
        call.meaning.target_suit = 'C'
        call.meaning.shown_length_min = 4
        effect = call.effect('partnership.force_status', owner='partnership')
        effect.value = 'game_forcing'
        effect.source = 'two_over_one'
        effect = call.effect('responder.length.C', owner='responder')
        effect.min_value = 4
        effect.source = 'two_over_one'

        call = self.call('fn_7')
        call.when = '1SP'
        call.bid = '2D'
        call.applies = fn_7_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'two_over_one_game_force'
        call.meaning.target_suit = 'D'
        call.meaning.shown_length_min = 4
        effect = call.effect('partnership.force_status', owner='partnership')
        effect.value = 'game_forcing'
        effect.source = 'two_over_one'
        effect = call.effect('responder.length.D', owner='responder')
        effect.min_value = 4
        effect.source = 'two_over_one'

        call = self.call('fn_8')
        call.when = '1SP'
        call.bid = '2H'
        call.applies = fn_8_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'two_over_one_game_force'
        call.meaning.target_suit = 'H'
        call.meaning.shown_length_min = 5
        effect = call.effect('partnership.force_status', owner='partnership')
        effect.value = 'game_forcing'
        effect.source = 'two_over_one'
        effect = call.effect('responder.length.H', owner='responder')
        effect.min_value = 5
        effect.source = 'two_over_one'
