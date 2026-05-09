# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_1_requires(ctx):
    return (ctx.state.exists('agreed_suit', suit='D') and not (ctx.state.exists('keycard_context', status='pending')) and not (ctx.state.exists('final_contract')))
def cs_1_applies(ctx):
    return (ctx.hand.hcp >= 12 and ctx.hand.length('D') >= 6)
def cs_2_requires(ctx):
    return (ctx.state.exists('keycard_context', method='minorwood_1430', trump_suit='D', status='pending') and not (ctx.state.exists('keycard_response', method='minorwood_1430')))
def cs_2_applies(ctx):
    return ((ctx.hand.keycard_count('D') in [1, 4]))
def cs_3_requires(ctx):
    return (ctx.state.exists('keycard_context', method='minorwood_1430', trump_suit='D', status='pending') and not (ctx.state.exists('keycard_response', method='minorwood_1430')))
def cs_3_applies(ctx):
    return ((ctx.hand.keycard_count('D') in [0, 3]))
def cs_4_requires(ctx):
    return (ctx.state.exists('keycard_context', method='minorwood_1430', trump_suit='D', status='pending') and not (ctx.state.exists('keycard_response', method='minorwood_1430')))
def cs_4_applies(ctx):
    return ((ctx.hand.keycard_count('D') == 2) and not (ctx.hand.contains_rank('D', 'Q')))
def cs_5_requires(ctx):
    return (ctx.state.exists('keycard_context', method='minorwood_1430', trump_suit='D', status='pending') and not (ctx.state.exists('keycard_response', method='minorwood_1430')))
def cs_5_applies(ctx):
    return ((ctx.hand.keycard_count('D') == 2) and ctx.hand.contains_rank('D', 'Q'))

class MeowMinorwoodKeycardGadget(Gadget):
    id = 'meow_minorwood_keycard'
    namespace = 'meow_2over1'
    name = 'Meow Minorwood Keycard'
    version = '0.1.0'
    description = 'Minorwood keycard asks for agreed minor suits.'
    system_notes = 'When diamonds are agreed, 4D is Minorwood keycard for diamonds in this benchmark slice.\n'
    author = Author('Meow Li')

    def build(self):

        frame = self.frame('frame_1')
        frame.frame_type = 'minorwood_1430'
        frame.when = '1NP2NP3CP'
        frame.seats = [1, 2, 3, 4]
        frame.source_call = '4D'
        frame.description = 'Minorwood 1430 frame after 4D asks for diamond keycards.'
        frame.system_notes = '4D opens a diamond keycard-answer frame when diamonds are agreed.'
        frame.variables = {'method': 'minorwood_1430', 'trump_suit': 'D', 'asker': 'actor', 'responder': 'partner'}
        frame.obligation = {'actor': 'responder', 'action': 'answer_frame', 'capabilities': ['answer_frame', 'keycard_response']}
        frame.stages = ['keycard_response', 'queen_or_king_continuation', 'final_placement']
        frame.allowed_continuations = ['keycard_response', 'queen_ask', 'specific_king_ask', 'signoff', 'slam_placement']
        frame.break_conditions = ['undefined_interference_without_policy']
        frame.closes = ['*']
        frame.close_on_actions = ['place_contract', 'pass_final_contract', 'signoff']
        frame.close_on_act_types = ['final_placement', 'signoff']

        call = self.call('cs_1')
        call.when = '*'
        call.bid = '4D'
        call.requires = cs_1_requires
        call.applies = cs_1_applies
        call.capabilities = ('start_frame', 'keycard_ask', 'slam_inquiry')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['inquiry', 'keycard_asking', 'context_initiating']
        call.meaning.action = 'minorwood_1430'
        call.meaning.target_suit = 'D'
        call.meaning.alertable = True
        effect = call.effect('keycard_context')
        effect.trump_suit = 'D'
        effect.method = 'minorwood_1430'
        effect.status = 'pending'
        call.description = 'Asker bids 4D as Minorwood keycard for diamonds.'
        call.system_notes = 'With diamonds agreed, 4D asks for diamond keycards using 1430 steps.'

        call = self.call('cs_2')
        call.when = '*'
        call.bid = '4H'
        call.requires = cs_2_requires
        call.applies = cs_2_applies
        call.capabilities = ('answer_frame', 'keycard_response')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['relay_response']
        call.meaning.action = 'keycard_response'
        call.meaning.alertable = True
        call.meaning.keycard_range = [1, 4]
        effect = call.effect('keycard_response')
        effect.trump_suit = 'D'
        effect.method = 'minorwood_1430'
        effect.response = 'one_or_four'
        call.description = 'Responder to diamond Minorwood answers 4H, showing 1 or 4 keycards.'
        call.system_notes = 'Over 4D Minorwood, 4H shows 1 or 4 keycards.'

        call = self.call('cs_3')
        call.when = '*'
        call.bid = '4S'
        call.requires = cs_3_requires
        call.applies = cs_3_applies
        call.capabilities = ('answer_frame', 'keycard_response')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['relay_response']
        call.meaning.action = 'keycard_response'
        call.meaning.alertable = True
        call.meaning.keycard_range = [0, 3]
        effect = call.effect('keycard_response')
        effect.trump_suit = 'D'
        effect.method = 'minorwood_1430'
        effect.response = 'zero_or_three'
        call.description = 'Responder to diamond Minorwood answers 4S, showing 0 or 3 keycards.'
        call.system_notes = 'Over 4D Minorwood, 4S shows 0 or 3 keycards.'

        call = self.call('cs_4')
        call.when = '*'
        call.bid = '4N'
        call.requires = cs_4_requires
        call.applies = cs_4_applies
        call.capabilities = ('answer_frame', 'keycard_response')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['relay_response']
        call.meaning.action = 'keycard_response'
        call.meaning.alertable = True
        call.meaning.keycard_count = 2
        call.meaning.trump_queen = False
        effect = call.effect('keycard_response')
        effect.trump_suit = 'D'
        effect.method = 'minorwood_1430'
        effect.response = 'two_without_queen'
        call.description = 'Responder to diamond Minorwood answers 4N, showing two keycards without the diamond queen.'
        call.system_notes = 'Over 4D Minorwood, 4N shows 2 keycards without the diamond queen.'

        call = self.call('cs_5')
        call.when = '*'
        call.bid = '5C'
        call.requires = cs_5_requires
        call.applies = cs_5_applies
        call.capabilities = ('answer_frame', 'keycard_response')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['relay_response']
        call.meaning.action = 'keycard_response'
        call.meaning.alertable = True
        call.meaning.keycard_count = 2
        call.meaning.trump_queen = True
        effect = call.effect('keycard_response')
        effect.trump_suit = 'D'
        effect.method = 'minorwood_1430'
        effect.response = 'two_with_queen'
        call.description = 'Responder to diamond Minorwood answers 5C, showing two keycards with the diamond queen.'
        call.system_notes = 'Over 4D Minorwood, 5C shows 2 keycards with the diamond queen.'
