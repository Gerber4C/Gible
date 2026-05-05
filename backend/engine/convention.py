from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .calls import normalize_call, normalize_pattern


PLAN_NODE_KINDS = frozenset(
    {
        "make_call",
        "wait_for_call",
        "branch",
        "select_by_policy",
        "enter_protocol",
        "update_plan_state",
        "end_plan",
        "fail_plan",
    }
)

PLAN_BRANCH_PREDICATE_KINDS = frozenset(
    {
        "call_is",
        "call_act_type_is",
        "protocol_frame_matches",
        "state_has",
        "state_missing",
        "hand_predicate",
        "environment_predicate",
        "interference_level",
        "obligation_status",
    }
)

PLAN_GOALS = frozenset(
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
class Convention:
    id: str
    namespace: str
    name: str
    version: str
    author: Author
    call_specifications: tuple["CallSpecification", ...]
    protocol_frames: tuple["ProtocolFrame", ...] = ()
    bidding_plans: tuple["BiddingPlan", ...] = ()
    call_selection_policies: tuple["CallSelectionPolicy", ...] = ()
    named_evaluators: tuple["NamedEvaluator", ...] = ()
    relay_automata: tuple["RelayAutomaton", ...] = ()
    description: str | None = None
    system_notes: str | None = None

    @classmethod
    def from_parts(
        cls,
        metadata: dict[str, Any],
        call_specification_data: list[dict[str, Any]],
        protocol_frame_data: list[dict[str, Any]] | None = None,
        bidding_plan_data: list[dict[str, Any]] | None = None,
        call_selection_policy_data: list[dict[str, Any]] | None = None,
        named_evaluator_data: list[dict[str, Any]] | None = None,
        relay_automaton_data: list[dict[str, Any]] | None = None,
    ) -> "Convention":
        author = Author.from_dict(metadata.get("author"))
        convention_shell = cls(
            id=metadata["id"],
            namespace=metadata.get("namespace", metadata["id"]),
            name=metadata["name"],
            version=metadata.get("version", "0.1.0"),
            author=author,
            call_specifications=(),
            description=metadata.get("description"),
            system_notes=metadata.get("system_notes"),
        )
        call_specifications = tuple(
            CallSpecification.from_dict(item, convention_shell, author) for item in call_specification_data
        )
        protocol_frames = tuple(
            ProtocolFrame.from_dict(item, convention_shell, author) for item in (protocol_frame_data or [])
        )
        bidding_plans = tuple(BiddingPlan.from_dict(item, convention_shell, author) for item in (bidding_plan_data or []))
        call_selection_policies = tuple(
            CallSelectionPolicy.from_dict(item, convention_shell, author) for item in (call_selection_policy_data or [])
        )
        named_evaluators = tuple(
            NamedEvaluator.from_dict(item, convention_shell, author) for item in (named_evaluator_data or [])
        )
        relay_automata = tuple(
            RelayAutomaton.from_dict(item, convention_shell, author) for item in (relay_automaton_data or [])
        )
        return cls(
            id=convention_shell.id,
            namespace=convention_shell.namespace,
            name=convention_shell.name,
            version=convention_shell.version,
            author=convention_shell.author,
            call_specifications=call_specifications,
            protocol_frames=protocol_frames,
            bidding_plans=bidding_plans,
            call_selection_policies=call_selection_policies,
            named_evaluators=named_evaluators,
            relay_automata=relay_automata,
            description=convention_shell.description,
            system_notes=convention_shell.system_notes,
        )

    @property
    def qualified_id(self) -> str:
        return f"{self.namespace}/{self.id}@{self.version}"


@dataclass(frozen=True)
class ConventionSet:
    id: str
    name: str
    version: str
    author: Author
    conventions: tuple[Convention, ...]
    description: str | None = None
    system_notes: str | None = None

    @property
    def call_specifications(self) -> tuple["CallSpecification", ...]:
        return tuple(item for convention in self.conventions for item in convention.call_specifications)

    @property
    def protocol_frames(self) -> tuple["ProtocolFrame", ...]:
        return tuple(item for convention in self.conventions for item in convention.protocol_frames)

    @property
    def bidding_plans(self) -> tuple["BiddingPlan", ...]:
        return tuple(item for convention in self.conventions for item in convention.bidding_plans)

    @property
    def call_selection_policies(self) -> tuple["CallSelectionPolicy", ...]:
        return tuple(item for convention in self.conventions for item in convention.call_selection_policies)

    @property
    def named_evaluators(self) -> tuple["NamedEvaluator", ...]:
        return tuple(item for convention in self.conventions for item in convention.named_evaluators)

    @property
    def relay_automata(self) -> tuple["RelayAutomaton", ...]:
        return tuple(item for convention in self.conventions for item in convention.relay_automata)


@dataclass(frozen=True)
class CallSpecification:
    id: str
    context: dict[str, Any]
    call: str
    convention_id: str
    convention_namespace: str
    convention_version: str
    convention_name: str
    author: Author
    call_act_types: tuple[str, ...] = ()
    requires: dict[str, Any] = field(default_factory=dict)
    applicability: dict[str, Any] = field(default_factory=dict)
    selection: dict[str, Any] = field(default_factory=dict)
    meaning: dict[str, Any] = field(default_factory=dict)
    effects: tuple[dict[str, Any], ...] = ()
    default_policy: bool = False
    description: str | None = None
    system_notes: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], convention: Convention, inherited_author: Author) -> "CallSpecification":
        context = _normalize_context(data.get("context", {}) or {})
        meaning = data.get("meaning", {}) or {}
        call_act_types = tuple(data.get("call_act_types", meaning.get("call_act_types", [])) or [])
        return cls(
            id=data["id"],
            context=context,
            call=normalize_call(data["call"]),
            convention_id=convention.id,
            convention_namespace=convention.namespace,
            convention_version=convention.version,
            convention_name=convention.name,
            author=Author.from_dict(data.get("author")) if data.get("author") else inherited_author,
            call_act_types=call_act_types,
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
    def has_selection(self) -> bool:
        return bool(self.selection)

    @property
    def has_meaning(self) -> bool:
        return bool(self.meaning)

    @property
    def qualified_id(self) -> str:
        return f"{self.convention_namespace}/{self.convention_id}@{self.convention_version}:call_specification:{self.id}"

    def origin_dict(self) -> dict[str, Any]:
        return {
            "namespace": self.convention_namespace,
            "convention_id": self.convention_id,
            "convention_name": self.convention_name,
            "convention_version": self.convention_version,
            "object_type": "call_specification",
            "object_id": self.id,
            "qualified_id": self.qualified_id,
            "author": self.author.to_dict(),
        }


@dataclass(frozen=True)
class ProtocolFrame:
    id: str
    frame_type: str
    context: dict[str, Any]
    source_convention_id: str
    source_convention_namespace: str
    source_convention_version: str
    source_convention_name: str
    author: Author
    description: str | None = None
    system_notes: str | None = None
    variables: dict[str, Any] = field(default_factory=dict)
    stages: tuple[Any, ...] = ()
    allowed_continuations: tuple[Any, ...] = ()
    break_conditions: tuple[Any, ...] = ()
    source_call: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], convention: Convention, inherited_author: Author) -> "ProtocolFrame":
        return cls(
            id=data["id"],
            frame_type=data["frame_type"],
            context=_normalize_context(data.get("context", {}) or {}),
            source_convention_id=convention.id,
            source_convention_namespace=convention.namespace,
            source_convention_version=convention.version,
            source_convention_name=convention.name,
            author=Author.from_dict(data.get("author")) if data.get("author") else inherited_author,
            description=data.get("description"),
            system_notes=data.get("system_notes"),
            variables=data.get("variables", {}) or {},
            stages=tuple(data.get("stages", []) or []),
            allowed_continuations=tuple(data.get("allowed_continuations", []) or []),
            break_conditions=tuple(data.get("break_conditions", []) or []),
            source_call=normalize_call(data["source_call"]) if data.get("source_call") else None,
        )

    def origin_dict(self) -> dict[str, Any]:
        return _ir_origin(
            self.source_convention_namespace,
            self.source_convention_id,
            self.source_convention_name,
            self.source_convention_version,
            "protocol_frame",
            self.id,
            self.author,
        )


