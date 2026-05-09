# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_1_applies(ctx):
    return ((ctx.hand.length('S') == 3) and (ctx.hand.hcp >= 6 and ctx.hand.hcp <= 10))
def cs_2_applies(ctx):
    return ((ctx.hand.length('H') == 3) and (ctx.hand.hcp >= 6 and ctx.hand.hcp <= 10))

class MeowSimpleMajorRaiseGadget(Gadget):
    id = 'meow_simple_major_raise'
    namespace = 'meow_2over1'
    name = 'Meow Simple Major Raise'
    version = '0.1.0'
    description = 'Natural single raise of a major. Artificial major-raise methods such as Bergen, Drury, Jacoby 2N, splinters, and game tries are separate Gadgets.\n'
    author = Author('Meow Li')

    def build(self):

        call = self.call('cs_1')
        call.when = '1SP'
        call.seats = [1, 2]
        call.bid = '2S'
        call.applies = cs_1_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'simple_raise'
        call.meaning.target_suit = 'S'
        call.meaning.support_length = 3
        call.meaning.raise_strength = 'simple'
        effect = call.effect('agreed_suit')
        effect.suit = 'S'
        effect.source = 'simple_raise'
        effect = call.effect('major_raise')
        effect.suit = 'S'
        effect.raise_type = 'simple'
        call.description = 'Responder gives a simple spade raise with exactly three-card support and non-forcing values.'
        call.system_notes = 'After 1S, 2S is a natural simple raise. In this benchmark, Bergen handles four-card constructive and limit raises.'

        call = self.call('cs_2')
        call.when = '1HP'
        call.seats = [1, 2]
        call.bid = '2H'
        call.applies = cs_2_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'simple_raise'
        call.meaning.target_suit = 'H'
        call.meaning.support_length = 3
        call.meaning.raise_strength = 'simple'
        effect = call.effect('agreed_suit')
        effect.suit = 'H'
        effect.source = 'simple_raise'
        effect = call.effect('major_raise')
        effect.suit = 'H'
        effect.raise_type = 'simple'
        call.description = 'Responder gives a simple heart raise with exactly three-card support and non-forcing values.'
        call.system_notes = 'After 1H, 2H is a natural simple raise. In this benchmark, Bergen handles four-card constructive and limit raises.'
