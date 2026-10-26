# Historical Jacoby splinters and opener's confirmed continuations. The
# responder's decision to start this slam route awaits deal simulation.


def not_yet_selected_by_simulation(ctx):
    return False


def splinter_ready(ctx, trump, short):
    return (ctx.state.exists('splinter_context', trump_suit=trump,
                             short_suit=short, status='pending')
            and ctx.state.exists('agreed_suit', suit=trump))


def second_round_control(ctx, suit):
    return (ctx.hand.contains_rank(suit, 'A')
            or ctx.hand.contains_rank(suit, 'K')
            or ctx.hand.length(suit) <= 1)


def reply_in_range(ctx, trump, short, lower, upper):
    if not splinter_ready(ctx, trump, short):
        return False
    points = splinter_adjusted_hcp(ctx.hand, short)
    return points >= lower and (upper is None or points <= upper)


def cue_available(ctx, trump, short, suit, earlier):
    return (reply_in_range(ctx, trump, short, 15.5, 16)
            and second_round_control(ctx, suit)
            and not any(second_round_control(ctx, previous) for previous in earlier))


class JacobySplinter(Gadget):
    id = 'jacoby_splinter'
    namespace = 'daqiush_2over1'
    name = 'Jacoby splinter and adjusted opener responses'
    author = Author('Daqiush')

    def build(self):
        for transfer, accept, trump in (('2D', '2H', 'H'), ('2H', '2S', 'S')):
            invitation = self.call('jacoby_' + trump.lower() + '_four_level_slam_invite')
            invitation.when = '1NP' + transfer + 'P' + accept + 'P'
            invitation.bid = '4' + trump
            invitation.applies = not_yet_selected_by_simulation
            invitation.meaning.action = 'major_slam_invitation'
            invitation.meaning.nature = ['natural']
            invitation.meaning.acts = ['slam_try']
            invitation.meaning.agreed_suit = trump
            invitation.effect('agreed_suit').suit = trump
            invitation.description = ('After an ordinary Jacoby acceptance, '
                                      'a no-shortage hand invites slam in the major; '
                                      'the private decision awaits simulation.')

        branches = (
            ('2D', '2H', 'H', '3S', ('4C', '4D')),
            ('2D', '2H', 'H', '4C', ('4D', '4S')),
            ('2D', '2H', 'H', '4D', ('4S', '5C')),
            ('2H', '2S', 'S', '4C', ('4D', '4H')),
            ('2H', '2S', 'S', '4D', ('4H', '5C')),
            ('2H', '2S', 'S', '4H', ('5C', '5D')),
        )
        for transfer, accept, trump, splinter, cues in branches:
            short = splinter[1]
            prefix = '1NP' + transfer + 'P' + accept + 'P'
            call = self.call('splinter_' + trump.lower() + '_' + short.lower())
            call.when = prefix
            call.bid = splinter
            call.applies = not_yet_selected_by_simulation
            call.meaning.action = 'splinter'
            call.meaning.nature = ['artificial']
            call.meaning.acts = ['slam_try', 'game_forcing']
            call.meaning.forcing = 'game_forcing'
            call.meaning.short_suit = short
            call.meaning.agreed_suit = trump
            agreement = call.effect('agreed_suit')
            agreement.suit = trump
            context = call.effect('splinter_context')
            context.trump_suit = trump
            context.short_suit = short
            context.status = 'pending'
            call.description = 'Splinter short suit; transferred major immediately agreed as trumps.'

            answer_prefix = prefix + splinter + 'P'
            weak = self.call('splinter_' + trump.lower() + '_' + short.lower() + '_weak')
            weak.when = answer_prefix
            weak.bid = '4' + trump
            weak.applies = lambda ctx, t=trump, s=short: reply_in_range(ctx, t, s, 0, 15)
            weak.meaning.action = 'splinter_decline'
            weak.meaning.nature = ['natural']
            weak.meaning.acts = ['signoff']
            weak.meaning.agreed_suit = trump
            weak.description = 'Adjusted HCP below 15.5; return to four of the agreed major.'

            for cue_bid in cues:
                cue_suit = cue_bid[1]
                earlier = tuple(item[1] for item in cues[:cues.index(cue_bid)])
                cue = self.call('splinter_' + trump.lower() + '_' + short.lower() + '_cue_' + cue_suit.lower())
                cue.when = answer_prefix
                cue.bid = cue_bid
                cue.applies = lambda ctx, t=trump, s=short, c=cue_suit, e=earlier: cue_available(ctx, t, s, c, e)
                cue.meaning.action = 'control_cue'
                cue.meaning.nature = ['artificial']
                cue.meaning.acts = ['slam_try', 'control_showing']
                cue.meaning.agreed_suit = trump
                cue.meaning.control_suit = cue_suit
                cue.description = 'Adjusted HCP 15.5–16; show a second-round control.'

            ask = self.call('splinter_' + trump.lower() + '_' + short.lower() + '_keycard')
            ask.when = answer_prefix
            ask.bid = '4NT'
            ask.applies = lambda ctx, t=trump, s=short: reply_in_range(ctx, t, s, 16.5, 17)
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
            ask.description = 'Adjusted HCP 16.5–17; Roman keycard ask for the agreed major.'
