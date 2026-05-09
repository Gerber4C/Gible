# Partner Python-BSL source.
# This file defines one class-authored Gadget.

def cs_1_applies(ctx):
    return ((((ctx.hand.length('C') >= 7) and ctx.hand.contains_rank('C', 'A') and ctx.hand.contains_rank('C', 'K') and ctx.hand.contains_rank('C', 'Q') and not ((ctx.hand.contains_rank('S', 'A') or ctx.hand.contains_rank('S', 'K') or ctx.hand.contains_rank('H', 'A') or ctx.hand.contains_rank('H', 'K') or ctx.hand.contains_rank('D', 'A') or ctx.hand.contains_rank('D', 'K')))) or ((ctx.hand.length('D') >= 7) and ctx.hand.contains_rank('D', 'A') and ctx.hand.contains_rank('D', 'K') and ctx.hand.contains_rank('D', 'Q') and not ((ctx.hand.contains_rank('S', 'A') or ctx.hand.contains_rank('S', 'K') or ctx.hand.contains_rank('H', 'A') or ctx.hand.contains_rank('H', 'K') or ctx.hand.contains_rank('C', 'A') or ctx.hand.contains_rank('C', 'K'))))))

class MeowGambling3ntGadget(Gadget):
    id = 'meow_gambling_3nt'
    namespace = 'meow_2over1'
    name = 'Meow Gambling 3N'
    version = '0.1.0'
    description = 'Gambling 3N opening showing a solid seven-card or longer minor and no outside ace or king.\n'
    author = Author('Meow Li')

    def build(self):

        call = self.call('cs_1')
        call.seats = [1, 2, 3]
        call.bid = '3N'
        call.applies = cs_1_applies
        call.meaning.nature = ['artificial', 'conventional']
        call.meaning.acts = ['descriptive', 'preemptive', 'context_initiating']
        call.meaning.action = 'gambling_3nt_opening'
        call.meaning.target_suit = 'N'
        call.meaning.alertable = True
        call.meaning.level = 3
        effect = call.effect('gambling_3nt')
        effect.status = 'active'
        effect = call.effect('running_minor')
        effect.target_suit = {'op': 'if', 'condition': {'op': 'gte', 'left': {'op': 'length', 'hand': 'self', 'suit': 'C'}, 'right': {'const': 7}}, 'then': {'const': 'C'}, 'else': {'const': 'D'}}
        call.description = 'Opens Gambling 3N with a solid seven-card or longer minor and no outside ace or king.'
        call.system_notes = '3N opening is Gambling, showing a solid long minor and no outside ace or king.'
