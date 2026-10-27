"""Shared DDS outcome metrics and warning classification rules."""

from __future__ import annotations

import math
from numbers import Real
from typing import Mapping


SET_FAILURE_THRESHOLD = .60
WRONG_RATIO_THRESHOLD = .80
BEST_OTHER_SUCCESS_FLOOR = .40
MISSED_THRESHOLD = .30
RULE_ID = 'success_probability_ratio_0.8_best_above_0.4_set_above_0.6'
GAME_TARGETS = {'3NT': ('NT', 9), '4S': ('S', 10), '4H': ('H', 10),
                '5D': ('D', 11), '5C': ('C', 11)}

_COMPUTED_FLAGS = (
    'contract_failure',
    'wrong_game',
    'missed_game',
    'missed_small_slam',
    'missed_grand_slam',
)


def _probability(value) -> float | None:
    if (isinstance(value, bool) or not isinstance(value, Real)
            or not math.isfinite(value) or not 0 <= value <= 1):
        return None
    return float(value)


def _ratio(value) -> float | None:
    if (isinstance(value, bool) or not isinstance(value, Real)
            or not math.isfinite(value) or value < 0):
        return None
    return float(value)


def available_level(table: Mapping, category: str) -> bool:
    if category == 'game':
        return (max(table['NT'][seat] for seat in 'ns') >= 9
                or any(max(table[strain][seat] for seat in 'ns') >= 10
                       for strain in 'HS')
                or any(max(table[strain][seat] for seat in 'ns') >= 11
                       for strain in 'DC'))
    if category not in ('small_slam', 'grand_slam'):
        raise ValueError(f'unknown target category: {category}')
    target = 12 if category == 'small_slam' else 13
    return any(max(table[strain][seat] for seat in 'ns') >= target
               for strain in ('S', 'H', 'D', 'C', 'NT'))


def reached_game(contract: str) -> bool:
    level, strain = int(contract[0]), contract[1:]
    return (level >= 6 or (strain == 'NT' and level >= 3)
            or (strain in ('H', 'S') and level >= 4)
            or (strain in ('C', 'D') and level >= 5))


def game_success_ratio(contract: str, declarer: str,
                       boards: list[Mapping]) -> tuple[float | None, dict[str, float]]:
    """Return chosen-game/best-other completion rate and other-game rates."""
    if contract not in GAME_TARGETS or not boards:
        return None, {}
    chosen_strain, chosen_tricks = GAME_TARGETS[contract]
    alternatives = {name: target for name, target in GAME_TARGETS.items()
                    if name != contract}
    selected_successes = sum(
        table[chosen_strain][declarer] >= chosen_tricks for table in boards)
    alternative_rates = {
        name: sum(max(table[strain][seat] for seat in 'ns') >= tricks
                  for table in boards) / len(boards)
        for name, (strain, tricks) in alternatives.items()
    }
    best_other = max(alternative_rates.values(), default=0.0)
    if best_other <= BEST_OTHER_SUCCESS_FLOOR:
        return None, alternative_rates
    return selected_successes / len(boards) / best_other, alternative_rates


def classify_rates(contract: str, rates: Mapping, alternative_rates: Mapping,
                   existing_flags=(), *, recompute_missed: bool = True) -> list[str]:
    """Classify validated aggregate rates while preserving unrelated flags."""
    replaced = set(_COMPUTED_FLAGS if recompute_missed else _COMPUTED_FLAGS[:2])
    flags = [flag for flag in existing_flags if flag not in replaced]

    contract_failure = _probability(rates.get('contract_failure'))
    if (contract_failure is not None
            and contract_failure > SET_FAILURE_THRESHOLD):
        flags.append('contract_failure')

    wrong_ratio = _ratio(rates.get('wrong_game'))
    valid_alternatives = [_probability(rate)
                          for rate in alternative_rates.values()]
    best_other = max((rate for rate in valid_alternatives if rate is not None),
                     default=None)
    if (contract in GAME_TARGETS and wrong_ratio is not None
            and wrong_ratio < WRONG_RATIO_THRESHOLD
            and best_other is not None
            and best_other > BEST_OTHER_SUCCESS_FLOOR):
        flags.append('wrong_game')

    if not recompute_missed:
        return flags

    level = int(contract[0])
    missed_game = _probability(rates.get('missed_game'))
    if (not reached_game(contract) and missed_game is not None
            and missed_game > MISSED_THRESHOLD):
        flags.append('missed_game')
    missed_small = _probability(rates.get('missed_small_slam'))
    if (level < 6 and missed_small is not None
            and missed_small > MISSED_THRESHOLD):
        flags.append('missed_small_slam')
    missed_grand = _probability(rates.get('missed_grand_slam'))
    if (level < 7 and missed_grand is not None
            and missed_grand > MISSED_THRESHOLD):
        flags.append('missed_grand_slam')
    return flags


def reclassify_analysis(contract: str, analysis: Mapping) -> dict:
    """Apply current SET/WRONG rules to stored legacy analysis evidence."""
    result = dict(analysis)
    rates = dict(analysis.get('rates') or {})
    failure = _probability(rates.get('contract_failure'))
    rates['contract_failure'] = failure

    raw_alternatives = analysis.get('alternative_game_rates') or {}
    alternatives = {name: _probability(rate)
                    for name, rate in raw_alternatives.items()}
    valid_other = [rate for name, rate in alternatives.items()
                   if name != contract and rate is not None]
    best_other = max(valid_other, default=None)
    if (contract in GAME_TARGETS and failure is not None
            and best_other is not None
            and best_other > BEST_OTHER_SUCCESS_FLOOR):
        rates['wrong_game'] = (1 - failure) / best_other
    else:
        rates['wrong_game'] = None

    result['rates'] = rates
    result['alternative_game_rates'] = alternatives
    result['flags'] = classify_rates(
        contract, rates, alternatives, analysis.get('flags') or (),
        recompute_missed=False,
    )
    return result


def board_result(contract: str, declarer: str, table: Mapping) -> dict:
    """Return one board's primary result and independent missed-target evidence."""
    level, strain = int(contract[0]), contract[1:]
    outcome = 'MAKE' if table[strain][declarer] >= level + 6 else 'SET'
    missed_target = None
    if not reached_game(contract) and available_level(table, 'game'):
        missed_target = 'game'
    if level < 6 and available_level(table, 'small_slam'):
        missed_target = 'small slam'
    if level < 7 and available_level(table, 'grand_slam'):
        missed_target = 'grand slam'
    return {'outcome': outcome, 'lose': missed_target is not None,
            'missed_target': missed_target}
