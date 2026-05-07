from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .calls import normalize_call, normalize_pattern


PRIVATE_ROUTE_NODE_KINDS = frozenset(
    {
        "make_call",
        "wait_for_call",
        "branch",
        "select_by_policy",
        "enter_frame",
        "update_route_state",
        "end_route",
        "fail_route",
    }
)

PRIVATE_ROUTE_BRANCH_PREDICATE_KINDS = frozenset(
    {
        "call_is",
        "call_act_type_is",
        "frame_matches",
        "state_has",
        "state_missing",
        "hand_predicate",
        "environment_predicate",
        "interference_level",
        "obligation_status",
    }
)

PRIVATE_ROUTE_GOALS = frozenset(
    {
        "signoff",
        "invite_game",
        "force_game",
        "explore_slam",
        "ask_keycards",
        "resolve_shape",
        "show_feature",
        "compete",
        "escape",
        "place_contract",
    }
)


@dataclass(frozen=True)
class Author:
    name: str
    contact: str | None = None
    organization: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any] | None) -> "Author":
        data = data or {}
        return cls(
            name=data.get("name", "Unknown"),
            contact=data.get("contact"),
            organization=data.get("organization"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "contact": self.contact,
            "organization": self.organization,
        }


@dataclass(frozen=True)
class SourceInfo:
    id: str
    namespace: str
    name: str
    version: str
    author: Author
    kind: str

    @property
    def qualified_id(self) -> str:
        return f"{self.namespace}/{self.id}@{self.version}"

    def origin_dict(self, object_type: str, object_id: str) -> dict[str, Any]:
        qualified_id = f"{self.qualified_id}:{object_type}:{object_id}"
        result = {
            "namespace": self.namespace,
            "object_type": object_type,
            "object_id": object_id,
            "qualified_id": qualified_id,
            "author": self.author.to_dict(),
        }
        if self.kind == "profile":
            result.update(
                {
                    "profile_id": self.id,
                    "profile_name": self.name,
                    "profile_version": self.version,
                }
            )
        else:
            result.update(
                {
                    "gadget_id": self.id,
                    "gadget_name": self.name,
                    "gadget_version": self.version,
                }
            )
        return result


@dataclass(frozen=True)
class Gadget:
    id: str
    namespace: str
    name: str
    version: str
    author: Author
    call_specs: tuple["CallSpec", ...]
    frame_specs: tuple["FrameSpec", ...] = ()
    private_route_specs: tuple["PrivateRouteSpec", ...] = ()
    policy_functions: tuple["PolicyFunction", ...] = ()
    evaluator_specs: tuple["EvaluatorSpec", ...] = ()
    relay_specs: tuple["RelaySpec", ...] = ()
    description: str | None = None
    system_notes: str | None = None

    @classmethod
    def from_parts(
        cls,
        metadata: dict[str, Any],
        call_spec_data: list[dict[str, Any]],
        frame_data: list[dict[str, Any]] | None = None,
        private_route_data: list[dict[str, Any]] | None = None,
        evaluator_data: list[dict[str, Any]] | None = None,
        relay_data: list[dict[str, Any]] | None = None,
    ) -> "Gadget":
        author = Author.from_dict(metadata.get("author"))
        source = SourceInfo(
            id=metadata["id"],
            namespace=metadata.get("namespace", metadata["id"]),
            name=metadata.get("name", metadata["id"]),
            version=metadata.get("version", "0.1.0"),
            author=author,
            kind="gadget",
        )
        return cls(
            id=source.id,
            namespace=source.namespace,
            name=source.name,
            version=source.version,
            author=source.author,
            call_specs=tuple(CallSpec.from_dict(item, source, author) for item in call_spec_data),
            frame_specs=tuple(FrameSpec.from_dict(item, source, author) for item in (frame_data or [])),
            private_route_specs=tuple(PrivateRouteSpec.from_dict(item, source, author) for item in (private_route_data or [])),
            policy_functions=(),
            evaluator_specs=tuple(EvaluatorSpec.from_dict(item, source, author) for item in (evaluator_data or [])),
            relay_specs=tuple(RelaySpec.from_dict(item, source, author) for item in (relay_data or [])),
            description=metadata.get("description"),
            system_notes=metadata.get("system_notes"),
        )

    @property
    def source_info(self) -> SourceInfo:
        return SourceInfo(self.id, self.namespace, self.name, self.version, self.author, "gadget")

    @property
    def qualified_id(self) -> str:
        return self.source_info.qualified_id

    @property
    def call_specifications(self) -> tuple["CallSpec", ...]:
        return self.call_specs


@dataclass(frozen=True)
class PartnershipProfile:
    id: str
    name: str
    version: str
    author: Author
    gadgets: tuple[Gadget, ...]
    policy_functions: tuple["PolicyFunction", ...] = ()
    evaluator_specs: tuple["EvaluatorSpec", ...] = ()
    description: str | None = None
    system_notes: str | None = None

    @property
    def source_info(self) -> SourceInfo:
        return SourceInfo(self.id, self.id, self.name, self.version, self.author, "profile")

    @property
    def call_specs(self) -> tuple["CallSpec", ...]:
        return tuple(item for gadget in self.gadgets for item in gadget.call_specs)

    @property
    def call_specifications(self) -> tuple["CallSpec", ...]:
        return self.call_specs

    @property
    def frame_specs(self) -> tuple["FrameSpec", ...]:
        return tuple(item for gadget in self.gadgets for item in gadget.frame_specs)

    @property
    def private_route_specs(self) -> tuple["PrivateRouteSpec", ...]:
        return tuple(item for gadget in self.gadgets for item in gadget.private_route_specs)

    @property
    def all_policy_functions(self) -> tuple["PolicyFunction", ...]:
        return (*self.policy_functions, *(item for gadget in self.gadgets for item in gadget.policy_functions))

    @property
    def all_evaluator_specs(self) -> tuple["EvaluatorSpec", ...]:
        return (*self.evaluator_specs, *(item for gadget in self.gadgets for item in gadget.evaluator_specs))

    @property
    def relay_specs(self) -> tuple["RelaySpec", ...]:
        return tuple(item for gadget in self.gadgets for item in gadget.relay_specs)

    @property
    def private_routes(self) -> tuple["PrivateRouteSpec", ...]:
        return self.private_route_specs

    @property
    def named_evaluators(self) -> tuple["EvaluatorSpec", ...]:
        return self.all_evaluator_specs


@dataclass(frozen=True)
class CallSpec:
    id: str
    context: dict[str, Any]
    call: str | None
    source: SourceInfo
    author: Author
    call_template: dict[str, Any] = field(default_factory=dict)
    call_act_types: tuple[str, ...] = ()
    capabilities: tuple[str, ...] = ()
    requires: dict[str, Any] = field(default_factory=dict)
    applicability: dict[str, Any] = field(default_factory=dict)
    selection: dict[str, Any] = field(default_factory=dict)
    meaning: dict[str, Any] = field(default_factory=dict)
    effects: tuple[dict[str, Any], ...] = ()
    default_policy: bool = False
    description: str | None = None
    system_notes: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], source: SourceInfo, inherited_author: Author) -> "CallSpec":
        context = _normalize_context(data.get("context", {}) or {})
        meaning = data.get("meaning", {}) or {}
        call_act_types = tuple(data.get("call_act_types", meaning.get("call_act_types", [])) or [])
        capabilities = _string_tuple(data.get("capabilities", meaning.get("capabilities", [])))
        return cls(
            id=data["id"],
            context=context,
            call=normalize_call(data["call"]) if isinstance(data.get("call"), str) else None,
            source=source,
            author=Author.from_dict(data.get("author")) if data.get("author") else inherited_author,
            call_template=data.get("call_template", data["call"] if isinstance(data.get("call"), dict) else {}) or {},
            call_act_types=call_act_types,
            capabilities=capabilities,
            requires=data.get("requires", {}) or {},
            applicability=data.get("applicability", {}) or {},
            selection=data.get("selection", {}) or {},
            meaning=meaning,
            effects=tuple(data.get("effects", []) or []),
            default_policy=bool(data.get("default_policy", False)),
            description=data.get("description"),
            system_notes=data.get("system_notes"),
        )

    @property
    def auction_pattern(self) -> str:
        return self.context.get("auction_pattern", "")

    @property
    def has_static_call(self) -> bool:
        return self.call is not None

    @property
    def has_selection(self) -> bool:
        return bool(self.selection)

    @property
    def has_meaning(self) -> bool:
        return bool(self.meaning)

    @property
    def qualified_id(self) -> str:
        return self.source.origin_dict("call_spec", self.id)["qualified_id"]

    def origin_dict(self) -> dict[str, Any]:
        return self.source.origin_dict("call_spec", self.id)


