"""Conservative executable slice of Daqiush's game-forcing five-major inquiry."""


def inquiry_hand(ctx):
    if ctx.hand is None:
        return False
    majors = [ctx.hand.length(s) for s in 'HS']
    ordinary = (max(majors) == 3 and min(majors) >= 2
                and max(ctx.hand.length(s) for s in 'CD') < 6
                and not (max(ctx.hand.length(s) for s in 'CD') >= 5
                         and ctx.hand.hcp >= 12 and ctx.hand_quality['kr_points'] >= 14)
                and not (ctx.hand.length('C') == 4 and ctx.hand.length('D') == 4
                         and ctx.hand.hcp >= 12 and ctx.hand_quality['kr_points'] >= 14))
    shortage = (sorted(majors) == [1, 3]
                and sorted(ctx.hand.length(s) for s in 'CD') == [4, 5])
    solid_clubs = (ctx.hand.length('C') == 6 and max(majors) == 3
                   and ctx.hand.honor_count('C', ('A', 'K', 'Q')) == 3
                   and ctx.hand.hcp >= 8)
    flat_game = (sorted(ctx.hand.length(s) for s in 'SHDC') == [3, 3, 3, 4]
                 and 10 <= ctx.hand.hcp <= 17)
    return (((ordinary or shortage) and 10 <= ctx.hand.hcp <= 15)
            or good_minor_5422(ctx) or solid_clubs or flat_game)


def flat_high_quantitative(ctx):
    return (ctx.hand is not None
            and sorted(ctx.hand.length(s) for s in 'SHDC') == [3, 3, 3, 4]
            and ctx.hand.hcp in (16, 17) and ctx.hand_quality['good'])


def good_minor_5422(ctx):
    return (ctx.hand is not None and ctx.hand.hcp in (14, 15)
            and ctx.hand_quality['good']
            and sorted(ctx.hand.length(s) for s in 'HS') == [2, 2]
            and sorted(ctx.hand.length(s) for s in 'CD') == [4, 5])


def singleton_major(ctx):
    if ctx.hand is None or sorted(ctx.hand.length(s) for s in 'HS') != [1, 3]:
        return None
    if sorted(ctx.hand.length(s) for s in 'CD') != [4, 5]:
        return None
    return 'H' if ctx.hand.length('H') == 1 else 'S'


def other_major(suit):
    return 'S' if suit == 'H' else 'H'


def five_four_minor(ctx, five, four):
    return (ctx.hand is not None
            and ctx.hand.length(five) == 5
            and ctx.hand.length(four) == 4
            and sorted(ctx.hand.length(s) for s in 'HS') == [1, 3])


def five_four_shortage(ctx):
    return (five_four_minor(ctx, 'C', 'D')
            or five_four_minor(ctx, 'D', 'C'))


def both_minor_special(ctx, shortage):
    if ctx.hand is None or any(ctx.hand.length(s) < 4 for s in 'CD'):
        return False
    if minor_game_control_points(
            ctx.hand, 'D', partner_long_suits=('C',)) < 14.5:
        return False
    holding = ctx.hand.holding(shortage)
    side_honors = {rank for rank in 'KQJ' if rank in holding}
    return not side_honors or (side_honors == {'K'} and 'A' in holding)


def singleton_route(ctx, shortage):
    """Return only the unique deterministic no-DDS continuation."""
    if ctx.hand is None:
        return None
    if both_minor_special(ctx, shortage):
        return '4' + shortage

    long_minors = [suit for suit in 'CD' if ctx.hand.length(suit) >= 4]
    ambiguous_minors = len(long_minors) == 2
    candidates = []
    if len(long_minors) == 1:
        candidates.append('4' + long_minors[0])

    other = other_major(shortage)
    if (ctx.hand.length(other) == 4
            and all(ctx.hand.length(suit) < 4 for suit in 'CD')):
        candidates.append('4' + other)
    elif all(ctx.hand.length(suit) == 3 for suit in 'CD'):
        candidates.append('4NT')

    stopped = inquiry_stopper(ctx.hand, shortage)
    if stopped and not candidates and not ambiguous_minors:
        return '3NT'
    if not stopped and len(candidates) == 1:
        return candidates[0]
    return None


def major_fit(ctx, major):
    return (five_four_shortage(ctx)
            and ctx.hand.length(major) == 3)


def major_singleton(ctx, major):
    return (five_four_shortage(ctx)
            and ctx.hand.length(major) == 1)


