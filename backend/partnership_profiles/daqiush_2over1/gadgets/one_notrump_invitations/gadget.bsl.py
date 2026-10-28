"""Bounded uncontested 1NT invitation and minor-transfer routes.

The numerical quality edges are initial, tunable policy values. A good minor
uses the CBB baseline of two of A/K/Q; Daqiush's transfer call mapping wins.
"""

INVITATION_QUALITY = {'poor_eight_kr': 6.5, 'strong_nine_delta': 1.0,
                      'shapely_seven_delta': 2.0}


def poor_eight(ctx):
    return (ctx.hand.hcp == 8
            and (ctx.hand_quality['kr_points'] <= INVITATION_QUALITY['poor_eight_kr']
                 or sorted(ctx.hand.length(suit) for suit in 'SHDC') == [3, 3, 3, 4]))


def strong_nine(ctx):
    return (ctx.hand.hcp == 9
            and ctx.hand_quality['kr_delta'] >= INVITATION_QUALITY['strong_nine_delta'])


def featureless(ctx):
    return (ctx.hand is not None and max(ctx.hand.length(s) for s in 'HS') <= 3)


def no_minor_transfer(ctx):
    return max(ctx.hand.length(s) for s in 'CD') <= 5


def weak_featureless(ctx):
    return (ctx.hand is not None and (ctx.hand.hcp <= 7 or poor_eight(ctx))
            and max(ctx.hand.length(s) for s in 'HS') <= 4
            and no_minor_transfer(ctx) and not garbage_stayman(ctx))


def garbage_stayman(ctx):
    return (ctx.hand is not None and (ctx.hand.hcp <= 7 or poor_eight(ctx))
            and tuple(ctx.hand.length(s) for s in 'SHDC')
            in ((4, 4, 4, 1), (3, 4, 5, 1), (4, 3, 5, 1),
                (4, 4, 5, 0)))


def game_featureless(ctx):
    return (featureless(ctx) and no_minor_transfer(ctx)
            and not (ctx.hand.length('C') >= 5 and ctx.hand.length('D') >= 5)
            and not good_minor_5422(ctx)
            and not minor_slam_probe(ctx)
            and (strong_nine(ctx) or (10 <= ctx.hand.hcp <= 15
                                     and max(ctx.hand.length(s) for s in 'HS') <= 2)))


def ordinary_invite(ctx):
    return (featureless(ctx) and ctx.hand.hcp in (8, 9)
            and not poor_eight(ctx) and not strong_nine(ctx)
            and not any(direct_minor_game(ctx, s) or solid_minor_three_notrump(ctx, s)
                        for s in 'CD')
            and not (sorted(ctx.hand.length(s) for s in 'CD') == [5, 6]
                     and min(ctx.hand.length(s) for s in 'HS') <= 1)
            and not (ctx.hand.length('C') == 5 and ctx.hand.length('D') == 5
                     and min(ctx.hand.length('H'), ctx.hand.length('S')) == 1)
            and not any(minor_invite(ctx, s) or shapely_invite(ctx, s) for s in 'CD'))


def spade_invite(ctx):
    return (ctx.hand is not None and ctx.hand.length('S') == 4
            and ctx.hand.length('H') <= 3 and ctx.hand.hcp in (8, 9)
            and not poor_eight(ctx) and not strong_nine(ctx)
            and seven_minor_four_major_game(ctx) is None)


def heart_invite(ctx):
    return (ctx.hand is not None and ctx.hand.length('H') == 4
            and ctx.hand.length('S') <= 3 and ctx.hand.hcp in (8, 9)
            and not poor_eight(ctx) and not strong_nine(ctx)
            and seven_minor_four_major_game(ctx) is None)


def double_major_invite(ctx):
    return (ctx.hand is not None
            and sorted(ctx.hand.length(s) for s in 'HS') == [4, 5]
            and ctx.hand.hcp in (8, 9)
            and not poor_eight(ctx) and not strong_nine(ctx))


def six_four_major_strength(ctx):
    if ctx.hand is None or sorted(ctx.hand.length(s) for s in 'HS') != [4, 6]:
        return None
    return shapely_combined_effective_points(ctx.hand)


def six_four_slam_band(ctx):
    """The owner's effective-point bands for a six-four two-major hand."""
    points = six_four_major_strength(ctx)
    if points is None or points < 10:
        return None
    if points >= 14:
        return 'strong'
    if points >= 12:
        return 'moderate'
    return 'weak'


def six_four_long_major(ctx):
    if six_four_major_strength(ctx) is None:
        return None
    return 'H' if ctx.hand.length('H') == 6 else 'S'


def six_four_first_minor_control(ctx):
    if ctx.hand is None:
        return None
    for minor in 'CD':
        if (ctx.hand.length(minor) <= 1
                or ctx.hand.contains_rank(minor, 'A')
                or ctx.hand.contains_rank(minor, 'K')):
            return minor
    return None


def both_four_major_invite(ctx):
    return (ctx.hand is not None
            and ctx.hand.length('H') == ctx.hand.length('S') == 4
            and ctx.hand.hcp in (8, 9)
            and not poor_eight(ctx) and not strong_nine(ctx))


def game_stayman(ctx):
    if ctx.hand is None or not (ctx.hand.hcp >= 10 or strong_nine(ctx)):
        return False
    if direct_notrump_power(ctx) is not None:
        return False
    hearts, spades = ctx.hand.length('H'), ctx.hand.length('S')
    if sorted(ctx.hand.length(s) for s in 'SHDC') == [3, 3, 3, 4]:
        return False  # These game hands seek a five-four fit via 3C.
    if min(hearts, spades) >= 5:
        return False  # Two five-card majors use their Jacoby two-suit route.
    if max(hearts, spades) < 4 or max(hearts, spades) >= 6:
        return False
    # Five cards in one major with at most three in the other use Jacoby.
    return not ((hearts == 5 and spades <= 3) or (spades == 5 and hearts <= 3))


def major_fit_slam_probe(ctx, answer):
    return (answer in ('2H', '2S') and game_stayman(ctx)
            and ctx.hand.length(answer[-1]) >= 4
            and ctx.hand.hcp >= 13 and ctx.hand_quality['kr_points'] >= 14)


def shortage_fit_probe(ctx, answer):
    if six_four_fit_probe(ctx, answer):
        return True
    return (answer in ('2H', '2S') and game_stayman(ctx)
            and ctx.hand.length(answer[-1]) >= 4
            and (major_fit_slam_probe(ctx, answer)
                 or (ctx.hand.hcp >= 11 and ctx.hand_quality['kr_points'] >= 13.5))
            and any(ctx.hand.length(suit) <= 1 for suit in 'SHDC'
                    if suit != answer[-1]))


def six_four_fit_probe(ctx, answer):
    if answer not in ('2H', '2S'):
        return False
    points = six_four_major_strength(ctx)
    if points is None or points < 10:
        return False
    answered = answer[-1]
    long_major = six_four_long_major(ctx)
    return answered != long_major or points >= 12


def flat_fit_probe(ctx, answer):
    return (major_fit_slam_probe(ctx, answer)
            and not shortage_fit_probe(ctx, answer))


def no_shortage_refusal_keycard(ctx):
    return ctx.hand is not None and ctx.hand.hcp >= 16


def seven_four_minor_alternative(ctx, answer, minor):
    return (shortage_fit_probe(ctx, answer)
            and ctx.hand.length(answer[-1]) == 4
            and ctx.hand.length(minor) >= 7)


