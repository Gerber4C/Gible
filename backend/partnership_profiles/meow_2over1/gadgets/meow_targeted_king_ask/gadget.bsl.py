# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_1_requires(ctx):
    return (ctx.state.exists('keycard_response', method='1430', trump_suit='H', response='zero_or_three') and not (ctx.state.exists('targeted_king_ask', status='pending')) and not (ctx.state.exists('final_contract')))
def cs_1_applies(ctx):
    return (ctx.hand.hcp >= 18 and ctx.hand.length('H') >= 6 and (ctx.hand.keycard_count('H') == 3))
def cs_2_requires(ctx):
    return (ctx.state.exists('targeted_king_ask', trump_suit='H', target_suit='D', rank='K', status='pending') and not (ctx.state.exists('targeted_king_response', target_suit='D', rank='K')))
def cs_2_applies(ctx):
    return (ctx.hand.contains_rank('D', 'K'))
def cs_3_requires(ctx):
    return (ctx.state.exists('targeted_king_response', trump_suit='H', target_suit='D', rank='K', status='yes') and not (ctx.state.exists('final_contract')))
def cs_3_applies(ctx):
    return (ctx.hand.hcp >= 18 and ctx.hand.length('H') >= 6)
def cs_4_requires(ctx):
    return ctx.state.exists('final_contract', source='targeted_king_ask')
def cs_4_applies(ctx):
    return (ctx.state.exists('final_contract', source='targeted_king_ask'))

class MeowTargetedKingAskGadget(Gadget):
    id = 'meow_targeted_king_ask'
    namespace = 'meow_2over1'
    name = 'Meow Targeted King Ask'
    version = '0.1.0'
    description = 'Targeted follow-up asks for a named king after keycard information is available.'
    system_notes = 'After keycard information, 5N can ask for the diamond king in the benchmark heart-slam route.\n'
    author = Author('Meow Li')

    def build(self):

        frame = self.frame('frame_1')
        frame.frame_type = 'targeted_king_ask'
        frame.when = '1NP2DP3HP4NP5DP'
        frame.seats = [1, 2, 3, 4]
        frame.source_call = '5N'
        frame.description = 'Targeted diamond-king ask frame after 5N in the benchmark heart RKCB route.'
        frame.system_notes = '5N asks for a named king, responder answers, and the asker places the final contract.'
        frame.variables = {'trump_suit': 'H', 'target_suit': 'D', 'target_rank': 'K', 'asker': 'actor', 'responder': 'partner'}
        frame.obligation = {'actor': 'responder', 'action': 'answer_frame', 'capabilities': ['answer_frame', 'specific_king_response']}
        frame.stages = ['targeted_response', 'final_placement']
        frame.allowed_continuations = ['targeted_king_response', 'signoff', 'slam_placement']
        frame.break_conditions = ['undefined_interference_without_policy']
        frame.closes = ['*']
        frame.close_on_actions = ['place_contract', 'pass_final_contract', 'signoff']
        frame.close_on_act_types = ['final_placement', 'signoff']

        call = self.call('cs_1')
        call.when = '*'
        call.bid = '5N'
        call.requires = cs_1_requires
        call.applies = cs_1_applies
        call.capabilities = ('start_frame', 'specific_king_ask', 'slam_inquiry')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['inquiry', 'honor_asking']
        call.meaning.action = 'targeted_king_ask'
        call.meaning.target_suit = 'D'
        call.meaning.alertable = True
        call.meaning.target_rank = 'K'
        call.meaning.trump_suit = 'H'
        effect = call.effect('targeted_king_ask')
        effect.trump_suit = 'H'
        effect.target_suit = 'D'
        effect.rank = 'K'
        effect.status = 'pending'
        effect = call.effect('all_keycards_known')
        effect.trump_suit = 'H'
        effect.status = 'yes'
        call.description = 'Asker bids 5N to ask specifically for the diamond king after a 1430 zero-or-three response.'
        call.system_notes = 'After 4N-5D in a heart RKCB auction, 5N asks whether partner holds the diamond king.'

        call = self.call('cs_2')
        call.when = '*'
        call.bid = '6D'
        call.requires = cs_2_requires
        call.applies = cs_2_applies
        call.capabilities = ('answer_frame', 'specific_king_response')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['relay_response', 'control_showing']
        call.meaning.action = 'targeted_king_response'
        call.meaning.target_suit = 'D'
        call.meaning.alertable = True
        call.meaning.target_rank = 'K'
        effect = call.effect('targeted_king_response')
        effect.trump_suit = 'H'
        effect.target_suit = 'D'
        effect.rank = 'K'
        effect.status = 'yes'
        call.description = 'Responder bids 6D to show the diamond king over the targeted king ask.'
        call.system_notes = 'Over the targeted 5N ask, 6D shows the diamond king.'

        call = self.call('cs_3')
        call.when = '*'
        call.bid = '7H'
        call.requires = cs_3_requires
        call.applies = cs_3_applies
        call.capabilities = ('place_contract', 'slam_placement')
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'H'
        call.meaning.level = 7
        effect = call.effect('final_contract')
        effect.target_suit = 'H'
        effect.level = 7
        effect.source = 'targeted_king_ask'
        call.description = 'Asker places the heart grand slam after the diamond king is confirmed.'
        call.system_notes = '7H is final placement after partner shows the diamond king in the heart-slam route.'

        call = self.call('cs_4')
        call.when = '*'
        call.bid = 'P'
        call.requires = cs_4_requires
        call.applies = cs_4_applies
        call.capabilities = ('place_contract', 'pass_final_contract')
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'pass_final_contract'
        call.description = 'Partner passes after the targeted-king route places a final contract.'
        call.system_notes = 'After 7H is placed, partner passes to end the auction.'
