# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_1_applies(ctx):
    return (ctx.hand.hcp >= 10 and ctx.hand.length('D') >= 4 and ((ctx.hand.length('S') <= 4) and (ctx.hand.length('H') <= 4)) and (ctx.hand.length('D') >= ctx.hand.length('C')))
def cs_2_applies(ctx):
    return (ctx.hand.hcp >= 10 and ctx.hand.length('C') >= 3 and ((ctx.hand.length('S') <= 4) and (ctx.hand.length('H') <= 4)))
def cs_31_applies(ctx):
    return (18 <= ctx.hand.hcp <= 19 and ctx.hand.balanced)
def cs_32_applies(ctx):
    return (18 <= ctx.hand.hcp <= 19 and ctx.hand.balanced)
def cs_33_applies(ctx):
    return (18 <= ctx.hand.hcp <= 19 and ctx.hand.balanced)
def cs_34_applies(ctx):
    return (18 <= ctx.hand.hcp <= 19 and ctx.hand.balanced)
def cs_35_applies(ctx):
    return (18 <= ctx.hand.hcp <= 19 and ctx.hand.balanced)
def cs_36_applies(ctx):
    return (ctx.hand.length('C') >= 5)
def cs_37_applies(ctx):
    return (ctx.hand.length('C') >= 5)
def cs_38_applies(ctx):
    return (ctx.hand.length('C') >= 5)
def cs_39_applies(ctx):
    return (ctx.hand.length('D') >= 5)
def cs_40_applies(ctx):
    return (ctx.hand.length('D') >= 5)
def cs_41_applies(ctx):
    return (ctx.hand.length('C') >= 4)
def cs_42_applies(ctx):
    return (ctx.hand.length('C') >= 4)
def cs_43_applies(ctx):
    return (ctx.hand.hcp >= 16 and ctx.hand.length('D') >= 4)
def cs_44_applies(ctx):
    return (ctx.hand.hcp >= 16 and ctx.hand.length('D') >= 4)
def cs_45_applies(ctx):
    return (ctx.hand.hcp >= 16 and ctx.hand.length('H') >= 4)
def cs_46_applies(ctx):
    return (ctx.hand.hcp >= 16 and ctx.hand.length('H') >= 4)
def cs_47_applies(ctx):
    return (ctx.hand.hcp >= 16 and ctx.hand.length('H') >= 4)
def cs_48_applies(ctx):
    return (ctx.hand.hcp >= 16 and ctx.hand.length('S') >= 4)
def cs_49_applies(ctx):
    return (ctx.hand.hcp >= 16 and ctx.hand.length('H') >= 4)
def cs_50_applies(ctx):
    return (ctx.hand.hcp >= 16 and ctx.hand.length('S') >= 4)
def cs_51_applies(ctx):
    return (ctx.hand.hcp >= 18 and ctx.hand.length('C') >= 5 and ctx.hand.length('H') >= 4)
def cs_52_applies(ctx):
    return (ctx.hand.hcp >= 18 and ctx.hand.length('C') >= 5 and ctx.hand.length('S') >= 4)
def cs_53_applies(ctx):
    return (ctx.hand.hcp >= 18 and ctx.hand.length('C') >= 5 and ctx.hand.length('S') >= 4)
def cs_54_applies(ctx):
    return (ctx.hand.hcp >= 18 and ctx.hand.length('D') >= 5 and ctx.hand.length('S') >= 4)
def cs_18_applies(ctx):
    return (ctx.hand.length('H') >= 4)
def cs_19_applies(ctx):
    return (ctx.hand.length('S') >= 4 and (ctx.hand.length('H') <= 3))
def cs_20_applies(ctx):
    return ((ctx.hand.hcp >= 12 and ctx.hand.hcp <= 14) and ctx.hand.balanced == True and ((ctx.hand.length('H') <= 3) and (ctx.hand.length('S') <= 3)))
def cs_21_applies(ctx):
    return (ctx.hand.length('S') >= 4)
def cs_22_applies(ctx):
    return ((ctx.hand.hcp >= 12 and ctx.hand.hcp <= 14) and ctx.hand.balanced == True and (ctx.hand.length('H') <= 3))
def cs_23_applies(ctx):
    return (ctx.hand.length('H') >= 3 and (ctx.hand.hcp >= 12 and ctx.hand.hcp <= 14))
def cs_24_applies(ctx):
    return ((ctx.hand.hcp >= 12 and ctx.hand.hcp <= 14) and ctx.hand.balanced == True and (ctx.hand.length('S') <= 3))
def cs_25_applies(ctx):
    return (ctx.hand.length('S') >= 3 and (ctx.hand.hcp >= 12 and ctx.hand.hcp <= 14))
def cs_26_applies(ctx):
    return (ctx.hand.length('S') >= 4)
def cs_27_applies(ctx):
    return ((ctx.hand.hcp >= 12 and ctx.hand.hcp <= 14) and ctx.hand.balanced == True and (ctx.hand.length('H') <= 3))
def cs_28_applies(ctx):
    return (ctx.hand.length('H') >= 3 and (ctx.hand.hcp >= 12 and ctx.hand.hcp <= 14))
def cs_29_applies(ctx):
    return ((ctx.hand.hcp >= 12 and ctx.hand.hcp <= 14) and ctx.hand.balanced == True and (ctx.hand.length('S') <= 3))
def cs_30_applies(ctx):
    return (ctx.hand.length('S') >= 3 and (ctx.hand.hcp >= 12 and ctx.hand.hcp <= 14))
def cs_55_applies(ctx):
    return (ctx.hand.length('H') >= 6 and ctx.hand.hcp <= 10)
def cs_56_applies(ctx):
    return (ctx.hand.length('H') >= 6 and ctx.hand.hcp <= 10)
def cs_57_applies(ctx):
    return (ctx.hand.length('H') >= 6 and ctx.hand.hcp <= 10)
def cs_58_applies(ctx):
    return (ctx.hand.length('H') >= 6 and ctx.hand.hcp <= 10)
def cs_59_applies(ctx):
    return (ctx.hand.length('S') >= 6 and ctx.hand.hcp <= 10)
def cs_60_applies(ctx):
    return (ctx.hand.length('S') >= 6 and ctx.hand.hcp <= 10)
def cs_3_applies(ctx):
    return (ctx.hand.hcp >= 6 and ctx.hand.length('D') >= 4)
def cs_4_applies(ctx):
    return (ctx.hand.hcp >= 6 and ctx.hand.length('H') >= 4 and (ctx.hand.length('S') <= 4))
