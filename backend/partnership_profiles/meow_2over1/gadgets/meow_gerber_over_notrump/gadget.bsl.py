# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_1_requires(ctx):
    if not ctx.state.exists('notrump_focus', status='active'):
        return False
    if ctx.state.exists('agreed_suit') or ctx.state.exists('ace_ask_context', status='pending') or ctx.state.exists('final_contract'):
        return False
    for procedure in ('transfer', 'stayman', 'puppet_stayman'):
        if ctx.state.exists(procedure, status='pending'):
            return False
        if ctx.state.exists(procedure, status='active'):
            return False
    return True
def cs_1_applies(ctx):
    return (ctx.hand.hcp >= 18 and ctx.hand.balanced == True)
def cs_2_requires(ctx):
    return (ctx.state.exists('ace_ask_context', method='gerber', status='pending') and not (ctx.state.exists('ace_ask_response', method='gerber')))
def cs_2_applies(ctx):
    return ((ctx.hand.ace_count() in [0, 4]))
def cs_3_requires(ctx):
    return (ctx.state.exists('ace_ask_context', method='gerber', status='pending') and not (ctx.state.exists('ace_ask_response', method='gerber')))
def cs_3_applies(ctx):
    return ((ctx.hand.ace_count() == 1))
def cs_4_requires(ctx):
    return (ctx.state.exists('ace_ask_context', method='gerber', status='pending') and not (ctx.state.exists('ace_ask_response', method='gerber')))
def cs_4_applies(ctx):
    return ((ctx.hand.ace_count() == 2))
def cs_5_requires(ctx):
    return (ctx.state.exists('ace_ask_context', method='gerber', status='pending') and not (ctx.state.exists('ace_ask_response', method='gerber')))
def cs_5_applies(ctx):
    return ((ctx.hand.ace_count() == 3))

class MeowGerberOverNotrumpGadget(Gadget):
    id = 'meow_gerber_over_notrump'
    namespace = 'meow_2over1'
    name = 'Meow Gerber Over Notrump'
    version = '0.1.0'
    description = 'Gerber ace-asking structure when the auction is notrump-focused and no suit is agreed.'
    system_notes = 'With notrump focus and no agreed suit, 4C can be Gerber asking for aces.\n'
    author = Author('Meow Li')

    def build(self):

        frame = self.frame('frame_1')
        frame.frame_type = 'gerber'
        frame.when = '1NP'
        frame.seats = [1, 2, 3, 4]
        frame.source_call = '4C'
        frame.description = 'Gerber ace-asking frame after 4C in a notrump-focused auction.'
        frame.system_notes = '4C Gerber opens an ace-answer frame, with possible later king asks or placement.'
        frame.variables = {'method': 'gerber', 'target_suit': 'N', 'asker': 'actor', 'responder': 'partner'}
        frame.obligation = {'actor': 'responder', 'action': 'answer_frame', 'capabilities': ['answer_frame', 'ace_response']}
        frame.stages = ['ace_response', 'king_or_placement', 'final_placement']
        frame.allowed_continuations = ['ace_ask_response', 'king_ask', 'signoff', 'slam_placement']
        frame.break_conditions = ['undefined_interference_without_policy']
        frame.closes = ['*']
        frame.close_on_actions = ['place_contract', 'pass_final_contract', 'signoff']
        frame.close_on_act_types = ['final_placement', 'signoff']

        call = self.call('cs_1')
        call.when = '*'
        call.bid = '4C'
        call.requires = cs_1_requires
        call.applies = cs_1_applies
        call.capabilities = ('start_frame', 'ace_ask', 'slam_inquiry')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['inquiry', 'ace_asking', 'context_initiating']
        call.meaning.action = 'gerber_ace_ask'
        call.meaning.target_suit = 'N'
        call.meaning.alertable = True
        effect = call.effect('ace_ask_context')
        effect.method = 'gerber'
        effect.target_suit = 'N'
        effect.status = 'pending'
        call.description = 'Responder bids 4C as Gerber over a notrump-focused auction.'
        call.system_notes = 'After a notrump focus with no agreed suit, 4C asks for aces.'

        call = self.call('cs_2')
        call.when = '*'
        call.bid = '4D'
        call.requires = cs_2_requires
        call.applies = cs_2_applies
        call.capabilities = ('answer_frame', 'ace_response')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['relay_response']
        call.meaning.action = 'ace_ask_response'
        call.meaning.alertable = True
        call.meaning.ace_range = [0, 4]
        effect = call.effect('ace_ask_response')
        effect.method = 'gerber'
        effect.response = 'zero_or_four'
        call.description = 'Responder to Gerber answers 4D, showing zero or four aces.'
        call.system_notes = 'Over 4C Gerber, 4D shows 0 or 4 aces.'

        call = self.call('cs_3')
        call.when = '*'
        call.bid = '4H'
        call.requires = cs_3_requires
        call.applies = cs_3_applies
        call.capabilities = ('answer_frame', 'ace_response')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['relay_response']
        call.meaning.action = 'ace_ask_response'
        call.meaning.alertable = True
        call.meaning.ace_count = 1
        effect = call.effect('ace_ask_response')
        effect.method = 'gerber'
        effect.response = 'one'
        call.description = 'Responder to Gerber answers 4H, showing one ace.'
        call.system_notes = 'Over 4C Gerber, 4H shows 1 ace.'

        call = self.call('cs_4')
        call.when = '*'
        call.bid = '4S'
        call.requires = cs_4_requires
        call.applies = cs_4_applies
        call.capabilities = ('answer_frame', 'ace_response')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['relay_response']
        call.meaning.action = 'ace_ask_response'
        call.meaning.alertable = True
        call.meaning.ace_count = 2
        effect = call.effect('ace_ask_response')
        effect.method = 'gerber'
        effect.response = 'two'
        call.description = 'Responder to Gerber answers 4S, showing two aces.'
        call.system_notes = 'Over 4C Gerber, 4S shows 2 aces.'

        call = self.call('cs_5')
        call.when = '*'
        call.bid = '4N'
        call.requires = cs_5_requires
        call.applies = cs_5_applies
        call.capabilities = ('answer_frame', 'ace_response')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['relay_response']
        call.meaning.action = 'ace_ask_response'
        call.meaning.alertable = True
        call.meaning.ace_count = 3
        effect = call.effect('ace_ask_response')
        effect.method = 'gerber'
        effect.response = 'three'
        call.description = 'Responder to Gerber answers 4N, showing three aces.'
        call.system_notes = 'Over 4C Gerber, 4N shows 3 aces.'
