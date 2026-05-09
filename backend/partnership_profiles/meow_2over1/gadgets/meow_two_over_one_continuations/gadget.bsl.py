# Partner Python-BSL source.
# This file defines one class-authored Gadget.


def opener_has_six_spades(ctx):
    return ctx.hand.length('S') >= 6


def opener_has_six_hearts(ctx):
    return ctx.hand.length('H') >= 6


def responder_has_spade_fit_for_six_card_opener(ctx):
    return ctx.hand.length('S') >= 2


def responder_lacks_spade_fit_for_six_card_opener(ctx):
    return ctx.hand.length('S') <= 1


def responder_has_heart_fit_for_six_card_opener(ctx):
    return ctx.hand.length('H') >= 2


def responder_lacks_heart_fit_for_six_card_opener(ctx):
    return ctx.hand.length('H') <= 1


def opener_has_four_card_suit(ctx, suit):
    return ctx.hand.length(suit) >= 4


def responder_supports_opener_side_major(ctx, suit):
    return ctx.hand.length(suit) >= 4


def responder_lacks_opener_side_major_fit(ctx, suit):
    return ctx.hand.length(suit) <= 3


def responder_places_notrump_after_minor_side_suit(ctx):
    return True


class MeowTwoOverOneContinuationsGadget(Gadget):
    id = 'meow_two_over_one_continuations'
    namespace = 'meow_2over1'
    name = 'Meow Two Over One Continuations'
    version = '0.1.0'
    description = 'Practical continuation layer after a game-forcing two-over-one response. This slice covers the common opener rebid of a six-card major and responder placement in major game or 3N.'
    system_notes = 'After a two-over-one game force, opener can rebid a six-card major. Responder then places game in the major with fit, or 3N without fit.'
    author = Author('Meow Li')

    def build(self):

        for response in ('2C', '2D', '2H'):
            call = self.call(f'opener_rebid_2s_after_{response.lower()}')
            call.when = f'1SP{response}P'
            call.bid = '2S'
            call.applies = opener_has_six_spades
            call.meaning.nature = ['natural']
            call.meaning.acts = ['descriptive', 'forcing']
            call.meaning.action = 'two_over_one_opener_major_rebid'
            call.meaning.target_suit = 'S'
            call.meaning.shown_length_min = 6
            effect = call.effect('opener.length.S', owner='opener')
            effect.min_value = 6
            effect.source = 'two_over_one_continuation'
            call.description = f'After 1S-{response}, opener rebids 2S to show a six-card spade suit.'
            call.system_notes = f'After 1S-{response}, 2S shows six or more spades and keeps the game force alive.'

            call = self.call(f'responder_raises_4s_after_{response.lower()}')
            call.when = f'1SP{response}P2SP'
            call.bid = '4S'
            call.applies = responder_has_spade_fit_for_six_card_opener
            call.meaning.nature = ['natural']
            call.meaning.acts = ['final_placement']
            call.meaning.action = 'place_contract'
            call.meaning.target_suit = 'S'
            call.meaning.level = 4
            effect = call.effect('partnership.fit.S', owner='partnership')
            effect.suit = 'S'
            effect.opener_min_length = 6
            effect.responder_min_length = 2
            effect.min_total = 8
            effect.pattern_floor = '6-2'
            effect.source = 'two_over_one_continuation'
            effect = call.effect('final_contract', owner='partnership')
            effect.target_suit = 'S'
            effect.level = 4
            effect.source = 'two_over_one_continuation'
            call.description = f'After 1S-{response}-2S, responder places 4S with a fit for opener six-card spades.'
            call.system_notes = f'After 1S-{response}-2S, 4S places game with at least a 6-2 spade fit.'

            call = self.call(f'responder_places_3n_after_2s_{response.lower()}')
            call.when = f'1SP{response}P2SP'
            call.bid = '3N'
            call.applies = responder_lacks_spade_fit_for_six_card_opener
            call.meaning.nature = ['natural']
            call.meaning.acts = ['final_placement']
            call.meaning.action = 'place_contract'
            call.meaning.target_suit = 'N'
            call.meaning.level = 3
            effect = call.effect('final_contract', owner='partnership')
            effect.target_suit = 'N'
            effect.level = 3
            effect.source = 'two_over_one_continuation'
            call.description = f'After 1S-{response}-2S, responder places 3N without a spade fit.'
            call.system_notes = f'After 1S-{response}-2S, 3N is the practical game without a spade fit.'

        for response in ('2C', '2D'):
            call = self.call(f'opener_rebid_2h_after_{response.lower()}')
            call.when = f'1HP{response}P'
            call.bid = '2H'
            call.applies = opener_has_six_hearts
            call.meaning.nature = ['natural']
            call.meaning.acts = ['descriptive', 'forcing']
            call.meaning.action = 'two_over_one_opener_major_rebid'
            call.meaning.target_suit = 'H'
            call.meaning.shown_length_min = 6
            effect = call.effect('opener.length.H', owner='opener')
            effect.min_value = 6
            effect.source = 'two_over_one_continuation'
            call.description = f'After 1H-{response}, opener rebids 2H to show a six-card heart suit.'
            call.system_notes = f'After 1H-{response}, 2H shows six or more hearts and keeps the game force alive.'

            call = self.call(f'responder_raises_4h_after_{response.lower()}')
            call.when = f'1HP{response}P2HP'
            call.bid = '4H'
            call.applies = responder_has_heart_fit_for_six_card_opener
            call.meaning.nature = ['natural']
            call.meaning.acts = ['final_placement']
            call.meaning.action = 'place_contract'
            call.meaning.target_suit = 'H'
            call.meaning.level = 4
            effect = call.effect('partnership.fit.H', owner='partnership')
            effect.suit = 'H'
            effect.opener_min_length = 6
            effect.responder_min_length = 2
            effect.min_total = 8
            effect.pattern_floor = '6-2'
            effect.source = 'two_over_one_continuation'
            effect = call.effect('final_contract', owner='partnership')
            effect.target_suit = 'H'
            effect.level = 4
            effect.source = 'two_over_one_continuation'
            call.description = f'After 1H-{response}-2H, responder places 4H with a fit for opener six-card hearts.'
            call.system_notes = f'After 1H-{response}-2H, 4H places game with at least a 6-2 heart fit.'

            call = self.call(f'responder_places_3n_after_2h_{response.lower()}')
            call.when = f'1HP{response}P2HP'
            call.bid = '3N'
            call.applies = responder_lacks_heart_fit_for_six_card_opener
            call.meaning.nature = ['natural']
            call.meaning.acts = ['final_placement']
            call.meaning.action = 'place_contract'
            call.meaning.target_suit = 'N'
            call.meaning.level = 3
            effect = call.effect('final_contract', owner='partnership')
            effect.target_suit = 'N'
            effect.level = 3
            effect.source = 'two_over_one_continuation'
            call.description = f'After 1H-{response}-2H, responder places 3N without a heart fit.'
            call.system_notes = f'After 1H-{response}-2H, 3N is the practical game without a heart fit.'

        for opening, response, rebid, side_suit in _two_over_one_side_rebid_cases():
            call = self.call(f'{opening.lower()}_{response.lower()}_rebid_{rebid.lower()}')
            call.when = f'{opening}P{response}P'
            call.bid = rebid
            call.applies = lambda ctx, side_suit=side_suit: opener_has_four_card_suit(ctx, side_suit)
            call.meaning.nature = ['natural']
            call.meaning.acts = ['descriptive', 'forcing']
            call.meaning.action = 'two_over_one_opener_side_suit_rebid'
            call.meaning.target_suit = side_suit
            call.meaning.shown_length_min = 4
            effect = call.effect(f'opener.length.{side_suit}', owner='opener')
            effect.min_value = 4
            effect.source = 'two_over_one_continuation'
            call.description = f'After {opening}-{response}, opener rebids {rebid} naturally to show four or more {side_suit}.'
            call.system_notes = f'After {opening}-{response}, {rebid} is natural and forcing, showing four or more {side_suit}.'

            if side_suit in ('H', 'S'):
                call = self.call(f'{opening.lower()}_{response.lower()}_{rebid.lower()}_raise_game')
                call.when = f'{opening}P{response}P{rebid}P'
                call.bid = '4' + side_suit
                call.applies = lambda ctx, side_suit=side_suit: responder_supports_opener_side_major(ctx, side_suit)
                call.meaning.nature = ['natural']
                call.meaning.acts = ['final_placement']
                call.meaning.action = 'place_contract'
                call.meaning.target_suit = side_suit
                call.meaning.level = 4
                effect = call.effect(f'partnership.fit.{side_suit}', owner='partnership')
                effect.suit = side_suit
                effect.opener_min_length = 4
                effect.responder_min_length = 4
                effect.min_total = 8
                effect.pattern_floor = '4-4'
                effect.source = 'two_over_one_continuation'
                effect = call.effect('final_contract', owner='partnership')
                effect.target_suit = side_suit
                effect.level = 4
                effect.source = 'two_over_one_continuation'
                call.description = f'Responder raises opener side major {side_suit} to game after the 2/1 dialogue finds a 4-4 fit.'
                call.system_notes = f'After {opening}-{response}-{rebid}, four of {side_suit} places game with a 4-4 fit.'

                call = self.call(f'{opening.lower()}_{response.lower()}_{rebid.lower()}_place_3n')
                call.when = f'{opening}P{response}P{rebid}P'
                call.bid = '3N'
                call.applies = lambda ctx, side_suit=side_suit: responder_lacks_opener_side_major_fit(ctx, side_suit)
                call.meaning.nature = ['natural']
                call.meaning.acts = ['final_placement']
                call.meaning.action = 'place_contract'
                call.meaning.target_suit = 'N'
                call.meaning.level = 3
                effect = call.effect('final_contract', owner='partnership')
                effect.target_suit = 'N'
                effect.level = 3
                effect.source = 'two_over_one_continuation'
                call.description = f'Responder places 3N after opener side-major rebid {rebid} when no 4-4 fit is present.'
                call.system_notes = f'After {opening}-{response}-{rebid}, 3N is the practical game without a {side_suit} fit.'
            else:
                call = self.call(f'{opening.lower()}_{response.lower()}_{rebid.lower()}_place_3n')
                call.when = f'{opening}P{response}P{rebid}P'
                call.bid = '3N'
                call.applies = responder_places_notrump_after_minor_side_suit
                call.meaning.nature = ['natural']
                call.meaning.acts = ['final_placement']
                call.meaning.action = 'place_contract'
                call.meaning.target_suit = 'N'
                call.meaning.level = 3
                effect = call.effect('final_contract', owner='partnership')
                effect.target_suit = 'N'
                effect.level = 3
                effect.source = 'two_over_one_continuation'
                call.description = f'Responder places 3N after opener shows minor side suit {side_suit} in the 2/1 game force.'
                call.system_notes = f'After {opening}-{response}-{rebid}, 3N is the practical game placement.'


def _two_over_one_side_rebid_cases():
    return (
        ('1S', '2C', '2D', 'D'),
        ('1S', '2C', '2H', 'H'),
        ('1S', '2D', '2H', 'H'),
        ('1H', '2C', '2D', 'D'),
        ('1H', '2C', '2S', 'S'),
        ('1H', '2D', '2S', 'S'),
    )
