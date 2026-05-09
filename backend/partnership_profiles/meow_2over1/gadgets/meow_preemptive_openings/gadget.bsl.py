# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_20_applies(ctx):
    return (True)
def cs_21_applies(ctx):
    return (ctx.hand.hcp >= 10)
def cs_22_applies(ctx):
    return (ctx.hand.length('D') >= 3)
def cs_23_applies(ctx):
    return (ctx.hand.hcp >= 12 and ctx.hand.length('H') >= 5)
def cs_24_applies(ctx):
    return (ctx.hand.hcp >= 12 and ctx.hand.length('S') >= 5)
def cs_25_applies(ctx):
    return (ctx.hand.hcp >= 12 and ctx.hand.length('C') >= 5)
def cs_26_applies(ctx):
    return (True)
def cs_27_applies(ctx):
    return (ctx.hand.hcp >= 10)
def cs_28_applies(ctx):
    return (ctx.hand.length('H') >= 3)
def cs_29_applies(ctx):
    return (ctx.hand.hcp >= 10 and ctx.hand.length('H') >= 3)
def cs_30_applies(ctx):
    return (ctx.hand.hcp >= 12 and ctx.hand.length('S') >= 5)
def cs_31_applies(ctx):
    return (ctx.hand.hcp >= 12 and ctx.hand.length('C') >= 5)
def cs_32_applies(ctx):
    return (ctx.hand.hcp >= 12 and ctx.hand.length('D') >= 5)
def cs_33_applies(ctx):
    return (True)
def cs_34_applies(ctx):
    return (ctx.hand.hcp >= 10)
def cs_35_applies(ctx):
    return (ctx.hand.length('S') >= 3)
def cs_36_applies(ctx):
    return (ctx.hand.hcp >= 10 and ctx.hand.length('S') >= 3)
def cs_37_applies(ctx):
    return (ctx.hand.hcp >= 12 and ctx.hand.length('C') >= 5)
def cs_38_applies(ctx):
    return (ctx.hand.hcp >= 12 and ctx.hand.length('D') >= 5)
def cs_39_applies(ctx):
    return (ctx.hand.hcp >= 12 and ctx.hand.length('H') >= 5)
def cs_40_applies(ctx):
    return (True)
def cs_41_applies(ctx):
    return (True)
def cs_42_applies(ctx):
    return (True)
def cs_43_applies(ctx):
    return (True)
def cs_44_applies(ctx):
    return (ctx.hand.honor_count('D', ['A', 'K', 'Q']) == 3)
def cs_45_applies(ctx):
    return (True)
def cs_46_applies(ctx):
    return (True)
def cs_47_applies(ctx):
    return (True)
def cs_48_applies(ctx):
    return (True)
def cs_49_applies(ctx):
    return (ctx.hand.honor_count('H', ['A', 'K', 'Q']) == 3)
def cs_50_applies(ctx):
    return (True)
def cs_51_applies(ctx):
    return (True)
def cs_52_applies(ctx):
    return (True)
def cs_53_applies(ctx):
    return (True)
def cs_54_applies(ctx):
    return (ctx.hand.honor_count('S', ['A', 'K', 'Q']) == 3)
def cs_55_applies(ctx):
    return (ctx.hand.length('H') >= 3)
def cs_56_applies(ctx):
    return (True)
def cs_57_applies(ctx):
    return (ctx.hand.length('S') >= 3)
def cs_58_applies(ctx):
    return (True)
def cs_59_applies(ctx):
    return (ctx.hand.length('C') >= 3)
def cs_60_applies(ctx):
    return (True)
def _top_honor_count(ctx, suit):
    return ctx.hand.honor_count(suit, ["A", "K", "Q"])
def _top_five_honor_count(ctx, suit):
    return ctx.hand.honor_count(suit, ["A", "K", "Q", "J", "T"])
def _good_suit(ctx, suit):
    return _top_honor_count(ctx, suit) >= 2 or _top_five_honor_count(ctx, suit) >= 3
def _preempt_strength_ok(ctx, target_suit, *, first_min, second_min, third_min, unfavorable_first_min):
    hcp = ctx.hand.hcp
    seat = ctx.environment.get("seat_position")
    vulnerability = ctx.environment.get("vulnerability_relation")

    if seat == 3:
        return hcp >= third_min
    if seat == 2:
        return hcp >= second_min and _good_suit(ctx, target_suit)
    if seat == 1 and vulnerability == "favorable":
        return hcp >= first_min
    if seat == 1 and vulnerability == "unfavorable":
        return hcp >= unfavorable_first_min and _good_suit(ctx, target_suit)
    if seat == 1:
        return hcp >= first_min + 1
    return False
