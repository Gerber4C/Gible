from __future__ import annotations

from typing import Any

from .cards import Hand
from .evaluator import evaluate_expression
from .trace import AuctionTrace, StateRecord


def apply_effect(
    trace: AuctionTrace,
    effect: dict[str, Any],
    origin: dict[str, Any],
    hand: Hand | None,
    environment: dict[str, Any],
) -> None:
    materialized = _materialize_effect(effect, hand, trace, environment)
    if "state" in materialized:
        trace.add_state(StateRecord.from_dict(materialized["state"], origin))
        return
    if "state_update" in materialized:
        trace.add_state(StateRecord.from_dict(materialized["state_update"], origin))
        return
    if "key" in materialized:
        trace.add_state(StateRecord.from_dict(materialized, origin))
        return
    trace.warn(f"Effect from {origin.get('qualified_id')} did not contain a state key: {materialized}")


def _materialize_effect(
    effect: dict[str, Any],
    hand: Hand | None,
    trace: AuctionTrace,
    environment: dict[str, Any],
) -> dict[str, Any]:
    active_hand = hand or Hand.from_dict({})
    return {key: _materialize_value(value, active_hand, trace, environment) for key, value in effect.items()}


def _materialize_value(value: Any, hand: Hand, trace: AuctionTrace, environment: dict[str, Any]) -> Any:
    if isinstance(value, dict) and "expr" in value:
        return evaluate_expression(value["expr"], hand, trace, environment)
    if isinstance(value, list):
        return [_materialize_value(item, hand, trace, environment) for item in value]
    if isinstance(value, dict):
        return {key: _materialize_value(item, hand, trace, environment) for key, item in value.items()}
    return value
