"""Grand-slam acceptance when partner invites at the seven level.

Owner rule (2026-10-27):

* A non-quantitative grand invitation (a king ask after keycard, or another
  control/showing invite) is made on the assumption that the acceptor's hand
  is in the best 15% of the range promised by its earlier bidding. Accept
  with seven when the actual hand is in that quantile.
* A quantitative five-notrump is different: it invites the top 50% of the
  range (just as quantitative 4NT invites the top half for a small slam).
  Those calls are listed explicitly by the owner:
  ``1NT-5NT``, ``1NT-2C-2D-5NT``, ``1NT-3C-3D-5NT`` and
  ``1NT-2H-2S-5NT``.

When sampled deals and a double-dummy table are available the grand
completion rate must also reach ``GRAND_QUALIFY_RATE``. If the solver is
missing, the deterministic quantile decides first (the owner's
"deterministic before DDS" rule).
"""

from __future__ import annotations

from .contract_evaluation import ContractTarget, compare_contract_targets
from .dds_adapter import DDSUnavailableError


GRAND_INVITE_QUANTILE = 0.15
QUANTITATIVE_QUANTILE = 0.50
GRAND_QUALIFY_RATE = 0.5

# The 1NT opening is 15-17 for the strong hands plus authored upgrades. A
# responder's range after a transfer is wide, so only the opener's range is
# used here; other contexts pass their own bounds.
ONE_NOTRUMP_RANGE = (15, 17)


def top_quantile_threshold(low: int, high: int, quantile: float) -> float:
    """HCP floor of the top ``quantile`` of an integer range."""
    if high <= low:
        return float(high)
    return high - quantile * (high - low)


def in_top_quantile(hand, low: int, high: int, quantile: float) -> bool:
    return hand.hcp >= top_quantile_threshold(low, high, quantile)


def quantile_for(quantitative: bool) -> float:
    return QUANTITATIVE_QUANTILE if quantitative else GRAND_INVITE_QUANTILE


def accept_grand(
    hand,
    *,
    low: int = ONE_NOTRUMP_RANGE[0],
    high: int = ONE_NOTRUMP_RANGE[1],
    quantitative: bool = False,
    deals=None,
    trump: str | None = None,
    declarer: str | None = None,
    solve_table=None,
) -> bool:
    """Return whether the hand accepts partner's grand-slam invitation.

    The deterministic quantile is the first gate. When full deals and a
    solver are supplied, the seven-level completion rate must also be at
    least ``GRAND_QUALIFY_RATE``; an unavailable solver falls back to the
    deterministic answer rather than guessing a different contract.
    """
    if not in_top_quantile(hand, low, high, quantile_for(quantitative)):
        return False
    if not deals or trump not in 'CDHS' or declarer not in 'NESW':
        return True
    table = solve_table
    if table is None:
        from .dds_adapter import calculate_available_table
        table = calculate_available_table
    try:
        estimates = compare_contract_targets(
            tuple(deals), (ContractTarget(7, trump, declarer),),
            solve_table=table)
    except DDSUnavailableError:
        return True
    return estimates[0].completion_rate >= GRAND_QUALIFY_RATE
