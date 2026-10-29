"""Kaplan-Rubens quality assessment using Richard Pavlicek's 26-step version.

Primary source: https://rpbridge.net/8j19.htm (accessed 2026-09-16).
Methods overview: https://rpbridge.net/ac01.htm.
The source notes an ambiguity in the original treatment of nines; this module
implements Pavlicek's explicit table, including step 8. Integer twentieths
preserve the published 0.05-point resolution. Pure K-R includes its own shape
adjustment regardless of trump and is always returned separately as kr_points.

Our classification, NOT a published K-R rule: score = kr_points - HCP plus
explicit optional context adjustments; good means score >= threshold (0.5).
HCP is never mutated and the score must not be added again to HCP requirements.
The source does not evaluate partnership context. Optional weights
partner_honors, opponent_honors and fit_shortage therefore default to zero and
are labeled extensions, never represented as pure K-R. They multiply honor
counts in the indicated suits or side-suit shortage units (3/2/1 for void/
singleton/doubleton). The latter requires an explicit trump and 3+ own trumps.
All context must come from public bidding; no actual partner hand is accepted.
Other returned features are descriptive evidence only, not weighted bonuses.
"""

from __future__ import annotations

from collections.abc import Mapping
import math
from numbers import Real

from .cards import Hand, normalize_suit_name


DEFAULT_WEIGHTS = {
    "partner_honors": 0.0,
    "opponent_honors": 0.0,
    "fit_shortage": 0.0,
    "threshold": 0.5,
}

MINOR_SLAM_KR = 14.0


def minor_slam_interest(hand: Hand) -> bool:
    """Return the shared Daqiush K-R fallback for minor-slam interest."""
    return assess_quality(hand)['kr_points'] >= MINOR_SLAM_KR


def inquiry_stopper(hand: Hand, suit: str) -> bool:
    """Return the established five-card-major-inquiry stopper predicate."""
    holding = hand.holding(suit)
    return ('A' in holding or ('K' in holding and len(holding) >= 2)
            or ('Q' in holding and ('J' in holding or 'T' in holding)))


def shapely_control_points(hand: Hand, known_long_suits) -> float:
    """Keep raw HCP in each publicly known 4+ partner suit; adjust the rest.

    The caller supplies suits learned from the auction, never from partner's
    hidden hand. This applies to every known long suit, not just the trump.
    """
    normal_suits = {normalize_suit_name(suit) for suit in known_long_suits}
    if not normal_suits:
        raise ValueError('At least one publicly known long suit is required')
    trump_points = {'A': 4.0, 'K': 3.0, 'Q': 2.0, 'J': 1.0}
    whole_suit = {
        'AKQJ': 9.0, 'AKQ': 8.4, 'AKJ': 7.3, 'AQJ': 5.8,
        'KQJ': 4.7, 'AK': 7.0, 'AQ': 5.5,
    }
    length_sensitive = {
        'AJ': (4.1, 4.4), 'KQ': (4.1, 4.4),
        'KJ': (2.9, 3.1), 'QJ': (0.4, 1.5),
    }
    single_honor = {
        'A': (4.0, 4.0, 4.0), 'K': (1.5, 2.6, 2.6),
        'Q': (0.3, 1.0, 1.3), 'J': (0.1, 0.2, 0.5),
    }

    def side_points(holding):
        honors = ''.join(rank for rank in 'AKQJ' if rank in holding)
        if honors in whole_suit:
            return whole_suit[honors]
        if honors in length_sensitive:
            return length_sensitive[honors][len(holding) >= 3]
        if honors in single_honor:
            return single_honor[honors][min(len(holding), 3) - 1]
        return 0.0
    return sum(sum(trump_points.get(rank, 0.0) for rank in holding)
               if suit in normal_suits else side_points(holding)
               for suit, holding in hand.suits.items())


def minor_game_control_points(hand: Hand, trump: str, *, partner_long_suits=()) -> float:
    """Minor invitation controls with all publicly shown partner suits retained."""
    trump = normalize_suit_name(trump)
    if trump not in ('clubs', 'diamonds'):
        raise ValueError('Minor game control points require a minor trump')
    return shapely_control_points(hand, (trump, *partner_long_suits))


def shapely_effective_points(hand: Hand, own_long_suit: str) -> float:
    """Value a shapely responder, retaining full HCP in the seven-card suit.

    Side-suit honors use the same control-sensitive table as the evaluation of
    a hand opposite a publicly shown shapely partner.
    """
    return shapely_control_points(hand, (own_long_suit,))


