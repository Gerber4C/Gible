from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .evaluator import evaluate_expression
from .model import Author as RuntimeAuthor
from .model import CallMeaning, StateEffect


class BSLValidationError(ValueError):
    pass


@dataclass(frozen=True)
class BSLObject:
    kind: str
    data: dict[str, Any]


@dataclass(frozen=True)
class BSLModuleData:
    profile: dict[str, Any] | None
    gadget_metadata: dict[str, Any] | None
    call_specs: list[dict[str, Any]]
    frame_specs: list[dict[str, Any]]
    private_route_specs: list[dict[str, Any]]
    evaluator_specs: list[dict[str, Any]]
    relay_specs: list[dict[str, Any]]


def load_bsl_files(paths: list[Path] | tuple[Path, ...]) -> BSLModuleData:
    collector = _Collector()
    namespace = _base_namespace(collector)
    for path in paths:
        source = path.read_text(encoding="utf-8").lstrip("\ufeff")
        _reject_unsupported_top_level_syntax(source, path)
        try:
            exec(compile(source, str(path), "exec"), namespace, namespace)
        except Exception as exc:
            raise BSLValidationError(f"{path}: {exc}") from exc
    _collect_class_authored_objects(namespace, collector)
    return collector.to_module_data()


def _reject_unsupported_top_level_syntax(source: str, path: Path) -> None:
    tree = ast.parse(source, filename=str(path))
    for statement in tree.body:
        if isinstance(statement, (ast.Import, ast.ImportFrom)):
            raise BSLValidationError(f"{path}: Unsupported top-level syntax: {statement.__class__.__name__}")


class _Collector:
    def __init__(self) -> None:
        self.profile: dict[str, Any] | None = None
        self.gadget_metadata: dict[str, Any] | None = None
        self.call_specs: list[dict[str, Any]] = []
        self.frame_specs: list[dict[str, Any]] = []
        self.private_route_specs: list[dict[str, Any]] = []
        self.evaluator_specs: list[dict[str, Any]] = []
        self.relay_specs: list[dict[str, Any]] = []

    def add(self, item: BSLObject) -> dict[str, Any]:
        if item.kind == "profile":
            if self.profile is not None:
                raise BSLValidationError("duplicate Profile object")
            self.profile = item.data
        elif item.kind == "gadget":
            if self.gadget_metadata is not None:
                raise BSLValidationError("duplicate Gadget object")
            self.gadget_metadata = item.data
        elif item.kind == "call_spec":
            self.call_specs.append(item.data)
        elif item.kind == "frame_spec":
            self.frame_specs.append(item.data)
        elif item.kind == "private_route_spec":
            self.private_route_specs.append(item.data)
        elif item.kind == "evaluator_spec":
            self.evaluator_specs.append(item.data)
        elif item.kind == "relay_spec":
            self.relay_specs.append(item.data)
        else:
            raise BSLValidationError(f"unsupported BSL object kind {item.kind}")
        return item.data

    def to_module_data(self) -> BSLModuleData:
        return BSLModuleData(
            profile=self.profile,
            gadget_metadata=self.gadget_metadata,
            call_specs=self.call_specs,
            frame_specs=self.frame_specs,
            private_route_specs=self.private_route_specs,
            evaluator_specs=self.evaluator_specs,
            relay_specs=self.relay_specs,
        )


class MeaningBuilder:
    action: str | None = None
    action_type: str | None = None
    target_suit: str | None = None
    nature: list[str]
    nature_labels: list[str]
    acts: list[str]
    call_act_types: list[str]
    forcing: str | None = None
    forcing_status: str | None = None
    alertable: bool = False
    acbl_explanation: str | None = None

    def __init__(self) -> None:
        self.action = None
        self.action_type = None
        self.target_suit = None
        self.nature = []
        self.nature_labels = []
        self.acts = []
        self.call_act_types = []
        self.forcing = None
        self.forcing_status = None
        self.alertable = False
        self.acbl_explanation = None

    def to_value(self) -> CallMeaning:
        known = {
            "action",
            "action_type",
            "target_suit",
            "nature",
            "nature_labels",
            "acts",
            "call_act_types",
            "forcing",
            "forcing_status",
            "alertable",
            "acbl_explanation",
        }
        details = {key: value for key, value in self.__dict__.items() if key not in known and value is not None}
        return CallMeaning(
            action_type=self.action_type or self.action,
            target_suit=self.target_suit,
            nature_labels=tuple(self.nature_labels or self.nature),
            call_act_types=tuple(self.call_act_types or self.acts),
            forcing_status=self.forcing_status or self.forcing,
            alertable=bool(self.alertable),
            acbl_explanation=self.acbl_explanation,
            details=details,
        )