def seven_minor_four_major_game(ctx):
    if ctx.hand is None:
        return None
    for minor in 'CD':
        if ctx.hand.length(minor) != 7 or max(ctx.hand.length('S'), ctx.hand.length('H')) != 4:
            continue
        points = shapely_effective_points(ctx.hand, minor)
        if 7 <= max(points, ctx.hand.hcp) < 9:
            return minor
    return None


def top_honors_only_outside_trump(ctx, trump):
    if ctx.hand is None:
        return False
    for suit in 'SHDC':
        if suit == trump:
            continue
        honors = ''.join(rank for rank in 'AKQJ' if ctx.hand.contains_rank(suit, rank))
        if honors and honors not in ('A', 'AK', 'AKQ', 'AKQJ'):
            return False
    return True


def shortage_adjusted_points(ctx, short_suit):
    return None if ctx.hand is None else splinter_adjusted_hcp(ctx.hand, short_suit)


def shortage_first_cue(answer_bid, trump, short_suit):
    rank = lambda bid: int(bid[0]) * 5 + 'CDHSN'.index(bid[1])
    choices = []
    for suit in 'CDHS':
        if suit in (trump, short_suit):
            continue
        bid = '4' + suit
        if rank(bid) <= rank(answer_bid):
            bid = '5' + suit
        choices.append(bid)
    return min(choices, key=rank)


def shortage_has_control(ctx, suit):
    return (ctx.hand.contains_rank(suit, 'A')
            or ctx.hand.contains_rank(suit, 'K')
            or ctx.hand.length(suit) <= 1)


def asks_stayman(ctx):
    return (ordinary_invite(ctx) or spade_invite(ctx) or heart_invite(ctx)
            or double_major_invite(ctx) or both_four_major_invite(ctx) or game_stayman(ctx)
            or minor_slam_probe(ctx) or minor_stayman_probe(ctx)
            or garbage_stayman(ctx) or seven_minor_four_major_game(ctx) is not None
            or 5 <= (six_four_major_strength(ctx) or 0) < 7
            or six_four_slam_band(ctx) is not None)


def direct_notrump_power(ctx):
    """Owner-reviewed raw-HCP placement for strong balanced/no-fit hands."""
    if ctx.hand is None:
        return None
    hcp = ctx.hand.hcp
    if hcp >= 22:
        return '7NT'  # The 1NT minimum already guarantees 37 combined HCP.
    if not ctx.hand.balanced:
        return None
    if hcp == 21 and ctx.hand_quality['good']:
        return '7NT'
    if hcp in (20, 21):
        return '5NT'
    if hcp in (18, 19) and sorted(ctx.hand.length(s) for s in 'SHDC') == [3, 3, 3, 4]:
        return '6NT'
    return None


def minor_stayman_probe(ctx):
    return (ctx.hand is not None and ctx.hand.hcp >= 12
            and ctx.hand_quality['kr_points'] >= 14
            and ctx.hand.length('C') == 4 and ctx.hand.length('D') == 4
            and max(ctx.hand.length(s) for s in 'HS') <= 3)


def minor_slam_probe(ctx):
    return (ctx.hand is not None and ctx.hand.hcp >= 12
            and ctx.hand_quality['kr_points'] >= 14
            and max(ctx.hand.length(s) for s in 'HS') <= 3
            and max(ctx.hand.length(s) for s in 'CD') >= 5
            and not solid_six_club_route(ctx)
            and not (ctx.hand.length('C') == 5 and ctx.hand.length('D') == 5)
            and not good_minor_5422(ctx)
            and not (sorted(ctx.hand.length(s) for s in 'HS') == [1, 3]
                     and sorted(ctx.hand.length(s) for s in 'CD') == [4, 5]))


def good_minor_5422(ctx):
    return (ctx.hand is not None and ctx.hand.hcp in (14, 15)
            and ctx.hand_quality['good']
            and sorted(ctx.hand.length(s) for s in 'HS') == [2, 2]
            and sorted(ctx.hand.length(s) for s in 'CD') == [4, 5])


def probe_minor(ctx, suit):
    return (minor_slam_probe(ctx) and ctx.hand.length(suit) >= 5
            and ctx.hand.length(suit) >= ctx.hand.length('D' if suit == 'C' else 'C'))


def strong_minor_with_other_major(ctx, answer, minor):
    if ctx.hand is None or answer not in ('2H', '2S'):
        return False
    other = 'S' if answer == '2H' else 'H'
    return (ctx.hand.length(answer[-1]) < 4 and ctx.hand.length(other) >= 4
            and ctx.hand.length(minor) >= 6 and ctx.hand.hcp >= 10
            and shapely_combined_effective_points(ctx.hand) >= 10)


def good_minor(ctx, suit):
    return ctx.hand.honor_count(suit, ('A', 'K', 'Q')) >= 2


def minor_invite(ctx, suit):
    return (ctx.hand is not None and ctx.hand.length(suit) >= 6
            and ctx.hand.hcp in (8, 9) and not poor_eight(ctx)
            and not strong_nine(ctx) and good_minor(ctx, suit)
            and max(ctx.hand.length(s) for s in 'HS') <= 3)


def shapely_invite(ctx, suit):
    return (ctx.hand is not None and ctx.hand.length(suit) >= 7
            and ctx.hand.length(suit) < 8
            and ((6 <= shapely_combined_effective_points(ctx.hand) < 8
                  and ctx.hand.honor_count(suit, ('A', 'K', 'Q')) < 2)
                 or (ctx.hand.hcp in (6, 7)
                     and ctx.hand_quality['kr_delta'] >= INVITATION_QUALITY['shapely_seven_delta']))
            and max(ctx.hand.length(s) for s in 'HS') <= 3)


def direct_minor_game(ctx, suit):
    if ctx.hand is None or ctx.hand.length(suit) < 7:
        return False
    if (shapely_effective_points(ctx.hand, suit) >= 8
            and max(ctx.hand.length(s) for s in 'HS') <= 3):
        return True
    if ctx.hand.hcp > 10:
        return False
    if ctx.hand.length(suit) >= 8:
        return True
    return (max(ctx.hand.length(s) for s in 'HS') <= 3
            and ctx.hand.honor_count(suit, ('A', 'K', 'Q')) < 2
            and shapely_combined_effective_points(ctx.hand) >= 8)


def solid_minor_three_notrump(ctx, suit):
    return (ctx.hand is not None and ctx.hand.length(suit) >= 6
            and ctx.hand.hcp <= 9
            and ctx.hand.honor_count(suit, ('A', 'K', 'Q')) == 3
            and (ctx.hand.length(suit) >= 7
                 or max(ctx.hand.length(s) for s in 'HS') <= 2))


def solid_six_club_route(ctx):
    return (ctx.hand is not None and ctx.hand.length('C') == 6
            and ctx.hand.length('S') >= 1
            and ctx.hand.honor_count('C', ('A', 'K', 'Q')) == 3)


def weak_minor(ctx, suit):
    return (ctx.hand is not None and ctx.hand.length(suit) >= 6
            and (ctx.hand.hcp <= 7 or poor_eight(ctx))
            and not shapely_invite(ctx, suit)
            and seven_minor_four_major_game(ctx) is None)


def minor_transfer(ctx, suit):
    solid_club_inquiry = (suit == 'C' and ctx.hand is not None
                          and ctx.hand.length('C') == 6
                          and max(ctx.hand.length(s) for s in 'HS') == 3
                          and ctx.hand.honor_count('C', ('A', 'K', 'Q')) == 3)
    return (not solid_club_inquiry
            and not direct_minor_game(ctx, suit) and not solid_minor_three_notrump(ctx, suit)
            and (weak_minor(ctx, suit) or minor_invite(ctx, suit) or shapely_invite(ctx, suit)))


