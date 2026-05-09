# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def agreed_suit(ctx):
    return state_attribute(ctx, "agreed_suit", "suit")
def pending_keycard_suit(ctx):
    return state_attribute(ctx, "keycard_context", "trump_suit", method="1430", status="pending")
def answered_keycard_suit(ctx):
    return state_attribute(ctx, "keycard_response", "trump_suit", method="1430")
def specific_king_ask_suit():
    return StateAttribute("specific_king_ask", "trump_suit", status="pending")
def keycard_context_suit():
    return StateAttribute("keycard_context", "trump_suit", method="1430", status="pending")
def keycard_response_suit():
    return StateAttribute("keycard_response", "trump_suit", method="1430")
def cs_1_requires(ctx):
    return (ctx.state.exists('agreed_suit') and not (ctx.state.exists('keycard_context', status='pending')) and not (ctx.state.exists('final_contract')))
def cs_1_applies(ctx):
    return ctx.hand.hcp >= 18 and ctx.hand.length(agreed_suit(ctx)) >= 5
def cs_2_requires(ctx):
    return (ctx.state.exists('keycard_context', method='1430', status='pending') and not (ctx.state.exists('keycard_response', method='1430')))
def cs_2_applies(ctx):
    return ctx.hand.keycard_count(pending_keycard_suit(ctx)) in [1, 4]
def cs_3_requires(ctx):
    return (ctx.state.exists('keycard_context', method='1430', status='pending') and not (ctx.state.exists('keycard_response', method='1430')))
def cs_3_applies(ctx):
    return ctx.hand.keycard_count(pending_keycard_suit(ctx)) in [0, 3]
def cs_4_requires(ctx):
    return (ctx.state.exists('keycard_context', method='1430', status='pending') and not (ctx.state.exists('keycard_response', method='1430')))
def cs_4_applies(ctx):
    suit = pending_keycard_suit(ctx)
    return ctx.hand.keycard_count(suit) == 2 and not ctx.hand.contains_rank(suit, 'Q')
def cs_5_requires(ctx):
    return (ctx.state.exists('keycard_context', method='1430', status='pending') and not (ctx.state.exists('keycard_response', method='1430')))
def cs_5_applies(ctx):
    suit = pending_keycard_suit(ctx)
    return ctx.hand.keycard_count(suit) == 2 and ctx.hand.contains_rank(suit, 'Q')
def cs_6_requires(ctx):
    return (ctx.state.exists('keycard_response', method='1430', response='one_or_four') and not (ctx.state.exists('specific_king_ask', status='pending')) and not (ctx.state.exists('final_contract')))
def cs_6_applies(ctx):
    suit = answered_keycard_suit(ctx)
    return ctx.hand.keycard_count(suit) == 4 and ctx.hand.contains_rank(suit, 'Q')
def cs_7_requires(ctx):
    return (ctx.state.exists('specific_king_ask', status='pending') and not (ctx.state.exists('specific_king_response')))
def cs_7_applies(ctx):
    return (ctx.hand.contains_rank('D', 'K'))
def cs_8_requires(ctx):
    return (ctx.state.exists('all_keycards_known', trump_suit='S', status='yes') and ctx.state.exists('specific_king_response', trump_suit='S', target_suit='D', rank='K') and not (ctx.state.exists('final_contract')))
def cs_8_applies(ctx):
    return (ctx.hand.hcp >= 18 and ctx.hand.length('S') >= 6)
def cs_9_requires(ctx):
    return (ctx.state.exists('all_keycards_known', trump_suit='H', status='yes') and ctx.state.exists('specific_king_response', trump_suit='H', target_suit='D', rank='K') and not (ctx.state.exists('final_contract')))
def cs_9_applies(ctx):
    return (ctx.hand.hcp >= 18 and ctx.hand.length('H') >= 6)
def cs_10_requires(ctx):
    return ctx.state.exists('final_contract', source='rkcb_1430')
