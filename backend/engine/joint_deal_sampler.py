"""Exact completion-count sampling for constrained North/South partnerships."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
import itertools
import math
import random
from bisect import bisect_left, bisect_right

from .cards import Hand, RANK_POINTS, SUITS
from .constrained_deals import RANKS, kr_shape_adjustment_units
from .hand_quality import _kr_suit


QJ_DOUBLETON = 1
HIGH_RANKS = 'AKQJT98'
LOW_RANKS = '765432'
RANK_ORDER = {rank: index for index, rank in enumerate('AKQJT98765432')}


@lru_cache(maxsize=None)
def _low_assignments(north_low: int, south_low: int):
    lows = tuple(LOW_RANKS)
    result = []
    for north in itertools.combinations(lows, north_low):
        remaining = tuple(rank for rank in lows if rank not in north)
        for south in itertools.combinations(remaining, south_low):
            result.append((north, south))
    return tuple(result)


@dataclass(frozen=True, order=True)
class HighSuitGroup:
    state: tuple[int, int, int, int, int]
    high: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]
    north_low: int
    south_low: int

    @property
    def count(self) -> int:
        return len(self.high) * len(_low_assignments(self.north_low, self.south_low))


@dataclass(frozen=True)
class HighSuitBuckets:
    groups: tuple[HighSuitGroup, ...]

    @property
    def total(self) -> int:
        return sum(group.count for group in self.groups)

    def sample(self, rng: random.Random):
        draw = rng.randrange(self.total)
        for group in self.groups:
            if draw < group.count:
                low_choices = _low_assignments(group.north_low, group.south_low)
                high_index = draw // len(low_choices)
                low_index = draw % len(low_choices)
                north_high, south_high = group.high[high_index]
                north_low, south_low = low_choices[low_index]
                return (
                    tuple(sorted(north_high + north_low, key=RANK_ORDER.get)),
                    tuple(sorted(south_high + south_low, key=RANK_ORDER.get)),
                )
            draw -= group.count
        raise AssertionError('weighted high/low suit draw fell outside its total')


def _high_state(north_high, south_high, north_length, south_length, bits):
    north_low = north_length - len(north_high)
    south_low = south_length - len(south_high)
    north_kr = _kr_suit(''.join(north_high) + 'x' * north_low)['twentieths']
    south_kr = _kr_suit(''.join(south_high) + 'x' * south_low)['twentieths']
    return (
        sum(RANK_POINTS.get(rank, 0) for rank in north_high),
        north_kr,
        sum(RANK_POINTS.get(rank, 0) for rank in south_high),
        south_kr,
        bits,
    )


@lru_cache(maxsize=None)
def _joint_high_buckets(ranks: str, north_length: int, south_length: int,
                        require_honor_singleton: bool):
    if ranks != 'AKQJT98765432':
        return None
    if north_length + south_length > 13:
        return None
    grouped = defaultdict(list)
    north_sizes = range(0, min(6, north_length) + 1)
    for north_high in itertools.chain.from_iterable(
            itertools.combinations(HIGH_RANKS, size) for size in north_sizes):
        if (require_honor_singleton and north_length == 1
                and (not north_high or north_high[0] not in 'AKQ')):
            continue
        remaining_high = tuple(rank for rank in HIGH_RANKS
                               if rank not in north_high)
        south_sizes = range(0, min(len(remaining_high), south_length) + 1)
        for south_high in itertools.chain.from_iterable(
                itertools.combinations(remaining_high, size)
                for size in south_sizes):
            north_low = north_length - len(north_high)
            south_low = south_length - len(south_high)
            if north_low + south_low > len(LOW_RANKS):
                continue
            bits = (QJ_DOUBLETON
                    if north_length == 2 and set(north_high) == {'Q', 'J'}
                    else 0)
            state = _high_state(north_high, south_high,
                                north_length, south_length, bits)
            grouped[(state, north_low, south_low)].append(
                (north_high, south_high))
    groups = tuple(
        HighSuitGroup(state, tuple(sorted(holdings)),
                      north_low, south_low)
        for (state, north_low, south_low), holdings in sorted(grouped.items())
    )
    return HighSuitBuckets(groups)


def _shape(value: Sequence[int], field: str) -> tuple[int, int, int, int]:
    if (not isinstance(value, (tuple, list)) or len(value) != 4
            or any(isinstance(item, bool) or not isinstance(item, int)
                   or item < 0 or item > 13 for item in value)
            or sum(value) != 13):
        raise ValueError(f'{field} must be four integer lengths totaling 13')
    return tuple(value)


def _kr_range(value: Sequence[float], field: str) -> tuple[float, float]:
    if (not isinstance(value, (tuple, list)) or len(value) != 2
            or any(isinstance(item, bool) or not isinstance(item, (int, float))
                   or not math.isfinite(item) for item in value)
            or value[0] > value[1]):
        raise ValueError(f'{field} must be an inclusive finite numeric range')
    return float(value[0]), float(value[1])


@dataclass(frozen=True)
class OpenerModeConstraints:
    """Named North shape, authored opening mode, and aggregate K-R envelope."""

    shape: tuple[int, int, int, int]
    mode: str
    kr: tuple[float, float]

    def __post_init__(self) -> None:
        object.__setattr__(self, 'shape', _shape(self.shape, 'north shape'))
        object.__setattr__(self, 'kr', _kr_range(self.kr, 'north K-R'))
        if self.mode not in ('normal', 'upgrade_14', 'soft_18'):
            raise ValueError(f'unknown opener mode: {self.mode!r}')
        family = tuple(sorted(self.shape, reverse=True))
        if self.mode == 'upgrade_14' and family != (5, 3, 3, 2):
            raise ValueError('upgrade_14 requires a 5-3-3-2 shape')
        if self.mode == 'soft_18' and family != (4, 4, 3, 2):
            raise ValueError('soft_18 requires a 4-4-3-2 shape')


@dataclass(frozen=True, order=True)
class SuitGroup:
    state: tuple[int, int, int, int, int]
    holdings: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...]

    @property
    def count(self) -> int:
        return len(self.holdings)


@dataclass(frozen=True)
class SuitBuckets:
    groups: tuple[SuitGroup, ...]

    @property
    def total(self) -> int:
        return sum(group.count for group in self.groups)

    def sample(self, rng: random.Random):
        draw = rng.randrange(self.total)
        for group in self.groups:
            if draw < group.count:
                return group.holdings[draw]
            draw -= group.count
        raise AssertionError('weighted suit draw fell outside its total')


@lru_cache(maxsize=None)
def _joint_suit_buckets(ranks: str, north_length: int, south_length: int,
                        require_honor_singleton: bool) -> SuitBuckets:
    if len(set(ranks)) != len(ranks):
        raise ValueError('ranks must be unique')
    if (north_length < 0 or south_length < 0
            or north_length + south_length > len(ranks)):
        raise ValueError('requested suit lengths exceed the available ranks')
    grouped = defaultdict(list)
    for north in itertools.combinations(ranks, north_length):
        if (require_honor_singleton and north_length == 1
                and north[0] not in 'AKQ'):
            continue
        remaining = tuple(rank for rank in ranks if rank not in north)
        north_hcp = sum(RANK_POINTS.get(rank, 0) for rank in north)
        north_kr = _kr_suit(''.join(north))['twentieths']
        bits = QJ_DOUBLETON if north_length == 2 and set(north) == {'Q', 'J'} else 0
        for south in itertools.combinations(remaining, south_length):
            state = (
                north_hcp,
                north_kr,
                sum(RANK_POINTS.get(rank, 0) for rank in south),
                _kr_suit(''.join(south))['twentieths'],
                bits,
            )
            grouped[state].append((north, south))
    groups = tuple(
        SuitGroup(state, tuple(sorted(holdings)))
        for state, holdings in sorted(grouped.items())
    )
    return SuitBuckets(groups)


def joint_suit_buckets(ranks: str, north_length: int, south_length: int,
                       *, require_honor_singleton: bool = False) -> SuitBuckets:
    """Return immutable grouped concrete holdings for one suit."""

    return _joint_suit_buckets(
        ranks, north_length, south_length, require_honor_singleton)


@lru_cache(maxsize=2)
def _hcp_pruned_convolution(first: SuitBuckets, second: SuitBuckets,
                            north_hcp_max: int, south_hcp_max: int):
    """Convolve two suit buckets, pruning only the HCP dimensions.

    The K-R sums are left unpruned so the same result can be reused across
    every K-R envelope a single cell samples (slot 0 probes a wide envelope,
    later slots a tight one).  The HCP bounds are fixed by the opener mode
    and the responder quota, so they are safe to bake into the cache key.
    """
    first_groups = tuple(
        (group.state, group.count) for group in first.groups
        if group.state[0] <= north_hcp_max and group.state[2] <= south_hcp_max
    )
    second_groups = tuple(
        (group.state, group.count) for group in second.groups
        if group.state[0] <= north_hcp_max and group.state[2] <= south_hcp_max
    )
    counts = defaultdict(int)
    for left, left_count in first_groups:
        left_hcp = left[0]
        left_kr = left[1]
        left_s_hcp = left[2]
        left_s_kr = left[3]
        left_bits = left[4]
        for right, right_count in second_groups:
            north_hcp = left_hcp + right[0]
            if north_hcp > north_hcp_max:
                continue
            south_hcp = left_s_hcp + right[2]
            if south_hcp > south_hcp_max:
                continue
            state = (north_hcp, left_kr + right[1], south_hcp,
                     left_s_kr + right[3], left_bits | right[4])
            counts[state] += left_count * right_count
    return dict(counts)


def _half_combination(first: SuitBuckets, second: SuitBuckets,
                      upper: tuple[int, int, int, int]):
    """Convolve two suit bucket sets and apply the full envelope."""
    north_hcp_max, north_kr_max, south_hcp_max, south_kr_max = upper
    counts = _hcp_pruned_convolution(
        first, second, north_hcp_max, south_hcp_max)
    return {
        state: count for state, count in counts.items()
        if state[1] <= north_kr_max and state[3] <= south_kr_max
    }


@lru_cache(maxsize=None)
def _bucket_state_index(bucket):
    """Map each suit state to its (group index, count) contributors."""
    grouped = defaultdict(list)
    for index, group in enumerate(bucket.groups):
        grouped[group.state].append((index, group.count))
    return {state: tuple(items) for state, items in grouped.items()}


class JointConstraintError(ValueError):
    """A joint constraint has no completion or violates its authored invariant."""


class JointPartnershipPlan:
    """Exact four-suit completion counts and a weighted backward sampler."""

    def __init__(self, north: OpenerModeConstraints,
                 south_shape: Sequence[int], south_hcp: int,
                 south_kr: Sequence[float], *, ranks: str = RANKS):
        if not isinstance(north, OpenerModeConstraints):
            raise TypeError('north must be OpenerModeConstraints')
        self.north = north
        self.south_shape = _shape(south_shape, 'south shape')
        if (isinstance(south_hcp, bool) or not isinstance(south_hcp, int)
                or not 0 <= south_hcp <= 37):
            raise ValueError('south HCP must be an integer from 0 through 37')
        self.south_hcp = south_hcp
        self.south_kr = _kr_range(south_kr, 'south K-R')
        self.ranks = ranks
        if any(north_len + south_len > len(ranks)
               for north_len, south_len in zip(north.shape, self.south_shape)):
            self.buckets = ()
            self.layers = ({(0, 0, 0, 0, 0): 1},)
            self.targets = ()
            self.total = 0
            return

        honor_singleton = 1 in north.shape
        self._high_mode = ranks == RANKS
        bucket_factory = (_joint_high_buckets if self._high_mode
                          else joint_suit_buckets)
        named_buckets = tuple(
            (index, bucket_factory(
                ranks, north_len, south_len,
                require_honor_singleton=honor_singleton))
            for index, (north_len, south_len) in enumerate(
                zip(north.shape, self.south_shape))
        )
        if any(bucket is None for _, bucket in named_buckets):
            self._high_mode = False
            named_buckets = tuple(
                (index, joint_suit_buckets(
                    ranks, north_len, south_len,
                    require_honor_singleton=honor_singleton))
                for index, (north_len, south_len) in enumerate(
                    zip(north.shape, self.south_shape))
            )
        self._bucket_order = tuple(index for index, _ in sorted(
            named_buckets, key=lambda item: (len(item[1].groups), item[0])))
        by_index = dict(named_buckets)
        self.buckets = tuple(by_index[index] for index in self._bucket_order)
        north_hcp_min, north_hcp_max = {
            'normal': (15, 17), 'upgrade_14': (14, 14),
            'soft_18': (18, 18),
        }[north.mode]
        north_adjustment = kr_shape_adjustment_units(north.shape)
        south_adjustment = kr_shape_adjustment_units(self.south_shape)
        self._north_kr_min = math.ceil(north.kr[0] * 20 - 1e-8) - north_adjustment
        self._north_kr_max = math.floor(north.kr[1] * 20 + 1e-8) - north_adjustment
        self._south_kr_min = math.ceil(self.south_kr[0] * 20 - 1e-8) - south_adjustment
        self._south_kr_max = math.floor(self.south_kr[1] * 20 + 1e-8) - south_adjustment

        lower = (north_hcp_min, self._north_kr_min,
                 south_hcp, self._south_kr_min)
        upper = (north_hcp_max, self._north_kr_max,
                 south_hcp, self._south_kr_max)

        left_counts = _half_combination(self.buckets[0], self.buckets[1], upper)
        right_counts = _half_combination(self.buckets[2], self.buckets[3], upper)
        self._half_counts = (left_counts, right_counts)
        right_lines = defaultdict(lambda: defaultdict(list))
        for state, count in sorted(right_counts.items()):
            right_lines[(state[0], state[2], state[4])][state[1]].append(
                (state[3], count))
        self._right_lines = {}
        self._right_keys = {}
        for key, by_north_kr in right_lines.items():
            lines = {}
            for north_kr, values in by_north_kr.items():
                south_values = []
                cumulative = []
                running = 0
                for south_kr, count in sorted(values):
                    south_values.append(south_kr)
                    running += count
                    cumulative.append(running)
                lines[north_kr] = (tuple(south_values), tuple(cumulative))
            self._right_lines[key] = lines
            self._right_keys[key] = tuple(sorted(lines))

        def line_count(line, minimum, maximum):
            values, cumulative = line
            start = bisect_left(values, minimum)
            stop = bisect_right(values, maximum)
            if start == stop:
                return 0
            return cumulative[stop - 1] - (cumulative[start - 1] if start else 0)

        target_counts = {}
        target_options = {}
        for left_state in sorted(left_counts):
            options = []
            for target_hcp in range(north_hcp_min, north_hcp_max + 1):
                bounds = self._right_bounds(left_state, target_hcp)
                if bounds is None:
                    continue
                north_min, north_max, south_min, south_max, allowed_bits = bounds
                for bits in allowed_bits:
                    key = (target_hcp - left_state[0],
                           south_hcp - left_state[2], bits)
                    lines = self._right_lines.get(key)
                    if not lines:
                        continue
                    north_kr_keys = self._right_keys[key]
                    lo = bisect_left(north_kr_keys, north_min)
                    hi = bisect_right(north_kr_keys, north_max)
                    count = 0
                    for position in range(lo, hi):
                        count += line_count(
                            lines[north_kr_keys[position]], south_min, south_max)
                    if count:
                        options.append((target_hcp, bits, bounds, count))
            if options:
                completion_count = sum(item[3] for item in options)
                target_counts[left_state] = left_counts[left_state] * completion_count
                target_options[left_state] = tuple(options)
        self._target_options = target_options
        # These are the four counted transitions: two one-suit layers, two
        # exact two-suit halves, and their legal full-hand targets.
        self.layers = (
            {(0, 0, 0, 0, 0): 1},
            {group.state: group.count for group in self.buckets[0].groups},
            left_counts,
            right_counts,
            dict(target_counts),
        )
        self.targets = tuple(sorted(target_counts.items()))
        self.total = sum(count for _, count in self.targets)

    def _right_bounds(self, left_state, target_hcp):
        north_min = self._north_kr_min - left_state[1]
        north_max = self._north_kr_max - left_state[1]
        south_min = self._south_kr_min - left_state[3]
        south_max = self._south_kr_max - left_state[3]
        adjustment = kr_shape_adjustment_units(self.north.shape)
        mode = self.north.mode
        if mode == 'upgrade_14':
            north_min = max(north_min, 320 - left_state[1])
        if mode == 'soft_18':
            north_max = min(north_max, 340 - left_state[1])
        spades, hearts, diamonds, clubs = self.north.shape
        five_major = max(spades, hearts) == 5
        four_minor = max(diamonds, clubs) == 4
        if five_major and target_hcp == 17:
            north_max = min(north_max, 339 - adjustment - left_state[1])
        family = tuple(sorted(self.north.shape, reverse=True))
        if five_major and four_minor and family == (5, 4, 2, 2):
            north_max = min(
                north_max, target_hcp * 20 - 30 - adjustment - left_state[1])
        if five_major and four_minor and family == (5, 4, 3, 1):
            north_max = min(
                north_max, target_hcp * 20 - 10 - adjustment - left_state[1])
        if north_min > north_max or south_min > south_max:
            return None
        if mode == 'soft_18' and not left_state[4] & QJ_DOUBLETON:
            bits = (QJ_DOUBLETON,)
        else:
            bits = (0, QJ_DOUBLETON)
        return north_min, north_max, south_min, south_max, bits

    def _target_is_legal(self, state: tuple[int, int, int, int, int]) -> bool:
        north_hcp, north_kr, south_hcp, south_kr, bits = state
        if south_hcp != self.south_hcp:
            return False
        if not self._south_kr_min <= south_kr <= self._south_kr_max:
            return False
        if not self._north_kr_min <= north_kr <= self._north_kr_max:
            return False
        mode = self.north.mode
        if mode == 'normal' and not 15 <= north_hcp <= 17:
            return False
        if mode == 'upgrade_14' and (north_hcp != 14 or north_kr < 320):
            return False
        if mode == 'soft_18' and (north_hcp != 18 or north_kr > 340
                                  or not bits & QJ_DOUBLETON):
            return False

        spades, hearts, diamonds, clubs = self.north.shape
        five_major = max(spades, hearts) == 5
        four_minor = max(diamonds, clubs) == 4
        adjusted_kr = north_kr + kr_shape_adjustment_units(self.north.shape)
        if five_major and north_hcp == 17 and adjusted_kr >= 340:
            return False
        family = tuple(sorted(self.north.shape, reverse=True))
        delta_units = adjusted_kr - north_hcp * 20
        if five_major and four_minor and family == (5, 4, 2, 2) \
                and delta_units > -30:
            return False
        if five_major and four_minor and family == (5, 4, 3, 1) \
                and delta_units > -10:
            return False
        return True

    def _half_choices(self, half_index, state):
        """Rebuild the (first, second) group pairs that sum to a half state.

        Branch lists run into the millions of entries per cell, so they are
        reconstructed on demand from the per-suit state index instead of
        being stored.
        """
        first = self.buckets[half_index * 2]
        second_lookup = _bucket_state_index(self.buckets[half_index * 2 + 1])
        s0, s1, s2, s3, s4 = state
        choices = []
        for first_index, group in enumerate(first.groups):
            left = group.state
            b0 = s0 - left[0]
            b1 = s1 - left[1]
            b2 = s2 - left[2]
            b3 = s3 - left[3]
            for b4 in (0, QJ_DOUBLETON):
                if (left[4] | b4) != s4:
                    continue
                for second_group_index, second_count in second_lookup.get(
                        (b0, b1, b2, b3, b4), ()):
                    choices.append(
                        (first_index, second_group_index,
                         group.count * second_count))
        return choices

    def sample(self, rng: random.Random) -> tuple[Hand, Hand]:
        if not self.total:
            raise JointConstraintError(self.diagnostics('completion_count=0'))
        draw = rng.randrange(self.total)
        for target, count in self.targets:
            if draw < count:
                break
            draw -= count
        options = self._target_options[target]
        draw = rng.randrange(sum(item[3] for item in options))
        for target_hcp, bits, bounds, weight in options:
            if draw < weight:
                break
            draw -= weight
        north_min, north_max, south_min, south_max, _ = bounds
        key = (target_hcp - target[0], self.south_hcp - target[2], bits)
        lines = self._right_lines[key]
        right_options = []
        right_total = 0
        for north_kr in range(north_min, north_max + 1):
            line = lines.get(north_kr)
            if line is None:
                continue
            south_values, cumulative = line
            start = bisect_left(south_values, south_min)
            stop = bisect_right(south_values, south_max)
            for position in range(start, stop):
                count = cumulative[position] - (
                    cumulative[position - 1] if position else 0)
                right_state = (key[0], north_kr, key[1],
                               south_values[position], bits)
                right_options.append((right_state, count))
                right_total += count
        draw = rng.randrange(right_total)
        for right_state, weight in right_options:
            if draw < weight:
                break
            draw -= weight
        half_states = (target, right_state)
        north_holdings = [''] * 4
        south_holdings = [''] * 4
        for half_index, state in enumerate(half_states):
            choices = self._half_choices(half_index, state)
            draw = rng.randrange(self._half_counts[half_index][state])
            for first_group_index, second_group_index, weight in choices:
                if draw < weight:
                    group_indexes = (first_group_index, second_group_index)
                    break
                draw -= weight
            for offset, group_index in enumerate(group_indexes):
                bucket_index = half_index * 2 + offset
                bucket = self.buckets[bucket_index]
                group = bucket.groups[group_index]
                named_index = self._bucket_order[bucket_index]
                if self._high_mode:
                    low_choices = _low_assignments(
                        group.north_low, group.south_low)
                    high_index = (rng.randrange(group.count)
                                  // len(low_choices))
                    north_high, south_high = group.high[high_index]
                    north_holdings[named_index] = ''.join(
                        sorted(north_high, key=RANK_ORDER.get))
                    south_holdings[named_index] = ''.join(
                        sorted(south_high, key=RANK_ORDER.get))
                else:
                    holding = group.holdings[rng.randrange(group.count)]
                    north_holdings[named_index] = ''.join(holding[0])
                    south_holdings[named_index] = ''.join(holding[1])
        # Fill low cards (2-7) only after every high-card structure is fixed.
        if self._high_mode:
            for suit in SUITS:
                index = SUITS.index(suit)
                north_len = self.north.shape[index]
                south_len = self.south_shape[index]
                north_low = north_len - len(north_holdings[index])
                south_low = south_len - len(south_holdings[index])
                low_choices = _low_assignments(north_low, south_low)
                north_low_ranks, south_low_ranks = low_choices[
                    rng.randrange(len(low_choices))]
                north_holdings[index] += ''.join(north_low_ranks)
                south_holdings[index] += ''.join(south_low_ranks)
        north = Hand.from_dict(dict(zip(SUITS, north_holdings)), validate_count=True)
        south = Hand.from_dict(dict(zip(SUITS, south_holdings)), validate_count=True)
        return north, south

    def diagnostics(self, suffix: str) -> str:
        return (
            f'north_shape={self.north.shape}, mode={self.north.mode}, '
            f'south_shape={self.south_shape}, south_hcp={self.south_hcp}, '
            f'north_kr={self.north.kr}, south_kr={self.south_kr}, {suffix}'
        )


def sample_conditioned_partnership(
        plan: JointPartnershipPlan, *, seed: int | None = None,
        rng: random.Random | None = None,
        opening_assessment: Callable[[Hand], object],
        complete_opponents: Callable[[random.Random, Hand, Hand], object] | None = None):
    """Sample exact N/S hands, enforce the authored invariant, then complete E/W."""

    if not isinstance(plan, JointPartnershipPlan):
        raise TypeError('plan must be a JointPartnershipPlan')
    if rng is not None and seed is not None:
        raise ValueError('provide rng or seed, not both')
    active_rng = rng if rng is not None else random.Random(seed)
    north, south = plan.sample(active_rng)
    result = opening_assessment(north)
    accepted = result.get('eligible') if isinstance(result, Mapping) else bool(result)
    if not accepted:
        raise JointConstraintError(plan.diagnostics(
            f'completion_count={plan.total}, predicate=opening_assessment, '
            f'predicate_result={result!r}'))
    if complete_opponents is not None:
        return complete_opponents(active_rng, north, south)
    return {'n': north, 's': south}


__all__ = (
    'JointConstraintError',
    'JointPartnershipPlan',
    'OpenerModeConstraints',
    'joint_suit_buckets',
    'sample_conditioned_partnership',
)
