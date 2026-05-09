# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def ntb_1_applies(ctx):
    return (ctx.hand.hcp <= 8)
def ntb_2_applies(ctx):
    return (10 <= ctx.hand.hcp <= 15 and ctx.hand.length('S') <= 3 and ctx.hand.length('H') <= 3 and ctx.hand.length('D') <= 4 and ctx.hand.length('C') <= 4)
def ntb_3_applies(ctx):
    return (ctx.hand.length('D') >= 5 and ctx.hand.length('C') >= 5 and ctx.hand.hcp >= 10)
def ntb_4_applies(ctx):
    return (ctx.hand.length('S') >= 5 and ctx.hand.length('H') >= 5 and 8 <= ctx.hand.hcp <= 9)
def ntb_5_applies(ctx):
    return (ctx.hand.length('S') >= 5 and ctx.hand.length('H') >= 5 and ctx.hand.hcp >= 10)

class MeowNotrumpResponseBasicsGadget(Gadget):
    id = 'meow_notrump_response_basics'
    namespace = 'meow_2over1'
    name = 'Meow Notrump Response Basics'
    version = '0.1.0'
    description = 'Pass and general route hooks for responder after a 1N opening.'
    system_notes = 'After a 15-17 1N opening, responder may pass with weak or non-invitational hands. Detailed Stayman, transfer, Texas, Puppet, and slam tools remain separate gadgets.'
    author = Author('Meow Li')

    def build(self):

        call = self.call('ntb_1')
        call.when = '1NP'
        call.seats = [1, 2, 3, 4]
        call.bid = 'P'
        call.requires = {'op': 'state_exists', 'query': {'key': 'notrump_focus', 'status': 'active'}}
        call.applies = ntb_1_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'pass_notrump'
        call.meaning.target_suit = 'N'
        call.meaning.level = 1
        effect = call.effect('final_contract', owner='partnership')
        effect.level = 1
        effect.target_suit = 'N'
        effect.source = 'notrump_response_basics'
        call.description = 'Responder passes 1N with weak or non-invitational values when no preferred escape or constructive route is chosen.'
        call.system_notes = 'Responder may pass 1N with weak or non-invitational values.'

        call = self.call('ntb_2')
        call.when = '1NP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3N'
        call.requires = {'op': 'state_exists', 'query': {'key': 'notrump_focus', 'status': 'active'}}
        call.applies = ntb_2_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'N'
        call.meaning.level = 3
        effect = call.effect('final_contract', owner='partnership')
        effect.level = 3
        effect.target_suit = 'N'
        effect.source = 'direct_notrump_game'
        call.description = 'Responder bids 3N directly over 1N with game values and no major-suit inquiry need.'
        call.system_notes = 'After 1N, 3N is natural to play.'

        call = self.call('ntb_3')
        call.when = '1NP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3D'
        call.requires = {'op': 'state_exists', 'query': {'key': 'notrump_focus', 'status': 'active'}}
        call.applies = ntb_3_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'five_five_minors_game_force'
        call.meaning.alertable = True
        call.meaning.shape = '5-5 minors'
        effect = call.effect('responder.shape', owner='responder')
        effect.value = '5-5 minors'
        effect.source = 'direct_1n_response'
        effect = call.effect('forcing_status', owner='partnership')
        effect.status = 'game_forcing'
        effect.source = 'direct_1n_response'
        call.description = 'Responder shows both minors, at least 5-5, game forcing.'
        call.system_notes = 'After 1N, 3D shows 5-5 minors and game-forcing values.'

        call = self.call('ntb_4')
        call.when = '1NP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3H'
        call.requires = {'op': 'state_exists', 'query': {'key': 'notrump_focus', 'status': 'active'}}
        call.applies = ntb_4_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['descriptive', 'invitation']
        call.meaning.action = 'five_five_majors_invitational'
        call.meaning.alertable = True
        call.meaning.shape = '5-5 majors'
        effect = call.effect('responder.shape', owner='responder')
        effect.value = '5-5 majors'
        effect.source = 'direct_1n_response'
        effect = call.effect('game_interest', owner='partnership')
        effect.value = 'invite'
        effect.source = 'direct_1n_response'
        call.description = 'Responder shows both majors, at least 5-5, invitational.'
        call.system_notes = 'After 1N, 3H shows 5-5 majors and invitational values.'

        call = self.call('ntb_5')
        call.when = '1NP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3S'
        call.requires = {'op': 'state_exists', 'query': {'key': 'notrump_focus', 'status': 'active'}}
        call.applies = ntb_5_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['descriptive', 'forcing']
        call.meaning.action = 'five_five_majors_game_force'
        call.meaning.alertable = True
        call.meaning.shape = '5-5 majors'
        effect = call.effect('responder.shape', owner='responder')
        effect.value = '5-5 majors'
        effect.source = 'direct_1n_response'
        effect = call.effect('forcing_status', owner='partnership')
        effect.status = 'game_forcing'
        effect.source = 'direct_1n_response'
        call.description = 'Responder shows both majors, at least 5-5, game forcing.'
        call.system_notes = 'After 1N, 3S shows 5-5 majors and game-forcing values.'
