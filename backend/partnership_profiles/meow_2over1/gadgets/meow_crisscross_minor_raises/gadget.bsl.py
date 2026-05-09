# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_3_applies(ctx):
    return (ctx.hand.balanced == True and named_evaluator(ctx, 'eval_crisscross_stopper', target_suit='D') and named_evaluator(ctx, 'eval_crisscross_stopper', target_suit='H') and named_evaluator(ctx, 'eval_crisscross_stopper', target_suit='S'))
def cs_4_applies(ctx):
    return (ctx.state.exists('minor_raise', target_suit='C', method='crisscross'))
def cs_5_applies(ctx):
    return (ctx.hand.balanced == True and named_evaluator(ctx, 'eval_crisscross_stopper', target_suit='C') and named_evaluator(ctx, 'eval_crisscross_stopper', target_suit='H') and named_evaluator(ctx, 'eval_crisscross_stopper', target_suit='S'))
def cs_6_applies(ctx):
    return (ctx.state.exists('minor_raise', target_suit='D', method='crisscross'))
def cs_7_applies(ctx):
    return (ctx.hand.length('C') >= 5)
def cs_8_applies(ctx):
    return (ctx.hand.length('D') >= 4)
def eval_crisscross_stopper(ctx, target_suit):
    return (
        ctx.hand.contains_rank(target_suit, "A")
        or ctx.hand.contains_rank(target_suit, "K")
        or (ctx.hand.contains_rank(target_suit, "Q") and ctx.hand.length(target_suit) >= 2)
    )
def cs_1_applies(ctx):
    return (ctx.hand.hcp >= 13 and ctx.hand.length('C') >= 5 and ((ctx.hand.length('H') <= 3) and (ctx.hand.length('S') <= 3)))
def cs_2_applies(ctx):
    return (ctx.hand.hcp >= 13 and ctx.hand.length('D') >= 4 and ((ctx.hand.length('H') <= 3) and (ctx.hand.length('S') <= 3)))

class MeowCrisscrossMinorRaisesGadget(Gadget):
    id = 'meow_crisscross_minor_raises'
    namespace = 'meow_2over1'
    name = 'Meow Crisscross Minor Raises'
    version = '0.1.0'
    description = 'Crisscross game-forcing minor raises: 1C-2D shows clubs and 1D-3C shows diamonds.\n'
    author = Author('Meow Li')

    def build(self):

        evaluator = self.evaluator('eval_crisscross_stopper')
        evaluator.function = eval_crisscross_stopper
        evaluator.description = 'Stopper evaluator used by crisscross notrump continuations.'

        call = self.call('cs_3')
        call.when = '1CP2DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3N'
        call.applies = cs_3_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'N'
        call.meaning.level = 3
        effect = call.effect('final_contract')
        effect.target_suit = 'N'
        effect.level = 3
        effect.source = 'crisscross'
        call.description = 'Opener bids 3N after 1C-2D with a balanced hand and side-suit stoppers.'
        call.system_notes = 'After the game-forcing club crisscross raise, 3N is the practical notrump game when stoppers are present.'

        call = self.call('cs_4')
        call.when = '1CP2DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3C'
        call.applies = cs_4_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['support_showing']
        call.meaning.action = 'minor_fallback'
        call.meaning.target_suit = 'C'
        effect = call.effect('minor_contract_interest')
        effect.target_suit = 'C'
        effect.source = 'crisscross'
        call.description = 'Opener rebids 3C after 1C-2D when 3N is unattractive.'
        call.system_notes = 'After the game-forcing club crisscross raise, 3C keeps the auction in clubs when notrump is unattractive.'

        call = self.call('cs_7')
        call.when = '1CP2DP3CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '5C'
        call.applies = cs_7_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'C'
        call.meaning.level = 5
        effect = call.effect('final_contract')
        effect.target_suit = 'C'
        effect.level = 5
        effect.source = 'crisscross'
        call.description = 'Responder places 5C after opener declines notrump in the game-forcing club crisscross auction.'
        call.system_notes = 'After 1C-2D-3C, 5C is the practical club game when notrump is unattractive.'

        call = self.call('cs_5')
        call.when = '1DP3CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3N'
        call.applies = cs_5_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'N'
        call.meaning.level = 3
        effect = call.effect('final_contract')
        effect.target_suit = 'N'
        effect.level = 3
        effect.source = 'crisscross'
        call.description = 'Opener bids 3N after 1D-3C with a balanced hand and side-suit stoppers.'
        call.system_notes = 'After the game-forcing diamond crisscross raise, 3N is the practical notrump game when stoppers are present.'

        call = self.call('cs_6')
        call.when = '1DP3CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3D'
        call.applies = cs_6_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['support_showing']
        call.meaning.action = 'minor_fallback'
        call.meaning.target_suit = 'D'
        effect = call.effect('minor_contract_interest')
        effect.target_suit = 'D'
        effect.source = 'crisscross'
        call.description = 'Opener rebids 3D after 1D-3C when 3N is unattractive.'
        call.system_notes = 'After the game-forcing diamond crisscross raise, 3D keeps the auction in diamonds when notrump is unattractive.'

        call = self.call('cs_8')
        call.when = '1DP3CP3DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '5D'
        call.applies = cs_8_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'D'
        call.meaning.level = 5
        effect = call.effect('final_contract')
        effect.target_suit = 'D'
        effect.level = 5
        effect.source = 'crisscross'
        call.description = 'Responder places 5D after opener declines notrump in the game-forcing diamond crisscross auction.'
        call.system_notes = 'After 1D-3C-3D, 5D is the practical diamond game when notrump is unattractive.'

        call = self.call('cs_1')
        call.when = '1CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2D'
        call.applies = cs_1_applies
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['support_showing', 'game_forcing', 'context_initiating']
        call.meaning.action = 'crisscross_minor_raise'
        call.meaning.target_suit = 'C'
        call.meaning.alertable = True
        call.meaning.raise_strength = 'game_force'
        effect = call.effect('minor_raise')
        effect.target_suit = 'C'
        effect.strength = 'game_force'
        effect.method = 'crisscross'
        effect = call.effect('agreed_suit')
        effect.suit = 'C'
        effect.source = 'crisscross'
        effect = call.effect('forcing_status')
        effect.status = 'game_forcing'
        effect.target_suit = 'C'
        call.description = 'Crisscross raise 1C-2D: game-forcing club support, no four-card major.'
        call.system_notes = 'After 1C, 2D is a game-forcing crisscross raise showing clubs.'

        call = self.call('cs_2')
        call.when = '1DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3C'
        call.applies = cs_2_applies
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['support_showing', 'game_forcing', 'context_initiating']
        call.meaning.action = 'crisscross_minor_raise'
        call.meaning.target_suit = 'D'
        call.meaning.alertable = True
        call.meaning.raise_strength = 'game_force'
        effect = call.effect('minor_raise')
        effect.target_suit = 'D'
        effect.strength = 'game_force'
        effect.method = 'crisscross'
        effect = call.effect('agreed_suit')
        effect.suit = 'D'
        effect.source = 'crisscross'
        effect = call.effect('forcing_status')
        effect.status = 'game_forcing'
        effect.target_suit = 'D'
        call.description = 'Crisscross raise 1D-3C: game-forcing diamond support, no four-card major.'
        call.system_notes = 'After 1D, 3C is a game-forcing crisscross raise showing diamonds.'