def cs_5_applies(ctx):
    return (ctx.hand.hcp >= 6 and ctx.hand.length('S') >= 4 and ((ctx.hand.length('H') <= 3) or (ctx.hand.length('S') >= 5)))
def cs_6_applies(ctx):
    return (ctx.hand.hcp >= 6 and ctx.hand.length('H') >= 4 and (ctx.hand.length('S') <= 4))
def cs_7_applies(ctx):
    return (ctx.hand.hcp >= 6 and ctx.hand.length('S') >= 4 and ((ctx.hand.length('H') <= 3) or (ctx.hand.length('S') >= 5)))
def cs_8_applies(ctx):
    return ((ctx.hand.hcp >= 6 and ctx.hand.hcp <= 10) and ((ctx.hand.length('H') <= 3) and (ctx.hand.length('S') <= 3)))
def cs_9_applies(ctx):
    return ((ctx.hand.hcp >= 6 and ctx.hand.hcp <= 10) and ((ctx.hand.length('H') <= 3) and (ctx.hand.length('S') <= 3)))
def cs_10_applies(ctx):
    return ((ctx.hand.hcp >= 11 and ctx.hand.hcp <= 12) and ctx.hand.balanced == True and ((ctx.hand.length('H') <= 3) and (ctx.hand.length('S') <= 3)))
def cs_11_applies(ctx):
    return ((ctx.hand.hcp >= 11 and ctx.hand.hcp <= 12) and ctx.hand.balanced == True and ((ctx.hand.length('H') <= 3) and (ctx.hand.length('S') <= 3)))
def cs_12_applies(ctx):
    return ((ctx.hand.hcp >= 13 and ctx.hand.hcp <= 15) and ctx.hand.balanced == True and ((ctx.hand.length('H') <= 3) and (ctx.hand.length('S') <= 3)))
def cs_13_applies(ctx):
    return ((ctx.hand.hcp >= 13 and ctx.hand.hcp <= 15) and ctx.hand.balanced == True and ((ctx.hand.length('H') <= 3) and (ctx.hand.length('S') <= 3)))
def cs_14_applies(ctx):
    return ((ctx.hand.hcp >= 3 and ctx.hand.hcp <= 7) and ctx.hand.length('H') >= 6)
def cs_15_applies(ctx):
    return ((ctx.hand.hcp >= 3 and ctx.hand.hcp <= 7) and ctx.hand.length('S') >= 6)
def cs_16_applies(ctx):
    return ((ctx.hand.hcp >= 3 and ctx.hand.hcp <= 7) and ctx.hand.length('H') >= 6)
def cs_17_applies(ctx):
    return ((ctx.hand.hcp >= 3 and ctx.hand.hcp <= 7) and ctx.hand.length('S') >= 6)

