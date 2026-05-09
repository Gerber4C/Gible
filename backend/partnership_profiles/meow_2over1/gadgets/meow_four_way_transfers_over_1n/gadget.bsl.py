# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def eval_minor_honor_third(ctx, target_suit):
    return (
        ctx.hand.length(target_suit) >= 3
        and ctx.hand.honor_count(target_suit, ["A", "K", "Q"]) >= 1
    )
def weak_heart_signoff(ctx):
    return ctx.hand.length("H") >= 5 and ctx.hand.hcp <= 6
def strong_heart_slam_route(ctx):
    return ctx.hand.length("H") >= 6 and ctx.hand.hcp >= 16
def superaccepted_hearts(ctx):
    return (
        ctx.state.exists("agreed_suit", suit="H")
        and ctx.state.exists("transfer_superaccept", target_suit="H", status="accepted")
    )
def cs_1_requires(ctx):
    return ctx.state.exists('notrump_focus', status='active')
def cs_1_applies(ctx):
    return (ctx.hand.length('H') >= 5)
def cs_2_requires(ctx):
    return ctx.state.exists('notrump_focus', status='active')
def cs_2_applies(ctx):
    return (ctx.hand.length('S') >= 5)
def cs_3_requires(ctx):
    return (ctx.state.exists('transfer', target_suit='H', status='pending'))
def cs_3_applies(ctx):
    return (ctx.state.exists('transfer', target_suit='H', status='pending'))
def cs_4_requires(ctx):
    return ctx.state.exists('notrump_focus', status='active')
def cs_4_applies(ctx):
    return (ctx.hand.length('C') >= 6)
def cs_5_requires(ctx):
    return ctx.state.exists('transfer', target_suit='C', status='pending')
def cs_5_applies(ctx):
    return (named_evaluator(ctx, 'eval_minor_honor_third', target_suit='C'))
def cs_6_requires(ctx):
    return ctx.state.exists('transfer', target_suit='C', status='pending')
def cs_6_applies(ctx):
    return (ctx.state.exists('transfer', target_suit='C', status='pending'))
def cs_7_requires(ctx):
    return ctx.state.exists('notrump_focus', status='active')
def cs_7_applies(ctx):
    return (ctx.hand.length('D') >= 6)
def cs_8_requires(ctx):
    return ctx.state.exists('transfer', target_suit='D', status='pending')
def cs_8_applies(ctx):
    return (named_evaluator(ctx, 'eval_minor_honor_third', target_suit='D'))
def cs_9_requires(ctx):
    return ctx.state.exists('transfer', target_suit='D', status='pending')
def cs_9_applies(ctx):
    return (ctx.state.exists('transfer', target_suit='D', status='pending'))
def cs_10_requires(ctx):
    return ctx.state.exists('transfer', target_suit='S', status='pending')
def cs_10_applies(ctx):
    return (ctx.state.exists('transfer', target_suit='S', status='pending'))
def cs_11_requires(ctx):
    return (ctx.state.exists('transfer', target_suit='H', status='pending'))
def cs_11_applies(ctx):
    return (ctx.state.exists('transfer', target_suit='H', status='pending') and ctx.hand.length('H') >= 4 and ctx.hand.hcp >= 16)
def cs_12_requires(ctx):
    return (ctx.state.exists('transfer', target_suit='S', status='pending'))
def cs_12_applies(ctx):
    return (ctx.state.exists('transfer', target_suit='S', status='pending') and ctx.hand.length('S') >= 4 and ctx.hand.hcp >= 16)