@dataclass(frozen=True)
class FrameSpec:
    id: str
    frame_type: str
    context: dict[str, Any]
    source: SourceInfo
    author: Author
    description: str | None = None
    system_notes: str | None = None
    variables: dict[str, Any] = field(default_factory=dict)
    obligation: dict[str, Any] = field(default_factory=dict)
    stages: tuple[Any, ...] = ()
    allowed_continuations: tuple[Any, ...] = ()
    break_conditions: tuple[Any, ...] = ()
    closes: tuple[str, ...] = ()
    close_on_actions: tuple[str, ...] = ()
    close_on_act_types: tuple[str, ...] = ()
    source_call: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], source: SourceInfo, inherited_author: Author) -> "FrameSpec":
        return cls(
            id=data["id"],
            frame_type=data["frame_type"],
            context=_normalize_context(data.get("context", {}) or {}),
            source=source,
            author=Author.from_dict(data.get("author")) if data.get("author") else inherited_author,
            description=data.get("description"),
            system_notes=data.get("system_notes"),
            variables=data.get("variables", {}) or {},
            obligation=data.get("obligation", {}) or {},
            stages=tuple(data.get("stages", []) or []),
            allowed_continuations=tuple(data.get("allowed_continuations", []) or []),
            break_conditions=tuple(data.get("break_conditions", []) or []),
            closes=tuple(data.get("closes", []) or []),
            close_on_actions=tuple(data.get("close_on_actions", []) or []),
            close_on_act_types=tuple(data.get("close_on_act_types", []) or []),
            source_call=normalize_call(data["source_call"]) if data.get("source_call") else None,
        )

    def origin_dict(self) -> dict[str, Any]:
        return self.source.origin_dict("frame_spec", self.id)


