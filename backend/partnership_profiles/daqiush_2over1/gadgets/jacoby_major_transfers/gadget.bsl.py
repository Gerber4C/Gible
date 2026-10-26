# Jacoby initiation for confirmed hand classes. Other strengths and later
# continuations are authored incrementally rather than inferred from a bid.


def weak_major_suit_quality(ctx, suit):
    return ctx.hand_quality['suit_evaluations'][suit]['twentieths']


def weak_major_transfer_suit(ctx):
    if ctx.hand is None or not (ctx.hand.hcp <= 7 or
                                (ctx.hand.hcp == 8 and ctx.hand_quality['kr_delta'] <= -1.5)):
        return None
    hearts, spades = ctx.hand.length('H'), ctx.hand.length('S')
    if min(hearts, spades) >= 5 and shapely_combined_effective_points(ctx.hand) >= 5:
        return None  # Two-suit invitation/force has its own agreed route.
    if sorted((hearts, spades)) == [4, 6] and shapely_combined_effective_points(ctx.hand) >= 5:
        return None  # Start with Stayman to find the four-four fit.
    if min(hearts, spades) < 4 or max(hearts, spades) < 5:
        return None
    if hearts != spades:
        return 'H' if hearts > spades else 'S'
    return 'H' if weak_major_suit_quality(ctx, 'H') > weak_major_suit_quality(ctx, 'S') else 'S'


def starts_jacoby(ctx, trump):
    if ctx.hand is None:
        return False
    selected_weak_major = weak_major_transfer_suit(ctx)
    if selected_weak_major is not None:
        return trump == selected_weak_major
    if min(ctx.hand.length('H'), ctx.hand.length('S')) >= 5:
        points = shapely_combined_effective_points(ctx.hand)
        if points >= 9:
            return trump == 'S'  # 2H–2S–3H: game-forcing 5-5 majors.
        if points >= 5:
            return trump == 'H'  # 2D–2H–2S: invitational 5-5 majors.
    other = 'S' if trump == 'H' else 'H'
    if ctx.hand.length(trump) == 5:
        return ctx.hand.length(other) <= 3
    if ctx.hand.length(trump) != 6 or ctx.hand.length(other) >= 4:
        return False
    shaped_points = shapely_second_minor_strength(ctx, trump)
    if shaped_points is not None and 4 <= shaped_points <= 6:
        return ctx.hand_quality['kr_points'] + 15 < 25
    if named_evaluator(ctx, 'texas_slam_keycard_' + trump):
        return False
    if named_evaluator(ctx, 'six_card_slam_interest_' + trump):
        return True
    if max(ctx.hand.length(suit) for suit in 'CD') >= 4:
        return True  # A second minor needs its own Jacoby continuation.
    return ctx.hand_quality['kr_points'] + 15 < 25  # Below the game-only Texas route.


def weak_jacoby(ctx, trump):
    return (ctx.hand is not None and ctx.hand.length(trump) >= 5
            and not (min(ctx.hand.length('H'), ctx.hand.length('S')) >= 5
                     and shapely_combined_effective_points(ctx.hand) >= 5)
            and not (ctx.hand.length(trump) == 5
                     and max(ctx.hand.length(s) for s in 'CD') == 6
                     and shapely_combined_effective_points(ctx.hand) >= 6)
            and not (ctx.hand.length(trump) == 5
                     and max(ctx.hand.length(s) for s in 'CD') == 5
                     and shapely_combined_effective_points(ctx.hand) >= 7)
            and not ((shapely_second_minor_strength(ctx, trump) or 0) >= 7)
            and (ctx.hand.hcp <= 7 or (ctx.hand.hcp == 8 and ctx.hand_quality['kr_delta'] <= -1.5)))


def inviting_jacoby(ctx, trump):
    return (ctx.hand is not None and ctx.hand.length(trump) >= 5
            and not (min(ctx.hand.length('H'), ctx.hand.length('S')) >= 5)
            and not ((shapely_second_minor_strength(ctx, trump) or 0) >= 7)
            and (ctx.hand.hcp in (8, 9)
                 or (ctx.hand.length(trump) == 5
                     and max(ctx.hand.length(s) for s in 'CD') == 5
                     and 7 <= shapely_combined_effective_points(ctx.hand) < 9)
                 or (ctx.hand.length(trump) == 5
                     and max(ctx.hand.length(s) for s in 'CD') == 6
                     and shapely_combined_effective_points(ctx.hand) >= 6))
            and not weak_jacoby(ctx, trump)
            and not (ctx.hand.hcp == 9 and ctx.hand_quality['kr_delta'] >= 1.0))


