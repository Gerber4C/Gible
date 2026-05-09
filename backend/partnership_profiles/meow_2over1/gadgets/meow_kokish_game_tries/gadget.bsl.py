# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_1_requires(ctx):
    return ctx.state.exists('agreed_suit', suit='S')
def cs_1_applies(ctx):
    return (ctx.hand.hcp >= 14 and ((ctx.hand.length('D') >= 3) and ctx.hand.contains_rank('D', 'Q')))
def cs_2_requires(ctx):
    return ctx.state.exists('game_try', game_try_type='help_suit', target_suit='D', agreed_suit='S', status='pending')
def cs_2_applies(ctx):
    return (((ctx.hand.honor_count('D', ['A', 'K', 'Q', 'J']) >= 1) or (ctx.hand.length('D') <= 1)) and ctx.hand.hcp >= 9)
def cs_3_requires(ctx):
    return ctx.state.exists('agreed_suit', suit='S')
def cs_3_applies(ctx):
    return (ctx.hand.hcp >= 14)
def cs_4_requires(ctx):
    return ctx.state.exists('agreed_suit', suit='S')
def cs_4_applies(ctx):
    return (ctx.hand.hcp >= 14 and (ctx.hand.honor_count('S', ['A', 'K', 'Q']) == 0))
def cs_5_requires(ctx):
    return ctx.state.exists('final_contract', target_suit='S', level=4)
def cs_5_applies(ctx):
    return (ctx.state.exists('final_contract', target_suit='S', level=4))
def cs_6_requires(ctx):
    return ctx.state.exists('agreed_suit', suit='H')
def cs_6_applies(ctx):
    return (ctx.hand.hcp >= 14)
def cs_7_requires(ctx):
    return ctx.state.exists('game_try', game_try_type='help_suit', ask_scope='any_help', agreed_suit='H', status='pending')
def cs_7_applies(ctx):
    return (((ctx.hand.honor_count('S', ['A', 'K', 'Q', 'J']) >= 1) or (ctx.hand.length('S') <= 1)) and ctx.hand.hcp >= 8)
def cs_8_requires(ctx):
    return ctx.state.exists('game_try_response', game_try_type='help_suit', target_suit='S', agreed_suit='H', status='accepted')
def cs_8_applies(ctx):
    return (ctx.hand.hcp >= 14)
def cs_9_requires(ctx):
    return ctx.state.exists('agreed_suit', suit='H')
def cs_9_applies(ctx):
    return (ctx.hand.hcp >= 14 and (ctx.hand.honor_count('H', ['A', 'K', 'Q']) == 0))
def cs_10_requires(ctx):
    return ctx.state.exists('final_contract', target_suit='H', level=4)
def cs_10_applies(ctx):
    return (ctx.state.exists('final_contract', target_suit='H', level=4))

