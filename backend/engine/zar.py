"""Base Petkov Zar scoring with conservative, non-integrated fit handling."""

from __future__ import annotations

from dataclasses import dataclass

from .cards import Hand, SUITS, normalize_suit_name


VERSION = "conservative"


@dataclass(frozen=True)
class ZarFitContext:
    trump_suit: str
    combined_trumps: int
    secondary_suit: str | None = None
    combined_secondary: int | None = None


@dataclass(frozen=True)
class ZarEvaluation:
    version: str
    hcp: int
    controls: int
    shape_points: int
    base_points: int
    primary_fit_points: int
    secondary_fit_points: int
    total_points: int


def evaluate_zar(hand: Hand, fit: ZarFitContext | None = None) -> ZarEvaluation:
    lengths = sorted((hand.length(suit) for suit in SUITS), reverse=True)
    longest, second_longest, _, shortest = lengths
    controls = 2 * hand.ace_count() + hand.king_count()
    shape_points = longest + second_longest + longest - shortest
    base_points = hand.hcp + controls + shape_points

    primary_fit_points = 0
    secondary_fit_points = 0
    if fit is not None:
        primary_fit_points, secondary_fit_points = _fit_points(hand, fit)

    return ZarEvaluation(
        version=VERSION,
        hcp=hand.hcp,
        controls=controls,
        shape_points=shape_points,
        base_points=base_points,
        primary_fit_points=primary_fit_points,
        secondary_fit_points=secondary_fit_points,
        total_points=base_points + primary_fit_points + secondary_fit_points,
    )


def _fit_points(hand: Hand, fit: ZarFitContext) -> tuple[int, int]:
    trump = normalize_suit_name(fit.trump_suit)
    combined_trumps = _validate_combined_length(
        fit.combined_trumps,
        "combined_trumps",
    )
    if combined_trumps < hand.length(trump):
        raise ValueError("combined_trumps cannot be shorter than own trump holding")

    shortest_side_suit = min(
        hand.length(suit) for suit in SUITS if suit != trump
    )
    shortness_multiplier = (
        2 if shortest_side_suit == 0 else 1 if shortest_side_suit == 1 else 0
    )
    primary_fit_points = (combined_trumps - 8) * shortness_multiplier

    has_secondary_suit = fit.secondary_suit is not None
    has_secondary_length = fit.combined_secondary is not None
    if not has_secondary_suit and not has_secondary_length:
        return primary_fit_points, 0
    if has_secondary_suit != has_secondary_length:
        raise ValueError(
            "secondary_suit and combined_secondary must be supplied together"
        )

    secondary = normalize_suit_name(fit.secondary_suit)
    if secondary == trump:
        raise ValueError("secondary_suit must differ from trump_suit")
    combined_secondary = _validate_combined_length(
        fit.combined_secondary,
        "combined_secondary",
    )
    own_secondary = hand.length(secondary)
    if combined_secondary < own_secondary:
        raise ValueError(
            "combined_secondary cannot be shorter than own secondary holding"
        )
    if own_secondary < 3:
        raise ValueError("own secondary holding must contain at least 3 cards")

    partner_secondary = combined_secondary - own_secondary
    if partner_secondary < 3:
        raise ValueError("partner secondary holding must contain at least 3 cards")
    partner_trumps = combined_trumps - hand.length(trump)
    if partner_trumps + partner_secondary > 13:
        raise ValueError("implied partner suit lengths cannot exceed 13 cards")

    secondary_fit_points = min(combined_secondary - 8, 2)
    return primary_fit_points, secondary_fit_points


def _validate_combined_length(value: object, field_name: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not 0 <= value <= 13
    ):
        raise ValueError(f"{field_name} must be an integer from 0 to 13")
    if value < 8:
        raise ValueError(f"{field_name} must be at least 8")
    return value