class MeowMinorOpeningStructureGadget(Gadget):
    id = 'meow_minor_opening_structure'
    namespace = 'meow_2over1'
    name = 'Meow Minor Opening Structure'
    version = '0.1.0'
    description = 'Natural 1C/1D openings, one-level responses, weak jump shifts in majors, natural notrump responses, and simple opener rebids for the Meow 2/1 benchmark.\n'
    author = Author('Meow Li')

    def build(self):

        call = self.call('cs_1')
        call.seats = [1, 2, 3, 4]
        call.bid = '1D'
        call.applies = cs_1_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'context_initiating']
        call.meaning.action = 'opening'
        call.meaning.target_suit = 'D'
        call.meaning.shown_length_min = 4
        effect = call.effect('minor_opening')
        effect.actor_role = 'opener'
        effect.target_suit = 'D'
        effect.shown_length_min = 4
        effect = call.effect('opener.length.D', owner='opener')
        effect.min_value = 4
        effect.source = 'minor_opening'
        effect = call.effect('opener.length.H', owner='opener')
        effect.max_value = 4
        effect.source = 'minor_opening_denial'
        effect = call.effect('opener.length.S', owner='opener')
        effect.max_value = 4
        effect.source = 'minor_opening_denial'
        call.description = 'Opens 1D naturally with opening values, at least four diamonds, no five-card major, and diamonds at least as long as clubs.'
        call.system_notes = '1D opening is natural, usually four or more diamonds, and denies a five-card major.'

        call = self.call('cs_2')
        call.seats = [1, 2, 3, 4]
        call.bid = '1C'
        call.applies = cs_2_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'context_initiating']
        call.meaning.action = 'opening'
        call.meaning.target_suit = 'C'
        call.meaning.shown_length_min = 3
        effect = call.effect('minor_opening')
        effect.actor_role = 'opener'
        effect.target_suit = 'C'
        effect.shown_length_min = 3
        effect = call.effect('opener.length.C', owner='opener')
        effect.min_value = 3
        effect.source = 'minor_opening'
        effect = call.effect('opener.length.H', owner='opener')
        effect.max_value = 4
        effect.source = 'minor_opening_denial'
        effect = call.effect('opener.length.S', owner='opener')
        effect.max_value = 4
        effect.source = 'minor_opening_denial'
        call.description = 'Opens 1C naturally with opening values, at least three clubs, and no five-card major.'
        call.system_notes = '1C opening is natural, may be three cards, and denies a five-card major.'

        call = self.call('cs_31')
        call.when = '1CP1DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2N'
        call.applies = cs_31_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'invitational']
        call.meaning.action = 'opener_notrump_rebid'
        call.meaning.target_suit = 'N'
        call.meaning.hcp_range = [18, 19]
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 18
        effect.max_value = 19
        effect.source = 'jump_notrump_rebid'
        effect = call.effect('opener.shape', owner='opener')
        effect.value = 'balanced'
        effect.source = 'jump_notrump_rebid'
        call.description = 'Opener rebids 2N after 1C-1D with an 18-19 balanced hand when no one-level major is chosen.'
        call.system_notes = 'After 1C-1D, 2N shows about 18-19 balanced values.'

        call = self.call('cs_32')
        call.when = '1CP1HP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2N'
        call.applies = cs_32_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'invitational']
        call.meaning.action = 'opener_notrump_rebid'
        call.meaning.target_suit = 'N'
        call.meaning.hcp_range = [18, 19]
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 18
        effect.max_value = 19
        effect.source = 'jump_notrump_rebid'
        effect = call.effect('opener.shape', owner='opener')
        effect.value = 'balanced'
        effect.source = 'jump_notrump_rebid'
        call.description = 'Opener rebids 2N after 1C-1H with 18-19 balanced values.'
        call.system_notes = 'After 1C-1H, 2N shows about 18-19 balanced values.'

        call = self.call('cs_33')
        call.when = '1CP1SP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2N'
        call.applies = cs_33_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'invitational']
        call.meaning.action = 'opener_notrump_rebid'
        call.meaning.target_suit = 'N'
        call.meaning.hcp_range = [18, 19]
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 18
        effect.max_value = 19
        effect.source = 'jump_notrump_rebid'
        effect = call.effect('opener.shape', owner='opener')
        effect.value = 'balanced'
        effect.source = 'jump_notrump_rebid'
        call.description = 'Opener rebids 2N after 1C-1S with 18-19 balanced values.'
        call.system_notes = 'After 1C-1S, 2N shows about 18-19 balanced values.'

        call = self.call('cs_34')
        call.when = '1DP1HP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2N'
        call.applies = cs_34_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'invitational']
        call.meaning.action = 'opener_notrump_rebid'
        call.meaning.target_suit = 'N'
        call.meaning.hcp_range = [18, 19]
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 18
        effect.max_value = 19
        effect.source = 'jump_notrump_rebid'
        effect = call.effect('opener.shape', owner='opener')
        effect.value = 'balanced'
        effect.source = 'jump_notrump_rebid'
        call.description = 'Opener rebids 2N after 1D-1H with 18-19 balanced values.'
        call.system_notes = 'After 1D-1H, 2N shows about 18-19 balanced values.'

        call = self.call('cs_35')
        call.when = '1DP1SP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2N'
        call.applies = cs_35_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'invitational']
        call.meaning.action = 'opener_notrump_rebid'
        call.meaning.target_suit = 'N'
        call.meaning.hcp_range = [18, 19]
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 18
        effect.max_value = 19
        effect.source = 'jump_notrump_rebid'
        effect = call.effect('opener.shape', owner='opener')
        effect.value = 'balanced'
        effect.source = 'jump_notrump_rebid'
        call.description = 'Opener rebids 2N after 1D-1S with 18-19 balanced values.'
        call.system_notes = 'After 1D-1S, 2N shows about 18-19 balanced values.'

        call = self.call('cs_36')
        call.when = '1CP1DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2C'
        call.applies = cs_36_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'opener_minor_rebid'
        call.meaning.target_suit = 'C'
        call.meaning.shown_length_min = 5
        effect = call.effect('opener.length.C', owner='opener')
        effect.min_value = 5
        effect.source = 'opener_minor_rebid'
        call.description = 'Opener rebids 2C after 1C-1D with at least five clubs when no major or notrump rebid is preferred.'
        call.system_notes = 'After 1C-1D, 2C is natural and usually shows at least five clubs.'

        call = self.call('cs_37')
        call.when = '1CP1HP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2C'
        call.applies = cs_37_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'opener_minor_rebid'
        call.meaning.target_suit = 'C'
        call.meaning.shown_length_min = 5
        effect = call.effect('opener.length.C', owner='opener')
        effect.min_value = 5
        effect.source = 'opener_minor_rebid'
        call.description = 'Opener rebids 2C after 1C-1H with at least five clubs.'
        call.system_notes = 'After 1C-1H, 2C is natural and usually shows at least five clubs.'

        call = self.call('cs_38')
        call.when = '1CP1SP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2C'
        call.applies = cs_38_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'opener_minor_rebid'
        call.meaning.target_suit = 'C'
        call.meaning.shown_length_min = 5
        effect = call.effect('opener.length.C', owner='opener')
        effect.min_value = 5
        effect.source = 'opener_minor_rebid'
        call.description = 'Opener rebids 2C after 1C-1S with at least five clubs.'
        call.system_notes = 'After 1C-1S, 2C is natural and usually shows at least five clubs.'

        call = self.call('cs_39')
        call.when = '1DP1HP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2D'
        call.applies = cs_39_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'opener_minor_rebid'
        call.meaning.target_suit = 'D'
        call.meaning.shown_length_min = 5
        effect = call.effect('opener.length.D', owner='opener')
        effect.min_value = 5
        effect.source = 'opener_minor_rebid'
        call.description = 'Opener rebids 2D after 1D-1H with at least five diamonds.'
        call.system_notes = 'After 1D-1H, 2D is natural and usually shows at least five diamonds.'

        call = self.call('cs_40')
        call.when = '1DP1SP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2D'
        call.applies = cs_40_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'opener_minor_rebid'
        call.meaning.target_suit = 'D'
        call.meaning.shown_length_min = 5
        effect = call.effect('opener.length.D', owner='opener')
        effect.min_value = 5
        effect.source = 'opener_minor_rebid'
        call.description = 'Opener rebids 2D after 1D-1S with at least five diamonds.'
        call.system_notes = 'After 1D-1S, 2D is natural and usually shows at least five diamonds.'

        call = self.call('cs_41')
        call.when = '1DP1HP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2C'
        call.applies = cs_41_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'opener_second_suit_rebid'
        call.meaning.target_suit = 'C'
        call.meaning.shown_length_min = 4
        effect = call.effect('opener.length.C', owner='opener')
        effect.min_value = 4
        effect.source = 'opener_second_suit_rebid'
        call.description = 'Opener rebids 2C after 1D-1H as a natural lower-ranking second suit.'
        call.system_notes = 'After 1D-1H, 2C is natural and shows clubs.'

        call = self.call('cs_42')
        call.when = '1DP1SP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2C'
        call.applies = cs_42_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'opener_second_suit_rebid'
        call.meaning.target_suit = 'C'
        call.meaning.shown_length_min = 4
        effect = call.effect('opener.length.C', owner='opener')
        effect.min_value = 4
        effect.source = 'opener_second_suit_rebid'
        call.description = 'Opener rebids 2C after 1D-1S as a natural lower-ranking second suit.'
        call.system_notes = 'After 1D-1S, 2C is natural and shows clubs.'

        call = self.call('cs_43')
        call.when = '1CP1HP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2D'
        call.applies = cs_43_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'opener_reverse'
        call.meaning.target_suit = 'D'
        call.meaning.shown_length_min = 4
        effect = call.effect('opener.length.D', owner='opener')
        effect.min_value = 4
        effect.source = 'opener_reverse'
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 16
        effect.source = 'opener_reverse'
        effect = call.effect('partnership.force_status', owner='partnership')
        effect.value = 'one_round_forcing'
        effect.source = 'opener_reverse'
        call.description = 'Opener reverses into diamonds after 1C-1H, showing extras.'
        call.system_notes = 'After 1C-1H, 2D is a reverse and shows extra values.'

        call = self.call('cs_44')
        call.when = '1CP1SP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2D'
        call.applies = cs_44_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'opener_reverse'
        call.meaning.target_suit = 'D'
        call.meaning.shown_length_min = 4
        effect = call.effect('opener.length.D', owner='opener')
        effect.min_value = 4
        effect.source = 'opener_reverse'
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 16
        effect.source = 'opener_reverse'
        effect = call.effect('partnership.force_status', owner='partnership')
        effect.value = 'one_round_forcing'
        effect.source = 'opener_reverse'
        call.description = 'Opener reverses into diamonds after 1C-1S, showing extras.'
        call.system_notes = 'After 1C-1S, 2D is a reverse and shows extra values.'

        call = self.call('cs_45')
        call.when = '1CP1SP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2H'
        call.applies = cs_45_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'opener_reverse'
        call.meaning.target_suit = 'H'
        call.meaning.shown_length_min = 4
        effect = call.effect('opener.length.H', owner='opener')
        effect.min_value = 4
        effect.source = 'opener_reverse'
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 16
        effect.source = 'opener_reverse'
        effect = call.effect('partnership.force_status', owner='partnership')
        effect.value = 'one_round_forcing'
        effect.source = 'opener_reverse'
        call.description = 'Opener reverses into hearts after 1C-1S, showing extras.'
        call.system_notes = 'After 1C-1S, 2H is a reverse and shows extra values.'

        call = self.call('cs_46')
        call.when = '1DP1SP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2H'
        call.applies = cs_46_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'opener_reverse'
        call.meaning.target_suit = 'H'
        call.meaning.shown_length_min = 4
        effect = call.effect('opener.length.H', owner='opener')
        effect.min_value = 4
        effect.source = 'opener_reverse'
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 16
        effect.source = 'opener_reverse'
        effect = call.effect('partnership.force_status', owner='partnership')
        effect.value = 'one_round_forcing'
        effect.source = 'opener_reverse'
        call.description = 'Opener reverses into hearts after 1D-1S, showing extras.'
        call.system_notes = 'After 1D-1S, 2H is a reverse and shows extra values.'

        call = self.call('cs_47')
        call.when = '1CP1HP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3H'
        call.applies = cs_47_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['support_showing', 'invitational']
        call.meaning.action = 'opener_jump_raise'
        call.meaning.target_suit = 'H'
        effect = call.effect('partnership.agreed_suit', owner='partnership')
        effect.value = 'H'
        effect.source = 'opener_jump_raise'
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 16
        effect.source = 'opener_jump_raise'
        effect = call.effect('opener.length.H', owner='opener')
        effect.min_value = 4
        effect.source = 'opener_jump_raise'
        call.description = 'Opener jump-raises hearts after 1C-1H with extras and four-card support.'
        call.system_notes = 'After 1C-1H, 3H is a strong raise with four-card support.'

        call = self.call('cs_48')
        call.when = '1CP1SP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3S'
        call.applies = cs_48_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['support_showing', 'invitational']
        call.meaning.action = 'opener_jump_raise'
        call.meaning.target_suit = 'S'
        effect = call.effect('partnership.agreed_suit', owner='partnership')
        effect.value = 'S'
        effect.source = 'opener_jump_raise'
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 16
        effect.source = 'opener_jump_raise'
        effect = call.effect('opener.length.S', owner='opener')
        effect.min_value = 4
        effect.source = 'opener_jump_raise'
        call.description = 'Opener jump-raises spades after 1C-1S with extras and four-card support.'
        call.system_notes = 'After 1C-1S, 3S is a strong raise with four-card support.'

        call = self.call('cs_49')
        call.when = '1DP1HP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3H'
        call.applies = cs_49_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['support_showing', 'invitational']
        call.meaning.action = 'opener_jump_raise'
        call.meaning.target_suit = 'H'
        effect = call.effect('partnership.agreed_suit', owner='partnership')
        effect.value = 'H'
        effect.source = 'opener_jump_raise'
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 16
        effect.source = 'opener_jump_raise'
        effect = call.effect('opener.length.H', owner='opener')
        effect.min_value = 4
        effect.source = 'opener_jump_raise'
        call.description = 'Opener jump-raises hearts after 1D-1H with extras and four-card support.'
        call.system_notes = 'After 1D-1H, 3H is a strong raise with four-card support.'

        call = self.call('cs_50')
        call.when = '1DP1SP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3S'
        call.applies = cs_50_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['support_showing', 'invitational']
        call.meaning.action = 'opener_jump_raise'
        call.meaning.target_suit = 'S'
        effect = call.effect('partnership.agreed_suit', owner='partnership')
        effect.value = 'S'
        effect.source = 'opener_jump_raise'
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 16
        effect.source = 'opener_jump_raise'
        effect = call.effect('opener.length.S', owner='opener')
        effect.min_value = 4
        effect.source = 'opener_jump_raise'
        call.description = 'Opener jump-raises spades after 1D-1S with extras and four-card support.'
        call.system_notes = 'After 1D-1S, 3S is a strong raise with four-card support.'

        call = self.call('cs_51')
        call.when = '1CP1DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2H'
        call.applies = cs_51_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'game_forcing']
        call.meaning.action = 'opener_jump_shift'
        call.meaning.target_suit = 'H'
        call.meaning.shown_length_min = 4
        effect = call.effect('opener.length.C', owner='opener')
        effect.min_value = 5
        effect.source = 'opener_jump_shift'
        effect = call.effect('opener.length.H', owner='opener')
        effect.min_value = 4
        effect.source = 'opener_jump_shift'
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 18
        effect.source = 'opener_jump_shift'
        effect = call.effect('partnership.force_status', owner='partnership')
        effect.value = 'game_forcing'
        effect.source = 'opener_jump_shift'
        call.description = 'Opener jump-shifts to 2H after 1C-1D with a strong 5+ club and 4+ heart hand.'
        call.system_notes = 'After 1C-1D, 2H is a strong natural jump shift showing clubs and hearts, game forcing.'

        call = self.call('cs_52')
        call.when = '1CP1DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2S'
        call.applies = cs_52_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'game_forcing']
        call.meaning.action = 'opener_jump_shift'
        call.meaning.target_suit = 'S'
        call.meaning.shown_length_min = 4
        effect = call.effect('opener.length.C', owner='opener')
        effect.min_value = 5
        effect.source = 'opener_jump_shift'
        effect = call.effect('opener.length.S', owner='opener')
        effect.min_value = 4
        effect.source = 'opener_jump_shift'
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 18
        effect.source = 'opener_jump_shift'
        effect = call.effect('partnership.force_status', owner='partnership')
        effect.value = 'game_forcing'
        effect.source = 'opener_jump_shift'
        call.description = 'Opener jump-shifts to 2S after 1C-1D with a strong 5+ club and 4+ spade hand.'
        call.system_notes = 'After 1C-1D, 2S is a strong natural jump shift showing clubs and spades, game forcing.'

        call = self.call('cs_53')
        call.when = '1CP1HP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2S'
        call.applies = cs_53_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'game_forcing']
        call.meaning.action = 'opener_jump_shift'
        call.meaning.target_suit = 'S'
        call.meaning.shown_length_min = 4
        effect = call.effect('opener.length.C', owner='opener')
        effect.min_value = 5
        effect.source = 'opener_jump_shift'
        effect = call.effect('opener.length.S', owner='opener')
        effect.min_value = 4
        effect.source = 'opener_jump_shift'
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 18
        effect.source = 'opener_jump_shift'
        effect = call.effect('partnership.force_status', owner='partnership')
        effect.value = 'game_forcing'
        effect.source = 'opener_jump_shift'
        call.description = 'Opener jump-shifts to 2S after 1C-1H with a strong 5+ club and 4+ spade hand.'
        call.system_notes = 'After 1C-1H, 2S is a strong natural jump shift showing clubs and spades, game forcing.'

        call = self.call('cs_54')
        call.when = '1DP1HP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2S'
        call.applies = cs_54_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'game_forcing']
        call.meaning.action = 'opener_jump_shift'
        call.meaning.target_suit = 'S'
        call.meaning.shown_length_min = 4
        effect = call.effect('opener.length.D', owner='opener')
        effect.min_value = 5
        effect.source = 'opener_jump_shift'
        effect = call.effect('opener.length.S', owner='opener')
        effect.min_value = 4
        effect.source = 'opener_jump_shift'
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 18
        effect.source = 'opener_jump_shift'
        effect = call.effect('partnership.force_status', owner='partnership')
        effect.value = 'game_forcing'
        effect.source = 'opener_jump_shift'
        call.description = 'Opener jump-shifts to 2S after 1D-1H with a strong 5+ diamond and 4+ spade hand.'
        call.system_notes = 'After 1D-1H, 2S is a strong natural jump shift showing diamonds and spades, game forcing.'

        call = self.call('cs_18')
        call.when = '1CP1DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '1H'
        call.applies = cs_18_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'opener_rebid'
        call.meaning.target_suit = 'H'
        call.meaning.shown_length_min = 4
        effect = call.effect('opener_rebid')
        effect.target_suit = 'H'
        effect.shown_length_min = 4
        effect = call.effect('opener.length.H', owner='opener')
        effect.min_value = 4
        effect.source = 'opener_rebid'
        call.description = 'Opener rebids 1H after 1C-1D with a four-card heart suit.'
        call.system_notes = 'After 1C-1D, 1H is natural and shows hearts.'

        call = self.call('cs_19')
        call.when = '1CP1DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '1S'
        call.applies = cs_19_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'opener_rebid'
        call.meaning.target_suit = 'S'
        call.meaning.shown_length_min = 4
        effect = call.effect('opener_rebid')
        effect.target_suit = 'S'
        effect.shown_length_min = 4
        effect = call.effect('opener.length.S', owner='opener')
        effect.min_value = 4
        effect.source = 'opener_rebid'
        effect = call.effect('opener.length.H', owner='opener')
        effect.max_value = 3
        effect.source = 'one_level_spade_rebid_denial'
        call.description = 'Opener rebids 1S after 1C-1D with four spades and fewer than four hearts.'
        call.system_notes = 'After 1C-1D, 1S is natural and shows spades.'

        call = self.call('cs_20')
        call.when = '1CP1DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '1N'
        call.applies = cs_20_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'notrump_rebid'
        call.meaning.hcp_range = [12, 14]
        effect = call.effect('opener_notrump_rebid')
        effect.hcp_min = 12
        effect.hcp_max = 14
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 12
        effect.max_value = 14
        effect.source = 'notrump_rebid'
        effect = call.effect('opener.shape', owner='opener')
        effect.value = 'balanced'
        effect.source = 'notrump_rebid'
        effect = call.effect('opener.length.H', owner='opener')
        effect.max_value = 3
        effect.source = 'notrump_rebid_denial'
        effect = call.effect('opener.length.S', owner='opener')
        effect.max_value = 3
        effect.source = 'notrump_rebid_denial'
        call.description = 'Opener rebids 1N after 1C-1D with 12-14 balanced values and no four-card major.'
        call.system_notes = 'After 1C-1D, 1N shows a minimum balanced hand.'

        call = self.call('cs_21')
        call.when = '1CP1HP'
        call.seats = [1, 2, 3, 4]
        call.bid = '1S'
        call.applies = cs_21_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'opener_rebid'
        call.meaning.target_suit = 'S'
        call.meaning.shown_length_min = 4
        effect = call.effect('opener_rebid')
        effect.target_suit = 'S'
        effect.shown_length_min = 4
        effect = call.effect('opener.length.S', owner='opener')
        effect.min_value = 4
        effect.source = 'opener_rebid'
        effect = call.effect('opener.length.H', owner='opener')
        effect.max_value = 3
        effect.source = 'one_level_spade_rebid_denial'
        call.description = 'Opener rebids 1S after 1C-1H with four spades.'
        call.system_notes = 'After 1C-1H, 1S is natural and shows spades.'

        call = self.call('cs_22')
        call.when = '1CP1HP'
        call.seats = [1, 2, 3, 4]
        call.bid = '1N'
        call.applies = cs_22_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'notrump_rebid'
        call.meaning.hcp_range = [12, 14]
        effect = call.effect('opener_notrump_rebid')
        effect.hcp_min = 12
        effect.hcp_max = 14
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 12
        effect.max_value = 14
        effect.source = 'notrump_rebid'
        effect = call.effect('opener.shape', owner='opener')
        effect.value = 'balanced'
        effect.source = 'notrump_rebid'
        effect = call.effect('opener.length.H', owner='opener')
        effect.max_value = 3
        effect.source = 'notrump_rebid_denial'
        effect = call.effect('opener.length.S', owner='opener')
        effect.max_value = 3
        effect.source = 'notrump_rebid_denial'
        call.description = 'Opener rebids 1N after 1C-1H with 12-14 balanced values and no heart support.'
        call.system_notes = 'After 1C-1H, 1N shows a minimum balanced hand.'

        call = self.call('cs_23')
        call.when = '1CP1HP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2H'
        call.applies = cs_23_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['support_showing']
        call.meaning.action = 'raise'
        call.meaning.target_suit = 'H'
        effect = call.effect('agreed_suit')
        effect.suit = 'H'
        effect.source = 'minor_opener_raise'
        effect = call.effect('partnership.force_status', owner='partnership')
        effect.value = 'not_forcing'
        effect.source = 'simple_raise'
        effect = call.effect('partnership.agreed_suit', owner='partnership')
        effect.value = 'H'
        effect.source = 'minor_opener_raise'
        call.description = 'Opener raises hearts after 1C-1H with three-card or longer support.'
        call.system_notes = 'After 1C-1H, 2H shows heart support and minimum opening values.'

        call = self.call('cs_24')
        call.when = '1CP1SP'
        call.seats = [1, 2, 3, 4]
        call.bid = '1N'
        call.applies = cs_24_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'notrump_rebid'
        call.meaning.hcp_range = [12, 14]
        effect = call.effect('opener_notrump_rebid')
        effect.hcp_min = 12
        effect.hcp_max = 14
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 12
        effect.max_value = 14
        effect.source = 'notrump_rebid'
        effect = call.effect('opener.shape', owner='opener')
        effect.value = 'balanced'
        effect.source = 'notrump_rebid'
        effect = call.effect('opener.length.S', owner='opener')
        effect.max_value = 3
        effect.source = 'notrump_rebid_denial'
        call.description = 'Opener rebids 1N after 1C-1S with 12-14 balanced values and no spade support.'
        call.system_notes = 'After 1C-1S, 1N shows a minimum balanced hand.'

        call = self.call('cs_25')
        call.when = '1CP1SP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2S'
        call.applies = cs_25_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['support_showing']
        call.meaning.action = 'raise'
        call.meaning.target_suit = 'S'
        effect = call.effect('agreed_suit')
        effect.suit = 'S'
        effect.source = 'minor_opener_raise'
        effect = call.effect('partnership.force_status', owner='partnership')
        effect.value = 'not_forcing'
        effect.source = 'simple_raise'
        effect = call.effect('partnership.agreed_suit', owner='partnership')
        effect.value = 'S'
        effect.source = 'minor_opener_raise'
        call.description = 'Opener raises spades after 1C-1S with three-card or longer support.'
        call.system_notes = 'After 1C-1S, 2S shows spade support and minimum opening values.'

        call = self.call('cs_26')
        call.when = '1DP1HP'
        call.seats = [1, 2, 3, 4]
        call.bid = '1S'
        call.applies = cs_26_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'opener_rebid'
        call.meaning.target_suit = 'S'
        call.meaning.shown_length_min = 4
        effect = call.effect('opener_rebid')
        effect.target_suit = 'S'
        effect.shown_length_min = 4
        effect = call.effect('opener.length.S', owner='opener')
        effect.min_value = 4
        effect.source = 'opener_rebid'
        effect = call.effect('opener.length.H', owner='opener')
        effect.max_value = 3
        effect.source = 'one_level_spade_rebid_denial'
        call.description = 'Opener rebids 1S after 1D-1H with four spades.'
        call.system_notes = 'After 1D-1H, 1S is natural and shows spades.'

        call = self.call('cs_27')
        call.when = '1DP1HP'
        call.seats = [1, 2, 3, 4]
        call.bid = '1N'
        call.applies = cs_27_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'notrump_rebid'
        call.meaning.hcp_range = [12, 14]
        effect = call.effect('opener_notrump_rebid')
        effect.hcp_min = 12
        effect.hcp_max = 14
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 12
        effect.max_value = 14
        effect.source = 'notrump_rebid'
        effect = call.effect('opener.shape', owner='opener')
        effect.value = 'balanced'
        effect.source = 'notrump_rebid'
        effect = call.effect('opener.length.H', owner='opener')
        effect.max_value = 3
        effect.source = 'notrump_rebid_denial'
        effect = call.effect('opener.length.S', owner='opener')
        effect.max_value = 3
        effect.source = 'notrump_rebid_denial'
        call.description = 'Opener rebids 1N after 1D-1H with 12-14 balanced values and no heart support.'
        call.system_notes = 'After 1D-1H, 1N shows a minimum balanced hand.'

        call = self.call('cs_28')
        call.when = '1DP1HP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2H'
        call.applies = cs_28_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['support_showing']
        call.meaning.action = 'raise'
        call.meaning.target_suit = 'H'
        effect = call.effect('agreed_suit')
        effect.suit = 'H'
        effect.source = 'minor_opener_raise'
        effect = call.effect('partnership.force_status', owner='partnership')
        effect.value = 'not_forcing'
        effect.source = 'simple_raise'
        effect = call.effect('partnership.agreed_suit', owner='partnership')
        effect.value = 'H'
        effect.source = 'minor_opener_raise'
        call.description = 'Opener raises hearts after 1D-1H with three-card or longer support.'
        call.system_notes = 'After 1D-1H, 2H shows heart support and minimum opening values.'

        call = self.call('cs_29')
        call.when = '1DP1SP'
        call.seats = [1, 2, 3, 4]
        call.bid = '1N'
        call.applies = cs_29_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'notrump_rebid'
        call.meaning.hcp_range = [12, 14]
        effect = call.effect('opener_notrump_rebid')
        effect.hcp_min = 12
        effect.hcp_max = 14
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 12
        effect.max_value = 14
        effect.source = 'notrump_rebid'
        effect = call.effect('opener.shape', owner='opener')
        effect.value = 'balanced'
        effect.source = 'notrump_rebid'
        effect = call.effect('opener.length.S', owner='opener')
        effect.max_value = 3
        effect.source = 'notrump_rebid_denial'
        call.description = 'Opener rebids 1N after 1D-1S with 12-14 balanced values and no spade support.'
        call.system_notes = 'After 1D-1S, 1N shows a minimum balanced hand.'

        call = self.call('cs_30')
        call.when = '1DP1SP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2S'
        call.applies = cs_30_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['support_showing']
        call.meaning.action = 'raise'
        call.meaning.target_suit = 'S'
        effect = call.effect('agreed_suit')
        effect.suit = 'S'
        effect.source = 'minor_opener_raise'
        call.description = 'Opener raises spades after 1D-1S with three-card or longer support.'
        call.system_notes = 'After 1D-1S, 2S shows spade support and minimum opening values.'

        call = self.call('cs_55')
        call.when = '1CP1HP1SP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2H'
        call.applies = cs_55_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'signoff']
        call.meaning.action = 'responder_major_rebid'
        call.meaning.target_suit = 'H'
        call.meaning.shown_length_min = 6
        effect = call.effect('responder.length.H', owner='responder')
        effect.min_value = 6
        effect.source = 'responder_major_rebid'
        effect = call.effect('responder.hcp', owner='responder')
        effect.max_value = 10
        effect.source = 'responder_major_rebid'
        call.description = 'Responder rebids 2H after 1C-1H-1S with long hearts and signoff values.'
        call.system_notes = 'After 1C-1H-1S, 2H is natural and non-forcing, usually six or more hearts.'

        call = self.call('cs_56')
        call.when = '1CP1HP1NP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2H'
        call.applies = cs_56_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'signoff']
        call.meaning.action = 'responder_major_rebid'
        call.meaning.target_suit = 'H'
        call.meaning.shown_length_min = 6
        effect = call.effect('responder.length.H', owner='responder')
        effect.min_value = 6
        effect.source = 'responder_major_rebid'
        effect = call.effect('responder.hcp', owner='responder')
        effect.max_value = 10
        effect.source = 'responder_major_rebid'
        call.description = 'Responder rebids 2H after 1C-1H-1N with long hearts and signoff values.'
        call.system_notes = 'After 1C-1H-1N, 2H is natural and non-forcing, usually six or more hearts.'

        call = self.call('cs_57')
        call.when = '1DP1HP1SP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2H'
        call.applies = cs_57_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'signoff']
        call.meaning.action = 'responder_major_rebid'
        call.meaning.target_suit = 'H'
        call.meaning.shown_length_min = 6
        effect = call.effect('responder.length.H', owner='responder')
        effect.min_value = 6
        effect.source = 'responder_major_rebid'
        effect = call.effect('responder.hcp', owner='responder')
        effect.max_value = 10
        effect.source = 'responder_major_rebid'
        call.description = 'Responder rebids 2H after 1D-1H-1S with long hearts and signoff values.'
        call.system_notes = 'After 1D-1H-1S, 2H is natural and non-forcing, usually six or more hearts.'

        call = self.call('cs_58')
        call.when = '1DP1HP1NP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2H'
        call.applies = cs_58_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'signoff']
        call.meaning.action = 'responder_major_rebid'
        call.meaning.target_suit = 'H'
        call.meaning.shown_length_min = 6
        effect = call.effect('responder.length.H', owner='responder')
        effect.min_value = 6
        effect.source = 'responder_major_rebid'
        effect = call.effect('responder.hcp', owner='responder')
        effect.max_value = 10
        effect.source = 'responder_major_rebid'
        call.description = 'Responder rebids 2H after 1D-1H-1N with long hearts and signoff values.'
        call.system_notes = 'After 1D-1H-1N, 2H is natural and non-forcing, usually six or more hearts.'

        call = self.call('cs_59')
        call.when = '1CP1SP1NP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2S'
        call.applies = cs_59_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'signoff']
        call.meaning.action = 'responder_major_rebid'
        call.meaning.target_suit = 'S'
        call.meaning.shown_length_min = 6
        effect = call.effect('responder.length.S', owner='responder')
        effect.min_value = 6
        effect.source = 'responder_major_rebid'
        effect = call.effect('responder.hcp', owner='responder')
        effect.max_value = 10
        effect.source = 'responder_major_rebid'
        call.description = 'Responder rebids 2S after 1C-1S-1N with long spades and signoff values.'
        call.system_notes = 'After 1C-1S-1N, 2S is natural and non-forcing, usually six or more spades.'

        call = self.call('cs_60')
        call.when = '1DP1SP1NP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2S'
        call.applies = cs_60_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'signoff']
        call.meaning.action = 'responder_major_rebid'
        call.meaning.target_suit = 'S'
        call.meaning.shown_length_min = 6
        effect = call.effect('responder.length.S', owner='responder')
        effect.min_value = 6
        effect.source = 'responder_major_rebid'
        effect = call.effect('responder.hcp', owner='responder')
        effect.max_value = 10
        effect.source = 'responder_major_rebid'
        call.description = 'Responder rebids 2S after 1D-1S-1N with long spades and signoff values.'
        call.system_notes = 'After 1D-1S-1N, 2S is natural and non-forcing, usually six or more spades.'

        call = self.call('cs_3')
        call.when = '1CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '1D'
        call.applies = cs_3_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'one_level_response'
        call.meaning.target_suit = 'D'
        call.meaning.shown_length_min = 4
        effect = call.effect('one_level_response')
        effect.target_suit = 'D'
        effect.shown_length_min = 4
        effect = call.effect('responder.length.D', owner='responder')
        effect.min_value = 4
        effect.source = 'one_level_response'
        call.description = 'Responds 1D to 1C with four or more diamonds. The profile policy uses Walsh-style judgment when responder also holds a major.'
        call.system_notes = 'After 1C, 1D is natural. One-level major responses may bypass diamonds with less than game-forcing values.'

        call = self.call('cs_4')
        call.when = '1CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '1H'
        call.applies = cs_4_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'one_level_response'
        call.meaning.target_suit = 'H'
        call.meaning.shown_length_min = 4
        effect = call.effect('one_level_response')
        effect.target_suit = 'H'
        effect.shown_length_min = 4
        effect = call.effect('responder.length.H', owner='responder')
        effect.min_value = 4
        effect.source = 'one_level_response'
        call.description = 'Responds 1H to a minor opening with at least four hearts; with 4-4 majors, hearts are bid first.'
        call.system_notes = 'After one of a minor, 1H shows hearts and may bypass diamonds after 1C.'

        call = self.call('cs_5')
        call.when = '1CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '1S'
        call.applies = cs_5_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'one_level_response'
        call.meaning.target_suit = 'S'
        call.meaning.shown_length_min = 4
        effect = call.effect('one_level_response')
        effect.target_suit = 'S'
        effect.shown_length_min = 4
        effect = call.effect('responder.length.S', owner='responder')
        effect.min_value = 4
        effect.source = 'one_level_response'
        call.description = 'Responds 1S to 1C with at least four spades; with 5S4H, spades are bid first.'
        call.system_notes = 'After 1C, 1S shows spades and may bypass diamonds.'

        call = self.call('cs_6')
        call.when = '1DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '1H'
        call.applies = cs_6_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'one_level_response'
        call.meaning.target_suit = 'H'
        call.meaning.shown_length_min = 4
        effect = call.effect('one_level_response')
        effect.target_suit = 'H'
        effect.shown_length_min = 4
        effect = call.effect('responder.length.H', owner='responder')
        effect.min_value = 4
        effect.source = 'one_level_response'
        call.description = 'Responds 1H to 1D with at least four hearts; with 4-4 majors, hearts are bid first.'
        call.system_notes = 'After 1D, 1H shows hearts.'

        call = self.call('cs_7')
        call.when = '1DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '1S'
        call.applies = cs_7_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'one_level_response'
        call.meaning.target_suit = 'S'
        call.meaning.shown_length_min = 4
        effect = call.effect('one_level_response')
        effect.target_suit = 'S'
        effect.shown_length_min = 4
        effect = call.effect('responder.length.S', owner='responder')
        effect.min_value = 4
        effect.source = 'one_level_response'
        call.description = 'Responds 1S to a 1D opening with at least four spades.'
        call.system_notes = 'After 1D, 1S shows spades.'

        call = self.call('cs_8')
        call.when = '1CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '1N'
        call.applies = cs_8_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'notrump_response'
        call.meaning.hcp_range = [6, 10]
        effect = call.effect('notrump_response')
        effect.hcp_min = 6
        effect.hcp_max = 10
        call.description = 'Responds 1N to 1C with 6-10 balanced-ish values and no four-card major.'
        call.system_notes = 'After 1C, 1N shows about 6-10 HCP and denies a four-card major.'

        call = self.call('cs_9')
        call.when = '1DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '1N'
        call.applies = cs_9_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'notrump_response'
        call.meaning.hcp_range = [6, 10]
        effect = call.effect('notrump_response')
        effect.hcp_min = 6
        effect.hcp_max = 10
        call.description = 'Responds 1N to 1D with 6-10 balanced-ish values and no four-card major.'
        call.system_notes = 'After 1D, 1N shows about 6-10 HCP and denies a four-card major.'

        call = self.call('cs_10')
        call.when = '1CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2N'
        call.applies = cs_10_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'invitational']
        call.meaning.action = 'notrump_response'
        call.meaning.hcp_range = [11, 12]
        effect = call.effect('notrump_response')
        effect.hcp_min = 11
        effect.hcp_max = 12
        call.description = 'Responds 2N to a minor opening with 11-12 balanced values and no four-card major.'
        call.system_notes = 'After one of a minor, 2N shows about 11-12 HCP balanced.'

        call = self.call('cs_11')
        call.when = '1DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2N'
        call.applies = cs_11_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'invitational']
        call.meaning.action = 'notrump_response'
        call.meaning.hcp_range = [11, 12]
        effect = call.effect('notrump_response')
        effect.hcp_min = 11
        effect.hcp_max = 12
        call.description = 'Responds 2N to 1D with 11-12 balanced values and no four-card major.'
        call.system_notes = 'After 1D, 2N shows about 11-12 HCP balanced.'

        call = self.call('cs_12')
        call.when = '1CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3N'
        call.applies = cs_12_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'N'
        call.meaning.level = 3
        call.meaning.hcp_range = [13, 15]
        effect = call.effect('final_contract')
        effect.target_suit = 'N'
        effect.level = 3
        effect.source = 'minor_notrump_response'
        call.description = 'Responds 3N to a minor opening with 13-15 balanced values and no four-card major.'
        call.system_notes = 'After one of a minor, 3N shows about 13-15 HCP balanced.'

        call = self.call('cs_13')
        call.when = '1DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3N'
        call.applies = cs_13_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'N'
        call.meaning.level = 3
        call.meaning.hcp_range = [13, 15]
        effect = call.effect('final_contract')
        effect.target_suit = 'N'
        effect.level = 3
        effect.source = 'minor_notrump_response'
        call.description = 'Responds 3N to 1D with 13-15 balanced values and no four-card major.'
        call.system_notes = 'After 1D, 3N shows about 13-15 HCP balanced.'

        call = self.call('cs_14')
        call.when = '1CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2H'
        call.applies = cs_14_applies
        call.meaning.nature = ['natural', 'weak']
        call.meaning.acts = ['descriptive', 'preemptive']
        call.meaning.action = 'weak_jump_shift'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.shown_length_min = 6
        effect = call.effect('weak_jump_shift')
        effect.target_suit = 'H'
        effect.shown_length_min = 6
        call.description = 'Weak jump-shift response 2H to 1C.'
        call.system_notes = 'After 1C, 2H is weak and natural, not Soloway.'

        call = self.call('cs_15')
        call.when = '1CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2S'
        call.applies = cs_15_applies
        call.meaning.nature = ['natural', 'weak']
        call.meaning.acts = ['descriptive', 'preemptive']
        call.meaning.action = 'weak_jump_shift'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.shown_length_min = 6
        effect = call.effect('weak_jump_shift')
        effect.target_suit = 'S'
        effect.shown_length_min = 6
        call.description = 'Weak jump-shift response 2S to 1C.'
        call.system_notes = 'After 1C, 2S is weak and natural, not Soloway.'

        call = self.call('cs_16')
        call.when = '1DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2H'
        call.applies = cs_16_applies
        call.meaning.nature = ['natural', 'weak']
        call.meaning.acts = ['descriptive', 'preemptive']
        call.meaning.action = 'weak_jump_shift'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.shown_length_min = 6
        effect = call.effect('weak_jump_shift')
        effect.target_suit = 'H'
        effect.shown_length_min = 6
        call.description = 'Weak jump-shift response 2H to 1D.'
        call.system_notes = 'After 1D, 2H is weak and natural, not Soloway.'

        call = self.call('cs_17')
        call.when = '1DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2S'
        call.applies = cs_17_applies
        call.meaning.nature = ['natural', 'weak']
        call.meaning.acts = ['descriptive', 'preemptive']
        call.meaning.action = 'weak_jump_shift'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.shown_length_min = 6
        effect = call.effect('weak_jump_shift')
        effect.target_suit = 'S'
        effect.shown_length_min = 6
        call.description = 'Weak jump-shift response 2S to 1D.'
        call.system_notes = 'After 1D, 2S is weak and natural, not Soloway.'
