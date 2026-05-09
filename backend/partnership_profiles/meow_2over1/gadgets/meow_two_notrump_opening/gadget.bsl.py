# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_1_applies(ctx):
    return ((ctx.hand.hcp >= 20 and ctx.hand.hcp <= 21) and ctx.hand.balanced == True)

class MeowTwoNotrumpOpeningGadget(Gadget):
    id = 'meow_two_notrump_opening'
    namespace = 'meow_2over1'
    name = 'Meow 2N Opening'
    version = '0.1.0'
    description = 'Standalone 2N opening Gadget for the Meow 2/1 benchmark. Puppet Stayman, transfers, and minor-suit Stayman over 2N are separate Gadgets.\n'
    author = Author('Meow Li')

    def build(self):

        call = self.call('cs_1')
        call.seats = [1, 2, 3, 4]
        call.bid = '2N'
        call.applies = cs_1_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'context_initiating']
        call.meaning.action = 'opening'
        call.meaning.target_suit = 'N'
        call.meaning.hcp_min = 20
        call.meaning.hcp_max = 21
        call.meaning.shape_class = 'balanced'
        effect = call.effect('notrump_opening')
        effect.actor_role = 'opener'
        effect.target_suit = 'N'
        effect.hcp_min = 20
        effect.hcp_max = 21
        effect.shape_class = 'balanced'
        effect = call.effect('notrump_focus')
        effect.status = 'active'
        call.description = 'Opens 2N with 20-21 HCP and balanced shape.'
        call.system_notes = '2N opening shows 20-21 HCP and balanced shape.'
