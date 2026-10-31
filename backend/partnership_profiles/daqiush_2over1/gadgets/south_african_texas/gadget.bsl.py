# Confirmed: 4C/4D transfer to H/S, respectively, with 6+ cards and game
# strength measured by responder's K-R plus 15 as opener's minimum.
GAME_KR_TOTAL = 25
# Tunable initial relative-quality baselines calibrated from owner-labelled
# six-card-major examples. Seven-card suits and second four-card suits are not
# classified by these first-cut values.
SLAM_INTEREST = {
    'no_shortage': {'hcp': 13, 'kr_delta': 1.5},
    'small_singleton': {'hcp': 11, 'kr_delta': 2.6},
}


def shapely_second_minor_strength(ctx, trump):
    """Adjusted honor count for a 6M-5m-1-1 hand; None means other shapes."""
    if ctx.hand is None or ctx.hand.length(trump) != 6:
        return None
    other_major = 'S' if trump == 'H' else 'H'
    if ctx.hand.length(other_major) != 1:
        return None
    if sorted(ctx.hand.length(suit) for suit in 'CD') != [1, 5]:
        return None
    minor_short = 'C' if ctx.hand.length('C') == 1 else 'D'
    points = ctx.hand.hcp
    for suit in (other_major, minor_short):
        rank = ctx.hand.holding(suit)
        ordinary = {'A': 4, 'K': 3, 'Q': 2, 'J': 1}.get(rank, 0)
        retained = {'A': 4, 'K': 1}.get(rank, 0)
        points += retained - ordinary
    return points


def has_texas_game(ctx, suit):
    length = None if ctx.hand is None else convention_length(ctx.hand, suit)
    if length is None or length < 6:
        return False
    if sorted((ctx.hand.length('H'), ctx.hand.length('S'))) == [4, 6]:
        return 7 <= shapely_combined_effective_points(ctx.hand) < 10
    shaped_points = shapely_second_minor_strength(ctx, suit)
    return (ctx.hand_quality['kr_points'] + 15 >= GAME_KR_TOTAL
            or shaped_points is not None and 4 <= shaped_points <= 6)


# A seventh (or later) trump is converted through K-R rather than by adding
# a raw HCP: K-R already pays for the extra length, so the same honour
# strength reaches a higher total and the game/slam bands below are K-R
# floors. Seven-card hands with game strength use Texas; invitational ones
# transfer and raise to three; weaker ones transfer and pass.
SEVEN_GAME_KR = 10.0
SEVEN_INVITE_KR = 8.0
SEVEN_SLAM_KR = 16.0
SEVEN_SLAM_SINGLETON_KR = 14.0
SEVEN_KEYCARD_KR = 17.0


def long_major_band(ctx, suit):
    """K-R strength band for a seven-plus card major."""
    length = None if ctx.hand is None else convention_length(ctx.hand, suit)
    if length is None or length < 7:
        return None
    kr = ctx.hand_quality['kr_points']
    if kr >= SEVEN_GAME_KR:
        return 'game'
    if kr >= SEVEN_INVITE_KR:
        return 'invite'
    return 'weak'


def _side_class(ctx, suit):
    """Classify the three side suits around the long major.

    ``no_shortage``: every side suit holds two or more cards.
    ``small_singleton``: exactly one side suit is a low singleton.
    Anything else (voids, high singletons) is its own route.
    """

    side_lengths = sorted(ctx.hand.length(other) for other in 'SHDC'
                          if other != suit)
    if side_lengths and side_lengths[0] >= 2:
        return 'no_shortage', None
    if side_lengths.count(1) == 1 and side_lengths[0] == 1:
        singleton = [other for other in 'SHDC' if other != suit
                     and ctx.hand.length(other) == 1][0]
        if ctx.hand.holding(singleton) in 'T98765432':
            return 'small_singleton', singleton
    return 'other', None


