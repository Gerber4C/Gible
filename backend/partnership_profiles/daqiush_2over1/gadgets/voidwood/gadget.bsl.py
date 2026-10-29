# Voidwood (void-showing keycard) ask after 1NT major transfers.
#
# Design-document definition (docs/15_daqiush_slam.md):
# - initiated by a jump to 4S or higher in a new suit with a trump agreed;
# - the bid suit is the void, so its ace is not a keycard;
# - five-step answers: 0/3, 1/4 without trump Q, 1/4 with trump Q,
#   2 without trump Q, 2 with trump Q;
# - after 0/3, +1 asks the trump Q and (while below 5NT) +2 asks kings;
# - after a 1/4 answer below 5NT, +1 asks kings;
# - when asking kings the ace of the void suit counts as that suit's king;
# - a king answer may not pass six of the trump;
# - if the first answer is 5NT or higher, every continuation by the asker is
#   a grand-slam invitation, and skipping a suit denies needing that king.
#
# The 1NT-transfer routes specified by the owner are:
#   1NT-2H-2S: 5C / 5D / 5H show a void in C / D / H (spades trump)
#   1NT-2D-2H: 4S / 5C / 5D show a void in S / C / D (hearts trump)
# Opponents have passed, so the "opponents showed joint strength" variant
# (void slam invite, not keycard) does not arise here.

CALL_ORDER = ('4C', '4D', '4H', '4S', '4NT', '5C', '5D', '5H', '5S',
              '5NT', '6C', '6D', '6H', '6S', '6NT', '7C', '7D', '7H', '7S', '7NT')

MINIMUM_ASK_KR = 17.0

# ask bid, trump, void suit, five answer bids (0/3, 1/4 no Q, 1/4 Q, 2 no Q, 2 Q)
VOIDWOOD_ASKS = (
    ('5C', 'S', 'C', ('5D', '5H', '5S', '5NT', '6C')),
    ('5D', 'S', 'D', ('5H', '5S', '5NT', '6C', '6D')),
    ('5H', 'S', 'H', ('5S', '5NT', '6C', '6D', '6H')),
    ('4S', 'H', 'S', ('4NT', '5C', '5D', '5H', '5S')),
    ('5C', 'H', 'C', ('5D', '5H', '5S', '5NT', '6C')),
    ('5D', 'H', 'D', ('5H', '5S', '5NT', '6C', '6D')),
)

STEPS = (
    ((0, 3), None),
    ((1, 4), False),
    ((1, 4), True),
    ((2,), False),
    ((2,), True),
)


def step_bid(anchor, steps):
    index = CALL_ORDER.index(anchor)
    target = index + steps
    if target < 0 or target >= len(CALL_ORDER):
        return None
    return CALL_ORDER[target]


def below_five_notrump(bid):
    return CALL_ORDER.index(bid) < CALL_ORDER.index('5NT')


def voidwood_ask_eligible(ctx, trump, void):
    return (ctx.hand is not None and ctx.hand.length(trump) >= 5
            and ctx.hand.length(void) == 0
            and state_exists(ctx, 'agreed_suit', suit=trump)
            and ctx.hand_quality['kr_points'] >= MINIMUM_ASK_KR)


def voidwood_answer(ctx, trump, void, counts, queen):
    if ctx.hand is None:
        return False
    if not ctx.state.exists('keycard_context', trump_suit=trump,
                            excluded_suit=void, status='pending'):
        return False
    if any(ctx.hand.length(suit) == 0 for suit in 'SHDC'):
        # A void in another suit would need its own exclusion treatment.
        return False
    count = ctx.hand.keycard_count(trump, excluded_suit=void)
    if count not in counts:
        return False
    return queen is None or ctx.hand.contains_rank(trump, 'Q') == queen


def queen_answer(ctx, trump, with_queen):
    if ctx.hand is None:
        return False
    if not ctx.state.exists('keycard_context', trump_suit=trump, status='pending'):
        return False
    return ctx.hand.contains_rank(trump, 'Q') == with_queen


def king_in(ctx, suit, void):
    """The suit's king, or the void suit's ace counted as its king."""
    if ctx.hand is None:
        return False
    if suit == void:
        return ctx.hand.contains_rank(suit, 'A')
    return ctx.hand.contains_rank(suit, 'K')


STATE_ASKS = ('4S', '5C', '5D', '5H', '5S', '6C', '6D', '6H', '6S')


def state_voidwood_ask(ctx, trump, void, ask):
    """The generic confirmed-trump Voidwood gate."""
    if ctx.hand is None or ctx.hand.length(void) != 0:
        return False
    if not state_exists(ctx, 'agreed_suit', suit=trump):
        return False
    if state_exists(ctx, 'keycard_context', status='pending'):
        return False
    if state_exists(ctx, 'voidwood', status='pending'):
        return False
    if voidwood_jump(ctx.auction, trump=trump, void=void) != ask:
        return False
    verdict = is_safe_voidwood_ask(
        ask, trump=trump,
        own_effective_keycards=effective_keycards(ctx.hand, trump, void))
    return verdict.safe


