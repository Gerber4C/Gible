from __future__ import annotations

from typing import Any

from .cards import Hand
from .trace import SemanticTrace


def evaluate(condition: dict[str, Any], hand: Hand, trace: SemanticTrace, environment: dict[str, Any] | None = None) -> bool:
    if not condition:
        return True

    environment = environment or {}

    if "all" in condition:
        return all(evaluate(item, hand, trace, environment) for item in condition["all"])

    if "any" in condition:
        return any(evaluate(item, hand, trace, environment) for item in condition["any"])

    if "not" in condition:
        return not evaluate(condition["not"], hand, trace, environment)

    if "fact_exists" in condition:
        return trace.fact_exists(condition["fact_exists"])

    if "state_has" in condition:
        return trace.state_has(condition["state_has"])

    if "state_missing" in condition:
        return not trace.state_has(condition["state_missing"])

    if "auction_state_exists" in condition:
        return trace.auction_state_exists(condition["auction_state_exists"])

    if "auction_state_missing" in condition:
        return not trace.auction_state_exists(condition["auction_state_missing"])

    if "auction_state_compare" in condition:
        return trace.auction_state_compare(condition["auction_state_compare"])

    if "expr" in condition:
        return bool(evaluate_expression(condition["expr"], hand, trace, environment))

    for key, expected in condition.items():
        actual = _resolve_value(key, hand, trace, environment)
        if not _compare(actual, expected):
            return False
    return True


def _resolve_value(key: str, hand: Hand, trace: SemanticTrace, environment: dict[str, Any]) -> Any:
    if key == "self.hcp":
        return hand.hcp
    if key == "self.balanced":
        return hand.balanced
    if key.startswith("self."):
        suit = key.removeprefix("self.")
        return hand.length(suit)
    if key.startswith("env."):
        return environment.get(key.removeprefix("env."))
    raise ValueError(f"Unsupported condition key: {key}")


def _compare(actual: Any, expected: Any) -> bool:
    if isinstance(expected, dict):
        if "min" in expected and expected["min"] is not None and actual < expected["min"]:
            return False
        if "max" in expected and expected["max"] is not None and actual > expected["max"]:
            return False
        if "eq" in expected and actual != expected["eq"]:
            return False
        if "in" in expected and actual not in expected["in"]:
            return False
        return True
    return actual == expected


def evaluate_selection(selection: dict[str, Any], hand: Hand, trace: SemanticTrace, environment: dict[str, Any] | None = None) -> dict[str, Any]:
    environment = environment or {}
    algorithm = selection.get("algorithm", "weighted_score")
    if algorithm != "weighted_score":
        raise ValueError(f"Unsupported selection algorithm: {algorithm}")

    score = 0
    eligible = True
    criteria_results = []
    for criterion in selection.get("criteria", []):
        result = evaluate_criterion(criterion, hand, trace, environment)
        if criterion.get("required", True) and not result["passed"]:
            eligible = False
        if result["passed"]:
            score += result["contribution"]
        criteria_results.append(result)

    return {
        "algorithm": algorithm,
        "eligible": eligible,
        "score": score,
        "criteria_results": criteria_results,
    }


def evaluate_criterion(criterion: dict[str, Any], hand: Hand, trace: SemanticTrace, environment: dict[str, Any]) -> dict[str, Any]:
    evaluator = criterion["evaluator"]
    value = None
    passed = False

    if evaluator == "range_contains":
        value = _resolve_value(criterion["input"], hand, trace, environment)
        passed = _compare(value, {"min": criterion.get("min"), "max": criterion.get("max")})
    elif evaluator == "min_value":
        value = _resolve_value(criterion["input"], hand, trace, environment)
        passed = value >= criterion["min"]
    elif evaluator == "equals":
        value = _resolve_value(criterion["input"], hand, trace, environment)
        passed = value == criterion["value"]
    elif evaluator == "fact_exists":
        value = criterion["query"]
        passed = trace.fact_exists(criterion["query"])
    elif evaluator == "expression":
        value = evaluate_expression(criterion["expr"], hand, trace, environment, criterion.get("params", {}))
        passed = bool(value)
    elif evaluator == "named_evaluator":
        evaluator_id = criterion["evaluator_id"]
        definition = environment.get("_named_evaluators", {}).get(evaluator_id)
        if definition is None:
            raise ValueError(f"Unknown Named Evaluator: {evaluator_id}")
        value = evaluate_expression(definition, hand, trace, environment, criterion.get("params", {}))
        passed = bool(value)
    else:
        raise ValueError(f"Unsupported criterion evaluator: {evaluator}")

    return {
        "criterion_id": criterion["criterion_id"],
        "evaluator": evaluator,
        "passed": passed,
        "required": criterion.get("required", True),
        "value": value,
        "contribution": int(criterion.get("weight", 0)) if passed else 0,
    }