def shapely_combined_effective_points(hand: Hand, minimum_length: int = 4) -> float:
    """Retain ordinary honors in every known long suit of a shapely hand.

    A 6-5 or 7-4 hand must not discount honors in its second suit merely
    because the longest suit was named first.
    """
    long_suits = tuple(suit for suit in 'SHDC' if hand.length(suit) >= minimum_length)
    if not long_suits:
        raise ValueError('Shapely effective points require a long suit')
    return shapely_control_points(hand, long_suits)


def shapely_description_proxy(hand: Hand, long_suit: str) -> dict:
    """A bounded convention substitute: one fewer long card, two more points.

    This is for selecting an authored route when the exact shape has no call.
    It never changes the real hand or the points used to evaluate a contract.
    """
    suit = normalize_suit_name(long_suit)
    length = hand.length(suit)
    has_second_suit = max(hand.length(other) for other in 'SHDC'
                          if normalize_suit_name(other) != suit) >= 4
    if length < 6 or (length < 7 and not has_second_suit):
        raise ValueError('The descriptive proxy requires a 7+ suit or 6+ / 4+ two-suit hand')
    return {
        'long_suit': suit,
        'actual_length': hand.length(suit),
        'described_length': hand.length(suit) - 1,
        'effective_points': shapely_combined_effective_points(hand) + 2,
    }

FEATURE_DESCRIPTIONS = {
    "control_balance": "A/K count minus Q/J count",
    "honor_concentration": "Grouped honors in suits of at least three cards",
    "long_suit_honors": "Honors in suits of at least five cards",
    "short_unsupported_honors": "Short-suit Q/J without A/K support",
    "partner_honors": "Honors in partner's indicated suits",
    "opponent_honors": "Honors in opponents' indicated suits",
    "long_suit": "Cards beyond four in long suits",
    "fit_shortage": "Side-suit shortage with at least three agreed trumps",
}


def _kr_suit(holding: str) -> dict:
    """Evaluate one suit; numbered evidence corresponds to source table rows."""
    length = len(holding)
    cards = set(holding)
    ace, king, queen, jack, ten, nine, eight = (rank in cards for rank in "AKQJT98")
    above_queen = int(ace) + int(king)
    above_jack = above_queen + int(queen)
    above_ten = above_jack + int(jack)
    # Steps 1-11 store half-points; multiplying by length gives twentieths.
    quality = {
        1: 8 * ace,
        2: 6 * king,
        3: 4 * queen,
        4: 2 * jack,
        5: int(ten),
        6: int(2 <= length <= 6 and ten and (jack or above_jack >= 2)),
        7: int(2 <= length <= 6 and nine and (eight or ten or above_ten == 2)),
        8: int(4 <= length <= 6 and nine and not eight and not ten and above_ten == 3),
        9: 2 * int(length >= 7 and (not queen or not jack)),
        10: 2 * int(length >= 8 and not queen),
        11: 2 * int(length >= 9 and not queen and not jack),
    }
    weighted_quality = sum(quality.values()) * length
    # The remaining rows are already integer twentieths of a point.
    honor_shape = {
        13: 60 * ace,
        14: 40 * int(king and length >= 2),
        15: 10 * int(king and length == 1),
        16: 20 * int(queen and length >= 3 and above_queen >= 1),
        17: 15 * int(queen and length >= 3 and above_queen == 0),
        18: 10 * int(queen and length == 2 and above_queen >= 1),
        19: 5 * int(queen and length == 2 and above_queen == 0),
        20: 10 * int(jack and above_jack == 2),
        21: 5 * int(jack and above_jack == 1),
        22: 5 * int(ten and above_ten == 2),
        23: 5 * int(ten and nine and above_ten == 1),
        24: 60 * int(length == 0),
        25: 40 * int(length == 1),
        26: 20 * int(length == 2),
    }
    total_units = weighted_quality + sum(honor_shape.values())
    return {
        "length": length,
        "points": total_units / 20,
        "twentieths": total_units,
        "steps": {
            **{str(step): value / 2 for step, value in quality.items()},
            "12": weighted_quality / 20,
            **{str(step): value / 20 for step, value in honor_shape.items()},
        },
    }


