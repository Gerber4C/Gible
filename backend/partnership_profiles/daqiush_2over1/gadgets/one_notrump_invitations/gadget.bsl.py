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
            and not poor_eight(ctx)
            and (not strong_nine(ctx) or non_good_minor_invite_2nt(ctx))
            and not any(direct_minor_game(ctx, s) or solid_minor_three_notrump(ctx, s)
                        for s in 'CD')
            and not (sorted(ctx.hand.length(s) for s in 'CD') == [5, 6]
                     and min(ctx.hand.length(s) for s in 'HS') <= 1)
            and not (ctx.hand.length('C') == 5 and ctx.hand.length('D') == 5
                     and min(ctx.hand.length('H'), ctx.hand.length('S')) == 1)
            and not any(minor_invite(ctx, s) or shapely_invite(ctx, s)
                        for s in 'CD'))

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
    if direct_notrump_power(ctx) == '7NT':
        return False  # 22+ (or a good 21) places 7NT without Stayman.
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


def no_shortage_continue_control(ctx, suit):
    return (ctx.hand is not None
            and (ctx.hand.contains_rank(suit, 'A')
                 or ctx.hand.contains_rank(suit, 'K')
                 or ctx.hand.length(suit) <= 1))


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
    if named_evaluator(ctx, 'good_16_17_3c_family'):
        return False  # These hands use the 3C major inquiry first.
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


def four_four_four_one(ctx, answer):
    """Any 4441 without a shown major fit asks the four-card minor with 4C."""
    if ctx.hand is None:
        return False
    if sorted(ctx.hand.length(s) for s in 'SHDC') != [1, 4, 4, 4]:
        return False
    if answer in ('2H', '2S'):
        return ctx.hand.length(answer[-1]) != 4
    return True