def superaccept(ctx, suit):
    return (ctx.hand is not None and ctx.hand.hcp >= 16
            and ctx.hand.length(suit) >= 2
            and any(ctx.hand.contains_rank(suit, rank) for rank in 'AKQ'))


def ordinary_accept(ctx, suit):
    return ctx.hand is not None and not superaccept(ctx, suit)


def low_stayman_answer(ctx):
    return ctx.hand is not None and ctx.hand.length('H') < 4 and ctx.hand.length('S') < 4


def heart_stayman_answer(ctx):
    return ctx.hand is not None and ctx.hand.length('H') >= 4


def spade_stayman_answer(ctx):
    return ctx.hand is not None and ctx.hand.length('H') < 4 and ctx.hand.length('S') >= 4


class OneNotrumpInvitations(Gadget):
    id = 'one_notrump_invitations'
    namespace = 'daqiush_2over1'
    name = '1NT natural and minor invitations'
    author = Author('Daqiush')

    def build(self):
        for contract in ('5NT', '6NT', '7NT'):
            power = self.call('strong_notrump_' + contract.lower())
            power.when = '1NP'
            power.bid = contract
            power.applies = lambda ctx, c=contract: direct_notrump_power(ctx) == c
            power.meaning.action = 'strong_notrump_placement'
            power.meaning.nature = ['natural']
            power.meaning.acts = ['invite'] if contract == '5NT' else ['signoff', 'final_placement']
            power.meaning.target_suit = 'N'
            if contract != '5NT':
                power.meaning.purpose_completed = True
            power.description = 'Raw-HCP notrump slam placement; 5NT invites grand slam.'

        for suit in 'CD':
            five_minor = self.call('direct_five_' + suit.lower() + '_long_suit')
            five_minor.when = '1NP'
            five_minor.bid = '5' + suit
            five_minor.applies = lambda ctx, s=suit: (
                direct_notrump_power(ctx) is None and direct_minor_game(ctx, s))
            five_minor.meaning.action = 'long_minor_game'
            five_minor.meaning.nature = ['natural']
            five_minor.meaning.acts = ['signoff', 'final_placement']
            five_minor.meaning.target_suit = suit
            five_minor.meaning.purpose_completed = True
            five_minor.description = 'Eight-card minor, or qualifying strong seven-card minor: place 5m directly.'

        for contract, accepts in (('6NT', False), ('7NT', True)):
            answer = self.call('strong_notrump_five_nt_' + contract.lower())
            answer.when = '1NP5NTP'
            answer.bid = contract
            answer.applies = lambda ctx, high=accepts: ctx.hand is not None and (ctx.hand.hcp >= 17) == high
            answer.meaning.action = 'grand_slam_invitation_' + ('accept' if accepts else 'reject')
            answer.meaning.nature = ['natural']
            answer.meaning.acts = [('accept' if accepts else 'reject'), 'final_placement']
            answer.meaning.target_suit = 'N'
            answer.meaning.purpose_completed = True
            answer.description = 'Answer the natural 5NT grand-slam invitation by the 1NT opening limit.'

        for bid, applies, action in (
            ('P', weak_featureless, 'weak_signoff'),
            ('3NT', lambda ctx: game_featureless(ctx) or any(
                solid_minor_three_notrump(ctx, suit) for suit in 'CD'), 'good_nine_game'),
        ):
            direct = self.call('featureless_' + action)
            direct.when = '1NP'
            direct.bid = bid
            direct.applies = applies
            direct.meaning.action = action
            direct.meaning.nature = ['natural']
            direct.meaning.acts = ['signoff']
            direct.meaning.target_suit = 'N'
            if bid == '3NT':
                direct.meaning.quality_upgrade = True
                direct.meaning.acts = ['signoff', 'final_placement']
                direct.meaning.purpose_completed = True
            direct.description = 'Weak hands without a transfer or garbage Stayman stop; game-going featureless hands place 3NT.'

        stayman = self.call('stayman_ask')
        stayman.when = '1NP'
        stayman.bid = '2C'
        stayman.applies = asks_stayman
        stayman.meaning.action = 'stayman'
        stayman.meaning.nature = ['artificial']
        stayman.meaning.acts = ['directive']
        stayman.description = 'Stayman for an invitation, a game-going major, or a weak club-shortage three-suiter.'

        for answer, applies in (('2D', low_stayman_answer),
                                ('2H', heart_stayman_answer),
                                ('2S', spade_stayman_answer)):
            reply = self.call('stayman_' + answer.lower())
            reply.when = '1NP2CP'
            reply.bid = answer
            reply.applies = applies
            reply.meaning.action = 'stayman_response'
            reply.meaning.nature = ['artificial' if answer == '2D' else 'natural']
            reply.meaning.acts = ['descriptive']
            reply.description = 'Shows opener major length according to Daqiush Stayman.'

            prefix = '1NP2CP' + answer + 'P'
            garbage_stop = self.call('garbage_stayman_pass_after_' + answer.lower())
            garbage_stop.when = prefix
            garbage_stop.bid = 'P'
            garbage_stop.applies = garbage_stayman
            garbage_stop.meaning.action = 'garbage_stayman_signoff'
            garbage_stop.meaning.nature = ['natural']
            garbage_stop.meaning.acts = ['signoff']
            garbage_stop.meaning.target_suit = answer[-1]
            garbage_stop.description = 'Weak club-shortage three-suiter stops in opener\'s two-level Stayman answer.'

            invitation = self.call('natural_invite_after_' + answer.lower())
            invitation.when = prefix
            invitation.bid = '2NT'
            invitation.applies = lambda ctx, a=answer: (ordinary_invite(ctx)
                                                         or (a == '2D' and both_four_major_invite(ctx))
                                                         or (a != '2H' and heart_invite(ctx))
                                                         or (a == '2D' and spade_invite(ctx)))
            invitation.meaning.action = 'natural_invitation'
            invitation.meaning.nature = ['natural']
            invitation.meaning.acts = ['invite']
            invitation.meaning.target_suit = 'N'
            invitation.description = 'Natural 3NT invitation with no relevant minor feature.'

            for bid, applies, act in (
                ('P', lambda ctx: ctx.hand is not None and ctx.hand.hcp <= 15, 'reject'),
                ('3NT', lambda ctx, a=answer: (
                    ctx.hand is not None and ctx.hand.hcp >= 16
                    and not (a == '2H' and ctx.hand.length('H') >= 5)
                    and not (a == '2S' and ctx.hand.length('S') >= 5)),
                 'accept'),
            ):
                placement = self.call('natural_invite_' + answer.lower() + '_' + act)
                placement.when = prefix + '2NTP'
                placement.bid = bid
                placement.applies = applies
                placement.meaning.action = 'natural_invitation_' + act
                placement.meaning.nature = ['natural']
                placement.meaning.acts = [act]
                placement.meaning.target_suit = 'N'
                if act == 'accept':
                    placement.meaning.acts = ['accept', 'final_placement']
                    placement.meaning.purpose_completed = True
                placement.description = 'Accept or decline natural notrump game invitation.'

            if answer in ('2H', '2S'):
                major = answer[-1]
                five_card = self.call(
                    'natural_invite_' + answer.lower() + '_five_card_major')
                five_card.when = prefix + '2NTP'
                five_card.bid = '3' + major
                five_card.applies = (
                    lambda ctx, m=major: (ctx.hand is not None
                                          and ctx.hand.hcp >= 16
                                          and ctx.hand.length(m) >= 5))
                five_card.meaning.action = 'natural_invitation_accept_five_card_major'
                five_card.meaning.nature = ['natural']
                five_card.meaning.acts = ['accept', 'descriptive']
                five_card.meaning.target_suit = major
                five_card.description = (
                    'Accept the invitation and show a five-card major.')

                for bid, applies, action in (
                    ('3NT', lambda ctx, m=major: (ctx.hand is not None
                                                  and ctx.hand.length(m) < 3),
                     'choice_notrump'),
                    ('4' + major, lambda ctx, m=major: (ctx.hand is not None
                                                        and ctx.hand.length(m) >= 3),
                     'choice_major_game'),
                ):
                    choice = self.call('natural_invite_' + answer.lower()
                                       + '_five_card_major_' + action)
                    choice.when = prefix + '2NTP3' + major + 'P'
                    choice.bid = bid
                    choice.applies = applies
                    choice.meaning.action = 'natural_invitation_' + action
                    choice.meaning.nature = ['natural']
                    choice.meaning.acts = ['accept', 'final_placement']
                    choice.meaning.target_suit = 'N' if bid == '3NT' else major
                    choice.meaning.purpose_completed = True
                    choice.description = (
                        'Choose the final game after opener shows a five-card major.')

        for answer in ('2D', '2H', '2S'):
            prefix = '1NP2CP' + answer + 'P'
            for minor in 'CD':
                no_fit = self.call('seven_' + minor.lower() + '_no_major_fit_after_' + answer.lower())
                no_fit.when = prefix
                no_fit.bid = '5' + minor
                no_fit.applies = (lambda ctx, m=minor, a=answer:
                                  seven_minor_four_major_game(ctx) == m
                                  and (a == '2D' or ctx.hand.length(a[-1]) < 4))
                no_fit.meaning.action = 'seven_minor_no_major_fit_game'
                no_fit.meaning.nature = ['natural']
                no_fit.meaning.acts = ['signoff', 'final_placement']
                no_fit.meaning.target_suit = minor
                no_fit.meaning.purpose_completed = True
                no_fit.description = 'No major fit after Stayman: place five of the seven-card minor.'
            for bid, applies, action in (
                ('3NT', lambda ctx, a=answer: game_stayman(ctx)
                 and (a == '2D' or ctx.hand.length(a[-1]) < 4)
                 and not any(strong_minor_with_other_major(ctx, a, m) for m in 'CD'),
                 'game_notrump'),
                ('4H', lambda ctx, a=answer: a == '2H' and game_stayman(ctx)
                 and ctx.hand.length('H') >= 4
                 and not major_fit_slam_probe(ctx, a)
                 and not shortage_fit_probe(ctx, a)
                 or a == '2H' and seven_minor_four_major_game(ctx) is not None
                 and ctx.hand.length('H') == 4
                 or a == '2H' and six_four_long_major(ctx) == 'H'
                 and six_four_slam_band(ctx) == 'weak', 'game_hearts'),
                ('4S', lambda ctx, a=answer: a == '2S' and game_stayman(ctx)
                 and ctx.hand.length('S') >= 4
                 and not major_fit_slam_probe(ctx, a)
                 and not shortage_fit_probe(ctx, a)
                 or a == '2S' and seven_minor_four_major_game(ctx) is not None
                 and ctx.hand.length('S') == 4
                 or a == '2S' and six_four_long_major(ctx) == 'S'
                 and six_four_slam_band(ctx) == 'weak', 'game_spades'),
            ):
                if answer == '2D' and bid in ('4H', '4S'):
                    continue  # No 4M Stayman placement after a major denial.
                continuation = self.call('stayman_' + answer.lower() + '_' + action)
                continuation.when = prefix
                continuation.bid = bid
                continuation.applies = applies
                continuation.meaning.action = action
                continuation.meaning.nature = ['natural']
                continuation.meaning.acts = ['descriptive'] if answer == '2H' and bid == '3NT' else ['signoff', 'final_placement']
                continuation.meaning.target_suit = 'N' if bid == '3NT' else bid[-1]
                if bid in ('4H', '4S'):
                    continuation.meaning.quality_upgrade = True
                if not (answer == '2H' and bid == '3NT'):
                    continuation.meaning.purpose_completed = True
                continuation.description = 'Game-going Stayman hand places game after opener describes the majors.'

            if answer in ('2H', '2S'):
                shortage = self.call('stayman_' + answer.lower() + '_fit_shortage_slam')
                shortage.when = prefix
                shortage.bid = '3S' if answer == '2H' else '3H'
                shortage.applies = lambda ctx, a=answer: shortage_fit_probe(ctx, a)
                shortage.meaning.action = 'major_fit_shortage_slam_probe'
                shortage.meaning.nature = ['artificial']
                shortage.meaning.acts = ['slam_try', 'game_forcing']
                shortage.meaning.forcing = 'game_forcing'
                shortage.meaning.agreed_suit = answer[-1]
                shortage.meaning.target_suit = answer[-1]
                shortage.effect('agreed_suit').suit = answer[-1]
                shortage.description = ('Other major confirms the answered major as a fit and probes slam; '
                                        'a six-four two-major hand can use this call too.')

                no_shortage = self.call('stayman_' + answer.lower() + '_fit_no_shortage_slam')
                no_shortage.when = prefix
                no_shortage.bid = '4D'
                no_shortage.applies = lambda ctx, a=answer: flat_fit_probe(ctx, a)
                no_shortage.meaning.action = 'major_fit_no_shortage_slam_probe'
                no_shortage.meaning.nature = ['artificial']
                no_shortage.meaning.acts = ['slam_try', 'game_forcing']
                no_shortage.meaning.forcing = 'game_forcing'
                no_shortage.meaning.agreed_suit = answer[-1]
                no_shortage.meaning.target_suit = answer[-1]
                no_shortage.effect('agreed_suit').suit = answer[-1]
                no_shortage.description = 'Four diamonds confirms the major fit and slam interest without a singleton or void.'

                shortage_prefix = prefix + shortage.bid + 'P'
                if answer == '2S':
                    counter = self.call('stayman_spade_shortage_counterinvite')
                    counter.when = shortage_prefix
                    counter.bid = '3S'
                    counter.applies = lambda ctx: top_honors_only_outside_trump(ctx, 'S')
                    counter.meaning.action = 'shortage_counterinvite'
                    counter.meaning.nature = ['artificial']
                    counter.meaning.acts = ['invite']
                    counter.meaning.agreed_suit = 'S'
                    counter.meaning.target_suit = 'S'
                    counter.description = 'Only A, AK, AKQ, or AKQJ side-suit honor structures: counterinvite in three spades.'

                ask_shortage = self.call('stayman_' + answer.lower() + '_ask_shortage')
                ask_shortage.when = shortage_prefix
                ask_shortage.bid = '3NT'
                ask_shortage.applies = (lambda ctx, a=answer:
                                        ctx.hand is not None and
                                        (a == '2H' or not top_honors_only_outside_trump(ctx, 'S')))
                ask_shortage.meaning.action = 'ask_short_suit'
                ask_shortage.meaning.nature = ['artificial']
                ask_shortage.meaning.acts = ['inquiry']
                ask_shortage.meaning.agreed_suit = answer[-1]
                ask_shortage.meaning.target_suit = answer[-1]
                ask_shortage.description = 'Ask which side suit is short after the major-fit slam probe.'

                shortage_suits = (
                    ('C', '4C', ()),
                    ('D', '4D', ('C',)),
                    ('H' if answer == '2S' else 'S', '4H', ('C', 'D')),
                )
                for short_suit, answer_bid, earlier_suits in shortage_suits:
                    shown = self.call('stayman_' + answer.lower() + '_show_'
                                      + short_suit.lower() + '_shortage')
                    shown.when = shortage_prefix + '3NTP'
                    shown.bid = answer_bid
                    shown.applies = (lambda ctx, suit=short_suit,
                                     earlier=earlier_suits:
                                     ctx.hand is not None
                                     and ctx.hand.length(suit) <= 1
                                     and not any(ctx.hand.length(other) <= 1
                                                 for other in earlier))
                    shown.meaning.action = 'show_short_suit'
                    # 4H both describes spade shortage and is a playable heart game.
                    # Treating it as only artificial would leave the game force active
                    # and incorrectly forbid opener's terminal Pass.
                    shown.meaning.nature = ['natural' if answer_bid == '4H' and answer == '2H'
                                            else 'artificial']
                    shown.meaning.acts = ['descriptive']
                    shown.meaning.agreed_suit = answer[-1]
                    shown.meaning.target_suit = answer[-1]
                    shown.meaning.shortage_suit = short_suit
                    shown.description = ('Shows ' + short_suit + ' shortage; '
                                         'with two short suits, show the lower available answer.')

                    trump = answer[-1]
                    next_prefix = shortage_prefix + '3NTP' + answer_bid + 'P'
                    first_cue = shortage_first_cue(answer_bid, trump, short_suit)
                    cue_suit = first_cue[-1]
                    game_call = 'P' if answer_bid == '4H' and trump == 'H' else '4' + trump

                    stop = self.call('stayman_' + trump.lower() + '_after_'
                                     + answer_bid.lower() + '_shortage_stop')
                    stop.when = next_prefix
                    stop.bid = game_call
                    stop.applies = (lambda ctx, s=short_suit, c=cue_suit:
                                    ctx.hand is not None and
                                    (shortage_adjusted_points(ctx, s) < 15.5
                                     or (shortage_adjusted_points(ctx, s) < 16.5
                                         and not shortage_has_control(ctx, c))))
                    stop.meaning.action = 'shortage_adjusted_game_signoff'
                    stop.meaning.nature = ['natural']
                    stop.meaning.acts = ['signoff', 'final_placement']
                    stop.meaning.target_suit = trump
                    stop.meaning.agreed_suit = trump
                    stop.meaning.purpose_completed = True
                    stop.description = 'After removing short-suit waste, play game if strength or the first cue control is missing.'

                    cue = self.call('stayman_' + trump.lower() + '_after_'
                                    + answer_bid.lower() + '_shortage_cue')
                    cue.when = next_prefix
                    cue.bid = first_cue
                    cue.applies = (lambda ctx, s=short_suit, c=cue_suit:
                                   ctx.hand is not None
                                   and 15.5 <= shortage_adjusted_points(ctx, s) < 16.5
                                   and shortage_has_control(ctx, c))
                    cue.meaning.action = 'shortage_adjusted_control_cue'
                    cue.meaning.nature = ['artificial']
                    cue.meaning.acts = ['slam_try', 'control_showing']
                    cue.meaning.control_suit = cue_suit
                    cue.meaning.agreed_suit = trump
                    cue.description = 'Intermediate retained strength: start a control cue in the lowest available side suit.'

                    ask = self.call('stayman_' + trump.lower() + '_after_'
                                    + answer_bid.lower() + '_shortage_keycard')
                    ask.when = next_prefix
                    ask.bid = '4NT'
                    ask.applies = lambda ctx, s=short_suit: (ctx.hand is not None and
                                                              shortage_adjusted_points(ctx, s) >= 16.5)
                    ask.meaning.action = 'rkcb_1430'
                    ask.meaning.nature = ['artificial']
                    ask.meaning.acts = ['inquiry', 'keycard_asking']
                    ask.meaning.target_suit = trump
                    ask.meaning.agreed_suit = trump
                    keycards = ask.effect('keycard_context')
                    keycards.trump_suit = trump
                    keycards.ask_call = '4N'
                    keycards.method = 'rkcb_1430'
                    keycards.status = 'pending'
                    ask.description = 'Enough retained strength after the shown shortage: ask major keycards directly.'

                refusal = self.call('stayman_' + answer.lower() + '_no_shortage_decline')
                refusal.when = prefix + '4DP'
                refusal.bid = '4' + answer[-1]
                refusal.applies = (lambda ctx, t=answer[-1]:
                                   named_evaluator(ctx, 'absolute_maximum_' + t) is not True)
                refusal.meaning.action = 'no_shortage_slam_decline'
                refusal.meaning.nature = ['natural']
                refusal.meaning.acts = ['reject', 'signoff', 'final_placement']
                refusal.meaning.target_suit = answer[-1]
                refusal.meaning.agreed_suit = answer[-1]
                refusal.description = 'Decline the no-shortage slam try at four of the agreed major.'

                continue_prefix = prefix + '4DP4' + answer[-1] + 'P'
                continue_ask = self.call('stayman_' + answer.lower()
                                         + '_no_shortage_after_refusal_keycard')
                continue_ask.when = continue_prefix
                continue_ask.bid = '4NT'
                continue_ask.applies = no_shortage_refusal_keycard
                continue_ask.meaning.action = 'rkcb_1430'
                continue_ask.meaning.nature = ['artificial']
                continue_ask.meaning.acts = ['inquiry', 'keycard_asking']
                continue_ask.meaning.target_suit = answer[-1]
                continue_ask.meaning.agreed_suit = answer[-1]
                continue_ask.effect('agreed_suit').suit = answer[-1]
                keycards = continue_ask.effect('keycard_context')
                keycards.trump_suit = answer[-1]
                keycards.ask_call = '4N'
                keycards.method = 'rkcb_1430'
                keycards.status = 'pending'
                continue_ask.description = (
                    'After the opener declines the no-shortage try, '
                    'a sufficiently strong responder continues with keycard.')

                continue_pass = self.call('stayman_' + answer.lower()
                                          + '_no_shortage_after_refusal_pass')
                continue_pass.when = continue_prefix
                continue_pass.bid = 'P'
                continue_pass.applies = lambda ctx: not no_shortage_refusal_keycard(ctx)
                continue_pass.meaning.action = 'no_shortage_slam_decline'
                continue_pass.meaning.nature = ['natural']
                continue_pass.meaning.acts = ['signoff', 'final_placement']
                continue_pass.meaning.target_suit = answer[-1]
                continue_pass.meaning.agreed_suit = answer[-1]
                continue_pass.meaning.purpose_completed = True
                continue_pass.description = 'Pass after the opener declines and responder lacks further slam strength.'

            for minor in 'CD':
                show = self.call('stayman_' + answer.lower() + '_show_' + minor.lower())
                show.when = prefix
                show.bid = '3' + minor
                show.applies = lambda ctx, m=minor, a=answer: (probe_minor(ctx, m)
                                                               or strong_minor_with_other_major(ctx, a, m)
                                                               or seven_four_minor_alternative(ctx, a, m))
                show.meaning.action = 'natural_minor_slam_probe'
                show.meaning.nature = ['natural']
                show.meaning.acts = ['game_forcing', 'slam_try']
                show.meaning.forcing = 'game_forcing'
                show.meaning.target_suit = minor
                show.description = 'Natural five-plus minor after Stayman; game forcing with slam interest.'

                probe_prefix = prefix + '3' + minor + 'P'
                support_bid = '3D' if answer != '2D' and minor == 'C' else '3H'
                for bid, applies, action, target in (
                    ('3D', lambda ctx, a=answer, m=minor: a == '2D' and m == 'C'
                     and ctx.hand.length('D') >= 5, 'natural_diamonds', 'D'),
                    ('3S', lambda ctx, a=answer: a == '2H'
                     and ctx.hand.length('S') >= 4, 'natural_spades', 'S'),
                    (support_bid, lambda ctx, a=answer, m=minor: ctx.hand.length(m) >= 3
                     and not (a == '2D' and m == 'C' and ctx.hand.length('D') >= 5)
                     and not (a == '2H' and ctx.hand.length('S') >= 4), 'minor_support', minor),
                    ('3NT', lambda ctx, a=answer, m=minor: ctx.hand.length(m) < 3
                     and not (a == '2D' and m == 'C' and ctx.hand.length('D') >= 5)
                     and not (a == '2H' and ctx.hand.length('S') >= 4), 'natural_notrump', 'N'),
                ):
                    if bid == '3D' and not (answer == '2D' and minor == 'C'):
                        continue
                    if bid == '3S' and answer != '2H':
                        continue
                    reply = self.call('stayman_' + answer.lower() + '_' + minor.lower()
                                      + '_' + action)
                    reply.when = probe_prefix
                    reply.bid = bid
                    reply.applies = applies
                    reply.meaning.action = action
                    reply.meaning.nature = ['artificial' if action == 'minor_support' else 'natural']
                    reply.meaning.acts = ['descriptive']
                    reply.meaning.target_suit = target
                    if action == 'minor_support':
                        reply.meaning.agreed_suit = minor
                        reply.effect('agreed_suit').suit = minor
                    reply.description = 'Natural new suit, conventional minor support, or 3NT without support.'

        for bid, applies, action in (
            ('4S', lambda ctx: ctx.hand is not None and ctx.hand.length('S') >= 4, 'spade_fit'),
            ('P', lambda ctx: ctx.hand is not None and ctx.hand.length('S') < 4, 'no_spade_fit'),
        ):
            placement = self.call('stayman_game_three_notrump_' + action)
            placement.when = '1NP2CP2HP3NTP'
            placement.bid = bid
            placement.applies = applies
            placement.meaning.action = 'stayman_game_' + action
            placement.meaning.nature = ['natural']
            placement.meaning.acts = ['signoff', 'final_placement']
            placement.meaning.target_suit = 'S' if bid == '4S' else 'N'
            placement.meaning.purpose_completed = True
            placement.description = 'After 2H–3NT, choose the known four-four spade fit or play 3NT.'

        for suit, earlier in (('D', ()), ('H', ('D',))):
            cue = self.call('strong_club_spade_fit_cue_' + suit.lower())
            cue.when = '1NP2CP2HP3CP3SP'
            cue.bid = '4' + suit
            cue.applies = (lambda ctx, s=suit, prior=earlier:
                           ctx.hand is not None and ctx.hand.length('S') >= 4
                           and ctx.hand.length('C') >= 6
                           and (s == 'H' or ctx.hand.contains_rank(s, 'A')
                                or ctx.hand.contains_rank(s, 'K')
                                or ctx.hand.length(s) <= 1)
                           and not any(ctx.hand.contains_rank(x, 'A')
                                       or ctx.hand.contains_rank(x, 'K')
                                       or ctx.hand.length(x) <= 1 for x in prior))
            cue.meaning.action = 'spade_slam_control_cue'
            cue.meaning.nature = ['artificial']
            cue.meaning.acts = ['slam_try', 'control_showing']
            cue.meaning.control_suit = suit
            cue.meaning.agreed_suit = 'S'
            cue.meaning.target_suit = 'S'
            cue.effect('agreed_suit').suit = 'S'
            cue.description = ('The 3S support sets spades; 4D shows diamond control. '
                               'Without it, 4H continues the spade slam try without promising heart control.')

        low_minor = self.call('four_minor_stayman')
        low_minor.when = '1NP2CP2DP'
        low_minor.bid = '4C'
        low_minor.applies = minor_stayman_probe
        low_minor.meaning.action = 'minor_stayman'
        low_minor.meaning.nature = ['artificial']
        low_minor.meaning.acts = ['inquiry', 'slam_try']
        low_minor.description = 'Ask about opener’s four-card minors after the major denial.'

        for answer, applies, suit in (
            ('4D', lambda ctx: ctx.hand is not None and ctx.hand.length('C') >= 4, 'C'),
            ('4H', lambda ctx: ctx.hand is not None and ctx.hand.length('C') < 4
             and ctx.hand.length('D') >= 4, 'D'),
            ('4NT', lambda ctx: ctx.hand is not None and ctx.hand.length('C') < 4
             and ctx.hand.length('D') < 4, None),
        ):
            answer_call = self.call('four_minor_stayman_answer_' + answer.lower())
            answer_call.when = '1NP2CP2DP4CP'
            answer_call.bid = answer
            answer_call.applies = applies
            answer_call.meaning.action = 'minor_stayman_response'
            answer_call.meaning.nature = ['artificial']
            answer_call.meaning.acts = ['descriptive']
            if suit:
                answer_call.meaning.target_suit = suit
                answer_call.meaning.agreed_suit = suit
                answer_call.effect('agreed_suit').suit = suit
            answer_call.description = '4D shows four clubs; 4H shows four diamonds without four clubs.'

        spade = self.call('stayman_heart_reply_spade_invite')
        spade.when = '1NP2CP2HP'
        spade.bid = '2S'
        spade.applies = spade_invite
        spade.meaning.action = 'spade_invitation'
        spade.meaning.nature = ['natural']
        spade.meaning.acts = ['invite']
        spade.meaning.target_suit = 'S'
        spade.description = 'Nonforcing 2S: invitational strength, four spades, no heart fit.'

        heart = self.call('stayman_heart_reply_heart_invite')
        heart.when = '1NP2CP2HP'
        heart.bid = '3H'
        heart.applies = lambda ctx: (heart_invite(ctx) or double_major_invite(ctx)
                                     or both_four_major_invite(ctx)
                                     or (ctx.hand.length('H') >= 4
                                         and 5 <= (six_four_major_strength(ctx) or 0) < 7))
        heart.meaning.action = 'heart_invitation'
        heart.meaning.nature = ['natural']
        heart.meaning.acts = ['invite']
        heart.meaning.target_suit = 'H'
        heart.meaning.shape_invitation = {'minimum': 5, 'min_lengths': {'H': 4, 'S': 4}}
        heart.description = 'Invitational raise of opener’s four-card heart suit.'

        for bid, action in (('P', 'reject'), ('4H', 'accept')):
            placement = self.call('heart_invite_' + action)
            placement.when = '1NP2CP2HP3HP'
            placement.bid = bid
            placement.applies = lambda ctx: ctx.hand is not None
            placement.meaning.action = 'heart_invitation_' + action
            placement.meaning.nature = ['natural']
            placement.meaning.acts = [action] if bid == 'P' else [action, 'final_placement']
            placement.meaning.target_suit = 'H'
            if bid != 'P':
                placement.meaning.purpose_completed = True
            placement.description = 'Accept or decline the heart game invitation.'

        spade_raise = self.call('stayman_spade_reply_spade_invite')
        spade_raise.when = '1NP2CP2SP'
        spade_raise.bid = '3S'
        spade_raise.applies = lambda ctx: (spade_invite(ctx) or double_major_invite(ctx)
                                           or both_four_major_invite(ctx)
                                           or (ctx.hand.length('S') >= 4
                                               and 5 <= (six_four_major_strength(ctx) or 0) < 7))
        spade_raise.meaning.action = 'spade_fit_invitation'
        spade_raise.meaning.nature = ['natural']
        spade_raise.meaning.acts = ['invite']
        spade_raise.meaning.target_suit = 'S'
        spade_raise.meaning.shape_invitation = {'minimum': 5, 'min_lengths': {'H': 4, 'S': 4}}
        spade_raise.description = 'Four spades and invitational strength raise opener’s four-card spade suit.'

        for bid, action in (('P', 'reject'), ('4S', 'accept')):
            placement = self.call('spade_fit_invite_' + action)
            placement.when = '1NP2CP2SP3SP'
            placement.bid = bid
            placement.applies = lambda ctx: ctx.hand is not None
            placement.meaning.action = 'spade_fit_invitation_' + action
            placement.meaning.nature = ['natural']
            placement.meaning.acts = [action] if bid == 'P' else [action, 'final_placement']
            placement.meaning.target_suit = 'S'
            if bid != 'P':
                placement.meaning.purpose_completed = True
            placement.description = 'Accept or decline the spade fit invitation.'

        for major in 'HS':
            show = self.call('stayman_denial_show_five_' + major.lower())
            show.when = '1NP2CP2DP'
            show.bid = '2' + major
            show.applies = lambda ctx, s=major: ctx.hand is not None and (
                (double_major_invite(ctx) and ctx.hand.length(s) == 5)
                or (ctx.hand.length(s) == 6
                    and 5 <= (six_four_major_strength(ctx) or 0) < 7))
            show.meaning.action = 'five_major_invitation'
            show.meaning.nature = ['natural']
            show.meaning.acts = ['invite']
            show.meaning.target_suit = major
            show.meaning.shape_invitation = {
                'minimum': 5, 'min_lengths': {major: 5,
                                              'H' if major == 'S' else 'S': 4}}
            show.description = 'Shows at least five of this major and four of the other; responder may still hold game-forcing shape strength.'

            prefix = '1NP2CP2DP2' + major + 'P'
            for bid, action, fits in (
                ('2NT', 'reject', None), ('3NT', 'accept', False),
                ('4' + major, 'accept', True),
            ):
                placement = self.call('stayman_five_' + major.lower() + '_' + action + '_' + bid.lower())
                placement.when = prefix
                placement.bid = bid
                placement.applies = (lambda ctx, s=major, f=fits: ctx.hand is not None
                                     and (f is None or (ctx.hand.length(s) >= 3) == f))
                placement.meaning.action = 'five_major_invitation_' + action
                placement.meaning.nature = ['natural']
                placement.meaning.acts = ([action, 'final_placement']
                                          if bid == '4' + major else [action])
                placement.meaning.target_suit = 'N' if bid == '3NT' else major
                if bid == '4' + major:
                    placement.meaning.purpose_completed = True
                placement.description = 'Reject with 2NT or accept the game invitation in 3NT/4M.'

            five_four_stop = self.call('stayman_five_' + major.lower() + '_reject_stop')
            five_four_stop.when = prefix + '2NTP'
            five_four_stop.bid = 'P'
            five_four_stop.applies = lambda ctx, s=major: (double_major_invite(ctx)
                                                           and ctx.hand.length(s) == 5)
            five_four_stop.meaning.action = 'five_four_major_invitation_stop'
            five_four_stop.meaning.nature = ['natural']
            five_four_stop.meaning.acts = ['signoff', 'final_placement']
            five_four_stop.meaning.target_suit = 'N'
            five_four_stop.meaning.purpose_completed = True
            five_four_stop.description = 'Without a six-card suit, respect opener’s rejection and play 2NT.'

            five_four_game = self.call('stayman_five_' + major.lower() + '_game_stop')
            five_four_game.when = prefix + '3NTP'
            five_four_game.bid = 'P'
            five_four_game.applies = lambda ctx, s=major: (double_major_invite(ctx)
                                                           and ctx.hand.length(s) == 5)
            five_four_game.meaning.action = 'five_four_major_game_stop'
            five_four_game.meaning.nature = ['natural']
            five_four_game.meaning.acts = ['signoff', 'final_placement']
            five_four_game.meaning.target_suit = 'N'
            five_four_game.meaning.purpose_completed = True
            five_four_game.description = 'Without a six-card suit, accept opener’s notrump game.'

            for earlier, final in (('2NT', '3' + major), ('3NT', '4' + major)):
                long_rebid = self.call('six_four_' + major.lower() + '_over_' + earlier.lower())
                long_rebid.when = prefix + earlier.replace('NT', 'N') + 'P'
                long_rebid.bid = final
                long_rebid.applies = lambda ctx, s=major, e=earlier: (
                    ctx.hand is not None and ctx.hand.length(s) == 6
                    and 5 <= (six_four_major_strength(ctx) or 0) < 7)
                long_rebid.meaning.action = 'six_four_major_placement'
                long_rebid.meaning.nature = ['natural']
                long_rebid.meaning.acts = ['signoff', 'final_placement']
                long_rebid.meaning.target_suit = major
                long_rebid.meaning.purpose_completed = True
                long_rebid.description = 'After notrump acceptance, return to the known six-card major.'

        for bid, applies, action in (
            ('P', lambda ctx: ctx.hand is not None and ctx.hand.length('S') >= 3, 'reject'),
            ('2NT', lambda ctx: ctx.hand is not None and ctx.hand.length('S') < 3, 'reject'),
            ('4S', lambda ctx: ctx.hand is not None and ctx.hand.length('S') >= 4, 'accept'),
            ('3NT', lambda ctx: ctx.hand is not None and ctx.hand.length('S') < 4, 'accept'),
        ):
            placement = self.call('spade_invite_' + action + '_' + bid.lower())
            placement.when = '1NP2CP2HP2SP'
            placement.bid = bid
            placement.applies = applies
            placement.meaning.action = 'spade_invitation_' + action
            placement.meaning.nature = ['natural']
            placement.meaning.acts = [action] if bid == 'P' else [action, 'final_placement']
            placement.meaning.target_suit = 'S' if bid in ('P', '4S') else 'N'
            if bid != 'P':
                placement.meaning.purpose_completed = True
            placement.description = 'Accept or decline the nonforcing spade invitation.'

        for suit, transfer, ordinary, special, invited in (
            ('C', '2S', '3C', '2NT', '4C'),
            ('D', '2NT', '3D', '3C', '4D'),
        ):
            ask = self.call('transfer_' + suit.lower())
            ask.when = '1NP'
            ask.bid = transfer
            ask.applies = lambda ctx, s=suit: minor_transfer(ctx, s)
            ask.private_purpose = lambda ctx, s=suit, low=ordinary, high=special: (
                {'kind': 'response_plan', 'trump': s,
                 'responses': {low: 'P', high: '3NT' if minor_invite(ctx, s) else '3' + s}}
                if not shapely_invite(ctx, s) else None)
            ask.meaning.action = 'minor_transfer'
            ask.meaning.nature = ['artificial']
            ask.meaning.acts = ['directive']
            ask.meaning.target_suit = suit
            ask.description = 'Six-plus minor transfer: weak signoff, good-suit 3NT invite, or shapely 5m invite.'

            for answer, applies, action in (
                (ordinary, lambda ctx, s=suit: ordinary_accept(ctx, s), 'ordinary'),
                (special, lambda ctx, s=suit: superaccept(ctx, s), 'superaccept'),
            ):
                reply = self.call('transfer_' + suit.lower() + '_' + action)
                reply.when = '1NP' + transfer + 'P'
                reply.bid = answer
                reply.applies = applies
                reply.meaning.action = 'minor_transfer_' + action
                reply.meaning.nature = ['artificial' if answer != ordinary else 'natural']
                reply.meaning.acts = ['descriptive']
                reply.meaning.target_suit = suit
                reply.description = 'Superaccept says an invitation is accepted; ordinary reply does not.'

                prefix = '1NP' + transfer + 'P' + answer + 'P'
                if answer == ordinary:
                    end = self.call('transfer_' + suit.lower() + '_ordinary_pass')
                    end.when = prefix
                    end.bid = 'P'
                    end.applies = lambda ctx, s=suit: weak_minor(ctx, s) or minor_invite(ctx, s)
                    end.meaning.action = 'minor_transfer_stop'
                    end.meaning.nature = ['natural']
                    end.meaning.acts = ['signoff']
                else:
                    for bid, applies, action_name in (
                        ('3' + suit, weak_minor, 'weak_signoff'),
                        ('3NT', minor_invite, 'accepted_3nt'),
                    ):
                        follow = self.call('transfer_' + suit.lower() + '_' + action_name)
                        follow.when = prefix
                        follow.bid = bid
                        follow.applies = lambda ctx, s=suit, fn=applies: fn(ctx, s)
                        follow.meaning.action = action_name
                        follow.meaning.nature = ['natural']
                        follow.meaning.acts = ['signoff']
                        follow.meaning.target_suit = 'N' if bid == '3NT' else suit
                        follow.meaning.acts = ['signoff', 'final_placement']
                        follow.meaning.purpose_completed = True

                shape = self.call('transfer_' + suit.lower() + '_invite_5m_after_' + answer.lower())
                shape.when = prefix
                shape.bid = invited
                shape.applies = lambda ctx, s=suit: shapely_invite(ctx, s)
                shape.meaning.action = 'shapely_minor_game_invitation'
                shape.meaning.nature = ['natural']
                shape.meaning.acts = ['invite']
                shape.meaning.target_suit = suit
                shape.meaning.shape_invitation = True
                shape.meaning.invite_acceptance = {'mode': 'minor_controls', 'trump': suit, 'minimum': 14.5}
                shape.description = 'Seven-plus minor with strong shape invites 5m; opener judges controls.'

                invite_prefix = prefix + invited + 'P'
                for verdict_bid, applies, act in (
                    ('P', lambda ctx, s=suit: minor_game_control_points(ctx.hand, s) < 14.5, 'reject'),
                    ('5' + suit, lambda ctx, s=suit: minor_game_control_points(ctx.hand, s) >= 14.5, 'accept'),
                ):
                    verdict = self.call('transfer_' + suit.lower() + '_' + verdict_bid.lower()
                                        + '_after_' + invited.lower() + '_' + action)
                    verdict.when = invite_prefix
                    verdict.bid = verdict_bid
                    verdict.applies = applies
                    verdict.meaning.action = 'shapely_minor_game_' + act
                    verdict.meaning.nature = ['natural']
                    verdict.meaning.acts = [act]
                    verdict.meaning.target_suit = suit
                    if act == 'accept':
                        verdict.meaning.acts = ['accept', 'final_placement']
                        verdict.meaning.purpose_completed = True
                    verdict.description = '5m invitation judged by retained trump HCP and outside controls.'

        # Six-four majors: game-only hands use direct Texas (in that gadget).
        # Slam-interest hands start with Stayman; H/S are handled symmetrically.
        for long_major, short_major in (('H', 'S'), ('S', 'H')):
            denial = '1NP2CP2DP'
            weak_transfer = '4D' if long_major == 'H' else '4H'
            weak = self.call('six_four_' + long_major.lower() + '_weak_slam_transfer')
            weak.when = denial
            weak.bid = weak_transfer
            weak.applies = lambda ctx, s=long_major: (six_four_long_major(ctx) == s
                                                       and six_four_slam_band(ctx) == 'weak')
            weak.meaning.action = 'six_four_weak_slam_transfer'
            weak.meaning.nature = ['artificial']
            weak.meaning.acts = ['directive', 'slam_try', 'game_forcing']
            weak.meaning.forcing = 'game_forcing'
            weak.meaning.target_suit = long_major
            weak.description = 'Weak slam interest after 2D: transfer to four of the six-card major.'

            complete = self.call('six_four_' + long_major.lower() + '_complete_weak_transfer')
            complete.when = denial + weak_transfer + 'P'
            complete.bid = '4' + long_major
            complete.applies = lambda ctx: ctx.hand is not None
            complete.meaning.action = 'complete_six_four_weak_slam_transfer'
            complete.meaning.nature = ['natural']
            complete.meaning.acts = ['descriptive']
            complete.meaning.target_suit = long_major
            complete.meaning.agreed_suit = long_major
            complete.effect('agreed_suit').suit = long_major
            complete.description = 'Complete the transfer; further slam choice awaits simulation.'

            strong_show = self.call('six_four_' + long_major.lower() + '_show_four_after_denial')
            strong_show.when = denial
            strong_show.bid = '3' + short_major
            strong_show.applies = lambda ctx, s=long_major: (six_four_long_major(ctx) == s
                                                              and six_four_slam_band(ctx)
                                                              in ('moderate', 'strong'))
            strong_show.meaning.action = 'six_four_slam_show_four_major'
            strong_show.meaning.nature = ['natural']
            strong_show.meaning.acts = ['descriptive', 'slam_try', 'game_forcing']
            strong_show.meaning.forcing = 'game_forcing'
            strong_show.meaning.target_suit = short_major
            strong_show.description = 'Moderate/strong slam interest: show the four-card major after 2D.'

            three_nt = self.call('six_four_' + long_major.lower() + '_opener_three_notrump')
            three_nt.when = denial + '3' + short_major + 'P'
            three_nt.bid = '3NT'
            three_nt.applies = lambda ctx: ctx.hand is not None
            three_nt.meaning.action = 'six_four_major_no_fit_notrump'
            three_nt.meaning.nature = ['natural']
            three_nt.meaning.acts = ['descriptive']
            three_nt.meaning.target_suit = 'N'
            three_nt.description = 'After denying a four-card major, offer 3NT; responder uses sampling.'

            choice_prefix = denial + '3' + short_major + 'P3NTP'
            game = self.call('six_four_' + long_major.lower() + '_moderate_game_after_three_nt')
            game.when = choice_prefix
            game.bid = '4' + long_major
            game.applies = lambda ctx, s=long_major: (six_four_long_major(ctx) == s
                                                       and six_four_slam_band(ctx) == 'moderate')
            game.meaning.action = 'six_four_major_simulated_game'
            game.meaning.nature = ['natural']
            game.meaning.acts = ['signoff', 'final_placement']
            game.meaning.target_suit = long_major
            game.meaning.agreed_suit = long_major
            game.meaning.quality_upgrade = True
            game.meaning.purpose_completed = True
            game.effect('agreed_suit').suit = long_major
            game.description = 'Moderate slam interest stops at 4M when sampled deals favor game.'

            for minor in 'CD':
                cue = self.call('six_four_' + long_major.lower() + '_'
                                + minor.lower() + '_cue_after_three_nt')
                cue.when = choice_prefix
                cue.bid = '4' + minor
                cue.applies = lambda ctx, s=long_major, m=minor: (
                    six_four_long_major(ctx) == s
                    and six_four_slam_band(ctx) in ('moderate', 'strong')
                    and six_four_first_minor_control(ctx) == m)
                cue.meaning.action = 'six_four_major_control_cue'
                cue.meaning.nature = ['artificial']
                cue.meaning.acts = ['slam_try', 'control_showing', 'game_forcing']
                cue.meaning.forcing = 'game_forcing'
                cue.meaning.target_suit = long_major
                cue.meaning.agreed_suit = long_major
                cue.meaning.control_suit = minor
                cue.effect('agreed_suit').suit = long_major
                cue.description = 'Control cue with the six-card major agreed; later choices need simulation.'