def six_minor_five_major_invite(ctx, trump):
    if ctx.hand is None or ctx.hand.length(trump) != 5:
        return False
    minor = max('CD', key=lambda suit: ctx.hand.length(suit))
    return (ctx.hand.length(minor) == 6
            and shapely_description_proxy(ctx.hand, minor)['effective_points'] >= 8)


def five_minor_five_major_invite(ctx, trump):
    return (ctx.hand is not None and ctx.hand.length(trump) == 5
            and max(ctx.hand.length(s) for s in 'CD') == 5
            and 7 <= shapely_combined_effective_points(ctx.hand) < 9)


def five_card_invite_acceptance_not_calibrated(ctx):
    return False


def major_two_suit_invite(ctx):
    return (ctx.hand is not None and min(ctx.hand.length(s) for s in 'HS') >= 5
            and 5 <= shapely_combined_effective_points(ctx.hand) < 9)


def major_two_suit_force(ctx):
    return (ctx.hand is not None and min(ctx.hand.length(s) for s in 'HS') >= 5
            and shapely_combined_effective_points(ctx.hand) >= 9)


def game_five_major(ctx, trump):
    return (ctx.hand is not None and ctx.hand.length(trump) == 5
            and max(ctx.hand.length(suit) for suit in 'CD') <= 3
            and (10 <= ctx.hand.hcp <= 14
                 or (ctx.hand.hcp == 9 and ctx.hand_quality['kr_delta'] >= 1.0)))


def second_minor_game_force(ctx, trump, minor):
    if ctx.hand is None or ctx.hand.length(trump) < 5 or ctx.hand.length(minor) < 4:
        return False
    if ctx.hand.length('H' if trump == 'S' else 'S') > 3:
        return False
    shaped_points = shapely_second_minor_strength(ctx, trump)
    if shaped_points is not None:
        return shaped_points >= 7
    if ctx.hand.length(trump) == 5 and ctx.hand.length(minor) == 5:
        return shapely_combined_effective_points(ctx.hand) >= 9
    return ctx.hand.hcp >= 10


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


def second_round_control(ctx, suit):
    holding = ctx.hand.holding(suit)
    return 'A' in holding or 'K' in holding or len(holding) <= 1


SUPERACCEPTS = {
    'H': (('2S', 'S'), ('2NT', 'D'), ('3C', 'C')),
    'S': (('2NT', 'H'), ('3C', 'C'), ('3D', 'D')),
}


def absolute_maximum(ctx, trump):
    return named_evaluator(ctx, 'absolute_maximum_' + trump) is True


def superaccept_doubleton(ctx, trump, doubleton):
    return (ctx.hand is not None and ctx.hand.length(trump) >= 4
            and ctx.hand.length(doubleton) == 2 and absolute_maximum(ctx, trump))


def superaccept_4333(ctx, trump):
    return (ctx.hand is not None and ctx.hand.length(trump) == 4
            and all(ctx.hand.length(suit) == 3 for suit in 'SHDC' if suit != trump)
            and absolute_maximum(ctx, trump))


def ordinary_acceptance(ctx, trump):
    return (ctx.hand is not None
            and not superaccept_4333(ctx, trump)
            and not any(superaccept_doubleton(ctx, trump, suit)
                        for _, suit in SUPERACCEPTS[trump]))


