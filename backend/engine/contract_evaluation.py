"""Compare separately declared contract targets over the same sampled deals.

This module is analysis-only: it does not create bidding candidates or choose a
call. The supplied table solver may be the DDS adapter or a test implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping


_STRAINS = frozenset(("C", "D", "H", "S", "NT"))
_SEATS = frozenset(("n", "e", "s", "w"))


@dataclass(frozen=True)
class ContractTarget:
    level: int
    strain: str
    declarer: str

    def __post_init__(self) -> None:
        if isinstance(self.level, bool) or not isinstance(self.level, int) or not 1 <= self.level <= 7:
            raise ValueError("Contract level must be an integer from 1 to 7")
        if self.strain not in _STRAINS:
            raise ValueError("Contract strain must be C, D, H, S or NT")
        if self.declarer not in _SEATS:
            raise ValueError("Declarer must be n, e, s or w")

    @property
    def contract(self) -> str:
        return f"{self.level}{self.strain}"

    @property
    def tricks_required(self) -> int:
        return self.level + 6


@dataclass(frozen=True)
class ContractEstimate:
    contract: str
    declarer: str
    made: int
    sample_count: int

    @property
    def completion_rate(self) -> float:
        return self.made / self.sample_count

    def to_dict(self) -> dict[str, Any]:
        return {
            "contract": self.contract,
            "declarer": self.declarer,
            "made": self.made,
            "sample_count": self.sample_count,
            "completion_rate": self.completion_rate,
        }


def compare_contract_targets(
    deals: Iterable[Any],
    targets: Iterable[ContractTarget],
    *,
    solve_table: Callable[[Any], Mapping[str, Mapping[str, int]]],
) -> tuple[ContractEstimate, ...]:
    """Evaluate target completion, retaining target level and declarer separately."""
    target_list = tuple(targets)
    if not target_list:
        raise ValueError("At least one target contract is required")
    if any(not isinstance(target, ContractTarget) for target in target_list):
        raise ValueError("All targets must be ContractTarget values")
    counts = [0] * len(target_list)
    sample_count = 0
    for deal in deals:
        table = solve_table(deal)
        for index, target in enumerate(target_list):
            try:
                tricks = table[target.strain][target.declarer]
            except (KeyError, TypeError) as exc:
                raise ValueError(f"Solver table lacks {target.strain}/{target.declarer}") from exc
            if isinstance(tricks, bool) or not isinstance(tricks, int) or not 0 <= tricks <= 13:
                raise ValueError("Solver trick count must be an integer from 0 to 13")
            counts[index] += tricks >= target.tricks_required
        sample_count += 1
    if not sample_count:
        raise ValueError("At least one sampled deal is required")
    return tuple(
        ContractEstimate(target.contract, target.declarer, made, sample_count)
        for target, made in zip(target_list, counts)
    )
