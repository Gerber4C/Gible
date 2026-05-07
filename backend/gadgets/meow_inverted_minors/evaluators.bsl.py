# BSL source for Partner bidding agreements.
# Edit this file as the source of truth for this Gadget object set.

Evaluator(
    id='eval_stopper',
    description='Stopper evaluator for notrump exploration: ace, king, guarded queen, or length with jack.',
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
                         'right': {'const': 2}}]},
              {'op': 'and',
               'args': [{'op': 'contains_rank',
                         'hand': 'self',
                         'suit': {'param': 'target_suit'},
                         'rank': 'J'},
                        {'op': 'gte',
                         'left': {'op': 'length', 'hand': 'self', 'suit': {'param': 'target_suit'}},
                         'right': {'const': 3}}]}]},
)
