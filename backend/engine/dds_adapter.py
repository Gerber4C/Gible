"""Optional double-dummy analysis for a *complete* four-hand deal.

This adapter is for after-the-deal analysis. Never pass its full-deal results
to the bidding selector, which must use only the acting player's known hand.

The official DDS Python package is ``dds3`` from https://github.com/dds-bridge/dds.
Pin an integration to a Git revision of that repository, rather than assuming
that a wheel version uniquely identifies its C++ solver implementation.
"""

from __future__ import annotations

import importlib
import importlib.metadata
from collections.abc import Mapping

from .cards import Hand


SEATS = ('n', 'e', 's', 'w')
SUITS = ('S', 'H', 'D', 'C')
STRAINS = (*SUITS, 'NT')
RANKS = 'AKQJT98765432'


class DDSUnavailableError(RuntimeError):
    """The optional official DDS Python package cannot be imported."""


def available_solver_info() -> dict[str, str | None]:
    """Identify the local solver package used by calculate_available_table."""
    for package in ('dds3', 'endplay'):
        try:
            importlib.import_module(package)
        except ImportError:
            continue
        try:
            version = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            version = None
        return {'package': package, 'version': version}
    return {'package': None, 'version': None}


def deal_to_pbn(hands: Mapping[str, Hand | str]) -> str:
    """Validate and encode a full deal as ``N:... ... ... ...`` PBN.

    ``hands`` must have exactly the lowercase keys ``n``, ``e``, ``s``, ``w``.
    Values may be :class:`engine.cards.Hand` instances or compact strings such
    as ``"SAKQHJTD32C98765"``. Each hand must have 13 known cards, and each
    card must occur exactly once across all four hands. Output is always in
    North, East, South, West order with suits Spades, Hearts, Diamonds, Clubs
    and ranks high to low. Empty suits are represented by empty PBN fields.
    """
    if not isinstance(hands, Mapping) or set(hands) != set(SEATS):
        raise ValueError('deal must have exactly the seats n, e, s, w')

    seen: set[tuple[str, str]] = set()
    pbn_hands: list[str] = []
    for seat in SEATS:
        value = hands[seat]
        if isinstance(value, str):
            value = Hand.parse(value)
        if not isinstance(value, Hand):
            raise TypeError(f'{seat} hand must be a Hand or compact string')

        fields: list[str] = []
        total = 0
        for suit in SUITS:
            holding = value.holding(suit)
            if not isinstance(holding, str):
                raise ValueError(f'{seat} has an invalid {suit} holding')
            total += len(holding)
            for rank in holding:
                if rank not in RANKS:
                    raise ValueError(f'{seat} has an unknown or invalid card rank: {rank}')
                card = (suit, rank)
                if card in seen:
                    raise ValueError(f'duplicate card in deal: {suit}{rank}')
                seen.add(card)
            fields.append(''.join(rank for rank in RANKS if rank in holding))
        if total != 13:
            raise ValueError(f'{seat} hand must contain 13 cards, got {total}')
        pbn_hands.append('.'.join(fields))

    if len(seen) != 52:
        raise ValueError(f'deal must contain 52 unique cards, got {len(seen)}')
    return 'N:' + ' '.join(pbn_hands)


def calculate_double_dummy_table(
    hands: Mapping[str, Hand | str], *, dds_module=None,
) -> dict[str, dict[str, int]]:
    """Return declarer tricks by strain (``S,H,D,C,NT``) and seat (``n,e,s,w``).

    Calls official ``dds3.calc_all_tables_pbn([pbn], mode=-1)``. The package is
    loaded only when this function is called; ``dds_module`` permits a caller
    to provide the same API directly, which is useful for deterministic tests.
    """
    pbn = deal_to_pbn(hands)
    if dds_module is None:
        try:
            dds_module = importlib.import_module('dds3')
        except ImportError as exc:
            raise DDSUnavailableError(
                'dds3 is unavailable; install the official dds-bridge/dds Python '
                'package built from a pinned Git revision.'
            ) from exc

    result = dds_module.calc_all_tables_pbn([pbn], mode=-1)
    try:
        if result['no_of_boards'] != 1 or len(result['tables']) != 1:
            raise ValueError('expected one table')
        matrix = result['tables'][0]['res_table']
        if len(matrix) != 5 or any(len(row) != 4 for row in matrix):
            raise ValueError('expected a 5x4 res_table')
        if any(isinstance(tricks, bool) or not isinstance(tricks, int) or not 0 <= tricks <= 13
               for row in matrix for tricks in row):
            raise ValueError('expected integer trick counts from 0 to 13')
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise RuntimeError(f'dds3 returned an invalid 5x4 table: {exc}') from exc

    return {
        strain: {seat: matrix[row][column] for column, seat in enumerate(SEATS)}
        for row, strain in enumerate(STRAINS)
    }


def calculate_endplay_table(hands: Mapping[str, Hand | str]) -> dict[str, dict[str, int]]:
    """Use endplay's bundled DDS solver where official dds3 is unavailable.

    endplay 0.5.12 publishes Windows and Linux wheels.  Keep the output shape
    identical to the official adapter; the known-deal test checks seat order.
    """
    pbn = deal_to_pbn(hands)
    try:
        from endplay.dds import calc_dd_table
        from endplay.types import Deal, Denom, Player
    except ImportError as exc:
        raise DDSUnavailableError(
            'No double-dummy solver is installed. Install endplay==0.5.12 '
            'or build official dds3 from a pinned revision.'
        ) from exc
    table = calc_dd_table(Deal(pbn))
    denoms = {'S': Denom.spades, 'H': Denom.hearts, 'D': Denom.diamonds,
              'C': Denom.clubs, 'NT': Denom.nt}
    players = {'n': Player.north, 'e': Player.east,
               's': Player.south, 'w': Player.west}
    return {strain: {seat: int(table[denoms[strain], players[seat]]) for seat in SEATS}
            for strain in STRAINS}


def calculate_available_table(hands: Mapping[str, Hand | str]) -> dict[str, dict[str, int]]:
    """Prefer official dds3, then an endplay wheel containing DDS."""
    try:
        importlib.import_module('dds3')
    except ImportError:
        return calculate_endplay_table(hands)
    return calculate_double_dummy_table(hands)
