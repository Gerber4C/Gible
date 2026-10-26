# Basic uncontested Roman keycard 1430 answers. Special void answers and
# post-answer signoffs remain unimplemented, so those branches still block.


def route_intent_not_yet_selected(ctx):
    return False


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
            ask.applies = lambda ctx, t=trump: named_evaluator(ctx, 'absolute_maximum_' + t) is True
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
                texas.applies = lambda ctx, t=trump: named_evaluator(ctx, 'texas_slam_keycard_' + t)
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
            for answer in superaccepts:
                prefix = '1NP' + transfer + 'P' + answer + 'P4NP'
                asks.append(('jacoby_' + trump + '_' + answer, prefix, trump))
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
        for branch, prefix, trump in asks:
            for bid, counts, queen, explanation in steps:
                answer = self.call(branch + '_answer_' + bid.lower())
                answer.when = prefix
                answer.bid = bid
                answer.applies = lambda ctx, t=trump, c=counts, q=queen: ordinary_keycard_answer(ctx, t, c, q)
                answer.meaning.action = 'rkcb_1430_answer'
                answer.meaning.nature = ['artificial']
                answer.meaning.acts = ['descriptive', 'keycard_answer']
                answer.meaning.target_suit = trump
                answer.meaning.agreed_suit = trump
                answer.meaning.keycard_counts = list(counts)
                if bid == '5D':
                    answer.meaning.preferred_keycard_count = 3
                if queen is not None:
                    answer.meaning.trump_queen = queen
                answer.description = explanation + '; later continuations are not yet defined.'

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
