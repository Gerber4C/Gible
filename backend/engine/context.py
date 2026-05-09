from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Iterator

from .auction import Auction
from .call_space import CallRelation, relation_to_last_contract
from .calls import normalize_call
from .cards import Hand
from .memory import SeatMemory


class UndefinedValue:
    def __bool__(self) -> bool:
        return False

    def __repr__(self) -> str:
        return "Undefined"

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, UndefinedValue)

    def __lt__(self, other: Any) -> bool:
        return False

    def __le__(self, other: Any) -> bool:
        return False

    def __gt__(self, other: Any) -> bool:
        return False

    def __ge__(self, other: Any) -> bool:
        return False

    def or_default(self, default: Any) -> Any:
        return default


UNDEFINED = UndefinedValue()


@dataclass(frozen=True)
class RangeEstimate:
    key: str
    min_value: Any = field(default_factory=lambda: UNDEFINED)
    max_value: Any = field(default_factory=lambda: UNDEFINED)
    value: Any = field(default_factory=lambda: UNDEFINED)
    evidence: tuple[Any, ...] = ()
    conflicts: tuple[str, ...] = ()

    @property
    def known(self) -> bool:
        return self.value is not UNDEFINED or self.min_value is not UNDEFINED or self.max_value is not UNDEFINED

    @property
    def exact(self) -> bool:
        return self.value is not UNDEFINED

    def contains(self, value: Any) -> bool:
        if self.value is not UNDEFINED:
            return value == self.value
        if self.min_value is not UNDEFINED and value < self.min_value:
            return False
        if self.max_value is not UNDEFINED and value > self.max_value:
            return False
        return True

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "key": self.key,
            "known": self.known,
            "evidence_count": len(self.evidence),
        }
        if self.value is not UNDEFINED:
            result["value"] = self.value
        if self.min_value is not UNDEFINED:
            result["min_value"] = self.min_value
        if self.max_value is not UNDEFINED:
            result["max_value"] = self.max_value
        if self.conflicts:
            result["conflicts"] = list(self.conflicts)
        return result


