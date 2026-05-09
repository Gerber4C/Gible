# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def sp_1_applies(ctx):
    return (ctx.hand.hcp >= 11)
def sp_2_applies(ctx):
    return (ctx.hand.hcp >= 11)
def sp_3_applies(ctx):
    return (ctx.hand.hcp >= 11)
def sp_4_applies(ctx):
    return (ctx.hand.hcp >= 11)
def sp_5_applies(ctx):
    return (12 <= ctx.hand.hcp <= 14 and ctx.hand.length('H') == 3)
def sp_6_applies(ctx):
    return (ctx.hand.hcp >= 15 and ctx.hand.length('H') == 3)
def sp_7_applies(ctx):
    return (12 <= ctx.hand.hcp <= 14 and ctx.hand.length('H') >= 4)
def sp_8_applies(ctx):
    return (ctx.hand.hcp >= 15 and ctx.hand.length('H') >= 4)
def sp_9_applies(ctx):
    return (12 <= ctx.hand.hcp <= 14 and ctx.hand.length('S') == 3)
def sp_10_applies(ctx):
    return (ctx.hand.hcp >= 15 and ctx.hand.length('S') == 3)
def sp_11_applies(ctx):
    return (12 <= ctx.hand.hcp <= 14 and ctx.hand.length('S') >= 4)
def sp_12_applies(ctx):
    return (ctx.hand.hcp >= 15 and ctx.hand.length('S') >= 4)
def sp_13_applies(ctx):
    return (ctx.hand.hcp >= 13 and ctx.hand.length('H') >= 5)
def sp_14_applies(ctx):
    return (ctx.hand.hcp >= 13 and ctx.hand.length('S') >= 5)
def sp_15_applies(ctx):
    return (12 <= ctx.hand.hcp <= 14 and ctx.hand.length('H') == 3)
def sp_16_applies(ctx):
    return (ctx.hand.hcp >= 15 and ctx.hand.length('H') == 3)
def sp_17_applies(ctx):
    return (12 <= ctx.hand.hcp <= 14 and ctx.hand.length('H') >= 4)
def sp_18_applies(ctx):
    return (ctx.hand.hcp >= 15 and ctx.hand.length('H') >= 4)
def sp_19_applies(ctx):
    return (12 <= ctx.hand.hcp <= 14 and ctx.hand.length('S') == 3)
def sp_20_applies(ctx):
    return (ctx.hand.hcp >= 15 and ctx.hand.length('S') == 3)
def sp_21_applies(ctx):
    return (12 <= ctx.hand.hcp <= 14 and ctx.hand.length('S') >= 4)
def sp_22_applies(ctx):
    return (ctx.hand.hcp >= 15 and ctx.hand.length('S') >= 4)

