# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_1_requires(ctx):
    return ctx.state.exists('notrump_focus', status='active')
def cs_1_applies(ctx):
    return (ctx.hand.length('S') >= 6 and ctx.hand.hcp >= 10)
def cs_2_requires(ctx):
    return ctx.state.exists('texas_transfer', target_suit='S', status='pending')
def cs_2_applies(ctx):
    return (ctx.state.exists('texas_transfer', target_suit='S', status='pending'))
def cs_3_requires(ctx):
    return ctx.state.exists('notrump_focus', status='active')
def cs_3_applies(ctx):
    return (ctx.hand.length('H') >= 6 and ctx.hand.hcp >= 10)
def cs_4_requires(ctx):
    return ctx.state.exists('texas_transfer', target_suit='H', status='pending')
def cs_4_applies(ctx):
    return (ctx.state.exists('texas_transfer', target_suit='H', status='pending'))
def cs_5_requires(ctx):
    return ctx.state.exists('texas_transfer', target_suit='H', status='completed')
def cs_5_applies(ctx):
    return (ctx.state.exists('texas_transfer', target_suit='H', status='completed'))
def cs_6_requires(ctx):
    return ctx.state.exists('texas_transfer', target_suit='S', status='completed')
def cs_6_applies(ctx):
    return (ctx.state.exists('texas_transfer', target_suit='S', status='completed'))

class MeowTexasTransfersOver1nGadget(Gadget):
    id = 'meow_texas_transfers_over_1n'
    namespace = 'meow_2over1'
    name = 'Meow Texas Transfers Over 1N'
    version = '0.1.0'
    description = 'Standalone Texas transfer Gadget over 1N. Texas creates transfer and agreed suit state; slam methods such as RKCB are separate Gadgets.\n'
    author = Author('Meow Li')

    def build(self):

        call = self.call('cs_1')
        call.when = '1NP'
        call.seats = [1, 2, 3, 4]
        call.bid = '4H'
        call.requires = cs_1_requires
        call.applies = cs_1_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['directive', 'context_initiating', 'forcing']
        call.meaning.action = 'texas_transfer'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        effect = call.effect('texas_transfer')
        effect.target_suit = 'S'
        effect.status = 'pending'
        call.description = 'Responder bids 4H as Texas transfer to spades.'
        call.system_notes = 'After 1N, 4H is Texas transfer to spades.'

        call = self.call('cs_2')
        call.when = '1NP4HP'
        call.seats = [1, 2, 3, 4]
        call.bid = '4S'
        call.requires = cs_2_requires
        call.applies = cs_2_applies
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['directive', 'context_setting']
        call.meaning.action = 'texas_completion'
        call.meaning.target_suit = 'S'
        effect = call.effect('texas_transfer')
        effect.target_suit = 'S'
        effect.status = 'completed'
        effect = call.effect('agreed_suit')
        effect.suit = 'S'
        effect.source = 'texas_transfer'
        call.description = 'Opener completes the Texas transfer to spades.'
        call.system_notes = 'After 1N-4H, 4S completes the Texas transfer.'

        call = self.call('cs_3')
        call.when = '1NP'
        call.seats = [1, 2, 3, 4]
        call.bid = '4D'
        call.requires = cs_3_requires
        call.applies = cs_3_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['directive', 'context_initiating', 'forcing']
        call.meaning.action = 'texas_transfer'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        effect = call.effect('texas_transfer')
        effect.target_suit = 'H'
        effect.status = 'pending'
        call.description = 'Responder bids 4D as Texas transfer to hearts.'
        call.system_notes = 'After 1N, 4D is Texas transfer to hearts.'

        call = self.call('cs_4')
        call.when = '1NP4DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '4H'
        call.requires = cs_4_requires
        call.applies = cs_4_applies
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['directive', 'context_setting']
        call.meaning.action = 'texas_completion'
        call.meaning.target_suit = 'H'
        effect = call.effect('texas_transfer')
        effect.target_suit = 'H'
        effect.status = 'completed'
        effect = call.effect('agreed_suit')
        effect.suit = 'H'
        effect.source = 'texas_transfer'
        call.description = 'Opener completes the Texas transfer to hearts.'
        call.system_notes = 'After 1N-4D, 4H completes the Texas transfer.'

        call = self.call('cs_5')
        call.when = '1NP4DP4HP'
        call.seats = [1, 2, 3, 4]
        call.bid = 'P'
        call.requires = cs_5_requires
        call.applies = cs_5_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['signoff', 'final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'H'
        call.meaning.level = 4
        effect = call.effect('final_contract')
        effect.target_suit = 'H'
        effect.level = 4
        effect.source = 'texas_transfer'
        call.description = 'Responder passes after the Texas heart transfer is completed, placing 4H.'
        call.system_notes = 'After 1N-4D-4H, pass places the heart game unless responder has slam interest.'

        call = self.call('cs_6')
        call.when = '1NP4HP4SP'
        call.seats = [1, 2, 3, 4]
        call.bid = 'P'
        call.requires = cs_6_requires
        call.applies = cs_6_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['signoff', 'final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'S'
        call.meaning.level = 4
        effect = call.effect('final_contract')
        effect.target_suit = 'S'
        effect.level = 4
        effect.source = 'texas_transfer'
        call.description = 'Responder passes after the Texas spade transfer is completed, placing 4S.'
        call.system_notes = 'After 1N-4H-4S, pass places the spade game unless responder has slam interest.'
