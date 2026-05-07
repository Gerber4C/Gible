# BSL source for Partner bidding agreements.
# Edit this file as the source of truth for this Gadget object set.

Call(
    id='cs_5',
    context={'auction_pattern': '*'},
    bid='P',
    meaning={'nature_labels': ['default'],
     'call_act_types': ['final_placement'],
     'action_type': 'fallback_pass',
     'alertable': False},
    default_policy=True,
    description='Explicit fallback pass when no benchmark Call Specification applies.',
    system_notes='Undefined benchmark auctions currently fall back to pass with diagnostics.',
)

Call(
    id='cs_6',
    context={'auction_pattern': '*'},
    bid='P',
    requires={'state_exists': {'key': 'final_contract'}},
    selection={'algorithm': 'weighted_score',
     'criteria': [{'criterion_id': 'final_contract_exists',
                   'evaluator': 'state_exists',
                   'query': {'key': 'final_contract'},
                   'weight': 1}]},
    meaning={'nature_labels': ['natural'],
     'call_act_types': ['final_placement'],
     'action_type': 'pass_final_contract',
     'alertable': False},
    description='Partner passes after a final contract has been placed by any loaded benchmark Gadget.',
    system_notes='Once a final-contract state record exists, pass is the normal continuation.',
)