class JacobyMajorTransfers(Gadget):
    id = 'jacoby_major_transfers'
    namespace = 'daqiush_2over1'
    name = 'Jacoby major transfers and superaccepts'
    author = Author('Daqiush')

    def build(self):
        self.evaluator('shapely_second_minor_strength_H',
                       lambda ctx: shapely_second_minor_strength(ctx, 'H'))
        self.evaluator('shapely_second_minor_strength_S',
                       lambda ctx: shapely_second_minor_strength(ctx, 'S'))
        for transfer, accept, trump in (('2D', '2H', 'H'), ('2H', '2S', 'S')):
            call = self.call('jacoby_' + trump.lower() + '_transfer')
            call.when = '1NP'
            call.bid = transfer
            call.applies = lambda ctx, t=trump: starts_jacoby(ctx, t)
            call.meaning.action = 'transfer'
            call.meaning.nature = ['artificial']
            call.meaning.acts = ['directive']
            call.meaning.target_suit = trump
            call.description = 'Jacoby transfer to a five-card major, a weak longer major in a 5-4+ two-major hand, or a confirmed six-card slam-interest major.'

            ordinary = self.call('jacoby_' + trump.lower() + '_ordinary_acceptance')
            ordinary.when = '1NP' + transfer + 'P'
            ordinary.bid = accept
            ordinary.applies = lambda ctx, t=trump: ordinary_acceptance(ctx, t)
            ordinary.meaning.action = 'transfer_acceptance'
            ordinary.meaning.nature = ['natural']
            ordinary.meaning.acts = ['descriptive']
            ordinary.meaning.target_suit = trump
            ordinary.description = 'Ordinary Jacoby transfer acceptance.'

            ordinary_prefix = '1NP' + transfer + 'P' + accept + 'P'
            if trump == 'H':
                two_major = self.call('jacoby_two_major_invitation')
                two_major.when = ordinary_prefix
                two_major.bid = '2S'
                two_major.applies = major_two_suit_invite
                two_major.meaning.action = 'two_major_invitation'
                two_major.meaning.nature = ['natural']
                two_major.meaning.acts = ['invite']
                two_major.meaning.target_suit = 'S'
                two_major.meaning.shape_invitation = {
                    'minimum': 5, 'min_lengths': {'H': 5, 'S': 5}}
                two_major.description = 'After the heart transfer, 2S invites with at least five cards in each major.'

                invite_prefix = ordinary_prefix + '2SP'
                for call, minimum, has_fit, named_suit in (
                    ('2NT', False, False, 'N'), ('3NT', True, False, 'N'),
                    ('3H', False, True, 'H'), ('4H', True, True, 'H'),
                    ('3S', False, True, 'S'), ('4S', True, True, 'S'),
                ):
                    reply = self.call('two_major_invitation_' + call.lower())
                    reply.when = invite_prefix
                    reply.bid = call
                    reply.applies = (lambda ctx, high=minimum, fit=has_fit, suit=named_suit:
                                     ctx.hand is not None
                                     and (ctx.hand.hcp >= 16) == high
                                     and ((max(ctx.hand.length('H'), ctx.hand.length('S')) < 3)
                                          if not fit else
                                          (ctx.hand.length(suit) >= 3 and
                                           (ctx.hand.length(suit), ctx.hand.honor_count(suit, ('A','K','Q')), suit == 'S')
                                           >= (ctx.hand.length('S' if suit == 'H' else 'H'),
                                               ctx.hand.honor_count('S' if suit == 'H' else 'H', ('A','K','Q')),
                                               suit == 'H'))))
                    reply.meaning.action = 'two_major_invitation_' + ('accept' if minimum else 'reject')
                    reply.meaning.nature = ['natural']
                    reply.meaning.acts = ['accept' if minimum else 'reject']
                    reply.meaning.target_suit = named_suit
                    reply.description = 'Choose the better major fit, or notrump without a three-card major fit.'

                for earlier, finish in (('3NT', '4S'), ('2NT', '3S')):
                    rebid = self.call('six_spades_after_two_major_' + earlier.lower())
                    rebid.when = invite_prefix + earlier.replace('NT', 'N') + 'P'
                    rebid.bid = finish
                    rebid.applies = lambda ctx: (major_two_suit_invite(ctx)
                                                  and ctx.hand.length('S') >= 6)
                    rebid.meaning.action = 'six_spades_after_notrump_invitation'
                    rebid.meaning.nature = ['natural']
                    rebid.meaning.acts = ['signoff', 'final_placement']
                    rebid.meaning.target_suit = 'S'
                    rebid.meaning.purpose_completed = True
                    rebid.description = 'Six spades are preferable to notrump after opener accepts or declines.'

                for answer in ('2NT', '3NT', '3H', '4H', '3S', '4S'):
                    stop = self.call('two_major_invitation_stop_after_' + answer.lower())
                    stop.when = invite_prefix + answer.replace('NT', 'N') + 'P'
                    stop.bid = 'P'
                    stop.applies = (lambda ctx, a=answer: major_two_suit_invite(ctx)
                                    and not (a in ('2NT', '3NT') and ctx.hand.length('S') >= 6))
                    stop.meaning.action = 'two_major_invitation_stop'
                    stop.meaning.nature = ['natural']
                    stop.meaning.acts = ['signoff', 'final_placement']
                    stop.meaning.target_suit = answer[-1] if answer[-1] in 'HS' else 'N'
                    stop.meaning.purpose_completed = True
                    stop.description = 'The invitation has been answered; play the chosen partscore or game.'
            else:
                two_major = self.call('jacoby_two_major_game_force')
                two_major.when = ordinary_prefix
                two_major.bid = '3H'
                two_major.applies = major_two_suit_force
                two_major.meaning.action = 'two_major_game_force'
                two_major.meaning.nature = ['natural']
                two_major.meaning.acts = ['game_forcing']
                two_major.meaning.forcing = 'game_forcing'
                two_major.meaning.target_suit = 'H'
                two_major.description = 'After the spade transfer, 3H shows game-forcing 5-5 majors.'

                force_prefix = ordinary_prefix + '3HP'
                for bid, applies, target in (
                    ('3S', lambda ctx: ctx.hand.length('S') >= 3 and ctx.hand.hcp >= 16, 'S'),
                    ('4S', lambda ctx: ctx.hand.length('S') >= 3 and ctx.hand.hcp < 16, 'S'),
                    ('4H', lambda ctx: ctx.hand.length('S') < 3 and ctx.hand.length('H') >= 3, 'H'),
                    ('3NT', lambda ctx: max(ctx.hand.length('S'), ctx.hand.length('H')) < 3, 'N'),
                ):
                    reply = self.call('two_major_force_' + bid.lower())
                    reply.when = force_prefix
                    reply.bid = bid
                    reply.applies = lambda ctx, fn=applies: ctx.hand is not None and fn(ctx)
                    reply.meaning.action = 'two_major_game_force_reply'
                    reply.meaning.nature = ['natural']
                    reply.meaning.acts = ['descriptive']
                    reply.meaning.target_suit = target
                    if target in 'HS':
                        reply.meaning.agreed_suit = target
                        reply.effect('agreed_suit').suit = target
                    reply.description = 'Show a major fit, with 3S reserving slam space for a stronger spade hand.'

                for answer, agreed_major in (('3S', 'S'), ('4S', 'S'), ('4H', 'H')):
                    placement = self.call('two_major_force_game_after_' + answer.lower())
                    placement.when = force_prefix + answer + 'P'
                    placement.bid = '4' + agreed_major if answer == '3S' else 'P'
                    placement.applies = lambda ctx: major_two_suit_force(ctx)
                    placement.meaning.action = 'two_major_game_placement'
                    placement.meaning.nature = ['natural']
                    placement.meaning.acts = ['signoff', 'final_placement']
                    placement.meaning.target_suit = agreed_major
                    placement.meaning.purpose_completed = True
                    placement.description = 'With a known major fit, play the major game until a slam route is justified.'

                slam = self.call('two_major_force_spade_keycard')
                slam.when = force_prefix + '3SP'
                slam.bid = '4NT'
                slam.applies = major_two_suit_force
                slam.meaning.action = 'rkcb_1430'
                slam.meaning.nature = ['artificial']
                slam.meaning.acts = ['inquiry', 'keycard_asking']
                slam.meaning.target_suit = 'S'
                slam.meaning.agreed_suit = 'S'
                slam.effect('agreed_suit').suit = 'S'
                keycards = slam.effect('keycard_context')
                keycards.trump_suit = 'S'
                keycards.ask_call = '4N'
                keycards.method = 'rkcb_1430'
                keycards.status = 'pending'
                slam.description = 'Public-deal simulation prefers a spade slam; ask spade keycards.'

                nt = self.call('two_major_force_no_fit_notrump')
                nt.when = force_prefix + '3NTP'
                nt.bid = '6NT'
                nt.applies = lambda ctx: major_two_suit_force(ctx) and ctx.hand.hcp >= 18
                nt.meaning.action = 'two_major_no_fit_slam'
                nt.meaning.nature = ['natural']
                nt.meaning.acts = ['signoff', 'final_placement']
                nt.meaning.target_suit = 'N'
                nt.meaning.purpose_completed = True
                nt.description = 'Without a major fit, the 18-HCP responder has enough for 6NT.'

                nt_stop = self.call('two_major_force_no_fit_game')
                nt_stop.when = force_prefix + '3NTP'
                nt_stop.bid = 'P'
                nt_stop.applies = lambda ctx: major_two_suit_force(ctx) and ctx.hand.hcp < 18
                nt_stop.meaning.action = 'two_major_no_fit_game'
                nt_stop.meaning.nature = ['natural']
                nt_stop.meaning.acts = ['signoff', 'final_placement']
                nt_stop.meaning.target_suit = 'N'
                nt_stop.meaning.purpose_completed = True

            for minor in 'CD':
                new_suit = self.call('jacoby_' + trump.lower() + '_second_' + minor.lower())
                new_suit.when = ordinary_prefix
                new_suit.bid = '3' + minor
                new_suit.applies = lambda ctx, t=trump, m=minor: second_minor_game_force(ctx, t, m)
                new_suit.meaning.action = 'natural_second_minor'
                new_suit.meaning.nature = ['natural']
                new_suit.meaning.acts = ['game_forcing']
                new_suit.meaning.forcing = 'game_forcing'
                new_suit.meaning.target_suit = minor
                new_suit.description = 'Natural four-plus second minor after Jacoby; game forcing.'

                minor_prefix = ordinary_prefix + '3' + minor + 'P'
                available_cues = [s for s in 'DHS' if s != minor
                                  and '3' + s != '3' + minor]
                for cue in available_cues:
                    if (minor == 'D' and cue == 'D') or (minor == 'C' and cue == 'C'):
                        continue
                    cue_call = self.call('jacoby_' + trump.lower() + '_' + minor.lower()
                                        + '_support_cue_' + cue.lower())
                    cue_call.when = minor_prefix
                    cue_call.bid = '3' + cue
                    cue_call.applies = (lambda ctx, m=minor, s=cue, earlier=tuple(
                        earlier for earlier in available_cues if earlier < cue):
                        ctx.hand is not None and ctx.hand.length(m) >= 4
                        and second_round_control(ctx, s)
                        and not any(second_round_control(ctx, x) for x in earlier))
                    cue_call.meaning.action = 'minor_support_control'
                    cue_call.meaning.nature = ['artificial']
                    cue_call.meaning.acts = ['control_showing']
                    cue_call.meaning.agreed_suit = minor
                    cue_call.meaning.target_suit = minor
                    cue_call.effect('agreed_suit').suit = minor
                    cue_call.description = 'Three-level control cue confirms four-card support for the second minor.'

                natural_nt = self.call('jacoby_' + trump.lower() + '_' + minor.lower() + '_no_cue')
                natural_nt.when = minor_prefix
                natural_nt.bid = '3NT'
                natural_nt.applies = (lambda ctx, m=minor, suits=tuple(available_cues):
                                      ctx.hand is not None and (ctx.hand.length(m) < 4
                                      or not any(second_round_control(ctx, s) for s in suits)))
                natural_nt.meaning.action = 'second_minor_natural_notrump'
                natural_nt.meaning.nature = ['natural']
                natural_nt.meaning.acts = ['descriptive']
                natural_nt.meaning.target_suit = 'N'
                natural_nt.description = 'Without a supported three-level cue, offer natural 3NT.'

                shaped_game = self.call('jacoby_' + trump.lower() + '_' + minor.lower()
                                        + '_shapely_game_after_3nt')
                shaped_game.when = minor_prefix + '3NTP'
                shaped_game.bid = '4' + trump
                shaped_game.applies = (lambda ctx, t=trump:
                                       (shapely_second_minor_strength(ctx, t) or 0) >= 7)
                shaped_game.meaning.action = 'six_five_major_game_without_minor_fit'
                shaped_game.meaning.nature = ['natural']
                shaped_game.meaning.acts = ['signoff', 'final_placement']
                shaped_game.meaning.target_suit = trump
                shaped_game.meaning.purpose_completed = True
                shaped_game.description = 'Without four-card support for the second minor, return to the six-card major game.'

            for bid, applies, action in (
                ('P', lambda ctx, t=trump: weak_jacoby(ctx, t), 'weak_stop'),
                ('2NT', lambda ctx, t=trump: ctx.hand.length(t) == 5
                 and inviting_jacoby(ctx, t)
                 and not six_minor_five_major_invite(ctx, t)
                 and not five_minor_five_major_invite(ctx, t), 'five_card_invite'),
                ('3' + trump, lambda ctx, t=trump: inviting_jacoby(ctx, t)
                 and (ctx.hand.length(t) == 6 or six_minor_five_major_invite(ctx, t)
                      or five_minor_five_major_invite(ctx, t)), 'six_card_invite'),
                ('3NT', lambda ctx, t=trump: game_five_major(ctx, t), 'five_card_game'),
            ):
                rebid = self.call('jacoby_' + trump.lower() + '_' + action)
                rebid.when = ordinary_prefix
                rebid.bid = bid
                rebid.applies = applies
                rebid.meaning.action = action
                rebid.meaning.nature = ['natural']
                rebid.meaning.acts = ['signoff'] if bid == 'P' else ['invite'] if 'invite' in action else ['descriptive']
                rebid.meaning.target_suit = 'N' if bid in ('2NT', '3NT') else trump
                if action == 'six_card_invite':
                    rebid.meaning.shape_invitation = {
                        'minimum': 6,
                        'min_lengths': {trump: 5}}
                rebid.description = 'Weak stop, natural invitation, or game after ordinary Jacoby acceptance.'

            for bid, has_fit, action in (
                ('P', False, 'reject'), ('3' + trump, True, 'reject'),
                ('3NT', False, 'accept'), ('4' + trump, True, 'accept'),
            ):
                follow = self.call('jacoby_' + trump.lower() + '_five_invite_' + action + '_' + bid.lower())
                follow.when = ordinary_prefix + '2NTP'
                follow.bid = bid
                follow.applies = five_card_invite_acceptance_not_calibrated
                follow.meaning.action = 'jacoby_five_invitation_' + action
                follow.meaning.nature = ['natural']
                follow.meaning.acts = [action] if bid == 'P' else [action, 'final_placement']
                follow.meaning.target_suit = 'N' if bid in ('P', '3NT') else trump
                if bid != 'P':
                    follow.meaning.purpose_completed = True
                follow.description = 'Opener accepts or rejects the five-card major game invitation.'

            for bid, action in (('P', 'reject'), ('4' + trump, 'accept')):
                follow = self.call('jacoby_' + trump.lower() + '_six_invite_' + action)
                follow.when = ordinary_prefix + '3' + trump + 'P'
                follow.bid = bid
                follow.applies = lambda ctx: ctx.hand is not None
                follow.meaning.action = 'jacoby_six_invitation_' + action
                follow.meaning.nature = ['natural']
                follow.meaning.acts = [action] if bid == 'P' else [action, 'final_placement']
                follow.meaning.target_suit = trump
                if bid != 'P':
                    follow.meaning.purpose_completed = True
                follow.description = 'Opener accepts or rejects the six-card major game invitation.'

            for bid, has_fit in (('P', False), ('4' + trump, True)):
                follow = self.call('jacoby_' + trump.lower() + '_game_' + bid.lower())
                follow.when = ordinary_prefix + '3NTP'
                follow.bid = bid
                follow.applies = lambda ctx, t=trump, fit=has_fit: ctx.hand is not None and (ctx.hand.length(t) >= 3) == fit
                follow.meaning.action = 'jacoby_game_placement'
                follow.meaning.nature = ['natural']
                follow.meaning.acts = ['signoff', 'final_placement']
                follow.meaning.target_suit = 'N' if bid == 'P' else trump
                follow.meaning.purpose_completed = True
                follow.description = 'With three-card support play 4M; otherwise play 3NT.'

            for answer, doubleton in SUPERACCEPTS[trump]:
                special = self.call('jacoby_' + trump.lower() + '_doubleton_' + doubleton.lower())
                special.when = '1NP' + transfer + 'P'
                special.bid = answer
                special.applies = lambda ctx, t=trump, d=doubleton: superaccept_doubleton(ctx, t, d)
                special.meaning.action = 'transfer_superaccept'
                special.meaning.nature = ['artificial']
                special.meaning.acts = ['descriptive']
                special.meaning.target_suit = trump
                special.meaning.doubleton_suit = doubleton
                special.meaning.support_length_min = 4
                special.description = 'Absolute-maximum superaccept with a doubleton in ' + doubleton + '.'

            flat = self.call('jacoby_' + trump.lower() + '_4333_superaccept')
            flat.when = '1NP' + transfer + 'P'
            flat.bid = '3' + trump
            flat.applies = lambda ctx, t=trump: superaccept_4333(ctx, t)
            flat.meaning.action = 'transfer_superaccept'
            flat.meaning.nature = ['natural']
            flat.meaning.acts = ['descriptive']
            flat.meaning.target_suit = trump
            flat.meaning.support_length_min = 4
            flat.meaning.shape_class = '4333'
            flat.description = 'Absolute-maximum superaccept with four-card major support and 4333 shape.'

            for answer in tuple(bid for bid, _ in SUPERACCEPTS[trump]) + ('3' + trump,):
                prefix = '1NP' + transfer + 'P' + answer + 'P'
                if answer != '3' + trump:
                    retransfer = '3D' if trump == 'H' else '3H'
                    return_call = self.call('jacoby_' + trump.lower() + '_retransfer_after_' + answer.lower())
                    return_call.when = prefix
                    return_call.bid = retransfer
                    return_call.applies = lambda ctx, t=trump: weak_jacoby(ctx, t)
                    return_call.meaning.action = 'major_retransfer'
                    return_call.meaning.nature = ['artificial']
                    return_call.meaning.acts = ['directive']
                    return_call.meaning.target_suit = trump
                    return_call.description = 'Weak major hand uses 3M−1 to retransfer after superaccept.'

                    complete = self.call('jacoby_' + trump.lower() + '_complete_retransfer_after_' + answer.lower())
                    complete.when = prefix + retransfer + 'P'
                    complete.bid = '3' + trump
                    complete.applies = lambda ctx: ctx.hand is not None
                    complete.meaning.action = 'major_retransfer_acceptance'
                    complete.meaning.nature = ['natural']
                    complete.meaning.acts = ['signoff', 'final_placement']
                    complete.meaning.target_suit = trump
                    complete.meaning.purpose_completed = True
                    complete.description = 'Complete the retransfer to the agreed major.'
                else:
                    stop = self.call('jacoby_' + trump.lower() + '_pass_three_major')
                    stop.when = prefix
                    stop.bid = 'P'
                    stop.applies = lambda ctx, t=trump: weak_jacoby(ctx, t)
                    stop.meaning.action = 'weak_major_stop'
                    stop.meaning.nature = ['natural']
                    stop.meaning.acts = ['signoff']
                    stop.meaning.target_suit = trump
                    stop.description = 'The superaccept already placed the major at level three.'

                game = self.call('jacoby_' + trump.lower() + '_game_after_' + answer.lower())
                game.when = prefix
                game.bid = '4' + trump
                game.applies = lambda ctx, t=trump: (ctx.hand is not None and
                                                      ((ctx.hand.length(t) == 5 and
                                                        (inviting_jacoby(ctx, t) or game_five_major(ctx, t)))
                                                       or (t == 'S' and major_two_suit_force(ctx))))
                game.meaning.action = 'major_game_after_superaccept'
                game.meaning.nature = ['natural']
                game.meaning.acts = ['signoff', 'final_placement']
                game.meaning.target_suit = trump
                game.meaning.purpose_completed = True
                game.description = 'Superaccept shows maximum support; place game with a five-card major.'

                ask = self.call('jacoby_' + trump.lower() + '_after_' + answer.lower() + '_keycard')
                ask.when = '1NP' + transfer + 'P' + answer + 'P'
                ask.bid = '4NT'
                ask.applies = lambda ctx, t=trump: (
                    named_evaluator(ctx, 'six_card_slam_interest_' + t)
                    or (t == 'S' and major_two_suit_force(ctx)))
                ask.meaning.action = 'rkcb_1430'
                ask.meaning.nature = ['artificial']
                ask.meaning.acts = ['inquiry', 'keycard_asking']
                ask.meaning.target_suit = trump
                ask.meaning.agreed_suit = trump
                ask.effect('agreed_suit').suit = trump
                keycards = ask.effect('keycard_context')
                keycards.trump_suit = trump
                keycards.ask_call = '4N'
                keycards.method = 'rkcb_1430'
                keycards.status = 'pending'
                ask.description = 'All confirmed slam-interest hands ask keycards immediately after this superaccept.'