class StateEffectBuilder:
    def __init__(
        self,
        key: str,
        *,
        namespace: str = "public",
        owner: str | None = None,
        visibility: str = "partnership",
        **attributes: Any,
    ) -> None:
        self.key = key
        self.namespace = namespace
        self.owner = owner
        self.visibility = visibility
        for attribute, value in attributes.items():
            setattr(self, attribute, value)

    def to_value(self) -> StateEffect:
        known = {"key", "namespace", "owner", "visibility"}
        attributes = {
            key: _expression_value_from_authoring(value)
            for key, value in self.__dict__.items()
            if key not in known
        }
        return StateEffect(
            key=self.key,
            attributes=attributes,
            namespace=self.namespace,
            owner=self.owner,
            visibility=self.visibility,
        )


class PuppetStaymanBuilder:
    def __init__(self, gadget: Any, id: str) -> None:
        self.gadget = gadget
        self.id = id
        self.over: str = ""
        self.ask: str = "3C"
        self.seats: list[int] = []
        self.notrump_level: int = 1
        self.ask_requires: Any = None
        self.ask_applies: Any = None
        self.description: str | None = None
        self.system_notes: str | None = None
        self._answers: list[PuppetNodeBuilder] = []
        self._continuations: list[PuppetNodeBuilder] = []
        self._resolutions: list[PuppetNodeBuilder] = []
        self._emitted = False

    def answer(self, bid: str, *, applies: Any = None, target_suit: str | None = None) -> "PuppetNodeBuilder":
        node = PuppetNodeBuilder("answer", bid, default_owner="opener", applies=applies)
        node.target_suit = target_suit
        self._answers.append(node)
        return node

    def continuation(
        self,
        *,
        after: str,
        bid: str,
        applies: Any = None,
        final: bool = False,
        target_suit: str | None = None,
    ) -> "PuppetNodeBuilder":
        node = PuppetNodeBuilder(
            "continuation",
            bid,
            after_answer=after,
            default_owner="responder",
            applies=applies,
            final=final,
        )
        node.target_suit = target_suit
        self._continuations.append(node)
        return node

    def resolution(
        self,
        *,
        after_answer: str,
        after_continuation: str,
        bid: str,
        applies: Any = None,
        target_suit: str | None = None,
    ) -> "PuppetNodeBuilder":
        node = PuppetNodeBuilder(
            "resolution",
            bid,
            after_answer=after_answer,
            after_continuation=after_continuation,
            default_owner="opener",
            applies=applies,
            final=True,
        )
        node.target_suit = target_suit
        self._resolutions.append(node)
        return node

    def emit(self) -> None:
        if self._emitted:
            return
        self._emitted = True
        if not self.over:
            raise BSLValidationError(f"Puppet Stayman flow {self.id} requires puppet.over")

        ask_call = self._new_call("ask")
        ask_call.when = f"{self.over}P"
        ask_call.seats = list(self.seats)
        ask_call.bid = self.ask
        ask_call.requires = self.ask_requires
        ask_call.applies = self.ask_applies
        ask_call.meaning.nature = ["artificial", "conventional"]
        ask_call.meaning.acts = ["inquiry", "context_initiating", "forcing"]
        ask_call.meaning.action = "puppet_stayman"
        ask_call.meaning.alertable = True
        ask_call.meaning.flow_id = self.id
        ask_call.description = self.description or f"{self.ask} starts Puppet Stayman over {self.over}."
        ask_call.system_notes = self.system_notes or f"After {self.over}, {self.ask} is Puppet Stayman."
        effect = ask_call.effect("puppet_stayman")
        effect.flow_id = self.id
        effect.notrump_level = self.notrump_level
        effect.status = "active"
        effect.stage = "opener_answer"
        effect.ask_call = self.ask

        for answer in self._answers:
            call = self._new_call(f"answer_{_call_id_fragment(answer.bid)}")
            call.when = f"{self.over}P{self.ask}P"
            call.seats = list(self.seats)
            call.bid = answer.bid
            call.requires = _puppet_state_requires(self.id, "opener_answer")
            call.applies = answer.applies
            call.capabilities = ("puppet_answer",)
            call.meaning.nature = ["artificial", "conventional"]
            call.meaning.acts = ["answer", "forcing"]
            call.meaning.action = answer.action or "puppet_answer"
            call.meaning.target_suit = answer.target_suit
            call.meaning.alertable = True
            call.meaning.flow_id = self.id
            call.description = answer.description
            call.system_notes = answer.system_notes
            self._add_stage_effect(
                call,
                stage="responder_continuation",
                answer_call=answer.bid,
                status="active",
            )
            self._copy_node_effects(call, answer)

        for continuation in self._continuations:
            call = self._new_call(
                f"continuation_{_call_id_fragment(continuation.after_answer)}_{_call_id_fragment(continuation.bid)}"
            )
            call.when = f"{self.over}P{self.ask}P{continuation.after_answer}P"
            call.seats = list(self.seats)
            call.bid = continuation.bid
            call.requires = _puppet_state_requires(
                self.id,
                "responder_continuation",
                answer_call=continuation.after_answer,
            )
            call.applies = continuation.applies
            call.capabilities = ("place_contract",) if continuation.final else ("puppet_continuation",)
            call.meaning.nature = ["natural"] if continuation.final else ["artificial", "conventional"]
            call.meaning.acts = ["final_placement"] if continuation.final else ["forcing", "relay_continuation"]
            call.meaning.action = continuation.action or (
                "place_contract" if continuation.final else "puppet_responder_continuation"
            )
            call.meaning.target_suit = continuation.target_suit or (
                _contract_suit_from_call(continuation.bid) if continuation.final else None
            )
            call.meaning.alertable = not continuation.final
            call.meaning.flow_id = self.id
            call.description = continuation.description
            call.system_notes = continuation.system_notes
            self._add_stage_effect(
                call,
                stage="complete" if continuation.final else "opener_resolution",
                answer_call=continuation.after_answer,
                continuation_call=continuation.bid,
                status="resolved" if continuation.final else "active",
            )
            if continuation.final:
                self._add_final_contract_effect(call, continuation.bid)
            self._copy_node_effects(call, continuation)

        for resolution in self._resolutions:
            call = self._new_call(
                "resolution_"
                f"{_call_id_fragment(resolution.after_answer)}_"
                f"{_call_id_fragment(resolution.after_continuation)}_"
                f"{_call_id_fragment(resolution.bid)}"
            )
            call.when = f"{self.over}P{self.ask}P{resolution.after_answer}P{resolution.after_continuation}P"
            call.seats = list(self.seats)
            call.bid = resolution.bid
            call.requires = _puppet_state_requires(
                self.id,
                "opener_resolution",
                answer_call=resolution.after_answer,
                continuation_call=resolution.after_continuation,
            )
            call.applies = resolution.applies
            call.capabilities = ("place_contract",)
            call.meaning.nature = ["natural"]
            call.meaning.acts = ["final_placement"]
            call.meaning.action = resolution.action or "place_contract"
            call.meaning.target_suit = resolution.target_suit or _contract_suit_from_call(resolution.bid)
            call.meaning.alertable = False
            call.meaning.flow_id = self.id
            call.description = resolution.description
            call.system_notes = resolution.system_notes
            self._add_stage_effect(
                call,
                stage="complete",
                answer_call=resolution.after_answer,
                continuation_call=resolution.after_continuation,
                resolution_call=resolution.bid,
                status="resolved",
            )
            self._add_final_contract_effect(call, resolution.bid)
            self._copy_node_effects(call, resolution)

    def _new_call(self, suffix: str) -> CallBuilder:
        return self.gadget.call(f"{self.id}_{suffix}")

    def _add_stage_effect(self, call: CallBuilder, **attributes: Any) -> None:
        effect = call.effect("puppet_stayman")
        effect.flow_id = self.id
        effect.notrump_level = self.notrump_level
        for key, value in attributes.items():
            setattr(effect, key, value)

    def _add_final_contract_effect(self, call: CallBuilder, contract: str) -> None:
        effect = call.effect("final_contract")
        effect.contract = contract
        effect.level = _contract_level_from_call(contract)
        effect.target_suit = _contract_suit_from_call(contract)
        effect.source = self.id

    def _copy_node_effects(self, call: CallBuilder, node: "PuppetNodeBuilder") -> None:
        for effect in node.effects:
            call.add_effect(effect)


