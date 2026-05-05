from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .convention import Author, Convention, ConventionSet


try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


def load_convention_set(convention_set_id: str, base_dir: Path | None = None) -> ConventionSet:
    base_dir = base_dir or Path(__file__).resolve().parents[1]
    convention_set_path = base_dir / "convention_sets" / f"{convention_set_id}.yaml"
    data = _read_yaml(convention_set_path)
    conventions = tuple(
        _load_convention(base_dir / "conventions" / Path(*convention_id.split(".")))
        for convention_id in data.get("conventions", [])
    )
    return ConventionSet(
        id=data["id"],
        name=data.get("name", data["id"]),
        version=data.get("version", "0.1.0"),
        author=Author.from_dict(data.get("author")),
        conventions=conventions,
        description=data.get("description"),
        system_notes=data.get("system_notes"),
    )


def _load_convention(convention_path: Path) -> Convention:
    metadata = _read_yaml(convention_path / "convention.yaml")
    call_specification_data: list[dict[str, Any]] = []
    protocol_frame_data: list[dict[str, Any]] = []
    bidding_plan_data: list[dict[str, Any]] = []
    call_selection_policy_data: list[dict[str, Any]] = []
    named_evaluator_data: list[dict[str, Any]] = []
    relay_automaton_data: list[dict[str, Any]] = []
    for path in sorted(convention_path.glob("*.yaml")):
        if path.name == "convention.yaml":
            continue
        content = _read_yaml(path)
        call_specification_data.extend(content.get("call_specifications", []) or [])
        protocol_frame_data.extend(content.get("protocol_frames", []) or [])
        bidding_plan_data.extend(content.get("bidding_plans", []) or [])
        call_selection_policy_data.extend(content.get("call_selection_policies", []) or [])
        named_evaluator_data.extend(content.get("named_evaluators", []) or [])
        relay_automaton_data.extend(content.get("relay_automata", []) or [])
    return Convention.from_parts(
        metadata,
        call_specification_data,
        protocol_frame_data=protocol_frame_data,
        bidding_plan_data=bidding_plan_data,
        call_selection_policy_data=call_selection_policy_data,
        named_evaluator_data=named_evaluator_data,
        relay_automaton_data=relay_automaton_data,
    )


def _read_yaml(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if yaml is None:
        return json.loads(text)
    return yaml.safe_load(text) or {}
