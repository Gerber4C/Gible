"""Base Petkov Zar scoring with conservative, non-integrated fit handling."""

from __future__ import annotations

from dataclasses import dataclass

from .cards import Hand, SUITS


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
    raise NotImplementedError("Fit-aware Zar evaluation is not implemented")
