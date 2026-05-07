# BSL source for Partner bidding agreements.
# Edit this file as the source of truth for this Gadget object set.

Call(
    id='cs_1',
    context={'auction_pattern': ''},
    bid='4N',
    selection={'algorithm': 'weighted_score',
     'criteria': [{'criterion_id': 'always',
                   'evaluator': 'min_value',
                   'input': 'self.hcp',
                   'min': 0,
                   'weight': 100}]},
    meaning={'nature_labels': ['artificial'],
     'call_act_types': ['inquiry'],
     'action_type': 'test_meaning_a',
     'alertable': False},
    description='Test 4N meaning A.',
)

Call(
    id='cs_2',
    context={'auction_pattern': ''},
    bid='4N',
    selection={'algorithm': 'weighted_score',
     'criteria': [{'criterion_id': 'always',
                   'evaluator': 'min_value',
                   'input': 'self.hcp',
                   'min': 0,
                   'weight': 100}]},
    meaning={'nature_labels': ['natural'],
     'call_act_types': ['invitation'],
     'action_type': 'test_meaning_b',
     'alertable': False},
    description='Test 4N meaning B.',
)