def evaluate_expression(
    expr: Any,
    hand: Hand,
    trace: SemanticTrace,
    environment: dict[str, Any],
    params: dict[str, Any] | None = None,
) -> Any:
    params = params or {}
    if not isinstance(expr, dict):
        return expr
    if "const" in expr:
        return expr["const"]
    if "var" in expr:
        return _resolve_expr_var(expr["var"], hand, environment)
    if "param" in expr:
        return params[expr["param"]]

    op = expr.get("op")
    if op == "and":
        return all(bool(evaluate_expression(item, hand, trace, environment, params)) for item in expr.get("args", []))
    if op == "or":
        return any(bool(evaluate_expression(item, hand, trace, environment, params)) for item in expr.get("args", []))
    if op == "not":
        return not bool(evaluate_expression(expr["arg"], hand, trace, environment, params))
    if op in {"eq", "neq", "lt", "lte", "gt", "gte", "in"}:
        left = evaluate_expression(expr["left"], hand, trace, environment, params)
        right = evaluate_expression(expr["right"], hand, trace, environment, params)
        return _expression_compare(op, left, right)
    if op in {"add", "sub", "mul", "div", "min", "max"}:
        values = [evaluate_expression(item, hand, trace, environment, params) for item in expr.get("args", [])]
        return _expression_arithmetic(op, values)
    if op == "abs":
        return abs(evaluate_expression(expr["arg"], hand, trace, environment, params))
    if op == "if":
        branch = "then" if evaluate_expression(expr["condition"], hand, trace, environment, params) else "else"
        return evaluate_expression(expr[branch], hand, trace, environment, params)
    if op == "length":
        return _expression_hand(expr, hand, environment).length(_expression_suit(expr.get("suit"), hand, trace, environment, params))
    if op == "honor_count":
        return _expression_hand(expr, hand, environment).honor_count(
            _expression_suit(expr.get("suit"), hand, trace, environment, params),
            expr.get("ranks", ["A", "K", "Q", "J"]),
        )
    if op == "contains_rank":
        return _expression_hand(expr, hand, environment).contains_rank(
            _expression_suit(expr.get("suit"), hand, trace, environment, params),
            expr["rank"],
        )
    if op == "keycard_count":
        return _expression_hand(expr, hand, environment).keycard_count(
            _expression_suit(expr.get("trump_suit"), hand, trace, environment, params),
            excluded_suit=_expression_optional_suit(expr.get("excluded_suit"), hand, trace, environment, params),
        )
    if op == "ace_count":
        return _expression_hand(expr, hand, environment).ace_count(
            excluded_suit=_expression_optional_suit(expr.get("excluded_suit"), hand, trace, environment, params)
        )
    if op == "king_count":
        return _expression_hand(expr, hand, environment).king_count(
            excluded_suit=_expression_optional_suit(expr.get("excluded_suit"), hand, trace, environment, params)
        )
    if op == "fact_exists":
        return trace.fact_exists(expr["query"])
    if op == "state_has":
        return trace.state_has(expr["query"])
    if op == "state_missing":
        return not trace.state_has(expr["query"])
    if op == "fact_attribute":
        return _expression_fact_attribute(expr, trace)
    if op == "auction_state_exists":
        return trace.auction_state_exists(expr["query"])
    if op == "auction_state_missing":
        return not trace.auction_state_exists(expr["query"])
    if op == "auction_state_compare":
        return trace.auction_state_compare(expr)
    if op == "auction_state_attribute":
        return _expression_auction_state_attribute(expr, trace)
    raise ValueError(f"Unsupported expression operator: {op}")