@dataclass(frozen=True)
class BiddingPlan:
    id: str
    owner: str
    goal: str
    context: dict[str, Any]
    preconditions: dict[str, Any]
    entry_call: str
    workflow: dict[str, Any]
    source_convention_id: str
    source_convention_namespace: str
    source_convention_version: str
    source_convention_name: str
    author: Author
    selection: dict[str, Any] = field(default_factory=dict)
    entry_candidate: bool = False
    entry_score: int = 100
    description: str | None = None
    system_notes: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], convention: Convention, inherited_author: Author) -> "BiddingPlan":
        if data["goal"] not in PLAN_GOALS:
            raise ValueError(f"Unsupported plan goal: {data['goal']}")
        workflow = data.get("workflow", {}) or {}
        _validate_plan_workflow(workflow)
        return cls(
            id=data["id"],
            owner=data["owner"],
            goal=data["goal"],
            context=_normalize_context(data.get("context", {}) or {}),
            preconditions=data.get("preconditions", {}) or {},
            entry_call=normalize_call(data["entry_call"]),
            workflow=workflow,
            source_convention_id=convention.id,
            source_convention_namespace=convention.namespace,
            source_convention_version=convention.version,
            source_convention_name=convention.name,
            author=Author.from_dict(data.get("author")) if data.get("author") else inherited_author,
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
        return _ir_origin(
            self.source_convention_namespace,
            self.source_convention_id,
            self.source_convention_name,
            self.source_convention_version,
            "bidding_plan",
            self.id,
            self.author,
        )


@dataclass(frozen=True)
class CallSelectionPolicy:
    id: str
    algorithm: str
    source_convention_id: str
    source_convention_namespace: str
    source_convention_version: str
    source_convention_name: str
    author: Author
    scope: dict[str, Any] = field(default_factory=dict)
    candidate_filter: dict[str, Any] = field(default_factory=dict)
    tie_breaker: str = "diagnose"
    same_call_resolution: str = "diagnose"
    choices: tuple[Any, ...] = ()
    fallback: str = "highest_score"
    evaluators: tuple[Any, ...] = ()
    random_source: dict[str, Any] = field(default_factory=dict)
    description: str | None = None
    system_notes: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], convention: Convention, inherited_author: Author) -> "CallSelectionPolicy":
        return cls(
            id=data["id"],
            algorithm=data.get("algorithm", "highest_score"),
            source_convention_id=convention.id,
            source_convention_namespace=convention.namespace,
            source_convention_version=convention.version,
            source_convention_name=convention.name,
            author=Author.from_dict(data.get("author")) if data.get("author") else inherited_author,
            scope=_normalize_scope(data.get("scope", {}) or {}),
            candidate_filter=data.get("candidate_filter", {}) or {},
            tie_breaker=data.get("tie_breaker", "diagnose"),
            same_call_resolution=data.get("same_call_resolution", "diagnose"),
            choices=tuple(data.get("choices", []) or []),
            fallback=data.get("fallback", "highest_score"),
            evaluators=tuple(data.get("evaluators", []) or []),
            random_source=data.get("random_source", {}) or {},
            description=data.get("description"),
            system_notes=data.get("system_notes"),
        )

    @property
    def qualified_id(self) -> str:
        return (
            f"{self.source_convention_namespace}/{self.source_convention_id}"
            f"@{self.source_convention_version}:call_selection_policy:{self.id}"
        )

    def origin_dict(self) -> dict[str, Any]:
        return {
            **_ir_origin(
                self.source_convention_namespace,
                self.source_convention_id,
                self.source_convention_name,
                self.source_convention_version,
                "call_selection_policy",
                self.id,
                self.author,
            ),
            "algorithm": self.algorithm,
            "tie_breaker": self.tie_breaker,
            "same_call_resolution": self.same_call_resolution,
            "fallback": self.fallback,
        }


