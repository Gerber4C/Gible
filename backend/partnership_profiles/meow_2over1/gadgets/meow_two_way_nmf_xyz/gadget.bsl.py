# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_1_requires(ctx):
    return ((ctx.state.exists('opener_notrump_rebid') or ctx.state.exists('opener_rebid')) and not (ctx.state.exists('checkback_relay')) and not (ctx.state.exists('checkback_game_force')) and not (ctx.state.exists('checkback_club_drop_dead')))
def cs_1_applies(ctx):
    return ((((ctx.hand.hcp >= 11) and (ctx.hand.hcp <= 12)) or ((ctx.hand.hcp <= 7) and (ctx.hand.length('D') >= 5))))
def cs_2_requires(ctx):
    return ((ctx.state.exists('opener_notrump_rebid') or ctx.state.exists('opener_rebid')) and not (ctx.state.exists('checkback_relay')) and not (ctx.state.exists('checkback_game_force')) and not (ctx.state.exists('checkback_club_drop_dead')))
def cs_2_applies(ctx):
    response_suit = state_attribute(ctx, 'one_level_response', 'target_suit')
    return ctx.hand.hcp >= 13 and (ctx.hand.length(response_suit) >= 5 or max(ctx.hand.length('H'), ctx.hand.length('S')) >= 4)
def cs_3_requires(ctx):
    return ((ctx.state.exists('opener_notrump_rebid') or ctx.state.exists('opener_rebid')) and not (ctx.state.exists('checkback_relay')) and not (ctx.state.exists('checkback_game_force')) and not (ctx.state.exists('checkback_club_drop_dead')))
def cs_3_applies(ctx):
    return (((ctx.hand.hcp <= 7) and (ctx.hand.length('C') >= 5)))
def cs_4_requires(ctx):
    return ((ctx.state.exists('opener_notrump_rebid') or ctx.state.exists('opener_rebid')) and not (ctx.state.exists('checkback_relay')) and not (ctx.state.exists('checkback_game_force')) and not (ctx.state.exists('checkback_club_drop_dead')))
def cs_4_applies(ctx):
    return (ctx.hand.hcp >= 16 and ctx.hand.length('C') >= 5)
def cs_5_requires(ctx):
    return ((ctx.state.exists('opener_notrump_rebid') or ctx.state.exists('opener_rebid')) and not (ctx.state.exists('checkback_relay')) and not (ctx.state.exists('checkback_game_force')) and not (ctx.state.exists('checkback_club_drop_dead')))
def cs_5_applies(ctx):
    return (ctx.hand.hcp >= 16 and ctx.hand.length('D') >= 5)
def cs_6_requires(ctx):
    return (ctx.state.exists('checkback_relay', relay_call='2D', status='pending') and not (ctx.state.exists('checkback_relay_completion', relay_call='2D', status='completed')))
def cs_6_applies(ctx):
    return (ctx.state.exists('checkback_relay', relay_call='2D', status='pending'))
def cs_7_requires(ctx):
    return ctx.state.exists('checkback_relay_completion', relay_call='2D', status='completed')
def cs_7_applies(ctx):
    return (((ctx.hand.hcp <= 7) and (ctx.hand.length('D') >= 5)))
def cs_8_requires(ctx):
    return ctx.state.exists('checkback_relay_completion', relay_call='2D', status='completed')
def cs_8_applies(ctx):
    return ((ctx.hand.hcp >= 11 and ctx.hand.hcp <= 12) and ctx.hand.balanced == True)
def cs_9_requires(ctx):
    return (ctx.state.exists('checkback_club_drop_dead', relay_call='3C', status='pending') and not (ctx.state.exists('checkback_club_drop_dead_completion', target_suit='C', status='completed')))
def cs_9_applies(ctx):
    return (ctx.state.exists('checkback_club_drop_dead', relay_call='3C', status='pending'))
def cs_10_requires(ctx):
    return ctx.state.exists('checkback_club_drop_dead_completion', target_suit='C', status='completed')
def cs_10_applies(ctx):
    return (((ctx.hand.hcp <= 7) and (ctx.hand.length('C') >= 5)))
def cs_11_requires(ctx):
    return ctx.state.exists('checkback_game_force', status='pending')
def cs_11_applies(ctx):
    return state_attribute(ctx, 'one_level_response', 'target_suit') == 'H' and ctx.hand.length('H') >= 3
def cs_12_requires(ctx):
    return ctx.state.exists('checkback_game_force', status='pending')
