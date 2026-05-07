# BSL source for Partner bidding agreements.
# Edit this file as the source of truth for this Gadget object set.

Evaluator(
    id='eval_minor_honor_third',
    description='Target minor has at least three cards and at least one of A, K, or Q.',
    system_notes='Minor-transfer superaccept support requires honor-third or stronger in the target minor.',
    evaluator_type='expression',
    definition={'op': 'and',
     'args': [{'op': 'gte',
               'left': {'op': 'length', 'hand': 'self', 'suit': {'param': 'target_suit'}},
               'right': {'const': 3}},
              {'op': 'gte',
               'left': {'op': 'honor_count',
                        'hand': 'self',
                        'suit': {'param': 'target_suit'},
                        'ranks': ['A', 'K', 'Q']},
               'right': {'const': 1}}]},
)