class PuppetNodeBuilder:
    def __init__(
        self,
        kind: str,
        bid: str,
        *,
        default_owner: str,
        applies: Any = None,
        after_answer: str | None = None,
        after_continuation: str | None = None,
        final: bool = False,
    ) -> None:
        self.kind = kind
        self.bid = bid
        self.default_owner = default_owner
        self.applies = applies
        self.after_answer = after_answer
        self.after_continuation = after_continuation
        self.final = final
        self.action: str | None = None
        self.target_suit: str | None = None
        self.description: str | None = None
        self.system_notes: str | None = None
        self.effects: list[Any] = []

    def shows_length(
        self,
        suit: str,
        *,
        owner: str | None = None,
        value: int | None = None,
        min: int | None = None,
        max: int | None = None,
    ) -> "PuppetNodeBuilder":
        active_owner = owner or self.default_owner
        attributes: dict[str, Any] = {"suit": suit}
        if value is not None:
            attributes["value"] = value
            attributes["min_value"] = value
            attributes["max_value"] = value
        if min is not None:
            attributes["min_value"] = min
        if max is not None:
            attributes["max_value"] = max
        self.effects.append(StateEffectBuilder(f"{active_owner}.length.{suit}", owner=active_owner, **attributes))
        return self

    def records_fit(
        self,
        suit: str,
        *,
        opener_min: int,
        responder_min: int,
        agree_trump: bool = True,
        basis: str | None = None,
    ) -> "PuppetNodeBuilder":
        min_total = opener_min + responder_min
        pattern_floor = f"{opener_min}-{responder_min}"
        attributes = {
            "suit": suit,
            "opener_min_length": opener_min,
            "responder_min_length": responder_min,
            "min_total": min_total,
            "pattern_floor": pattern_floor,
        }
        if basis is not None:
            attributes["basis"] = basis
        self.effects.append(StateEffectBuilder(f"partnership.fit.{suit}", **attributes))
        if agree_trump:
            self.effects.append(StateEffectBuilder("agreed_suit", **attributes))
        return self

    def effect(
        self,
        key: str,
        *,
        namespace: str = "public",
        owner: str | None = None,
        visibility: str = "partnership",
        **attributes: Any,
    ) -> StateEffectBuilder:
        effect = StateEffectBuilder(key, namespace=namespace, owner=owner, visibility=visibility, **attributes)
        self.effects.append(effect)
        return effect


