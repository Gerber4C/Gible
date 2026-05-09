# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_1_applies(ctx):
    return ((ctx.hand.length('S') == 3) and (ctx.hand.hcp >= 10 and ctx.hand.hcp <= 12))
def cs_2_applies(ctx):
    return (ctx.hand.length('S') >= 4 and (ctx.hand.hcp >= 10 and ctx.hand.hcp <= 12))
def cs_3_applies(ctx):
    return ((ctx.hand.length('H') == 3) and (ctx.hand.hcp >= 10 and ctx.hand.hcp <= 12))
def cs_4_applies(ctx):
    return (ctx.hand.length('H') >= 4 and (ctx.hand.hcp >= 10 and ctx.hand.hcp <= 12))
def opener_declines_drury(ctx):
    return ctx.hand.hcp <= 13
def opener_accepts_drury_game(ctx):
    return ctx.hand.hcp >= 14

class MeowTwoWayReverseDruryGadget(Gadget):
    id = 'meow_two_way_reverse_drury'
    namespace = 'meow_2over1'
    name = 'Meow Two-Way Reverse Drury'
    version = '0.1.0'
    description = 'Standalone two-way reverse Drury Gadget by a passed hand after third- or fourth-seat major openings.\n'
    author = Author('Meow Li')

    def build(self):

        call = self.call('cs_1')
        call.when = '1SP'
        call.seats = [3, 4]
        call.bid = '2C'
        call.applies = cs_1_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['descriptive', 'inquiry']
        call.meaning.action = 'two_way_reverse_drury'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.support_length = 3
        effect = call.effect('agreed_suit')
        effect.suit = 'S'
        effect.source = 'drury'
        effect = call.effect('drury')
        effect.suit = 'S'
        effect.support_length = 3
        effect.status = 'pending'
        call.description = 'Two-way reverse Drury 2C by a passed hand, showing exactly three-card support.'
        call.system_notes = 'By a passed hand after a seat 3 or 4 major opening, 2C is two-way reverse Drury with exactly three-card support.'

        call = self.call('cs_2')
        call.when = '1SP'
        call.seats = [3, 4]
        call.bid = '2D'
        call.applies = cs_2_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['descriptive', 'inquiry']
        call.meaning.action = 'two_way_reverse_drury'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.support_length_min = 4
        effect = call.effect('agreed_suit')
        effect.suit = 'S'
        effect.source = 'drury'
        effect = call.effect('drury')
        effect.suit = 'S'
        effect.support_length_min = 4
        effect.status = 'pending'
        call.description = 'Two-way reverse Drury 2D by a passed hand, showing four-card or longer support.'
        call.system_notes = 'By a passed hand after a seat 3 or 4 major opening, 2D is two-way reverse Drury with four-card or longer support.'

        call = self.call('cs_3')
        call.when = '1HP'
        call.seats = [3, 4]
        call.bid = '2C'
        call.applies = cs_3_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['descriptive', 'inquiry']
        call.meaning.action = 'two_way_reverse_drury'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.support_length = 3
        effect = call.effect('agreed_suit')
        effect.suit = 'H'
        effect.source = 'drury'
        effect = call.effect('drury')
        effect.suit = 'H'
        effect.support_length = 3
        effect.status = 'pending'
        call.description = 'Two-way reverse Drury 2C by a passed hand, showing exactly three-card heart support.'
        call.system_notes = 'By a passed hand after a seat 3 or 4 major opening, 2C is two-way reverse Drury with exactly three-card heart support.'

        call = self.call('cs_4')
        call.when = '1HP'
        call.seats = [3, 4]
        call.bid = '2D'
        call.applies = cs_4_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['descriptive', 'inquiry']
        call.meaning.action = 'two_way_reverse_drury'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.support_length_min = 4
        effect = call.effect('agreed_suit')
        effect.suit = 'H'
        effect.source = 'drury'
        effect = call.effect('drury')
        effect.suit = 'H'
        effect.support_length_min = 4
        effect.status = 'pending'
        call.description = 'Two-way reverse Drury 2D by a passed hand, showing four-card or longer heart support.'
        call.system_notes = 'By a passed hand after a seat 3 or 4 major opening, 2D is two-way reverse Drury with four-card or longer heart support.'

        for suit in ('S', 'H'):
            opening = '1' + suit
            signoff = '2' + suit
            game = '4' + suit
            for inquiry, support_text in (('2C', 'three-card support'), ('2D', 'four-card support')):
                call = self.call(f'{suit.lower()}_drury_{inquiry.lower()}_decline')
                call.when = f'{opening}P{inquiry}P'
                call.seats = [3, 4]
                call.bid = signoff
                call.applies = opener_declines_drury
                call.meaning.nature = ['natural']
                call.meaning.acts = ['final_placement']
                call.meaning.action = 'drury_decline'
                call.meaning.target_suit = suit
                call.meaning.level = 2
                effect = call.effect('final_contract', owner='partnership')
                effect.target_suit = suit
                effect.level = 2
                effect.source = 'drury'
                call.description = f'Opener signs off in {signoff} after Drury when the third- or fourth-seat opening is not worth game.'
                call.system_notes = f'After {opening}-{inquiry} Drury showing {support_text}, {signoff} declines game.'

                call = self.call(f'{suit.lower()}_drury_{inquiry.lower()}_accept')
                call.when = f'{opening}P{inquiry}P'
                call.seats = [3, 4]
                call.bid = game
                call.applies = opener_accepts_drury_game
                call.meaning.nature = ['natural']
                call.meaning.acts = ['final_placement']
                call.meaning.action = 'drury_accept_game'
                call.meaning.target_suit = suit
                call.meaning.level = 4
                effect = call.effect('final_contract', owner='partnership')
                effect.target_suit = suit
                effect.level = 4
                effect.source = 'drury'
                call.description = f'Opener accepts Drury by bidding {game} with enough strength opposite the passed-hand limit raise.'
                call.system_notes = f'After {opening}-{inquiry} Drury showing {support_text}, {game} accepts game.'
