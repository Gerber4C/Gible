# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def notrump_focus_active(ctx):
    return ctx.state.exists('notrump_focus', status='active')


def responder_starts_puppet_over_2n(ctx):
    return (
        ctx.hand.hcp >= 4
        and ctx.hand.length('H') <= 4
        and ctx.hand.length('S') <= 4
        and (ctx.hand.length('H') == 4 or ctx.hand.length('S') == 4)
    )


def opener_has_five_hearts(ctx):
    return ctx.hand.length('H') >= 5


def opener_has_five_spades(ctx):
    return ctx.hand.length('S') >= 5


def opener_has_four_card_major_without_five(ctx):
    hearts = ctx.hand.length('H')
    spades = ctx.hand.length('S')
    return hearts < 5 and spades < 5 and (hearts == 4 or spades == 4)


def opener_has_no_four_or_five_card_major(ctx):
    return ctx.hand.length('H') <= 3 and ctx.hand.length('S') <= 3


def responder_supports_hearts(ctx):
    return ctx.hand.length('H') >= 3


def responder_lacks_heart_support(ctx):
    return ctx.hand.length('H') < 3


def responder_supports_spades(ctx):
    return ctx.hand.length('S') >= 3


def responder_lacks_spade_support(ctx):
    return ctx.hand.length('S') < 3


def responder_has_spades_only(ctx):
    return ctx.hand.length('S') == 4 and ctx.hand.length('H') < 4


def responder_has_hearts_only(ctx):
    return ctx.hand.length('H') == 4 and ctx.hand.length('S') < 4


def responder_has_both_majors(ctx):
    return ctx.hand.length('H') == 4 and ctx.hand.length('S') == 4


def opener_has_four_hearts(ctx):
    return ctx.hand.length('H') == 4


def opener_lacks_four_hearts(ctx):
    return ctx.hand.length('H') < 4


def opener_has_four_spades(ctx):
    return ctx.hand.length('S') == 4


def opener_lacks_four_spades(ctx):
    return ctx.hand.length('S') < 4


def opener_prefers_spades_with_both_major_fits(ctx):
    return ctx.hand.length('S') == 4


def opener_chooses_hearts_without_spade_fit(ctx):
    return ctx.hand.length('S') < 4 and ctx.hand.length('H') == 4