class CallBuilder:
    def __init__(self, id: str) -> None:
        self.id = id
        self.when: str | dict[str, Any] = ""
        self.seats: list[int] = []
        self.bid: str | dict[str, Any] | None = None
        self.call_template: dict[str, Any] = {}
        self.call_act_types: tuple[str, ...] = ()
        self.capabilities: tuple[str, ...] = ()
        self.requires: Any = None
        self.applies: Any = None
        self.meaning = MeaningBuilder()
        self.effects: list[Any] = []
        self.default_policy = False
        self.description: str | None = None
        self.system_notes: str | None = None
        self.author: Any = None

    def effect(
        self,
        key: str,
        *,
        namespace: str = "public",
        owner: str | None = None,
        visibility: str = "partnership",
        **attributes: Any,
    ) -> StateEffectBuilder:
        effect = StateEffectBuilder(key, namespace=namespace, owner=owner, visibility=visibility, **attributes)
        self.effects.append(effect)
        return effect

    def add_effect(self, effect: Any) -> Any:
        self.effects.append(effect)
        return effect

    def to_data(self) -> dict[str, Any]:
        if self.bid is None:
            raise BSLValidationError(f"Call {self.id} requires call.bid")
        data: dict[str, Any] = {
            "id": self.id,
            "context": _context_from_authoring(self.when, self.seats),
            "call": self.bid,
            "call_act_types": self.call_act_types,
            "capabilities": self.capabilities,
            "meaning": _materialize_meaning(self.meaning),
            "effects": tuple(_materialize_effect(effect) for effect in self.effects),
            "default_policy": self.default_policy,
        }
        if self.call_template:
            data["call_template"] = self.call_template
        if self.requires is not None:
            data["requires"] = _condition_from_authoring(self.requires)
        if self.applies is not None:
            data["applicability"] = _condition_from_authoring(self.applies)
        if self.description is not None:
            data["description"] = self.description
        if self.system_notes is not None:
            data["system_notes"] = self.system_notes
        if self.author is not None:
            data["author"] = _author_to_dict(self.author)
        return data


class FrameBuilder:
    def __init__(self, id: str) -> None:
        self.id = id
        self.frame_type: str | None = None
        self.when: str | dict[str, Any] = ""
        self.seats: list[int] = []
        self.description: str | None = None
        self.system_notes: str | None = None
        self.variables: dict[str, Any] = {}
        self.obligation: dict[str, Any] = {}
        self.stages: tuple[Any, ...] | list[Any] = ()
        self.allowed_continuations: tuple[Any, ...] | list[Any] = ()
        self.break_conditions: tuple[Any, ...] | list[Any] = ()
        self.closes: tuple[str, ...] | list[str] = ()
        self.close_on_actions: tuple[str, ...] | list[str] = ()
        self.close_on_act_types: tuple[str, ...] | list[str] = ()
        self.source_call: str | None = None
        self.author: Any = None

    def to_data(self) -> dict[str, Any]:
        if not self.frame_type:
            raise BSLValidationError(f"Frame {self.id} requires frame.frame_type")
        data = {
            "id": self.id,
            "frame_type": self.frame_type,
            "context": _context_from_authoring(self.when, self.seats),
            "description": self.description,
            "system_notes": self.system_notes,
            "variables": self.variables,
            "obligation": self.obligation,
            "stages": tuple(self.stages),
            "allowed_continuations": tuple(self.allowed_continuations),
            "break_conditions": tuple(self.break_conditions),
            "closes": tuple(self.closes),
            "close_on_actions": tuple(self.close_on_actions),
            "close_on_act_types": tuple(self.close_on_act_types),
            "source_call": self.source_call,
        }
        if self.author is not None:
            data["author"] = _author_to_dict(self.author)
        return {key: value for key, value in data.items() if value not in (None, (), {}, [])}