class MeowFourWayTransfersOver1nGadget(Gadget):
    id = 'meow_four_way_transfers_over_1n'
    namespace = 'meow_2over1'
    name = 'Meow Four-Way Transfers Over 1N'
    version = '0.1.0'
    description = 'Standalone four-way transfer structure over 1N. It creates transfer semantic state that other Gadgets can consume, but it does not own RKCB.\n'
    author = Author('Meow Li')

    def build(self):

        evaluator = self.evaluator('eval_minor_honor_third')
        evaluator.function = eval_minor_honor_third
        evaluator.description = 'Target minor has at least three cards and at least one of A, K, or Q.'
        evaluator.system_notes = 'Minor-transfer superaccept support requires honor-third or stronger in the target minor.'

        frame = self.frame('frame_1')
        frame.frame_type = 'major_transfer'
        frame.when = '1NP'
        frame.seats = [1, 2, 3, 4]
        frame.source_call = '2D'
        frame.description = 'Live heart-transfer frame after responder bids 2D over 1N.'
        frame.system_notes = 'A 2D transfer creates a heart-transfer context until responder places or redirects the contract.'
        frame.variables = {'target_suit': 'H', 'initiator': 'responder', 'acceptor': 'opener'}
        frame.stages = ['opener_rebid', 'responder_continuation']
        frame.allowed_continuations = ['transfer_completion', 'superaccept', 'responder_signoff', 'responder_invite', 'responder_second_suit', 'responder_slam_exploration']
        frame.break_conditions = ['undefined_interference_without_policy']
        frame.close_on_actions = ['place_contract', 'pass_final_contract', 'signoff']
        frame.close_on_act_types = ['final_placement', 'signoff']

        route = self.route('route_1')
        route.owner = 'responder'
        route.goal = 'signoff'
        route.entry_call = '2D'
        route.when = '1NP'
        route.seats = [1, 2, 3, 4]
        route.preconditions = weak_heart_signoff
        route.workflow = {'start': 'wait_for_acceptance', 'nodes': {'wait_for_acceptance': {'kind': 'wait_for_call', 'branches': [{'when': {'kind': 'call_is', 'value': '2H'}, 'goto': 'pass_acceptance'}, {'when': {'kind': 'call_is', 'value': '3H'}, 'goto': 'pass_acceptance'}], 'actor': 'opener'}, 'pass_acceptance': {'kind': 'make_call', 'call': 'P', 'requires_call_specification': False, 'meaning': Meaning(action='final_placement', target_suit='H', nature=['natural'], acts=['signoff', 'final_placement'])}}}
        route.description = 'Weak heart-transfer signoff route.'
        route.system_notes = "With 5+ hearts and 0-6 HCP, responder may transfer to hearts and pass opener's acceptance."

        route = self.route('route_2')
        route.owner = 'responder'
        route.goal = 'ask_keycards'
        route.entry_call = '2D'
        route.when = '1NP'
        route.seats = [1, 2, 3, 4]
        route.preconditions = strong_heart_slam_route
        route.workflow = {'start': 'wait_for_superaccept', 'nodes': {'wait_for_superaccept': {'kind': 'wait_for_call', 'branches': [{'when': {'kind': 'call_is', 'value': '3H'}, 'goto': 'ask_keycards'}], 'actor': 'opener'}, 'ask_keycards': {'kind': 'make_call', 'call': '4N', 'requires_call_specification': True, 'requires': superaccepted_hearts}}}
        route.entry_candidate = True
        route.description = 'Heart-transfer slam exploration route after a superaccept.'
        route.system_notes = 'With a strong long-heart hand, responder can start with 2D; if opener superaccepts at 3H, responder may use 4N as RKCB for hearts.'

        call = self.call('cs_1')
        call.when = '1NP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2D'
        call.requires = cs_1_requires
        call.applies = cs_1_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['directive', 'context_initiating', 'forcing']
        call.meaning.action = 'transfer'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        call.meaning.acbl_explanation = 'hearts'
        effect = call.effect('transfer')
        effect.target_suit = 'H'
        effect.status = 'pending'
        call.description = 'Responder bids 2D as a transfer to hearts with at least five hearts.'
        call.system_notes = 'After 1N, 2D transfers to hearts.'

        call = self.call('cs_2')
        call.when = '1NP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2H'
        call.requires = cs_2_requires
        call.applies = cs_2_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['directive', 'context_initiating', 'forcing']
        call.meaning.action = 'transfer'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        call.meaning.acbl_explanation = 'spades'
        effect = call.effect('transfer')
        effect.target_suit = 'S'
        effect.status = 'pending'
        call.description = 'Responder bids 2H as a transfer to spades with at least five spades.'
        call.system_notes = 'After 1N, 2H transfers to spades.'

        call = self.call('cs_3')
        call.when = '1NP2DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2H'
        call.requires = cs_3_requires
        call.applies = cs_3_applies
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['directive', 'context_setting']
        call.meaning.action = 'transfer_completion'
        call.meaning.target_suit = 'H'
        effect = call.effect('transfer_completion')
        effect.target_suit = 'H'
        effect.status = 'completed'
        call.description = 'Opener completes the heart transfer at 2H.'
        call.system_notes = 'After 1N-2D, 2H completes the heart transfer.'

        call = self.call('cs_4')
        call.when = '1NP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2S'
        call.requires = cs_4_requires
        call.applies = cs_4_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['directive', 'context_initiating', 'forcing']
        call.meaning.action = 'transfer'
        call.meaning.target_suit = 'C'
        call.meaning.alertable = True
        effect = call.effect('transfer')
        effect.target_suit = 'C'
        effect.status = 'pending'
        call.description = 'Responder bids 2S as a transfer to clubs with at least six clubs.'
        call.system_notes = 'After 1N, 2S transfers to clubs and requires a six-card club suit.'

        call = self.call('cs_5')
        call.when = '1NP2SP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2N'
        call.requires = cs_5_requires
        call.applies = cs_5_applies
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['directive', 'context_setting']
        call.meaning.action = 'superaccept'
        call.meaning.target_suit = 'C'
        call.meaning.alertable = True
        effect = call.effect('transfer_superaccept')
        effect.target_suit = 'C'
        effect.status = 'accepted'
        call.description = 'Opener bids the gap 2N to superaccept the club transfer with honor-third or stronger support.'
        call.system_notes = 'After 1N-2S, 2N is the gap superaccept for clubs.'

        call = self.call('cs_6')
        call.when = '1NP2SP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3C'
        call.requires = cs_6_requires
        call.applies = cs_6_applies
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['directive', 'context_setting']
        call.meaning.action = 'transfer_completion'
        call.meaning.target_suit = 'C'
        effect = call.effect('transfer_completion')
        effect.target_suit = 'C'
        effect.status = 'completed'
        call.description = 'Opener accepts the club transfer normally at 3C.'
        call.system_notes = 'After 1N-2S, 3C is the normal club transfer acceptance.'

        call = self.call('cs_7')
        call.when = '1NP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2N'
        call.requires = cs_7_requires
        call.applies = cs_7_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['directive', 'context_initiating', 'forcing']
        call.meaning.action = 'transfer'
        call.meaning.target_suit = 'D'
        call.meaning.alertable = True
        effect = call.effect('transfer')
        effect.target_suit = 'D'
        effect.status = 'pending'
        call.description = 'Responder bids 2N as a transfer to diamonds with at least six diamonds.'
        call.system_notes = 'After 1N, 2N transfers to diamonds and requires a six-card diamond suit.'

        call = self.call('cs_8')
        call.when = '1NP2NP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3C'
        call.requires = cs_8_requires
        call.applies = cs_8_applies
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['directive', 'context_setting']
        call.meaning.action = 'superaccept'
        call.meaning.target_suit = 'D'
        call.meaning.alertable = True
        effect = call.effect('transfer_superaccept')
        effect.target_suit = 'D'
        effect.status = 'accepted'
        effect = call.effect('agreed_suit')
        effect.suit = 'D'
        effect.source = 'minor_transfer_superaccept'
        call.description = 'Opener bids the gap 3C to superaccept the diamond transfer with honor-third or stronger support.'
        call.system_notes = 'After 1N-2N, 3C is the gap superaccept for diamonds.'

        call = self.call('cs_9')
        call.when = '1NP2NP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3D'
        call.requires = cs_9_requires
        call.applies = cs_9_applies
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['directive', 'context_setting']
        call.meaning.action = 'transfer_completion'
        call.meaning.target_suit = 'D'
        effect = call.effect('transfer_completion')
        effect.target_suit = 'D'
        effect.status = 'completed'
        call.description = 'Opener accepts the diamond transfer normally at 3D.'
        call.system_notes = 'After 1N-2N, 3D is the normal diamond transfer acceptance.'

        call = self.call('cs_10')
        call.when = '1NP2HP'
        call.seats = [1, 2, 3, 4]
        call.bid = '2S'
        call.requires = cs_10_requires
        call.applies = cs_10_applies
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['directive', 'context_setting']
        call.meaning.action = 'transfer_completion'
        call.meaning.target_suit = 'S'
        effect = call.effect('transfer_completion')
        effect.target_suit = 'S'
        effect.status = 'completed'
        call.description = 'Opener completes the spade transfer at 2S.'
        call.system_notes = 'After 1N-2H, 2S completes the spade transfer.'

        call = self.call('cs_11')
        call.when = '1NP2DP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3H'
        call.requires = cs_11_requires
        call.applies = cs_11_applies
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['directive', 'context_setting']
        call.meaning.action = 'superaccept'
        call.meaning.target_suit = 'H'
        call.meaning.alertable = True
        effect = call.effect('transfer_superaccept')
        effect.target_suit = 'H'
        effect.status = 'accepted'
        effect = call.effect('agreed_suit')
        effect.suit = 'H'
        effect.source = 'major_transfer_superaccept'
        call.description = 'Opener superaccepts the heart transfer at 3H with four-card support and maximum values.'
        call.system_notes = 'After 1N-2D, 3H is a heart-transfer superaccept with four-card heart support and maximum values.'

        call = self.call('cs_12')
        call.when = '1NP2HP'
        call.seats = [1, 2, 3, 4]
        call.bid = '3S'
        call.requires = cs_12_requires
        call.applies = cs_12_applies
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['directive', 'context_setting']
        call.meaning.action = 'superaccept'
        call.meaning.target_suit = 'S'
        call.meaning.alertable = True
        effect = call.effect('transfer_superaccept')
        effect.target_suit = 'S'
        effect.status = 'accepted'
        effect = call.effect('agreed_suit')
        effect.suit = 'S'
        effect.source = 'major_transfer_superaccept'
        call.description = 'Opener superaccepts the spade transfer at 3S with four-card support and maximum values.'
        call.system_notes = 'After 1N-2H, 3S is a spade-transfer superaccept with four-card spade support and maximum values.'