class MeowPuppetStaymanOver2nGadget(Gadget):
    id = 'meow_puppet_stayman_over_2n'
    namespace = 'meow_2over1'
    name = 'Meow Puppet Stayman Over 2N'
    version = '0.1.0'
    description = 'Puppet Stayman over 2N as a dialogue flow: responder asks with 3C, opener answers, responder clarifies major interest, and opener places the contract when a precise fit is found.\n'
    author = Author('Meow Li')

    def build(self):
        puppet = self.puppet_stayman('puppet_2n')
        puppet.over = '2N'
        puppet.ask = '3C'
        puppet.seats = [1, 2, 3, 4]
        puppet.notrump_level = 2
        puppet.ask_requires = notrump_focus_active
        puppet.ask_applies = responder_starts_puppet_over_2n
        puppet.description = 'Responder uses 3C as Puppet Stayman over 2N with at least one four-card major and no five-card major.'
        puppet.system_notes = 'After 2N, 3C is Puppet Stayman, normally with a four-card major and no five-card major.'

        answer = puppet.answer('3D', applies=opener_has_four_card_major_without_five)
        answer.shows_length('H', max=4).shows_length('S', max=4)
        answer.effect('opener.major_length_max', value=4, min_value=4, max_value=4)
        answer.description = 'Opener denies a five-card major and shows at least one four-card major.'
        answer.system_notes = 'After 2N-3C, 3D denies a five-card major and shows at least one four-card major.'

        answer = puppet.answer('3H', applies=opener_has_five_hearts, target_suit='H')
        answer.shows_length('H', min=5)
        answer.description = 'Opener shows five or more hearts.'
        answer.system_notes = 'After 2N-3C, 3H shows a five-card heart suit.'

        answer = puppet.answer('3S', applies=opener_has_five_spades, target_suit='S')
        answer.shows_length('S', min=5)
        answer.description = 'Opener shows five or more spades.'
        answer.system_notes = 'After 2N-3C, 3S shows a five-card spade suit.'

        answer = puppet.answer('3N', applies=opener_has_no_four_or_five_card_major, target_suit='N')
        answer.shows_length('H', max=3).shows_length('S', max=3)
        answer.description = 'Opener denies a four- or five-card major.'
        answer.system_notes = 'After 2N-3C, 3N denies a four- or five-card major.'

        continuation = puppet.continuation(after='3H', bid='4H', applies=responder_supports_hearts, final=True, target_suit='H')
        continuation.shows_length('H', min=3).records_fit('H', opener_min=5, responder_min=3, basis='puppet_2n_5_3_heart_fit')
        continuation.description = 'Responder raises opener five-card hearts to game with at least three-card support.'
        continuation.system_notes = 'After 2N-3C-3H, 4H places game with at least three-card heart support.'

        continuation = puppet.continuation(after='3H', bid='3N', applies=responder_lacks_heart_support, final=True, target_suit='N')
        continuation.shows_length('H', max=2)
        continuation.description = 'Responder places 3N without three-card heart support.'
        continuation.system_notes = 'After 2N-3C-3H, 3N denies three-card heart support.'

        continuation = puppet.continuation(after='3S', bid='4S', applies=responder_supports_spades, final=True, target_suit='S')
        continuation.shows_length('S', min=3).records_fit('S', opener_min=5, responder_min=3, basis='puppet_2n_5_3_spade_fit')
        continuation.description = 'Responder raises opener five-card spades to game with at least three-card support.'
        continuation.system_notes = 'After 2N-3C-3S, 4S places game with at least three-card spade support.'

        continuation = puppet.continuation(after='3S', bid='3N', applies=responder_lacks_spade_support, final=True, target_suit='N')
        continuation.shows_length('S', max=2)
        continuation.description = 'Responder places 3N without three-card spade support.'
        continuation.system_notes = 'After 2N-3C-3S, 3N denies three-card spade support.'

        continuation = puppet.continuation(after='3D', bid='3H', applies=responder_has_spades_only, target_suit='S')
        continuation.shows_length('S', value=4).shows_length('H', max=3)
        continuation.description = 'Responder shows four spades and denies four hearts.'
        continuation.system_notes = 'After 2N-3C-3D, 3H shows four spades and denies four hearts.'

        continuation = puppet.continuation(after='3D', bid='3S', applies=responder_has_hearts_only, target_suit='H')
        continuation.shows_length('H', value=4).shows_length('S', max=3)
        continuation.description = 'Responder shows four hearts and denies four spades.'
        continuation.system_notes = 'After 2N-3C-3D, 3S shows four hearts and denies four spades.'

        continuation = puppet.continuation(after='3D', bid='4D', applies=responder_has_both_majors)
        continuation.shows_length('H', value=4).shows_length('S', value=4)
        continuation.description = 'Responder shows both majors, allowing opener to choose the major-suit game.'
        continuation.system_notes = 'After 2N-3C-3D, 4D shows both majors and asks opener to choose.'

        resolution = puppet.resolution(after_answer='3D', after_continuation='3H', bid='4S', applies=opener_has_four_spades, target_suit='S')
        resolution.shows_length('S', value=4).records_fit('S', opener_min=4, responder_min=4, basis='puppet_2n_4_4_spade_fit')
        resolution.description = 'Opener places 4S with four spades opposite responder four spades.'
        resolution.system_notes = 'After 2N-3C-3D-3H, 4S confirms a 4-4 spade fit.'

        resolution = puppet.resolution(after_answer='3D', after_continuation='3H', bid='3N', applies=opener_lacks_four_spades, target_suit='N')
        resolution.shows_length('S', max=3)
        resolution.description = 'Opener places 3N without four spades.'
        resolution.system_notes = 'After 2N-3C-3D-3H, 3N denies a spade fit.'

        resolution = puppet.resolution(after_answer='3D', after_continuation='3S', bid='4H', applies=opener_has_four_hearts, target_suit='H')
        resolution.shows_length('H', value=4).records_fit('H', opener_min=4, responder_min=4, basis='puppet_2n_4_4_heart_fit')
        resolution.description = 'Opener places 4H with four hearts opposite responder four hearts.'
        resolution.system_notes = 'After 2N-3C-3D-3S, 4H confirms a 4-4 heart fit.'

        resolution = puppet.resolution(after_answer='3D', after_continuation='3S', bid='3N', applies=opener_lacks_four_hearts, target_suit='N')
        resolution.shows_length('H', max=3)
        resolution.description = 'Opener places 3N without four hearts.'
        resolution.system_notes = 'After 2N-3C-3D-3S, 3N denies a heart fit.'

        resolution = puppet.resolution(after_answer='3D', after_continuation='4D', bid='4S', applies=opener_prefers_spades_with_both_major_fits, target_suit='S')
        resolution.shows_length('S', value=4).records_fit('S', opener_min=4, responder_min=4, basis='puppet_2n_both_majors_spades')
        resolution.description = 'Opener chooses 4S with four spades when responder shows both majors.'
        resolution.system_notes = 'After 2N-3C-3D-4D, 4S chooses spades.'

        resolution = puppet.resolution(after_answer='3D', after_continuation='4D', bid='4H', applies=opener_chooses_hearts_without_spade_fit, target_suit='H')
        resolution.shows_length('H', value=4).records_fit('H', opener_min=4, responder_min=4, basis='puppet_2n_both_majors_hearts')
        resolution.description = 'Opener chooses 4H with four hearts and no four-card spade fit when responder shows both majors.'
        resolution.system_notes = 'After 2N-3C-3D-4D, 4H chooses hearts when opener lacks four spades.'