@dataclass(frozen=True)
class StateView:
    records: tuple[Any, ...] = ()
    frame_states: tuple[Any, ...] = ()
    private_route_states: tuple[Any, ...] = ()

    @classmethod
    def from_trace(cls, trace: Any) -> "StateView":
        return cls(
            records=tuple(getattr(trace, "state_records", ())),
            frame_states=tuple(getattr(trace, "frame_states", ())),
            private_route_states=tuple(getattr(trace, "private_route_states", ())),
        )

    def estimate(self, key: str) -> RangeEstimate:
        evidence = tuple(record for record in self.records if getattr(record, "key", None) == key)
        if not evidence:
            return RangeEstimate(key=key)

        min_values = []
        max_values = []
        exact_values = []
        conflicts = []
        for record in evidence:
            attributes = getattr(record, "attributes", {})
            if attributes.get("value", UNDEFINED) is not UNDEFINED:
                exact_values.append(attributes["value"])
            if attributes.get("min_value", UNDEFINED) is not UNDEFINED:
                min_values.append(attributes["min_value"])
            if attributes.get("max_value", UNDEFINED) is not UNDEFINED:
                max_values.append(attributes["max_value"])

        value = exact_values[-1] if exact_values else UNDEFINED
        if len({repr(item) for item in exact_values}) > 1:
            conflicts.append("multiple exact values")

        min_value = max(min_values) if min_values else UNDEFINED
        max_value = min(max_values) if max_values else UNDEFINED
        if min_value is not UNDEFINED and max_value is not UNDEFINED and min_value > max_value:
            conflicts.append("empty range")
        if value is not UNDEFINED:
            if min_value is not UNDEFINED and value < min_value:
                conflicts.append("exact value below lower bound")
            if max_value is not UNDEFINED and value > max_value:
                conflicts.append("exact value above upper bound")

        return RangeEstimate(
            key=key,
            min_value=min_value,
            max_value=max_value,
            value=value,
            evidence=evidence,
            conflicts=tuple(conflicts),
        )

    def value(self, key: str, default: Any = UNDEFINED) -> Any:
        estimate = self.estimate(key)
        if estimate.value is UNDEFINED:
            return default
        return estimate.value

    def estimates_with_prefix(self, prefix: str) -> dict[str, RangeEstimate]:
        keys = sorted({record.key for record in self.records if getattr(record, "key", "").startswith(prefix)})
        return {key: self.estimate(key) for key in keys}

    def records_matching(self, key: str | None = None, **attributes: Any) -> tuple[Any, ...]:
        matches = []
        for record in self.records:
            if key is not None and getattr(record, "key", None) != key:
                continue
            if all(record.attribute(name) == value for name, value in attributes.items()):
                matches.append(record)
        return tuple(matches)

    def exists(self, key: str | None = None, **attributes: Any) -> bool:
        return bool(self.records_matching(key, **attributes))

    def active_frames(self, frame_type: str | None = None) -> tuple[Any, ...]:
        return tuple(
            frame
            for frame in self.frame_states
            if getattr(frame, "status", None) == "active"
            and (frame_type is None or getattr(frame, "frame_type", None) == frame_type)
        )

    def dominant_frame(self) -> Any | None:
        active = self.active_frames()
        return active[-1] if active else None

    def dominant_frame_obligation(self) -> dict[str, Any]:
        frame = self.dominant_frame()
        if frame is None:
            return {}
        return dict(getattr(frame, "obligation", {}) or {})

    def active_private_routes(self, goal: str | None = None) -> tuple[Any, ...]:
        return tuple(
            route
            for route in self.private_route_states
            if getattr(route, "status", None) == "active"
            and (goal is None or getattr(route, "goal", None) == goal)
        )

    def to_dict(self) -> dict[str, Any]:
        estimates = {key: self.estimate(key).to_dict() for key in sorted({record.key for record in self.records})}
        dominant_frame = self.dominant_frame()
        return {
            "estimates": estimates,
            "records": [record.to_dict() for record in self.records],
            "active_frames": [frame.to_dict() for frame in self.active_frames()],
            "dominant_frame": dominant_frame.to_dict() if dominant_frame is not None else None,
            "active_private_routes": [route.to_dict() for route in self.active_private_routes()],
        }


@dataclass(frozen=True)
class SuitKnowledge:
    state: StateView
    owner: str
    suit: str

    @property
    def length(self) -> RangeEstimate:
        return self.state.estimate(f"{self.owner}.length.{self.suit}")


@dataclass(frozen=True)
class HandKnowledge:
    state: StateView
    owner: str

    def suit(self, suit: str) -> SuitKnowledge:
        return SuitKnowledge(self.state, self.owner, str(suit).upper())

    @property
    def S(self) -> SuitKnowledge:
        return self.suit("S")

    @property
    def H(self) -> SuitKnowledge:
        return self.suit("H")

    @property
    def D(self) -> SuitKnowledge:
        return self.suit("D")

    @property
    def C(self) -> SuitKnowledge:
        return self.suit("C")

    @property
    def hcp(self) -> RangeEstimate:
        return self.state.estimate(f"{self.owner}.hcp")


@dataclass(frozen=True)
class FitKnowledge:
    state: StateView
    suit: str

    @property
    def records(self) -> tuple[Any, ...]:
        return self.state.records_matching(f"partnership.fit.{self.suit}")

    @property
    def latest(self) -> Any | None:
        return self.records[-1] if self.records else None

    @property
    def min_total(self) -> RangeEstimate:
        evidence = tuple(record for record in self.records if record.attribute("min_total") is not None)
        if not evidence:
            return RangeEstimate(key=f"partnership.fit.{self.suit}.min_total")

        values = [record.attribute("min_total") for record in evidence]
        exact_values = {repr(value) for value in values}
        return RangeEstimate(
            key=f"partnership.fit.{self.suit}.min_total",
            min_value=max(values),
            value=values[-1] if len(exact_values) == 1 else UNDEFINED,
            evidence=evidence,
            conflicts=() if len(exact_values) <= 1 else ("multiple fit totals",),
        )

    @property
    def pattern_floor(self) -> Any:
        latest = self.latest
        return latest.attribute("pattern_floor") if latest is not None else UNDEFINED