class MeowKokishGameTriesGadget(Gadget):
    id = 'meow_kokish_game_tries'
    namespace = 'meow_2over1'
    name = 'Meow Kokish Game Tries'
    version = '0.1.0'
    description = 'Standalone Kokish/help-suit game-try Gadget after a simple major raise.\n'
    author = Author('Meow Li')

    def build(self):

        call = self.call('cs_1')
        call.when = '1SP2SP'
        call.seats = [1, 2]
        call.bid = '3D'
        call.requires = cs_1_requires
        call.applies = cs_1_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['invitation', 'inquiry']
        call.meaning.action = 'help_suit_game_try'
        call.meaning.target_suit = 'D'
        call.meaning.agreed_suit = 'S'
        effect = call.effect('game_try')
        effect.game_try_type = 'help_suit'
        effect.target_suit = 'D'
        effect.agreed_suit = 'S'
        effect.status = 'pending'
        call.description = 'Opener asks for diamond help after 1S-2S.'
        call.system_notes = 'After 1S-2S, 3D asks whether responder can help in diamonds.'

        call = self.call('cs_2')
        call.when = '1SP2SP3DP'
        call.seats = [1, 2]
        call.bid = '4S'
        call.requires = cs_2_requires
        call.applies = cs_2_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'accept_game_try'
        call.meaning.target_suit = 'S'
        call.meaning.level = 4
        effect = call.effect('final_contract')
        effect.target_suit = 'S'
        effect.level = 4
        call.description = 'Responder accepts the diamond help-suit game try by bidding 4S.'
        call.system_notes = 'After a diamond help-suit game try, 4S accepts and places the game.'

        call = self.call('cs_3')
        call.when = '1SP2SP'
        call.seats = [1, 2]
        call.bid = '2N'
        call.requires = cs_3_requires
        call.applies = cs_3_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['invitation', 'inquiry']
        call.meaning.action = 'help_suit_game_try'
        call.meaning.alertable = True
        call.meaning.ask_scope = 'any_help'
        call.meaning.agreed_suit = 'S'
        call.description = 'Opener asks generally where responder can help after 1S-2S.'
        call.system_notes = 'After 1S-2S, 2N asks where responder can offer help.'

        call = self.call('cs_4')
        call.when = '1SP2SP'
        call.seats = [1, 2]
        call.bid = '3S'
        call.requires = cs_4_requires
        call.applies = cs_4_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['invitation', 'inquiry']
        call.meaning.action = 'trump_help_game_try'
        call.meaning.target_suit = 'S'
        call.description = 'Opener asks for trump help after 1S-2S.'
        call.system_notes = 'After 1S-2S, 3S asks whether responder can help in trumps.'

        call = self.call('cs_5')
        call.when = '1SP2SP3DP4SP'
        call.seats = [1, 2]
        call.bid = 'P'
        call.requires = cs_5_requires
        call.applies = cs_5_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'pass_final_contract'
        call.description = 'Opener passes after responder accepts the help-suit game try and the next hand passes.'
        call.system_notes = 'After 1S-2S-3D-4S, opener passes to end the auction.'

        call = self.call('cs_6')
        call.when = '1HP2HP'
        call.seats = [1, 2]
        call.bid = '2S'
        call.requires = cs_6_requires
        call.applies = cs_6_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['invitation', 'inquiry']
        call.meaning.action = 'help_suit_game_try'
        call.meaning.alertable = True
        call.meaning.ask_scope = 'any_help'
        call.meaning.agreed_suit = 'H'
        effect = call.effect('game_try')
        effect.game_try_type = 'help_suit'
        effect.ask_scope = 'any_help'
        effect.agreed_suit = 'H'
        effect.status = 'pending'
        call.description = 'Opener asks generally where responder can help after 1H-2H.'
        call.system_notes = 'After 1H-2H, 2S asks where responder can offer help.'

        call = self.call('cs_7')
        call.when = '1HP2HP2SP'
        call.seats = [1, 2]
        call.bid = '2N'
        call.requires = cs_7_requires
        call.applies = cs_7_applies
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'game_try_response'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.agreed_suit = 'H'
        effect = call.effect('game_try_response')
        effect.game_try_type = 'help_suit'
        effect.target_suit = 'S'
        effect.agreed_suit = 'H'
        effect.status = 'accepted'
        call.description = 'Responder shows spade help after the heart any-help game try.'
        call.system_notes = 'After 1H-2H-2S, 2N shows help in spades.'

        call = self.call('cs_8')
        call.when = '1HP2HP2SP2NP'
        call.seats = [1, 2]
        call.bid = '4H'
        call.requires = cs_8_requires
        call.applies = cs_8_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'accept_game_try'
        call.meaning.target_suit = 'H'
        call.meaning.level = 4
        effect = call.effect('final_contract')
        effect.target_suit = 'H'
        effect.level = 4
        call.description = 'Opener places the heart game after responder shows spade help.'
        call.system_notes = 'After 1H-2H-2S-2N, 4H places the game.'

        call = self.call('cs_9')
        call.when = '1HP2HP'
        call.seats = [1, 2]
        call.bid = '2N'
        call.requires = cs_9_requires
        call.applies = cs_9_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['invitation', 'inquiry']
        call.meaning.action = 'trump_help_game_try'
        call.meaning.target_suit = 'H'
        call.description = 'Opener asks for trump help after 1H-2H.'
        call.system_notes = 'After 1H-2H, 2N is a help-suit game try in hearts.'

        call = self.call('cs_10')
        call.when = '1HP2HP2SP2NP4HP'
        call.seats = [1, 2]
        call.bid = 'P'
        call.requires = cs_10_requires
        call.applies = cs_10_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'pass_final_contract'
        call.description = 'Opener passes after responder accepts the heart help-suit game try and the next hand passes.'
        call.system_notes = "After 1H-2H-2S-2N-4H, opener's partner passes to end the auction."
