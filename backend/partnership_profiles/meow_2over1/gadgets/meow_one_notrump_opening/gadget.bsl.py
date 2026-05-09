# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_1_applies(ctx):
    return ((ctx.hand.hcp >= 15 and ctx.hand.hcp <= 17) and ctx.hand.balanced == True)

class MeowOneNotrumpOpeningGadget(Gadget):
    id = 'meow_one_notrump_opening'
    namespace = 'meow_2over1'
    name = 'Meow 1N Opening'
    version = '0.1.0'
    description = 'Standalone 1N opening Gadget for the Meow 2/1 benchmark. Response structures such as Stayman, transfers, Texas, and Puppet Stayman are separate Gadgets that consume the notrump semantic state created here.\n'
    author = Author('Meow Li')

    def build(self):

        call = self.call('cs_1')
        call.seats = [1, 2, 3, 4]
        call.bid = '1N'
        call.applies = cs_1_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'context_initiating']
        call.meaning.action = 'opening'
        call.meaning.target_suit = 'N'
        call.meaning.hcp_min = 15
        call.meaning.hcp_max = 17
        call.meaning.shape_class = 'balanced'
        effect = call.effect('notrump_opening')
        effect.actor_role = 'opener'
        effect.target_suit = 'N'
        effect.hcp_min = 15
        effect.hcp_max = 17
        effect.shape_class = 'balanced'
        effect = call.effect('notrump_focus')
        effect.status = 'active'
        call.description = 'Opens 1N with 15-17 HCP and balanced shape.'
        call.system_notes = '1N opening shows 15-17 HCP and balanced shape.'
