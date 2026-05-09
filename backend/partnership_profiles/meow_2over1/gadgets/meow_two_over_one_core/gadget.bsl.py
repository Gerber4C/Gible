# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_6_requires(ctx):
    return ctx.state.exists('final_contract')
def cs_6_applies(ctx):
    return (ctx.state.exists('final_contract'))
def cs_1_applies(ctx):
    return (ctx.hand.hcp >= 10 and ctx.hand.length('S') >= 5)
def cs_2_applies(ctx):
    return (ctx.hand.hcp >= 10 and ctx.hand.length('H') >= 5)
def cs_3_applies(ctx):
    return (ctx.hand.hcp >= 10 and ctx.hand.length('S') >= 5)
def cs_4_applies(ctx):
    return (ctx.hand.hcp >= 10 and ctx.hand.length('H') >= 5)
def cs_7_applies(ctx):
    return (True)
def cs_8_applies(ctx):
    return (True)

class MeowTwoOverOneCoreGadget(Gadget):
    id = 'meow_two_over_one_core'
    namespace = 'meow_2over1'
    name = 'Meow 2/1 Core'
    version = '0.1.0'
    description = 'Core natural opening structure for the Meow 2/1 benchmark. This slice includes natural five-card major openings, 15-17 1N, 20-21 2N, and explicit default pass behavior.\n'
    author = Author('Meow Li')

    def build(self):

        call = self.call('cs_5')
        call.when = '*'
        call.bid = 'P'
        call.default_policy = True
        call.meaning.nature = ['default']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'fallback_pass'
        call.description = 'Explicit fallback pass when no benchmark Call Specification applies.'
        call.system_notes = 'Undefined benchmark auctions currently fall back to pass with diagnostics.'

        call = self.call('cs_6')
        call.when = '*'
        call.bid = 'P'
        call.requires = cs_6_requires
        call.applies = cs_6_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'pass_final_contract'
        call.description = 'Partner passes after a final contract has been placed by any loaded benchmark Gadget.'
        call.system_notes = 'Once a final-contract state record exists, pass is the normal continuation.'

        call = self.call('cs_1')
        call.seats = [1, 2]
        call.bid = '1S'
        call.applies = cs_1_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'context_initiating']
        call.meaning.action = 'opening'
        call.meaning.target_suit = 'S'
        call.meaning.shown_length_min = 5
        effect = call.effect('major_opening')
        effect.actor_role = 'opener'
        effect.target_suit = 'S'
        effect.shown_length_min = 5
        call.description = 'Opens 1S naturally with opening values and at least five spades.'
        call.system_notes = '1S opening is natural and shows at least five spades.'

        call = self.call('cs_2')
        call.seats = [1, 2]
        call.bid = '1H'
        call.applies = cs_2_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'context_initiating']
        call.meaning.action = 'opening'
        call.meaning.target_suit = 'H'
        call.meaning.shown_length_min = 5
        effect = call.effect('major_opening')
        effect.actor_role = 'opener'
        effect.target_suit = 'H'
        effect.shown_length_min = 5
        call.description = 'Opens 1H naturally with opening values and at least five hearts.'
        call.system_notes = '1H opening is natural and shows at least five hearts.'

        call = self.call('cs_3')
        call.seats = [3, 4]
        call.bid = '1S'
        call.applies = cs_3_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'context_initiating']
        call.meaning.action = 'opening'
        call.meaning.target_suit = 'S'
        call.meaning.shown_length_min = 5
        call.meaning.seat_style = 'third_or_fourth_seat_may_be_light'
        effect = call.effect('major_opening')
        effect.actor_role = 'opener'
        effect.target_suit = 'S'
        effect.shown_length_min = 5
        effect.seat_style = 'third_or_fourth_seat_may_be_light'
        call.description = 'Opens 1S in third or fourth seat with at least five spades; the profile policy decides whether a light opening is practical.'
        call.system_notes = 'Third- and fourth-seat 1S opening is natural, at least five spades, and may be lighter by partnership style.'

        call = self.call('cs_4')
        call.seats = [3, 4]
        call.bid = '1H'
        call.applies = cs_4_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'context_initiating']
        call.meaning.action = 'opening'
        call.meaning.target_suit = 'H'
        call.meaning.shown_length_min = 5
        call.meaning.seat_style = 'third_or_fourth_seat_may_be_light'
        effect = call.effect('major_opening')
        effect.actor_role = 'opener'
        effect.target_suit = 'H'
        effect.shown_length_min = 5
        effect.seat_style = 'third_or_fourth_seat_may_be_light'
        call.description = 'Opens 1H in third or fourth seat with at least five hearts; the profile policy decides whether a light opening is practical.'
        call.system_notes = 'Third- and fourth-seat 1H opening is natural, at least five hearts, and may be lighter by partnership style.'

        call = self.call('cs_7')
        call.seats = [3, 4]
        call.bid = 'P'
        call.applies = cs_7_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'opening_pass'
        call.description = 'Explicit pass candidate for third- and fourth-seat opening judgment.'
        call.system_notes = 'In third and fourth seat, pass is an explicit opening-route choice when the profile policy judges that opening is unattractive.'

        call = self.call('cs_8')
        call.seats = [1, 2]
        call.bid = 'P'
        call.applies = cs_8_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'opening_pass'
        call.description = 'Explicit first- and second-seat pass candidate when the profile policy judges the hand unsuitable to open.'
        call.system_notes = 'In first and second seat, pass is an explicit opening-route choice when opening or preempting is unattractive.'