def six_card_slam_interest(ctx, suit):
    length = None if ctx.hand is None else convention_length(ctx.hand, suit)
    if length is None or length < 6:
        return False
    side_class, _ = _side_class(ctx, suit)
    if side_class == 'no_shortage':
        threshold = SLAM_INTEREST['no_shortage']
    elif side_class == 'small_singleton':
        threshold = SLAM_INTEREST['small_singleton']
    else:
        return False
    if length >= 7:
        floor = (SEVEN_SLAM_SINGLETON_KR if side_class == 'small_singleton'
                 else SEVEN_SLAM_KR)
        return ctx.hand_quality['kr_points'] >= floor
    # A six-card hand compares raw HCP plus honour quality (K-R delta).
    return (ctx.hand.hcp >= threshold['hcp']
            and ctx.hand_quality['kr_delta'] >= threshold['kr_delta'])


def game_only_texas(ctx, suit):
    """Game-only Texas: 6+ trumps and game strength, independent of shape."""
    length = convention_length(ctx.hand, suit)
    if not has_texas_game(ctx, suit) or length < 6:
        return False
    if length >= 7:
        return (long_major_band(ctx, suit) == 'game'
                and not six_card_slam_interest(ctx, suit)
                and not slam_keycard_texas(ctx, suit))
    return (not six_card_slam_interest(ctx, suit)
            and not slam_keycard_texas(ctx, suit))


def slam_keycard_texas(ctx, suit):
    """The 6322 six-card hand already committed to slam if keycards permit.

    A seventh card is measured in K-R rather than by discounting HCP.
    """
    length = convention_length(ctx.hand, suit)
    if not has_texas_game(ctx, suit) or length not in (6, 7):
        return False
    if min(ctx.hand.length(other) for other in 'SHDC' if other != suit) < 2:
        return False
    if length >= 7:
        return ctx.hand_quality['kr_points'] >= SEVEN_KEYCARD_KR
    return ctx.hand.hcp >= 17


def texas_ordinary_slam(ctx, suit):
    """A single-suit six-plus-card major asks keycards through Texas."""
    return (ctx.hand is not None
            and convention_length(ctx.hand, suit) in (6, 7)
            and six_card_slam_interest(ctx, suit)
            and max(ctx.hand.length(s) for s in 'CD') < 4
            and min(ctx.hand.length(s) for s in 'HS') < 4)


def shapely_game_texas(ctx, suit):
    points = shapely_second_minor_strength(ctx, suit)
    return (points is not None and 4 <= points <= 6
            and has_texas_game(ctx, suit)
            and not six_card_slam_interest(ctx, suit))


def exclusion_void_hand(ctx, suit):
    """A void plus slam strength keeps the transfer space for exclusion keycard.

    The first response already chooses between this route and Texas-4NT, so a
    hand that will ask exclusion keycards must not consume the space with
    Texas. The expected-value comparison is approximated by preferring the
    more accurate exclusion count whenever a side void exists; without a void
    ordinary 4NT remains the only keycard route.
    """
    return (ctx.hand is not None and ctx.hand_quality['kr_points'] >= 17
            and any(ctx.hand.length(other) == 0 for other in 'SHDC'
                    if other != suit))


def texas_hearts(ctx):
    return (not exclusion_void_hand(ctx, 'H')
            and (game_only_texas(ctx, 'H') or shapely_game_texas(ctx, 'H')
                 or slam_keycard_texas(ctx, 'H')
                 or texas_ordinary_slam(ctx, 'H')))


def texas_spades(ctx):
    return (not exclusion_void_hand(ctx, 'S')
            and (game_only_texas(ctx, 'S') or shapely_game_texas(ctx, 'S')
                 or slam_keycard_texas(ctx, 'S')
                 or texas_ordinary_slam(ctx, 'S')))


def public_hearts(ctx):
    return has_texas_game(ctx, 'H')


def public_spades(ctx):
    return has_texas_game(ctx, 'S')


def unprotected_kq(ctx):
    if ctx.hand is None:
        return None
    count = 0
    for suit in 'SHDC':
        holding = ctx.hand.holding(suit)
        if 'K' in holding and 'A' not in holding:
            count += 1
        if 'Q' in holding and 'A' not in holding and 'K' not in holding:
            count += 1
    return count


def wants_declarer(ctx):
    count = unprotected_kq(ctx)
    return count is not None and count > 1


def does_not_want_declarer(ctx):
    count = unprotected_kq(ctx)
    return count is not None and count <= 1