def eval_weak_two_opening(ctx, target_suit):
    return (
        ctx.hand.length(target_suit) >= 6
        and ctx.hand.hcp <= 10
        and _preempt_strength_ok(
            ctx,
            target_suit,
            first_min=5,
            second_min=7,
            third_min=4,
            unfavorable_first_min=7,
        )
    )
def eval_three_level_preempt(ctx, target_suit):
    return (
        ctx.hand.length(target_suit) >= 7
        and ctx.hand.hcp <= 10
        and _preempt_strength_ok(
            ctx,
            target_suit,
            first_min=4,
            second_min=7,
            third_min=3,
            unfavorable_first_min=6,
        )
    )
def cs_1_applies(ctx):
    return (named_evaluator(ctx, 'eval_weak_two_opening', target_suit='D'))
def cs_2_applies(ctx):
    return (named_evaluator(ctx, 'eval_weak_two_opening', target_suit='H'))
def cs_3_applies(ctx):
    return (named_evaluator(ctx, 'eval_weak_two_opening', target_suit='S'))
def cs_4_applies(ctx):
    return (named_evaluator(ctx, 'eval_three_level_preempt', target_suit='C'))
def cs_5_applies(ctx):
    return (named_evaluator(ctx, 'eval_three_level_preempt', target_suit='D'))
def cs_6_applies(ctx):
    return (named_evaluator(ctx, 'eval_three_level_preempt', target_suit='H'))
def cs_7_applies(ctx):
    return (named_evaluator(ctx, 'eval_three_level_preempt', target_suit='S'))

