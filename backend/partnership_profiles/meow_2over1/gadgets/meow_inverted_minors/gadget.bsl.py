# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def im_17_applies(ctx):
    return (ctx.hand.hcp >= 15 and ctx.hand.balanced == True and named_evaluator(ctx, 'eval_stopper', target_suit='D') and named_evaluator(ctx, 'eval_stopper', target_suit='H') and named_evaluator(ctx, 'eval_stopper', target_suit='S'))
def im_18_applies(ctx):
    return (ctx.hand.hcp >= 15 and ctx.hand.balanced == True and named_evaluator(ctx, 'eval_stopper', target_suit='C') and named_evaluator(ctx, 'eval_stopper', target_suit='H') and named_evaluator(ctx, 'eval_stopper', target_suit='S'))
def im_19_applies(ctx):
    return (10 <= ctx.hand.hcp <= 12 and ctx.hand.balanced == True)
def im_20_applies(ctx):
    return (10 <= ctx.hand.hcp <= 12 and ctx.hand.balanced == True)
def im_21_applies(ctx):
    return (10 <= ctx.hand.hcp <= 12 and ctx.hand.balanced == True)
def im_22_applies(ctx):
    return (ctx.hand.hcp >= 13 and ctx.hand.balanced == True)
def im_23_applies(ctx):
    return (ctx.hand.hcp >= 13 and ctx.hand.balanced == True)
def im_24_applies(ctx):
    return (ctx.hand.hcp >= 13 and ctx.hand.balanced == True)
def im_25_applies(ctx):
    return (10 <= ctx.hand.hcp <= 12 and ctx.hand.length('C') >= 5)
def im_26_applies(ctx):
    return (10 <= ctx.hand.hcp <= 12 and ctx.hand.balanced == True)
def im_27_applies(ctx):
    return (10 <= ctx.hand.hcp <= 12 and ctx.hand.balanced == True)
def im_28_applies(ctx):
    return (10 <= ctx.hand.hcp <= 12 and ctx.hand.length('D') >= 4)
def im_29_applies(ctx):
    return (ctx.hand.hcp >= 13 and ctx.hand.balanced == True)
def im_30_applies(ctx):
    return (ctx.hand.hcp >= 13 and ctx.hand.balanced == True)
def eval_stopper(ctx, target_suit):
    return (
        ctx.hand.contains_rank(target_suit, "A")
        or ctx.hand.contains_rank(target_suit, "K")
        or (ctx.hand.contains_rank(target_suit, "Q") and ctx.hand.length(target_suit) >= 2)
        or (ctx.hand.contains_rank(target_suit, "J") and ctx.hand.length(target_suit) >= 3)
    )
def cs_1_applies(ctx):
    return (ctx.hand.hcp >= 10 and ctx.hand.length('C') >= 5 and ((ctx.hand.length('H') <= 3) and (ctx.hand.length('S') <= 3)))
def cs_2_applies(ctx):
    return (ctx.hand.hcp >= 10 and ctx.hand.length('D') >= 4 and ((ctx.hand.length('H') <= 3) and (ctx.hand.length('S') <= 3)))
def cs_3_applies(ctx):
    return ((ctx.hand.hcp >= 12 and ctx.hand.hcp <= 14) and ctx.hand.balanced == True and named_evaluator(ctx, 'eval_stopper', target_suit='D') and named_evaluator(ctx, 'eval_stopper', target_suit='H') and named_evaluator(ctx, 'eval_stopper', target_suit='S'))
def cs_4_applies(ctx):
    return (named_evaluator(ctx, 'eval_stopper', target_suit='D'))
def cs_5_applies(ctx):
    return (not (ctx.state.exists('stopper', suit='D')) and named_evaluator(ctx, 'eval_stopper', target_suit='H') and not ((ctx.hand.contains_rank('D', 'A') or ctx.hand.contains_rank('D', 'K') or (ctx.hand.contains_rank('D', 'Q') and (ctx.hand.length('D') >= 2)))))
