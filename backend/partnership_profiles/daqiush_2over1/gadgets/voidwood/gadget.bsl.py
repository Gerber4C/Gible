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
MINIMUM_VOIDWOOD_ASKER_LENGTH = 6
MINIMUM_EFFECTIVE_QUEEN_FIT = 9

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


def next_non_trump(anchor, trump):
    """The next call above the answer that is not the trump strain."""
    for candidate in CALL_ORDER[CALL_ORDER.index(anchor) + 1:]:
        if candidate[1] != trump:
            return candidate
    return None


def voidwood_ask_eligible(ctx, trump, void):
    return (ctx.hand is not None
            and ctx.hand.length(trump) >= MINIMUM_VOIDWOOD_ASKER_LENGTH
            and ctx.hand.length(void) == 0
            and state_exists(ctx, 'agreed_suit', suit=trump)
            and ctx.hand_quality['kr_points'] >= MINIMUM_ASK_KR)


def has_effective_trump_queen(ctx, trump):
    """An actual queen, or the public nine-card fit announced by Voidwood."""
    return (ctx.hand.contains_rank(trump, 'Q')
            or ctx.state.exists(
                'agreed_suit', suit=trump,
                asker_min_length=MINIMUM_VOIDWOOD_ASKER_LENGTH,
                min_total=MINIMUM_EFFECTIVE_QUEEN_FIT))


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
    return queen is None or has_effective_trump_queen(ctx, trump) == queen


def queen_answer(ctx, trump, with_queen):
    if ctx.hand is None:
        return False
    if not ctx.state.exists('keycard_context', trump_suit=trump, status='pending'):
        return False
    return has_effective_trump_queen(ctx, trump) == with_queen


def king_in(ctx, suit, void):
    """The suit's king, or the void suit's ace counted as its king."""
    if ctx.hand is None:
        return False
    if suit == void:
        return (ctx.hand.contains_rank(suit, 'A')
                or ctx.hand.contains_rank(suit, 'K'))
    return ctx.hand.contains_rank(suit, 'K')


STATE_ASKS = ('4S', '5C', '5D', '5H', '5S', '6C', '6D', '6H', '6S')


def public_voidwood_requires(ctx, trump):
    """Public gate for a Voidwood ask.

    A pending ordinary keycard frame means the same bid belongs to the
    ordinary-RKCB answer set; Voidwood must not compete for it in replay.
    The trump may be already agreed or inferred from the last natural suit
    when the partnership has not agreed one yet.
    """
    if ctx.state.exists('keycard_context', method='rkcb_1430'):
        return False
    current = current_voidwood_trump(ctx.trace, ctx.auction.actor_to_call)
    if current is not None:
        return current == trump
    inferred = inferred_voidwood_trump(ctx.auction, ctx.trace)
    return inferred is not None and inferred[0] == trump


def state_voidwood_ask(ctx, trump, void, ask):
    """The generic confirmed- or inferred-trump Voidwood gate."""
    if (ctx.hand is None
            or ctx.hand.length(trump) < MINIMUM_VOIDWOOD_ASKER_LENGTH
            or ctx.hand.length(void) != 0):
        return False
    current = current_voidwood_trump(ctx.trace, ctx.auction.actor_to_call)
    if current is not None:
        if current != trump:
            return False
    else:
        inferred = inferred_voidwood_trump(ctx.auction, ctx.trace)
        if inferred is None or inferred[0] != trump:
            return False
        if ctx.hand.length(trump) + inferred[1] < 8:
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
    return queen is None or has_effective_trump_queen(ctx, trump) == queen


def last_non_pass(auction):
    index = len(auction.calls) - 1
    while index >= 0:
        call = auction.calls[index]
        if call not in ('P', 'X', 'R'):
            return call
        index -= 1
    return None


def canonical_bid(bid):
    return bid + 'T' if bid.endswith('N') and not bid.endswith('NT') else bid


def engine_bid(bid):
    return bid[:-1] if bid.endswith('NT') else bid


def asker_seat(auction, ask):
    index = len(auction.calls) - 1
    while index >= 0:
        if auction.calls[index] == ask:
            return auction.actor_at(index)
        index -= 1
    return None


