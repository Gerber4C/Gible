# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_1_applies(ctx):
    return (ctx.hand.hcp >= 18)
def cs_7_applies(ctx):
    return (22 <= ctx.hand.hcp <= 24)
def cs_8_applies(ctx):
    return (ctx.hand.hcp >= 17 and ctx.hand.length('H') >= 5)
def cs_9_applies(ctx):
    return (ctx.hand.hcp >= 17 and ctx.hand.length('S') >= 5)
def cs_10_applies(ctx):
    return (ctx.hand.hcp >= 17 and ctx.hand.length('C') >= 5)
def cs_11_applies(ctx):
    return (ctx.hand.hcp >= 17 and ctx.hand.length('D') >= 5)
def cs_12_applies(ctx):
    return (ctx.hand.hcp >= 25)
def cs_13_applies(ctx):
    return (ctx.hand.hcp <= 3)
def cs_14_applies(ctx):
    return (ctx.hand.hcp <= 3)
def cs_15_applies(ctx):
    return (ctx.hand.hcp <= 3)
def cs_16_applies(ctx):
    return (ctx.hand.hcp <= 3)
def cs_17_applies(ctx):
    return (ctx.hand.hcp <= 2)
def cs_18_applies(ctx):
    return (ctx.hand.hcp >= 3)
def cs_19_applies(ctx):
    return (ctx.hand.length('H') >= 5)
def cs_20_applies(ctx):
    return (ctx.hand.length('S') >= 5)
def cs_21_applies(ctx):
    return (ctx.hand.length('C') >= 4 and ctx.hand.length('D') >= 4)
def cs_22_applies(ctx):
    return (ctx.hand.hcp >= 3)
def cs_23_applies(ctx):
    return (ctx.hand.length('H') >= 6 and ctx.hand.hcp <= 19)
def cs_24_applies(ctx):
    return (ctx.hand.length('H') >= 6 and ctx.hand.hcp >= 20)
def cs_25_applies(ctx):
    return (ctx.hand.length('S') >= 6 and ctx.hand.hcp <= 19)
def cs_26_applies(ctx):
    return (ctx.hand.length('S') >= 6 and ctx.hand.hcp >= 20)
def cs_2_applies(ctx):
    return (True)