def assess_quality(
    hand: Hand,
    partner_suits=(),
    opponent_suits=(),
    trump=None,
    weights=None,
) -> dict:
    """Return complete, reproducible quality evidence using public context.

    ``weights`` is a partial mapping of the three optional context names and/or
    ``threshold`` to finite real numbers. Unknown keys, booleans, strings,
    nonnumeric values and nonfinite values raise ValueError. Suit aliases
    accepted by Hand (S/H/D/C and full names) are normalized and deduplicated.
    """
    effective_weights = dict(DEFAULT_WEIGHTS)
    if weights is not None:
        if not isinstance(weights, Mapping):
            raise ValueError("Quality weights must be a mapping")
        for name, value in weights.items():
            if name not in DEFAULT_WEIGHTS:
                raise ValueError(f"Unknown quality weight: {name}")
            if isinstance(value, bool) or not isinstance(value, Real):
                raise ValueError(f"Quality weight {name} must be a finite number")
            try:
                numeric = float(value)
            except (OverflowError, ValueError) as exc:
                raise ValueError(f"Quality weight {name} must be a finite number") from exc
            if not math.isfinite(numeric):
                raise ValueError(f"Quality weight {name} must be a finite number")
            effective_weights[name] = numeric

    partner = {normalize_suit_name(suit) for suit in partner_suits}
    opponents = {normalize_suit_name(suit) for suit in opponent_suits}
    trump_suit = normalize_suit_name(trump) if trump is not None else None
    supported_trump = trump_suit is not None and hand.length(trump_suit) >= 3
    features = {name: 0 for name in FEATURE_DESCRIPTIONS}

    for suit_code in "SHDC":
        suit = normalize_suit_name(suit_code)
        holding = hand.holding(suit)
        length = hand.length(suit)
        controls = sum(rank in "AK" for rank in holding)
        lesser_honors = sum(rank in "QJ" for rank in holding)
        honors = controls + lesser_honors
        features["control_balance"] += controls - lesser_honors
        if length >= 3:
            features["honor_concentration"] += max(honors - 1, 0)
        if length >= 5:
            features["long_suit_honors"] += honors
        if length <= 2 and controls == 0:
            features["short_unsupported_honors"] += lesser_honors
        if suit in partner:
            features["partner_honors"] += honors
        if suit in opponents:
            features["opponent_honors"] += honors
        features["long_suit"] += max(length - 4, 0)
        if supported_trump and suit != trump_suit:
            features["fit_shortage"] += max(3 - length, 0)

    suit_evaluations = {suit: _kr_suit(hand.holding(suit)) for suit in "SHDC"}
    balanced_4333 = sorted(hand.length(suit) for suit in "SHDC") == [3, 3, 3, 4]
    final_adjustment_units = -20 + (10 if balanced_4333 else 0)
    kr_units = sum(value["twentieths"] for value in suit_evaluations.values()) + final_adjustment_units
    kr_points = kr_units / 20
    kr_delta = (kr_units - hand.hcp * 20) / 20
    context_adjustments = {
        name: features[name] * effective_weights[name]
        for name in ("partner_honors", "opponent_honors", "fit_shortage")
    }
    try:
        context_adjustment = math.fsum(context_adjustments.values())
        score = math.fsum((kr_delta, context_adjustment))
    except (OverflowError, ValueError) as exc:
        raise ValueError("Quality weights produce a nonfinite score") from exc
    if not math.isfinite(score):
        raise ValueError("Quality weights produce a nonfinite score")
    threshold = effective_weights["threshold"]
    reasons = [f"Kaplan-Rubens {kr_points:g} minus HCP {hand.hcp} = {kr_delta:+g}"]
    reasons.extend(
        f"Optional context extension — {FEATURE_DESCRIPTIONS[name]}: "
        f"{features[name]} x {effective_weights[name]:g} = {contribution:+g}"
        for name, contribution in context_adjustments.items() if contribution != 0
    )
    reasons.append(f"Project quality classification: score {score:g}; good threshold >= {threshold:g}")
    return {
        "good": score >= threshold,
        "score": score,
        "features": features,
        "reasons": reasons,
        "model": "kaplan_rubens",
        "source": "https://rpbridge.net/8j19.htm",
        "kr_points": kr_points,
        "kr_delta": kr_delta,
        "suit_evaluations": suit_evaluations,
        "kr_final_adjustment": final_adjustment_units / 20,
        "context_adjustments": context_adjustments,
        "context_adjustment": context_adjustment,
        "weights": effective_weights,
        "threshold": threshold,
        "hcp": hand.hcp,
    }