def cs_6_applies(ctx):
    return (named_evaluator(ctx, 'eval_stopper', target_suit='S') and (not ((ctx.hand.contains_rank('D', 'A') or ctx.hand.contains_rank('D', 'K') or (ctx.hand.contains_rank('D', 'Q') and (ctx.hand.length('D') >= 2)))) and not ((ctx.hand.contains_rank('H', 'A') or ctx.hand.contains_rank('H', 'K') or (ctx.hand.contains_rank('H', 'Q') and (ctx.hand.length('H') >= 2))))))
def cs_7_applies(ctx):
    return (ctx.state.exists('minor_raise', target_suit='C'))
def cs_8_applies(ctx):
    return ((ctx.hand.hcp >= 10 and ctx.hand.hcp <= 12))
def cs_9_applies(ctx):
    return (ctx.hand.hcp >= 13)
def cs_10_applies(ctx):
    return ((ctx.hand.hcp >= 12 and ctx.hand.hcp <= 14) and ctx.hand.balanced == True and named_evaluator(ctx, 'eval_stopper', target_suit='C') and named_evaluator(ctx, 'eval_stopper', target_suit='H') and named_evaluator(ctx, 'eval_stopper', target_suit='S'))
def cs_11_applies(ctx):
    return (named_evaluator(ctx, 'eval_stopper', target_suit='H'))
def cs_12_applies(ctx):
    return (named_evaluator(ctx, 'eval_stopper', target_suit='S') and not ((ctx.hand.contains_rank('H', 'A') or ctx.hand.contains_rank('H', 'K') or (ctx.hand.contains_rank('H', 'Q') and (ctx.hand.length('H') >= 2)))))
def cs_13_applies(ctx):
    return (named_evaluator(ctx, 'eval_stopper', target_suit='C') and (not ((ctx.hand.contains_rank('H', 'A') or ctx.hand.contains_rank('H', 'K') or (ctx.hand.contains_rank('H', 'Q') and (ctx.hand.length('H') >= 2)))) and not ((ctx.hand.contains_rank('S', 'A') or ctx.hand.contains_rank('S', 'K') or (ctx.hand.contains_rank('S', 'Q') and (ctx.hand.length('S') >= 2))))))
def cs_14_applies(ctx):
    return (ctx.state.exists('minor_raise', target_suit='D'))
def cs_15_applies(ctx):
    return ((ctx.hand.hcp >= 10 and ctx.hand.hcp <= 12))
def cs_16_applies(ctx):
    return (ctx.hand.hcp >= 13)