class MeowStrongTwoClubGadget(Gadget):
    id = 'meow_strong_two_club'
    namespace = 'meow_2over1'
    name = 'Meow Strong 2C Opening'
    version = '0.1.0'
    description = 'Strong artificial 2C opening structure with 2D waiting, natural rebids, second negative, and notrump continuations.'
    author = Author('Meow Li')

    def build(self):

        call = self.call('cs_1')
        call.seats = [1, 2, 3, 4]
        call.bid = '2C'
        call.applies = cs_1_applies
        call.meaning.nature = ['artificial', 'strong', 'forcing']
        call.meaning.acts = ['descriptive', 'context_initiating']
        call.meaning.action = 'strong_two_club_opening'
        call.meaning.target_suit = 'C'
        call.meaning.style = '22+ balanced or game-forcing unbalanced'
        effect = call.effect('strong_two_club_opening', owner='opener')
        effect.status = 'active'
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 18
        effect = call.effect('forcing_status', owner='partnership')
        effect.status = 'forcing'
        call.description = 'Artificial strong 2C opening. The profile policy admits 22+ balanced hands and game-forcing unbalanced hands.'
        call.system_notes = '2C opening is artificial, strong, and forcing. It covers balanced hands above the direct 2N opening range and unbalanced hands too strong to risk a one-level opening being passed out.'

        call = self.call('cs_7')
        call.when = '2C P 2D P'
        call.seats = [1, 2, 3, 4]
        call.bid = '2N'
        call.applies = cs_7_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'context_initiating']
        call.meaning.action = 'strong_two_club_notrump_rebid'
        call.meaning.target_suit = 'N'
        call.meaning.hcp_min = 22
        call.meaning.hcp_max = 24
        call.meaning.shape_class = 'balanced_or_semibalanced'
        effect = call.effect('notrump_opening', owner='opener')
        effect.target_suit = 'N'
        effect.hcp_min = 22
        effect.hcp_max = 24
        effect.shape_class = 'balanced_or_semibalanced'
        effect = call.effect('notrump_focus')
        effect.status = 'active'
        effect.source = 'strong_two_club'
        effect = call.effect('opener.hcp', owner='opener')
        effect.min_value = 22
        effect.max_value = 24
        call.description = 'After 2C-2D, opener rebids 2N with 22-24 balanced or near-balanced shape.'
        call.system_notes = "After 2C-2D, opener's 2N rebid shows 22-24 balanced or near-balanced shape. Notrump continuations are system-on with adjusted ranges."

        call = self.call('cs_8')
        call.when = '2C P 2D P'
        call.seats = [1, 2, 3, 4]
        call.bid = '2H'
        call.applies = cs_8_applies
        call.meaning.nature = ['natural', 'forcing']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'strong_two_club_suit_rebid'
        call.meaning.target_suit = 'H'
        call.meaning.shown_length_min = 5
        effect = call.effect('strong_two_club_rebid', owner='opener')
        effect.target_suit = 'H'
        effect = call.effect('opener.length.H', owner='opener')
        effect.min_value = 5
        call.description = 'After 2C-2D, opener rebids 2H naturally with a strong heart hand.'
        call.system_notes = 'After 2C-2D, 2H is natural and forcing for at least one round.'

        call = self.call('cs_9')
        call.when = '2C P 2D P'
        call.seats = [1, 2, 3, 4]
        call.bid = '2S'
        call.applies = cs_9_applies
        call.meaning.nature = ['natural', 'forcing']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'strong_two_club_suit_rebid'
        call.meaning.target_suit = 'S'
        call.meaning.shown_length_min = 5
        effect = call.effect('strong_two_club_rebid', owner='opener')
        effect.target_suit = 'S'
        effect = call.effect('opener.length.S', owner='opener')
        effect.min_value = 5
        call.description = 'After 2C-2D, opener rebids 2S naturally with a strong spade hand.'
        call.system_notes = 'After 2C-2D, 2S is natural and forcing for at least one round.'

        call = self.call('cs_10')
        call.when = '2C P 2D P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3C'
        call.applies = cs_10_applies
        call.meaning.nature = ['natural', 'forcing']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'strong_two_club_suit_rebid'
        call.meaning.target_suit = 'C'
        call.meaning.shown_length_min = 5
        effect = call.effect('strong_two_club_rebid', owner='opener')
        effect.target_suit = 'C'
        effect = call.effect('opener.length.C', owner='opener')
        effect.min_value = 5
        call.description = 'After 2C-2D, opener rebids 3C naturally with a strong club hand.'
        call.system_notes = 'After 2C-2D, 3C is natural and forcing for at least one round.'

        call = self.call('cs_11')
        call.when = '2C P 2D P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3D'
        call.applies = cs_11_applies
        call.meaning.nature = ['natural', 'forcing']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'strong_two_club_suit_rebid'
        call.meaning.target_suit = 'D'
        call.meaning.shown_length_min = 5
        effect = call.effect('strong_two_club_rebid', owner='opener')
        effect.target_suit = 'D'
        effect = call.effect('opener.length.D', owner='opener')
        effect.min_value = 5
        call.description = 'After 2C-2D, opener rebids 3D naturally with a strong diamond hand.'
        call.system_notes = 'After 2C-2D, 3D is natural and forcing for at least one round.'

        call = self.call('cs_12')
        call.when = '2C P 2D P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3N'
        call.applies = cs_12_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'final_placement']
        call.meaning.action = 'strong_two_club_three_notrump_rebid'
        call.meaning.target_suit = 'N'
        call.meaning.hcp_min = 25
        call.meaning.hcp_max = 27
        call.meaning.shape_class = 'balanced_or_semibalanced'
        effect = call.effect('notrump_opening', owner='opener')
        effect.target_suit = 'N'
        effect.hcp_min = 25
        effect.hcp_max = 27
        effect.shape_class = 'balanced_or_semibalanced'
        effect = call.effect('notrump_focus')
        effect.status = 'active'
        effect.source = 'strong_two_club'
        effect = call.effect('final_contract', owner='partnership')
        effect.level = 3
        effect.target_suit = 'N'
        effect.source = 'strong_two_club'
        call.description = 'After 2C-2D, opener rebids 3N with 25-27 balanced or near-balanced shape.'
        call.system_notes = 'After 2C-2D, 3N shows a balanced or near-balanced hand too strong for a 2N rebid.'

        call = self.call('cs_13')
        call.when = '2C P 2D P 2H P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3C'
        call.applies = cs_13_applies
        call.meaning.nature = ['artificial', 'negative']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'strong_two_club_second_negative'
        effect = call.effect('strong_two_club_second_negative', owner='responder')
        effect = call.effect('responder.hcp', owner='responder')
        effect.max_value = 3
        call.description = 'Second negative after 2C-2D-2H.'
        call.system_notes = "After 2C-2D and opener's 2H rebid, 3C is the second negative."

        call = self.call('cs_14')
        call.when = '2C P 2D P 2S P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3C'
        call.applies = cs_14_applies
        call.meaning.nature = ['artificial', 'negative']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'strong_two_club_second_negative'
        effect = call.effect('strong_two_club_second_negative', owner='responder')
        effect = call.effect('responder.hcp', owner='responder')
        effect.max_value = 3
        call.description = 'Second negative after 2C-2D-2S.'
        call.system_notes = "After 2C-2D and opener's 2S rebid, 3C is the second negative."

        call = self.call('cs_15')
        call.when = '2C P 2D P 3C P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3D'
        call.applies = cs_15_applies
        call.meaning.nature = ['artificial', 'negative']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'strong_two_club_second_negative'
        effect = call.effect('strong_two_club_second_negative', owner='responder')
        effect = call.effect('responder.hcp', owner='responder')
        effect.max_value = 3
        call.description = 'Second negative after 2C-2D-3C.'
        call.system_notes = "After 2C-2D and opener's 3C rebid, 3D is the second negative."

        call = self.call('cs_16')
        call.when = '2C P 2D P 3D P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3N'
        call.applies = cs_16_applies
        call.meaning.nature = ['artificial', 'negative']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'strong_two_club_second_negative'
        effect = call.effect('strong_two_club_second_negative', owner='responder')
        effect = call.effect('responder.hcp', owner='responder')
        effect.max_value = 3
        call.description = 'Second negative after 2C-2D-3D when no cheaper minor is available at the three level.'
        call.system_notes = "After 2C-2D and opener's 3D rebid, 3N is the second negative in this benchmark."

        call = self.call('cs_23')
        call.when = '2CP2DP2HP3CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3H'
        call.applies = cs_23_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'strong_two_club_major_rebid_after_negative'
        call.meaning.target_suit = 'H'
        effect = call.effect('opener.length.H', owner='opener')
        effect.min_value = 6
        effect.source = 'strong_two_club_after_second_negative'
        call.description = 'After a second negative, opener rebids 3H with a strong but not self-placing heart hand.'
        call.system_notes = 'After 2C-2D-2H-3C, 3H is natural and shows at least six hearts without forcing game opposite a bust.'

        call = self.call('cs_24')
        call.when = '2CP2DP2HP3CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '4H'
        call.applies = cs_24_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'H'
        call.meaning.level = 4
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'H'
        effect.level = 4
        effect.source = 'strong_two_club_after_second_negative'
        call.description = 'After a second negative, opener places 4H with enough playing strength opposite a bust.'
        call.system_notes = 'After 2C-2D-2H-3C, 4H is to play with a heart hand strong enough to insist on game.'

        call = self.call('cs_25')
        call.when = '2CP2DP2SP3CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3S'
        call.applies = cs_25_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'strong_two_club_major_rebid_after_negative'
        call.meaning.target_suit = 'S'
        effect = call.effect('opener.length.S', owner='opener')
        effect.min_value = 6
        effect.source = 'strong_two_club_after_second_negative'
        call.description = 'After a second negative, opener rebids 3S with a strong but not self-placing spade hand.'
        call.system_notes = 'After 2C-2D-2S-3C, 3S is natural and shows at least six spades without forcing game opposite a bust.'

        call = self.call('cs_26')
        call.when = '2CP2DP2SP3CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '4S'
        call.applies = cs_26_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'S'
        call.meaning.level = 4
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'S'
        effect.level = 4
        effect.source = 'strong_two_club_after_second_negative'
        call.description = 'After a second negative, opener places 4S with enough playing strength opposite a bust.'
        call.system_notes = 'After 2C-2D-2S-3C, 4S is to play with a spade hand strong enough to insist on game.'

        call = self.call('cs_17')
        call.when = '2C P 2D P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = 'P'
        call.applies = cs_17_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'pass_notrump'
        call.meaning.target_suit = 'N'
        call.meaning.level = 2
        effect = call.effect('final_contract', owner='partnership')
        effect.level = 2
        effect.target_suit = 'N'
        effect.source = 'strong_two_club'
        call.description = 'Responder may pass 2N with a true bust after 2C-2D-2N.'
        call.system_notes = 'After 2C-2D-2N, pass is available with a true bust.'

        call = self.call('cs_18')
        call.when = '2C P 2D P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3C'
        call.applies = cs_18_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['inquiry', 'context_initiating', 'forcing']
        call.meaning.action = 'puppet_stayman'
        call.meaning.alertable = True
        effect = call.effect('puppet_stayman')
        effect.notrump_level = 2
        effect.status = 'pending'
        effect.source = 'strong_two_club'
        call.description = 'Puppet Stayman after 2C-2D-2N.'
        call.system_notes = 'After 2C-2D-2N, 3C is Puppet Stayman, system-on over the 22-24 notrump rebid.'

        call = self.call('cs_19')
        call.when = '2C P 2D P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3D'
        call.applies = cs_19_applies
        call.meaning.nature = ['artificial', 'transfer']
        call.meaning.acts = ['relay', 'context_initiating']
        call.meaning.action = 'transfer'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        effect = call.effect('pending_transfer', owner='responder')
        effect.target_suit = 'H'
        effect.accept_call = '3H'
        effect.source = 'strong_two_club'
        call.description = 'Transfer to hearts after 2C-2D-2N.'
        call.system_notes = 'After 2C-2D-2N, 3D transfers to hearts.'

        call = self.call('cs_20')
        call.when = '2C P 2D P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3H'
        call.applies = cs_20_applies
        call.meaning.nature = ['artificial', 'transfer']
        call.meaning.acts = ['relay', 'context_initiating']
        call.meaning.action = 'transfer'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        effect = call.effect('pending_transfer', owner='responder')
        effect.target_suit = 'S'
        effect.accept_call = '3S'
        effect.source = 'strong_two_club'
        call.description = 'Transfer to spades after 2C-2D-2N.'
        call.system_notes = 'After 2C-2D-2N, 3H transfers to spades.'

        call = self.call('cs_21')
        call.when = '2C P 2D P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3S'
        call.applies = cs_21_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['inquiry', 'forcing']
        call.meaning.action = 'minor_suit_stayman'
        call.meaning.alertable = True
        effect = call.effect('minor_suit_stayman')
        effect.status = 'pending'
        effect.source = 'strong_two_club'
        call.description = 'Minor suit Stayman after 2C-2D-2N.'
        call.system_notes = 'After 2C-2D-2N, 3S is minor suit Stayman.'

        call = self.call('cs_22')
        call.when = '2C P 2D P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3N'
        call.applies = cs_22_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'N'
        call.meaning.level = 3
        effect = call.effect('final_contract', owner='partnership')
        effect.level = 3
        effect.target_suit = 'N'
        effect.source = 'strong_two_club'
        call.description = 'Natural 3N after 2C-2D-2N.'
        call.system_notes = 'After 2C-2D-2N, 3N is natural to play when responder has game values and no useful inquiry.'

        call = self.call('cs_2')
        call.when = '2C P'
        call.seats = [1, 2, 3, 4]
        call.bid = '2D'
        call.applies = cs_2_applies
        call.meaning.nature = ['artificial', 'waiting']
        call.meaning.acts = ['relay', 'forcing']
        call.meaning.action = 'strong_two_club_waiting'
        effect = call.effect('strong_two_club_response', owner='responder')
        effect.response_type = 'waiting'
        call.description = '2D waiting response to strong 2C.'
        call.system_notes = 'After 2C, 2D is waiting. This benchmark does not use immediate positive suit responses.'
