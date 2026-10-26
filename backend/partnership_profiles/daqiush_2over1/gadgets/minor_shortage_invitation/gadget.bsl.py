"""Five-five minor invitation with a singleton in the named major."""


def invites_with_shortage(ctx, shortage):
    minor_lengths = sorted(ctx.hand.length(s) for s in 'CD') if ctx.hand is not None else []
    return (ctx.hand is not None and minor_lengths in ([5, 5], [5, 6])
            and ctx.hand.length(shortage) == 1
            and ctx.hand.hcp in (8, 9)
            and (minor_lengths == [5, 5]
                 or shapely_combined_effective_points(ctx.hand) < 7)
            and not (ctx.hand.hcp == 8 and ctx.hand_quality['kr_delta'] <= -1.5)
            and not (ctx.hand.hcp == 9 and ctx.hand_quality['kr_delta'] >= 1.0))


def best_minor(ctx):
    scores = {s: minor_game_control_points(ctx.hand, s, partner_long_suits=('C', 'D'))
              for s in 'CD'}
    return max('CD', key=lambda s: (scores[s], ctx.hand.length(s), s == 'C'))


def has_major_stopper(ctx, suit):
    holding = ctx.hand.holding(suit)
    return ('A' in holding or ('K' in holding and len(holding) >= 2)
            or ('Q' in holding and ('J' in holding or 'T' in holding)))


def accepts_invitation(ctx):
    return max(minor_game_control_points(ctx.hand, s, partner_long_suits=('C', 'D'))
               for s in 'CD') >= 14.5


class MinorShortageInvitation(Gadget):
    id = 'minor_shortage_invitation'
    namespace = 'daqiush_2over1'
    name = 'Five-five minor invitation with major shortage'
    author = Author('Daqiush')

    def build(self):
        for shortage in 'HS':
            ask = self.call('minor_shortage_' + shortage.lower())
            ask.when = '1NP'
            ask.bid = '3' + shortage
            ask.applies = lambda ctx, s=shortage: invites_with_shortage(ctx, s)
            ask.meaning.action = 'minor_shortage_invitation'
            ask.meaning.nature = ['artificial']
            ask.meaning.acts = ['invite']
            ask.meaning.short_suit = shortage
            ask.meaning.invite_acceptance = {'mode':'best_minor_controls',
                                             'normal_suits':['C','D'], 'minimum':14.5}
            ask.description = 'Five-five minors, invitational strength; named major is a singleton.'

            for minor in 'CD':
                for level, action in ((4, 'reject'), (5, 'accept')):
                    placement = self.call('minor_shortage_' + shortage.lower()
                                          + '_' + action + '_' + minor.lower())
                    placement.when = '1NP3' + shortage + 'P'
                    placement.bid = str(level) + minor
                    placement.applies = (lambda ctx, m=minor, a=action:
                                         ctx.hand is not None and best_minor(ctx) == m
                                         and accepts_invitation(ctx) == (a == 'accept')
                                         and (a == 'reject' or not all(has_major_stopper(ctx, s) for s in 'HS')))
                    placement.meaning.action = 'minor_shortage_' + action
                    placement.meaning.nature = ['natural']
                    placement.meaning.acts = [action, 'final_placement']
                    placement.meaning.target_suit = minor
                    placement.meaning.purpose_completed = True
                    placement.description = 'Control quality decides whether to play four or five of the better minor.'

            notrump = self.call('minor_shortage_three_notrump_' + shortage.lower())
            notrump.when = '1NP3' + shortage + 'P'
            notrump.bid = '3NT'
            notrump.applies = lambda ctx: (ctx.hand is not None and accepts_invitation(ctx)
                                          and all(has_major_stopper(ctx, s) for s in 'HS'))
            notrump.meaning.action = 'minor_shortage_accept_notrump'
            notrump.meaning.nature = ['natural']
            notrump.meaning.acts = ['accept', 'final_placement']
            notrump.meaning.target_suit = 'N'
            notrump.meaning.purpose_completed = True
            notrump.description = 'Accept in 3NT when controls and both major stoppers are sufficient.'