class PrivateRouteBuilder:
    def __init__(self, id: str) -> None:
        self.id = id
        self.owner: str | None = None
        self.goal: str | None = None
        self.when: str | dict[str, Any] = ""
        self.seats: list[int] = []
        self.preconditions: Any = None
        self.entry_call: str | None = None
        self.workflow: dict[str, Any] | None = None
        self.capabilities: tuple[str, ...] | list[str] = ()
        self.entry_candidate = False
        self.entry_score = 100
        self.description: str | None = None
        self.system_notes: str | None = None
        self.author: Any = None

    def to_data(self) -> dict[str, Any]:
        if not self.owner or not self.goal or not self.entry_call or self.workflow is None:
            raise BSLValidationError(f"Private route {self.id} requires owner, goal, entry_call, and workflow")
        data = {
            "id": self.id,
            "owner": self.owner,
            "goal": self.goal,
            "context": _context_from_authoring(self.when, self.seats),
            "preconditions": self.preconditions or {},
            "entry_call": self.entry_call,
            "workflow": self.workflow,
            "capabilities": tuple(self.capabilities),
            "entry_candidate": self.entry_candidate,
            "entry_score": self.entry_score,
            "description": self.description,
            "system_notes": self.system_notes,
        }
        if self.author is not None:
            data["author"] = _author_to_dict(self.author)
        return {key: value for key, value in data.items() if value not in (None, (), {}, [])}


class EvaluatorBuilder:
    def __init__(self, id: str) -> None:
        self.id = id
        self.function: Any = None
        self.description: str | None = None
        self.system_notes: str | None = None
        self.author: Any = None

    def to_data(self) -> dict[str, Any]:
        if not callable(self.function):
            raise BSLValidationError(f"Evaluator {self.id} requires evaluator.function")
        data = {
            "id": self.id,
            "evaluator_type": "python_function",
            "definition": self.function,
            "description": self.description,
            "system_notes": self.system_notes,
        }
        if self.author is not None:
            data["author"] = _author_to_dict(self.author)
        return {key: value for key, value in data.items() if value is not None}


class RelayBuilder:
    def __init__(self, id: str) -> None:
        self.id = id

    def to_data(self) -> dict[str, Any]:
        return dict(self.__dict__)


def _context_from_authoring(value: str | dict[str, Any], seats: list[int] | tuple[int, ...] | None = None) -> dict[str, Any]:
    if isinstance(value, dict):
        context = dict(value)
    else:
        context = {"auction_pattern": value}
    if seats:
        context["seat_positions"] = list(seats)
    return context


def _condition_from_authoring(value: Any) -> Any:
    if isinstance(value, dict) and "op" in value and "expr" not in value:
        return {"expr": value}
    return value


def _expression_value_from_authoring(value: Any) -> Any:
    if isinstance(value, dict) and "op" in value and "expr" not in value:
        return {"expr": value}
    if isinstance(value, list):
        return [_expression_value_from_authoring(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_expression_value_from_authoring(item) for item in value)
    return value


def _materialize_meaning(value: Any) -> Any:
    if isinstance(value, MeaningBuilder):
        return value.to_value()
    return value


def _materialize_effect(value: Any) -> Any:
    if isinstance(value, StateEffectBuilder):
        return value.to_value()
    return value


def _author_to_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, RuntimeAuthor):
        return value.to_dict()
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        return {"name": value}
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return {"name": str(value)}


def _class_metadata(cls: type, kind: str) -> dict[str, Any]:
    object_id = getattr(cls, "id", None)
    if not object_id:
        raise BSLValidationError(f"{cls.__name__} requires class attribute id")
    data = {
        "id": object_id,
        "name": getattr(cls, "name", object_id),
        "version": getattr(cls, "version", "0.1.0"),
        "author": _author_to_dict(getattr(cls, "author", {"name": "Unknown"})),
    }
    if kind == "gadget":
        data["namespace"] = getattr(cls, "namespace", object_id)
    if hasattr(cls, "gadgets"):
        data["gadgets"] = [_gadget_reference(item) for item in getattr(cls, "gadgets")]
    for key in ("description", "system_notes"):
        if getattr(cls, key, None) is not None:
            data[key] = getattr(cls, key)
    return data


def _gadget_reference(item: Any) -> str:
    if isinstance(item, str):
        return item
    if isinstance(item, type):
        return getattr(item, "id")
    return str(item)


def _puppet_state_requires(flow_id: str, stage: str, **attributes: Any):
    def requires(ctx: Any) -> bool:
        return ctx.state.exists("puppet_stayman", flow_id=flow_id, stage=stage, **attributes)

    requires.__name__ = f"requires_{_call_id_fragment(flow_id)}_{_call_id_fragment(stage)}"
    return requires


def _call_id_fragment(value: Any) -> str:
    text = str(value or "none").replace("N", "nt")
    fragment = "".join(char.lower() if char.isalnum() else "_" for char in text)
    return fragment.strip("_") or "none"


def _contract_suit_from_call(call: str) -> str | None:
    text = str(call or "")
    if not text or text == "P":
        return None
    return text[-1]


