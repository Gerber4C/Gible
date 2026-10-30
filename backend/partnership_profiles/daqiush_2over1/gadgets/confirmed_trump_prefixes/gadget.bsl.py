# Confirmed *historical* prefixes. The responder's earlier route choices are
# not auto-selected until their hand criteria or simulation policy are authored.


def await_route_definition(ctx):
    return False


class ConfirmedTrumpPrefixes(Gadget):
    id = 'confirmed_trump_prefixes'
    namespace = 'daqiush_2over1'
    name = 'Confirmed minor-trump reference prefixes'
    author = Author('Daqiush')

    def build(self):
        stages = (
            ('minor_stayman_diamonds', '1NP2CP2DP4CP4DP', '4H', 'shows_four_diamonds', 'D'),
            ('minor_stayman_diamonds_h', '1NP2CP2HP4CP4DP', '4H', 'shows_four_diamonds', 'D'),
            ('minor_stayman_diamonds_s', '1NP2CP2SP4CP4DP', '4H', 'shows_four_diamonds', 'D'),
        )
        for id, prefix, bid, action, target in stages:
            call = self.call(id)
            call.when = prefix
            call.bid = bid
            call.applies = await_route_definition
            call.meaning.action = action
            call.meaning.historical_only = True
            call.meaning.nature = ['natural' if action == 'natural_suit' else 'artificial']
            call.meaning.acts = ['descriptive']
            if target:
                call.meaning.target_suit = target
            if id == 'diamond_fit':
                call.meaning.agreed_suit = 'D'
                call.effect('agreed_suit').suit = 'D'
            call.description = 'Owner-confirmed historical meaning; initiation not yet automatic.'

        for id, prefix, suit in (
            ('minor_stayman_club_fit', '1NP2CP2DP4CP4DP', 'C'),
            ('minor_stayman_diamond_fit', '1NP2CP2DP4CP4DP4HP', 'D'),
            ('minor_stayman_club_fit_h', '1NP2CP2HP4CP4DP', 'C'),
            ('minor_stayman_diamond_fit_h', '1NP2CP2HP4CP4DP4HP', 'D'),
            ('minor_stayman_club_fit_s', '1NP2CP2SP4CP4DP', 'C'),
            ('minor_stayman_diamond_fit_s', '1NP2CP2SP4CP4DP4HP', 'D'),
        ):
            call = self.call(id)
            call.when = prefix
            call.bid = '4S'
            call.applies = await_route_definition
            call.meaning.action = 'minor_fit'
            call.meaning.historical_only = True
            call.meaning.nature = ['artificial']
            call.meaning.acts = ['descriptive']
            call.meaning.agreed_suit = suit
            call.effect('agreed_suit').suit = suit
            call.description = 'Both partners have shown four cards; this minor is now the reference trump.'

        ask = self.call('diamond_fit_keycard_after_natural_hearts')
        ask.when = '1NP2DP2HP3DP3SP4HP'
        ask.bid = '4NT'
        ask.applies = lambda ctx: ctx.hand is not None and ctx.hand.hcp >= 16
        ask.meaning.action = 'rkcb_1430'
        ask.meaning.historical_only = False
        ask.meaning.nature = ['artificial']
        ask.meaning.acts = ['inquiry', 'keycard_asking']
        ask.meaning.target_suit = 'D'
        ask.meaning.agreed_suit = 'D'
        ask.effect('agreed_suit').suit = 'D'
        keycards = ask.effect('keycard_context')
        keycards.trump_suit = 'D'
        keycards.ask_call = '4N'
        keycards.method = 'rkcb_1430'
        keycards.status = 'pending'
        ask.description = 'A maximum asks diamond keycards despite the natural four-heart suggestion.'