def state_voidwood_answer(ctx, ask, step):
    if ctx.hand is None:
        return False
    if not state_exists(ctx, 'voidwood', ask=ask, status='pending'):
        return False
    trump = state_attribute(ctx, 'voidwood', 'trump')
    void = state_attribute(ctx, 'voidwood', 'void')
    if trump not in 'CDHS' or void not in 'CDHS':
        return False
    counts, queen = STEPS[step]
    count = effective_keycards(ctx.hand, trump, void)
    if count not in counts:
        return False
    return queen is None or ctx.hand.contains_rank(trump, 'Q') == queen


class Voidwood(Gadget):
    id = 'voidwood'
    namespace = 'daqiush_2over1'
    name = 'Voidwood（缺门关键张）'
    author = Author('Daqiush')

    def build(self):
        for ask, trump, void, answer_map in VOIDWOOD_ASKS:
            transfer = '2H' if trump == 'S' else '2D'
            accept = '2S' if trump == 'S' else '2H'
            prefix = '1NP' + transfer + 'P' + accept + 'P'

            call = self.call('voidwood_' + trump.lower() + '_void_' + void.lower())
            call.when = prefix
            call.requires = StateExists('agreed_suit', suit=trump)
            call.bid = ask
            call.applies = (lambda ctx, t=trump, v=void: voidwood_ask_eligible(ctx, t, v))
            call.meaning.action = 'voidwood_ask'
            call.meaning.nature = ['artificial']
            call.meaning.acts = ['inquiry', 'keycard_asking', 'slam_try']
            call.meaning.target_suit = trump
            call.meaning.agreed_suit = trump
            call.meaning.void_suit = void
            call.effect('agreed_suit').suit = trump
            context = call.effect('keycard_context')
            context.trump_suit = trump
            context.excluded_suit = void
            context.ask_call = ask
            context.method = 'voidwood'
            context.status = 'pending'
            call.description = ('Voidwood: a ' + void + ' void, asking '
                                'keycards outside ' + void + ' with ' + trump + ' trump.')

            answer_prefix = prefix + ask + 'P'
            for index in range(len(STEPS)):
                counts, queen = STEPS[index]
                answer = self.call('voidwood_' + trump.lower() + '_void_' + void.lower()
                                   + '_answer_' + answer_map[index].lower())
                answer.when = answer_prefix
                answer.bid = answer_map[index]
                answer.applies = (lambda ctx, t=trump, v=void, c=counts, q=queen:
                                  voidwood_answer(ctx, t, v, c, q))
                answer.meaning.action = 'voidwood_answer'
                answer.meaning.nature = ['artificial']
                answer.meaning.acts = ['descriptive', 'keycard_answer']
                answer.meaning.target_suit = trump
                answer.meaning.agreed_suit = trump
                answer.meaning.keycard_counts = list(counts)
                if queen is not None:
                    answer.meaning.trump_queen = queen
                answer.description = ('Voidwood answer: ' + answer_map[index]
                                      + ' shows ' + str(counts) + ' keycards outside '
                                      + void + '.')

                if index == 0:
                    # 0 or 3: +1 asks the trump queen, +2 (below 5NT) asks kings.
                    queen_ask = step_bid(answer_map[index], 1)
                    if queen_ask is not None:
                        qcall = self.call('voidwood_' + trump.lower() + '_void_'
                                          + void.lower() + '_queen_ask_after_'
                                          + answer_map[index].lower())
                        qcall.when = answer_prefix + answer_map[index] + 'P'
                        qcall.bid = queen_ask
                        qcall.applies = lambda ctx: ctx.hand is not None
                        qcall.meaning.action = 'voidwood_queen_ask'
                        qcall.meaning.nature = ['artificial']
                        qcall.meaning.acts = ['inquiry']
                        qcall.meaning.target_suit = trump
                        qcall.description = 'Ask for the trump queen after 0/3 keycards.'

                        for offset, with_queen, label in ((1, False, 'no'),
                                                          (2, True, 'yes')):
                            qanswer_bid = step_bid(queen_ask, offset)
                            if qanswer_bid is None:
                                continue
                            qanswer = self.call('voidwood_' + trump.lower() + '_void_'
                                                + void.lower() + '_queen_answer_'
                                                + label + '_after_'
                                                + answer_map[index].lower())
                            qanswer.when = answer_prefix + answer_map[index] + 'P' \
                                + queen_ask + 'P'
                            qanswer.bid = qanswer_bid
                            qanswer.applies = (lambda ctx, t=trump, w=with_queen:
                                               queen_answer(ctx, t, w))
                            qanswer.meaning.action = 'voidwood_queen_answer'
                            qanswer.meaning.nature = ['artificial']
                            qanswer.meaning.acts = ['descriptive']
                            qanswer.meaning.trump_queen = with_queen
                            qanswer.description = 'Trump queen ' + label + '.'

                    king_ask = step_bid(answer_map[index], 2)
                    if king_ask is not None and below_five_notrump(king_ask):
                        kcall = self.call('voidwood_' + trump.lower() + '_void_'
                                          + void.lower() + '_king_ask_after_'
                                          + answer_map[index].lower())
                        kcall.when = answer_prefix + answer_map[index] + 'P'
                        kcall.bid = king_ask
                        kcall.applies = lambda ctx: ctx.hand is not None
                        kcall.meaning.action = 'voidwood_king_ask'
                        kcall.meaning.nature = ['artificial']
                        kcall.meaning.acts = ['inquiry']
                        kcall.meaning.target_suit = trump
                        kcall.description = ('Ask kings after 0/3 keycards; the void '
                                             'suit ace counts as its king.')

                if index == 1:
                    # 1 or 4 below 5NT: +1 asks kings.
                    if below_five_notrump(answer_map[index]):
                        king_ask = step_bid(answer_map[index], 1)
                        if king_ask is not None:
                            kcall = self.call('voidwood_' + trump.lower() + '_void_'
                                              + void.lower() + '_king_ask_after_'
                                              + answer_map[index].lower())
                            kcall.when = answer_prefix + answer_map[index] + 'P'
                            kcall.bid = king_ask
                            kcall.applies = lambda ctx: ctx.hand is not None
                            kcall.meaning.action = 'voidwood_king_ask'
                            kcall.meaning.nature = ['artificial']
                            kcall.meaning.acts = ['inquiry']
                            kcall.meaning.target_suit = trump
                            kcall.description = ('Ask kings after 1/4 keycards; the void '
                                                 'suit ace counts as its king.')

                if not below_five_notrump(answer_map[index]):
                    # Any continuation beyond a 5NT-or-higher answer is a
                    # grand-slam invitation; six of the trump declines.
                    for bid in ('6' + trump, '7' + trump):
                        grand = self.call('voidwood_' + trump.lower() + '_void_'
                                          + void.lower() + '_grand_after_'
                                          + answer_map[index].lower() + '_' + bid.lower())
                        grand.when = answer_prefix + answer_map[index] + 'P'
                        grand.bid = bid
                        grand.applies = lambda ctx: ctx.hand is not None
                        grand.meaning.action = ('grand_slam_invitation'
                                                if bid == '6' + trump
                                                else 'grand_slam_acceptance')
                        grand.meaning.nature = ['natural']
                        grand.meaning.acts = (['invite'] if bid == '6' + trump
                                              else ['accept', 'final_placement'])
                        grand.meaning.target_suit = trump
                        if bid == '7' + trump:
                            grand.meaning.purpose_completed = True

                    invite_prefix = answer_prefix + answer_map[index] + 'P' \
                        + '6' + trump + 'P'
                    decline = self.call('voidwood_' + trump.lower() + '_void_'
                                        + void.lower() + '_grand_decline_after_'
                                        + answer_map[index].lower())
                    decline.when = invite_prefix
                    decline.bid = 'P'
                    decline.applies = (lambda ctx, t=trump: ctx.hand is not None
                                       and not (ctx.hand.contains_rank(t, 'Q')
                                                and (ctx.hand.hcp >= 17
                                                     or ctx.hand_quality['kr_points'] >= 18)))
                    decline.meaning.action = 'grand_slam_decline'
                    decline.meaning.nature = ['natural']
                    decline.meaning.acts = ['signoff', 'final_placement']
                    decline.meaning.target_suit = trump
                    decline.meaning.purpose_completed = True

                    accept = self.call('voidwood_' + trump.lower() + '_void_'
                                       + void.lower() + '_grand_accept_after_'
                                       + answer_map[index].lower())
                    accept.when = invite_prefix
                    accept.bid = '7' + trump
                    accept.applies = (lambda ctx, t=trump: ctx.hand is not None
                                      and ctx.hand.contains_rank(t, 'Q')
                                      and (ctx.hand.hcp >= 17
                                           or ctx.hand_quality['kr_points'] >= 18))
                    accept.meaning.action = 'grand_slam_accept'
                    accept.meaning.nature = ['natural']
                    accept.meaning.acts = ['accept', 'final_placement']
                    accept.meaning.target_suit = trump
                    accept.meaning.purpose_completed = True

            # King answers: show the lowest king (or the void ace) at or below
            # six of the trump; six of the trump when nothing is showable.
            for index in range(len(STEPS)):
                counts, _ = STEPS[index]
                if counts not in ((0, 3), (1, 4)):
                    continue
                offset = 2 if counts == (0, 3) else 1
                king_ask = step_bid(answer_map[index], offset)
                if king_ask is None or not below_five_notrump(king_ask):
                    continue
                after_king = answer_prefix + answer_map[index] + 'P' + king_ask + 'P'
                shown = []
                for suit in 'CDHS':
                    if suit == trump:
                        continue
                    bid = '6' + suit
                    if CALL_ORDER.index(bid) > CALL_ORDER.index('6' + trump):
                        continue
                    show = self.call('voidwood_' + trump.lower() + '_void_'
                                     + void.lower() + '_king_show_' + suit.lower()
                                     + '_after_' + answer_map[index].lower())
                    show.when = after_king
                    show.bid = bid
                    show.applies = (lambda ctx, s=suit, v=void, prior=tuple(shown):
                                    king_in(ctx, s, v)
                                    and not any(king_in(ctx, x, v) for x in prior))
                    show.meaning.action = 'voidwood_king_show'
                    show.meaning.nature = ['artificial']
                    show.meaning.acts = ['descriptive']
                    show.meaning.control_suit = suit
                    show.meaning.target_suit = trump
                    show.description = ('Show the ' + suit + ' king; the void ace counts '
                                        'as that suit king.')
                    shown.append(suit)

                no_king = self.call('voidwood_' + trump.lower() + '_void_'
                                    + void.lower() + '_no_king_after_'
                                    + answer_map[index].lower())
                no_king.when = after_king
                no_king.bid = '6' + trump
                no_king.applies = (lambda ctx, t=trump, v=void: (
                    ctx.hand is not None
                    and not any(king_in(ctx, s, v) for s in 'CDHS'
                                if s != t
                                and CALL_ORDER.index('6' + s) <= CALL_ORDER.index('6' + t))))
                no_king.meaning.action = 'voidwood_no_king'
                no_king.meaning.nature = ['natural']
                no_king.meaning.acts = ['signoff', 'final_placement']
                no_king.meaning.target_suit = trump
                no_king.meaning.purpose_completed = True

        # State-driven Voidwood: any confirmed-trump auction may use the
        # one-level jump into a void suit. The legacy transfer blocks above
        # cover the 1NT-transfer regression routes; this layer covers the
        # confirmed diamond route 1NT-2H-2S-3D-3H and future fits.
        for trump in 'CDHS':
            for void in 'CDHS':
                if void == trump:
                    continue
                for ask in STATE_ASKS:
                    if ask[-1] != void:
                        continue
                    call = self.call('state_voidwood_' + trump.lower()
                                     + '_void_' + void.lower() + '_'
                                     + ask.lower())
                    call.when = '*'
                    call.requires = StateExists('agreed_suit', suit=trump)
                    call.bid = ask
                    call.applies = (lambda ctx, t=trump, v=void, a=ask:
                                    state_voidwood_ask(ctx, t, v, a))
                    call.meaning.action = 'voidwood_ask'
                    call.meaning.nature = ['artificial']
                    call.meaning.acts = ['inquiry', 'keycard_asking', 'slam_try']
                    call.meaning.target_suit = trump
                    call.meaning.agreed_suit = trump
                    call.meaning.void_suit = void
                    call.effect('agreed_suit').suit = trump
                    frame = call.effect('voidwood')
                    frame.trump = trump
                    frame.void = void
                    frame.ask = ask
                    frame.method = 'voidwood'
                    frame.status = 'pending'
                    call.description = ('Voidwood: confirmed ' + trump
                                        + ' trumps, a ' + void
                                        + ' void, and a safe answer set.')

                    answers = answer_bids(ask)
                    for step in range(len(STEPS)):
                        answer = self.call('state_voidwood_' + trump.lower()
                                           + '_void_' + void.lower() + '_'
                                           + ask.lower() + '_answer_'
                                           + answers[step].lower())
                        answer.when = '*'
                        answer.requires = StateExists('voidwood', ask=ask,
                                                      trump=trump, void=void,
                                                      status='pending')
                        answer.bid = answers[step]
                        answer.applies = (lambda ctx, a=ask, s=step:
                                          state_voidwood_answer(ctx, a, s))
                        counts, queen = STEPS[step]
                        answer.meaning.action = 'voidwood_answer'
                        answer.meaning.nature = ['artificial']
                        answer.meaning.acts = ['descriptive', 'keycard_answer']
                        answer.meaning.target_suit = trump
                        answer.meaning.agreed_suit = trump
                        answer.meaning.keycard_counts = list(counts)
                        if queen is not None:
                            answer.meaning.trump_queen = queen
                        answer.description = ('Voidwood answer ' + answers[step]
                                              + ' for the ' + void + ' void.')