@dataclass(frozen=True)
class PrivateRouteSpec:
    id: str
    owner: str
    goal: str
    context: dict[str, Any]
    preconditions: dict[str, Any]
    entry_call: str
    workflow: dict[str, Any]
    source: SourceInfo
    author: Author
    capabilities: tuple[str, ...] = ()
    selection: dict[str, Any] = field(default_factory=dict)
    entry_candidate: bool = False
    entry_score: int = 100
    description: str | None = None
    system_notes: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], source: SourceInfo, inherited_author: Author) -> "PrivateRouteSpec":
        if data["goal"] not in PRIVATE_ROUTE_GOALS:
            raise ValueError(f"Unsupported PrivateRoute goal: {data['goal']}")
        workflow = data.get("workflow", {}) or {}
        _validate_private_route_workflow(workflow)
        return cls(
            id=data["id"],
            owner=data["owner"],
            goal=data["goal"],
            context=_normalize_context(data.get("context", {}) or {}),
            preconditions=data.get("preconditions", {}) or {},
            entry_call=normalize_call(data["entry_call"]),
            workflow=workflow,
            source=source,
            author=Author.from_dict(data.get("author")) if data.get("author") else inherited_author,
            capabilities=_string_tuple(data.get("capabilities", [])),
            selection=data.get("selection", {}) or {},
            entry_candidate=bool(data.get("entry_candidate", False)),
            entry_score=int(data.get("entry_score", 100)),
            description=data.get("description"),
            system_notes=data.get("system_notes"),
        )

    @property
    def start_node(self) -> str:
        return self.workflow["start"]

    def origin_dict(self) -> dict[str, Any]:
        return self.source.origin_dict("private_route_spec", self.id)


@dataclass(frozen=True)
class PolicyFunction:
    id: str
    procedure: Any
    source: SourceInfo
    author: Author
    source_path: str | None = None

    @property
    def qualified_id(self) -> str:
        return self.origin_dict()["qualified_id"]

    def origin_dict(self) -> dict[str, Any]:
        return {
            **self.source.origin_dict("policy_function", self.id),
            "algorithm": "python_bsl_function",
            "source_path": self.source_path,
        }


