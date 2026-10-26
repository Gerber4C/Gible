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


def has_texas_game(ctx, suit):
    return (ctx.hand is not None and ctx.hand.length(suit) >= 6
            and ctx.hand_quality['kr_points'] + 15 >= GAME_KR_TOTAL)


def six_card_slam_interest(ctx, suit):
    if ctx.hand is None or ctx.hand.length(suit) != 6:
        return False
    side_lengths = [ctx.hand.length(other) for other in 'SHDC' if other != suit]
    if max(side_lengths) != 3:
        return False  # A second suit or a different long-suit shape needs its own route.
    if sorted(side_lengths) == [2, 2, 3]:
        threshold = SLAM_INTEREST['no_shortage']
    elif sorted(side_lengths) == [1, 3, 3]:
        singleton = [other for other in 'SHDC' if other != suit and ctx.hand.length(other) == 1][0]
        if ctx.hand.holding(singleton) not in 'T98765432':
            return False
        threshold = SLAM_INTEREST['small_singleton']
    else:
        return False
    # Raw HCP sets the minimum for slam exploration. K-R minus raw HCP then
    # compares honor quality against the usual bonus of this six-card shape.
    hcp = ctx.hand.hcp
    return hcp >= threshold['hcp'] and ctx.hand_quality['kr_delta'] >= threshold['kr_delta']


def game_only_texas(ctx, suit):
    if not has_texas_game(ctx, suit) or ctx.hand.length(suit) != 6:
        return False
    side_lengths = sorted(ctx.hand.length(other) for other in 'SHDC' if other != suit)
    if side_lengths == [2, 2, 3]:
        supported = True
    elif side_lengths == [1, 3, 3]:
        singleton = [other for other in 'SHDC' if other != suit and ctx.hand.length(other) == 1][0]
        supported = ctx.hand.holding(singleton) in 'T98765432'
    else:
        supported = False
    return supported and not six_card_slam_interest(ctx, suit) and not slam_keycard_texas(ctx, suit)


def seven_card_texas(ctx, suit):
    return (ctx.hand is not None and ctx.hand.length(suit) >= 7
            and has_texas_game(ctx, suit) and ctx.hand.hcp <= 10)


def slam_keycard_texas(ctx, suit):
    """The six-card 6322 hand already committed to slam if keycards permit."""
    return (has_texas_game(ctx, suit) and ctx.hand.length(suit) == 6
            and ctx.hand.hcp >= 17
            and sorted(ctx.hand.length(other) for other in 'SHDC' if other != suit) == [2, 2, 3])


def shapely_game_texas(ctx, suit):
    points = named_evaluator(ctx, 'shapely_second_minor_strength_' + suit)
    return (points is not None and 4 <= points <= 6
            and has_texas_game(ctx, suit))


def texas_hearts(ctx):
    return (game_only_texas(ctx, 'H') or shapely_game_texas(ctx, 'H')
            or slam_keycard_texas(ctx, 'H') or seven_card_texas(ctx, 'H'))


def texas_spades(ctx):
    return (game_only_texas(ctx, 'S') or shapely_game_texas(ctx, 'S')
            or slam_keycard_texas(ctx, 'S') or seven_card_texas(ctx, 'S'))


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
            call.meaning.strength_evidence = {'model': 'kaplan_rubens', 'partner_min': 15}
            call.meaning.public_evidence = {
                'evaluator': 'texas_' + suit + '_public', 'equals': True,
                'bounds': {'min_lengths': {suit: 6}},
            }
            call.effect('agreed_suit').suit = suit
            call.description = ('South African Texas transfer with a six-card major, '
                                'K-R game strength, and a privately fixed game-only purpose.')

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
