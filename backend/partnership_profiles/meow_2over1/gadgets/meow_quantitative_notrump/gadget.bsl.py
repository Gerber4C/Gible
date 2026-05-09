# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_1_requires(ctx):
    if not ctx.state.exists('notrump_focus', status='active'):
        return False
    if ctx.state.exists('agreed_suit') or ctx.state.exists('final_contract'):
        return False
    for procedure in ('transfer', 'texas_transfer', 'stayman', 'puppet_stayman'):
        if ctx.state.exists(procedure, status='pending'):
            return False
        if ctx.state.exists(procedure, status='active'):
            return False
    return True
def cs_1_applies(ctx):
    return ((ctx.hand.hcp >= 16 and ctx.hand.hcp <= 17) and ctx.hand.balanced == True)

class MeowQuantitativeNotrumpGadget(Gadget):
    id = 'meow_quantitative_notrump'
    namespace = 'meow_2over1'
    name = 'Meow Quantitative Notrump'
    version = '0.1.0'
    description = 'Quantitative notrump raises when notrump focus is active and no suit is agreed.'
    author = Author('Meow Li')

    def build(self):

        call = self.call('cs_1')
        call.when = '*'
        call.bid = '4N'
        call.requires = cs_1_requires
        call.applies = cs_1_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['invitation']
        call.meaning.action = 'quantitative_notrump_invite'
        call.meaning.target_suit = 'N'
        call.meaning.level = 4
        effect = call.effect('quantitative_notrump_invite')
        effect.target_suit = 'N'
        effect.level = 4
        effect.status = 'pending'
        call.description = 'Responder bids 4N as a quantitative notrump slam invitation.'
        call.system_notes = 'With notrump focus and no agreed suit, 4N is quantitative.'
