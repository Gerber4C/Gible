# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_1_requires(ctx):
    return (ctx.state.exists('agreed_suit', suit='H') and not (ctx.state.exists('keycard_context', status='pending')) and not (ctx.state.exists('final_contract')))
def cs_1_applies(ctx):
    return (ctx.hand.hcp >= 16 and ctx.hand.length('H') >= 6 and (ctx.hand.length('D') == 0))
def cs_2_requires(ctx):
    return (ctx.state.exists('keycard_context', method='exclusion_1430', trump_suit='H', excluded_suit='D', status='pending') and not (ctx.state.exists('keycard_response', method='exclusion_1430')))
def cs_2_applies(ctx):
    return ctx.hand.keycard_count('H', excluded_suit='D') in [1, 4]
def cs_3_requires(ctx):
    return (ctx.state.exists('keycard_context', method='exclusion_1430', trump_suit='H', excluded_suit='D', status='pending') and not (ctx.state.exists('keycard_response', method='exclusion_1430')))
def cs_3_applies(ctx):
    return ctx.hand.keycard_count('H', excluded_suit='D') in [0, 3]
def cs_4_requires(ctx):
    return (ctx.state.exists('keycard_context', method='exclusion_1430', trump_suit='H', excluded_suit='D', status='pending') and not (ctx.state.exists('keycard_response', method='exclusion_1430')))
def cs_4_applies(ctx):
    return ctx.hand.keycard_count('H', excluded_suit='D') == 2 and not ctx.hand.contains_rank('H', 'Q')

class MeowExclusionKeycardGadget(Gadget):
    id = 'meow_exclusion_keycard'
    namespace = 'meow_2over1'
    name = 'Meow Exclusion Keycard'
    version = '0.1.0'
    description = "Exclusion keycard asks that ignore the ace of the asker's void suit."
    system_notes = 'With hearts agreed, a diamond-void hand can jump to 5D to ask for heart keycards excluding the diamond ace.\n'
    author = Author('Meow Li')

    def build(self):

        frame = self.frame('frame_1')
        frame.frame_type = 'exclusion_1430'
        frame.when = '1NP2DP3HP'
        frame.seats = [1, 2, 3, 4]
        frame.source_call = '5D'
        frame.description = 'Exclusion keycard frame after 5D asks for heart keycards excluding diamonds.'
        frame.system_notes = '5D opens a keycard-answer frame for hearts while excluding the diamond ace.'
        frame.variables = {'method': 'exclusion_1430', 'trump_suit': 'H', 'excluded_suit': 'D', 'asker': 'actor', 'responder': 'partner'}
        frame.obligation = {'actor': 'responder', 'action': 'answer_frame', 'capabilities': ['answer_frame', 'keycard_response']}
        frame.stages = ['keycard_response', 'queen_or_king_continuation', 'final_placement']
        frame.allowed_continuations = ['keycard_response', 'queen_ask', 'specific_king_ask', 'signoff', 'slam_placement']
        frame.break_conditions = ['undefined_interference_without_policy']
        frame.closes = ['*']
        frame.close_on_actions = ['place_contract', 'pass_final_contract', 'signoff']
        frame.close_on_act_types = ['final_placement', 'signoff']

        call = self.call('cs_1')
        call.when = '*'
        call.bid = '5D'
        call.requires = cs_1_requires
        call.applies = cs_1_applies
        call.capabilities = ('start_frame', 'keycard_ask', 'slam_inquiry')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['inquiry', 'keycard_asking', 'shortness_showing', 'context_initiating']
        call.meaning.action = 'exclusion_1430'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.excluded_suit = 'D'
        effect = call.effect('keycard_context')
        effect.trump_suit = 'H'
        effect.method = 'exclusion_1430'
        effect.excluded_suit = 'D'
        effect.status = 'pending'
        call.description = 'Asker bids 5D as Exclusion keycard for hearts, excluding the diamond ace.'
        call.system_notes = 'With hearts agreed and diamond void, 5D asks for heart keycards excluding the diamond ace.'

        call = self.call('cs_2')
        call.when = '*'
        call.bid = '5H'
        call.requires = cs_2_requires
        call.applies = cs_2_applies
        call.capabilities = ('answer_frame', 'keycard_response')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['relay_response']
        call.meaning.action = 'keycard_response'
        call.meaning.alertable = True
        call.meaning.keycard_range = [1, 4]
        call.meaning.excluded_suit = 'D'
        effect = call.effect('keycard_response')
        effect.trump_suit = 'H'
        effect.method = 'exclusion_1430'
        effect.excluded_suit = 'D'
        effect.response = 'one_or_four'
        call.description = 'Responder to Exclusion answers 5H, showing 1 or 4 keycards outside diamonds.'
        call.system_notes = 'Over 5D Exclusion for hearts, 5H shows 1 or 4 keycards excluding the diamond ace.'

        call = self.call('cs_3')
        call.when = '*'
        call.bid = '5S'
        call.requires = cs_3_requires
        call.applies = cs_3_applies
        call.capabilities = ('answer_frame', 'keycard_response')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['relay_response']
        call.meaning.action = 'keycard_response'
        call.meaning.alertable = True
        call.meaning.keycard_range = [0, 3]
        call.meaning.excluded_suit = 'D'
        effect = call.effect('keycard_response')
        effect.trump_suit = 'H'
        effect.method = 'exclusion_1430'
        effect.excluded_suit = 'D'
        effect.response = 'zero_or_three'
        call.description = 'Responder to Exclusion answers 5S, showing 0 or 3 keycards outside diamonds.'
        call.system_notes = 'Over 5D Exclusion for hearts, 5S shows 0 or 3 keycards excluding the diamond ace.'

        call = self.call('cs_4')
        call.when = '*'
        call.bid = '5N'
        call.requires = cs_4_requires
        call.applies = cs_4_applies
        call.capabilities = ('answer_frame', 'keycard_response')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['relay_response']
        call.meaning.action = 'keycard_response'
        call.meaning.alertable = True
        call.meaning.keycard_count = 2
        call.meaning.trump_queen = False
        call.meaning.excluded_suit = 'D'
        effect = call.effect('keycard_response')
        effect.trump_suit = 'H'
        effect.method = 'exclusion_1430'
        effect.excluded_suit = 'D'
        effect.response = 'two_without_queen'
        call.description = 'Responder to Exclusion answers 5N, showing two keycards outside diamonds without the heart queen.'
        call.system_notes = 'Over 5D Exclusion for hearts, 5N shows 2 keycards excluding the diamond ace and denies the heart queen.'
