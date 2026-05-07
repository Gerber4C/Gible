# BSL source for Partner bidding agreements.
# Edit this file as the source of truth for this Gadget object set.

Evaluator(
    id='eval_crisscross_stopper',
    description='Stopper evaluator used by crisscross notrump continuations.',
    evaluator_type='expression',
    definition={'op': 'or',
     'args': [{'op': 'contains_rank', 'hand': 'self', 'suit': {'param': 'target_suit'}, 'rank': 'A'},
              {'op': 'contains_rank', 'hand': 'self', 'suit': {'param': 'target_suit'}, 'rank': 'K'},
              {'op': 'and',
               'args': [{'op': 'contains_rank',
                         'hand': 'self',
                         'suit': {'param': 'target_suit'},
                         'rank': 'Q'},
                        {'op': 'gte',
                         'left': {'op': 'length', 'hand': 'self', 'suit': {'param': 'target_suit'}},
                         'right': {'const': 2}}]}]},
)
