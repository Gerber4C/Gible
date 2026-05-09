# Partner Python-BSL source.
# This file defines one class-authored Gadget.


def responder_places_major_game_after_ogust(ctx, target_suit):
    return ctx.hand.length(target_suit) >= 2 and ctx.hand.hcp >= 14


def responder_signs_off_after_ogust(ctx, target_suit):
    return ctx.hand.length(target_suit) >= 2 and ctx.hand.hcp <= 15


def responder_places_diamond_game_after_ogust(ctx):
    return ctx.hand.length('D') >= 3 and ctx.hand.hcp >= 16


def responder_signs_off_diamonds_after_ogust(ctx):
    return ctx.hand.length('D') >= 3 and ctx.hand.hcp <= 15


def responder_passes_ogust_answer_in_suit(ctx):
    return True


class MeowOgustPlacementGadget(Gadget):
    id = 'meow_ogust_placement'
    namespace = 'meow_2over1'
    name = 'Meow Ogust Placement'
    version = '0.1.0'
    description = 'Responder placement after weak-two Ogust answers. The asking hand chooses signoff or game from the answer and its own support.'
    system_notes = 'After a weak-two Ogust answer, responder places the contract: signoff in three of the preempt suit with invitational values, or game with enough combined strength.'
    author = Author('Meow Li')

    def build(self):

        major_answer_sets = {
            'H': ('3C', '3D', '3H', '3S', '3N'),
            'S': ('3C', '3D', '3H', '3S', '3N'),
        }
        for suit, answers in major_answer_sets.items():
            opening = '2' + suit
            signoff = '3' + suit
            game = '4' + suit
            for answer in answers:
                if answer != signoff:
                    call = self.call(f'{opening.lower()}_{answer.lower()}_signoff_{signoff.lower()}')
                    call.when = f'{opening}P2NP{answer}P'
                    call.bid = signoff
                    call.applies = lambda ctx, target_suit=suit: responder_signs_off_after_ogust(ctx, target_suit)
                    call.meaning.nature = ['natural']
                    call.meaning.acts = ['final_placement']
                    call.meaning.action = 'ogust_signoff'
                    call.meaning.target_suit = suit
                    call.meaning.level = 3
                    effect = call.effect('final_contract', owner='partnership')
                    effect.target_suit = suit
                    effect.level = 3
                    effect.source = 'ogust_placement'
                    call.description = f'After {opening}-2N-{answer}, responder signs off in {signoff}.'
                    call.system_notes = f'After {opening}-2N-{answer}, {signoff} is to play when responder declines game.'

                call = self.call(f'{opening.lower()}_{answer.lower()}_game_{game.lower()}')
                call.when = f'{opening}P2NP{answer}P'
                call.bid = game
                call.applies = lambda ctx, target_suit=suit: responder_places_major_game_after_ogust(ctx, target_suit)
                call.meaning.nature = ['natural']
                call.meaning.acts = ['final_placement']
                call.meaning.action = 'place_contract'
                call.meaning.target_suit = suit
                call.meaning.level = 4
                effect = call.effect('final_contract', owner='partnership')
                effect.target_suit = suit
                effect.level = 4
                effect.source = 'ogust_placement'
                call.description = f'After {opening}-2N-{answer}, responder places game in {game}.'
                call.system_notes = f'After {opening}-2N-{answer}, {game} is to play when responder accepts game.'

                if answer == signoff:
                    call = self.call(f'{opening.lower()}_{answer.lower()}_pass')
                    call.when = f'{opening}P2NP{answer}P'
                    call.bid = 'P'
                    call.applies = responder_passes_ogust_answer_in_suit
                    call.meaning.nature = ['natural']
                    call.meaning.acts = ['final_placement']
                    call.meaning.action = 'pass_final_contract'
                    call.meaning.target_suit = suit
                    call.meaning.level = 3
                    effect = call.effect('final_contract', owner='partnership')
                    effect.target_suit = suit
                    effect.level = 3
                    effect.source = 'ogust_placement'
                    call.description = f'After {opening}-2N-{answer}, responder may pass because the answer is already {signoff}.'
                    call.system_notes = f'After {opening}-2N-{answer}, pass signs off in {signoff}.'

        for answer in ('3C', '3D', '3H', '3S', '3N'):
            if answer != '3D':
                call = self.call(f'2d_{answer.lower()}_signoff_3d')
                call.when = f'2DP2NP{answer}P'
                call.bid = '3D'
                call.applies = responder_signs_off_diamonds_after_ogust
                call.meaning.nature = ['natural']
                call.meaning.acts = ['final_placement']
                call.meaning.action = 'ogust_signoff'
                call.meaning.target_suit = 'D'
                call.meaning.level = 3
                effect = call.effect('final_contract', owner='partnership')
                effect.target_suit = 'D'
                effect.level = 3
                effect.source = 'ogust_placement'
                call.description = f'After 2D-2N-{answer}, responder signs off in 3D.'
                call.system_notes = f'After 2D-2N-{answer}, 3D is to play when responder declines game.'

            call = self.call(f'2d_{answer.lower()}_game_5d')
            call.when = f'2DP2NP{answer}P'
            call.bid = '5D'
            call.applies = responder_places_diamond_game_after_ogust
            call.meaning.nature = ['natural']
            call.meaning.acts = ['final_placement']
            call.meaning.action = 'place_contract'
            call.meaning.target_suit = 'D'
            call.meaning.level = 5
            effect = call.effect('final_contract', owner='partnership')
            effect.target_suit = 'D'
            effect.level = 5
            effect.source = 'ogust_placement'
            call.description = f'After 2D-2N-{answer}, responder places diamond game.'
            call.system_notes = f'After 2D-2N-{answer}, 5D is to play with game-going values.'

            if answer == '3D':
                call = self.call('2d_3d_pass')
                call.when = '2DP2NP3DP'
                call.bid = 'P'
                call.applies = responder_passes_ogust_answer_in_suit
                call.meaning.nature = ['natural']
                call.meaning.acts = ['final_placement']
                call.meaning.action = 'pass_final_contract'
                call.meaning.target_suit = 'D'
                call.meaning.level = 3
                effect = call.effect('final_contract', owner='partnership')
                effect.target_suit = 'D'
                effect.level = 3
                effect.source = 'ogust_placement'
                call.description = 'After 2D-2N-3D, responder may pass because the answer is already 3D.'
                call.system_notes = 'After 2D-2N-3D, pass signs off in diamonds.'