class SouthAfricanTexas(Gadget):
    id = 'south_african_texas'
    namespace = 'daqiush_2over1'
    name = 'South African Texas after 1NT'
    author = Author('Daqiush')

    def build(self):
        self.evaluator('unprotected_kq_count', unprotected_kq)
        self.evaluator('texas_H_public', public_hearts)
        self.evaluator('texas_S_public', public_spades)
        self.evaluator('six_card_slam_interest_H', lambda ctx: six_card_slam_interest(ctx, 'H'))
        self.evaluator('six_card_slam_interest_S', lambda ctx: six_card_slam_interest(ctx, 'S'))
        self.evaluator('long_major_band_H', lambda ctx: long_major_band(ctx, 'H'))
        self.evaluator('long_major_band_S', lambda ctx: long_major_band(ctx, 'S'))
        self.evaluator('texas_slam_keycard_H', lambda ctx: slam_keycard_texas(ctx, 'H'))
        self.evaluator('texas_slam_keycard_S', lambda ctx: slam_keycard_texas(ctx, 'S'))
        for suit, ask, weak, strong, eligible in (
            ('H', '4C', '4D', '4H', texas_hearts),
            ('S', '4D', '4H', '4S', texas_spades),
        ):
            call = self.call('texas_' + suit.lower())
            call.when = '1NP'
            call.bid = ask
            call.applies = eligible
            call.private_purpose = {
                'kind': 'response_plan', 'trump': suit,
                'responses': {weak: strong, strong: 'P'},
                'skip_if': {'min_hcp': 17, 'side_lengths': [2, 2, 3]},
            }
            call.meaning.action = 'transfer'
            call.meaning.target_suit = suit
            call.meaning.nature = ['artificial']
            call.meaning.acts = ['directive', 'game_forcing']
            call.meaning.forcing = 'game_forcing'
            call.meaning.agreed_suit = suit
            call.meaning.strength_evidence = {
                'model': 'kaplan_rubens_or_shapely_effective', 'partner_min': 15,
                'shape_minimum': 4,
                'shape_lengths': [[1, 1, 5, 6], [1, 2, 4, 6], [0, 3, 4, 6]]}
            call.meaning.public_evidence = {
                'evaluator': 'texas_' + suit + '_public', 'equals': True,
                'bounds': {'min_lengths': {suit: 6}},
            }
            call.effect('agreed_suit').suit = suit
            call.description = ('South African Texas transfer with a six-card major, '
                                'game strength or the authored 6M–5m shape exception, '
                                'and a privately fixed game-only purpose.')

            for answer, applies, id_suffix, natural in (
                (weak, does_not_want_declarer, 'decline_declarer', False),
                (strong, wants_declarer, 'choose_declarer', True),
            ):
                reply = self.call('texas_' + suit.lower() + '_' + id_suffix)
                reply.when = '1NP' + ask + 'P'
                reply.bid = answer
                reply.applies = applies
                reply.meaning.action = 'transfer_acceptance'
                reply.meaning.target_suit = suit
                reply.meaning.nature = ['natural' if natural else 'artificial']
                reply.meaning.acts = ['descriptive']
                reply.meaning.public_evidence = {
                    'evaluator': 'unprotected_kq_count',
                    'min': 2 if natural else 0,
                    'max': 16 if natural else 1,
                }
                reply.description = ('Wants' if natural else 'Does not want') + ' declarership according to unprotected K/Q count.'

            placed = self.call('texas_' + suit.lower() + '_game_placement')
            placed.when = '1NP' + ask + 'P' + weak + 'P'
            placed.bid = strong
            placed.applies = lambda ctx: False  # Selected by the initiator's saved purpose.
            placed.meaning.action = 'game_only_texas_placement'
            placed.meaning.historical_only = True
            placed.meaning.nature = ['natural']
            placed.meaning.acts = ['final_placement', 'signoff']
            placed.meaning.target_suit = suit
            placed.meaning.agreed_suit = suit
            placed.description = 'Responder completes the lower Texas answer at game level.'

            completed = self.call('texas_' + suit.lower() + '_game_completed')
            completed.when = '1NP' + ask + 'P' + weak + 'P' + strong + 'P'
            completed.bid = 'P'
            completed.meaning.action = 'game_only_texas_complete'
            completed.meaning.nature = ['natural']
            completed.meaning.acts = ['signoff']
            completed.meaning.target_suit = suit
            completed.description = 'Responder placed the agreed major game after the lower Texas answer.'