def minor_slam_probe(ctx):
    club_length = 0 if ctx.hand is None else ctx.hand.length('C')
    diamond_length = 0 if ctx.hand is None else ctx.hand.length('D')
    return (ctx.hand is not None and ctx.hand.hcp >= 12
            and ctx.hand_quality['kr_points'] >= 14
            and max(ctx.hand.length(s) for s in 'HS') <= 3
            and max(club_length, diamond_length) == 5
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


def strong_nine_minor(ctx, suit):
    """A strong nine with a six-card minor invites 3NT through the transfer."""
    return (ctx.hand is not None and ctx.hand.length(suit) >= 6
            and strong_nine(ctx)
            and max(ctx.hand.length(s) for s in 'HS') <= 3)


def minor_invite(ctx, suit):
    return (ctx.hand is not None and ctx.hand.length(suit) >= 6
            and ctx.hand.hcp in (8, 9) and not poor_eight(ctx)
            and not strong_nine(ctx) and good_minor(ctx, suit)
            and not minor_three_notrump(ctx)
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
    if minor_slam_transfer(ctx, suit):
        return False  # Slam interest transfers first to keep the space below game.
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


def minor_slam_transfer(ctx, suit):
    """A six-plus minor with slam strength and no four-card major transfers.

    Only the minimum length and the major-length ceiling matter: the second
    minor can be anywhere from one to five cards, and K-R converts the rare
    shapes (6-5, 8-4) so they need no separate definition.
    """
    return (ctx.hand is not None and ctx.hand.length(suit) >= 6
            and minor_slam_interest(ctx.hand)
            and max(ctx.hand.length(s) for s in 'HS') <= 3)


MINOR_SERIOUS_OVERSTRENGTH_HCP = 18


def minor_serious_overstrength(ctx, suit):
    """Strength that reserves the cheapest space for the serious 3NT ladder.

    A responder with 18+ HCP opposite a 15--17 notrump has already exceeded
    the ordinary game range.  Even with a readily available side-suit
    control, serious 3NT comes first; opener's forced cue then lets responder
    ask keycards without spending that space on an advance cue.
    """
    return (minor_slam_transfer(ctx, suit)
            and ctx.hand.hcp >= MINOR_SERIOUS_OVERSTRENGTH_HCP)


def minor_control(ctx, suit):
    return shortage_has_control(ctx, suit)


def slam_transfer_shape(ctx, suit):
    """Six-four (or a single long minor) uses the cue route; 6-5 keeps 4NT."""
    other = 'D' if suit == 'C' else 'C'
    return ctx.hand is not None and ctx.hand.length(other) <= 4


def minor_stopper(ctx, suit):
    return ctx.hand is not None and ctx.hand.honor_count(suit, ('A', 'K', 'Q')) >= 1


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
            and (weak_minor(ctx, suit) or minor_invite(ctx, suit) or shapely_invite(ctx, suit)
                 or minor_slam_transfer(ctx, suit)))


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


MINOR_THREE_NT_KR = 11.0


def non_good_minor_invite_2nt(ctx):
    """Below the good-suit 3NT band, a non-good six/seven minor invites."""
    if ctx.hand is None:
        return False
    minor = 'C' if ctx.hand.length('C') >= ctx.hand.length('D') else 'D'
    return (ctx.hand.length(minor) in (6, 7)
            and ctx.hand.hcp in (8, 9)
            and not good_minor(ctx, minor)
            and ctx.hand_quality['kr_points'] < MINOR_THREE_NT_KR
            and max(ctx.hand.length(s) for s in 'HS') <= 3)


def minor_three_notrump(ctx):
    """A six- or seven-card minor in the good-suit 3NT K-R band.

    The owner lowered the floor to K-R 11.0; the ceiling is the cue-bid
    slam-interest lower bound, so the band is
    [MINOR_THREE_NT_KR, minor-slam interest).
    """
    if ctx.hand is None:
        return False
    minor = 'C' if ctx.hand.length('C') >= ctx.hand.length('D') else 'D'
    return (ctx.hand.length(minor) in (6, 7)
            and max(ctx.hand.length(s) for s in 'HS') <= 3
            and ctx.hand_quality['kr_points'] >= MINOR_THREE_NT_KR
            and not minor_slam_interest(ctx.hand))


def minor_featureless_invite(ctx):
    """A six/seven-card non-good minor invite below the 3NT K-R band."""
    if ctx.hand is None:
        return False
    minor = 'C' if ctx.hand.length('C') >= ctx.hand.length('D') else 'D'
    return (ctx.hand.length(minor) in (6, 7)
            and max(ctx.hand.length(s) for s in 'HS') <= 3
            and ctx.hand.hcp in (8, 9)
            and not poor_eight(ctx)
            and not good_minor(ctx, minor)
            and ctx.hand_quality['kr_points'] < MINOR_THREE_NT_KR
            and not minor_slam_interest(ctx.hand))


def flat_minor_333_three_notrump(ctx):
    return (ctx.hand is not None
            and not named_evaluator(ctx, 'good_16_17_3c_family')
            and sorted(ctx.hand.length(s) for s in 'SHDC') == [3, 3, 3, 4]
            and max(ctx.hand.length('H'), ctx.hand.length('S')) == 3
            and 10 <= ctx.hand.hcp <= 17)


class OneNotrumpInvitations(Gadget):
    id = 'one_notrump_invitations'
    namespace = 'daqiush_2over1'
    name = '1NT natural and minor invitations'
    author = Author('Daqiush')

    def build(self):
        self.evaluator('strong_notrump_power', direct_notrump_power)
        for contract in ('5NT', '6NT', '7NT'):
            power = self.call('strong_notrump_' + contract.lower())
            power.when = '1NP'
            power.bid = contract
            power.applies = (lambda ctx, c=contract: (
                direct_notrump_power(ctx) == c
                and not (c == '5NT' and game_stayman(ctx))
                and not (c == '5NT'
                         and named_evaluator(ctx, 'five_four_shortage_any'))))
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

        nt_route_prefixes = (
            '1NP2CP2DP', '1NP2CP2HP', '1NP2CP2SP',
            '1NP2DP2HP', '1NP2HP2SP',
            '1NP2DP2SP', '1NP2DP2NP', '1NP2DP3CP', '1NP2DP3HP',
            '1NP2HP2NP', '1NP2HP3CP', '1NP2HP3DP',
            '1NP3CP3DP', '1NP3CP3HP', '1NP3CP3SP',
        )
        for prefix in nt_route_prefixes:
            for contract in ('5NT', '6NT', '7NT'):
                call = self.call('strong_notrump_' + contract.lower() + '_'
                                 + prefix.lower())
                call.when = prefix
                call.bid = contract
                call.applies = (lambda ctx, c=contract, p=prefix: (
                    direct_notrump_power(ctx) == c
                    and not (c == '5NT'
                             and named_evaluator(ctx, 'flat_five_major_any'))
                    and not (c == '5NT'
                             and p in ('1NP2CP2HP', '1NP2CP2SP')
                             and ctx.hand.length(p[-2]) >= 4)
                    and not (c == '5NT'
                             and p in ('1NP3CP3HP', '1NP3CP3SP')
                             and ctx.hand.length(p[-2]) >= 3)
                    and not (c == '5NT'
                             and p in ('1NP3CP3DP', '1NP3CP3HP', '1NP3CP3SP')
                             and named_evaluator(ctx, 'five_four_shortage_any'))))
                call.meaning.action = 'strong_notrump_placement'
                call.meaning.nature = ['natural']
                call.meaning.acts = (['invite', 'slam_try'] if contract == '5NT'
                                     else ['signoff', 'final_placement'])
                call.meaning.target_suit = 'N'
                if contract != '5NT':
                    call.meaning.purpose_completed = True
                call.description = ('Strong notrump ladder after the route: '
                                    + contract + ' from the 20-21+ range.')

        for contract, accepts in (('6NT', False), ('7NT', True)):
            answer = self.call('strong_notrump_five_nt_' + contract.lower())
            answer.when = '1NP5NTP'
            answer.bid = contract
            # Quantitative 5NT invites the top half of the 15-17 range, so
            # 16 HCP accepts (the owner's 50% rule); 15 declines.
            for prefix in nt_route_prefixes:
                route_answer = self.call('strong_notrump_five_nt_' + contract.lower()
                                         + '_after_' + prefix.lower())
                route_answer.when = prefix + '5NTP'
                route_answer.bid = contract
                route_answer.applies = (lambda ctx, high=accepts: (
                    ctx.hand is not None and (ctx.hand.hcp >= 16) == high))
                route_answer.meaning.action = ('grand_slam_invitation_'
                                               + ('accept' if accepts else 'reject'))
                route_answer.meaning.nature = ['natural']
                route_answer.meaning.acts = ([('accept' if accepts else 'reject'),
                                              'final_placement'])
                route_answer.meaning.target_suit = 'N'
                route_answer.meaning.purpose_completed = True
                route_answer.description = ('Answer the 5NT grand-slam invitation '
                                            'by the 1NT opening limit.')
            answer.applies = lambda ctx, high=accepts: (ctx.hand is not None
                                                        and (ctx.hand.hcp >= 16) == high)
            answer.meaning.action = 'grand_slam_invitation_' + ('accept' if accepts else 'reject')
            answer.meaning.nature = ['natural']
            answer.meaning.acts = [('accept' if accepts else 'reject'), 'final_placement']
            answer.meaning.target_suit = 'N'
            answer.meaning.purpose_completed = True
            answer.description = 'Answer the natural 5NT grand-slam invitation by the 1NT opening limit.'

        for bid, applies, action in (
            ('P', weak_featureless, 'weak_signoff'),
            ('3NT', lambda ctx: (game_featureless(ctx)
                                 or any(solid_minor_three_notrump(ctx, suit)
                                        for suit in 'CD')
                                 or minor_three_notrump(ctx)
                                 or flat_minor_333_three_notrump(ctx)),
             'good_nine_game'),
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
            if answer == '2H':
                reply.meaning.min_lengths = {'H': 4}
            elif answer == '2S':
                reply.meaning.min_lengths = {'S': 4}
                reply.meaning.max_lengths = {'H': 3}
            else:
                reply.meaning.max_lengths = {'H': 3, 'S': 3}

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
                 and not named_evaluator(ctx, 'good_16_17_4324')
                 and (a == '2D' or ctx.hand.length(a[-1]) < 4)
                 and not four_four_four_one(ctx, a)
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

            if answer in ('2D', '2H'):
                quantitative = self.call('good_16_17_4324_quantitative_after_'
                                         + answer.lower())
                quantitative.when = prefix
                quantitative.bid = '4NT'
                quantitative.applies = lambda ctx: named_evaluator(
                    ctx, 'good_16_17_4324')
                quantitative.meaning.action = 'quantitative_notrump_invitation'
                quantitative.meaning.nature = ['natural']
                quantitative.meaning.acts = ['invite']
                quantitative.meaning.target_suit = 'N'
                quantitative.meaning.hcp_min = 16
                quantitative.meaning.hcp_max = 17
                quantitative.meaning.shape_class = '4-3-2-4'
                quantitative.meaning.min_lengths = {'S': 4}
                quantitative.description = (
                    'Good 16-17 4-3-2-4 invites 6NT; after 2H the promised '
                    'four-card major is spades, and a fit uses the existing '
                    'major-fit route instead.')

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
                no_shortage.meaning.min_lengths = {'S': 2, 'H': 2, 'D': 2,
                                                   'C': 2, answer[-1]: 4}
                no_shortage.meaning.min_kr = 14.0
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
                refusal.applies = lambda ctx: ctx.hand is not None
                refusal.meaning.action = 'no_shortage_slam_decline'
                refusal.meaning.nature = ['natural']
                refusal.meaning.acts = ['reject', 'signoff', 'final_placement']
                refusal.meaning.target_suit = answer[-1]
                refusal.meaning.agreed_suit = answer[-1]
                refusal.description = 'Decline the no-shortage slam try at four of the agreed major.'

                # Third option: keep cue-bidding a side control. The
                # simulation policy selects among the keycard, game, and cue
                # candidates at this position.
                cue_bids = {'H': (('S', '4S'), ('C', '5C'), ('D', '5D')),
                            'S': (('C', '5C'), ('D', '5D'), ('H', '5H'))}[answer[-1]]
                for cue_suit, cue_bid in cue_bids:
                    cont = self.call('stayman_' + answer.lower()
                                     + '_no_shortage_continue_' + cue_suit.lower())
                    cont.when = prefix + '4DP'
                    cont.bid = cue_bid
                    cont.applies = (lambda ctx, s=cue_suit:
                                    no_shortage_continue_control(ctx, s))
                    cont.meaning.action = 'no_shortage_continue_cue'
                    cont.meaning.nature = ['artificial']
                    cont.meaning.acts = ['slam_try', 'control_showing']
                    cont.meaning.control_suit = cue_suit
                    cont.meaning.agreed_suit = answer[-1]
                    cont.meaning.target_suit = answer[-1]
                    cont.description = ('Keep cue-bidding a side control after the '
                                        'no-shortage major slam try.')

                continue_prefix = prefix + '4DP4' + answer[-1] + 'P'
                continue_ask = self.call('stayman_' + answer.lower()
                                         + '_no_shortage_after_refusal_keycard')
                continue_ask.when = continue_prefix
                continue_ask.bid = '4NT'
                continue_ask.applies = lambda ctx: ctx.hand is not None
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
                continue_pass.applies = lambda ctx: ctx.hand is not None
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
                # After 2H-3C, 3S is natural spades, 3H shows the fifth
                # heart, and 3D is the artificial club support.
                for bid, applies, action, target in (
                    ('3D', lambda ctx, a=answer, m=minor: a == '2D' and m == 'C'
                     and ctx.hand.length('D') >= 5, 'natural_diamonds', 'D'),
                    ('3S', lambda ctx, a=answer: a == '2H'
                     and ctx.hand.length('S') >= 4, 'natural_spades', 'S'),
                    ('3S', lambda ctx, a=answer: a == '2S'
                     and ctx.hand.length('S') >= 5, 'natural_spades', 'S'),
                    ('3S', lambda ctx, a=answer, m=minor: a == '2D'
                     and ctx.hand.length(m) >= 3
                     and minor_control(ctx, 'S'),
                     'minor_support_control', minor),
                    ('3H', lambda ctx, a=answer, m=minor: a == '2H' and m == 'C'
                     and not (a == '2H' and ctx.hand.length('S') >= 4)
                     and ctx.hand.length('H') >= 5, 'natural_hearts', 'H'),
                    (support_bid, lambda ctx, a=answer, m=minor: ctx.hand.length(m) >= 3
                     and not (a == '2D' and m == 'C' and ctx.hand.length('D') >= 5)
                     and not (a == '2H' and ctx.hand.length('S') >= 4), 'minor_support', minor),
                    ('3NT', lambda ctx, a=answer, m=minor: ctx.hand.length(m) < 3
                     and not (a == '2D' and m == 'C' and ctx.hand.length('D') >= 5)
                     and not (a == '2H' and ctx.hand.length('S') >= 4), 'natural_notrump', 'N'),
                ):
                    if (bid == '3D' and action == 'natural_diamonds'
                            and not (answer == '2D' and minor == 'C')):
                        continue
                    reply = self.call('stayman_' + answer.lower() + '_' + minor.lower()
                                      + '_' + action)
                    reply.when = probe_prefix
                    reply.bid = bid
                    reply.applies = applies
                    if action == 'minor_support':
                        reply.meaning.action = 'minor_support_cue'
                        reply.meaning.nature = ['artificial']
                        reply.meaning.acts = ['slam_try', 'support']
                        reply.meaning.agreed_suit = minor
                        reply.effect('agreed_suit').suit = minor
                    elif action == 'minor_support_control':
                        reply.meaning.action = 'minor_support_control'
                        reply.meaning.nature = ['artificial']
                        reply.meaning.acts = ['control_showing', 'slam_try']
                        reply.meaning.control_suit = 'S'
                        reply.meaning.agreed_suit = minor
                        reply.effect('agreed_suit').suit = minor
                    else:
                        reply.meaning.action = action
                        reply.meaning.nature = ['natural']
                        reply.meaning.acts = ['descriptive']
                    reply.meaning.target_suit = target
                    if action == 'natural_spades':
                        reply.description = (
                            'Natural fifth spade; it does not agree spades.'
                            if answer == '2S' else
                            'Natural four-card spade suit; it does not agree spades.')
                    elif action == 'natural_hearts':
                        reply.description = (
                            'Natural fifth heart; it does not agree hearts.')
                    else:
                        reply.description = ('Natural new suit, conventional '
                                             'minor support, or 3NT without support.')

                notrump_signoff = self.call('stayman_' + answer.lower() + '_'
                                            + minor.lower() + '_notrump_signoff')
                notrump_signoff.when = probe_prefix + '3NTP'
                notrump_signoff.bid = 'P'
                notrump_signoff.applies = (
                    lambda ctx: ctx.hand is not None
                    and not minor_slam_interest(ctx.hand))
                notrump_signoff.meaning.action = 'natural_minor_probe_notrump_signoff'
                notrump_signoff.meaning.nature = ['natural']
                notrump_signoff.meaning.acts = ['signoff', 'final_placement']
                notrump_signoff.meaning.target_suit = 'N'
                notrump_signoff.meaning.purpose_completed = True
                notrump_signoff.description = (
                    'Without further slam interest, pass the natural 3NT.')

                if answer == '2H' and minor == 'C':
                    hearts_notrump = self.call('stayman_2h_c_after_hearts_notrump')
                    hearts_notrump.when = probe_prefix + '3HP'
                    hearts_notrump.bid = '3NT'
                    hearts_notrump.applies = (
                        lambda ctx: ctx.hand is not None
                        and not minor_slam_interest(ctx.hand))
                    hearts_notrump.meaning.action = 'natural_minor_probe_hearts_notrump'
                    hearts_notrump.meaning.nature = ['natural']
                    hearts_notrump.meaning.acts = ['signoff', 'final_placement']
                    hearts_notrump.meaning.target_suit = 'N'
                    hearts_notrump.meaning.purpose_completed = True
                    hearts_notrump.description = (
                        'After opener shows five hearts, choose 3NT without '
                        'further slam interest.')

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

        for answer_prefix, answer_key in (
                ('1NP2CP2DP', '2D'),
                ('1NP2CP2HP', '2H'),
                ('1NP2CP2SP', '2S')):
            low_minor = self.call('four_minor_stayman_' + answer_key.lower())
            low_minor.when = answer_prefix
            low_minor.bid = '4C'
            low_minor.applies = (lambda ctx, a=answer_key: (
                minor_stayman_probe(ctx) or four_four_four_one(ctx, a)))
            low_minor.meaning.action = 'minor_stayman'
            low_minor.meaning.nature = ['artificial']
            low_minor.meaning.acts = ['inquiry', 'slam_try']
            low_minor.description = ('Ask about opener’s four-card minors; a four-four-'
                                     'four-one without a major fit also starts here.')

            for answer, applies, suit in (
                ('4D', lambda ctx: ctx.hand is not None and ctx.hand.length('C') >= 4, 'C'),
                ('4H', lambda ctx: ctx.hand is not None and ctx.hand.length('C') < 4
                 and ctx.hand.length('D') >= 4, 'D'),
                ('4NT', lambda ctx: ctx.hand is not None and ctx.hand.length('C') < 4
                 and ctx.hand.length('D') < 4, None),
            ):
                answer_call = self.call('four_minor_stayman_' + answer_key.lower()
                                        + '_answer_' + answer.lower())
                answer_call.when = answer_prefix + '4CP'
                answer_call.bid = answer
                answer_call.applies = applies
                answer_call.meaning.action = 'minor_stayman_response'
                answer_call.meaning.nature = ['artificial']
                answer_call.meaning.acts = ['descriptive']
                if suit:
                    answer_call.meaning.target_suit = suit
                    answer_call.meaning.agreed_suit = suit
                    answer_call.effect('agreed_suit').suit = suit
                answer_call.description = ('4D shows four clubs; 4H shows four diamonds '
                                           'without four clubs.')

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
                None if minor_slam_transfer(ctx, s) else
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

                # Slam-interest continuations. After the ordinary completion
                # the other minor is natural; after a superaccept the same bid
                # is a control cue. At the three level a cue shows a control
                # and doubles as a stopper ask; a four-level cue below the
                # minor game shows extra strength.
                slam_cues = []
                other = 'D' if suit == 'C' else 'C'
                if answer == ordinary:
                    om_bid = '3D' if suit == 'C' else '4C'
                    om = self.call('transfer_' + suit.lower() + '_other_minor')
                    om.when = prefix
                    om.bid = om_bid
                    om.applies = (lambda ctx, s=suit, o=other: (minor_slam_transfer(ctx, s)
                                                               and ctx.hand.length(o) == 4))
                    om.meaning.action = 'minor_slam_other_minor'
                    om.meaning.nature = ['natural']
                    om.meaning.acts = ['game_forcing']
                    om.meaning.forcing = 'game_forcing'
                    om.meaning.target_suit = other
                    om.description = 'Six-four (or longer) both-minor slam interest shows the other minor.'

                    om_prefix = prefix + om_bid + 'P'
                    for follow_bid, follow_target, follow_action in (
                        ('3NT', 'N', 'both_minor_notrump'),
                        ('4' + suit, suit, 'first_minor_agreement'),
                        ('5' + suit, suit, 'first_minor_game'),
                        ('4' + other, other, 'second_minor_agreement'),
                        ('5' + other, other, 'second_minor_game'),
                    ):
                        if follow_bid <= om_bid:
                            continue
                        follow = self.call('transfer_' + suit.lower() + '_both_minor_'
                                           + follow_bid.lower())
                        follow.when = om_prefix
                        follow.bid = follow_bid
                        follow.applies = lambda ctx: ctx.hand is not None
                        follow.meaning.action = follow_action
                        follow.meaning.nature = ['natural']
                        follow.meaning.acts = (['descriptive'] if follow_bid == '3NT'
                                               else ['signoff', 'final_placement'])
                        follow.meaning.target_suit = follow_target
                        if follow_target != 'N':
                            follow.meaning.agreed_suit = follow_target
                            follow.effect('agreed_suit').suit = follow_target
                        if follow_bid in ('5' + suit, '5' + other):
                            follow.meaning.purpose_completed = True

                        if follow_bid == '3NT':
                            stop = self.call('transfer_' + suit.lower()
                                             + '_both_minor_notrump_stop')
                            stop.when = om_prefix + '3NTP'
                            stop.bid = 'P'
                            stop.applies = lambda ctx: ctx.hand is not None
                            stop.meaning.action = 'both_minor_notrump_stop'
                            stop.meaning.nature = ['natural']
                            stop.meaning.acts = ['signoff', 'final_placement']
                            stop.meaning.target_suit = 'N'
                            stop.meaning.purpose_completed = True

                            # Slaw interest after opener's 3NT: the responder
                            # may still place either minor or keep driving.
                            for level in (5, 6):
                                for target in (suit, other):
                                    push = self.call('transfer_' + suit.lower()
                                                     + '_both_minor_push_'
                                                     + str(level) + target.lower())
                                    push.when = om_prefix + '3NTP'
                                    push.bid = str(level) + target
                                    push.applies = (lambda ctx, s=suit: (
                                        ctx.hand is not None
                                        and ctx.hand.length(s) >= 6
                                        and ctx.hand_quality['kr_points'] >= 15))
                                    push.meaning.action = 'both_minor_slam_push'
                                    push.meaning.nature = ['natural']
                                    push.meaning.acts = ['signoff', 'final_placement']
                                    push.meaning.target_suit = target
                                    push.meaning.agreed_suit = target
                                    if level == 6:
                                        push.meaning.purpose_completed = True

                                    close = self.call('transfer_' + suit.lower()
                                                      + '_both_minor_push_close_'
                                                      + str(level) + target.lower())
                                    close.when = om_prefix + '3NTP' + str(level) + target + 'P'
                                    close.bid = 'P'
                                    close.applies = lambda ctx: ctx.hand is not None
                                    close.meaning.action = 'both_minor_push_close'
                                    close.meaning.nature = ['natural']
                                    close.meaning.acts = ['signoff', 'final_placement']
                                    close.meaning.target_suit = target
                                    close.meaning.purpose_completed = True
                        elif follow_bid in ('4' + suit, '4' + other):
                            for level in (5, 6):
                                finish = self.call('transfer_' + suit.lower()
                                                   + '_both_minor_' + follow_bid.lower()
                                                   + '_' + str(level) + follow_target.lower())
                                finish.when = om_prefix + follow_bid + 'P'
                                finish.bid = str(level) + follow_target
                                finish.applies = lambda ctx: ctx.hand is not None
                                finish.meaning.action = 'both_minor_placement'
                                finish.meaning.nature = ['natural']
                                finish.meaning.acts = ['signoff', 'final_placement']
                                finish.meaning.target_suit = follow_target
                                finish.meaning.agreed_suit = follow_target
                                finish.meaning.purpose_completed = True

                    serious = self.call('transfer_' + suit.lower() + '_serious_3nt')
                    serious.when = prefix
                    serious.bid = '3NT'
                    serious.applies = (lambda ctx, s=suit: (minor_slam_transfer(ctx, s)
                                                            and slam_transfer_shape(ctx, s)
                                                            and (minor_serious_overstrength(ctx, s)
                                                                 or not any(minor_control(ctx, c)
                                                                            for c in ('H', 'S')))))
                    serious.meaning.action = 'minor_serious_3nt'
                    serious.meaning.nature = ['artificial']
                    serious.meaning.acts = ['slam_try']
                    serious.meaning.target_suit = 'N'
                    serious.description = ('The low-level serious 3NT: slam interest '
                                           'without a cue, or with overstrength that '
                                           'takes priority over an advance cue.')

                    # Control ladder after serious 3NT.  Partner's first
                    # cue is forced and says nothing about extra strength.
                    # Either partner then continues with the cheapest
                    # unshown control until the partnership has nothing
                    # further to show, a skipped suit is confirmed missing,
                    # or someone asks keycards / places the minor game.
                    serious_prefix = prefix + '3NTP'
                    game_minor = '5' + suit
                    cue_suits = [side for side in 'CDHS' if side != suit]
                    cue_sequences = [()]
                    for first_index in range(len(cue_suits)):
                        first = cue_suits[first_index]
                        cue_sequences.append((first,))
                        for second_index in range(first_index + 1, len(cue_suits)):
                            second = cue_suits[second_index]
                            cue_sequences.append((first, second))
                            for third_index in range(second_index + 1,
                                                      len(cue_suits)):
                                cue_sequences.append((first, second,
                                                      cue_suits[third_index]))

                    for sequence in cue_sequences:
                        sequence_label = ''.join(side.lower() for side in sequence)
                        if not sequence_label:
                            sequence_label = 'start'
                        node_prefix = serious_prefix
                        for shown in sequence:
                            node_prefix = node_prefix + '4' + shown + 'P'

                        if sequence:
                            partner_last = sequence[-1]
                            last_index = cue_suits.index(partner_last)
                            # Only suits above the previous cue were
                            # available to the partner who just bid.  A lower
                            # unshown suit was simply out of bidding space,
                            # so it is not yet known to be missing.
                            if len(sequence) > 1:
                                previous_index = cue_suits.index(sequence[-2])
                            else:
                                previous_index = -1
                            skipped = tuple(side for side in
                                            cue_suits[previous_index + 1:last_index]
                                            if side not in sequence)
                        else:
                            skipped = ()

                        if sequence:
                            remaining = []
                            last_index = cue_suits.index(sequence[-1])
                            for side_index in range(last_index + 1,
                                                    len(cue_suits)):
                                side = cue_suits[side_index]
                                if side not in sequence:
                                    remaining.append(side)
                        else:
                            remaining = [side for side in cue_suits
                                         if side not in sequence]

                        for target in remaining:
                            target_index = cue_suits.index(target)
                            lower = tuple(side for side in remaining
                                          if cue_suits.index(side) < target_index)
                            cue = self.call('transfer_' + suit.lower()
                                            + '_serious_' + sequence_label
                                            + '_cue_' + target.lower())
                            cue.when = node_prefix
                            cue.bid = '4' + target
                            cue.applies = (
                                lambda ctx, c=target, low=lower, skp=skipped:
                                (ctx.hand is not None
                                 and not any(not minor_control(ctx, x)
                                             for x in skp)
                                 and minor_control(ctx, c)
                                 and not any(minor_control(ctx, x)
                                             for x in low)))
                            cue.meaning.action = ('serious_forced_control_cue'
                                                  if not sequence
                                                  else 'serious_control_cue')
                            cue.meaning.nature = ['artificial']
                            cue.meaning.acts = ['control_showing', 'slam_try']
                            cue.meaning.control_suit = target
                            cue.meaning.agreed_suit = suit
                            cue.meaning.target_suit = suit
                            if not sequence:
                                cue.meaning.forced_control_cue = True
                            cue.effect('agreed_suit').suit = suit
                            cue.description = (
                                'Control cue after serious 3NT' if sequence else
                                'Forced control cue after serious 3NT; it does '
                                'not promise extra strength.')

                        if sequence:
                            ask = self.call('transfer_' + suit.lower()
                                            + '_serious_' + sequence_label
                                            + '_keycard')
                            ask.when = node_prefix
                            ask.bid = '4NT'
                            ask.applies = (
                                lambda ctx, skp=skipped:
                                (ctx.hand is not None
                                 and not any(not minor_control(ctx, x)
                                             for x in skp)))
                            ask.meaning.action = 'rkcb_1430'
                            ask.meaning.nature = ['artificial']
                            ask.meaning.acts = ['inquiry', 'keycard_asking']
                            ask.meaning.target_suit = suit
                            ask.meaning.agreed_suit = suit
                            ask.effect('agreed_suit').suit = suit
                            context = ask.effect('keycard_context')
                            context.trump_suit = suit
                            context.ask_call = '4N'
                            context.method = 'rkcb_1430'
                            context.status = 'pending'
                            ask.description = ('After the cue ladder, 4NT '
                                               'asks keycards for the agreed '
                                               'minor.')

                        game = self.call('transfer_' + suit.lower()
                                         + '_serious_' + sequence_label
                                         + '_game')
                        game.when = node_prefix
                        game.bid = game_minor
                        game.applies = lambda ctx: ctx.hand is not None
                        game.meaning.action = ('serious_game_signoff'
                                               if not sequence
                                               else 'serious_cue_game')
                        game.meaning.nature = ['natural']
                        game.meaning.acts = ['signoff', 'final_placement']
                        game.meaning.target_suit = suit
                        game.meaning.agreed_suit = suit
                        game.meaning.purpose_completed = True
                        game.description = ('Sign off in five of the minor.'
                                            if not sequence else
                                            'Return to the minor game.')

                    slam_cues = [('3H', 'H'), ('3S', 'S')]
                else:
                    # The other minor (3D for clubs, 4C for diamonds) is a
                    # control cue after the superaccept, never natural.
                    if suit == 'C':
                        slam_cues = [('3D', 'D'), ('3H', 'H'), ('3S', 'S')]
                    else:
                        slam_cues = [('3H', 'H'), ('3S', 'S'), ('4C', 'C')]

                for index in range(len(slam_cues)):
                    cue_bid, control = slam_cues[index]
                    prior = tuple(item[1] for item in slam_cues[:index])
                    cue_call = self.call('transfer_' + suit.lower() + '_slam_cue_'
                                         + cue_bid.lower())
                    cue_call.when = prefix
                    cue_call.bid = cue_bid
                    cue_call.applies = (lambda ctx, s=suit, c=control, p=prior: (
                        minor_slam_transfer(ctx, s) and slam_transfer_shape(ctx, s)
                        and not minor_serious_overstrength(ctx, s)
                        and minor_control(ctx, c)
                        and not any(minor_control(ctx, x) for x in p)))
                    cue_call.meaning.action = 'minor_slam_control_cue'
                    cue_call.meaning.nature = ['artificial']
                    cue_call.meaning.acts = ['slam_try', 'control_showing',
                                             'game_forcing']
                    cue_call.meaning.forcing = 'game_forcing'
                    cue_call.meaning.control_suit = control
                    cue_call.meaning.agreed_suit = suit
                    cue_call.meaning.target_suit = suit
                    cue_call.effect('agreed_suit').suit = suit
                    cue_call.description = ('Cue a control with the minor agreed, asking '
                                            'partner for the remaining stoppers.')

                    after_cue = prefix + cue_bid + 'P'
                    remaining = [s for s in 'CDHS' if s not in (suit, control)]
                    if '3NT' > cue_bid:
                        stopper = self.call('transfer_' + suit.lower() + '_stopper_after_'
                                            + cue_bid.lower())
                        stopper.when = after_cue
                        stopper.bid = '3NT'
                        stopper.applies = (lambda ctx, r=tuple(remaining): (
                            ctx.hand is not None and all(minor_stopper(ctx, s) for s in r)
                            and ctx.hand.hcp <= 16))
                        stopper.meaning.action = 'minor_slam_stopper_notrump'
                        stopper.meaning.nature = ['natural']
                        stopper.meaning.acts = ['signoff', 'final_placement']
                        stopper.meaning.target_suit = 'N'
                        stopper.meaning.purpose_completed = True
                        stopper.description = ('Stoppers in the remaining ask suits and no '
                                               'slam strength: play 3NT.')

                    minimum = self.call('transfer_' + suit.lower() + '_minimum_after_'
                                        + cue_bid.lower())
                    minimum.when = after_cue
                    minimum.bid = '4' + suit
                    minimum.applies = (lambda ctx: ctx.hand is not None and ctx.hand.hcp <= 16)
                    minimum.meaning.action = 'minor_slam_minimum_game'
                    minimum.meaning.nature = ['natural']
                    minimum.meaning.acts = ['descriptive']
                    minimum.meaning.target_suit = suit
                    minimum.meaning.agreed_suit = suit
                    minimum.description = ('A minimum declines the slam try at four of the '
                                           'minor; the partner simulates pass, five, or more cueing.')

                    for stop_bid in ('P', '5' + suit):
                        stop = self.call('transfer_' + suit.lower() + '_minimum_reply_'
                                         + stop_bid.lower() + '_after_' + cue_bid.lower())
                        stop.when = after_cue + '4' + suit + 'P'
                        stop.bid = stop_bid
                        stop.applies = lambda ctx: ctx.hand is not None
                        stop.meaning.action = 'minor_slam_minimum_reply'
                        stop.meaning.nature = ['natural']
                        stop.meaning.acts = ['signoff', 'final_placement']
                        stop.meaning.target_suit = suit
                        stop.meaning.purpose_completed = True
                        if stop_bid == '5' + suit:
                            close = self.call('transfer_' + suit.lower()
                                              + '_minimum_game_close_after_'
                                              + cue_bid.lower() + '_' + stop_bid.lower())
                            close.when = after_cue + '4' + suit + 'P' + stop_bid + 'P'
                            close.bid = 'P'
                            close.applies = lambda ctx: ctx.hand is not None
                            close.meaning.action = 'minor_slam_game_close'
                            close.meaning.nature = ['natural']
                            close.meaning.acts = ['signoff', 'final_placement']
                            close.meaning.target_suit = suit
                            close.meaning.purpose_completed = True

                    for lift in [s for s in 'CDHS' if '4' + s > '4' + suit
                                 and s not in (suit, control)]:
                        strong = self.call('transfer_' + suit.lower() + '_strength_cue_'
                                           + lift.lower() + '_after_' + cue_bid.lower())
                        strong.when = after_cue
                        strong.bid = '4' + lift
                        strong.applies = (lambda ctx, s=suit, c=lift: (
                            ctx.hand is not None and ctx.hand.hcp >= 17
                            and minor_control(ctx, c)))
                        strong.meaning.action = 'minor_slam_strength_cue'
                        strong.meaning.nature = ['artificial']
                        strong.meaning.acts = ['slam_try', 'control_showing']
                        strong.meaning.control_suit = lift
                        strong.meaning.agreed_suit = suit
                        strong.meaning.target_suit = suit
                        strong.effect('agreed_suit').suit = suit
                        strong.description = ('A four-level cue with the fit still at three '
                                              'shows extra strength.')

                        for finish_bid in ('5' + suit, '6' + suit):
                            finish = self.call('transfer_' + suit.lower() + '_strength_reply_'
                                               + finish_bid.lower() + '_' + lift.lower()
                                               + '_after_' + cue_bid.lower())
                            finish.when = after_cue + '4' + lift + 'P'
                            finish.bid = finish_bid
                            finish.applies = lambda ctx: ctx.hand is not None
                            finish.meaning.action = 'minor_slam_strength_reply'
                            finish.meaning.nature = ['natural']
                            finish.meaning.acts = ['signoff', 'final_placement']
                            finish.meaning.target_suit = suit
                            finish.meaning.purpose_completed = (finish_bid == '6' + suit)

                            close = self.call('transfer_' + suit.lower()
                                              + '_strength_game_close_'
                                              + finish_bid.lower() + '_' + lift.lower()
                                              + '_after_' + cue_bid.lower())
                            close.when = after_cue + '4' + lift + 'P' + finish_bid + 'P'
                            close.bid = 'P'
                            close.applies = lambda ctx: ctx.hand is not None
                            close.meaning.action = 'minor_slam_game_close'
                            close.meaning.nature = ['natural']
                            close.meaning.acts = ['signoff', 'final_placement']
                            close.meaning.target_suit = suit
                            close.meaning.purpose_completed = True

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