def set_agreed_suit(call, suit):
    call.meaning.agreed_suit = suit
    call.effect('agreed_suit').suit = suit


def set_final(call, target):
    call.meaning.acts = ['signoff', 'final_placement']
    call.meaning.target_suit = target
    call.meaning.purpose_completed = True


class FiveCardMajorInquiry(Gadget):
    id = 'five_card_major_inquiry'
    namespace = 'daqiush_2over1'
    name = '1NT–3C five-card major inquiry'
    author = Author('Daqiush')

    def build(self):
        ask = self.call('ask_five_card_major')
        ask.when = '1NP'
        ask.bid = '3C'
        ask.applies = inquiry_hand
        ask.meaning.action = 'five_card_major_inquiry'
        ask.meaning.nature = ['artificial']
        ask.meaning.acts = ['inquiry', 'game_forcing']
        ask.meaning.forcing = 'game_forcing'
        ask.description = 'Game-forcing inquiry for a five-card major; this slice handles 3-2 or 3-3 majors.'

        for answer, applies, suit in (
            ('3D', lambda ctx: ctx.hand is not None and max(ctx.hand.length(s) for s in 'HS') < 5, None),
            ('3H', lambda ctx: ctx.hand is not None and ctx.hand.length('H') >= 5, 'H'),
            ('3S', lambda ctx: ctx.hand is not None and ctx.hand.length('H') < 5
             and ctx.hand.length('S') >= 5, 'S'),
        ):
            reply = self.call('answer_' + answer.lower())
            reply.when = '1NP3CP'
            reply.bid = answer
            reply.applies = applies
            reply.meaning.action = 'five_card_major_reply'
            reply.meaning.nature = ['artificial' if answer == '3D' else 'natural']
            reply.meaning.acts = ['descriptive']
            if suit:
                reply.meaning.target_suit = suit
            reply.description = 'Show a five-card major, or deny one with 3D.'

            if suit:
                prefix = '1NP3CP' + answer + 'P'
                game = self.call('five_three_' + suit.lower() + '_game')
                game.when = prefix
                game.bid = '4' + suit
                game.applies = (lambda ctx, s=suit: inquiry_hand(ctx)
                                and ctx.hand.length(s) >=
                                (4 if sorted(ctx.hand.length(x) for x in 'SHDC')
                                 == [3, 3, 3, 4] else 3))
                game.meaning.action = 'five_card_major_game_placement'
                game.meaning.nature = ['natural']
                set_final(game, suit)
                set_agreed_suit(game, suit)
                game.description = 'Use the five-three major fit and play game.'

                notrump = self.call('five_one_' + suit.lower() + '_three_notrump')
                notrump.when = prefix
                notrump.bid = '3NT'
                notrump.applies = (lambda ctx, s=suit: inquiry_hand(ctx)
                                   and ctx.hand.length(s) <
                                   (4 if sorted(ctx.hand.length(x) for x in 'SHDC')
                                    == [3, 3, 3, 4] else 3))
                notrump.meaning.action = 'five_card_major_game_placement'
                notrump.meaning.nature = ['natural']
                set_final(notrump, 'N')
                notrump.description = 'Without a usable fit, play three notrump.'

                strength = self.call('five_three_' + suit.lower() + '_strength_show')
                strength.when = prefix
                strength.bid = ('3S' if suit == 'H' else '4H')
                strength.applies = (lambda ctx, s=suit: major_fit(ctx, s))
                strength.meaning.action = 'five_three_major_strength_show'
                strength.meaning.nature = ['artificial']
                strength.meaning.acts = ['slam_try', 'strength_showing']
                strength.meaning.target_suit = suit
                set_agreed_suit(strength, suit)
                strength.description = ('The lowest legal other-major call shows '
                                        'slam interest in the known five-three fit.')

                for five, four in (('C', 'D'), ('D', 'C')):
                    minor = self.call('five_one_' + suit.lower() + '_show_'
                                      + five.lower() + four.lower())
                    minor.when = prefix
                    minor.bid = '4' + five
                    minor.applies = (lambda ctx, s=suit, f=five, o=four:
                                     major_singleton(ctx, s)
                                     and five_four_minor(ctx, f, o))
                    minor.meaning.action = 'five_four_minor_shape'
                    minor.meaning.nature = ['natural']
                    minor.meaning.acts = ['descriptive', 'slam_try']
                    minor.meaning.target_suit = five
                    minor.meaning.five_card_suit = five
                    minor.meaning.four_card_suit = four
                    minor.meaning.min_lengths = {five: 5, four: 4}
                    minor.meaning.max_lengths = {five: 5, four: 4}
                    minor.description = ('With a singleton in opener’s major, '
                                         'show the five-card minor and slam interest.')

        quantitative = self.call('flat_4333_quantitative_after_denial')
        quantitative.when = '1NP3CP3DP'
        quantitative.bid = '4NT'
        quantitative.applies = flat_high_quantitative
        quantitative.meaning.action = 'quantitative_notrump_invitation'
        quantitative.meaning.nature = ['natural']
        quantitative.meaning.acts = ['invite']
        quantitative.meaning.target_suit = 'N'
        quantitative.description = 'A good 16–17 HCP 4333 invites 6NT after the five-major inquiry denies a fit.'

        for bid, high in (('P', False), ('6NT', True)):
            answer = self.call('flat_4333_quantitative_' + bid.lower())
            answer.when = '1NP3CP3DP4NP'
            answer.bid = bid
            answer.applies = lambda ctx, strong=high: ctx.hand is not None and (ctx.hand.hcp >= 17) == strong
            answer.meaning.action = 'quantitative_notrump_' + ('accept' if high else 'reject')
            answer.meaning.nature = ['natural']
            answer.meaning.acts = ['accept' if high else 'reject', 'final_placement']
            answer.meaning.target_suit = 'N'
            answer.meaning.purpose_completed = True
            answer.description = 'Answer the natural quantitative 6NT invitation.'

        for shortage in 'HS':
            show = self.call('show_singleton_' + shortage.lower())
            show.when = '1NP3CP3DP'
            show.bid = '3' + shortage
            show.applies = lambda ctx, s=shortage: inquiry_hand(ctx) and singleton_major(ctx) == s
            show.meaning.action = 'show_singleton_major'
            show.meaning.nature = ['artificial']
            show.meaning.acts = ['descriptive']
            show.meaning.short_suit = shortage
            show.description = 'After 3D denies a five-card major, show the singleton major in 3-1-5-4.'

            continuation = '1NP3CP3DP3' + shortage + 'P'
            finish = self.call('stopper_after_singleton_' + shortage.lower())
            finish.when = continuation
            finish.bid = '3NT'
            finish.applies = lambda ctx, s=shortage: (ctx.hand is not None
                                                      and inquiry_stopper(ctx.hand, s))
            finish.meaning.action = 'singleton_major_three_notrump'
            finish.meaning.nature = ['natural']
            set_final(finish, 'N')
            finish.description = 'Opener has a stopper in the shown singleton major; play 3NT.'

            special = self.call('both_minors_after_singleton_' + shortage.lower())
            special.when = continuation
            special.bid = '4' + shortage
            special.applies = lambda ctx, s=shortage: both_minor_special(ctx, s)
            special.meaning.action = 'set_diamonds_with_both_minors'
            special.meaning.nature = ['artificial']
            special.meaning.acts = ['trump_setting']
            special.meaning.target_suit = 'D'
            set_agreed_suit(special, 'D')
            special.description = 'Both minors are playable; this artificial call sets diamonds, not a control.'

            for minor_suit in 'CD':
                choose_minor = self.call('set_' + minor_suit.lower()
                                         + '_after_singleton_' + shortage.lower())
                choose_minor.when = continuation
                choose_minor.bid = '4' + minor_suit
                choose_minor.applies = (lambda ctx, s=shortage, m=minor_suit:
                                        ctx.hand is not None
                                        and ctx.hand.length(m) >= 4
                                        and not both_minor_special(ctx, s))
                choose_minor.meaning.action = 'set_minor_trump'
                choose_minor.meaning.nature = ['natural']
                choose_minor.meaning.acts = ['trump_setting']
                choose_minor.meaning.target_suit = minor_suit
                set_agreed_suit(choose_minor, minor_suit)
                choose_minor.description = 'Choose the unique four-card minor as trumps.'

            other = other_major(shortage)
            choose_major = self.call('place_other_major_after_singleton_'
                                     + shortage.lower())
            choose_major.when = continuation
            choose_major.bid = '4' + other
            choose_major.applies = (lambda ctx, s=shortage, o=other:
                                    ctx.hand is not None
                                    and ctx.hand.length(o) == 4
                                    and all(ctx.hand.length(x) < 4 for x in 'CD')
                                    and not both_minor_special(ctx, s))
            choose_major.meaning.action = 'other_major_four_three_fit'
            choose_major.meaning.nature = ['natural']
            choose_major.meaning.acts = ['descriptive']
            choose_major.meaning.target_suit = other
            set_agreed_suit(choose_major, other)
            choose_major.description = 'Place the contract in the known four-three other-major fit.'

            other_prefix = continuation + '4' + other + 'P'
            stop_other = self.call('stop_in_other_major_after_singleton_'
                                   + shortage.lower())
            stop_other.when = other_prefix
            stop_other.bid = 'P'
            stop_other.applies = lambda ctx: five_four_shortage(ctx)
            stop_other.meaning.action = 'other_major_game_signoff'
            stop_other.meaning.nature = ['natural']
            set_final(stop_other, other)
            stop_other.description = 'With no remaining slam interest, stop in the other-major game.'

            for five, four in (('C', 'D'), ('D', 'C')):
                show_minor = self.call('other_major_then_' + five.lower()
                                       + '_after_' + shortage.lower())
                show_minor.when = other_prefix
                show_minor.bid = '5' + five
                show_minor.applies = (lambda ctx, f=five, o=four:
                                      five_four_minor(ctx, f, o))
                show_minor.meaning.action = 'other_major_show_five_card_minor'
                show_minor.meaning.nature = ['natural']
                show_minor.meaning.acts = ['descriptive', 'slam_try']
                show_minor.meaning.target_suit = five
                show_minor.meaning.five_card_suit = five
                show_minor.description = 'Name the lowest legal five-card minor for final strain comparison.'

                for finish_bid, finish_trump in (
                        ('P', five), ('5' + other, other),
                        ('6' + five, five), ('6' + other, other)):
                    finish = self.call('finish_' + finish_bid.lower()
                                       + '_after_' + five.lower()
                                       + '_' + shortage.lower())
                    finish.when = other_prefix + '5' + five + 'P'
                    finish.bid = finish_bid
                    finish.applies = lambda ctx: ctx.hand is not None
                    finish.meaning.action = 'five_major_final_strain'
                    finish.meaning.nature = ['natural']
                    finish.meaning.acts = ['signoff', 'final_placement']
                    finish.meaning.target_suit = finish_trump
                    finish.meaning.agreed_suit = finish_trump
                    finish.meaning.purpose_completed = True
                    finish.effect('agreed_suit').suit = finish_trump
                    finish.description = ('Compare the five-card minor and other '
                                          'major; final placement.')

            three_three = self.call('three_three_minors_after_singleton_'
                                    + shortage.lower())
            three_three.when = continuation
            three_three.bid = '4NT'
            three_three.applies = (lambda ctx, s=shortage: (
                ctx.hand is not None
                and ctx.hand.length('C') == 3 and ctx.hand.length('D') == 3
                and ctx.hand.length(other_major(s)) != 4))
            three_three.meaning.action = 'three_three_minor_placement_request'
            three_three.meaning.nature = ['artificial']
            three_three.meaning.acts = ['inquiry']
            three_three.description = 'With exactly three-three minors, ask responder for the five-card minor.'

            three_three_prefix = continuation + '4NTP'
            for five, four in (('C', 'D'), ('D', 'C')):
                fallback = self.call('three_three_fallback_' + five.lower()
                                     + '_after_' + shortage.lower())
                fallback.when = three_three_prefix
                fallback.bid = '5' + five
                fallback.applies = lambda ctx, f=five, o=four: five_four_minor(ctx, f, o)
                fallback.meaning.action = 'five_card_minor_game_placement'
                fallback.meaning.nature = ['natural']
                set_final(fallback, five)
                set_agreed_suit(fallback, five)
                fallback.description = 'Name the five-card minor and stop at game without DDS.'

                slam = self.call('three_three_slam_' + five.lower()
                                 + '_after_' + shortage.lower())
                slam.when = three_three_prefix
                slam.bid = '6' + five
                slam.applies = lambda ctx, f=five, o=four: five_four_minor(ctx, f, o)
                slam.meaning.action = 'five_card_minor_slam_placement'
                slam.meaning.nature = ['natural']
                set_final(slam, five)
                set_agreed_suit(slam, five)
                slam.description = 'Name the five-card minor for the small slam.'

        for shown_major in 'HS':
            major_prefix = '1NP3CP3' + shown_major + 'P'
            for shown_minor, selectors in (
                    ('C', (('4D', 'D', False), ('4H', 'C', False),
                           ('4S', 'C', False), ('5C', 'C', True))),
                    ('D', (('4H', 'C', False), ('4S', 'D', False)))):
                selector_prefix = major_prefix + '4' + shown_minor + 'P'
                for selector_bid, trump, final in selectors:
                    selector = self.call('select_' + trump.lower() + '_after_'
                                         + shown_major.lower() + '_4'
                                         + shown_minor.lower() + '_'
                                         + selector_bid.lower())
                    selector.when = selector_prefix
                    selector.bid = selector_bid
                    selector.applies = lambda ctx: ctx.hand is not None
                    selector.meaning.action = 'select_minor_trump'
                    selector.meaning.nature = ['artificial']
                    selector.meaning.acts = ['trump_setting']
                    selector.meaning.target_suit = trump
                    set_agreed_suit(selector, trump)
                    if final:
                        set_final(selector, trump)
                    selector.description = ('Select the minor trump; the suit bid '
                                            'does not promise a control.')

        ordinary_notrump = self.call('ordinary_three_notrump_after_denial')
        ordinary_notrump.when = '1NP3CP3DP'
        ordinary_notrump.bid = '3NT'
        ordinary_notrump.applies = (lambda ctx: inquiry_hand(ctx)
                                    and singleton_major(ctx) is None
                                    and not good_minor_5422(ctx)
                                    and not flat_high_quantitative(ctx))
        ordinary_notrump.meaning.action = 'five_card_major_game_placement'
        ordinary_notrump.meaning.nature = ['natural']
        set_final(ordinary_notrump, 'N')
        ordinary_notrump.description = 'With no five-card-major fit or special minor route, play three notrump.'

        probe = self.call('good_5422_minor_slam_probe')
        probe.when = '1NP3CP3DP'
        probe.bid = '4NT'
        probe.applies = good_minor_5422
        probe.meaning.action = 'minor_slam_probe'
        probe.meaning.nature = ['artificial']
        probe.meaning.acts = ['slam_try']
        probe.meaning.shape_class = 'minor_5422'
        probe.meaning.hcp_min = 14
        probe.meaning.hcp_max = 15
        probe.description = ('Good 14–15 HCP minor 5-4-2-2 probes for a minor slam; '
                             'later calls require sampled-deal evaluation.')
        probe.priority = 1

        for level in (5, 6):
            for minor in 'CD':
                placement = self.call('good_5422_simulated_' + str(level) + minor.lower())
                placement.when = '1NP3CP3DP4NTP'
                placement.bid = str(level) + minor
                placement.applies = lambda ctx: ctx.hand is not None
                placement.meaning.action = 'simulated_minor_placement'
                placement.meaning.nature = ['natural']
                placement.meaning.acts = ['signoff', 'final_placement']
                placement.meaning.target_suit = minor
                placement.meaning.purpose_completed = True
                placement.description = 'Chosen by public-information sampled DDS decision.'

        choice = self.call('three_three_minor_choice_5nt')
        choice.when = '1NP3CP3DP4NTP'
        choice.bid = '5NT'
        choice.applies = (lambda ctx: ctx.hand is not None
                          and sorted(ctx.hand.length(s) for s in 'CD') == [3, 3])
        choice.meaning.action = 'minor_suit_choice_ask'
        choice.meaning.nature = ['artificial']
        choice.meaning.acts = ['inquiry']
        choice.description = ('With 3-3 minors ask responder to name the '
                              'five-card minor at the six level.')

        for minor in 'CD':
            named = self.call('three_three_minor_choice_6' + minor.lower())
            named.when = '1NP3CP3DP4NTP5NTP'
            named.bid = '6' + minor
            named.applies = (lambda ctx, m=minor: ctx.hand is not None
                             and ctx.hand.length(m) >= 5)
            named.meaning.action = 'five_card_minor_placement'
            named.meaning.nature = ['natural']
            named.meaning.acts = ['signoff', 'final_placement']
            named.meaning.target_suit = minor
            named.meaning.purpose_completed = True
            named.description = 'Name the five-card minor for the slam.'

        no_minor = self.call('three_three_minor_choice_6nt')
        no_minor.when = '1NP3CP3DP4NTP5NTP'
        no_minor.bid = '6NT'
        no_minor.applies = (lambda ctx: ctx.hand is not None
                            and max(ctx.hand.length(s) for s in 'CD') < 5)
        no_minor.meaning.action = 'minor_choice_no_five_card_minor'
        no_minor.meaning.nature = ['natural']
        no_minor.meaning.acts = ['signoff', 'final_placement']
        no_minor.meaning.target_suit = 'N'
        no_minor.meaning.purpose_completed = True
        no_minor.description = 'Without a five-card minor, play 6NT.'