def _contract_level_from_call(call: str) -> int | None:
    text = str(call or "")
    if not text or text == "P":
        return None
    try:
        return int(text[0])
    except ValueError:
        return None


def _collect_class_authored_objects(namespace: dict[str, Any], collector: _Collector) -> None:
    profile_base = namespace["Profile"]
    gadget_base = namespace["Gadget"]
    for value in list(namespace.values()):
        if isinstance(value, type) and value is not profile_base and issubclass(value, profile_base):
            collector.add(BSLObject("profile", _class_metadata(value, "profile")))
    for value in list(namespace.values()):
        if isinstance(value, type) and value is not gadget_base and issubclass(value, gadget_base):
            instance = value()
            if not getattr(instance, "_authoring_built", False):
                instance.build()
                instance._authoring_built = True
            for flow in instance._authoring_flows:
                flow.emit()
            collector.add(BSLObject("gadget", _class_metadata(value, "gadget")))
            for item in instance._authoring_evaluators:
                collector.add(BSLObject("evaluator_spec", item.to_data()))
            for item in instance._authoring_frames:
                collector.add(BSLObject("frame_spec", item.to_data()))
            for item in instance._authoring_routes:
                collector.add(BSLObject("private_route_spec", item.to_data()))
            for item in instance._authoring_relays:
                collector.add(BSLObject("relay_spec", item.to_data()))
            for item in instance._authoring_calls:
                collector.add(BSLObject("call_spec", item.to_data()))