class MeowInvertedMinorsGadget(Gadget):
    id = 'meow_inverted_minors'
    namespace = 'meow_2over1'
    name = 'Meow Inverted Minors'
    version = '0.1.0'
    description = 'Inverted minor raises after 1C and 1D: invitational or better, no four-card major, forcing to 2N or three of the agreed minor, with stopper-showing continuations.\n'
    author = Author('Meow Li')

    def build(self):

        evaluator = self.evaluator('eval_stopper')
        evaluator.function = eval_stopper
        evaluator.description = 'Stopper evaluator for notrump exploration: ace, king, guarded queen, or length with jack.'

        call = self.call('im_17')
        call.when = '1CP2CP'
        call.bid = '3N'
        call.applies = im_17_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'N'
        call.meaning.level = 3
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'N'
        effect.level = 3
        effect.source = 'inverted_minor'
        call.description = 'Opener places 3N after an inverted club raise with extra balanced values and side stoppers.'

        call = self.call('im_18')
        call.when = '1DP2DP'
        call.bid = '3N'
        call.applies = im_18_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'N'
        call.meaning.level = 3
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'N'
        effect.level = 3
        effect.source = 'inverted_minor'
        call.description = 'Opener places 3N after an inverted diamond raise with extra balanced values and side stoppers.'

        call = self.call('im_19')
        call.when = '1CP2CP2DP'
        call.bid = '2N'
        call.applies = im_19_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['invitational']
        call.meaning.action = 'notrump_invite'
        call.meaning.target_suit = 'N'
        call.meaning.level = 2
        effect = call.effect('notrump_contract_interest', owner='partnership')
        effect.level = 2
        effect.source = 'inverted_minor'

        call = self.call('im_20')
        call.when = '1CP2CP2HP'
        call.bid = '2N'
        call.applies = im_20_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['invitational']
        call.meaning.action = 'notrump_invite'
        call.meaning.target_suit = 'N'
        call.meaning.level = 2
        effect = call.effect('notrump_contract_interest', owner='partnership')
        effect.level = 2
        effect.source = 'inverted_minor'

        call = self.call('im_21')
        call.when = '1CP2CP2SP'
        call.bid = '2N'
        call.applies = im_21_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['invitational']
        call.meaning.action = 'notrump_invite'
        call.meaning.target_suit = 'N'
        call.meaning.level = 2
        effect = call.effect('notrump_contract_interest', owner='partnership')
        effect.level = 2
        effect.source = 'inverted_minor'

        call = self.call('im_22')
        call.when = '1CP2CP2DP'
        call.bid = '3N'
        call.applies = im_22_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'N'
        call.meaning.level = 3
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'N'
        effect.level = 3
        effect.source = 'inverted_minor'

        call = self.call('im_23')
        call.when = '1CP2CP2HP'
        call.bid = '3N'
        call.applies = im_23_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'N'
        call.meaning.level = 3
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'N'
        effect.level = 3
        effect.source = 'inverted_minor'

        call = self.call('im_24')
        call.when = '1CP2CP2SP'
        call.bid = '3N'
        call.applies = im_24_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'N'
        call.meaning.level = 3
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'N'
        effect.level = 3
        effect.source = 'inverted_minor'

        call = self.call('im_25')
        call.when = '1CP2CP2DP'
        call.bid = '3C'
        call.applies = im_25_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'minor_fallback'
        call.meaning.target_suit = 'C'
        call.meaning.level = 3
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'C'
        effect.level = 3
        effect.source = 'inverted_minor'

        call = self.call('im_26')
        call.when = '1DP2DP2HP'
        call.bid = '2N'
        call.applies = im_26_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['invitational']
        call.meaning.action = 'notrump_invite'
        call.meaning.target_suit = 'N'
        call.meaning.level = 2
        effect = call.effect('notrump_contract_interest', owner='partnership')
        effect.level = 2
        effect.source = 'inverted_minor'

        call = self.call('im_27')
        call.when = '1DP2DP2SP'
        call.bid = '2N'
        call.applies = im_27_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['invitational']
        call.meaning.action = 'notrump_invite'
        call.meaning.target_suit = 'N'
        call.meaning.level = 2
        effect = call.effect('notrump_contract_interest', owner='partnership')
        effect.level = 2
        effect.source = 'inverted_minor'

        call = self.call('im_28')
        call.when = '1DP2DP3CP'
        call.bid = '3D'
        call.applies = im_28_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'minor_fallback'
        call.meaning.target_suit = 'D'
        call.meaning.level = 3
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'D'
        effect.level = 3
        effect.source = 'inverted_minor'

        call = self.call('im_29')
        call.when = '1DP2DP2HP'
        call.bid = '3N'
        call.applies = im_29_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'N'
        call.meaning.level = 3
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'N'
        effect.level = 3
        effect.source = 'inverted_minor'

        call = self.call('im_30')
        call.when = '1DP2DP2SP'
        call.bid = '3N'
        call.applies = im_30_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'N'
        call.meaning.level = 3
        effect = call.effect('final_contract', owner='partnership')
        effect.target_suit = 'N'
        effect.level = 3
        effect.source = 'inverted_minor'

        call = self.call('cs_1')
        call.when = '1CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2C'
        call.applies = cs_1_applies
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['support_showing', 'forcing', 'context_initiating']
        call.meaning.action = 'inverted_minor_raise'
        call.meaning.target_suit = 'C'
        call.meaning.alertable = True
        call.meaning.raise_strength = 'invitational_plus'
        effect = call.effect('minor_raise')
        effect.target_suit = 'C'
        effect.strength = 'invitational_plus'
        effect.method = 'inverted_minor'
        effect = call.effect('agreed_suit')
        effect.suit = 'C'
        effect.source = 'inverted_minor'
        effect = call.effect('forcing_status')
        effect.status = 'forcing_to_2N_or_3m'
        effect.target_suit = 'C'
        call.description = 'Inverted raise 1C-2C: invitational or better club support, no four-card major, forcing to 2N or 3C.'
        call.system_notes = 'After 1C, 2C is an inverted minor raise, invitational or better, denying a four-card major.'

        call = self.call('cs_2')
        call.when = '1DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2D'
        call.applies = cs_2_applies
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['support_showing', 'forcing', 'context_initiating']
        call.meaning.action = 'inverted_minor_raise'
        call.meaning.target_suit = 'D'
        call.meaning.alertable = True
        call.meaning.raise_strength = 'invitational_plus'
        effect = call.effect('minor_raise')
        effect.target_suit = 'D'
        effect.strength = 'invitational_plus'
        effect.method = 'inverted_minor'
        effect = call.effect('agreed_suit')
        effect.suit = 'D'
        effect.source = 'inverted_minor'
        effect = call.effect('forcing_status')
        effect.status = 'forcing_to_2N_or_3m'
        effect.target_suit = 'D'
        call.description = 'Inverted raise 1D-2D: invitational or better diamond support, no four-card major, forcing to 2N or 3D.'
        call.system_notes = 'After 1D, 2D is an inverted minor raise, invitational or better, denying a four-card major.'

        call = self.call('cs_3')
        call.when = '1CP2CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2N'
        call.applies = cs_3_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'context_setting']
        call.meaning.action = 'stopper_notrump_rebid'
        call.meaning.target_suit = 'N'
        call.meaning.level = 2
        effect = call.effect('notrump_contract_interest')
        effect.level = 2
        effect.source = 'inverted_minor'
        call.description = 'Opener rebids 2N after 1C-2C with a minimum balanced hand and stoppers in the side suits.'
        call.system_notes = 'After 1C-2C, 2N shows a minimum balanced hand with side-suit stoppers.'

        call = self.call('cs_4')
        call.when = '1CP2CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2D'
        call.applies = cs_4_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['stopper_showing', 'forcing']
        call.meaning.action = 'stopper_bid'
        call.meaning.target_suit = 'D'
        effect = call.effect('stopper')
        effect.suit = 'D'
        effect.source = 'inverted_minor'
        call.description = 'Opener shows a diamond stopper after 1C-2C when not making the immediate 2N rebid.'
        call.system_notes = 'After 1C-2C, 2D shows a diamond stopper up the line.'

        call = self.call('cs_5')
        call.when = '1CP2CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2H'
        call.applies = cs_5_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['stopper_showing', 'forcing']
        call.meaning.action = 'stopper_bid'
        call.meaning.target_suit = 'H'
        effect = call.effect('stopper')
        effect.suit = 'H'
        effect.source = 'inverted_minor'
        call.description = 'Opener shows a heart stopper after 1C-2C when no diamond stopper has been shown.'
        call.system_notes = 'After 1C-2C, 2H shows a heart stopper when diamonds were not stopped.'

        call = self.call('cs_6')
        call.when = '1CP2CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2S'
        call.applies = cs_6_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['stopper_showing', 'forcing']
        call.meaning.action = 'stopper_bid'
        call.meaning.target_suit = 'S'
        effect = call.effect('stopper')
        effect.suit = 'S'
        effect.source = 'inverted_minor'
        call.description = 'Opener shows a spade stopper after 1C-2C when lower side suits were not stopped.'
        call.system_notes = 'After 1C-2C, 2S shows a spade stopper when lower side suits were not stopped.'

        call = self.call('cs_7')
        call.when = '1CP2CP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3C'
        call.applies = cs_7_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['support_showing']
        call.meaning.action = 'minor_fallback'
        call.meaning.target_suit = 'C'
        effect = call.effect('minor_contract_interest')
        effect.target_suit = 'C'
        effect.source = 'inverted_minor'
        call.description = 'Opener rebids 3C after 1C-2C when notrump is unattractive.'
        call.system_notes = 'After 1C-2C, 3C is the minor fallback when opener does not show a notrump route.'

        call = self.call('cs_8')
        call.when = '1CP2CP2NP'
        call.seats = [1, 2, 3, 4]
        call.bid = 'P'
        call.applies = cs_8_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'pass_final_contract'
        call.meaning.target_suit = 'N'
        call.meaning.level = 2
        effect = call.effect('final_contract')
        effect.target_suit = 'N'
        effect.level = 2
        effect.source = 'inverted_minor'
        call.description = "Responder passes opener's 2N with invitational values after 1C-2C."
        call.system_notes = 'After 1C-2C-2N, pass accepts playing 2N with invitational values.'

        call = self.call('cs_9')
        call.when = '1CP2CP2NP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3N'
        call.applies = cs_9_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'N'
        call.meaning.level = 3
        effect = call.effect('final_contract')
        effect.target_suit = 'N'
        effect.level = 3
        effect.source = 'inverted_minor'
        call.description = 'Responder bids 3N with game-going values after 1C-2C-2N.'
        call.system_notes = 'After 1C-2C-2N, 3N accepts notrump game with game-going values.'

        call = self.call('cs_10')
        call.when = '1DP2DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2N'
        call.applies = cs_10_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive', 'context_setting']
        call.meaning.action = 'stopper_notrump_rebid'
        call.meaning.target_suit = 'N'
        call.meaning.level = 2
        effect = call.effect('notrump_contract_interest')
        effect.level = 2
        effect.source = 'inverted_minor'
        call.description = 'Opener rebids 2N after 1D-2D with a minimum balanced hand and stoppers in clubs and both majors.'
        call.system_notes = 'After 1D-2D, 2N shows a minimum balanced hand with side-suit stoppers.'

        call = self.call('cs_11')
        call.when = '1DP2DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2H'
        call.applies = cs_11_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['stopper_showing', 'forcing']
        call.meaning.action = 'stopper_bid'
        call.meaning.target_suit = 'H'
        effect = call.effect('stopper')
        effect.suit = 'H'
        effect.source = 'inverted_minor'
        call.description = 'Opener shows a heart stopper after 1D-2D.'
        call.system_notes = 'After 1D-2D, 2H shows a heart stopper up the line.'

        call = self.call('cs_12')
        call.when = '1DP2DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2S'
        call.applies = cs_12_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['stopper_showing', 'forcing']
        call.meaning.action = 'stopper_bid'
        call.meaning.target_suit = 'S'
        effect = call.effect('stopper')
        effect.suit = 'S'
        effect.source = 'inverted_minor'
        call.description = 'Opener shows a spade stopper after 1D-2D when hearts were not stopped.'
        call.system_notes = 'After 1D-2D, 2S shows a spade stopper when hearts were not stopped.'

        call = self.call('cs_13')
        call.when = '1DP2DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3C'
        call.applies = cs_13_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['stopper_showing', 'forcing']
        call.meaning.action = 'stopper_bid'
        call.meaning.target_suit = 'C'
        effect = call.effect('stopper')
        effect.suit = 'C'
        effect.source = 'inverted_minor'
        call.description = 'Opener shows a club stopper after 1D-2D when major stoppers were not available.'
        call.system_notes = 'After 1D-2D, 3C shows a club stopper when major stoppers were not available.'

        call = self.call('cs_14')
        call.when = '1DP2DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3D'
        call.applies = cs_14_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['support_showing']
        call.meaning.action = 'minor_fallback'
        call.meaning.target_suit = 'D'
        effect = call.effect('minor_contract_interest')
        effect.target_suit = 'D'
        effect.source = 'inverted_minor'
        call.description = 'Opener rebids 3D after 1D-2D when notrump is unattractive.'
        call.system_notes = 'After 1D-2D, 3D is the minor fallback when opener does not show a notrump route.'

        call = self.call('cs_15')
        call.when = '1DP2DP2NP'
        call.seats = [1, 2, 3, 4]
        call.bid = 'P'
        call.applies = cs_15_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'pass_final_contract'
        call.meaning.target_suit = 'N'
        call.meaning.level = 2
        effect = call.effect('final_contract')
        effect.target_suit = 'N'
        effect.level = 2
        effect.source = 'inverted_minor'
        call.description = "Responder passes opener's 2N with invitational values after 1D-2D."
        call.system_notes = 'After 1D-2D-2N, pass accepts playing 2N with invitational values.'

        call = self.call('cs_16')
        call.when = '1DP2DP2NP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3N'
        call.applies = cs_16_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'N'
        call.meaning.level = 3
        effect = call.effect('final_contract')
        effect.target_suit = 'N'
        effect.level = 3
        effect.source = 'inverted_minor'
        call.description = 'Responder bids 3N with game-going values after 1D-2D-2N.'
        call.system_notes = 'After 1D-2D-2N, 3N accepts notrump game with game-going values.'
