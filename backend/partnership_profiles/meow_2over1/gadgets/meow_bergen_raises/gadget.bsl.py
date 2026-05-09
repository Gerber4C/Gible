# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_1_applies(ctx):
    return (ctx.hand.length('S') >= 4 and (ctx.hand.hcp >= 7 and ctx.hand.hcp <= 9))
def cs_2_applies(ctx):
    return (ctx.hand.length('S') >= 4 and (ctx.hand.hcp >= 10 and ctx.hand.hcp <= 12))
def cs_3_applies(ctx):
    return (ctx.hand.length('S') >= 4 and (ctx.hand.hcp >= 0 and ctx.hand.hcp <= 6))
def cs_4_applies(ctx):
    return (ctx.hand.length('H') >= 4 and (ctx.hand.hcp >= 7 and ctx.hand.hcp <= 9))
def cs_5_applies(ctx):
    return (ctx.hand.length('H') >= 4 and (ctx.hand.hcp >= 10 and ctx.hand.hcp <= 12))
def cs_6_applies(ctx):
    return (ctx.hand.length('H') >= 4 and (ctx.hand.hcp >= 0 and ctx.hand.hcp <= 6))
def opener_declines_constructive_bergen(ctx):
    return ctx.hand.hcp <= 15
def opener_accepts_constructive_bergen(ctx):
    return ctx.hand.hcp >= 16
def opener_declines_limit_bergen(ctx):
    return ctx.hand.hcp <= 13
def opener_accepts_limit_bergen(ctx):
    return ctx.hand.hcp >= 14
def opener_passes_preemptive_bergen(ctx):
    return ctx.hand.hcp <= 17
def opener_accepts_preemptive_bergen(ctx):
    return ctx.hand.hcp >= 18