class MeowPreemptiveOpeningsGadget(Gadget):
    id = 'meow_preemptive_openings'
    namespace = 'meow_2over1'
    name = 'Meow Preemptive Openings'
    version = '0.1.0'
    description = 'Seat- and vulnerability-sensitive weak 2D/2H/2S and natural three-level preemptive openings for the Meow 2/1 benchmark, with Ogust and forcing new-suit continuations after two-level preempts. 2C is intentionally not defined here.\n'
    author = Author('Meow Li')

    def build(self):

        evaluator = self.evaluator('eval_weak_two_opening')
        evaluator.function = eval_weak_two_opening
        evaluator.description = 'Seat- and vulnerability-sensitive weak two opening evaluator.'

        evaluator = self.evaluator('eval_three_level_preempt')
        evaluator.function = eval_three_level_preempt
        evaluator.description = 'Seat- and vulnerability-sensitive natural three-level preempt evaluator.'

        call = self.call('cs_20')
        call.when = '2D P'
        call.seats = [1, 2, 3, 4]
        call.bid = 'P'
        call.applies = cs_20_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'pass_preempt'
        call.meaning.target_suit = 'D'
        effect = call.effect('final_contract', owner='partnership')
        effect.level = 2
        effect.target_suit = 'D'
        effect.source = 'weak_two'
        call.description = 'Responder passes a weak 2D when no constructive action is attractive.'
        call.system_notes = 'After a weak 2D, pass is natural.'

        call = self.call('cs_21')
        call.when = '2D P'
        call.seats = [1, 2, 3, 4]
        call.bid = '2N'
        call.applies = cs_21_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['inquiry', 'forcing']
        call.meaning.action = 'ogust_inquiry'
        call.meaning.target_suit = 'D'
        call.meaning.alertable = True
        effect = call.effect('ogust_inquiry', owner='responder')
        effect.target_suit = 'D'
        effect.status = 'pending'
        call.description = '2N Ogust inquiry after a weak 2D.'
        call.system_notes = 'After a weak 2D, 2N is Ogust, asking opener to describe hand strength and suit quality.'

        call = self.call('cs_22')
        call.when = '2D P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3D'
        call.applies = cs_22_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['preemptive']
        call.meaning.action = 'raise_preempt'
        call.meaning.target_suit = 'D'
        effect = call.effect('final_contract', owner='partnership')
        effect.level = 3
        effect.target_suit = 'D'
        effect.source = 'weak_two_raise'
        call.description = 'Responder raises a weak 2D to 3D.'
        call.system_notes = 'After a weak 2D, 3D is a natural raise.'

        call = self.call('cs_23')
        call.when = '2D P'
        call.seats = [1, 2, 3, 4]
        call.bid = '2H'
        call.applies = cs_23_applies
        call.meaning.nature = ['natural', 'forcing']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'new_suit_forcing_over_preempt'
        call.meaning.target_suit = 'H'
        effect = call.effect('forcing_new_suit', owner='responder')
        effect.target_suit = 'H'
        effect.opener_suit = 'D'
        effect.status = 'active'
        call.description = 'Responder bids 2H naturally and forcing after a weak 2D.'
        call.system_notes = 'After a weak 2D, a new suit is natural and forcing.'

        call = self.call('cs_24')
        call.when = '2D P'
        call.seats = [1, 2, 3, 4]
        call.bid = '2S'
        call.applies = cs_24_applies
        call.meaning.nature = ['natural', 'forcing']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'new_suit_forcing_over_preempt'
        call.meaning.target_suit = 'S'
        effect = call.effect('forcing_new_suit', owner='responder')
        effect.target_suit = 'S'
        effect.opener_suit = 'D'
        effect.status = 'active'
        call.description = 'Responder bids 2S naturally and forcing after a weak 2D.'
        call.system_notes = 'After a weak 2D, a new suit is natural and forcing.'

        call = self.call('cs_25')
        call.when = '2D P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3C'
        call.applies = cs_25_applies
        call.meaning.nature = ['natural', 'forcing']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'new_suit_forcing_over_preempt'
        call.meaning.target_suit = 'C'
        effect = call.effect('forcing_new_suit', owner='responder')
        effect.target_suit = 'C'
        effect.opener_suit = 'D'
        effect.status = 'active'
        call.description = 'Responder bids 3C naturally and forcing after a weak 2D.'
        call.system_notes = 'After a weak 2D, a new suit is natural and forcing.'

        call = self.call('cs_26')
        call.when = '2H P'
        call.seats = [1, 2, 3, 4]
        call.bid = 'P'
        call.applies = cs_26_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'pass_preempt'
        call.meaning.target_suit = 'H'
        effect = call.effect('final_contract', owner='partnership')
        effect.level = 2
        effect.target_suit = 'H'
        effect.source = 'weak_two'
        call.description = 'Responder passes a weak 2H when no constructive action is attractive.'
        call.system_notes = 'After a weak 2H, pass is natural.'

        call = self.call('cs_27')
        call.when = '2H P'
        call.seats = [1, 2, 3, 4]
        call.bid = '2N'
        call.applies = cs_27_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['inquiry', 'forcing']
        call.meaning.action = 'ogust_inquiry'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        effect = call.effect('ogust_inquiry', owner='responder')
        effect.target_suit = 'H'
        effect.status = 'pending'
        call.description = '2N Ogust inquiry after a weak 2H.'
        call.system_notes = 'After a weak 2H, 2N is Ogust, asking opener to describe hand strength and suit quality.'

        call = self.call('cs_28')
        call.when = '2H P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3H'
        call.applies = cs_28_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['preemptive']
        call.meaning.action = 'raise_preempt'
        call.meaning.target_suit = 'H'
        effect = call.effect('final_contract', owner='partnership')
        effect.level = 3
        effect.target_suit = 'H'
        effect.source = 'weak_two_raise'
        call.description = 'Responder raises a weak 2H to 3H.'
        call.system_notes = 'After a weak 2H, 3H is a natural raise.'

        call = self.call('cs_29')
        call.when = '2H P'
        call.seats = [1, 2, 3, 4]
        call.bid = '4H'
        call.applies = cs_29_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'H'
        call.meaning.level = 4
        effect = call.effect('final_contract', owner='partnership')
        effect.level = 4
        effect.target_suit = 'H'
        effect.source = 'weak_two_game_raise'
        call.description = 'Responder raises a weak 2H to game.'
        call.system_notes = 'After a weak 2H, 4H is to play.'

        call = self.call('cs_30')
        call.when = '2H P'
        call.seats = [1, 2, 3, 4]
        call.bid = '2S'
        call.applies = cs_30_applies
        call.meaning.nature = ['natural', 'forcing']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'new_suit_forcing_over_preempt'
        call.meaning.target_suit = 'S'
        effect = call.effect('forcing_new_suit', owner='responder')
        effect.target_suit = 'S'
        effect.opener_suit = 'H'
        effect.status = 'active'
        call.description = 'Responder bids 2S naturally and forcing after a weak 2H.'
        call.system_notes = 'After a weak 2H, a new suit is natural and forcing.'

        call = self.call('cs_31')
        call.when = '2H P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3C'
        call.applies = cs_31_applies
        call.meaning.nature = ['natural', 'forcing']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'new_suit_forcing_over_preempt'
        call.meaning.target_suit = 'C'
        effect = call.effect('forcing_new_suit', owner='responder')
        effect.target_suit = 'C'
        effect.opener_suit = 'H'
        effect.status = 'active'
        call.description = 'Responder bids 3C naturally and forcing after a weak 2H.'
        call.system_notes = 'After a weak 2H, a new suit is natural and forcing.'

        call = self.call('cs_32')
        call.when = '2H P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3D'
        call.applies = cs_32_applies
        call.meaning.nature = ['natural', 'forcing']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'new_suit_forcing_over_preempt'
        call.meaning.target_suit = 'D'
        effect = call.effect('forcing_new_suit', owner='responder')
        effect.target_suit = 'D'
        effect.opener_suit = 'H'
        effect.status = 'active'
        call.description = 'Responder bids 3D naturally and forcing after a weak 2H.'
        call.system_notes = 'After a weak 2H, a new suit is natural and forcing.'

        call = self.call('cs_33')
        call.when = '2S P'
        call.seats = [1, 2, 3, 4]
        call.bid = 'P'
        call.applies = cs_33_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'pass_preempt'
        call.meaning.target_suit = 'S'
        effect = call.effect('final_contract', owner='partnership')
        effect.level = 2
        effect.target_suit = 'S'
        effect.source = 'weak_two'
        call.description = 'Responder passes a weak 2S when no constructive action is attractive.'
        call.system_notes = 'After a weak 2S, pass is natural.'

        call = self.call('cs_34')
        call.when = '2S P'
        call.seats = [1, 2, 3, 4]
        call.bid = '2N'
        call.applies = cs_34_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['inquiry', 'forcing']
        call.meaning.action = 'ogust_inquiry'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        effect = call.effect('ogust_inquiry', owner='responder')
        effect.target_suit = 'S'
        effect.status = 'pending'
        call.description = '2N Ogust inquiry after a weak 2S.'
        call.system_notes = 'After a weak 2S, 2N is Ogust, asking opener to describe hand strength and suit quality.'

        call = self.call('cs_35')
        call.when = '2S P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3S'
        call.applies = cs_35_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['preemptive']
        call.meaning.action = 'raise_preempt'
        call.meaning.target_suit = 'S'
        effect = call.effect('final_contract', owner='partnership')
        effect.level = 3
        effect.target_suit = 'S'
        effect.source = 'weak_two_raise'
        call.description = 'Responder raises a weak 2S to 3S.'
        call.system_notes = 'After a weak 2S, 3S is a natural raise.'

        call = self.call('cs_36')
        call.when = '2S P'
        call.seats = [1, 2, 3, 4]
        call.bid = '4S'
        call.applies = cs_36_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'S'
        call.meaning.level = 4
        effect = call.effect('final_contract', owner='partnership')
        effect.level = 4
        effect.target_suit = 'S'
        effect.source = 'weak_two_game_raise'
        call.description = 'Responder raises a weak 2S to game.'
        call.system_notes = 'After a weak 2S, 4S is to play.'

        call = self.call('cs_37')
        call.when = '2S P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3C'
        call.applies = cs_37_applies
        call.meaning.nature = ['natural', 'forcing']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'new_suit_forcing_over_preempt'
        call.meaning.target_suit = 'C'
        effect = call.effect('forcing_new_suit', owner='responder')
        effect.target_suit = 'C'
        effect.opener_suit = 'S'
        effect.status = 'active'
        call.description = 'Responder bids 3C naturally and forcing after a weak 2S.'
        call.system_notes = 'After a weak 2S, a new suit is natural and forcing.'

        call = self.call('cs_38')
        call.when = '2S P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3D'
        call.applies = cs_38_applies
        call.meaning.nature = ['natural', 'forcing']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'new_suit_forcing_over_preempt'
        call.meaning.target_suit = 'D'
        effect = call.effect('forcing_new_suit', owner='responder')
        effect.target_suit = 'D'
        effect.opener_suit = 'S'
        effect.status = 'active'
        call.description = 'Responder bids 3D naturally and forcing after a weak 2S.'
        call.system_notes = 'After a weak 2S, a new suit is natural and forcing.'

        call = self.call('cs_39')
        call.when = '2S P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3H'
        call.applies = cs_39_applies
        call.meaning.nature = ['natural', 'forcing']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'new_suit_forcing_over_preempt'
        call.meaning.target_suit = 'H'
        effect = call.effect('forcing_new_suit', owner='responder')
        effect.target_suit = 'H'
        effect.opener_suit = 'S'
        effect.status = 'active'
        call.description = 'Responder bids 3H naturally and forcing after a weak 2S.'
        call.system_notes = 'After a weak 2S, a new suit is natural and forcing.'

        call = self.call('cs_40')
        call.when = '2D P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3C'
        call.applies = cs_40_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'ogust_response'
        call.meaning.target_suit = 'D'
        call.meaning.alertable = True
        call.meaning.hand_quality = 'minimum'
        call.meaning.suit_quality = 'poor'
        effect = call.effect('ogust_response', owner='opener')
        effect.target_suit = 'D'
        effect.hand_quality = 'minimum'
        effect.suit_quality = 'poor'
        call.description = 'Ogust response: minimum hand, poor diamond suit.'
        call.system_notes = 'After weak 2D-2N, 3C shows minimum hand and poor suit.'

        call = self.call('cs_41')
        call.when = '2D P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3D'
        call.applies = cs_41_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'ogust_response'
        call.meaning.target_suit = 'D'
        call.meaning.alertable = True
        call.meaning.hand_quality = 'minimum'
        call.meaning.suit_quality = 'good'
        effect = call.effect('ogust_response', owner='opener')
        effect.target_suit = 'D'
        effect.hand_quality = 'minimum'
        effect.suit_quality = 'good'
        call.description = 'Ogust response: minimum hand, good diamond suit.'
        call.system_notes = 'After weak 2D-2N, 3D shows minimum hand and good suit.'

        call = self.call('cs_42')
        call.when = '2D P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3H'
        call.applies = cs_42_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'ogust_response'
        call.meaning.target_suit = 'D'
        call.meaning.alertable = True
        call.meaning.hand_quality = 'maximum'
        call.meaning.suit_quality = 'poor'
        effect = call.effect('ogust_response', owner='opener')
        effect.target_suit = 'D'
        effect.hand_quality = 'maximum'
        effect.suit_quality = 'poor'
        call.description = 'Ogust response: maximum hand, poor diamond suit.'
        call.system_notes = 'After weak 2D-2N, 3H shows maximum hand and poor suit.'

        call = self.call('cs_43')
        call.when = '2D P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3S'
        call.applies = cs_43_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'ogust_response'
        call.meaning.target_suit = 'D'
        call.meaning.alertable = True
        call.meaning.hand_quality = 'maximum'
        call.meaning.suit_quality = 'good'
        effect = call.effect('ogust_response', owner='opener')
        effect.target_suit = 'D'
        effect.hand_quality = 'maximum'
        effect.suit_quality = 'good'
        call.description = 'Ogust response: maximum hand, good diamond suit.'
        call.system_notes = 'After weak 2D-2N, 3S shows maximum hand and good suit.'

        call = self.call('cs_44')
        call.when = '2D P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3N'
        call.applies = cs_44_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'ogust_response'
        call.meaning.target_suit = 'D'
        call.meaning.alertable = True
        call.meaning.hand_quality = 'maximum'
        call.meaning.suit_quality = 'solid'
        effect = call.effect('ogust_response', owner='opener')
        effect.target_suit = 'D'
        effect.hand_quality = 'maximum'
        effect.suit_quality = 'solid'
        call.description = 'Ogust response: solid diamond suit.'
        call.system_notes = 'After weak 2D-2N, 3N shows a solid suit.'

        call = self.call('cs_45')
        call.when = '2H P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3C'
        call.applies = cs_45_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'ogust_response'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.hand_quality = 'minimum'
        call.meaning.suit_quality = 'poor'
        effect = call.effect('ogust_response', owner='opener')
        effect.target_suit = 'H'
        effect.hand_quality = 'minimum'
        effect.suit_quality = 'poor'
        call.description = 'Ogust response: minimum hand, poor heart suit.'
        call.system_notes = 'After weak 2H-2N, 3C shows minimum hand and poor suit.'

        call = self.call('cs_46')
        call.when = '2H P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3D'
        call.applies = cs_46_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'ogust_response'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.hand_quality = 'minimum'
        call.meaning.suit_quality = 'good'
        effect = call.effect('ogust_response', owner='opener')
        effect.target_suit = 'H'
        effect.hand_quality = 'minimum'
        effect.suit_quality = 'good'
        call.description = 'Ogust response: minimum hand, good heart suit.'
        call.system_notes = 'After weak 2H-2N, 3D shows minimum hand and good suit.'

        call = self.call('cs_47')
        call.when = '2H P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3H'
        call.applies = cs_47_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'ogust_response'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.hand_quality = 'maximum'
        call.meaning.suit_quality = 'poor'
        effect = call.effect('ogust_response', owner='opener')
        effect.target_suit = 'H'
        effect.hand_quality = 'maximum'
        effect.suit_quality = 'poor'
        call.description = 'Ogust response: maximum hand, poor heart suit.'
        call.system_notes = 'After weak 2H-2N, 3H shows maximum hand and poor suit.'

        call = self.call('cs_48')
        call.when = '2H P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3S'
        call.applies = cs_48_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'ogust_response'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.hand_quality = 'maximum'
        call.meaning.suit_quality = 'good'
        effect = call.effect('ogust_response', owner='opener')
        effect.target_suit = 'H'
        effect.hand_quality = 'maximum'
        effect.suit_quality = 'good'
        call.description = 'Ogust response: maximum hand, good heart suit.'
        call.system_notes = 'After weak 2H-2N, 3S shows maximum hand and good suit.'

        call = self.call('cs_49')
        call.when = '2H P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3N'
        call.applies = cs_49_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'ogust_response'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.hand_quality = 'maximum'
        call.meaning.suit_quality = 'solid'
        effect = call.effect('ogust_response', owner='opener')
        effect.target_suit = 'H'
        effect.hand_quality = 'maximum'
        effect.suit_quality = 'solid'
        call.description = 'Ogust response: solid heart suit.'
        call.system_notes = 'After weak 2H-2N, 3N shows a solid suit.'

        call = self.call('cs_50')
        call.when = '2S P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3C'
        call.applies = cs_50_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'ogust_response'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.hand_quality = 'minimum'
        call.meaning.suit_quality = 'poor'
        effect = call.effect('ogust_response', owner='opener')
        effect.target_suit = 'S'
        effect.hand_quality = 'minimum'
        effect.suit_quality = 'poor'
        call.description = 'Ogust response: minimum hand, poor spade suit.'
        call.system_notes = 'After weak 2S-2N, 3C shows minimum hand and poor suit.'

        call = self.call('cs_51')
        call.when = '2S P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3D'
        call.applies = cs_51_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'ogust_response'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.hand_quality = 'minimum'
        call.meaning.suit_quality = 'good'
        effect = call.effect('ogust_response', owner='opener')
        effect.target_suit = 'S'
        effect.hand_quality = 'minimum'
        effect.suit_quality = 'good'
        call.description = 'Ogust response: minimum hand, good spade suit.'
        call.system_notes = 'After weak 2S-2N, 3D shows minimum hand and good suit.'

        call = self.call('cs_52')
        call.when = '2S P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3H'
        call.applies = cs_52_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'ogust_response'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.hand_quality = 'maximum'
        call.meaning.suit_quality = 'poor'
        effect = call.effect('ogust_response', owner='opener')
        effect.target_suit = 'S'
        effect.hand_quality = 'maximum'
        effect.suit_quality = 'poor'
        call.description = 'Ogust response: maximum hand, poor spade suit.'
        call.system_notes = 'After weak 2S-2N, 3H shows maximum hand and poor suit.'

        call = self.call('cs_53')
        call.when = '2S P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3S'
        call.applies = cs_53_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'ogust_response'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.hand_quality = 'maximum'
        call.meaning.suit_quality = 'good'
        effect = call.effect('ogust_response', owner='opener')
        effect.target_suit = 'S'
        effect.hand_quality = 'maximum'
        effect.suit_quality = 'good'
        call.description = 'Ogust response: maximum hand, good spade suit.'
        call.system_notes = 'After weak 2S-2N, 3S shows maximum hand and good suit.'

        call = self.call('cs_54')
        call.when = '2S P 2N P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3N'
        call.applies = cs_54_applies
        call.meaning.nature = ['artificial']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'ogust_response'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.hand_quality = 'maximum'
        call.meaning.suit_quality = 'solid'
        effect = call.effect('ogust_response', owner='opener')
        effect.target_suit = 'S'
        effect.hand_quality = 'maximum'
        effect.suit_quality = 'solid'
        call.description = 'Ogust response: solid spade suit.'
        call.system_notes = 'After weak 2S-2N, 3N shows a solid suit.'

        call = self.call('cs_55')
        call.when = '2D P 2H P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3H'
        call.applies = cs_55_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'support_new_suit_forcing'
        call.meaning.target_suit = 'H'
        effect = call.effect('agreed_suit')
        effect.suit = 'H'
        effect.source = 'preempt_new_suit_forcing'
        call.description = "Opener supports hearts after responder's forcing new-suit bid."
        call.system_notes = "After weak 2D and responder's forcing 2H, opener raises with support."

        call = self.call('cs_56')
        call.when = '2D P 2H P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3D'
        call.applies = cs_56_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'rebid_preempt_suit'
        call.meaning.target_suit = 'D'
        effect = call.effect('preempt_suit_rebid', owner='opener')
        effect.target_suit = 'D'
        call.description = "Opener rebids diamonds after responder's forcing new-suit bid."
        call.system_notes = "After weak 2D and responder's forcing 2H, opener rebids diamonds without a better descriptive action."

        call = self.call('cs_57')
        call.when = '2H P 2S P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3S'
        call.applies = cs_57_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'support_new_suit_forcing'
        call.meaning.target_suit = 'S'
        effect = call.effect('agreed_suit')
        effect.suit = 'S'
        effect.source = 'preempt_new_suit_forcing'
        call.description = "Opener supports spades after responder's forcing new-suit bid."
        call.system_notes = "After weak 2H and responder's forcing 2S, opener raises with support."

        call = self.call('cs_58')
        call.when = '2H P 2S P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3H'
        call.applies = cs_58_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'rebid_preempt_suit'
        call.meaning.target_suit = 'H'
        effect = call.effect('preempt_suit_rebid', owner='opener')
        effect.target_suit = 'H'
        call.description = "Opener rebids hearts after responder's forcing new-suit bid."
        call.system_notes = "After weak 2H and responder's forcing 2S, opener rebids hearts without a better descriptive action."

        call = self.call('cs_59')
        call.when = '2S P 3C P'
        call.seats = [1, 2, 3, 4]
        call.bid = '4C'
        call.applies = cs_59_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'support_new_suit_forcing'
        call.meaning.target_suit = 'C'
        effect = call.effect('agreed_suit')
        effect.suit = 'C'
        effect.source = 'preempt_new_suit_forcing'
        call.description = "Opener supports clubs after responder's forcing new-suit bid."
        call.system_notes = "After weak 2S and responder's forcing 3C, opener raises with support."

        call = self.call('cs_60')
        call.when = '2S P 3C P'
        call.seats = [1, 2, 3, 4]
        call.bid = '3S'
        call.applies = cs_60_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'rebid_preempt_suit'
        call.meaning.target_suit = 'S'
        effect = call.effect('preempt_suit_rebid', owner='opener')
        effect.target_suit = 'S'
        call.description = "Opener rebids spades after responder's forcing new-suit bid."
        call.system_notes = "After weak 2S and responder's forcing 3C, opener rebids spades without a better descriptive action."

        call = self.call('cs_1')
        call.seats = [1, 2, 3]
        call.bid = '2D'
        call.applies = cs_1_applies
        call.meaning.nature = ['natural', 'weak']
        call.meaning.acts = ['preemptive', 'descriptive', 'context_initiating']
        call.meaning.action = 'weak_two_opening'
        call.meaning.target_suit = 'D'
        call.meaning.shown_length_min = 6
        effect = call.effect('preemptive_opening')
        effect.level = 2
        effect.target_suit = 'D'
        effect.style = 'seat_and_vulnerability_dependent'
        call.description = 'Opens a weak 2D with a six-card diamond suit, adjusted by seat and vulnerability.'
        call.system_notes = '2D is weak and natural; style varies by seat and vulnerability.'

        call = self.call('cs_2')
        call.seats = [1, 2, 3]
        call.bid = '2H'
        call.applies = cs_2_applies
        call.meaning.nature = ['natural', 'weak']
        call.meaning.acts = ['preemptive', 'descriptive', 'context_initiating']
        call.meaning.action = 'weak_two_opening'
        call.meaning.target_suit = 'H'
        call.meaning.shown_length_min = 6
        effect = call.effect('preemptive_opening')
        effect.level = 2
        effect.target_suit = 'H'
        effect.style = 'seat_and_vulnerability_dependent'
        call.description = 'Opens a weak 2H with a six-card heart suit, adjusted by seat and vulnerability.'
        call.system_notes = '2H is weak and natural; style varies by seat and vulnerability.'

        call = self.call('cs_3')
        call.seats = [1, 2, 3]
        call.bid = '2S'
        call.applies = cs_3_applies
        call.meaning.nature = ['natural', 'weak']
        call.meaning.acts = ['preemptive', 'descriptive', 'context_initiating']
        call.meaning.action = 'weak_two_opening'
        call.meaning.target_suit = 'S'
        call.meaning.shown_length_min = 6
        effect = call.effect('preemptive_opening')
        effect.level = 2
        effect.target_suit = 'S'
        effect.style = 'seat_and_vulnerability_dependent'
        call.description = 'Opens a weak 2S with a six-card spade suit, adjusted by seat and vulnerability.'
        call.system_notes = '2S is weak and natural; style varies by seat and vulnerability.'

        call = self.call('cs_4')
        call.seats = [1, 2, 3]
        call.bid = '3C'
        call.applies = cs_4_applies
        call.meaning.nature = ['natural', 'weak']
        call.meaning.acts = ['preemptive', 'descriptive', 'context_initiating']
        call.meaning.action = 'three_level_preempt'
        call.meaning.target_suit = 'C'
        call.meaning.shown_length_min = 7
        effect = call.effect('preemptive_opening')
        effect.level = 3
        effect.target_suit = 'C'
        effect.style = 'seat_and_vulnerability_dependent'
        call.description = 'Opens 3C as a natural preempt with a seven-card club suit, adjusted by seat and vulnerability.'
        call.system_notes = '3C is natural and preemptive; style varies by seat and vulnerability.'

        call = self.call('cs_5')
        call.seats = [1, 2, 3]
        call.bid = '3D'
        call.applies = cs_5_applies
        call.meaning.nature = ['natural', 'weak']
        call.meaning.acts = ['preemptive', 'descriptive', 'context_initiating']
        call.meaning.action = 'three_level_preempt'
        call.meaning.target_suit = 'D'
        call.meaning.shown_length_min = 7
        effect = call.effect('preemptive_opening')
        effect.level = 3
        effect.target_suit = 'D'
        effect.style = 'seat_and_vulnerability_dependent'
        call.description = 'Opens 3D as a natural preempt with a seven-card diamond suit, adjusted by seat and vulnerability.'
        call.system_notes = '3D is natural and preemptive; style varies by seat and vulnerability.'

        call = self.call('cs_6')
        call.seats = [1, 2, 3]
        call.bid = '3H'
        call.applies = cs_6_applies
        call.meaning.nature = ['natural', 'weak']
        call.meaning.acts = ['preemptive', 'descriptive', 'context_initiating']
        call.meaning.action = 'three_level_preempt'
        call.meaning.target_suit = 'H'
        call.meaning.shown_length_min = 7
        effect = call.effect('preemptive_opening')
        effect.level = 3
        effect.target_suit = 'H'
        effect.style = 'seat_and_vulnerability_dependent'
        call.description = 'Opens 3H as a natural preempt with a seven-card heart suit, adjusted by seat and vulnerability.'
        call.system_notes = '3H is natural and preemptive; style varies by seat and vulnerability.'

        call = self.call('cs_7')
        call.seats = [1, 2, 3]
        call.bid = '3S'
        call.applies = cs_7_applies
        call.meaning.nature = ['natural', 'weak']
        call.meaning.acts = ['preemptive', 'descriptive', 'context_initiating']
        call.meaning.action = 'three_level_preempt'
        call.meaning.target_suit = 'S'
        call.meaning.shown_length_min = 7
        effect = call.effect('preemptive_opening')
        effect.level = 3
        effect.target_suit = 'S'
        effect.style = 'seat_and_vulnerability_dependent'
        call.description = 'Opens 3S as a natural preempt with a seven-card spade suit, adjusted by seat and vulnerability.'
        call.system_notes = '3S is natural and preemptive; style varies by seat and vulnerability.'