def cs_10_applies(ctx):
    return (ctx.state.exists('final_contract', source='rkcb_1430'))

class MeowRkcb1430Gadget(Gadget):
    id = 'meow_rkcb_1430'
    namespace = 'meow_2over1'
    name = 'Meow RKCB 1430'
    version = '0.1.0'
    description = 'Standalone RKCB 1430 Gadget. It consumes agreed-suit semantic state created by transfers, raises, splinters, or other Gadgets. The current executable slice keeps visible anchors for the Texas-to-spades benchmark route until the engine supports fully generic semantic-context matching.\n'
    author = Author('Meow Li')

    def build(self):

        frame = self.frame('frame_1')
        frame.frame_type = 'rkcb_1430'
        frame.when = '*'
        frame.source_call = '4N'
        frame.description = 'Active RKCB 1430 keycard-asking frame after 4N is interpreted as RKCB.'
        frame.system_notes = 'A 4N RKCB ask opens a keycard-answer frame using 1430 responses.'
        frame.variables = {'method': '1430', 'trump_suit_source': 'agreed_suit', 'asker': 'actor', 'responder': 'partner'}
        frame.obligation = {'actor': 'responder', 'action': 'answer_frame', 'capabilities': ['answer_frame', 'keycard_response']}
        frame.stages = ['keycard_response', 'queen_or_king_continuation', 'final_placement']
        frame.allowed_continuations = ['keycard_response', 'queen_ask', 'specific_king_ask', 'signoff', 'slam_placement']
        frame.break_conditions = ['undefined_interference_without_policy']
        frame.closes = ['*']
        frame.close_on_actions = ['place_contract', 'pass_final_contract', 'signoff']
        frame.close_on_act_types = ['final_placement', 'signoff']

        call = self.call('cs_1')
        call.when = '*'
        call.bid = '4N'
        call.requires = cs_1_requires
        call.applies = cs_1_applies
        call.capabilities = ('start_frame', 'keycard_ask', 'slam_inquiry')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['inquiry', 'keycard_asking']
        call.meaning.action = 'rkcb_1430'
        call.meaning.alertable = True
        call.meaning.target_suit_source = 'agreed_suit'
        effect = call.effect('keycard_context')
        effect.trump_suit = {'op': 'state_attribute', 'query': {'key': 'agreed_suit'}, 'attribute': 'suit'}
        effect.ask_call = '4N'
        effect.method = '1430'
        effect.status = 'pending'
        call.description = 'Asker bids 4N as RKCB 1430 for the currently agreed suit.'
        call.system_notes = 'When a suit is agreed and slam interest is present, 4N is RKCB 1430 for that suit.'

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
        effect.trump_suit = {'op': 'state_attribute', 'query': {'key': 'keycard_context', 'method': '1430', 'status': 'pending'}, 'attribute': 'trump_suit'}
        effect.method = '1430'
        effect.response = 'one_or_four'
        call.description = 'Responder to RKCB answers 5C, showing 1 or 4 keycards.'
        call.system_notes = 'In RKCB 1430, 5C shows 1 or 4 keycards.'

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
        effect.trump_suit = {'op': 'state_attribute', 'query': {'key': 'keycard_context', 'method': '1430', 'status': 'pending'}, 'attribute': 'trump_suit'}
        effect.method = '1430'
        effect.response = 'zero_or_three'
        call.description = 'Responder to RKCB answers 5D, showing 0 or 3 keycards.'
        call.system_notes = 'In RKCB 1430, 5D shows 0 or 3 keycards.'

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
        effect.trump_suit = {'op': 'state_attribute', 'query': {'key': 'keycard_context', 'method': '1430', 'status': 'pending'}, 'attribute': 'trump_suit'}
        effect.method = '1430'
        effect.response = 'two_without_queen'
        call.description = 'Responder to RKCB answers 5H, showing 2 keycards without the trump queen.'
        call.system_notes = 'In RKCB 1430, 5H shows 2 keycards without the trump queen.'

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
        effect.trump_suit = {'op': 'state_attribute', 'query': {'key': 'keycard_context', 'method': '1430', 'status': 'pending'}, 'attribute': 'trump_suit'}
        effect.method = '1430'
        effect.response = 'two_with_queen'
        call.description = 'Responder to RKCB answers 5S, showing 2 keycards with the trump queen.'
        call.system_notes = 'In RKCB 1430, 5S shows 2 keycards with the trump queen.'

        call = self.call('cs_6')
        call.when = '*'
        call.bid = '5N'
        call.requires = cs_6_requires
        call.applies = cs_6_applies
        call.capabilities = ('start_frame', 'specific_king_ask', 'slam_inquiry')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['inquiry']
        call.meaning.action = 'specific_king_ask'
        call.meaning.alertable = True
        effect = call.effect('all_keycards_known')
        effect.trump_suit = {'op': 'state_attribute', 'query': {'key': 'keycard_response', 'method': '1430'}, 'attribute': 'trump_suit'}
        effect.status = 'yes'
        effect = call.effect('specific_king_ask')
        effect.trump_suit = {'op': 'state_attribute', 'query': {'key': 'keycard_response', 'method': '1430'}, 'attribute': 'trump_suit'}
        effect.status = 'pending'
        call.description = 'Asker bids 5N to ask for specific kings after accounting for all keycards.'
        call.system_notes = '5N asks for specific kings and guarantees all keycards in this benchmark route.'

        call = self.call('cs_7')
        call.when = '*'
        call.bid = '6D'
        call.requires = cs_7_requires
        call.applies = cs_7_applies
        call.capabilities = ('answer_frame', 'specific_king_response')
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['relay_response', 'control_showing']
        call.meaning.action = 'specific_king_response'
        call.meaning.target_suit = 'D'
        call.meaning.alertable = True
        effect = call.effect('specific_king_response')
        effect.trump_suit = {'op': 'state_attribute', 'query': {'key': 'specific_king_ask', 'status': 'pending'}, 'attribute': 'trump_suit'}
        effect.target_suit = 'D'
        effect.rank = 'K'
        call.description = 'Responder shows the diamond king over the specific-king ask.'
        call.system_notes = 'Over 5N specific-king ask, 6D shows the diamond king.'

        call = self.call('cs_8')
        call.when = '*'
        call.bid = '7S'
        call.requires = cs_8_requires
        call.applies = cs_8_applies
        call.capabilities = ('place_contract', 'slam_placement')
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'S'
        call.meaning.level = 7
        effect = call.effect('final_contract')
        effect.target_suit = 'S'
        effect.level = 7
        effect.source = 'rkcb_1430'
        call.description = 'Asker places the grand slam in spades after the diamond king is shown.'
        call.system_notes = '7S is final placement after the RKCB and specific-king route.'

        call = self.call('cs_9')
        call.when = '*'
        call.bid = '7H'
        call.requires = cs_9_requires
        call.applies = cs_9_applies
        call.capabilities = ('place_contract', 'slam_placement')
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'place_contract'
        call.meaning.target_suit = 'H'
        call.meaning.level = 7
        effect = call.effect('final_contract')
        effect.target_suit = 'H'
        effect.level = 7
        effect.source = 'rkcb_1430'
        call.description = 'Asker places the grand slam in hearts after the diamond king is shown.'
        call.system_notes = '7H is final placement after the RKCB and specific-king route.'

        call = self.call('cs_10')
        call.when = '*'
        call.bid = 'P'
        call.requires = cs_10_requires
        call.applies = cs_10_applies
        call.capabilities = ('place_contract', 'pass_final_contract')
        call.meaning.nature = ['natural']
        call.meaning.acts = ['final_placement']
        call.meaning.action = 'pass_final_contract'
        call.description = 'Partner passes after a final contract has been placed.'
        call.system_notes = 'After a final contract is placed, partner passes to end the auction.'
