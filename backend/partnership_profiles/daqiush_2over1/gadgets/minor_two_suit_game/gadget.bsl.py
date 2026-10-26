"""Game-only 1NT–3D route with exactly five cards in each minor."""


def exact_minor_two_suit_game(ctx):
    return (ctx.hand is not None and ctx.hand.length('C') == 5
            and ctx.hand.length('D') == 5
            and (10 <= ctx.hand.hcp <= 12
                 or (ctx.hand.hcp == 9 and ctx.hand_quality['kr_delta'] >= 1.0)))


def six_five_minor_choice(ctx):
    return (ctx.hand is not None
            and sorted(ctx.hand.length(s) for s in 'CD') == [5, 6]
            and shapely_combined_effective_points(ctx.hand) >= 7)


def six_five_after_diamond_transfer(ctx):
    return (ctx.hand is not None and ctx.hand.length('D') == 6
            and ctx.hand.length('C') == 5)


def six_five_transfer_strength(ctx):
    return shapely_combined_effective_points(ctx.hand) >= 7


def preferred_minor(ctx):
    return max('CD', key=lambda suit: (
        ctx.hand.length(suit),
        minor_game_control_points(ctx.hand, suit, partner_long_suits=('C', 'D')),
        ctx.hand.honor_count(suit, ('A', 'K', 'Q')), suit == 'C'))


def major_stopper(ctx, suit):
    holding = ctx.hand.holding(suit)
    return ('A' in holding or ('K' in holding and len(holding) >= 2)
            or ('Q' in holding and ('J' in holding or 'T' in holding)))


class MinorTwoSuitGame(Gadget):
    id = 'minor_two_suit_game'
    namespace = 'daqiush_2over1'
    name = '1NT–3D two-minor game force'
    author = Author('Daqiush')

    def build(self):
        route = self.call('six_five_after_diamond_transfer_select_minor')
        route.when = '1NP2NTP3DP'
        route.bid = '4NT'
        route.applies = (lambda ctx: six_five_after_diamond_transfer(ctx)
                         and six_five_transfer_strength(ctx))
        route.meaning.action = 'six_five_minor_select_minor'
        route.meaning.nature = ['artificial']
        route.meaning.acts = ['inquiry', 'game_forcing']
        route.meaning.target_suit = 'N'
        route.meaning.forcing = 'game_forcing'
        route.description = 'Use effective points to ask opener to choose between six-five minor games.'

        for prefix, label in (('1NP4NTP', 'direct'), ('1NP2NTP3DP4NP', 'after_diamond_transfer')):
            for minor in 'CD':
                answer = self.call('six_five_choose_' + label + '_' + minor.lower())
                answer.when = prefix
                answer.bid = '5' + minor
                answer.applies = lambda ctx, s=minor: (
                    ctx.hand is not None and preferred_minor(ctx) == s)
                answer.meaning.action = 'chosen_minor_game'
                answer.meaning.nature = ['natural']
                answer.meaning.acts = ['signoff', 'final_placement']
                answer.meaning.target_suit = minor
                answer.meaning.purpose_completed = True
                answer.description = 'Choose the minor with more support, then better controls.'

        choice = self.call('six_five_minor_game_choice')
        choice.when = '1NP'
        choice.bid = '4NT'
        choice.applies = six_five_minor_choice
        choice.meaning.action = 'choose_minor_game'
        choice.meaning.nature = ['artificial']
        choice.meaning.acts = ['inquiry', 'game_forcing']
        choice.meaning.forcing = 'game_forcing'
        choice.description = 'At least seven effective honor points in 6-5 minors: ask opener to choose the better minor game.'

        for minor in 'CD':
            answer = self.call('six_five_choose_' + minor.lower())
            answer.when = '1NP4NTP'
            answer.bid = '5' + minor
            answer.applies = lambda ctx, s=minor: ctx.hand is not None and preferred_minor(ctx) == s
            answer.meaning.action = 'chosen_minor_game'
            answer.meaning.nature = ['natural']
            answer.meaning.acts = ['signoff', 'final_placement']
            answer.meaning.target_suit = minor
            answer.meaning.purpose_completed = True
            answer.description = 'Choose the minor with more support, then better controls.'

        ask = self.call('five_five_minors')
        ask.when = '1NP'
        ask.bid = '3D'
        ask.applies = exact_minor_two_suit_game
        ask.meaning.action = 'two_minor_game_force'
        ask.meaning.nature = ['artificial']
        ask.meaning.acts = ['game_forcing']
        ask.meaning.forcing = 'game_forcing'
        ask.description = 'Five-five minors, game force; this executable slice is game only.'

        for answer, applies, stopper_suit in (
            ('3NT', lambda ctx: major_stopper(ctx, 'H') and major_stopper(ctx, 'S'), None),
            ('3H', lambda ctx: major_stopper(ctx, 'H') and not major_stopper(ctx, 'S'), 'H'),
            ('3S', lambda ctx: major_stopper(ctx, 'S') and not major_stopper(ctx, 'H'), 'S'),
        ):
            reply = self.call('stopper_' + answer.lower())
            reply.when = '1NP3DP'
            reply.bid = answer
            reply.applies = lambda ctx, test=applies: ctx.hand is not None and test(ctx)
            reply.meaning.action = 'major_stopper_reply'
            reply.meaning.nature = ['natural' if answer == '3NT' else 'artificial']
            reply.meaning.acts = ['signoff', 'final_placement'] if answer == '3NT' else ['descriptive']
            reply.meaning.target_suit = 'N' if answer == '3NT' else stopper_suit
            if answer == '3NT':
                reply.meaning.purpose_completed = True
            reply.description = 'Show the available major stopper or place 3NT with both.'

            if stopper_suit:
                other = 'S' if stopper_suit == 'H' else 'H'
                placement = self.call('other_stopper_after_' + answer.lower())
                placement.when = '1NP3DP' + answer + 'P'
                placement.bid = '3NT'
                placement.applies = lambda ctx, s=other: exact_minor_two_suit_game(ctx) and major_stopper(ctx, s)
                placement.meaning.action = 'two_minor_three_notrump'
                placement.meaning.nature = ['natural']
                placement.meaning.acts = ['signoff', 'final_placement']
                placement.meaning.target_suit = 'N'
                placement.meaning.purpose_completed = True
                placement.description = 'The responder has the other major stopper, so play 3NT.'
