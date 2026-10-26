"""Derive constraints on unseen hands from authored, publicly visible calls.

The evidence is declared in a call's public meaning.  Historical replay picks
that meaning without using a hidden hand; evaluators then run on *sampled*
hypothetical hands.  Neither the actual other hands nor client-supplied meaning
objects enter this module.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Mapping

from .auction import Auction
from .hand_quality import assess_quality
from .model import PartnershipProfile
from .replay import replay_auction


_ALLOWED_EVALUATORS = frozenset({
    'opening_assessment', 'texas_H_public', 'texas_S_public',
    'unprotected_kq_count',
})


@dataclass(frozen=True)
class _Promise:
    seat: str
    label: str
    evaluator: Any
    expected: Mapping[str, Any]

    def accepts(self, hand: Any) -> bool:
        ctx = SimpleNamespace(hand=hand, hand_quality=assess_quality(hand))
        result = self.evaluator(ctx)
        if 'truth_key' in self.expected:
            if not isinstance(result, Mapping):
                raise ValueError(f'{self.label} did not return a mapping')
            result = result[self.expected['truth_key']]
        if 'equals' in self.expected and result != self.expected['equals']:
            return False
        if 'min' in self.expected and result < self.expected['min']:
            return False
        if 'max' in self.expected and result > self.expected['max']:
            return False
        return True


@dataclass(frozen=True)
class PublicEvidence:
    constraints: dict[str, dict[str, Any]]
    promises: tuple[_Promise, ...]

    @property
    def labels(self) -> tuple[str, ...]:
        return tuple(item.label for item in self.promises)

    def accepts(self, deal: Mapping[str, Any]) -> bool:
        return all(item.accepts(deal[item.seat]) for item in self.promises)


def _merge_bounds(target: dict[str, Any], added: Mapping[str, Any]) -> None:
    for key, value in added.items():
        if key in ('min_hcp', 'max_hcp'):
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f'invalid public {key}')
            previous = target.get(key)
            target[key] = (max if key.startswith('min') else min)(previous, value) if previous is not None else value
        elif key in ('min_lengths', 'max_lengths') and isinstance(value, Mapping):
            existing = target.setdefault(key, {})
            for suit, length in value.items():
                if suit not in 'SHDC' or isinstance(length, bool) or not isinstance(length, int):
                    raise ValueError(f'invalid public {key}')
                previous = existing.get(suit)
                existing[suit] = (max if key.startswith('min') else min)(previous, length) if previous is not None else length
        else:
            raise ValueError(f'unsupported public bound: {key}')


def derive_public_evidence(profile: PartnershipProfile, auction: Auction) -> PublicEvidence:
    """Replay an auction and collect machine-readable public hand promises.

    Undefined/ambiguous non-Pass calls are refused.  A broad sample that silently
    ignores a known convention would misstate the chance of making a contract.
    """
    trace = replay_auction(profile, auction)
    if trace.diagnostics:
        raise ValueError('Auction lacks an unambiguous public meaning: ' + '; '.join(trace.diagnostics))
    evaluators = {item.id: item.definition for item in profile.named_evaluators
                  if item.evaluator_type == 'python_function'}
    constraints: dict[str, dict[str, Any]] = {}
    promises: list[_Promise] = []
    for entry in trace.applied_meanings:
        declaration = entry['public_meaning'].get('public_evidence')
        if declaration is None:
            if entry['call'] != 'P':
                raise ValueError(f"No sampling evidence for public call {entry['call']} at auction position {entry['index'] + 1}")
            continue
        if not isinstance(declaration, Mapping):
            raise ValueError('public_evidence must be a mapping')
        label = declaration.get('evaluator')
        if label not in _ALLOWED_EVALUATORS or label not in evaluators or not callable(evaluators[label]):
            raise ValueError(f'unsupported public evaluator: {label}')
        seat = entry['seat']
        _merge_bounds(constraints.setdefault(seat, {}), declaration.get('bounds', {}))
        checks = {key: declaration[key] for key in ('truth_key', 'equals', 'min', 'max')
                  if key in declaration}
        if not checks:
            raise ValueError(f'public evaluator {label} has no acceptance condition')
        promises.append(_Promise(seat, label, evaluators[label], checks))
    return PublicEvidence(constraints, tuple(promises))