def partner_seat(seat):
    return {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[seat]


def queen_ask_bid(ask, trump):
    answers = answer_bids(ask)
    if len(answers) != 5:
        return None
    q = step_bid(canonical_bid(answers[0]), 1)
    if q == '5' + trump:
        q = step_bid(q, 1)
    return q


def queen_ask_applies(ctx, ask, trump):
    asker = asker_seat(ctx.auction, ask)
    if asker is None or ctx.auction.actor_to_call != asker:
        return False
    if last_non_pass(ctx.auction) != answer_bids(ask)[0]:
        return False
    q = queen_ask_bid(ask, trump)
    if q is None:
        return False
    if CALL_ORDER.index(q) >= CALL_ORDER.index('5' + trump):
        asker_zar = zar_total(ctx.hand, trump, ctx.hand.length(trump) + 5)
        return asker_zar + 31 >= 67
    return True


def lowest_side_suit(ctx, trump, q):
    for suit in 'CDHS':
        if suit == trump:
            continue
        bid = '6' + suit
        if CALL_ORDER.index(bid) > CALL_ORDER.index(q):
            return bid
    return None


def queen_expected_bid(ctx, ask, trump, void, high_zar=31):
    asker = asker_seat(ctx.auction, ask)
    if asker is None or ctx.auction.actor_to_call != partner_seat(asker):
        return None
    q = queen_ask_bid(ask, trump)
    if q is None or last_non_pass(ctx.auction) != engine_bid(q):
        return None
    has_queen = ctx.hand.contains_rank(trump, 'Q')
    zar = zar_total(ctx.hand, trump, 5 + ctx.hand.length(trump))
    high = zar >= high_zar
    kings = [suit for suit in 'CDHS'
             if suit != trump and king_in(ctx, suit, void)
             and CALL_ORDER.index('6' + suit) <= CALL_ORDER.index('6' + trump)]
    five_trump = CALL_ORDER.index('5' + trump)
    five_nt = CALL_ORDER.index('5NT')
    q_rank = CALL_ORDER.index(q)
    if not has_queen:
        if q_rank < five_trump:
            return '5' + trump
        return '6' + trump
    if kings:
        if q_rank >= five_trump and high:
            return '7' + trump
        return '6' + kings[0]
    if q_rank < five_trump:
        return '6' + trump if not high else '5NT'
    if q_rank < five_nt:
        return '5NT'
    return lowest_side_suit(ctx, trump, q)


def grand_invite_applies(ctx, ask, trump):
    asker = asker_seat(ctx.auction, ask)
    if asker is None or ctx.auction.actor_to_call != asker:
        return False
    if not state_exists(ctx, 'voidwood', ask=ask, status='pending'):
        return False
    q = queen_ask_bid(ask, trump)
    if q is None or last_non_pass(ctx.auction) != engine_bid(q):
        return False
    asker_zar = zar_total(ctx.hand, trump, ctx.hand.length(trump) + 5)
    return asker_zar + 31 >= 67


def grand_accept_applies(ctx, trump, void, ask):
    asker = asker_seat(ctx.auction, ask)
    if asker is None or ctx.auction.actor_to_call != partner_seat(asker):
        return False
    if not state_exists(ctx, 'voidwood', ask=ask, status='pending'):
        return False
    zar = zar_total(ctx.hand, trump, 5 + ctx.hand.length(trump))
    has_king = any(king_in(ctx, suit, void) for suit in 'CDHS'
                   if suit != trump)
    return (ctx.hand.contains_rank(trump, 'Q') and zar >= 31 and has_king)


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
            call.requires = lambda ctx, t=trump: public_voidwood_requires(ctx, t)
            call.bid = ask
            call.applies = (lambda ctx, t=trump, v=void: voidwood_ask_eligible(ctx, t, v))
            call.meaning.action = 'voidwood_ask'
            call.meaning.nature = ['artificial']
            call.meaning.acts = ['inquiry', 'keycard_asking', 'slam_try']
            call.meaning.target_suit = trump
            call.meaning.agreed_suit = trump
            call.meaning.void_suit = void
            agreement = call.effect('agreed_suit')
            agreement.suit = trump
            agreement.asker_min_length = MINIMUM_VOIDWOOD_ASKER_LENGTH
            agreement.min_total = MINIMUM_EFFECTIVE_QUEEN_FIT
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
                    answer.meaning.trump_queen_basis = 'actual_or_nine_card_fit'
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

                if index in (3, 4) and below_five_notrump(answer_map[index]):
                    # Two-keycard continuations: the next non-trump call asks
                    # kings; the asker may instead place 6/7 directly.
                    k_bid = next_non_trump(answer_map[index], trump)
                    kcall = self.call('voidwood_' + trump.lower() + '_void_'
                                      + void.lower() + '_king_ask_after_'
                                      + answer_map[index].lower())
                    kcall.when = answer_prefix + answer_map[index] + 'P'
                    kcall.bid = k_bid
                    kcall.applies = (lambda ctx, t=trump, v=void,
                                     qa=STEPS[index][1]: (
                        ctx.hand is not None
                        and ctx.hand.keycard_count(t, excluded_suit=v) + 2 == 4
                        and (ctx.hand.contains_rank(t, 'Q') or qa is True)))
                    kcall.priority = 1
                    kcall.meaning.action = 'voidwood_king_ask'
                    kcall.meaning.nature = ['artificial']
                    kcall.meaning.acts = ['inquiry']
                    kcall.meaning.target_suit = trump
                    kcall.description = ('The next non-trump call asks kings while '
                                         'the asker is still deciding between six '
                                         'and seven.')
                    for final_bid, grand in (('6' + trump, False),
                                             ('7' + trump, True)):
                        final = self.call('voidwood_' + trump.lower() + '_void_'
                                          + void.lower() + '_direct_'
                                          + final_bid.lower() + '_after_'
                                          + answer_map[index].lower())
                        final.when = answer_prefix + answer_map[index] + 'P'
                        final.bid = final_bid
                        final.applies = (lambda ctx, t=trump, v=void,
                                         g=grand, qa=STEPS[index][1]: (
                            ctx.hand is not None
                            and ((ctx.hand.keycard_count(t, excluded_suit=v) + 2 == 3)
                                 if not g else
                                 (ctx.hand.keycard_count(t, excluded_suit=v) + 2 == 4
                                  and (ctx.hand.contains_rank(t, 'Q') or qa is True)))))
                        final.priority = 2 if grand else 1
                        final.meaning.action = ('voidwood_grand_acceptance'
                                                if grand else 'voidwood_slam')
                        final.meaning.nature = ['natural']
                        final.meaning.acts = ['signoff', 'final_placement']
                        final.meaning.target_suit = trump
                        final.meaning.purpose_completed = True
                        final.description = ('No king ask needed: place the '
                                             + ('grand' if grand else 'small')
                                             + ' slam directly.')

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
                if index in (3, 4):
                    king_ask = next_non_trump(answer_map[index], trump)
                elif counts in ((0, 3), (1, 4)):
                    offset = 2 if counts == (0, 3) else 1
                    king_ask = step_bid(answer_map[index], offset)
                else:
                    continue
                if king_ask is None or not below_five_notrump(king_ask):
                    # 5NT itself can be the king ask after a two-keycard answer.
                    if not (index in (3, 4) and king_ask == '5NT'):
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

                if king_ask != '5NT' and CALL_ORDER.index('5NT') > CALL_ORDER.index(king_ask):
                    beyond = [suit for suit in 'CDHS'
                              if suit != trump
                              and CALL_ORDER.index('6' + suit)
                              > CALL_ORDER.index('6' + trump)]
                    if beyond:
                        show5 = self.call('voidwood_' + trump.lower() + '_void_'
                                          + void.lower() + '_king_show_5nt_after_'
                                          + answer_map[index].lower())
                        show5.when = after_king
                        show5.bid = '5NT'
                        show5.applies = (lambda ctx, t=trump, v=void,
                                         suits=tuple(beyond): (
                            any(king_in(ctx, s, v) for s in suits)
                            and not any(king_in(ctx, s, v) for s in 'CDHS'
                                        if s != t and s not in suits
                                        and CALL_ORDER.index('6' + s)
                                        <= CALL_ORDER.index('6' + t))))
                        show5.meaning.action = 'voidwood_king_show'
                        show5.meaning.nature = ['artificial']
                        show5.meaning.acts = ['descriptive']
                        show5.meaning.control_suit = 'S'
                        show5.meaning.target_suit = trump
                        show5.description = ('Five notrump shows a king in a suit '
                                             'whose six-level bid lies beyond six '
                                             'of trumps.')

                no_king = self.call('voidwood_' + trump.lower() + '_void_'
                                    + void.lower() + '_no_king_after_'
                                    + answer_map[index].lower())
                no_king.when = after_king
                no_king.bid = '6' + trump
                no_king.applies = (lambda ctx, t=trump, v=void: (
                    ctx.hand is not None
                    and not any(king_in(ctx, s, v) for s in 'CDHS'
                                if s != t)))
                no_king.meaning.action = 'voidwood_no_king'
                no_king.meaning.nature = ['natural']
                no_king.meaning.acts = ['signoff', 'final_placement']
                no_king.meaning.target_suit = trump
                no_king.meaning.purpose_completed = True

                # After any six-level (or 5NT) king show, the asker accepts
                # with seven of trumps or rejects with six.
                accept7 = self.call('voidwood_' + trump.lower() + '_void_'
                                    + void.lower() + '_accept_seven_after_'
                                    + answer_map[index].lower())
                accept7.when = after_king
                accept7.bid = '7' + trump
                accept7.applies = (lambda ctx, a=ask, t=trump, v=void:
                                   grand_accept_applies(ctx, t, v, a))
                accept7.meaning.action = 'voidwood_grand_acceptance'
                accept7.meaning.nature = ['natural']
                accept7.meaning.acts = ['accept', 'final_placement']
                accept7.meaning.target_suit = trump
                accept7.meaning.purpose_completed = True
                accept7.description = ('The king ask itself is enough to '
                                       'accept the grand slam.')

                show_bids = ['5NT'] + ['6' + s for s in 'CDHS'
                                       if s != trump
                                       and CALL_ORDER.index('6' + s)
                                       <= CALL_ORDER.index('6' + trump)]
                for show_bid in show_bids:
                    if CALL_ORDER.index(show_bid) <= CALL_ORDER.index(king_ask):
                        continue
                    for final_bid, grand in (('6' + trump, False),
                                             ('7' + trump, True)):
                        finish = self.call('voidwood_' + trump.lower() + '_void_'
                                           + void.lower() + '_after_king_'
                                           + answer_map[index].lower() + '_'
                                           + show_bid.lower() + '_'
                                           + final_bid.lower())
                        finish.when = after_king + show_bid + 'P'
                        finish.bid = final_bid
                        finish.applies = (lambda ctx, t=trump, v=void,
                                         g=grand, qa=STEPS[index][1]: (
                            ctx.hand is not None
                            and ((ctx.hand.keycard_count(t, excluded_suit=v) + 2 == 3)
                                 if not g else
                                 (ctx.hand.keycard_count(t, excluded_suit=v) + 2 == 4
                                  and (ctx.hand.contains_rank(t, 'Q') or qa is True)))))
                        finish.meaning.action = ('voidwood_grand_acceptance'
                                                 if grand else 'voidwood_slam')
                        finish.meaning.nature = ['natural']
                        finish.meaning.acts = ['signoff', 'final_placement']
                        finish.meaning.target_suit = trump
                        finish.meaning.purpose_completed = True
                        finish.description = ('After the king show, '
                                              + ('accept the grand' if grand
                                                 else 'reject with the small slam')
                                              + '.')

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
                    call.requires = lambda ctx, t=trump: public_voidwood_requires(ctx, t)
                    call.bid = ask
                    call.applies = (lambda ctx, t=trump, v=void, a=ask:
                                    state_voidwood_ask(ctx, t, v, a))
                    call.meaning.action = 'voidwood_ask'
                    call.meaning.nature = ['artificial']
                    call.meaning.acts = ['inquiry', 'keycard_asking', 'slam_try']
                    call.meaning.target_suit = trump
                    call.meaning.agreed_suit = trump
                    call.meaning.void_suit = void
                    agreement = call.effect('agreed_suit')
                    agreement.suit = trump
                    agreement.asker_min_length = MINIMUM_VOIDWOOD_ASKER_LENGTH
                    agreement.min_total = MINIMUM_EFFECTIVE_QUEEN_FIT
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
                            answer.meaning.trump_queen_basis = 'actual_or_nine_card_fit'
                        answer.description = ('Voidwood answer ' + answers[step]
                                              + ' for the ' + void + ' void.')
                    q = queen_ask_bid(ask, trump)
                    if q is not None:
                        qcall = self.call('state_voidwood_' + trump.lower()
                                          + '_void_' + void.lower() + '_'
                                          + ask.lower() + '_queen_ask')
                        qcall.when = '*'
                        qcall.requires = StateExists('voidwood', ask=ask,
                                                    trump=trump, void=void,
                                                    status='pending')
                        qcall.bid = q
                        qcall.applies = (lambda ctx, a=ask, t=trump:
                                         queen_ask_applies(ctx, a, t))
                        qcall.meaning.action = 'voidwood_queen_ask'
                        qcall.meaning.nature = ['artificial']
                        qcall.meaning.acts = ['inquiry']
                        qcall.meaning.target_suit = trump
                        qcall.description = 'Ask for the trump queen after 0/3.'

                        for q_bid in ('5NT', '6C', '6D', '6H', '6S', '6NT',
                                      '7C', '7D', '7H', '7S', '7NT'):
                            if CALL_ORDER.index(q_bid) <= CALL_ORDER.index(q):
                                continue
                            qans = self.call('state_voidwood_' + trump.lower()
                                             + '_void_' + void.lower() + '_'
                                             + ask.lower() + '_queen_answer_'
                                             + q_bid.lower())
                            qans.when = '*'
                            qans.requires = StateExists('voidwood', ask=ask,
                                                        trump=trump, void=void,
                                                        status='pending')
                            qans.bid = q_bid
                            qans.applies = (lambda ctx, a=ask, t=trump, v=void,
                                            b=q_bid:
                                            queen_expected_bid(ctx, a, t, v) == b)
                            qans.meaning.action = 'voidwood_queen_answer'
                            qans.meaning.nature = ['artificial']
                            qans.meaning.acts = ['descriptive']
                            qans.meaning.target_suit = trump
                            qans.description = 'Answer the trump-queen ask.'

                        invite = self.call('state_voidwood_' + trump.lower()
                                           + '_void_' + void.lower() + '_'
                                           + ask.lower() + '_grand_invite')
                        invite.when = '*'
                        invite.requires = StateExists('voidwood', ask=ask,
                                                      trump=trump, void=void,
                                                      status='pending')
                        invite.bid = '6' + trump
                        invite.applies = (lambda ctx, a=ask, t=trump:
                                          grand_invite_applies(ctx, a, t))
                        invite.meaning.action = 'voidwood_grand_invitation'
                        invite.meaning.nature = ['natural']
                        invite.meaning.acts = ['invite']
                        invite.meaning.target_suit = trump
                        invite.description = 'Invite the grand slam after the queen answer.'

                        for g_bid in ('P', '7' + trump):
                            gans = self.call('state_voidwood_' + trump.lower()
                                             + '_void_' + void.lower() + '_'
                                             + ask.lower() + '_grand_'
                                             + g_bid.lower())
                            gans.when = '*'
                            gans.requires = StateExists('voidwood', ask=ask,
                                                        trump=trump, void=void,
                                                        status='pending')
                            gans.bid = g_bid
                            if g_bid == 'P':
                                gans.applies = (lambda ctx, t=trump:
                                                last_non_pass(ctx.auction)
                                                == '6' + t)
                            else:
                                gans.applies = (lambda ctx, t=trump, v=void:
                                                last_non_pass(ctx.auction)
                                                == '6' + t
                                                and grand_accept_applies(ctx, t, v, ask))
                            gans.meaning.action = 'voidwood_grand_' + (
                                'accept' if g_bid != 'P' else 'decline')
                            gans.meaning.nature = ['natural']
                            gans.meaning.acts = ['accept' if g_bid != 'P' else 'signoff',
                                                 'final_placement']
                            gans.meaning.target_suit = trump
                            gans.meaning.purpose_completed = True