def _base_namespace(collector: _Collector) -> dict[str, Any]:
    def Author(name: str, contact: str | None = None, organization: str | None = None) -> dict[str, Any]:
        return {"name": name, "contact": contact, "organization": organization}

    class Profile:
        id: str = ""
        name: str | None = None
        version: str = "0.1.0"
        author: Any = {"name": "Unknown"}
        gadgets: list[Any] | tuple[Any, ...] = ()
        description: str | None = None
        system_notes: str | None = None

        def __init__(self, id: str | None = None, **kwargs: Any) -> None:
            if id is None:
                return
            data = {
                "id": id,
                "name": kwargs.pop("name", id),
                "version": kwargs.pop("version", "0.1.0"),
                "author": _author_to_dict(kwargs.pop("author", {"name": "Unknown"})),
                "gadgets": kwargs.pop("gadgets", []),
                **kwargs,
            }
            collector.add(BSLObject("profile", data))

    class Gadget:
        id: str = ""
        namespace: str | None = None
        name: str | None = None
        version: str = "0.1.0"
        author: Any = {"name": "Unknown"}
        description: str | None = None
        system_notes: str | None = None

        def __init__(self, id: str | None = None, **kwargs: Any) -> None:
            self._authoring_calls: list[CallBuilder] = []
            self._authoring_frames: list[FrameBuilder] = []
            self._authoring_routes: list[PrivateRouteBuilder] = []
            self._authoring_evaluators: list[EvaluatorBuilder] = []
            self._authoring_relays: list[RelayBuilder] = []
            self._authoring_flows: list[PuppetStaymanBuilder] = []
            self._authoring_built = False
            if id is None:
                return
            data = {
                "id": id,
                "namespace": kwargs.pop("namespace", id),
                "name": kwargs.pop("name", id),
                "version": kwargs.pop("version", "0.1.0"),
                "author": _author_to_dict(kwargs.pop("author", {"name": "Unknown"})),
                **kwargs,
            }
            collector.add(BSLObject("gadget", data))

        def build(self) -> None:
            return None

        def call(self, id: str) -> CallBuilder:
            item = CallBuilder(id)
            self._authoring_calls.append(item)
            return item

        def frame(self, id: str) -> FrameBuilder:
            item = FrameBuilder(id)
            self._authoring_frames.append(item)
            return item

        def route(self, id: str) -> PrivateRouteBuilder:
            item = PrivateRouteBuilder(id)
            self._authoring_routes.append(item)
            return item

        def evaluator(self, id: str, function: Any | None = None) -> EvaluatorBuilder:
            item = EvaluatorBuilder(id)
            item.function = function
            self._authoring_evaluators.append(item)
            return item

        def relay(self, id: str) -> RelayBuilder:
            item = RelayBuilder(id)
            self._authoring_relays.append(item)
            return item

        def puppet_stayman(self, id: str) -> PuppetStaymanBuilder:
            item = PuppetStaymanBuilder(self, id)
            self._authoring_flows.append(item)
            return item

    def Call(id: str, **kwargs: Any) -> dict[str, Any]:
        if "selection" in kwargs:
            raise BSLValidationError(
                "Call selection must be written as Python: use applies=<function> for eligibility "
                "and profile/gadget policy functions for choosing among candidates."
            )
        call = kwargs.pop("bid", kwargs.pop("call", None))
        if call is None:
            raise BSLValidationError("Call requires bid=... or call=...")
        data = {
            "id": id,
            "context": kwargs.pop("when", kwargs.pop("context", {})),
            "call": call,
            **kwargs,
        }
        if "applies" in data and "applicability" not in data:
            data["applicability"] = data.pop("applies")
        return collector.add(BSLObject("call_spec", data))

    def Auction(pattern: str, seats: list[int] | tuple[int, ...] | None = None, seat_positions=None) -> dict[str, Any]:
        context = {"auction_pattern": pattern}
        active_seats = seats if seats is not None else seat_positions
        if active_seats is not None:
            context["seat_positions"] = list(active_seats)
        return context

    def Bid(call: str) -> str:
        return call

    def Meaning(
        *,
        action: str | None = None,
        action_type: str | None = None,
        target_suit: str | None = None,
        nature: list[str] | tuple[str, ...] = (),
        nature_labels: list[str] | tuple[str, ...] = (),
        acts: list[str] | tuple[str, ...] = (),
        call_act_types: list[str] | tuple[str, ...] = (),
        forcing: str | None = None,
        forcing_status: str | None = None,
        alertable: bool = False,
        acbl_explanation: str | None = None,
        **details: Any,
    ) -> CallMeaning:
        return CallMeaning(
            action_type=action_type or action,
            target_suit=target_suit,
            nature_labels=tuple(nature_labels or nature),
            call_act_types=tuple(call_act_types or acts),
            forcing_status=forcing_status or forcing,
            alertable=alertable,
            acbl_explanation=acbl_explanation,
            details=details,
        )

    def State(
        key: str,
        namespace: str = "public",
        owner: str | None = None,
        visibility: str = "partnership",
        **attributes: Any,
    ) -> StateEffect:
        return StateEffect(key=key, attributes=attributes, namespace=namespace, owner=owner, visibility=visibility)

    def StateUpdate(key: str, **attributes: Any) -> StateEffect:
        return State(key, **attributes)

    def Agreement(suit: str, source: str | None = None, **attributes: Any) -> StateEffect:
        if source is not None:
            attributes["source"] = source
        return State("agreed_suit", suit=suit, **attributes)

    def Force(status: str, **attributes: Any) -> StateEffect:
        return State("forcing_status", status=status, **attributes)

    def Control(suit: str, agreed_suit: str, round: str = "first_or_second", **attributes: Any) -> StateEffect:
        return State("control", suit=suit, agreed_suit=agreed_suit, round=round, status="shown", **attributes)

    def StepAfterState(key: str | None = None, **kwargs: Any) -> dict[str, Any]:
        query = dict(kwargs.pop("query", {"key": key}))
        query.update(kwargs.pop("match", {}))
        return {
            "relative_call": {
                "type": "step_after_state_call",
                "query": query,
                "attribute": kwargs.pop("attribute", "ask_call"),
                "step": kwargs.pop("step", 1),
            }
        }

    def StepAfterLastContract(step: int, **_: Any) -> dict[str, Any]:
        return {"relative_call": {"type": "step_after_last_contract", "step": step}}

    def Evaluator(id: str, function: Any | None = None, **kwargs: Any) -> dict[str, Any]:
        if function is None:
            function = kwargs.pop("function", None)
        if function is None and "definition" in kwargs:
            definition = kwargs.pop("definition")
            if callable(definition):
                function = definition
            else:
                raise BSLValidationError(
                    "Evaluator definition must be a Python function. "
                    "Write def my_evaluator(ctx, **params): ... and register it with Evaluator(id, function=my_evaluator)."
                )
        if function is None or not callable(function):
            raise BSLValidationError(f"Evaluator {id} requires function=<callable>")
        data = {"id": id, "evaluator_type": "python_function", "definition": function, **kwargs}
        return collector.add(BSLObject("evaluator_spec", data))

    def Frame(id: str, **kwargs: Any) -> dict[str, Any]:
        data = {
            "id": id,
            "frame_type": kwargs.pop("frame_type", kwargs.pop("type", None)),
            "context": kwargs.pop("when", kwargs.pop("context", {})),
            **kwargs,
        }
        return collector.add(BSLObject("frame_spec", data))

    def PrivateRoute(id: str, **kwargs: Any) -> dict[str, Any]:
        data = {"id": id, **kwargs}
        return collector.add(BSLObject("private_route_spec", data))

    def Relay(id: str, **kwargs: Any) -> dict[str, Any]:
        return collector.add(BSLObject("relay_spec", {"id": id, **kwargs}))

    def Workflow(start: str, *nodes: dict[str, Any]) -> dict[str, Any]:
        return {
            "start": start,
            "nodes": {
                node["id"]: {key: value for key, value in node.items() if key != "id"}
                for node in nodes
            },
        }

    def WaitForCall(id: str, *branches: dict[str, Any], actor: str | None = None) -> dict[str, Any]:
        data: dict[str, Any] = {"id": id, "kind": "wait_for_call", "branches": list(branches)}
        if actor is not None:
            data["actor"] = actor
        return data

    def MakeCall(
        id: str,
        call: str,
        *,
        requires: Any = None,
        meaning: Any = None,
        requires_call_specification: bool = False,
        capabilities: list[str] | tuple[str, ...] = (),
        goto: str | None = None,
    ) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": id,
            "kind": "make_call",
            "call": call,
            "requires_call_specification": requires_call_specification,
        }
        if requires is not None:
            data["requires"] = requires
        if meaning is not None:
            data["meaning"] = meaning
        if capabilities:
            data["capabilities"] = tuple(capabilities)
        if goto is not None:
            data["goto"] = goto
        return data

    def EndRoute(id: str) -> dict[str, Any]:
        return {"id": id, "kind": "end_route"}

    def OnCall(call: str, goto: str) -> dict[str, Any]:
        return {"when": {"kind": "call_is", "value": call}, "goto": goto}

    def named_evaluator(ctx: Any, evaluator_id: str, **params: Any) -> Any:
        definition = ctx.environment.get("_named_evaluators", {}).get(evaluator_id)
        if definition is None:
            raise ValueError(f"Unknown Named Evaluator: {evaluator_id}")
        if callable(definition):
            return definition(ctx, **params)
        return evaluate_expression(definition, ctx.hand, ctx.trace, ctx.environment, params)

    def eval_expr(ctx: Any, expression: Any, **params: Any) -> Any:
        return evaluate_expression(expression, ctx.hand, ctx.trace, ctx.environment, params)

    def Length(suit: str, hand: str = "self") -> dict[str, Any]:
        return {"op": "length", "hand": hand, "suit": suit}

    def Honors(suit: str, ranks: list[str] | tuple[str, ...] = ("A", "K", "Q"), hand: str = "self") -> dict[str, Any]:
        return {"op": "honor_count", "hand": hand, "suit": suit, "ranks": list(ranks)}

    def HasRank(suit: str, rank: str, hand: str = "self") -> dict[str, Any]:
        return {"op": "contains_rank", "hand": hand, "suit": suit, "rank": rank}

    def StateExists(key: str, **query: Any) -> dict[str, Any]:
        return {"expr": {"op": "state_exists", "query": {"key": key, **query}}}

    def StateAttribute(key: str, attribute: str, default: Any = None, **query: Any) -> dict[str, Any]:
        expression: dict[str, Any] = {
            "op": "state_attribute",
            "query": {"key": key, **query},
            "attribute": attribute,
        }
        if default is not None:
            expression["default"] = default
        return {"expr": expression}

    def state_attribute(ctx: Any, key: str, attribute: str, default: Any = None, **query: Any) -> Any:
        records = ctx.state.records_matching(key, **query)
        if not records:
            return default
        value = records[-1].attribute(attribute)
        return default if value is None else value

    def state_exists(ctx: Any, key: str, **attributes: Any) -> bool:
        return ctx.state.exists(key, **attributes)

    def state_missing(ctx: Any, key: str, **attributes: Any) -> bool:
        return not ctx.state.exists(key, **attributes)

    namespace: dict[str, Any] = {
        "__builtins__": {
            "__build_class__": __build_class__,
            "abs": abs,
            "all": all,
            "any": any,
            "bool": bool,
            "dict": dict,
            "float": float,
            "int": int,
            "len": len,
            "list": list,
            "max": max,
            "min": min,
            "range": range,
            "set": set,
            "sorted": sorted,
            "str": str,
            "sum": sum,
            "tuple": tuple,
        },
        "__name__": "partner_bsl",
        "Author": Author,
        "Profile": Profile,
        "Gadget": Gadget,
        "Call": Call,
        "Auction": Auction,
        "Bid": Bid,
        "Meaning": Meaning,
        "State": State,
        "StateUpdate": StateUpdate,
        "Update": StateUpdate,
        "Agreement": Agreement,
        "Force": Force,
        "Control": Control,
        "Evaluator": Evaluator,
        "Frame": Frame,
        "PrivateRoute": PrivateRoute,
        "Relay": Relay,
        "Workflow": Workflow,
        "WaitForCall": WaitForCall,
        "MakeCall": MakeCall,
        "EndRoute": EndRoute,
        "OnCall": OnCall,
        "StepAfterState": StepAfterState,
        "StepAfterLastContract": StepAfterLastContract,
        "named_evaluator": named_evaluator,
        "eval_expr": eval_expr,
        "Length": Length,
        "Honors": Honors,
        "HasRank": HasRank,
        "StateExists": StateExists,
        "StateAttribute": StateAttribute,
        "state_exists": state_exists,
        "state_missing": state_missing,
        "state_attribute": state_attribute,
        "S": "S",
        "H": "H",
        "D": "D",
        "C": "C",
        "N": "N",
    }
    return namespace
