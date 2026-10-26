from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .legality import SIDE_BY_SEAT
from .trump_state import TrumpState, promote, transition


@dataclass(frozen=True)
class StateRecord:
    key: str
    attributes: dict[str, Any]
    origin: dict[str, Any]
    namespace: str = "public"
    owner: str | None = None
    visibility: str = "partnership"

    @classmethod
    def from_dict(cls, data: dict[str, Any], origin: dict[str, Any]) -> "StateRecord":
        attributes = dict(data)
        key = str(attributes.pop("key"))
        namespace = str(attributes.pop("namespace", "public"))
        owner = attributes.pop("owner", None)
        visibility = str(attributes.pop("visibility", "partnership"))
        return cls(
            key=key,
            namespace=namespace,
            owner=owner,
            visibility=visibility,
            attributes=attributes,
            origin=origin,
        )

    def matches(self, query: dict[str, Any]) -> bool:
        for key, expected in query.items():
            actual = self.attribute(key)
            if actual != expected:
                return False
        return True

    def attribute(self, name: str) -> Any:
        if name == "key":
            return self.key
        if name == "namespace":
            return self.namespace
        if name == "owner":
            return self.owner
        if name == "visibility":
            return self.visibility
        return self.attributes.get(name)

    def to_dict(self) -> dict[str, Any]:
        result = {
            "key": self.key,
            "namespace": self.namespace,
            "visibility": self.visibility,
            **self.attributes,
            "origin": self.origin,
        }
        if self.owner is not None:
            result["owner"] = self.owner
        return result


@dataclass(frozen=True)
class FrameState:
    frame_id: str
    frame_type: str
    status: str
    variables: dict[str, Any]
    origin: dict[str, Any]
    current_stage: str | None = None
    obligation: dict[str, Any] = field(default_factory=dict)
    close_on_actions: tuple[str, ...] = ()
    close_on_act_types: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "frame_id": self.frame_id,
            "frame_type": self.frame_type,
            "status": self.status,
            "current_stage": self.current_stage,
            "variables": self.variables,
            "obligation": self.obligation,
            "origin": self.origin,
        }


@dataclass(frozen=True)
class PrivateRouteState:
    route_id: str
    goal: str
    owner: str
    current_node: str
    status: str
    origin: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "route_id": self.route_id,
            "goal": self.goal,
            "owner": self.owner,
            "current_node": self.current_node,
            "status": self.status,
            "origin": self.origin,
        }


@dataclass
class AuctionTrace:
    state_records: list[StateRecord] = field(default_factory=list)
    applied_meanings: list[dict[str, Any]] = field(default_factory=list)
    frame_states: list[FrameState] = field(default_factory=list)
    private_route_states: list[PrivateRouteState] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)
    axioms: dict[str, Any] = field(default_factory=dict)
    trump_states: dict[str, TrumpState] = field(default_factory=dict)
    perspective_side: str | None = None
    active_seat: str | None = None

    def trump_state(self, side: str) -> TrumpState:
        return self.trump_states.get(side, TrumpState())

    def promote_for_call(self, seat: str) -> None:
        side = SIDE_BY_SEAT[seat]
        self.trump_states[side] = promote(self.trump_state(side), seat)

    @property
    def current_state_records(self) -> tuple[StateRecord, ...]:
        records: list[StateRecord] = []
        last_event: dict[str, int] = {}
        for index, record in enumerate(self.state_records):
            if record.key in ('trump_state', 'agreed_suit') and record.owner in self.trump_states:
                last_event[record.owner] = index
        for index, record in enumerate(self.state_records):
            if record.key not in ('trump_state', 'agreed_suit'):
                records.append(record)
                continue
            side = record.owner
            if side not in self.trump_states:
                if self.perspective_side is None:
                    records.append(record)
                continue
            if index != last_event[side] or (self.perspective_side is not None and side != self.perspective_side):
                continue
            state = self.trump_state(side)
            if state.status == 'unset':
                continue
            if record.key == 'trump_state':
                records.append(StateRecord('trump_state',
                                           {'status': state.status, **(state.attributes or {}), 'suit': state.suit},
                                           state.origin or {}, owner=side))
            if state.status == 'agreed':
                records.append(StateRecord('agreed_suit', {**(state.attributes or {}), 'suit': state.suit},
                                           state.origin or {}, owner=side))
        return tuple(records)

    def add_state(self, record: StateRecord) -> None:
        if (record.key in ('trump_state', 'agreed_suit') and record.namespace == 'public'
                and record.visibility != 'private' and self.active_seat is not None):
            side = SIDE_BY_SEAT[self.active_seat]
            self.trump_states[side] = transition(self.trump_state(side),
                                                  {'key': record.key, **record.attributes},
                                                  self.active_seat, record.origin)
            record = StateRecord(record.key, record.attributes, record.origin,
                                 record.namespace, side, record.visibility)
        self.state_records.append(record)

    def state_exists(self, query: dict[str, Any]) -> bool:
        return any(record.matches(query) for record in self.current_state_records)

    def matching_state(self, query: dict[str, Any]) -> list[StateRecord]:
        return [record for record in self.current_state_records if record.matches(query)]

    def state_compare(self, query: dict[str, Any]) -> bool:
        lookup = dict(query.get("query", {}))
        attribute = query.get("attribute", "value")
        comparison = {key: value for key, value in query.items() if key not in ("query", "attribute")}
        matches = self.matching_state(lookup)
        return any(_compare_state_value(record.attribute(attribute), comparison) for record in matches)

    def state_has(self, query: dict[str, Any]) -> bool:
        if "key" in query:
            return self.state_exists(query)
        return all(self.state_exists(_state_query(key, attributes)) for key, attributes in query.items())

    def add_applied_meaning(self, entry: dict[str, Any]) -> None:
        self.applied_meanings.append(entry)

    def add_frame_state(self, frame: FrameState) -> None:
        self.frame_states.append(frame)

    def add_private_route_state(self, route_state: PrivateRouteState) -> None:
        self.private_route_states.append(route_state)

    def warn(self, text: str) -> None:
        self.diagnostics.append(text)


def _state_query(key: str, attributes: Any) -> dict[str, Any]:
    if attributes is None:
        attributes = {}
    if not isinstance(attributes, dict):
        raise ValueError(f"State query for {key} must be a mapping")
    return {"key": key, **attributes}


def _compare_state_value(actual: Any, comparison: dict[str, Any]) -> bool:
    if "eq" in comparison and actual != comparison["eq"]:
        return False
    if "neq" in comparison and actual == comparison["neq"]:
        return False
    if "in" in comparison and actual not in comparison["in"]:
        return False
    if actual is None and any(key in comparison for key in ("min", "max")):
        return False
    if "min" in comparison and comparison["min"] is not None and actual < comparison["min"]:
        return False
    if "max" in comparison and comparison["max"] is not None and actual > comparison["max"]:
        return False
    return True
