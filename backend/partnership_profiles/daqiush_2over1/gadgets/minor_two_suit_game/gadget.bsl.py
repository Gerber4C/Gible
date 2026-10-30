"""Game-only 1NT–3D route with exactly five cards in each minor."""


def exact_minor_two_suit_game(ctx):
    """Five-five, or strong six-five, minors at game-forcing strength."""
    lengths = None if ctx.hand is None else sorted(
        (ctx.hand.length('C'), ctx.hand.length('D')))
    return (lengths in ([5, 5], [5, 6])
            and (ctx.hand.hcp >= 10
                 or (ctx.hand.hcp == 9
                     and ctx.hand_quality['kr_delta'] >= 1.0)))


def six_five_minor_choice(ctx):
    lengths = None if ctx.hand is None else sorted(
        ctx.hand.length(s) for s in 'CD')
    return (lengths is not None and lengths[0] >= 5 and lengths[1] >= 6
            and shapely_combined_effective_points(ctx.hand) >= 7
            and not exact_minor_two_suit_game(ctx))


def six_five_after_diamond_transfer(ctx):
    # Weak 6D-5C hands intentionally have no defined 3H convention here;
    # they fall through to the existing transfer-stop/pass route.
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


def five_five_minors(ctx):
    return (ctx.hand is not None and ctx.hand.length('C') == 5
            and ctx.hand.length('D') == 5)


def six_five_minors(ctx):
    if ctx.hand is None:
        return False
    return sorted((ctx.hand.length('C'), ctx.hand.length('D'))) == [5, 6]


def six_card_minor(ctx):
    return 'D' if ctx.hand.length('D') == 6 else 'C'


def extra_minor_slam_interest(ctx):
    return ctx.hand is not None and minor_slam_interest(ctx.hand)


def shortage_in(ctx, suit):
    return ctx.hand is not None and ctx.hand.length(suit) <= 1


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
        ask.description = 'Five-five or strong six-five minors at game-forcing strength.'

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
            reply.meaning.acts = ['descriptive']
            reply.meaning.target_suit = 'N' if answer == '3NT' else stopper_suit
            reply.description = 'Show the available major stopper; responder may pass or continue.'

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

        # After opener's stopper reply, responder can stop in 3NT (only after
        # the both-stoppers 3NT), choose a minor game with 4NT, show a
        # six-card minor at the four level with 6-5, or show major shortage
        # with 5-5.
        for prefix in ('1NP3DP3NP', '1NP3DP3HP', '1NP3DP3SP'):
            if prefix.endswith('3NP'):
                pass_3nt = self.call('two_minor_pass_after_3nt')
                pass_3nt.when = prefix
                pass_3nt.bid = 'P'
                pass_3nt.applies = (lambda ctx: ctx.hand is not None
                                    and not extra_minor_slam_interest(ctx))
                pass_3nt.meaning.action = 'two_minor_three_notrump_signoff'
                pass_3nt.meaning.nature = ['natural']
                pass_3nt.meaning.acts = ['signoff', 'final_placement']
                pass_3nt.meaning.target_suit = 'N'
                pass_3nt.meaning.purpose_completed = True
                pass_3nt.description = 'Without extra slam strength, play 3NT.'

            for minor in 'CD':
                length = self.call('two_minor_six_card_' + prefix[-3:].lower()
                                   + '_' + minor.lower())
                length.when = prefix
                length.bid = '4' + minor
                length.applies = (lambda ctx, m=minor: (
                    six_five_minors(ctx)
                    and extra_minor_slam_interest(ctx)
                    and six_card_minor(ctx) == m))
                length.meaning.action = 'minor_six_card_slam_try'
                length.meaning.nature = ['natural']
                length.meaning.acts = ['slam_try']
                length.meaning.target_suit = minor
                length.description = ('Six-five shape: bid four of the '
                                      'six-card minor as a slam try.')

                choose = self.call('two_minor_four_notrump_' + prefix[-3:].lower()
                                   + '_' + minor.lower())
                choose.when = prefix + '4NTP'
                choose.bid = '5' + minor
                choose.applies = (lambda ctx, m=minor: (
                    ctx.hand is not None and preferred_minor(ctx) == m))
                choose.meaning.action = 'chosen_minor_game'
                choose.meaning.nature = ['natural']
                choose.meaning.acts = ['signoff', 'final_placement']
                choose.meaning.target_suit = minor
                choose.meaning.purpose_completed = True
                choose.description = 'Choose the better minor game.'

            for suit in 'HS':
                shortage = self.call('two_minor_shortage_' + prefix[-3:].lower()
                                     + '_' + suit.lower())
                shortage.when = prefix
                shortage.bid = '4' + suit
                shortage.applies = (lambda ctx, s=suit: (
                    five_five_minors(ctx)
                    and extra_minor_slam_interest(ctx)
                    and shortage_in(ctx, s)))
                shortage.meaning.action = 'minor_shortage_slam_try'
                shortage.meaning.nature = ['artificial']
                shortage.meaning.acts = ['slam_try', 'control_showing']
                shortage.meaning.shortage_suit = suit
                shortage.meaning.target_suit = suit
                shortage.description = 'Five-five shape: show a major singleton or void as a slam try.'

            game_choice = self.call('two_minor_four_notrump_' + prefix[-3:].lower())
            game_choice.when = prefix
            game_choice.bid = '4NT'
            game_choice.applies = (lambda ctx, p=prefix: (
                (five_five_minors(ctx) or six_five_minors(ctx))
                and (not p.endswith('3NP') or extra_minor_slam_interest(ctx))))
            game_choice.meaning.action = 'minor_game_choice'
            game_choice.meaning.nature = ['artificial']
            game_choice.meaning.acts = ['inquiry', 'game_forcing']
            game_choice.meaning.forcing = 'game_forcing'
            game_choice.meaning.target_suit = 'N'
            game_choice.description = 'Ask opener to choose five clubs or five diamonds.'