class MeowSpiral3344Gadget(Gadget):
    id = 'meow_spiral_3344'
    namespace = 'meow_2over1'
    name = 'Meow Spiral 3344'
    version = '0.1.0'
    description = 'Rodwell-style 3344 inquiry after opener raises responder major in a one-minor auction.'
    system_notes = 'After 1m-P-1M-P-2M-P, 2N asks whether opener has three or four-card support and minimum or maximum values. Responses are 3C=min with three, 3D=max with three, 3H=min with four, 3S=max with four.'
    author = Author('Meow Li')

    def build(self):

        call = self.call('sp_1')
        call.when = '1CP1HP2HP'
        call.bid = '2N'
        call.applies = sp_1_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['inquiry']
        call.meaning.action = 'spiral_3344_query'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        effect = call.effect('spiral_3344_query', owner='responder')
        effect.target_suit = 'H'
        effect.status = 'pending'
        call.description = 'Responder asks whether opener raised hearts with three or four-card support and minimum or maximum values.'

        call = self.call('sp_2')
        call.when = '1CP1SP2SP'
        call.bid = '2N'
        call.applies = sp_2_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['inquiry']
        call.meaning.action = 'spiral_3344_query'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        effect = call.effect('spiral_3344_query', owner='responder')
        effect.target_suit = 'S'
        effect.status = 'pending'

        call = self.call('sp_3')
        call.when = '1DP1HP2HP'
        call.bid = '2N'
        call.applies = sp_3_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['inquiry']
        call.meaning.action = 'spiral_3344_query'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        effect = call.effect('spiral_3344_query', owner='responder')
        effect.target_suit = 'H'
        effect.status = 'pending'

        call = self.call('sp_4')
        call.when = '1DP1SP2SP'
        call.bid = '2N'
        call.applies = sp_4_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['inquiry']
        call.meaning.action = 'spiral_3344_query'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        effect = call.effect('spiral_3344_query', owner='responder')
        effect.target_suit = 'S'
        effect.status = 'pending'

        call = self.call('sp_5')
        call.when = '1CP1HP2HP2NP'
        call.bid = '3C'
        call.applies = sp_5_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'spiral_3344_answer'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.support_length = 3
        call.meaning.opener_strength = 'minimum'
        effect = call.effect('spiral_3344_answer', owner='opener')
        effect.target_suit = 'H'
        effect.support_length = 3
        effect.opener_strength = 'minimum'

        call = self.call('sp_6')
        call.when = '1CP1HP2HP2NP'
        call.bid = '3D'
        call.applies = sp_6_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'spiral_3344_answer'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.support_length = 3
        call.meaning.opener_strength = 'maximum'
        effect = call.effect('spiral_3344_answer', owner='opener')
        effect.target_suit = 'H'
        effect.support_length = 3
        effect.opener_strength = 'maximum'

        call = self.call('sp_7')
        call.when = '1CP1HP2HP2NP'
        call.bid = '3H'
        call.applies = sp_7_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'spiral_3344_answer'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.support_length = 4
        call.meaning.opener_strength = 'minimum'
        effect = call.effect('spiral_3344_answer', owner='opener')
        effect.target_suit = 'H'
        effect.support_length = 4
        effect.opener_strength = 'minimum'

        call = self.call('sp_8')
        call.when = '1CP1HP2HP2NP'
        call.bid = '3S'
        call.applies = sp_8_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'spiral_3344_answer'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.support_length = 4
        call.meaning.opener_strength = 'maximum'
        effect = call.effect('spiral_3344_answer', owner='opener')
        effect.target_suit = 'H'
        effect.support_length = 4
        effect.opener_strength = 'maximum'

        call = self.call('sp_9')
        call.when = '1CP1SP2SP2NP'
        call.bid = '3C'
        call.applies = sp_9_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'spiral_3344_answer'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.support_length = 3
        call.meaning.opener_strength = 'minimum'
        effect = call.effect('spiral_3344_answer', owner='opener')
        effect.target_suit = 'S'
        effect.support_length = 3
        effect.opener_strength = 'minimum'

        call = self.call('sp_10')
        call.when = '1CP1SP2SP2NP'
        call.bid = '3D'
        call.applies = sp_10_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'spiral_3344_answer'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.support_length = 3
        call.meaning.opener_strength = 'maximum'
        effect = call.effect('spiral_3344_answer', owner='opener')
        effect.target_suit = 'S'
        effect.support_length = 3
        effect.opener_strength = 'maximum'

        call = self.call('sp_11')
        call.when = '1CP1SP2SP2NP'
        call.bid = '3H'
        call.applies = sp_11_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'spiral_3344_answer'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.support_length = 4
        call.meaning.opener_strength = 'minimum'
        effect = call.effect('spiral_3344_answer', owner='opener')
        effect.target_suit = 'S'
        effect.support_length = 4
        effect.opener_strength = 'minimum'

        call = self.call('sp_12')
        call.when = '1CP1SP2SP2NP'
        call.bid = '3S'
        call.applies = sp_12_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'spiral_3344_answer'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.support_length = 4
        call.meaning.opener_strength = 'maximum'
        effect = call.effect('spiral_3344_answer', owner='opener')
        effect.target_suit = 'S'
        effect.support_length = 4
        effect.opener_strength = 'maximum'

        call = self.call('sp_13')
        call.when = '1CP1HP2HP2NP3DP'
        call.bid = '4H'
        call.applies = sp_13_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'H'
        call.meaning.level = 4
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'H'
        effect.level = 4
        effect.source = 'spiral_3344'

        call = self.call('sp_14')
        call.when = '1CP1SP2SP2NP3HP'
        call.bid = '4S'
        call.applies = sp_14_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'S'
        call.meaning.level = 4
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'S'
        effect.level = 4
        effect.source = 'spiral_3344'

        call = self.call('sp_15')
        call.when = '1DP1HP2HP2NP'
        call.bid = '3C'
        call.applies = sp_15_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'spiral_3344_answer'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.support_length = 3
        call.meaning.opener_strength = 'minimum'
        effect = call.effect('spiral_3344_answer', owner='opener')
        effect.target_suit = 'H'
        effect.support_length = 3
        effect.opener_strength = 'minimum'

        call = self.call('sp_16')
        call.when = '1DP1HP2HP2NP'
        call.bid = '3D'
        call.applies = sp_16_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'spiral_3344_answer'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.support_length = 3
        call.meaning.opener_strength = 'maximum'
        effect = call.effect('spiral_3344_answer', owner='opener')
        effect.target_suit = 'H'
        effect.support_length = 3
        effect.opener_strength = 'maximum'

        call = self.call('sp_17')
        call.when = '1DP1HP2HP2NP'
        call.bid = '3H'
        call.applies = sp_17_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'spiral_3344_answer'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.support_length = 4
        call.meaning.opener_strength = 'minimum'
        effect = call.effect('spiral_3344_answer', owner='opener')
        effect.target_suit = 'H'
        effect.support_length = 4
        effect.opener_strength = 'minimum'

        call = self.call('sp_18')
        call.when = '1DP1HP2HP2NP'
        call.bid = '3S'
        call.applies = sp_18_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'spiral_3344_answer'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.support_length = 4
        call.meaning.opener_strength = 'maximum'
        effect = call.effect('spiral_3344_answer', owner='opener')
        effect.target_suit = 'H'
        effect.support_length = 4
        effect.opener_strength = 'maximum'

        call = self.call('sp_19')
        call.when = '1DP1SP2SP2NP'
        call.bid = '3C'
        call.applies = sp_19_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'spiral_3344_answer'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.support_length = 3
        call.meaning.opener_strength = 'minimum'
        effect = call.effect('spiral_3344_answer', owner='opener')
        effect.target_suit = 'S'
        effect.support_length = 3
        effect.opener_strength = 'minimum'

        call = self.call('sp_20')
        call.when = '1DP1SP2SP2NP'
        call.bid = '3D'
        call.applies = sp_20_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'spiral_3344_answer'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.support_length = 3
        call.meaning.opener_strength = 'maximum'
        effect = call.effect('spiral_3344_answer', owner='opener')
        effect.target_suit = 'S'
        effect.support_length = 3
        effect.opener_strength = 'maximum'

        call = self.call('sp_21')
        call.when = '1DP1SP2SP2NP'
        call.bid = '3H'
        call.applies = sp_21_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'spiral_3344_answer'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.support_length = 4
        call.meaning.opener_strength = 'minimum'
        effect = call.effect('spiral_3344_answer', owner='opener')
        effect.target_suit = 'S'
        effect.support_length = 4
        effect.opener_strength = 'minimum'

        call = self.call('sp_22')
        call.when = '1DP1SP2SP2NP'
        call.bid = '3S'
        call.applies = sp_22_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'spiral_3344_answer'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.support_length = 4
        call.meaning.opener_strength = 'maximum'
        effect = call.effect('spiral_3344_answer', owner='opener')
        effect.target_suit = 'S'
        effect.support_length = 4
        effect.opener_strength = 'maximum'