@dataclass(frozen=True)
class NamedEvaluator:
    id: str
    evaluator_type: str
    source_convention_id: str
    source_convention_namespace: str
    source_convention_version: str
    source_convention_name: str
    author: Author
    definition: dict[str, Any] = field(default_factory=dict)
    description: str | None = None
    system_notes: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any], convention: Convention, inherited_author: Author) -> "NamedEvaluator":
        return cls(
            id=data["id"],
            evaluator_type=data["evaluator_type"],
            source_convention_id=convention.id,
            source_convention_namespace=convention.namespace,
            source_convention_version=convention.version,
            source_convention_name=convention.name,
            author=Author.from_dict(data.get("author")) if data.get("author") else inherited_author,
            definition=data.get("definition", {}) or {},
            description=data.get("description"),
            system_notes=data.get("system_notes"),
        )

    def origin_dict(self) -> dict[str, Any]:
        return _ir_origin(
            self.source_convention_namespace,
            self.source_convention_id,
            self.source_convention_name,
            self.source_convention_version,
            "named_evaluator",
            self.id,
            self.author,
        )


@dataclass(frozen=True)
class RelayAutomaton:
    id: str
    source_convention_id: str
    source_convention_namespace: str
    source_convention_version: str
    source_convention_name: str
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
    def from_dict(cls, data: dict[str, Any], convention: Convention, inherited_author: Author) -> "RelayAutomaton":
        return cls(
            id=data["id"],
            source_convention_id=convention.id,
            source_convention_namespace=convention.namespace,
            source_convention_version=convention.version,
            source_convention_name=convention.name,
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
        return _ir_origin(
            self.source_convention_namespace,
            self.source_convention_id,
            self.source_convention_name,
            self.source_convention_version,
            "relay_automaton",
            self.id,
            self.author,
        )


def _normalize_context(context: dict[str, Any]) -> dict[str, Any]:
    if "auction_pattern" in context:
        context = {**context, "auction_pattern": normalize_pattern(context["auction_pattern"])}
    return context


def _normalize_scope(scope: dict[str, Any]) -> dict[str, Any]:
    context = scope.get("context")
    if isinstance(context, dict):
        return {**scope, "context": _normalize_context(context)}
    return scope


def _validate_plan_workflow(workflow: dict[str, Any]) -> None:
    start = workflow.get("start")
    nodes = workflow.get("nodes")
    if not isinstance(start, str) or not start:
        raise ValueError("Bidding plan workflow requires a non-empty start node")
    if not isinstance(nodes, dict) or not nodes:
        raise ValueError("Bidding plan workflow requires nodes")
    if start not in nodes:
        raise ValueError(f"Bidding plan start node is missing: {start}")
    for node_id, node in nodes.items():
        kind = node.get("kind")
        if kind not in PLAN_NODE_KINDS:
            raise ValueError(f"Unsupported Bidding Plan node kind for {node_id}: {kind}")
        for branch in node.get("branches", []) or []:
            predicate = branch.get("when", {})
            _validate_branch_predicate(predicate, node_id)
            goto = branch.get("goto")
            if goto is not None and goto not in nodes:
                raise ValueError(f"Bidding Plan node {node_id} branches to unknown node: {goto}")


def _validate_branch_predicate(predicate: dict[str, Any], node_id: str) -> None:
    if not predicate:
        raise ValueError(f"Bidding Plan branch in {node_id} requires a typed predicate")
    kind = predicate.get("kind")
    if kind not in PLAN_BRANCH_PREDICATE_KINDS:
        raise ValueError(f"Unsupported Bidding Plan branch predicate kind in {node_id}: {kind}")


def _ir_origin(
    namespace: str,
    convention_id: str,
    convention_name: str,
    convention_version: str,
    object_type: str,
    object_id: str,
    author: Author,
) -> dict[str, Any]:
    qualified_id = f"{namespace}/{convention_id}@{convention_version}:{object_type}:{object_id}"
    return {
        "namespace": namespace,
        "convention_id": convention_id,
        "convention_name": convention_name,
        "convention_version": convention_version,
        "object_type": object_type,
        "object_id": object_id,
        "qualified_id": qualified_id,
        "author": author.to_dict(),
    }
