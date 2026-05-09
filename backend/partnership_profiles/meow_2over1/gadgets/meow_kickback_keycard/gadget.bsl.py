# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_1_requires(ctx):
    return (ctx.state.exists('agreed_suit', suit='H') and not (ctx.state.exists('keycard_context', status='pending')) and not (ctx.state.exists('final_contract')))
def cs_1_applies(ctx):
    return (ctx.hand.hcp >= 18 and ctx.hand.length('H') >= 6 and not ((ctx.hand.contains_rank('D', 'A') or ctx.hand.contains_rank('D', 'K') or (ctx.hand.length('D') <= 1))))
def cs_2_requires(ctx):
    return (ctx.state.exists('keycard_context', method='kickback_1430', trump_suit='H', status='pending') and not (ctx.state.exists('keycard_response', method='kickback_1430')))
def cs_2_applies(ctx):
    return ((ctx.hand.keycard_count('H') in [1, 4]))
def cs_3_requires(ctx):
    return (ctx.state.exists('keycard_context', method='kickback_1430', trump_suit='H', status='pending') and not (ctx.state.exists('keycard_response', method='kickback_1430')))
def cs_3_applies(ctx):
    return ((ctx.hand.keycard_count('H') in [0, 3]))
def cs_4_requires(ctx):
    return (ctx.state.exists('keycard_context', method='kickback_1430', trump_suit='H', status='pending') and not (ctx.state.exists('keycard_response', method='kickback_1430')))
def cs_4_applies(ctx):
    return ((ctx.hand.keycard_count('H') == 2) and not (ctx.hand.contains_rank('H', 'Q')))
def cs_5_requires(ctx):
    return (ctx.state.exists('keycard_context', method='kickback_1430', trump_suit='H', status='pending') and not (ctx.state.exists('keycard_response', method='kickback_1430')))
def cs_5_applies(ctx):
    return ((ctx.hand.keycard_count('H') == 2) and ctx.hand.contains_rank('H', 'Q'))

class MeowKickbackKeycardGadget(Gadget):
    id = 'meow_kickback_keycard'
    namespace = 'meow_2over1'
    name = 'Meow Kickback Keycard'
    version = '0.1.0'
    description = 'Kickback keycard asks using the four-level step above the agreed trump suit.'
    system_notes = 'When hearts are agreed, 4S is Kickback keycard for hearts in this benchmark slice.\n'
    author = Author('Meow Li')

    def build(self):

        frame = self.frame('frame_1')
        frame.frame_type = 'kickback_1430'
        frame.when = '1NP2DP3HP'
        frame.seats = [1, 2, 3, 4]
        frame.source_call = '4S'
        frame.description = 'Kickback 1430 frame after 4S asks for heart keycards.'
        frame.system_notes = 'The step above four hearts opens a keycard-answer frame for hearts.'
        frame.variables = {'method': 'kickback_1430', 'trump_suit': 'H', 'asker': 'actor', 'responder': 'partner'}
        frame.obligation = {'actor': 'responder', 'action': 'answer_frame', 'capabilities': ['answer_frame', 'keycard_response']}
        frame.stages = ['keycard_response', 'queen_or_king_continuation', 'final_placement']
        frame.allowed_continuations = ['keycard_response', 'queen_ask', 'specific_king_ask', 'signoff', 'slam_placement']
        frame.break_conditions = ['undefined_interference_without_policy']
        frame.closes = ['*']
        frame.close_on_actions = ['place_contract', 'pass_final_contract', 'signoff']
        frame.close_on_act_types = ['final_placement', 'signoff']

        call = self.call('cs_1')
        call.when = '*'
        call.bid = '4S'
        call.requires = cs_1_requires
        call.applies = cs_1_applies
        call.capabilities = ('start_frame', 'keycard_ask', 'slam_inquiry')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['inquiry', 'keycard_asking', 'context_initiating']
        call.meaning.action = 'kickback_1430'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        effect = call.effect('keycard_context')
        effect.trump_suit = 'H'
        effect.ask_call = '4S'
        effect.method = 'kickback_1430'
        effect.status = 'pending'
        call.description = 'Asker bids 4S as Kickback keycard for hearts.'
        call.system_notes = 'With hearts agreed, 4S asks for keycards using Kickback.'

        call = self.call('cs_2')
        call.when = '*'
        call.bid = StepAfterState('keycard_context')
        call.requires = cs_2_requires
        call.applies = cs_2_applies
        call.capabilities = ('answer_frame', 'keycard_response')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['relay_response']
        call.meaning.action = 'keycard_response'
        call.meaning.alertable = True
        call.meaning.keycard_range = [1, 4]
        effect = call.effect('keycard_response')
        effect.trump_suit = 'H'
        effect.method = 'kickback_1430'
        effect.response = 'one_or_four'
        call.description = 'Responder to heart Kickback answers 4N, showing 1 or 4 keycards.'
        call.system_notes = 'Over heart Kickback, 4N is the first 1430 step, showing 1 or 4 keycards.'

        call = self.call('cs_3')
        call.when = '*'
        call.bid = StepAfterState('keycard_context', step=2)
        call.requires = cs_3_requires
        call.applies = cs_3_applies
        call.capabilities = ('answer_frame', 'keycard_response')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['relay_response']
        call.meaning.action = 'keycard_response'
        call.meaning.alertable = True
        call.meaning.keycard_range = [0, 3]
        effect = call.effect('keycard_response')
        effect.trump_suit = 'H'
        effect.method = 'kickback_1430'
        effect.response = 'zero_or_three'
        call.description = 'Responder to heart Kickback answers 5C, showing 0 or 3 keycards.'
        call.system_notes = 'Over heart Kickback, 5C is the second 1430 step, showing 0 or 3 keycards.'

        call = self.call('cs_4')
        call.when = '*'
        call.bid = StepAfterState('keycard_context', step=3)
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
        effect.trump_suit = 'H'
        effect.method = 'kickback_1430'
        effect.response = 'two_without_queen'
        call.description = 'Responder to heart Kickback answers 5D, showing two keycards without the heart queen.'
        call.system_notes = 'Over heart Kickback, 5D shows 2 keycards without the heart queen.'

        call = self.call('cs_5')
        call.when = '*'
        call.bid = StepAfterState('keycard_context', step=4)
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
        effect.trump_suit = 'H'
        effect.method = 'kickback_1430'
        effect.response = 'two_with_queen'
        call.description = 'Responder to heart Kickback answers 5H, showing two keycards with the heart queen.'
        call.system_notes = 'Over heart Kickback, 5H shows 2 keycards with the heart queen.'
