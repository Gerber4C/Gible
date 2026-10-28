"""Deterministic North opener strata and South-cell allocation.

This module is deliberately independent from :mod:`coverage_scan`: schedule
construction must remain pure, fast, and free of card generation or bidding.
Shapes throughout are in named S/H/D/C order.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from itertools import permutations, product
from typing import Iterable, Mapping, Sequence


REQUIRED_CELLS = 92
OPENER_MODES = frozenset({'normal', 'upgrade_14', 'soft_18'})
_NORMAL_FAMILIES = (
    (4, 3, 3, 3),
    (4, 4, 3, 2),
    (5, 3, 3, 2),
    (6, 3, 2, 2),
    (5, 4, 2, 2),
    (4, 4, 4, 1),
    (5, 4, 3, 1),
)
_MODE_MIN_HCP = {'normal': 15, 'upgrade_14': 14, 'soft_18': 18}
_MODE_MAX_HCP = {'normal': 17, 'upgrade_14': 14, 'soft_18': 18}
_HONOR_POINTS = (4, 3, 2, 1)


def _shape(value: object, field: str) -> tuple[int, int, int, int]:
    if not isinstance(value, (list, tuple)) or len(value) != 4:
        raise ValueError(f'{field} must contain four suit lengths')
    if any(not isinstance(length, int) or isinstance(length, bool)
           for length in value):
        raise ValueError(f'{field} suit lengths must be integers')
    result = tuple(value)
    if any(length < 0 or length > 13 for length in result):
        raise ValueError(f'{field} suit lengths must be between 0 and 13')
    if sum(result) != 13:
        raise ValueError(f'{field} must total 13')
    return result


@dataclass(frozen=True, order=True)
class OpenerStratum:
    """One named North shape and opening-strength mode."""

    shape: tuple[int, int, int, int]
    mode: str

    def __post_init__(self) -> None:
        canonical = _shape(self.shape, 'shape')
        if canonical != self.shape or not isinstance(self.shape, tuple):
            raise ValueError('shape must be a four-integer tuple totaling 13')
        if self.mode not in OPENER_MODES:
            raise ValueError(f'unknown opener mode: {self.mode!r}')


def stratum_key(item: OpenerStratum) -> str:
    """Return the stable textual identifier used in reports."""

    return f"{item.mode}:{'-'.join(map(str, item.shape))}"


def _legal_normal_shape(shape: tuple[int, int, int, int]) -> bool:
    spades, hearts, _, _ = shape
    return (spades < 6 and hearts < 6
            and not (spades >= 5 and hearts >= 4)
            and not (hearts >= 5 and spades >= 4))


def normal_named_shapes() -> tuple[tuple[int, int, int, int], ...]:
    """Enumerate the 68 legal ordinary 1NT shapes in S/H/D/C order."""

    return tuple(sorted({
        shape
        for family in _NORMAL_FAMILIES
        for shape in permutations(family)
        if _legal_normal_shape(shape)
    }))


def _merge_by_normalized_rank(
        normal: Sequence[OpenerStratum],
        exceptional: Sequence[OpenerStratum]) -> tuple[OpenerStratum, ...]:
    """Merge pools by midpoint rank using exact integer comparisons."""

    merged = []
    normal_index = exceptional_index = 0
    while normal_index < len(normal) and exceptional_index < len(exceptional):
        normal_rank = (2 * normal_index + 1) * len(exceptional)
        exceptional_rank = (2 * exceptional_index + 1) * len(normal)
        if normal_rank <= exceptional_rank:
            merged.append(normal[normal_index])
            normal_index += 1
        else:
            merged.append(exceptional[exceptional_index])
            exceptional_index += 1
    merged.extend(normal[normal_index:])
    merged.extend(exceptional[exceptional_index:])
    return tuple(merged)


def required_opener_strata() -> tuple[OpenerStratum, ...]:
    """Return the stable, evenly interleaved 92-stratum base sequence."""

    shapes = normal_named_shapes()
    normal = tuple(OpenerStratum(shape, 'normal') for shape in shapes)
    upgrades = tuple(OpenerStratum(shape, 'upgrade_14') for shape in shapes
                     if tuple(sorted(shape, reverse=True)) == (5, 3, 3, 2))
    soft = tuple(OpenerStratum(shape, 'soft_18') for shape in shapes
                 if tuple(sorted(shape, reverse=True)) == (4, 4, 3, 2))
    exceptional = tuple(
        item
        for pair in zip(upgrades, soft)
        for item in pair
    )
    return _merge_by_normalized_rank(normal, exceptional)


def rotate_responder_shape(
        base_shape: Sequence[int], target_hcp: int,
        base_shape_index: int) -> tuple[int, int, int, int]:
    """Rotate a responder base shape left by the one shared schedule rule."""

    shape = _shape(base_shape, 'base_shape')
    if not isinstance(target_hcp, int) or isinstance(target_hcp, bool):
        raise ValueError('target_hcp must be an integer')
    if not isinstance(base_shape_index, int) or isinstance(base_shape_index, bool):
        raise ValueError('base_shape_index must be an integer')
    offset = (target_hcp + base_shape_index) % 4
    return shape[offset:] + shape[:offset]


def _integer_field(value: object, field: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f'{field} must be an integer')
    if value < 0:
        raise ValueError(f'{field} must be non-negative')
    return value


def _unknown_fields(fields: Iterable[object]) -> str:
    return ', '.join(sorted(str(field) for field in fields))


def validate_cell_identity(cell: object) -> dict[str, int]:
    """Validate and copy an exact two-field summary cell identity."""

    if not isinstance(cell, Mapping):
        raise ValueError('cell identity must be an object')
    required = {'target_hcp', 'base_shape_index'}
    missing = required - set(cell)
    if missing:
        raise ValueError(f'missing {sorted(missing)[0]}')
    extra = set(cell) - required
    if extra:
        raise ValueError(f'unknown fields: {_unknown_fields(extra)}')
    return {
        'target_hcp': _integer_field(cell['target_hcp'], 'target_hcp'),
        'base_shape_index': _integer_field(
            cell['base_shape_index'], 'base_shape_index'),
    }


def _validate_explicit_cell(cell: object) -> dict[str, object]:
    if not isinstance(cell, Mapping):
        raise ValueError('coverage cell must be an object')
    required = {
        'target_hcp', 'base_shape_index', 'base_shape', 'pair_slot',
        'opener_shape', 'opener_mode',
    }
    missing = required - set(cell)
    if missing:
        raise ValueError(f'missing {sorted(missing)[0]}')
    extra = set(cell) - required
    if extra:
        raise ValueError(f'unknown fields: {_unknown_fields(extra)}')
    identity = validate_cell_identity({key: cell[key] for key in (
        'target_hcp', 'base_shape_index')})
    mode = cell['opener_mode']
    if not isinstance(mode, str) or mode not in OPENER_MODES:
        raise ValueError(f'opener_mode is unknown: {mode!r}')
    return {
        **identity,
        'base_shape': _shape(cell['base_shape'], 'base_shape'),
        'pair_slot': _integer_field(cell['pair_slot'], 'pair_slot'),
        'opener_shape': _shape(cell['opener_shape'], 'opener_shape'),
        'opener_mode': mode,
    }


def validate_explicit_coverage_cell(
        cell: object, *, siblings: Iterable[object] = ()) -> dict[str, object]:
    """Validate full generation metadata and same-cell sibling consistency."""

    validated = _validate_explicit_cell(cell)
    identity_fields = ('target_hcp', 'base_shape_index')
    metadata_fields = ('base_shape', 'opener_shape', 'opener_mode')
    for sibling in siblings:
        other = _validate_explicit_cell(sibling)
        for field in identity_fields + metadata_fields:
            if other[field] != validated[field]:
                raise ValueError(f'inconsistent sibling {field}')
    return validated


@dataclass(frozen=True)
class _QuotaSlot:
    stratum: OpenerStratum
    occurrence: int


class OpenerAllocationError(ValueError):
    """Raised when quota-preserving compatible allocation is impossible."""

    def __init__(self, available_cells: int, required_cells: int,
                 unmatched_slots: Iterable[_QuotaSlot]):
        self.available_cells = available_cells
        self.required_cells = required_cells
        self.unmatched_slots = tuple({
            'shape': slot.stratum.shape,
            'mode': slot.stratum.mode,
            'occurrence': slot.occurrence,
        } for slot in unmatched_slots)
        keys = ', '.join(
            f"{item['mode']}:{'-'.join(map(str, item['shape']))}"
            f"#{item['occurrence']}"
            for item in self.unmatched_slots)
        super().__init__(
            f'cannot allocate opener strata: available_cells={available_cells}, '
            f'required_cells={required_cells}, unmatched_slots=[{keys}]')


@dataclass(frozen=True)
class _SouthCell:
    identity: tuple[int, int]
    shape: tuple[int, int, int, int]


def _south_cell(value: object) -> _SouthCell:
    if not isinstance(value, Mapping):
        raise ValueError('South cell must be an object')
    required = {'target_hcp', 'base_shape_index', 'base_shape'}
    missing = required - set(value)
    if missing:
        raise ValueError(f'missing {sorted(missing)[0]}')
    extra = set(value) - required
    if extra:
        raise ValueError(f'unknown fields: {_unknown_fields(extra)}')
    identity = validate_cell_identity({
        'target_hcp': value['target_hcp'],
        'base_shape_index': value['base_shape_index'],
    })
    rotated = rotate_responder_shape(
        value['base_shape'], identity['target_hcp'],
        identity['base_shape_index'])
    return _SouthCell(
        (identity['target_hcp'], identity['base_shape_index']), rotated)


@lru_cache(maxsize=None)
def _suit_hcp_totals(north_length: int, south_length: int,
                     require_honor_singleton: bool) -> frozenset[tuple[int, int]]:
    """Return attainable North/South HCP pairs for one named suit."""

    totals = set()
    for owners in product(range(3), repeat=len(_HONOR_POINTS)):
        north_honors = tuple(
            index for index, owner in enumerate(owners) if owner == 0)
        south_honors = tuple(
            index for index, owner in enumerate(owners) if owner == 1)
        if (len(north_honors) > north_length
                or len(south_honors) > south_length
                or (north_length - len(north_honors)
                    + south_length - len(south_honors) > 9)):
            continue
        if (require_honor_singleton and north_length == 1
                and (len(north_honors) != 1 or north_honors[0] == 3)):
            continue
        totals.add((
            sum(_HONOR_POINTS[index] for index in north_honors),
            sum(_HONOR_POINTS[index] for index in south_honors),
        ))
    return frozenset(totals)


@lru_cache(maxsize=None)
def _hcp_bounds(
        suit_pairs: tuple[tuple[int, int], ...],
        honor_singleton: bool) -> tuple[int, ...]:
    """Return necessary aggregate HCP bounds for a sequence of suit lengths."""

    north_min = north_max = south_min = south_max = 0
    partnership_min = partnership_max = 0
    for north_length, south_length in suit_pairs:
        suit_totals = _suit_hcp_totals(
            north_length, south_length, honor_singleton)
        north_values = tuple(item[0] for item in suit_totals)
        south_values = tuple(item[1] for item in suit_totals)
        partnership_values = tuple(sum(item) for item in suit_totals)
        north_min += min(north_values)
        north_max += max(north_values)
        south_min += min(south_values)
        south_max += max(south_values)
        partnership_min += min(partnership_values)
        partnership_max += max(partnership_values)
    return (north_min, north_max, south_min, south_max,
            partnership_min, partnership_max)


def _shape_hcp_bounds(
        north_shape: tuple[int, int, int, int],
        south_shape: tuple[int, int, int, int]) -> tuple[int, ...]:
    """Return necessary aggregate HCP bounds for two named shapes."""

    return _hcp_bounds(tuple(zip(north_shape, south_shape)), 1 in north_shape)


@lru_cache(maxsize=None)
def _soft_doubleton_south_hcp(south_length: int) -> frozenset[int]:
    """Return South HCPs attainable opposite a pinned North QJ doubleton."""

    result = set()
    for honor_count in range(3):  # 0, 1, or 2 of {A, K}
        if honor_count > south_length:
            continue
        if south_length - honor_count > 9:  # only nine ranks below the jack
            continue
        if honor_count == 0:
            result.add(0)
        elif honor_count == 1:
            result.update((3, 4))  # king or ace
        else:
            result.add(7)  # ace and king
    return frozenset(result)


def _soft_18_hcp_feasible(
        north_shape: tuple[int, int, int, int],
        south_shape: tuple[int, int, int, int],
        south_hcp: int) -> bool:
    """Check soft-18 HCP attainability with the QJ doubleton pinned.

    ``soft_18`` pins one North suit to exactly Q-J (two HCP), so the other
    three suits must supply exactly sixteen HCP for North while South carries
    the remaining honours.  This is the cheap necessary relaxation: it sums
    per-suit minima/maxima rather than enumerating every holding, so it can
    only reject provably impossible assignments, never a legal hand.
    """

    doubleton_index = north_shape.index(2)
    free_pairs = tuple(
        (north_length, south_length)
        for index, (north_length, south_length)
        in enumerate(zip(north_shape, south_shape))
        if index != doubleton_index
    )
    (north_min, north_max, south_min, south_max,
     partnership_min, partnership_max) = _hcp_bounds(free_pairs, False)
    north_need = 18 - 2
    for south_doubleton in _soft_doubleton_south_hcp(
            south_shape[doubleton_index]):
        south_need = south_hcp - south_doubleton
        if not north_min <= north_need <= north_max:
            continue
        if not south_min <= south_need <= south_max:
            continue
        if not partnership_min <= north_need + south_need <= partnership_max:
            continue
        return True
    return False


def _hcp_feasible(stratum: OpenerStratum,
                  south_shape: tuple[int, int, int, int],
                  south_hcp: int) -> bool:
    """Check exact HCP attainability, ignoring the costlier K-R predicates."""

    mode_min = _MODE_MIN_HCP[stratum.mode]
    mode_max = _MODE_MAX_HCP[stratum.mode]
    if stratum.mode == 'soft_18':
        return _soft_18_hcp_feasible(stratum.shape, south_shape, south_hcp)
    (north_min, north_max, south_min, south_max,
     partnership_min, partnership_max) = _shape_hcp_bounds(
         stratum.shape, south_shape)
    return (south_min <= south_hcp <= south_max
            and north_min <= mode_max and mode_min <= north_max
            and partnership_min <= mode_max + south_hcp
            and mode_min + south_hcp <= partnership_max)


def _compatible(slot: _QuotaSlot, cell: _SouthCell) -> bool:
    return (all(north + south <= 13
                for north, south in zip(slot.stratum.shape, cell.shape))
            and _hcp_feasible(slot.stratum, cell.shape, cell.identity[0]))


def _stable_cell_order(cell: _SouthCell) -> tuple[bytes, tuple[int, int]]:
    hcp, shape_index = cell.identity
    key = f'north-stratum-v1:{hcp}:{shape_index}'.encode('ascii')
    return sha256(key).digest(), cell.identity


def _selected_slots(count: int) -> tuple[_QuotaSlot, ...]:
    base = required_opener_strata()
    if count < len(base):
        selected = list(base[:count])
    else:
        normal = tuple(OpenerStratum(shape, 'normal')
                       for shape in normal_named_shapes())
        selected = list(base)
        selected.extend(normal[index % len(normal)]
                        for index in range(count - len(base)))
    occurrences: Counter[OpenerStratum] = Counter()
    slots = []
    for stratum in selected:
        slots.append(_QuotaSlot(stratum, occurrences[stratum]))
        occurrences[stratum] += 1
    return tuple(slots)


def allocate_opener_strata(cells: Iterable[object]) -> dict[str, object]:
    """Match deterministic opener quotas to compatible stable South cells."""

    south_cells = tuple(_south_cell(cell) for cell in cells)
    identities = [cell.identity for cell in south_cells]
    if len(set(identities)) != len(identities):
        raise ValueError('South cells contain duplicate cell identity')

    slots = _selected_slots(len(south_cells))
    stable_cells = tuple(sorted(south_cells, key=_stable_cell_order))
    # Compatibility depends only on the stratum, so duplicate normal-shape
    # slots (which dominate a 529-cell schedule) share one nested scan.
    compatible_cells = {}
    for slot in slots:
        stratum = slot.stratum
        if stratum not in compatible_cells:
            compatible_cells[stratum] = tuple(
                cell for cell in stable_cells if _compatible(slot, cell))
    neighbors = {slot: compatible_cells[slot.stratum] for slot in slots}
    ordered_slots = tuple(sorted(
        slots,
        key=lambda slot: (len(neighbors[slot]), stratum_key(slot.stratum),
                          slot.occurrence),
    ))
    cell_to_slot: dict[_SouthCell, _QuotaSlot] = {}
    slot_to_cell: dict[_QuotaSlot, _SouthCell] = {}

    def add_augmenting_layer() -> bool:
        queue = deque()
        distance: dict[_QuotaSlot, int] = {}
        for slot in ordered_slots:
            if slot not in slot_to_cell:
                distance[slot] = 0
                queue.append(slot)
        found = False
        while queue:
            slot = queue.popleft()
            for cell in neighbors[slot]:
                previous = cell_to_slot.get(cell)
                if previous is None:
                    found = True
                elif previous not in distance:
                    distance[previous] = distance[slot] + 1
                    queue.append(previous)

        def augment(slot: _QuotaSlot) -> bool:
            for cell in neighbors[slot]:
                previous = cell_to_slot.get(cell)
                if (previous is None
                        or (distance.get(previous) == distance[slot] + 1
                            and augment(previous))):
                    slot_to_cell[slot] = cell
                    cell_to_slot[cell] = slot
                    return True
            distance[slot] = -1
            return False

        if found:
            for slot in ordered_slots:
                if slot not in slot_to_cell:
                    augment(slot)
        return found

    while add_augmenting_layer():
        pass
    unmatched = [slot for slot in ordered_slots if slot not in slot_to_cell]
    if unmatched:
        raise OpenerAllocationError(
            len(south_cells), REQUIRED_CELLS, unmatched)

    assignments = {
        cell.identity: cell_to_slot[cell].stratum
        for cell in sorted(south_cells, key=lambda item: item.identity)
    }
    omitted = required_opener_strata()[len(south_cells):]
    ungenerated = tuple({
        'shape': list(stratum.shape),
        'mode': stratum.mode,
        'cell': None,
        'reason': 'insufficient_cells',
    } for stratum in omitted)
    return {
        'assignments': assignments,
        'required_cells': REQUIRED_CELLS,
        'available_cells': len(south_cells),
        'complete': len(south_cells) >= REQUIRED_CELLS,
        'ungenerated_strata': ungenerated,
    }


def build_north_summary(
        *,
        cells: Sequence[Mapping],
        assignments: Mapping[tuple[int, int], OpenerStratum],
        generated_pairs: Mapping[tuple[int, int], int],
        north_hcp_by_mode: Mapping[str, Sequence[int]],
        cell_failures: Sequence[Mapping],
        required_cells: int = REQUIRED_CELLS) -> dict[str, object]:
    """Build the exact ``coverage.north`` summary for an explicit report."""

    required = required_opener_strata()
    scheduled = Counter()
    requested = []
    failures = {}
    for failure in cell_failures:
        cell = validate_cell_identity(failure.get('cell'))
        failures[(cell['target_hcp'], cell['base_shape_index'])] = failure

    for cell in cells:
        identity = (cell['target_hcp'], cell['base_shape_index'])
        stratum = assignments.get(identity)
        if stratum is None:
            continue
        scheduled[stratum_key(stratum)] += 1
        generated = generated_pairs.get(identity, 0)
        failure = failures.get(identity)
        if failure is not None:
            status = 'partial' if generated > 0 else 'failed'
        else:
            status = 'generated'
        requested.append({
            'shape': list(stratum.shape),
            'mode': stratum.mode,
            'cell': {'target_hcp': identity[0],
                     'base_shape_index': identity[1]},
            'status': status,
        })

    observed = []
    seen = set()
    for item in requested:
        key = stratum_key(OpenerStratum(tuple(item['shape']), item['mode']))
        if key not in seen:
            seen.add(key)
            observed.append({'shape': item['shape'], 'mode': item['mode']})

    cell_counts = {stratum_key(stratum): scheduled[stratum_key(stratum)]
                   for stratum in required}
    pair_counts = {stratum_key(stratum): 0 for stratum in required}
    for cell in cells:
        identity = (cell['target_hcp'], cell['base_shape_index'])
        stratum = assignments.get(identity)
        if stratum is not None:
            pair_counts[stratum_key(stratum)] += generated_pairs.get(identity, 0)

    ungenerated = []
    for stratum in required:
        if scheduled[stratum_key(stratum)] == 0:
            ungenerated.append({
                'shape': list(stratum.shape), 'mode': stratum.mode,
                'cell': None, 'reason': 'insufficient_cells',
            })
    for failure in cell_failures:
        ungenerated.append({
            'shape': list(failure['shape']), 'mode': failure['mode'],
            'cell': failure['cell'], 'reason': failure['reason'],
        })

    complete = (len(cells) >= required_cells and not cell_failures
                and all(scheduled[stratum_key(stratum)] > 0
                        for stratum in required))
    return {
        'schema_status': 'explicit',
        'required_cells': required_cells,
        'available_cells': len(cells),
        'complete': complete,
        'requested_strata': requested,
        'observed_strata': observed,
        'cell_counts': cell_counts,
        'pair_counts': pair_counts,
        'hcp_by_mode': {mode: sorted(north_hcp_by_mode.get(mode, ()))
                        for mode in OPENER_MODES},
        'cell_failures': list(cell_failures),
        'ungenerated_strata': ungenerated,
    }


__all__ = (
    'OpenerAllocationError',
    'OpenerStratum',
    'allocate_opener_strata',
    'build_north_summary',
    'normal_named_shapes',
    'required_opener_strata',
    'rotate_responder_shape',
    'stratum_key',
    'validate_cell_identity',
    'validate_explicit_coverage_cell',
)