@dataclass(frozen=True)
class PartnershipKnowledge:
    state: StateView

    @property
    def opener(self) -> HandKnowledge:
        return HandKnowledge(self.state, "opener")

    @property
    def responder(self) -> HandKnowledge:
        return HandKnowledge(self.state, "responder")

    @property
    def partner(self) -> HandKnowledge:
        return HandKnowledge(self.state, "partner")

    @property
    def actor(self) -> HandKnowledge:
        return HandKnowledge(self.state, "actor")

    def fit(self, suit: str) -> FitKnowledge:
        return FitKnowledge(self.state, str(suit).upper())


@dataclass(frozen=True)
class BridgeContext:
    phase: str
    auction: Auction
    actor: str | None
    hand: Hand | None
    environment: dict[str, Any]
    state: StateView
    legal_calls: tuple[str, ...] = ()
    candidates: "CandidatePool | None" = None
    memory: SeatMemory = field(default_factory=SeatMemory)
    trace: Any = None

    @classmethod
    def from_trace(
        cls,
        *,
        phase: str,
        auction: Auction,
        hand: Hand | None,
        environment: dict[str, Any] | None,
        trace: Any,
        legal_calls: Iterable[str] = (),
        candidates: "CandidatePool | None" = None,
        memory: SeatMemory | dict[str, Any] | None = None,
    ) -> "BridgeContext":
        return cls(
            phase=phase,
            auction=auction,
            actor=auction.actor_to_call,
            hand=hand,
            environment=dict(environment or {}),
            state=StateView.from_trace(trace),
            legal_calls=tuple(legal_calls),
            candidates=candidates,
            memory=SeatMemory.coerce(memory),
            trace=trace,
        )

    @property
    def private_routes(self) -> tuple[Any, ...]:
        return self.state.private_route_states

    @property
    def frames(self) -> tuple[Any, ...]:
        return self.state.frame_states

    @property
    def dominant_frame(self) -> Any | None:
        return self.state.dominant_frame()

    @property
    def frame_obligation(self) -> dict[str, Any]:
        return self.state.dominant_frame_obligation()

    @property
    def obligation_candidates(self) -> tuple[Any, ...]:
        if self.candidates is None:
            return ()
        return self.candidates.by_obligation(self.frame_obligation)

    @property
    def knowledge(self) -> PartnershipKnowledge:
        return PartnershipKnowledge(self.state)


@dataclass(frozen=True)
class CandidateFeatures:
    call: str
    level: int | None
    denomination: str | None
    is_pass: bool
    is_contract: bool
    action_type: str | None
    act_types: tuple[str, ...]
    capabilities: tuple[str, ...]
    has_private_route: bool
    score: int
    relation: CallRelation | None = None


@dataclass(frozen=True)
class Decision:
    candidate: Any | None
    reason: str | None = None
    procedure: dict[str, Any] | None = None


@dataclass(frozen=True)
class CallCandidate:
    call: str
    origin: dict[str, Any]
    public_meaning: dict[str, Any]
    source_kind: str
    source_id: str
    score: int
    criterion_results: tuple[dict[str, Any], ...]
    private_route_origin: dict[str, Any] | None = None
    implementation_origin: dict[str, Any] | None = None
    capabilities: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BidDecision:
    call: str | None
    selected_candidate: CallCandidate | None
    candidate_pool: "CandidatePool"
    trace: Any
    policy_origin: dict[str, Any] | None = None
    context: BridgeContext | None = None
    private_memory: SeatMemory = field(default_factory=SeatMemory)


