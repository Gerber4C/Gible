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


def stopper(ctx, suit):
    holding = ctx.hand.holding(suit)
    return ('A' in holding or ('K' in holding and len(holding) >= 2)
            or ('Q' in holding and ('J' in holding or 'T' in holding)))


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

            prefix = '1NP3CP' + answer + 'P'
            for bid, fit in ((('4' + suit) if suit else None, True), ('3NT', False)):
                if bid is None:
                    continue
                placement = self.call('place_after_' + answer.lower() + '_' + bid.lower())
                placement.when = prefix
                placement.bid = bid
                placement.applies = (lambda ctx, s=suit, f=fit: inquiry_hand(ctx)
                                     and (s is not None and ctx.hand.length(s) >=
                                          (4 if sorted(ctx.hand.length(x) for x in 'SHDC')
                                           == [3, 3, 3, 4] else 3)) == f
                                     and (s is not None or singleton_major(ctx) is None)
                                     and (s is not None or not good_minor_5422(ctx))
                                     and (s is not None or not flat_high_quantitative(ctx)))
                placement.meaning.action = 'five_card_major_game_placement'
                placement.meaning.nature = ['natural']
                placement.meaning.acts = ['signoff', 'final_placement']
                placement.meaning.target_suit = suit if fit else 'N'
                placement.meaning.purpose_completed = True
                placement.description = 'Use the five-three major fit or play 3NT.'

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

            finish = self.call('stopper_after_singleton_' + shortage.lower())
            finish.when = '1NP3CP3DP3' + shortage + 'P'
            finish.bid = '3NT'
            finish.applies = lambda ctx, s=shortage: ctx.hand is not None and stopper(ctx, s)
            finish.meaning.action = 'singleton_major_three_notrump'
            finish.meaning.nature = ['natural']
            finish.meaning.acts = ['signoff', 'final_placement']
            finish.meaning.target_suit = 'N'
            finish.meaning.purpose_completed = True
            finish.description = 'Opener has a stopper in the shown singleton major; play 3NT.'

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
