from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SUIT_NAMES = {
    "S": "S",
    "H": "H",
    "D": "D",
    "C": "C",
    "N": "N",
}

SUIT_ATTRIBUTES = {
    "S": "S",
    "H": "H",
    "D": "D",
    "C": "C",
    "spades": "S",
    "hearts": "H",
    "diamonds": "D",
    "clubs": "C",
}

TOP_HONORS = {
    3: ["A", "K", "Q"],
    4: ["A", "K", "Q", "J"],
    5: ["A", "K", "Q", "J", "T"],
}


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
    symbols: dict[str, Any] = {}
    for path in paths:
        compiler = _Compiler(path, symbols)
        for item in compiler.compile():
            collector.add(item, path)
    return collector.to_module_data()


class _Collector:
    def __init__(self) -> None:
        self.profile: dict[str, Any] | None = None
        self.gadget_metadata: dict[str, Any] | None = None
        self.call_specs: list[dict[str, Any]] = []
        self.frame_specs: list[dict[str, Any]] = []
        self.private_route_specs: list[dict[str, Any]] = []
        self.evaluator_specs: list[dict[str, Any]] = []
        self.relay_specs: list[dict[str, Any]] = []

    def add(self, item: BSLObject, path: Path) -> None:
        if item.kind == "profile":
            if self.profile is not None:
                raise BSLValidationError(f"{path}: duplicate Profile object")
            self.profile = item.data
        elif item.kind == "gadget":
            if self.gadget_metadata is not None:
                raise BSLValidationError(f"{path}: duplicate Gadget object")
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
        else:  # pragma: no cover - guarded by constructor dispatch
            raise BSLValidationError(f"{path}: unsupported BSL object kind {item.kind}")

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