class CandidatePool:
    def __init__(self, candidates: Iterable[Any], auction: Auction | None = None) -> None:
        self.candidates = tuple(candidates)
        self._auction = auction

    def __iter__(self) -> Iterator[Any]:
        return iter(self.candidates)

    def __len__(self) -> int:
        return len(self.candidates)

    @property
    def calls(self) -> tuple[str, ...]:
        return tuple(candidate.call for candidate in self.candidates)

    def has(self, call: str) -> bool:
        normalized = normalize_call(call)
        return any(candidate.call == normalized for candidate in self.candidates)

    def for_call(self, call: str) -> tuple[Any, ...]:
        normalized = normalize_call(call)
        return tuple(candidate for candidate in self.candidates if candidate.call == normalized)

    def get(self, call: str) -> Any | None:
        return self.pick(call)

    def pick(self, call: str) -> Any | None:
        matching = self.for_call(call)
        if not matching:
            return None
        return self.best(matching)

    def first_available(self, *calls: str) -> Any | None:
        for call in calls:
            candidate = self.pick(call)
            if candidate is not None:
                return candidate
        return None

    def by_action_type(self, action_type: str) -> tuple[Any, ...]:
        return tuple(
            candidate
            for candidate in self.candidates
            if (candidate.public_meaning or {}).get("action_type") == action_type
        )

    def by_target_suit(self, suit: str) -> tuple[Any, ...]:
        normalized = str(suit).upper()
        return tuple(
            candidate
            for candidate in self.candidates
            if (candidate.public_meaning or {}).get("target_suit") == normalized
        )

    def by_capability(self, *capabilities: str) -> tuple[Any, ...]:
        required = set(capabilities)
        return tuple(
            candidate
            for candidate in self.candidates
            if required.issubset(set(getattr(candidate, "capabilities", ()) or ()))
        )

    def by_obligation(self, obligation: dict[str, Any] | None) -> tuple[Any, ...]:
        if not obligation:
            return ()
        capabilities = obligation.get("capabilities", ())
        if isinstance(capabilities, str):
            capabilities = (capabilities,)
        if not capabilities:
            return ()
        return self.by_capability(*tuple(capabilities or ()))

    def best(self, candidates: Iterable[Any] | None = None) -> Any:
        values = tuple(self.candidates if candidates is None else candidates)
        if not values:
            raise ValueError("CandidatePool.best() requires at least one candidate")
        return sorted(values, key=self._sort_key, reverse=True)[0]

    def features(self, candidate: Any) -> CandidateFeatures:
        level, denomination = _call_level_and_denomination(candidate.call)
        meaning = candidate.public_meaning or {}
        return CandidateFeatures(
            call=candidate.call,
            level=level,
            denomination=denomination,
            is_pass=candidate.call == "P",
            is_contract=level is not None,
            action_type=meaning.get("action_type"),
            act_types=tuple(meaning.get("call_act_types", ()) or ()),
            capabilities=tuple(getattr(candidate, "capabilities", ()) or ()),
            has_private_route=candidate.private_route_origin is not None,
            score=int(candidate.score),
            relation=relation_to_last_contract(self._auction, candidate.call) if self._auction is not None else None,
        )

    def _sort_key(self, candidate: Any) -> tuple[int, int, int]:
        features = self.features(candidate)
        return (
            features.score,
            1 if features.has_private_route else 0,
            0 if features.is_pass else 1,
        )


class DecisionProcedure:
    def choose(self, ctx: BridgeContext, pool: CandidatePool) -> Decision:
        return Decision(candidate=pool.best(), reason="highest ranked candidate")


def _call_level_and_denomination(call: str) -> tuple[int | None, str | None]:
    if not call or call[0] not in "1234567":
        return None, None
    return int(call[0]), call[1:]
