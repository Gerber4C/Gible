"""Small two-ply game tree for keycard continuations.

The keycard bidder should not always cash a final contract immediately.  When
there is room, the bidder can choose an invitation, observe partner's legal
reaction, and only then choose the final contract.  This module evaluates that
shape without knowing which keycard convention produced the state:

    for each candidate continuation:
        for each sampled partner hand:
            partner chooses the best legal reaction available to that hand
        average the resulting final-contract scores
    choose the continuation with the highest average

The sampler and scorer are injected so live bidding can use public-deal
sampling and DDS, while unit tests can use deterministic fakes.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, Sequence, TypeVar

T = TypeVar('T')


@dataclass(frozen=True)
class BranchResult:
    call: str
    expected_score: float
    reactions: tuple[tuple[T, str, str | None], ...]


def choose_reactive_continuation(
    candidates: Iterable[str],
    partner_hands: Sequence[T],
    *,
    responses: Callable[[str, T], Iterable[str]],
    final_contract: Callable[[str, str, T], str | None],
    score: Callable[[str, T], float],
) -> BranchResult | None:
    """Choose a continuation while preserving partner's reaction branches.

    ``responses`` must return legal partner reactions for that candidate and
    sampled hand.  A reaction with no legal final contract is ignored.  If a
    candidate has no usable reaction it is not selected.
    """
    partner_hands = tuple(partner_hands)
    if not partner_hands:
        return None
    best = None
    for candidate in candidates:
        total = 0.0
        used = 0
        reactions = []
        for partner in partner_hands:
            branch_score = None
            branch_final = None
            branch_response = None
            for response in responses(candidate, partner):
                final = final_contract(candidate, response, partner)
                if final is None:
                    continue
                value = score(final, partner)
                if branch_score is None or value > branch_score:
                    branch_score = value
                    branch_final = final
                    branch_response = response
            if branch_score is None:
                continue
            total += branch_score
            used += 1
            reactions.append((partner, branch_response, branch_final))
        if used == 0:
            continue
        expected = total / used
        if best is None or expected > best.expected_score:
            best = BranchResult(candidate, expected, tuple(reactions))
    return best