def cs_12_applies(ctx):
    return state_attribute(ctx, 'one_level_response', 'target_suit') == 'S' and ctx.hand.length('S') >= 3
def cs_13_requires(ctx):
    return ctx.state.exists('checkback_game_force', status='pending')
def cs_13_applies(ctx):
    response_suit = state_attribute(ctx, 'one_level_response', 'target_suit')
    return ctx.hand.length(response_suit) <= 2

class MeowTwoWayNmfXyzGadget(Gadget):
    id = 'meow_two_way_nmf_xyz'
    namespace = 'meow_2over1'
    name = 'Meow Two-Way NMF and XYZ'
    version = '0.1.0'
    description = "Two-way New Minor Forcing after opener's 1N rebid and XYZ after three one-level calls, including 2C invitational relay, 2D game force, and 2N transfer to 3C for drop-dead club routes.\n"
    author = Author('Meow Li')

    def build(self):

        call = self.call('cs_1')
        call.when = '*'
        call.bid = '2C'
        call.requires = cs_1_requires
        call.applies = cs_1_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['relay', 'context_initiating']
        call.meaning.action = 'checkback_two_club_relay'
        call.meaning.alertable = True
        call.meaning.relay_call = '2D'
        effect = call.effect('checkback_relay')
        effect.relay_call = '2D'
        effect.status = 'pending'
        effect.strength_band = 'invitational_or_weak_diamonds'
        call.description = 'Responder starts the 2C relay in two-way New Minor Forcing or XYZ.'
        call.system_notes = 'After 1X-1Y-1N or a three-call one-level auction, 2C relays to 2D for invitational hands or weak diamond signoff routes.'

        call = self.call('cs_2')
        call.when = '*'
        call.bid = '2D'
        call.requires = cs_2_requires
        call.applies = cs_2_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['inquiry', 'game_forcing', 'context_initiating']
        call.meaning.action = 'checkback_game_force'
        call.meaning.alertable = True
        effect = call.effect('checkback_game_force')
        effect.status = 'pending'
        effect = call.effect('partnership.force_status', owner='partnership')
        effect.value = 'game_forcing'
        effect.source = 'checkback_game_force'
        effect = call.effect('responder.route_purpose', namespace='private', owner='responder')
        effect.value = 'establish_force_before_describing_long_suit_or_shape'
        effect.source = 'checkback_game_force'
        call.description = 'Responder starts the 2D game-forcing checkback route in two-way NMF or XYZ.'
        call.system_notes = 'After 1X-1Y-1N or a three-call one-level auction, 2D is artificial and game forcing.'

        call = self.call('cs_3')
        call.when = '*'
        call.bid = '2N'
        call.requires = cs_3_requires
        call.applies = cs_3_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['relay', 'signoff_preparation', 'context_initiating']
        call.meaning.action = 'checkback_two_notrump_club_relay'
        call.meaning.alertable = True
        call.meaning.relay_call = '3C'
        effect = call.effect('checkback_club_drop_dead')
        effect.relay_call = '3C'
        effect.status = 'pending'
        call.description = 'Responder bids 2N as a transfer to 3C for weak club drop-dead routes.'
        call.system_notes = 'In the benchmark XYZ structure, 2N transfers opener to 3C, usually to play there.'

        call = self.call('cs_4')
        call.when = '*'
        call.bid = '3C'
        call.requires = cs_4_requires
        call.applies = cs_4_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['slam_try', 'descriptive']
        call.meaning.action = 'natural_slam_try'
        call.meaning.target_suit = 'C'
        effect = call.effect('slam_interest')
        effect.target_suit = 'C'
        effect.status = 'active'
        effect.source = 'checkback_structure'
        call.description = 'Responder makes a natural club slam try instead of using the 2N drop-dead relay.'
        call.system_notes = 'In the benchmark checkback/XYZ structure, 3C is a natural slam try.'

        call = self.call('cs_5')
        call.when = '*'
        call.bid = '3D'
        call.requires = cs_5_requires
        call.applies = cs_5_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['slam_try', 'descriptive']
        call.meaning.action = 'natural_slam_try'
        call.meaning.target_suit = 'D'
        effect = call.effect('slam_interest')
        effect.target_suit = 'D'
        effect.status = 'active'
        effect.source = 'checkback_structure'
        call.description = 'Responder makes a natural diamond slam try.'
        call.system_notes = 'In the benchmark checkback/XYZ structure, 3D is a natural slam try.'

        call = self.call('cs_6')
        call.when = '*'
        call.bid = '2D'
        call.requires = cs_6_requires
        call.applies = cs_6_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['relay_completion']
        call.meaning.action = 'checkback_relay_completion'
        call.meaning.alertable = True
        effect = call.effect('checkback_relay_completion')
        effect.relay_call = '2D'
        effect.status = 'completed'
        call.description = 'Opener completes the 2C checkback relay by bidding 2D.'
        call.system_notes = 'Over the artificial 2C checkback relay, opener bids 2D as requested.'

        call = self.call('cs_7')
        call.when = '*'
        call.bid = 'P'
        call.requires = cs_7_requires
        call.applies = cs_7_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['signoff', 'final_placement']
        call.meaning.action = 'pass_final_contract'
        call.meaning.target_suit = 'D'
        call.meaning.level = 2
        effect = call.effect('final_contract')
        effect.target_suit = 'D'
        effect.level = 2
        effect.source = 'checkback_structure'
        call.description = 'Responder passes 2D after the checkback relay with weak diamonds.'
        call.system_notes = 'After 2C-2D in the checkback structure, pass is the weak diamond signoff route.'

        call = self.call('cs_8')
        call.when = '*'
        call.bid = '2N'
        call.requires = cs_8_requires
        call.applies = cs_8_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['invitational']
        call.meaning.action = 'notrump_invite'
        call.meaning.target_suit = 'N'
        call.meaning.level = 2
        effect = call.effect('game_invite')
        effect.target_suit = 'N'
        effect.source = 'checkback_structure'
        call.description = 'Responder rebids 2N after the 2C-2D relay with invitational notrump values.'
        call.system_notes = 'After 2C-2D in the checkback structure, 2N is invitational.'

        call = self.call('cs_9')
        call.when = '*'
        call.bid = '3C'
        call.requires = cs_9_requires
        call.applies = cs_9_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['relay_completion']
        call.meaning.action = 'checkback_club_relay_completion'
        call.meaning.alertable = True
        effect = call.effect('checkback_club_drop_dead_completion')
        effect.target_suit = 'C'
        effect.status = 'completed'
        call.description = 'Opener completes the 2N club relay by bidding 3C.'
        call.system_notes = 'Over the artificial 2N club relay, opener bids 3C as requested.'

        call = self.call('cs_10')
        call.when = '*'
        call.bid = 'P'
        call.requires = cs_10_requires
        call.applies = cs_10_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['signoff', 'final_placement']
        call.meaning.action = 'pass_final_contract'
        call.meaning.target_suit = 'C'
        call.meaning.level = 3
        effect = call.effect('final_contract')
        effect.target_suit = 'C'
        effect.level = 3
        effect.source = 'checkback_structure'
        call.description = 'Responder passes 3C after the 2N-3C relay with weak clubs.'
        call.system_notes = 'After 2N-3C in the checkback structure, pass is the weak club signoff route.'

        call = self.call('cs_11')
        call.when = '*'
        call.bid = '2H'
        call.requires = cs_11_requires
        call.applies = cs_11_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['support_showing']
        call.meaning.action = 'checkback_support_showing'
        call.meaning.target_suit = 'H'
        effect = call.effect('agreed_suit')
        effect.suit = 'H'
        effect.source = 'checkback_game_force'
        call.description = 'Opener shows three-card heart support over the 2D game-forcing checkback ask.'
        call.system_notes = "Over artificial 2D checkback, opener bids 2H with three-card heart support when hearts were responder's suit."

        call = self.call('cs_12')
        call.when = '*'
        call.bid = '2S'
        call.requires = cs_12_requires
        call.applies = cs_12_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['support_showing']
        call.meaning.action = 'checkback_support_showing'
        call.meaning.target_suit = 'S'
        effect = call.effect('agreed_suit')
        effect.suit = 'S'
        effect.source = 'checkback_game_force'
        call.description = 'Opener shows three-card spade support over the 2D game-forcing checkback ask.'
        call.system_notes = "Over artificial 2D checkback, opener bids 2S with three-card spade support when spades were responder's suit."

        call = self.call('cs_13')
        call.when = '*'
        call.bid = '2N'
        call.requires = cs_13_requires
        call.applies = cs_13_applies
        call.meaning.nature = ['natural']
        call.meaning.acts = ['descriptive']
        call.meaning.action = 'checkback_no_support'
        call.meaning.target_suit = 'N'
        call.meaning.level = 2
        call.description = 'Opener rebids 2N over the 2D game-forcing checkback ask without three-card support.'
        call.system_notes = "Over artificial 2D checkback, 2N denies three-card support for responder's major in this benchmark slice."
