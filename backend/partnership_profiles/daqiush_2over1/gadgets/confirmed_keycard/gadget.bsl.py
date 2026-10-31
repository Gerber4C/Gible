# Basic uncontested Roman keycard 1430 answers. Special void answers and
# post-answer signoffs remain unimplemented, so those branches still block.


def route_intent_not_yet_selected(ctx):
    return False


def current_ordinary_frame(ctx, trump):
    frame = ordinary_rkcb_frame(ctx.trace)
    if frame is None or frame.trump != trump:
        return None
    return frame


def ordinary_queen_ask_requires(ctx, trump, category, bid):
    frame = current_ordinary_frame(ctx, trump)
    return (frame is not None and frame.status == 'answered'
            and frame.answer_category == category
            and frame.continuation_stage is None
            and ordinary_queen_ask_call(ctx.auction, frame) == bid)


def ordinary_relay_requires(ctx, trump):
    frame = current_ordinary_frame(ctx, trump)
    return (frame is not None and frame.status == 'answered'
            and frame.continuation_stage is None
            and ordinary_five_spade_role(ctx.auction, frame) == 'relay')


def ordinary_relay_pending(ctx):
    frame = ordinary_rkcb_frame(ctx.trace)
    return frame is not None and frame.status == 'relay_pending'


def ordinary_relay_completed(ctx):
    frame = ordinary_rkcb_frame(ctx.trace)
    return frame is not None and frame.status == 'relay_completed'


def ordinary_relay_completed_for(ctx, trump, status):
    frame = current_ordinary_frame(ctx, trump)
    return frame is not None and frame.status == status


def last_non_pass_seat(auction):
    for index in range(len(auction.calls) - 1, -1, -1):
        if auction.calls[index] not in ('P', 'X', 'R'):
            return auction.actor_at(index)
    return None


def partner_of(seat):
    return {'n': 's', 's': 'n', 'e': 'w', 'w': 'e'}[seat]


def partner_of_last_bidder(ctx):
    last = last_non_pass_seat(ctx.auction)
    return last is not None and ctx.auction.actor_to_call == partner_of(last)


def ordinary_relay_pending_for_actor(ctx, trump):
    return (ordinary_relay_completed_for(ctx, trump, 'relay_pending')
            and partner_of_last_bidder(ctx))


def ordinary_relay_completion_for_actor(ctx, trump):
    return (ordinary_relay_completed_for(ctx, trump, 'relay_completed')
            and partner_of_last_bidder(ctx))


def current_bidder_is_partner(ctx):
    seat = ordinary_partner_of_last_bidder(ctx.auction)
    return seat is not None and ctx.auction.actor_to_call == seat


def ordinary_high_answer_for_actor(ctx, trump):
    frame = current_ordinary_frame(ctx, trump)
    return (frame is not None and frame.status == 'answered'
            and frame.continuation_stage is None
            and ordinary_is_high_answer(frame)
            and current_bidder_is_partner(ctx))


def ordinary_grand_invite_actor(ctx, trump, answer_bid, invitation):
    frame = current_ordinary_frame(ctx, trump)
    return (frame is not None and frame.status == 'answered'
            and frame.continuation_stage is None
            and frame.answer_call == answer_bid
            and ordinary_is_high_answer(frame)
            and current_bidder_is_partner(ctx))


def ordinary_grand_responder(ctx, trump):
    frame = current_ordinary_frame(ctx, trump)
    return (frame is not None
            and frame.continuation_stage == 'grand_invitation'
            and current_bidder_is_partner(ctx))


def ordinary_counterinvite_asker(ctx, trump):
    frame = current_ordinary_frame(ctx, trump)
    return (frame is not None
            and frame.continuation_stage == 'counterinvited'
            and current_bidder_is_partner(ctx))


