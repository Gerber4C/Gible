# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def control_context(agreed_suit):
    def applies(ctx):
        return (
            ctx.state.exists('agreed_suit', suit=agreed_suit)
            and (
                ctx.state.exists('slam_interest', status='active')
                or ctx.state.exists('transfer_superaccept', target_suit=agreed_suit, status='accepted')
            )
            and not ctx.state.exists('keycard_context', status='pending')
            and not ctx.state.exists('final_contract')
        )
    return applies
def control_available(call, control_suit):
    def applies(ctx):
        return (
            call in ctx.legal_calls
            and (
                ctx.hand.contains_rank(control_suit, 'A')
                or ctx.hand.contains_rank(control_suit, 'K')
                or ctx.hand.length(control_suit) <= 1
            )
        )
    return applies

class MeowControlBiddingGadget(Gadget):
    id = 'meow_control_bidding'
    namespace = 'meow_2over1'
    name = 'Meow Control Bidding'
    version = '0.1.0'
    description = 'Cooperative control-showing calls after a suit is agreed and slam interest is present.'
    system_notes = 'After a fit is agreed, non-trump suit calls can show controls and cooperate in slam exploration.\n'
    author = Author('Meow Li')

    def build(self):

        frame = self.frame('frame_1')
        frame.frame_type = 'control_bidding'
        frame.when = '1NP2DP3HP'
        frame.seats = [1, 2, 3, 4]
        frame.source_call = '4D'
        frame.description = 'Cooperative control-bidding frame after a diamond control bid in the heart-transfer route.'
        frame.system_notes = 'A control bid opens a cooperative slam frame; later calls may sign off, continue controls, or ask keycards.'
        frame.variables = {'agreed_suit': 'H', 'control_suit': 'D', 'initiator': 'actor', 'responder': 'partner'}
        frame.stages = ['cooperation', 'keycard_or_signoff', 'final_placement']
        frame.allowed_continuations = ['control_showing', 'keycard_asking', 'signoff', 'slam_placement']
        frame.break_conditions = ['undefined_interference_without_policy']
        frame.closes = ['major_transfer', 'minor_transfer', 'transfer']
        frame.close_on_actions = ['place_contract', 'pass_final_contract', 'signoff']
        frame.close_on_act_types = ['final_placement', 'signoff']

        call = self.call('control_H_S_3S')
        call.when = '*'
        call.bid = '3S'
        call.requires = control_context('H')
        call.applies = control_available('3S', 'S')
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['control_showing', 'slam_try', 'context_setting']
        call.meaning.action = 'control_bid'
        call.meaning.target_suit = 'S'
        call.meaning.agreed_suit = 'H'
        call.meaning.control_round = 'first_or_second'
        effect = call.effect('control')
        effect.suit = 'S'
        effect.agreed_suit = 'H'
        effect.round = 'first_or_second'
        effect.status = 'shown'
        effect = call.effect('slam_interest')
        effect.agreed_suit = 'H'
        effect.status = 'active'
        effect.source = 'control_bid'
        call.description = '3S shows first- or second-round S control with H agreed.'
        call.system_notes = 'With H agreed and slam interest active, 3S shows S control.'

        call = self.call('control_H_C_4C')
        call.when = '*'
        call.bid = '4C'
        call.requires = control_context('H')
        call.applies = control_available('4C', 'C')
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['control_showing', 'slam_try', 'context_setting']
        call.meaning.action = 'control_bid'
        call.meaning.target_suit = 'C'
        call.meaning.agreed_suit = 'H'
        call.meaning.control_round = 'first_or_second'
        effect = call.effect('control')
        effect.suit = 'C'
        effect.agreed_suit = 'H'
        effect.round = 'first_or_second'
        effect.status = 'shown'
        effect = call.effect('slam_interest')
        effect.agreed_suit = 'H'
        effect.status = 'active'
        effect.source = 'control_bid'
        call.description = '4C shows first- or second-round C control with H agreed.'
        call.system_notes = 'With H agreed and slam interest active, 4C shows C control.'

        call = self.call('control_H_D_4D')
        call.when = '*'
        call.bid = '4D'
        call.requires = control_context('H')
        call.applies = control_available('4D', 'D')
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['control_showing', 'slam_try', 'context_setting']
        call.meaning.action = 'control_bid'
        call.meaning.target_suit = 'D'
        call.meaning.agreed_suit = 'H'
        call.meaning.control_round = 'first_or_second'
        effect = call.effect('control')
        effect.suit = 'D'
        effect.agreed_suit = 'H'
        effect.round = 'first_or_second'
        effect.status = 'shown'
        effect = call.effect('slam_interest')
        effect.agreed_suit = 'H'
        effect.status = 'active'
        effect.source = 'control_bid'
        call.description = '4D shows first- or second-round D control with H agreed.'
        call.system_notes = 'With H agreed and slam interest active, 4D shows D control.'

        call = self.call('control_S_C_4C')
        call.when = '*'
        call.bid = '4C'
        call.requires = control_context('S')
        call.applies = control_available('4C', 'C')
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['control_showing', 'slam_try', 'context_setting']
        call.meaning.action = 'control_bid'
        call.meaning.target_suit = 'C'
        call.meaning.agreed_suit = 'S'
        call.meaning.control_round = 'first_or_second'
        effect = call.effect('control')
        effect.suit = 'C'
        effect.agreed_suit = 'S'
        effect.round = 'first_or_second'
        effect.status = 'shown'
        effect = call.effect('slam_interest')
        effect.agreed_suit = 'S'
        effect.status = 'active'
        effect.source = 'control_bid'
        call.description = '4C shows first- or second-round C control with S agreed.'
        call.system_notes = 'With S agreed and slam interest active, 4C shows C control.'

        call = self.call('control_S_D_4D')
        call.when = '*'
        call.bid = '4D'
        call.requires = control_context('S')
        call.applies = control_available('4D', 'D')
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['control_showing', 'slam_try', 'context_setting']
        call.meaning.action = 'control_bid'
        call.meaning.target_suit = 'D'
        call.meaning.agreed_suit = 'S'
        call.meaning.control_round = 'first_or_second'
        effect = call.effect('control')
        effect.suit = 'D'
        effect.agreed_suit = 'S'
        effect.round = 'first_or_second'
        effect.status = 'shown'
        effect = call.effect('slam_interest')
        effect.agreed_suit = 'S'
        effect.status = 'active'
        effect.source = 'control_bid'
        call.description = '4D shows first- or second-round D control with S agreed.'
        call.system_notes = 'With S agreed and slam interest active, 4D shows D control.'

        call = self.call('control_S_H_4H')
        call.when = '*'
        call.bid = '4H'
        call.requires = control_context('S')
        call.applies = control_available('4H', 'H')
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['control_showing', 'slam_try', 'context_setting']
        call.meaning.action = 'control_bid'
        call.meaning.target_suit = 'H'
        call.meaning.agreed_suit = 'S'
        call.meaning.control_round = 'first_or_second'
        effect = call.effect('control')
        effect.suit = 'H'
        effect.agreed_suit = 'S'
        effect.round = 'first_or_second'
        effect.status = 'shown'
        effect = call.effect('slam_interest')
        effect.agreed_suit = 'S'
        effect.status = 'active'
        effect.source = 'control_bid'
        call.description = '4H shows first- or second-round H control with S agreed.'
        call.system_notes = 'With S agreed and slam interest active, 4H shows H control.'

        call = self.call('control_C_H_3H')
        call.when = '*'
        call.bid = '3H'
        call.requires = control_context('C')
        call.applies = control_available('3H', 'H')
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['control_showing', 'slam_try', 'context_setting']
        call.meaning.action = 'control_bid'
        call.meaning.target_suit = 'H'
        call.meaning.agreed_suit = 'C'
        call.meaning.control_round = 'first_or_second'
        effect = call.effect('control')
        effect.suit = 'H'
        effect.agreed_suit = 'C'
        effect.round = 'first_or_second'
        effect.status = 'shown'
        effect = call.effect('slam_interest')
        effect.agreed_suit = 'C'
        effect.status = 'active'
        effect.source = 'control_bid'
        call.description = '3H shows first- or second-round H control with C agreed.'
        call.system_notes = 'With C agreed and slam interest active, 3H shows H control.'

        call = self.call('control_C_S_3S')
        call.when = '*'
        call.bid = '3S'
        call.requires = control_context('C')
        call.applies = control_available('3S', 'S')
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['control_showing', 'slam_try', 'context_setting']
        call.meaning.action = 'control_bid'
        call.meaning.target_suit = 'S'
        call.meaning.agreed_suit = 'C'
        call.meaning.control_round = 'first_or_second'
        effect = call.effect('control')
        effect.suit = 'S'
        effect.agreed_suit = 'C'
        effect.round = 'first_or_second'
        effect.status = 'shown'
        effect = call.effect('slam_interest')
        effect.agreed_suit = 'C'
        effect.status = 'active'
        effect.source = 'control_bid'
        call.description = '3S shows first- or second-round S control with C agreed.'
        call.system_notes = 'With C agreed and slam interest active, 3S shows S control.'

        call = self.call('control_C_D_4D')
        call.when = '*'
        call.bid = '4D'
        call.requires = control_context('C')
        call.applies = control_available('4D', 'D')
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['control_showing', 'slam_try', 'context_setting']
        call.meaning.action = 'control_bid'
        call.meaning.target_suit = 'D'
        call.meaning.agreed_suit = 'C'
        call.meaning.control_round = 'first_or_second'
        effect = call.effect('control')
        effect.suit = 'D'
        effect.agreed_suit = 'C'
        effect.round = 'first_or_second'
        effect.status = 'shown'
        effect = call.effect('slam_interest')
        effect.agreed_suit = 'C'
        effect.status = 'active'
        effect.source = 'control_bid'
        call.description = '4D shows first- or second-round D control with C agreed.'
        call.system_notes = 'With C agreed and slam interest active, 4D shows D control.'

        call = self.call('control_D_S_3S')
        call.when = '*'
        call.bid = '3S'
        call.requires = control_context('D')
        call.applies = control_available('3S', 'S')
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['control_showing', 'slam_try', 'context_setting']
        call.meaning.action = 'control_bid'
        call.meaning.target_suit = 'S'
        call.meaning.agreed_suit = 'D'
        call.meaning.control_round = 'first_or_second'
        effect = call.effect('control')
        effect.suit = 'S'
        effect.agreed_suit = 'D'
        effect.round = 'first_or_second'
        effect.status = 'shown'
        effect = call.effect('slam_interest')
        effect.agreed_suit = 'D'
        effect.status = 'active'
        effect.source = 'control_bid'
        call.description = '3S shows first- or second-round S control with D agreed.'
        call.system_notes = 'With D agreed and slam interest active, 3S shows S control.'

        call = self.call('control_D_C_4C')
        call.when = '*'
        call.bid = '4C'
        call.requires = control_context('D')
        call.applies = control_available('4C', 'C')
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['control_showing', 'slam_try', 'context_setting']
        call.meaning.action = 'control_bid'
        call.meaning.target_suit = 'C'
        call.meaning.agreed_suit = 'D'
        call.meaning.control_round = 'first_or_second'
        effect = call.effect('control')
        effect.suit = 'C'
        effect.agreed_suit = 'D'
        effect.round = 'first_or_second'
        effect.status = 'shown'
        effect = call.effect('slam_interest')
        effect.agreed_suit = 'D'
        effect.status = 'active'
        effect.source = 'control_bid'
        call.description = '4C shows first- or second-round C control with D agreed.'
        call.system_notes = 'With D agreed and slam interest active, 4C shows C control.'

        call = self.call('control_D_H_4H')
        call.when = '*'
        call.bid = '4H'
        call.requires = control_context('D')
        call.applies = control_available('4H', 'H')
        call.meaning.nature = ['conventional']
        call.meaning.acts = ['control_showing', 'slam_try', 'context_setting']
        call.meaning.action = 'control_bid'
        call.meaning.target_suit = 'H'
        call.meaning.agreed_suit = 'D'
        call.meaning.control_round = 'first_or_second'
        effect = call.effect('control')
        effect.suit = 'H'
        effect.agreed_suit = 'D'
        effect.round = 'first_or_second'
        effect.status = 'shown'
        effect = call.effect('slam_interest')
        effect.agreed_suit = 'D'
        effect.status = 'active'
        effect.source = 'control_bid'
        call.description = '4H shows first- or second-round H control with D agreed.'
        call.system_notes = 'With D agreed and slam interest active, 4H shows H control.'
