from __future__ import annotations

from pathlib import Path
from typing import Any

from .model import CallSpec, Gadget, PartnershipProfile, PrivateRouteSpec


def generate_system_notes(profile: PartnershipProfile) -> str:
    lines: list[str] = [
        f"# {profile.name}",
        "",
        f"Profile ID: `{profile.id}`",
        f"Version: `{profile.version}`",
        f"Author: {profile.author.name}",
    ]
    if profile.description:
        lines.extend(["", profile.description.strip()])
    if profile.system_notes:
        lines.extend(["", profile.system_notes.strip()])

    for gadget in profile.gadgets:
        _render_gadget(lines, gadget)

    if profile.policy_functions:
        lines.extend(["", "## Profile Policy Functions"])
        for policy_function in profile.policy_functions:
            source = Path(policy_function.source_path).name if policy_function.source_path else "unknown"
            lines.extend(["", f"- `{policy_function.id}`", "  - Algorithm: `python_bsl_function`", f"  - Source: `{source}`"])

    lines.append("")
    return "\n".join(lines)


def _render_gadget(lines: list[str], gadget: Gadget) -> None:
    lines.extend(
        [
            "",
            f"## {gadget.name}",
            "",
            f"Gadget ID: `{gadget.id}`",
            f"Namespace: `{gadget.namespace}`",
            f"Version: `{gadget.version}`",
            f"Author: {gadget.author.name}",
        ]
    )
    if gadget.description:
        lines.extend(["", gadget.description.strip()])
    if gadget.system_notes:
        lines.extend(["", gadget.system_notes.strip()])

    if gadget.call_specs:
        lines.extend(["", "### Call Specifications"])
        for item in gadget.call_specs:
            _render_call_specification(lines, item)

    if gadget.frame_specs:
        lines.extend(["", "### Frames"])
        for frame in gadget.frame_specs:
            lines.extend(
                [
                    "",
                    f"- `{frame.id}`: `{frame.frame_type}`",
                    f"  - Context: {_format_context(frame.context)}",
                    f"  - Source call: `{frame.source_call}`",
                    f"  - Variables: {_format_mapping(frame.variables)}",
                    f"  - Obligation: {_format_mapping(frame.obligation)}",
                    f"  - Closes: {_format_list(frame.closes)}",
                    f"  - Close on actions: {_format_list(frame.close_on_actions)}",
                    f"  - Close on act types: {_format_list(frame.close_on_act_types)}",
                ]
            )
            if frame.description:
                lines.append(f"  - Notes: {frame.description.strip()}")

    if gadget.private_route_specs:
        lines.extend(["", "### Private Routes"])
        for route in gadget.private_route_specs:
            _render_private_route(lines, route)

    if gadget.policy_functions:
        lines.extend(["", "### Policy Functions"])
        for policy_function in gadget.policy_functions:
            source = Path(policy_function.source_path).name if policy_function.source_path else "unknown"
            lines.extend(
                [
                    "",
                    f"- `{policy_function.id}`",
                    "  - Algorithm: `python_bsl_function`",
                    f"  - Source: `{source}`",
                ]
            )

    if gadget.evaluator_specs:
        lines.extend(["", "### Named Evaluators"])
        for evaluator in gadget.evaluator_specs:
            lines.extend(
                [
                    "",
                    f"- `{evaluator.id}`",
                    f"  - Evaluator type: `{evaluator.evaluator_type}`",
                    f"  - Definition: {_format_mapping(evaluator.definition)}",
                ]
            )
            if evaluator.description:
                lines.append(f"  - Notes: {evaluator.description.strip()}")
            if evaluator.system_notes:
                lines.append(f"  - System Notes: {evaluator.system_notes.strip()}")


def _render_call_specification(lines: list[str], item: CallSpec) -> None:
    lines.extend(
        [
            "",
            f"- `{item.id}`",
            f"  - Context: {_format_context(item.context)}",
            f"  - Call: `{_format_call(item)}`",
            f"  - Call Act Types: {_format_list(item.call_act_types)}",
            f"  - Capabilities: {_format_list(item.capabilities)}",
            f"  - Requires: {_format_mapping(item.requires)}",
            f"  - Meaning: {_format_mapping(item.meaning.to_dict())}",
            f"  - Applicability: {_format_mapping(item.applicability)}",
            f"  - Effects: {_format_list(item.effects)}",
        ]
    )
    if item.description:
        lines.append(f"  - Notes: {item.description.strip()}")
    if item.system_notes:
        lines.append(f"  - System Notes: {item.system_notes.strip()}")


def _render_private_route(lines: list[str], route: PrivateRouteSpec) -> None:
    lines.extend(
        [
            "",
            f"- `{route.id}`",
            f"  - Owner: `{route.owner}`",
            f"  - Goal: `{route.goal}`",
            f"  - Context: {_format_context(route.context)}",
            f"  - Entry call: `{route.entry_call}`",
            f"  - Entry candidate: `{str(route.entry_candidate).lower()}`",
            f"  - Entry score: `{route.entry_score}`",
            f"  - Capabilities: {_format_list(route.capabilities)}",
            f"  - Preconditions: {_format_mapping(route.preconditions)}",
            f"  - Workflow start: `{route.start_node}`",
            "  - Workflow nodes:",
        ]
    )
    for node_id, node in route.workflow.get("nodes", {}).items():
        lines.append(f"    - `{node_id}`: `{node.get('kind')}`")
        if "actor" in node:
            lines.append(f"      - Actor: `{node['actor']}`")
        if "policy" in node:
            lines.append(f"      - Policy: `{node['policy']}`")
        for branch in node.get("branches", []) or []:
            lines.append(f"      - Branch: when {_format_mapping(branch.get('when', {}))} goto `{branch.get('goto')}`")
    if route.description:
        lines.append(f"  - Notes: {route.description.strip()}")


def _format_call(item: CallSpec) -> str:
    if item.call is not None:
        return item.call
    return _format_mapping(item.call_template)


def _format_context(context: dict[str, Any]) -> str:
    if not context:
        return "`any`"
    return _format_mapping(context)


def _format_mapping(value: Any) -> str:
    if value is None:
        return "`none`"
    if isinstance(value, dict):
        if not value:
            return "`none`"
        return ", ".join(f"`{key}`={_format_mapping(item)}" for key, item in value.items())
    if isinstance(value, (list, tuple)):
        if not value:
            return "`none`"
        return "[" + ", ".join(_format_mapping(item) for item in value) + "]"
    if isinstance(value, bool):
        return f"`{str(value).lower()}`"
    if callable(value):
        return f"`{getattr(value, '__name__', 'python_function')}`"
    if hasattr(value, "to_dict"):
        return _format_mapping(value.to_dict())
    if value == "":
        return '`""`'
    return f"`{value}`"


def _format_list(value: Any) -> str:
    if not value:
        return "`none`"
    if isinstance(value, (list, tuple)):
        return ", ".join(_format_mapping(item) for item in value)
    return _format_mapping(value)
