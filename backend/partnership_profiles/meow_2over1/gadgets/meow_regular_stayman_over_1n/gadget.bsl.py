# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_1_requires(ctx):
    return ctx.state.exists('notrump_focus', status='active')
def cs_1_applies(ctx):
    return (ctx.hand.hcp >= 8 and ((ctx.hand.length('H') >= 4) or (ctx.hand.length('S') >= 4)))
def cs_2_requires(ctx):
    return ctx.state.exists('stayman', status='pending')
def cs_2_applies(ctx):
    return (((ctx.hand.length('H') < 4) and (ctx.hand.length('S') < 4)))
def cs_3_requires(ctx):
    return ctx.state.exists('stayman_response', status='no_major')
def cs_3_applies(ctx):
    return ((ctx.hand.hcp >= 8 and ctx.hand.hcp <= 9))

class MeowRegularStaymanOver1nGadget(Gadget):
    id = 'meow_regular_stayman_over_1n'
    namespace = 'meow_2over1'
    name = 'Meow Regular Stayman Over 1N'
    version = '0.1.0'
    description = 'Regular Stayman over a 1N opening. Puppet Stayman is a separate Gadget.\n'
    author = Author('Meow Li')

    def build(self):

        call = self.call('cs_1')
        call.when = '1NP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2C'
        call.requires = cs_1_requires
        call.applies = cs_1_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['inquiry', 'context_initiating']
        call.meaning.action = 'stayman'
        call.meaning.alertable = True
        effect = call.effect('stayman')
        effect.status = 'pending'
        call.description = 'Responder bids Stayman over 1N.'
        call.system_notes = 'After 1N, 2C is regular Stayman.'

        call = self.call('cs_2')
        call.when = '1NP2CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2D'
        call.requires = cs_2_requires
        call.applies = cs_2_applies
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'stayman_response'
        call.meaning.denies_four_card_major = True
        effect = call.effect('stayman_response')
        effect.status = 'no_major'
        call.description = 'Opener denies a four-card major after regular Stayman.'
        call.system_notes = 'After regular Stayman, 2D denies a four-card major in this benchmark slice.'

        call = self.call('cs_3')
        call.when = '1NP2CP2DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2N'
        call.requires = cs_3_requires
        call.applies = cs_3_applies
        call.meaning.nature = ['natural', 'conventional']
        call.meaning.acts = ['invitation']
        call.meaning.action = 'notrump_invitation'
        call.meaning.alertable = True
        call.meaning.acbl_explanation = 'may or may not have a four-card major'
        call.description = 'Responder rebids 2N as the invitational regular-Stayman route.'
        call.system_notes = "After Stayman and opener's response, 2N is invitational and may or may not include a four-card major."
