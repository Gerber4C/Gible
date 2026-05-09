# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_1_applies(ctx):
    return (ctx.hand.length('S') >= 4 and ctx.hand.hcp >= 13)
def cs_2_applies(ctx):
    return (ctx.hand.length('H') >= 4 and ctx.hand.hcp >= 13)
def opener_jacoby_minimum_no_shortness(ctx, trump_suit):
    return ctx.hand.hcp <= 14 and not opener_has_side_shortness(ctx, trump_suit)
def opener_jacoby_extras_no_shortness(ctx, trump_suit):
    return ctx.hand.hcp >= 15 and not opener_has_side_shortness(ctx, trump_suit)
def opener_jacoby_shortness(ctx, short_suit):
    return ctx.hand.length(short_suit) <= 1
def opener_has_side_shortness(ctx, trump_suit):
    return any(ctx.hand.length(suit) <= 1 for suit in ('S', 'H', 'D', 'C') if suit != trump_suit)
def responder_places_game_after_jacoby(ctx, trump_suit):
    return not (ctx.hand.hcp >= 18 and ctx.hand.length(trump_suit) >= 5)

class MeowJacoby2ntMajorRaiseGadget(Gadget):
    id = 'meow_jacoby_2nt_major_raise'
    namespace = 'meow_2over1'
    name = 'Meow Jacoby 2N Major Raise'
    version = '0.1.0'
    description = 'Standalone Jacoby 2N major-raise Gadget. Opener continuation structure is intentionally separate from Bergen and Drury.\n'
    author = Author('Meow Li')

    def build(self):

        call = self.call('cs_1')
        call.when = '1SP'
        call.seats = [1, 2]
        call.bid = '2N'
        call.applies = cs_1_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['context_initiating', 'forcing']
        call.meaning.action = 'jacoby_2n'
        call.meaning.target_suit = 'S'
        call.meaning.forcing = 'game_forcing'
        call.meaning.alertable = True
        effect = call.effect('agreed_suit')
        effect.suit = 'S'
        effect.source = 'jacoby_2n'
        effect = call.effect('forcing_status')
        effect.status = 'game_forcing'
        call.description = 'Jacoby 2N game-forcing spade raise declaration.'
        call.system_notes = 'After 1S, 2N is Jacoby 2N, game forcing with four-card support.'

        call = self.call('cs_2')
        call.when = '1HP'
        call.seats = [1, 2]
        call.bid = '2N'
        call.applies = cs_2_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['context_initiating', 'forcing']
        call.meaning.action = 'jacoby_2n'
        call.meaning.target_suit = 'H'
        call.meaning.forcing = 'game_forcing'
        call.meaning.alertable = True
        effect = call.effect('agreed_suit')
        effect.suit = 'H'
        effect.source = 'jacoby_2n'
        effect = call.effect('forcing_status')
        effect.status = 'game_forcing'
        call.description = 'Jacoby 2N game-forcing heart raise declaration.'
        call.system_notes = 'After 1H, 2N is Jacoby 2N, game forcing with four-card support.'

        for suit in ('S', 'H'):
            opening = '1' + suit
            signoff = '4' + suit
            extras = '3' + suit

            for short_suit, short_call in _jacoby_shortness_calls(suit):
                call = self.call(f'{suit.lower()}_jacoby_short_{short_suit.lower()}')
                call.when = f'{opening}P2NP'
                call.seats = [1, 2]
                call.bid = short_call
                call.applies = lambda ctx, short_suit=short_suit: opener_jacoby_shortness(ctx, short_suit)
                call.meaning.nature = ['artificial', 'conventional']
                call.meaning.acts = ['descriptive', 'forcing']
                call.meaning.action = 'jacoby_shortness_response'
                call.meaning.target_suit = suit
                call.meaning.short_suit = short_suit
                call.meaning.alertable = True
                effect = call.effect('opener.shortness', owner='opener')
                effect.suit = short_suit
                effect.max_value = 1
                effect.source = 'jacoby_2n'
                effect = call.effect(f'opener.length.{short_suit}', owner='opener')
                effect.max_value = 1
                effect.source = 'jacoby_2n'
                call.description = f'Opener shows {short_suit} shortness after Jacoby 2N for {suit}.'
                call.system_notes = f'After {opening}-2N, {short_call} shows shortness in {short_suit}.'

            call = self.call(f'{suit.lower()}_jacoby_extras_no_shortness')
            call.when = f'{opening}P2NP'
            call.seats = [1, 2]
            call.bid = extras
            call.applies = lambda ctx, suit=suit: opener_jacoby_extras_no_shortness(ctx, suit)
            call.meaning.nature = ['natural']
            call.meaning.acts = ['descriptive', 'forcing']
            call.meaning.action = 'jacoby_extras_no_shortness'
            call.meaning.target_suit = suit
            call.meaning.level = 3
            effect = call.effect('opener.extra_values', owner='opener')
            effect.status = 'yes'
            effect.source = 'jacoby_2n'
            call.description = f'Opener rebids {extras} after Jacoby 2N to show extras without side shortness.'
            call.system_notes = f'After {opening}-2N, {extras} shows extras without side shortness.'

            call = self.call(f'{suit.lower()}_jacoby_minimum_signoff')
            call.when = f'{opening}P2NP'
            call.seats = [1, 2]
            call.bid = signoff
            call.applies = lambda ctx, suit=suit: opener_jacoby_minimum_no_shortness(ctx, suit)
            call.meaning.nature = ['natural']
            call.meaning.acts = ['final_placement']
            call.meaning.action = 'jacoby_minimum_game'
            call.meaning.target_suit = suit
            call.meaning.level = 4
            effect = call.effect('final_contract', owner='partnership')
            effect.target_suit = suit
            effect.level = 4
            effect.source = 'jacoby_2n'
            call.description = f'Opener signs off in {signoff} after Jacoby 2N with a minimum and no side shortness.'
            call.system_notes = f'After {opening}-2N, {signoff} shows a minimum without side shortness.'

            for continuation in _jacoby_responder_placement_calls(suit):
                call = self.call(f'{suit.lower()}_jacoby_after_{continuation.lower()}_place_game')
                call.when = f'{opening}P2NP{continuation}P'
                call.seats = [1, 2]
                call.bid = signoff
                call.applies = lambda ctx, suit=suit: responder_places_game_after_jacoby(ctx, suit)
                call.meaning.nature = ['natural']
                call.meaning.acts = ['final_placement']
                call.meaning.action = 'place_contract'
                call.meaning.target_suit = suit
                call.meaning.level = 4
                effect = call.effect('final_contract', owner='partnership')
                effect.target_suit = suit
                effect.level = 4
                effect.source = 'jacoby_2n'
                call.description = f'Responder places {signoff} after opener continuation {continuation} in the Jacoby 2N dialogue.'
                call.system_notes = f'After {opening}-2N-{continuation}, {signoff} is to play unless responder continues toward slam.'


def _jacoby_shortness_calls(trump_suit):
    if trump_suit == 'S':
        return (('C', '3C'), ('D', '3D'), ('H', '3H'))
    return (('C', '3C'), ('D', '3D'), ('S', '3S'))


def _jacoby_responder_placement_calls(trump_suit):
    if trump_suit == 'S':
        return ('3C', '3D', '3H', '3S')
    return ('3C', '3D', '3H', '3S')
