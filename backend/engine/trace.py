from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SemanticFact:
    fact_type: str
    attributes: dict[str, Any]
    origin: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any], origin: dict[str, Any]) -> "SemanticFact":
        attributes = dict(data)
        fact_type = str(attributes.pop("fact_type"))
        return cls(fact_type=fact_type, attributes=attributes, origin=origin)

    def matches(self, query: dict[str, Any]) -> bool:
        for key, expected in query.items():
            if key == "fact_type":
                actual = self.fact_type
            else:
                actual = self.attributes.get(key)
            if actual != expected:
                return False
        return True

    def to_dict(self) -> dict[str, Any]:
        return {
            "fact_type": self.fact_type,
            **self.attributes,
            "origin": self.origin,
        }


@dataclass(frozen=True)
class AuctionStateVariable:
    key: str
    namespace: str
    owner: str | None
    attributes: dict[str, Any]
    origin: dict[str, Any]

    @classmethod
    def from_dict(cls, data: dict[str, Any], origin: dict[str, Any]) -> "AuctionStateVariable":
        attributes = dict(data)
        key = str(attributes.pop("key"))
        namespace = str(attributes.pop("namespace", "public"))
        owner = attributes.pop("owner", None)
        return cls(key=key, namespace=namespace, owner=owner, attributes=attributes, origin=origin)

    def matches(self, query: dict[str, Any]) -> bool:
        for key, expected in query.items():
            if key == "key":
                actual = self.key
            elif key == "namespace":
                actual = self.namespace
            elif key == "owner":
                actual = self.owner
            else:
                actual = self.attributes.get(key)
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
        return self.attributes.get(name)

    def to_dict(self) -> dict[str, Any]:
        result = {
            "key": self.key,
            "namespace": self.namespace,
            **self.attributes,
            "origin": self.origin,
        }
        if self.owner is not None:
            result["owner"] = self.owner
        return result


@dataclass(frozen=True)
class ProtocolFrameState:
    frame_id: str
    frame_type: str
    status: str
    variables: dict[str, Any]
    origin: dict[str, Any]
    current_stage: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "frame_id": self.frame_id,
            "frame_type": self.frame_type,
            "status": self.status,
            "current_stage": self.current_stage,
            "variables": self.variables,
            "origin": self.origin,
        }


@dataclass(frozen=True)
class PlanState:
    plan_id: str
    goal: str
    owner: str
    current_node: str
    status: str
    origin: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_id": self.plan_id,
            "goal": self.goal,
            "owner": self.owner,
            "current_node": self.current_node,
            "status": self.status,
            "origin": self.origin,
        }


@dataclass
class SemanticTrace:
    facts: list[SemanticFact] = field(default_factory=list)
    auction_state: list[AuctionStateVariable] = field(default_factory=list)
    applied_meanings: list[dict[str, Any]] = field(default_factory=list)
    protocol_frames: list[ProtocolFrameState] = field(default_factory=list)
    plan_states: list[PlanState] = field(default_factory=list)
    diagnostics: list[str] = field(default_factory=list)

    def add_fact(self, fact: SemanticFact) -> None:
        self.facts.append(fact)

    def add_auction_state(self, variable: AuctionStateVariable) -> None:
        self.auction_state.append(variable)

    def fact_exists(self, query: dict[str, Any]) -> bool:
        return any(fact.matches(query) for fact in self.facts)

    def matching_facts(self, query: dict[str, Any]) -> list[SemanticFact]:
        return [fact for fact in self.facts if fact.matches(query)]

    def auction_state_exists(self, query: dict[str, Any]) -> bool:
        return any(variable.matches(query) for variable in self.auction_state)

    def matching_auction_state(self, query: dict[str, Any]) -> list[AuctionStateVariable]:
        return [variable for variable in self.auction_state if variable.matches(query)]

    def auction_state_compare(self, query: dict[str, Any]) -> bool:
        lookup = dict(query.get("query", {}))
        attribute = query.get("attribute", "value")
        comparison = {key: value for key, value in query.items() if key not in ("query", "attribute")}
        matches = self.matching_auction_state(lookup)
        return any(_compare_state_value(variable.attribute(attribute), comparison) for variable in matches)

    def state_has(self, query: dict[str, Any]) -> bool:
        return all(self.fact_exists(_semantic_state_query(state_type, attributes)) for state_type, attributes in query.items())

    def add_applied_meaning(self, entry: dict[str, Any]) -> None:
        self.applied_meanings.append(entry)

    def add_protocol_frame(self, frame: ProtocolFrameState) -> None:
        self.protocol_frames.append(frame)

    def add_plan_state(self, plan_state: PlanState) -> None:
        self.plan_states.append(plan_state)

    def warn(self, text: str) -> None:
        self.diagnostics.append(text)


def _semantic_state_query(state_type: str, attributes: Any) -> dict[str, Any]:
    if attributes is None:
        attributes = {}
    if not isinstance(attributes, dict):
        raise ValueError(f"Semantic state query for {state_type} must be a mapping")
    return {"fact_type": state_type, **attributes}


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