def carry_answer_state(record, trump):
    query = {'method': 'rkcb_1430', 'trump_suit': trump}
    record.answer_category = StateAttribute('keycard_context', 'answer_category', **query)
    record.answer_call = StateAttribute('keycard_context', 'answer_call', **query)
    record.keycard_counts = StateAttribute('keycard_context', 'keycard_counts', **query)
    record.trump_queen = StateAttribute('keycard_context', 'trump_queen', **query)
    record.useful_void = StateAttribute('keycard_context', 'useful_void', **query)
    record.useful_void_category = StateAttribute(
        'keycard_context', 'useful_void_category', **query)
    record.not_required_kings = StateAttribute(
        'keycard_context', 'not_required_kings', **query)


def ordinary_keycard_answer(ctx, trump, counts, queen):
    if ctx.hand is None or not ctx.state.exists('keycard_context', trump_suit=trump, status='pending'):
        return False
    if any(ctx.hand.length(suit) == 0 for suit in 'SHDC'):
        return False
    count = ctx.hand.keycard_count(trump)
    if count not in counts:
        return False
    return queen is None or ctx.hand.contains_rank(trump, 'Q') == queen


class ConfirmedKeycard(Gadget):
    id = 'confirmed_keycard'
    namespace = 'daqiush_2over1'
    name = 'Confirmed ordinary RKCB 1430 prefix'
    author = Author('Daqiush')

    def build(self):
        asks = [('diamond_fit', '1NP2DP2HP3DP3SP4HP4NP', 'D')]
        asks.append(('two_major_spade_slam',
                     '1NP2HP2SP3HP3SP4NP', 'S'))
        for answer in ('2H', '2S'):
            trump = answer[-1]
            ask = self.call('stayman_' + answer.lower() + '_no_shortage_keycard_ask')
            ask.when = '1NP2CP' + answer + 'P4DP'
            ask.bid = '4NT'
            ask.applies = lambda ctx: ctx.hand is not None
            ask.meaning.action = 'rkcb_1430'
            ask.meaning.nature = ['artificial']
            ask.meaning.acts = ['inquiry', 'keycard_asking']
            ask.meaning.target_suit = trump
            ask.meaning.agreed_suit = trump
            context = ask.effect('keycard_context')
            context.trump_suit = trump
            context.ask_call = '4N'
            context.method = 'rkcb_1430'
            context.status = 'pending'
            ask.description = 'Accept the no-shortage major slam try and ask agreed-major keycards.'
            asks.append(('stayman_' + trump + '_no_shortage',
                         '1NP2CP' + answer + 'P4DP4NP', trump))
            asks.append(('stayman_' + trump + '_no_shortage_after_refusal',
                         '1NP2CP' + answer + 'P4DP4' + answer[-1]
                         + 'P4NP', trump))
            shortage_probe = '3S' if trump == 'H' else '3H'
            for shortage_answer in ('4C', '4D', '4H'):
                asks.append(('stayman_' + trump + '_shortage_' + shortage_answer,
                             '1NP2CP' + answer + 'P' + shortage_probe
                             + 'P3NTP' + shortage_answer + 'P4NP', trump))
        for transfer, trump, answers in (
            ('4C', 'H', ('4D', '4H')),
            ('4D', 'S', ('4H', '4S')),
        ):
            for answer in answers:
                texas = self.call('texas_' + trump.lower() + '_after_' + answer.lower() + '_keycard_ask')
                texas.when = '1NP' + transfer + 'P' + answer + 'P'
                texas.bid = '4NT'
                texas.applies = (lambda ctx, t=trump: (
                    named_evaluator(ctx, 'texas_slam_keycard_' + t)
                    or named_evaluator(ctx, 'six_card_slam_interest_' + t)))
                texas.meaning.action = 'rkcb_1430'
                texas.meaning.nature = ['artificial']
                texas.meaning.acts = ['inquiry', 'keycard_asking']
                texas.meaning.target_suit = trump
                texas.meaning.agreed_suit = trump
                context = texas.effect('keycard_context')
                context.trump_suit = trump
                context.ask_call = '4N'
                context.method = 'rkcb_1430'
                context.status = 'pending'
                texas.description = 'The committed South African Texas slam route asks major keycards.'
                asks.append(('texas_' + trump + '_' + answer,
                             '1NP' + transfer + 'P' + answer + 'P4NP', trump))
        for transfer, trump, superaccepts in (
            ('2D', 'H', ('2S', '2N', '3C', '3H')),
            ('2H', 'S', ('2N', '3C', '3D', '3S')),
        ):
            retransfer = '3D' if trump == 'H' else '3H'
            for answer in superaccepts:
                prefix = '1NP' + transfer + 'P' + answer + 'P4NP'
                asks.append(('jacoby_' + trump + '_' + answer, prefix, trump))
                retransfer_prefix = ('1NP' + transfer + 'P' + answer + 'P'
                                     + retransfer + 'P3' + trump + 'P4NP')
                asks.append(('jacoby_' + trump + '_' + answer
                             + '_retransfer', retransfer_prefix, trump))
        for transfer, accept, trump in (('2D', '2H', 'H'), ('2H', '2S', 'S')):
            # Six-plus-card slam interest after the ordinary acceptance.
            for minor in 'CD':
                table = '1NP' + transfer + 'P' + accept + 'P3' + minor + 'P3NTP'
                # Six-four shape: the cue agrees the major, then keycard.
                for cue in [suit for suit in 'CDHS' if suit not in (trump, minor)]:
                    asks.append(('jacoby_' + trump + '_' + minor + '_six_four_'
                                 + cue, table + '4' + cue + 'P4NP', trump))
                # Two-suiter: opener cues and responder asks in the minor.
                for cue in [suit for suit in 'CDHS'
                            if suit != minor and '4' + suit > '4' + minor]:
                    asks.append(('jacoby_' + trump + '_' + minor + '_two_suiter_'
                                 + cue, table + '4' + minor + 'P4' + cue + 'P4NP',
                                 minor))
        for transfer, accept, trump, splinters in (
            ('2D', '2H', 'H', ('3S', '4C', '4D')),
            ('2H', '2S', 'S', ('4C', '4D', '4H')),
        ):
            for splinter in splinters:
                prefix = '1NP' + transfer + 'P' + accept + 'P' + splinter + 'P4NP'
                asks.append(('splinter_' + trump + '_' + splinter, prefix, trump))

        steps = (
            ('5C', (1, 4), None, '1 or 4 keycards'),
            ('5D', (0, 3), None, '0 or 3 keycards'),
            ('5H', (2,), False, '2 keycards without trump queen'),
            ('5S', (2,), True, '2 keycards with trump queen'),
        )
        for trump in 'CDHS':
            for bid, counts, queen, category in (
                ('5C', (1, 4), None, '1/4'),
                ('5D', (0, 3), None, '0/3'),
                ('5H', (2,), False, '2/no_q'),
                ('5S', (2,), True, '2/q'),
                ('5N', (0, 2, 4), None, '0/2/4/void'),
                ('6C', (1, 3), None, '1/3/void'),
                ('6D', (1, 3), None, '1/3/void'),
                ('6H', (1, 3), None, '1/3/void'),
                ('6S', (1, 3), None, '1/3/void'),
            ):
                answer = self.call('ordinary_rkcb_' + trump.lower()
                                   + '_answer_' + bid.lower())
                answer.when = '*'
                answer.requires = lambda ctx, t=trump: (
                    ordinary_rkcb_pending(ctx, t))
                answer.bid = bid
                answer.applies = (lambda ctx, t=trump, b=bid: (
                    ordinary_rkcb_pending(ctx, t)
                    and ordinary_rkcb_response_call(ctx, t) == b))
                answer.meaning.action = 'rkcb_1430_answer'
                answer.meaning.nature = ['artificial']
                answer.meaning.acts = ['descriptive', 'keycard_answer']
                answer.meaning.contract_effect = 'none'
                answer.meaning.target_suit = trump
                answer.meaning.agreed_suit = trump
                answer.meaning.keycard_counts = list(counts)
                if queen is not None:
                    answer.meaning.trump_queen = queen
                if bid == '5N':
                    answer.meaning.useful_void_category = 'unspecified'
                elif bid[0] == '6':
                    if bid[-1] == trump:
                        answer.meaning.useful_void_category = 'higher_than_trump'
                    else:
                        answer.meaning.useful_void = bid[-1]
                        answer.meaning.useful_void_category = 'exact'
                answer.description = ('Ordinary RKCB answer ' + bid
                                      + ' from the public pending frame.')

                record = answer.effect('keycard_context')
                record.method = 'rkcb_1430'
                record.trump_suit = trump
                record.status = 'answered'
                record.answer_category = category
                record.answer_call = bid
                record.keycard_counts = list(counts)
                if queen is not None:
                    record.trump_queen = queen
                if bid == '5N':
                    record.useful_void_category = 'unspecified'
                elif bid[0] == '6':
                    if bid[-1] == trump:
                        record.useful_void_category = 'higher_than_trump'
                    else:
                        record.useful_void = bid[-1]
                        record.useful_void_category = 'exact'

        # Ordinary-RKCB continuations read the latest public frame. Queen asks
        # come first; the five-spade relay only exists where that bid is not
        # structurally the queen ask.
        queen_asks = {
            'C': {'1/4': '5D', '0/3': '5H'},
            'D': {'1/4': '5H', '0/3': '5H'},
            'H': {'1/4': '5D', '0/3': '5S'},
            'S': {'1/4': '5D', '0/3': '5H'},
        }
        for trump, categories in queen_asks.items():
            for category, bid in categories.items():
                qa = self.call('ordinary_rkcb_' + trump.lower()
                               + '_queen_ask_' + category.replace('/', '_')
                               + '_' + bid.lower())
                qa.when = '*'
                qa.requires = (lambda ctx, t=trump, c=category, b=bid:
                               ordinary_queen_ask_requires(ctx, t, c, b))
                qa.bid = bid
                qa.applies = (lambda ctx, t=trump, c=category, b=bid:
                              ordinary_queen_ask_requires(ctx, t, c, b))
                qa.meaning.action = 'rkcb_1430_queen_ask'
                qa.meaning.nature = ['artificial']
                qa.meaning.acts = ['inquiry']
                qa.meaning.target_suit = trump
                qa.meaning.agreed_suit = trump
                qa.description = 'Ask for the trump queen from the public 1430 answer.'
                record = qa.effect('keycard_context')
                record.method = 'rkcb_1430'
                record.trump_suit = trump
                record.status = 'answered'
                record.continuation_stage = 'queen_ask'
                carry_answer_state(record, trump)

            relay = self.call('ordinary_rkcb_' + trump.lower()
                              + '_five_spade_relay')
            relay.when = '*'
            relay.requires = (lambda ctx, t=trump:
                              ordinary_relay_requires(ctx, t))
            relay.bid = '5S'
            relay.applies = (lambda ctx, t=trump:
                             ordinary_relay_requires(ctx, t))
            relay.meaning.action = 'rkcb_1430_relay_to_five_notrump'
            relay.meaning.nature = ['artificial']
            relay.meaning.acts = ['relay']
            relay.meaning.target_suit = trump
            relay.meaning.agreed_suit = trump
            relay.description = ('Relay to five notrump when five of trumps is '
                                 'unavailable or for a king show.')
            record = relay.effect('keycard_context')
            record.method = 'rkcb_1430'
            record.trump_suit = trump
            record.status = 'relay_pending'
            record.continuation_stage = 'relay'
            carry_answer_state(record, trump)

            forced = self.call('ordinary_rkcb_' + trump.lower()
                               + '_forced_five_notrump')
            forced.when = '*'
            forced.requires = lambda ctx, t=trump: (
                ordinary_relay_pending_for_actor(ctx, t))
            forced.bid = '5NT'
            forced.applies = lambda ctx, t=trump: (
                ordinary_relay_pending_for_actor(ctx, t))
            forced.meaning.action = 'rkcb_1430_forced_relay_completion'
            forced.meaning.nature = ['artificial']
            forced.meaning.acts = ['relay']
            forced.meaning.target_suit = trump
            forced.description = 'Complete the forced five notrump relay.'
            record = forced.effect('keycard_context')
            record.method = 'rkcb_1430'
            record.trump_suit = trump
            record.status = 'relay_completed'
            record.continuation_stage = 'relay'
            carry_answer_state(record, trump)

            for bid, action, acts in (
                ('P', 'rkcb_1430_relay_pass', ['signoff', 'final_placement']),
                ('6' + trump, 'rkcb_1430_relay_small_slam',
                 ['signoff', 'final_placement']),
            ):
                finish = self.call('ordinary_rkcb_' + trump.lower()
                                   + '_relay_after_' + bid.lower())
                finish.when = '*'
                finish.requires = lambda ctx, t=trump: (
                    ordinary_relay_completion_for_actor(ctx, t))
                finish.bid = bid
                finish.applies = lambda ctx, t=trump: (
                    ordinary_relay_completion_for_actor(ctx, t))
                finish.meaning.action = action
                finish.meaning.nature = ['natural']
                finish.meaning.acts = acts
                finish.meaning.target_suit = trump if bid != 'P' else 'N'
                finish.meaning.agreed_suit = trump
                finish.meaning.purpose_completed = (bid == '6' + trump)
                finish.description = ('Place the contract after the forced relay.'
                                      if bid != 'P' else
                                      'Pass the forced five notrump relay.')
                record = finish.effect('keycard_context')
                record.method = 'rkcb_1430'
                record.trump_suit = trump
                record.status = 'completed'
                record.continuation_stage = 'relay'
                carry_answer_state(record, trump)

            for suit in 'CDHS':
                if suit == trump or '6' + suit > '6' + trump:
                    continue
                show = self.call('ordinary_rkcb_' + trump.lower()
                                 + '_relay_show_' + suit.lower() + '_king')
                show.when = '*'
                show.requires = lambda ctx, t=trump: (
                    ordinary_relay_completion_for_actor(ctx, t))
                show.bid = '6' + suit
                show.applies = (lambda ctx, t=trump, s=suit: (
                    ordinary_relay_completion_for_actor(ctx, t)
                    and ctx.hand is not None
                    and ctx.hand.contains_rank(s, 'K')))
                show.meaning.action = 'rkcb_1430_relay_king_show'
                show.meaning.nature = ['artificial']
                show.meaning.acts = ['control_showing', 'slam_try']
                show.meaning.target_suit = trump
                show.meaning.agreed_suit = trump
                show.meaning.control_suit = suit
                show.description = ('Show the ' + suit + ' king after the relay; '
                                    'this is not a specific king ask.')
                record = show.effect('keycard_context')
                record.method = 'rkcb_1430'
                record.trump_suit = trump
                record.status = 'answered'
                record.continuation_stage = 'relay'
                carry_answer_state(record, trump)

            # Direct high-answer continuations: Pass places the current
            # contract, a legal lower six-level side suit is a grand
            # invitation, and seven of trumps is final.
            place = self.call('ordinary_rkcb_' + trump.lower()
                              + '_high_answer_pass')
            place.when = '*'
            place.requires = lambda ctx, t=trump: (
                ordinary_high_answer_for_actor(ctx, t))
            place.bid = 'P'
            place.applies = lambda ctx, t=trump: (
                ordinary_high_answer_for_actor(ctx, t))
            place.meaning.action = 'rkcb_1430_high_answer_placement'
            place.meaning.nature = ['natural']
            place.meaning.acts = ['signoff', 'final_placement']
            place.meaning.target_suit = trump
            place.meaning.agreed_suit = trump
            place.description = ('Place the current contract after a direct '
                                 'high-answer; this is not a grand invitation.')
            record = place.effect('keycard_context')
            record.method = 'rkcb_1430'
            record.trump_suit = trump
            record.status = 'completed'
            carry_answer_state(record, trump)

            answer_bids = ['5N']
            answer_bids.extend('6' + suit for suit in 'CDHS'
                               if suit != trump and '6' + suit < '6' + trump)
            answer_bids.append('6' + trump)
            for answer_bid in answer_bids:
                for invitation in 'CDHS':
                    if invitation == trump:
                        continue
                    if answer_bid == '5N':
                        if not ('5N' < '6' + invitation < '6' + trump):
                            continue
                    elif not ('6' + answer_bid[1] < '6' + invitation
                              < '6' + trump):
                        continue
                    skipped = ordinary_skipped_lower_kings(
                        answer_bid, '6' + invitation, trump,
                        ['6' + suit for suit in 'CDHS'])
                    invite = self.call(
                        'ordinary_rkcb_' + trump.lower() + '_grand_invite_'
                        + answer_bid.lower() + '_' + invitation.lower())
                    invite.when = '*'
                    invite.requires = (
                        lambda ctx, t=trump, a=answer_bid, i='6' + invitation:
                        ordinary_grand_invite_actor(ctx, t, a, i))
                    invite.bid = '6' + invitation
                    invite.applies = (
                        lambda ctx, t=trump, a=answer_bid, i='6' + invitation:
                        ordinary_grand_invite_actor(ctx, t, a, i))
                    invite.meaning.action = 'rkcb_1430_grand_invitation'
                    invite.meaning.nature = ['artificial']
                    invite.meaning.acts = ['invite', 'slam_try']
                    invite.meaning.target_suit = trump
                    invite.meaning.agreed_suit = trump
                    invite.description = ('Grand invitation after a direct '
                                          'high answer; not a specific king ask.')
                    record = invite.effect('keycard_context')
                    record.method = 'rkcb_1430'
                    record.trump_suit = trump
                    record.status = 'answered'
                    record.continuation_stage = 'grand_invitation'
                    carry_answer_state(record, trump)
                    record.invitation_call = '6' + invitation
                    record.counterinvite_count = 0
                    record.not_required_kings = list(skipped)

            final = self.call('ordinary_rkcb_' + trump.lower()
                              + '_high_answer_seven')
            final.when = '*'
            final.requires = lambda ctx, t=trump: (
                ordinary_high_answer_for_actor(ctx, t))
            final.bid = '7' + trump
            final.applies = lambda ctx, t=trump: (
                ordinary_high_answer_for_actor(ctx, t))
            final.meaning.action = 'rkcb_1430_grand_placement'
            final.meaning.nature = ['natural']
            final.meaning.acts = ['signoff', 'final_placement']
            final.meaning.target_suit = trump
            final.meaning.agreed_suit = trump
            final.meaning.purpose_completed = True
            final.description = 'A seven-level call is final, not an invitation.'
            record = final.effect('keycard_context')
            record.method = 'rkcb_1430'
            record.trump_suit = trump
            record.status = 'completed'
            carry_answer_state(record, trump)

            for suit in 'CDHS':
                if suit == trump or '6' + suit > '6' + trump:
                    continue
                counter = self.call('ordinary_rkcb_' + trump.lower()
                                    + '_counterinvite_' + suit.lower())
                counter.when = '*'
                counter.requires = lambda ctx, t=trump: (
                    ordinary_grand_responder(ctx, t))
                counter.bid = '6' + suit
                counter.applies = (lambda ctx, t=trump, s=suit: (
                    ordinary_grand_responder(ctx, t)
                    and ctx.hand is not None
                    and ctx.hand.contains_rank(s, 'K')))
                counter.meaning.action = 'rkcb_1430_counter_invitation'
                counter.meaning.nature = ['artificial']
                counter.meaning.acts = ['invite', 'slam_try', 'control_showing']
                counter.meaning.target_suit = trump
                counter.meaning.agreed_suit = trump
                counter.meaning.control_suit = suit
                counter.description = ('Counter-invite with a higher unknown '
                                       'king; this is not a specific king ask.')
                record = counter.effect('keycard_context')
                record.method = 'rkcb_1430'
                record.trump_suit = trump
                record.status = 'answered'
                record.continuation_stage = 'counterinvited'
                record.counterinvite_count = 1
                record.shown_king = suit
                carry_answer_state(record, trump)
                record.not_required_kings = StateAttribute(
                    'keycard_context', 'not_required_kings',
                    method='rkcb_1430', trump_suit=trump)

            for bid, action, acts in (
                ('6' + trump, 'rkcb_1430_grand_reject',
                 ['signoff', 'final_placement']),
                ('7' + trump, 'rkcb_1430_grand_accept',
                 ['final_placement']),
            ):
                reply = self.call('ordinary_rkcb_' + trump.lower()
                                  + '_grand_reply_' + bid.lower())
                reply.when = '*'
                reply.requires = lambda ctx, t=trump: (
                    ordinary_grand_responder(ctx, t))
                reply.bid = bid
                reply.applies = lambda ctx, t=trump: (
                    ordinary_grand_responder(ctx, t))
                reply.meaning.action = action
                reply.meaning.nature = ['natural']
                reply.meaning.acts = acts
                reply.meaning.target_suit = trump
                reply.meaning.agreed_suit = trump
                reply.meaning.purpose_completed = True
                reply.description = ('Reject with six or accept with seven of trumps.')
                record = reply.effect('keycard_context')
                record.method = 'rkcb_1430'
                record.trump_suit = trump
                record.status = 'completed'
                carry_answer_state(record, trump)

            for bid in ('6' + trump, '7' + trump):
                finish_counter = self.call('ordinary_rkcb_' + trump.lower()
                                           + '_after_counterinvite_'
                                           + bid.lower())
                finish_counter.when = '*'
                finish_counter.requires = lambda ctx, t=trump: (
                    ordinary_counterinvite_asker(ctx, t))
                finish_counter.bid = bid
                finish_counter.applies = lambda ctx, t=trump: (
                    ordinary_counterinvite_asker(ctx, t))
                finish_counter.meaning.action = 'rkcb_1430_counterinvite_decision'
                finish_counter.meaning.nature = ['natural']
                finish_counter.meaning.acts = ['final_placement']
                finish_counter.meaning.target_suit = trump
                finish_counter.meaning.agreed_suit = trump
                finish_counter.meaning.purpose_completed = True
                finish_counter.description = ('Choose six or seven of trumps '
                                              'after the single counter-invitation.')
                record = finish_counter.effect('keycard_context')
                record.method = 'rkcb_1430'
                record.trump_suit = trump
                record.status = 'completed'
                carry_answer_state(record, trump)

        for branch, prefix, trump in asks:
            for bid, counts, queen, explanation in steps:
                # The asker's private keycard purpose selects five or six of
                # the agreed suit. These public declarations make that final
                # placement legible to the other player, who can then pass.
                for level in (5, 6):
                    placement_bid = str(level) + trump
                    if level == 5 and 'CDHSN'.index(trump) <= 'CDHSN'.index(bid[-1]):
                        continue
                    placement = self.call(branch + '_after_' + bid.lower()
                                          + '_place_' + placement_bid.lower())
                    placement.when = prefix + bid + 'P'
                    placement.bid = placement_bid
                    placement.applies = route_intent_not_yet_selected
                    placement.meaning.action = 'keycard_final_placement'
                    placement.meaning.historical_only = True
                    placement.meaning.nature = ['natural']
                    placement.meaning.acts = ['signoff', 'final_placement']
                    placement.meaning.target_suit = trump
                    placement.meaning.agreed_suit = trump
                    placement.meaning.purpose_completed = True
                    placement.description = 'Asker placed the agreed-trump contract after the keycard answer.'
