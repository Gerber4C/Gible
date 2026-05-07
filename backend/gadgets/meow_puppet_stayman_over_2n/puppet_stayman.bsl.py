# BSL source for Partner bidding agreements.
# Edit this file as the source of truth for this Gadget object set.

Call(
    id='cs_1',
    context={'auction_pattern': '2NP', 'seat_positions': [1, 2, 3, 4]},
    bid='3C',
    requires={'state_exists': {'key': 'notrump_focus', 'status': 'active'}},
    selection={'algorithm': 'weighted_score',
     'criteria': [{'criterion_id': 'game_values',
                   'evaluator': 'min_value',
                   'input': 'self.hcp',
                   'min': 4,
                   'weight': 30}]},
    meaning={'nature_labels': ['artificial', 'conventional'],
     'call_act_types': ['inquiry', 'context_initiating', 'forcing'],
     'action_type': 'puppet_stayman',
     'alertable': True},
    effects=[{'key': 'puppet_stayman', 'notrump_level': 2, 'status': 'pending'}],
    description='Responder bids 3C as Puppet Stayman over 2N.',
    system_notes='After 2N, 3C is Puppet Stayman.',
)