@dataclass(frozen=True)
class EvaluatorSpec:
    id: str
    evaluator_type: str
    source: SourceInfo
    author: Author
    definition: dict[str, Any] = field(default_factory=dict)
    description: str | None = None
    system_notes: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], source: SourceInfo, inherited_author: Author) -> "EvaluatorSpec":
        return cls(
            id=data["id"],
            evaluator_type=data["evaluator_type"],
            source=source,
            author=Author.from_dict(data.get("author")) if data.get("author") else inherited_author,
            definition=data.get("definition", {}) or {},
            description=data.get("description"),
            system_notes=data.get("system_notes"),
        )

    def origin_dict(self) -> dict[str, Any]:
        return self.source.origin_dict("evaluator_spec", self.id)


@dataclass(frozen=True)
class RelaySpec:
    id: str
    source: SourceInfo
    author: Author
    asker: str
    describer: str
    current_stage: str | None = None
    next_relay_call: str | None = None
    response_decoder: dict[str, Any] = field(default_factory=dict)
    step_table: dict[str, Any] = field(default_factory=dict)
    reserved_calls: tuple[Any, ...] = ()
    break_conditions: tuple[Any, ...] = ()
    interference_policy: dict[str, Any] = field(default_factory=dict)
    description: str | None = None
    system_notes: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], source: SourceInfo, inherited_author: Author) -> "RelaySpec":
        return cls(
            id=data["id"],
            source=source,
            author=Author.from_dict(data.get("author")) if data.get("author") else inherited_author,
            asker=data["asker"],
            describer=data["describer"],
            current_stage=data.get("current_stage"),
            next_relay_call=data.get("next_relay_call"),
            response_decoder=data.get("response_decoder", {}) or {},
            step_table=data.get("step_table", {}) or {},
            reserved_calls=tuple(data.get("reserved_calls", []) or []),
            break_conditions=tuple(data.get("break_conditions", []) or []),
            interference_policy=data.get("interference_policy", {}) or {},
            description=data.get("description"),
            system_notes=data.get("system_notes"),
        )

    def origin_dict(self) -> dict[str, Any]:
        return self.source.origin_dict("relay_spec", self.id)


def _normalize_context(context: dict[str, Any]) -> dict[str, Any]:
    if "auction_pattern" in context:
        context = {**context, "auction_pattern": normalize_pattern(context["auction_pattern"])}
    return context


def _normalize_scope(scope: dict[str, Any]) -> dict[str, Any]:
    context = scope.get("context")
    if isinstance(context, dict):
        return {**scope, "context": _normalize_context(context)}
    return scope


def _string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        return (value,)
    return tuple(str(item) for item in value)


def _validate_private_route_workflow(workflow: dict[str, Any]) -> None:
    start = workflow.get("start")
    nodes = workflow.get("nodes")
    if not isinstance(start, str) or not start:
        raise ValueError("PrivateRoute workflow requires a non-empty start node")
    if not isinstance(nodes, dict) or not nodes:
        raise ValueError("PrivateRoute workflow requires nodes")
    if start not in nodes:
        raise ValueError(f"PrivateRoute start node is missing: {start}")
    for node_id, node in nodes.items():
        kind = node.get("kind")
        if kind not in PRIVATE_ROUTE_NODE_KINDS:
            raise ValueError(f"Unsupported PrivateRoute node kind for {node_id}: {kind}")
        for branch in node.get("branches", []) or []:
            predicate = branch.get("when", {})
            _validate_branch_predicate(predicate, node_id)
            goto = branch.get("goto")
            if goto is not None and goto not in nodes:
                raise ValueError(f"PrivateRoute node {node_id} branches to unknown node: {goto}")


def _validate_branch_predicate(predicate: dict[str, Any], node_id: str) -> None:
    if not predicate:
        raise ValueError(f"PrivateRoute branch in {node_id} requires a typed predicate")
    kind = predicate.get("kind")
    if kind not in PRIVATE_ROUTE_BRANCH_PREDICATE_KINDS:
        raise ValueError(f"Unsupported PrivateRoute branch predicate kind in {node_id}: {kind}")