class MeowBergenRaisesGadget(Gadget):
    id = 'meow_bergen_raises'
    namespace = 'meow_2over1'
    name = 'Meow Bergen Raises'
    version = '0.1.0'
    description = 'Standalone Bergen raise Gadget by an unpassed responder after first- or second-seat major openings.\n'
    author = Author('Meow Li')

    def build(self):

        call = self.call('cs_1')
        call.when = '1SP'
        call.seats = [1, 2]
        call.bid = '3C'
        call.applies = cs_1_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'bergen_raise'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.raise_strength = 'constructive'
        effect = call.effect('agreed_suit')
        effect.suit = 'S'
        effect.source = 'bergen_raise'
        effect = call.effect('major_raise')
        effect.suit = 'S'
        effect.raise_type = 'bergen_constructive'
        call.description = 'Normal Bergen 3C constructive four-card spade raise.'
        call.system_notes = 'After 1S, 3C is a constructive four-card Bergen raise.'

        call = self.call('cs_2')
        call.when = '1SP'
        call.seats = [1, 2]
        call.bid = '3D'
        call.applies = cs_2_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['descriptive', 'invitation']
        call.meaning.action = 'bergen_raise'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.raise_strength = 'limit'
        effect = call.effect('agreed_suit')
        effect.suit = 'S'
        effect.source = 'bergen_raise'
        effect = call.effect('major_raise')
        effect.suit = 'S'
        effect.raise_type = 'bergen_limit'
        call.description = 'Normal Bergen 3D limit four-card spade raise.'
        call.system_notes = 'After 1S, 3D is a limit four-card Bergen raise.'

        call = self.call('cs_3')
        call.when = '1SP'
        call.seats = [1, 2]
        call.bid = '3S'
        call.applies = cs_3_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['preemptive']
        call.meaning.action = 'bergen_raise'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.raise_strength = 'preemptive'
        effect = call.effect('agreed_suit')
        effect.suit = 'S'
        effect.source = 'bergen_raise'
        effect = call.effect('major_raise')
        effect.suit = 'S'
        effect.raise_type = 'bergen_preemptive'
        call.description = 'Normal Bergen 3S preemptive four-card spade raise.'
        call.system_notes = 'After 1S, 3S is a preemptive four-card Bergen raise.'

        call = self.call('cs_4')
        call.when = '1HP'
        call.seats = [1, 2]
        call.bid = '3C'
        call.applies = cs_4_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'bergen_raise'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.raise_strength = 'constructive'
        effect = call.effect('agreed_suit')
        effect.suit = 'H'
        effect.source = 'bergen_raise'
        effect = call.effect('major_raise')
        effect.suit = 'H'
        effect.raise_type = 'bergen_constructive'
        call.description = 'Normal Bergen 3C constructive four-card heart raise.'
        call.system_notes = 'After 1H, 3C is a constructive four-card Bergen raise.'

        call = self.call('cs_5')
        call.when = '1HP'
        call.seats = [1, 2]
        call.bid = '3D'
        call.applies = cs_5_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['descriptive', 'invitation']
        call.meaning.action = 'bergen_raise'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.raise_strength = 'limit'
        effect = call.effect('agreed_suit')
        effect.suit = 'H'
        effect.source = 'bergen_raise'
        effect = call.effect('major_raise')
        effect.suit = 'H'
        effect.raise_type = 'bergen_limit'
        call.description = 'Normal Bergen 3D limit four-card heart raise.'
        call.system_notes = 'After 1H, 3D is a limit four-card Bergen raise.'

        call = self.call('cs_6')
        call.when = '1HP'
        call.seats = [1, 2]
        call.bid = '3H'
        call.applies = cs_6_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['preemptive']
        call.meaning.action = 'bergen_raise'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.raise_strength = 'preemptive'
        effect = call.effect('agreed_suit')
        effect.suit = 'H'
        effect.source = 'bergen_raise'
        effect = call.effect('major_raise')
        effect.suit = 'H'
        effect.raise_type = 'bergen_preemptive'
        call.description = 'Normal Bergen 3H preemptive four-card heart raise.'
        call.system_notes = 'After 1H, 3H is a preemptive four-card Bergen raise.'

        for suit in ('S', 'H'):
            opening = '1' + suit
            signoff = '3' + suit
            game = '4' + suit

            for response, strength, decline_fn, accept_fn in (
                ('3C', 'constructive', opener_declines_constructive_bergen, opener_accepts_constructive_bergen),
                ('3D', 'limit', opener_declines_limit_bergen, opener_accepts_limit_bergen),
            ):
                call = self.call(f'{suit.lower()}_bergen_{strength}_decline')
                call.when = f'{opening}P{response}P'
                call.seats = [1, 2]
                call.bid = signoff
                call.applies = decline_fn
                call.meaning.nature = ['natural']
                call.meaning.acts = ['final_placement']
                call.meaning.action = 'bergen_decline'
                call.meaning.target_suit = suit
                call.meaning.raise_strength = strength
                call.meaning.level = 3
                effect = call.effect('final_contract', owner='partnership')
                effect.target_suit = suit
                effect.level = 3
                effect.source = 'bergen_raise'
                call.description = f'Opener declines the {strength} Bergen raise by signing off in {signoff}.'
                call.system_notes = f'After {opening}-{response}, {signoff} declines the {strength} Bergen raise.'

                call = self.call(f'{suit.lower()}_bergen_{strength}_accept')
                call.when = f'{opening}P{response}P'
                call.seats = [1, 2]
                call.bid = game
                call.applies = accept_fn
                call.meaning.nature = ['natural']
                call.meaning.acts = ['final_placement']
                call.meaning.action = 'bergen_accept_game'
                call.meaning.target_suit = suit
                call.meaning.raise_strength = strength
                call.meaning.level = 4
                effect = call.effect('final_contract', owner='partnership')
                effect.target_suit = suit
                effect.level = 4
                effect.source = 'bergen_raise'
                call.description = f'Opener accepts the {strength} Bergen raise by bidding {game}.'
                call.system_notes = f'After {opening}-{response}, {game} accepts the {strength} Bergen raise.'

            call = self.call(f'{suit.lower()}_bergen_preemptive_pass')
            call.when = f'{opening}P{signoff}P'
            call.seats = [1, 2]
            call.bid = 'P'
            call.applies = opener_passes_preemptive_bergen
            call.meaning.nature = ['natural']
            call.meaning.acts = ['final_placement']
            call.meaning.action = 'pass_final_contract'
            call.meaning.target_suit = suit
            call.meaning.raise_strength = 'preemptive'
            call.meaning.level = 3
            effect = call.effect('final_contract', owner='partnership')
            effect.target_suit = suit
            effect.level = 3
            effect.source = 'bergen_raise'
            call.description = f'Opener passes the preemptive Bergen raise in {signoff}.'
            call.system_notes = f'After {opening}-{signoff}, pass accepts the preemptive Bergen raise as final.'

            call = self.call(f'{suit.lower()}_bergen_preemptive_accept')
            call.when = f'{opening}P{signoff}P'
            call.seats = [1, 2]
            call.bid = game
            call.applies = opener_accepts_preemptive_bergen
            call.meaning.nature = ['natural']
            call.meaning.acts = ['final_placement']
            call.meaning.action = 'bergen_accept_game'
            call.meaning.target_suit = suit
            call.meaning.raise_strength = 'preemptive'
            call.meaning.level = 4
            effect = call.effect('final_contract', owner='partnership')
            effect.target_suit = suit
            effect.level = 4
            effect.source = 'bergen_raise'
            call.description = f'Opener accepts the preemptive Bergen raise with enough playing strength by bidding {game}.'
            call.system_notes = f'After {opening}-{signoff}, {game} accepts the preemptive Bergen raise.'
