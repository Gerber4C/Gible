from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Purpose:
    """A bidder's private plan, fixed when its initiating call is selected."""

    kind: str
    owner: str
    source_index: int
    source_call: str
    trump: str
    status: str = "active"
    own_keycards: int | None = None
    owns_trump_queen: bool | None = None
    grand_candidate: bool | None = None
    combined_min: int | None = None
    responses: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Purpose":
        return cls(**{key: data.get(key) for key in (
            'kind', 'owner', 'source_index', 'source_call', 'trump',
            'status', 'own_keycards', 'owns_trump_queen', 'grand_candidate',
            'combined_min', 'responses') if key in data})

    def to_dict(self) -> dict[str, Any]:
        return {key: getattr(self, key) for key in (
            'kind', 'owner', 'source_index', 'source_call', 'trump',
            'status', 'own_keycards', 'owns_trump_queen', 'grand_candidate',
            'combined_min', 'responses')}


@dataclass(frozen=True)
class MemoryRoute:
    qualified_id: str
    route_id: str | None
    goal: str | None
    owner: str | None
    origin: dict[str, Any]
    last_call: str | None = None
    last_node: str | None = None
    source_kind: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_candidate(cls, candidate: Any) -> "MemoryRoute | None":
        origin = getattr(candidate, "private_route_origin", None)
        if not origin:
            return None
        metadata = dict(getattr(candidate, "metadata", {}) or {})
        return cls(
            qualified_id=origin["qualified_id"],
            route_id=metadata.get("route_id") or origin.get("object_id"),
            goal=metadata.get("route_goal"),
            owner=origin.get("owner"),
            origin=dict(origin),
            last_call=getattr(candidate, "call", None),
            last_node=metadata.get("route_node"),
            source_kind=getattr(candidate, "source_kind", None),
            metadata=metadata,
        )

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "MemoryRoute":
        return cls(
            qualified_id=str(data["qualified_id"]),
            route_id=data.get("route_id"),
            goal=data.get("goal"),
            owner=data.get("owner"),
            origin=dict(data.get("origin", {})),
            last_call=data.get("last_call"),
            last_node=data.get("last_node"),
            source_kind=data.get("source_kind"),
            metadata=dict(data.get("metadata", {}) or {}),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "qualified_id": self.qualified_id,
            "route_id": self.route_id,
            "goal": self.goal,
            "owner": self.owner,
            "origin": self.origin,
            "last_call": self.last_call,
            "last_node": self.last_node,
            "source_kind": self.source_kind,
            "metadata": self.metadata,
        }


@dataclass(frozen=True)
class SeatMemory:
    selected_routes: tuple[MemoryRoute, ...] = ()
    purposes: tuple[Purpose, ...] = ()

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "SeatMemory":
        if not data:
            return cls()
        return cls(
            selected_routes=tuple(
                MemoryRoute.from_dict(item)
                for item in data.get("selected_routes", []) or []
            ),
            purposes=tuple(Purpose.from_dict(item) for item in data.get('purposes', []) or []),
        )

    @classmethod
    def coerce(cls, value: "SeatMemory | dict[str, Any] | None") -> "SeatMemory":
        if isinstance(value, SeatMemory):
            return value
        if value is None:
            return cls()
        return cls.from_dict(value)

    def remember_candidate(self, candidate: Any | None) -> "SeatMemory":
        memory_route = MemoryRoute.from_candidate(candidate)
        if memory_route is None:
            return self
        routes = [route for route in self.selected_routes if route.qualified_id != memory_route.qualified_id]
        routes.append(memory_route)
        return SeatMemory(selected_routes=tuple(routes), purposes=self.purposes)

    def with_purpose(self, purpose: Purpose) -> "SeatMemory":
        return SeatMemory(selected_routes=self.selected_routes,
                          purposes=(*self.purposes, purpose))

    def replace_purpose(self, old: Purpose, new: Purpose) -> "SeatMemory":
        return SeatMemory(selected_routes=self.selected_routes,
                          purposes=tuple(new if item is old else item for item in self.purposes))

    def has_selected_route(self, origin: dict[str, Any] | None) -> bool:
        if not origin:
            return False
        qualified_id = origin.get("qualified_id")
        return any(route.qualified_id == qualified_id for route in self.selected_routes)

    def has_any_selected_route(self) -> bool:
        return bool(self.selected_routes)

    def to_dict(self) -> dict[str, Any]:
        return {
            "selected_routes": [route.to_dict() for route in self.selected_routes],
            "purposes": [purpose.to_dict() for purpose in self.purposes],
        }