class _Compiler:
    def __init__(self, path: Path, symbols: dict[str, Any]) -> None:
        self.path = path
        self.symbols = symbols

    def compile(self) -> list[BSLObject]:
        source = self.path.read_text(encoding="utf-8").lstrip("\ufeff")
        tree = ast.parse(source, filename=str(self.path))
        output: list[BSLObject] = []
        for statement in tree.body:
            if isinstance(statement, ast.Expr):
                value = self._value(statement.value)
                if isinstance(value, BSLObject):
                    output.append(value)
                elif value is not None:
                    raise self._error(statement, "Top-level expression must be a BSL object")
                continue
            if isinstance(statement, ast.Assign):
                self._assign(statement)
                continue
            if isinstance(statement, ast.AnnAssign):
                self._ann_assign(statement)
                continue
            raise self._error(statement, f"Unsupported top-level syntax: {statement.__class__.__name__}")
        return output

    def _assign(self, statement: ast.Assign) -> None:
        if len(statement.targets) != 1 or not isinstance(statement.targets[0], ast.Name):
            raise self._error(statement, "Only simple name assignments are allowed")
        self.symbols[statement.targets[0].id] = self._value(statement.value)

    def _ann_assign(self, statement: ast.AnnAssign) -> None:
        if not isinstance(statement.target, ast.Name):
            raise self._error(statement, "Only simple annotated name assignments are allowed")
        self.symbols[statement.target.id] = self._value(statement.value)

    def _value(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.List):
            return [self._value(item) for item in node.elts]
        if isinstance(node, ast.Tuple):
            return tuple(self._value(item) for item in node.elts)
        if isinstance(node, ast.Dict):
            return {self._value(key): self._value(value) for key, value in zip(node.keys, node.values)}
        if isinstance(node, ast.Name):
            if node.id in self.symbols:
                return self.symbols[node.id]
            if node.id in SUIT_NAMES:
                return SUIT_NAMES[node.id]
            if node.id in {"True", "False", "None"}:
                return {"True": True, "False": False, "None": None}[node.id]
            raise self._error(node, f"Unknown name: {node.id}")
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            value = self._value(node.operand)
            if not isinstance(value, (int, float)):
                raise self._error(node, "Unary minus only supports numeric literals")
            return -value
        if isinstance(node, ast.Call):
            return self._constructor(node)
        if _is_expression_node(node):
            return {"expr": self._expr(node)}
        raise self._error(node, f"Unsupported value syntax: {node.__class__.__name__}")

    def _constructor(self, node: ast.Call) -> Any:
        name = _call_name(node.func)
        if name is None:
            raise self._error(node, "Only direct BSL constructor calls are allowed")
        if name in EXPRESSION_HELPERS:
            return self._expr(node)
        if name not in CONSTRUCTORS:
            raise self._error(node, f"Unsupported BSL constructor: {name}")
        return getattr(self, f"_build_{CONSTRUCTORS[name]}")(node)

    def _build_author(self, node: ast.Call) -> dict[str, Any]:
        kwargs = self._kwargs(node)
        name = self._arg(node, 0, "name", kwargs)
        return {
            "name": name,
            "contact": kwargs.get("contact"),
            "organization": kwargs.get("organization"),
        }

    def _build_profile(self, node: ast.Call) -> BSLObject:
        kwargs = self._kwargs(node)
        data = {
            "id": self._arg(node, 0, "id", kwargs),
            "name": kwargs.get("name", self._arg(node, 0, "id", kwargs)),
            "version": kwargs.get("version", "0.1.0"),
            "author": kwargs.get("author", {"name": "Unknown"}),
            "gadgets": kwargs.get("gadgets", []),
        }
        _copy_optional(kwargs, data, "description")
        _copy_optional(kwargs, data, "system_notes")
        return BSLObject("profile", data)

    def _build_gadget(self, node: ast.Call) -> BSLObject:
        kwargs = self._kwargs(node)
        gadget_id = self._arg(node, 0, "id", kwargs)
        data = {
            "id": gadget_id,
            "namespace": kwargs.get("namespace", gadget_id),
            "name": kwargs.get("name", gadget_id),
            "version": kwargs.get("version", "0.1.0"),
            "author": kwargs.get("author", {"name": "Unknown"}),
        }
        _copy_optional(kwargs, data, "description")
        _copy_optional(kwargs, data, "system_notes")
        return BSLObject("gadget", data)

    def _build_call(self, node: ast.Call) -> BSLObject:
        kwargs = self._kwargs(node)
        data = {
            "id": self._arg(node, 0, "id", kwargs),
            "context": kwargs.get("when", kwargs.get("context", {})),
            "call": kwargs.get("bid", kwargs.get("call")),
        }
        if data["call"] is None:
            raise self._error(node, "Call requires bid=Bid(...) or call=...")
        for source, target in (
            ("requires", "requires"),
            ("applies", "applicability"),
            ("applicability", "applicability"),
            ("selection", "selection"),
            ("meaning", "meaning"),
            ("capabilities", "capabilities"),
            ("effects", "effects"),
            ("default_policy", "default_policy"),
            ("description", "description"),
            ("system_notes", "system_notes"),
            ("author", "author"),
        ):
            if source in kwargs:
                data[target] = _condition_or_value(kwargs[source]) if source in {"requires", "applies", "applicability"} else kwargs[source]
        return BSLObject("call_spec", data)

    def _build_auction(self, node: ast.Call) -> dict[str, Any]:
        kwargs = self._kwargs(node)
        pattern = self._arg(node, 0, "pattern", kwargs)
        context = {"auction_pattern": pattern}
        seats = kwargs.get("seats", kwargs.get("seat_positions"))
        if seats is not None:
            context["seat_positions"] = list(seats)
        return context

    def _build_bid(self, node: ast.Call) -> str:
        return self._arg(node, 0, "call", self._kwargs(node))

    def _build_meaning(self, node: ast.Call) -> dict[str, Any]:
        kwargs = self._kwargs(node)
        meaning: dict[str, Any] = {}
        if "nature" in kwargs:
            meaning["nature_labels"] = kwargs.pop("nature")
        if "nature_labels" in kwargs:
            meaning["nature_labels"] = kwargs.pop("nature_labels")
        if "acts" in kwargs:
            meaning["call_act_types"] = kwargs.pop("acts")
        if "call_act_types" in kwargs:
            meaning["call_act_types"] = kwargs.pop("call_act_types")
        if "action" in kwargs:
            meaning["action_type"] = kwargs.pop("action")
        if "action_type" in kwargs:
            meaning["action_type"] = kwargs.pop("action_type")
        meaning.update(kwargs)
        return meaning

    def _build_state(self, node: ast.Call) -> dict[str, Any]:
        kwargs = self._kwargs(node)
        state = {
            "key": self._arg(node, 0, "key", kwargs),
            "namespace": kwargs.pop("namespace", "public"),
        }
        if "owner" in kwargs:
            state["owner"] = kwargs.pop("owner")
        state.update(kwargs)
        return {"state": state}

    def _build_update(self, node: ast.Call) -> dict[str, Any]:
        kwargs = self._kwargs(node)
        record = {"key": self._arg(node, 0, "key", kwargs)}
        record.update(kwargs)
        return {"state": record}

    def _build_selection(self, node: ast.Call) -> dict[str, Any]:
        kwargs = self._kwargs(node)
        data = {
            "algorithm": kwargs.get("algorithm", "weighted_score"),
            "criteria": kwargs.get("criteria", []),
        }
        if "applicability" in kwargs:
            data["applicability"] = _condition_or_value(kwargs["applicability"])
        return data

    def _build_criterion(self, node: ast.Call) -> dict[str, Any]:
        kwargs = self._kwargs(node, skip_positionals=True)
        criterion_id = self._positional_value(node, 0)
        condition = self._positional_expr(node, 1) if len(node.args) > 1 else kwargs.pop("condition", kwargs.pop("expr", None))
        data = {
            "criterion_id": criterion_id,
            "weight": kwargs.pop("weight", 0),
            "required": kwargs.pop("required", True),
        }
        if condition is not None:
            data["evaluator"] = "expression"
            data["expr"] = _expression_or_value(condition)
        else:
            data["evaluator"] = kwargs.pop("evaluator")
            data.update(kwargs)
        return data

    def _build_evaluator(self, node: ast.Call) -> BSLObject:
        kwargs = self._kwargs(node)
        data = {
            "id": self._arg(node, 0, "id", kwargs),
            "evaluator_type": kwargs.get("evaluator_type", "expression"),
            "definition": _expression_or_value(kwargs.get("definition", kwargs.get("returns", {}))),
        }
        for key in ("description", "system_notes", "author"):
            _copy_optional(kwargs, data, key)
        return BSLObject("evaluator_spec", data)

    def _build_frame(self, node: ast.Call) -> BSLObject:
        kwargs = self._kwargs(node)
        data = {
            "id": self._arg(node, 0, "id", kwargs),
            "frame_type": kwargs.get("frame_type", kwargs.get("type")),
            "context": kwargs.get("when", kwargs.get("context", {})),
        }
        for key in (
            "source_call",
            "description",
            "system_notes",
            "variables",
            "obligation",
            "stages",
            "allowed_continuations",
            "break_conditions",
            "closes",
            "close_on_actions",
            "close_on_act_types",
            "author",
        ):
            _copy_optional(kwargs, data, key)
        return BSLObject("frame_spec", data)

    def _build_private_route(self, node: ast.Call) -> BSLObject:
        kwargs = self._kwargs(node)
        data = {"id": self._arg(node, 0, "id", kwargs)}
        for key in (
            "owner",
            "goal",
            "context",
            "when",
            "preconditions",
            "entry_call",
            "workflow",
            "capabilities",
            "selection",
            "entry_candidate",
            "entry_score",
            "description",
            "system_notes",
            "author",
        ):
            if key in kwargs:
                data["context" if key == "when" else key] = kwargs[key]
        return BSLObject("private_route_spec", data)

    def _build_step_after_state(self, node: ast.Call) -> dict[str, Any]:
        kwargs = self._kwargs(node)
        query = dict(kwargs.get("query", {"key": self._positional_value(node, 0)}))
        for key, value in kwargs.items():
            if key not in {"query", "attribute", "step"}:
                query[key] = value
        return {
            "relative_call": {
                "type": "step_after_state_call",
                "query": query,
                "attribute": kwargs.get("attribute", "ask_call"),
                "step": kwargs.get("step", 1),
            }
        }

    def _build_step_after_last_contract(self, node: ast.Call) -> dict[str, Any]:
        kwargs = self._kwargs(node)
        return {
            "relative_call": {
                "type": "step_after_last_contract",
                "step": self._arg(node, 0, "step", kwargs),
            }
        }

    def _build_relay(self, node: ast.Call) -> BSLObject:
        kwargs = self._kwargs(node)
        data = {"id": self._arg(node, 0, "id", kwargs)}
        data.update(kwargs)
        return BSLObject("relay_spec", data)

    def _kwargs(self, node: ast.Call, skip_positionals: bool = False) -> dict[str, Any]:
        for keyword in node.keywords:
            if keyword.arg is None:
                raise self._error(keyword, "Star keyword expansion is not allowed")
        if skip_positionals:
            return {keyword.arg: self._value(keyword.value) for keyword in node.keywords}
        return {keyword.arg: self._value(keyword.value) for keyword in node.keywords}

    def _arg(self, node: ast.Call, index: int, key: str, kwargs: dict[str, Any]) -> Any:
        if key in kwargs:
            return kwargs[key]
        return self._positional_value(node, index)

    def _positional_value(self, node: ast.Call, index: int) -> Any:
        if len(node.args) <= index:
            raise self._error(node, f"Missing positional argument {index + 1}")
        return self._value(node.args[index])

    def _positional_expr(self, node: ast.Call, index: int) -> Any:
        if len(node.args) <= index:
            raise self._error(node, f"Missing expression argument {index + 1}")
        return self._expr(node.args[index])

    def _expr(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            return {"const": node.value}
        if isinstance(node, ast.Name):
            if node.id in SUIT_NAMES:
                return {"const": SUIT_NAMES[node.id]}
            raise self._error(node, f"Unknown expression name: {node.id}")
        if isinstance(node, ast.Attribute):
            return self._attribute_expr(node)
        if isinstance(node, ast.BoolOp):
            op = "and" if isinstance(node.op, ast.And) else "or"
            return {"op": op, "args": [self._expr(item) for item in node.values]}
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return {"op": "not", "arg": self._expr(node.operand)}
        if isinstance(node, ast.Compare):
            return self._compare_expr(node)
        if isinstance(node, ast.BinOp):
            return self._binop_expr(node)
        if isinstance(node, ast.Call):
            return self._expression_helper(node)
        raise self._error(node, f"Unsupported expression syntax: {node.__class__.__name__}")

    def _attribute_expr(self, node: ast.Attribute) -> dict[str, Any]:
        if isinstance(node.value, ast.Name):
            root = node.value.id
            attr = node.attr
            if root == "self":
                if attr in {"hcp", "balanced"}:
                    return {"var": f"self.{attr}"}
                if attr in SUIT_ATTRIBUTES:
                    return {"op": "length", "hand": "self", "suit": SUIT_ATTRIBUTES[attr]}
            if root == "partner":
                if attr == "hcp":
                    return {"var": "partner.hcp"}
                if attr in SUIT_ATTRIBUTES:
                    return {"op": "length", "hand": "partner", "suit": SUIT_ATTRIBUTES[attr]}
            if root == "env":
                return {"var": f"env.{attr}"}
        raise self._error(node, "Unsupported attribute expression")

    def _compare_expr(self, node: ast.Compare) -> dict[str, Any]:
        expressions = []
        left = node.left
        for op_node, right in zip(node.ops, node.comparators):
            expressions.append(
                {
                    "op": _compare_operator(op_node, self.path, node),
                    "left": self._expr(left),
                    "right": self._expr(right),
                }
            )
            left = right
        if len(expressions) == 1:
            return expressions[0]
        return {"op": "and", "args": expressions}

    def _binop_expr(self, node: ast.BinOp) -> dict[str, Any]:
        op = _binop_operator(node.op, self.path, node)
        return {"op": op, "args": [self._expr(node.left), self._expr(node.right)]}

    def _expression_helper(self, node: ast.Call) -> dict[str, Any]:
        name = _call_name(node.func)
        kwargs = self._kwargs(node)
        if name == "Length":
            return {"op": "length", "hand": kwargs.get("hand", "self"), "suit": self._positional_value(node, 0)}
        if name == "Honors":
            top = kwargs.get("top")
            ranks = kwargs.get("ranks", TOP_HONORS.get(top, ["A", "K", "Q", "J"]))
            return {"op": "honor_count", "hand": kwargs.get("hand", "self"), "suit": self._positional_value(node, 0), "ranks": ranks}
        if name == "HasRank":
            return {"op": "contains_rank", "hand": kwargs.get("hand", "self"), "suit": self._positional_value(node, 0), "rank": self._positional_value(node, 1)}
        if name == "StateExists":
            query = dict(kwargs.get("query", {"key": self._positional_value(node, 0)}))
            query.update({key: value for key, value in kwargs.items() if key != "query"})
            return {"op": "state_exists", "query": query}
        raise self._error(node, f"Unsupported expression helper: {name}")

    def _error(self, node: ast.AST, message: str) -> BSLValidationError:
        location = f"{self.path}:{getattr(node, 'lineno', '?')}:{getattr(node, 'col_offset', '?')}"
        return BSLValidationError(f"{location}: {message}")


CONSTRUCTORS = {
    "Author": "author",
    "Profile": "profile",
    "Gadget": "gadget",
    "Call": "call",
    "Auction": "auction",
    "Bid": "bid",
    "Meaning": "meaning",
    "State": "state",
    "Update": "update",
    "Selection": "selection",
    "Criterion": "criterion",
    "Evaluator": "evaluator",
    "Frame": "frame",
    "PrivateRoute": "private_route",
    "StepAfterState": "step_after_state",
    "StepAfterLastContract": "step_after_last_contract",
    "Relay": "relay",
}

EXPRESSION_HELPERS = {"Length", "Honors", "HasRank", "StateExists"}


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    return None


def _is_expression_node(node: ast.AST) -> bool:
    return isinstance(node, (ast.BoolOp, ast.UnaryOp, ast.Compare, ast.BinOp, ast.Attribute))


def _condition_or_value(value: Any) -> Any:
    if isinstance(value, dict) and "expr" in value:
        return value
    if isinstance(value, dict) and "op" in value:
        return {"expr": value}
    return value


def _expression_or_value(value: Any) -> Any:
    if isinstance(value, dict) and "expr" in value:
        return value["expr"]
    return value


def _copy_optional(source: dict[str, Any], target: dict[str, Any], key: str) -> None:
    if key in source:
        target[key] = source[key]


def _compare_operator(node: ast.cmpop, path: Path, source: ast.AST) -> str:
    if isinstance(node, ast.Eq):
        return "eq"
    if isinstance(node, ast.NotEq):
        return "neq"
    if isinstance(node, ast.Lt):
        return "lt"
    if isinstance(node, ast.LtE):
        return "lte"
    if isinstance(node, ast.Gt):
        return "gt"
    if isinstance(node, ast.GtE):
        return "gte"
    if isinstance(node, ast.In):
        return "in"
    raise BSLValidationError(f"{path}:{getattr(source, 'lineno', '?')}:{getattr(source, 'col_offset', '?')}: unsupported comparison operator")


def _binop_operator(node: ast.operator, path: Path, source: ast.AST) -> str:
    if isinstance(node, ast.Add):
        return "add"
    if isinstance(node, ast.Sub):
        return "sub"
    if isinstance(node, ast.Mult):
        return "mul"
    if isinstance(node, ast.Div):
        return "div"
    raise BSLValidationError(f"{path}:{getattr(source, 'lineno', '?')}:{getattr(source, 'col_offset', '?')}: unsupported arithmetic operator")
