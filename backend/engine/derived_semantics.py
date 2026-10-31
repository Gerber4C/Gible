"""Priority-safe dispatcher for derived bidding meanings.

Derivation only fills otherwise undefined calls. Explicit profile meanings and
committed private purposes always win; ambiguity returns a structured conflict,
never a guessed call.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .context import CallCandidate
from .derived_evidence import DerivedEvidence, collect_evidence
from .legality import legal_calls
from .matcher import matches_context
from .candidate_generation import call_for_call_specification


@dataclass(frozen=True)
class DerivationResult:
    evidence: DerivedEvidence
    candidates: tuple[CallCandidate, ...] = ()
    conflicts: tuple[dict[str, Any], ...] = ()

    @property
    def calls(self) -> tuple[str, ...]:
        return tuple(candidate.call for candidate in self.candidates)


def reserved_calls(profile, auction, trace, environment=None) -> frozenset[str]:
    """Calls whose authored definition owns this public context.

    A call stays reserved even when the current hand fails its private
    applicability, so derivation never invents a second meaning.
    """
    from .replay import _public_condition_passes
    reserved = set()
    for spec in profile.call_specifications:
        if not matches_context(spec.context, auction):
            continue
        if call_for_call_specification(spec, auction, trace) != spec.call:
            continue
        if not _public_condition_passes(spec.requires, auction, trace,
                                        environment or {}):
            continue
        reserved.add(spec.call)
    return frozenset(reserved)


def derive_candidates(profile, auction, trace, evidence: DerivedEvidence,
                      reserved: frozenset[str] = frozenset(), hand=None
                      ) -> DerivationResult:
    from . import (derived_cue, derived_fit_calls, derived_four_notrump,
                   derived_keycard_placement, derived_minor_shortage)
    from .derived_terminals import derive_six_notrump, derive_terminal_pass

    candidates = []
    conflicts = list(evidence.conflicts)
    families = (
        derived_four_notrump.derive,
        derived_fit_calls.derive,
        derived_cue.derive,
        derived_minor_shortage.derive,
        derived_keycard_placement.derive,
        derive_six_notrump,
        derive_terminal_pass,
    )
    allowed = set(legal_calls(auction)) - set(reserved)
    for family in families:
        if family in (derived_minor_shortage.derive,
                                    derive_six_notrump, derive_terminal_pass):
            result = family(profile, auction, trace, evidence, allowed, hand)
        else:
            result = family(profile, auction, trace, evidence, allowed)
        candidates.extend(result.candidates)
        conflicts.extend(result.conflicts)
    # One call may have only one derived meaning.
    grouped: dict[str, list[CallCandidate]] = {}
    for candidate in candidates:
        if candidate.call not in allowed:
            continue
        grouped.setdefault(candidate.call, []).append(candidate)
    unique = []
    for call, group in grouped.items():
        if len(group) == 1:
            unique.append(group[0])
        else:
            conflicts.append({
                'code': 'AMBIGUOUS_DERIVED_CALL',
                'call': call,
                'rules': [item.metadata.get('derived_rule') for item in group],
                'message': 'More than one derived family claims this call',
            })
    return DerivationResult(evidence, tuple(unique), tuple(conflicts))


def derived_candidate(call: str, rule: str, meaning: dict[str, Any],
                      evidence: DerivedEvidence, *,
                      effects: tuple[dict[str, Any], ...] = (),
                      confidence: float = 1.0,
                      score: int = 0) -> CallCandidate:
    origin = {'namespace': 'derived', 'object_type': 'rule',
              'object_id': rule, 'qualified_id': f'derived/rule:{rule}'}
    metadata = {
        'derived_rule': rule,
        'derived_confidence': confidence,
        'derived_plausible_trumps': list(evidence.plausible_trumps),
        'derived_evidence': {
            'agreed_trump': evidence.agreed_trump,
            'provisional_trump': evidence.provisional_trump,
            'natural_suits': evidence.natural_suits,
            'enemy_suits': list(evidence.enemy_suits),
            'contract': evidence.contract,
        },
        'derived_effects': list(effects),
    }
    return CallCandidate(
        call=call, origin=origin, public_meaning=dict(meaning),
        source_kind='derived_semantics', source_id=rule, score=score,
        criterion_results=(), capabilities=('derived_meaning',),
        metadata=metadata)