def _resolve_expr_var(path: str, hand: Hand, environment: dict[str, Any]) -> Any:
    if path == "self.hcp":
        return hand.hcp
    if path == "self.balanced":
        return hand.balanced
    if path.startswith("self.") and path.endswith(".length"):
        return hand.length(path.split(".")[1])
    if path == "partner.hcp":
        return _partner_hand(environment).hcp
    if path.startswith("partner.") and path.endswith(".length"):
        return _partner_hand(environment).length(path.split(".")[1])
    if path.startswith("env."):
        return environment.get(path.removeprefix("env."))
    raise ValueError(f"Unsupported expression variable: {path}")


def _expression_compare(op: str, left: Any, right: Any) -> bool:
    if op == "eq":
        return left == right
    if op == "neq":
        return left != right
    if op == "lt":
        return left < right
    if op == "lte":
        return left <= right
    if op == "gt":
        return left > right
    if op == "gte":
        return left >= right
    if op == "in":
        return left in right
    raise ValueError(f"Unsupported expression comparison: {op}")


def _expression_arithmetic(op: str, values: list[Any]) -> Any:
    if op == "add":
        return sum(values)
    if op == "sub":
        if not values:
            raise ValueError("sub expression requires at least one value")
        result = values[0]
        for value in values[1:]:
            result -= value
        return result
    if op == "mul":
        result = 1
        for value in values:
            result *= value
        return result
    if op == "div":
        if len(values) != 2:
            raise ValueError("div expression requires exactly two values")
        return values[0] / values[1]
    if op == "min":
        return min(values)
    if op == "max":
        return max(values)
    raise ValueError(f"Unsupported expression arithmetic: {op}")


def _expression_hand(expr: dict[str, Any], hand: Hand, environment: dict[str, Any]) -> Hand:
    hand_name = expr.get("hand", "self")
    if hand_name == "self":
        return hand
    if hand_name == "partner":
        return _partner_hand(environment)
    raise ValueError(f"Unsupported expression hand: {hand_name}")


def _partner_hand(environment: dict[str, Any]) -> Hand:
    partner = environment.get("partner_hand")
    if isinstance(partner, Hand):
        return partner
    if isinstance(partner, str):
        return Hand.parse(partner)
    raise ValueError("Expression requires partner_hand in environment")


def _expression_suit(value: Any, hand: Hand, trace: SemanticTrace, environment: dict[str, Any], params: dict[str, Any]) -> Any:
    if isinstance(value, dict):
        return evaluate_expression(value, hand, trace, environment, params)
    return value


def _expression_optional_suit(
    value: Any,
    hand: Hand,
    trace: SemanticTrace,
    environment: dict[str, Any],
    params: dict[str, Any],
) -> Any:
    if value is None:
        return None
    return _expression_suit(value, hand, trace, environment, params)


def _expression_fact_attribute(expr: dict[str, Any], trace: SemanticTrace) -> Any:
    matches = trace.matching_facts(expr["query"])
    if not matches:
        if "default" in expr:
            return expr["default"]
        raise ValueError(f"No semantic fact matches query: {expr['query']}")
    fact = matches[-1] if expr.get("which", "last") == "last" else matches[0]
    attribute = expr["attribute"]
    if attribute == "fact_type":
        return fact.fact_type
    if attribute not in fact.attributes:
        if "default" in expr:
            return expr["default"]
        raise ValueError(f"Semantic fact lacks attribute {attribute}: {fact.to_dict()}")
    return fact.attributes[attribute]


def _expression_auction_state_attribute(expr: dict[str, Any], trace: SemanticTrace) -> Any:
    matches = trace.matching_auction_state(expr["query"])
    if not matches:
        if "default" in expr:
            return expr["default"]
        raise ValueError(f"No auction-state variable matches query: {expr['query']}")
    variable = matches[-1] if expr.get("which", "last") == "last" else matches[0]
    attribute = expr["attribute"]
    value = variable.attribute(attribute)
    if value is None and "default" in expr:
        return expr["default"]
    return value
