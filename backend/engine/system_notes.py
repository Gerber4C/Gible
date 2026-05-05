from __future__ import annotations

from typing import Any

from .convention import BiddingPlan, CallSpecification, Convention, ConventionSet


def generate_system_notes(convention_set: ConventionSet) -> str:
    lines: list[str] = [
        f"# {convention_set.name}",
        "",
        f"Convention Set ID: `{convention_set.id}`",
        f"Version: `{convention_set.version}`",
        f"Author: {convention_set.author.name}",
    ]
    if convention_set.description:
        lines.extend(["", convention_set.description.strip()])
    if convention_set.system_notes:
        lines.extend(["", convention_set.system_notes.strip()])

    for convention in convention_set.conventions:
        _render_convention(lines, convention)

    lines.append("")
    return "\n".join(lines)


def _render_convention(lines: list[str], convention: Convention) -> None:
    lines.extend(
        [
            "",
            f"## {convention.name}",
            "",
            f"Convention ID: `{convention.id}`",
            f"Namespace: `{convention.namespace}`",
            f"Version: `{convention.version}`",
            f"Author: {convention.author.name}",
        ]
    )
    if convention.description:
        lines.extend(["", convention.description.strip()])
    if convention.system_notes:
        lines.extend(["", convention.system_notes.strip()])

    if convention.call_specifications:
        lines.extend(["", "### Call Specifications"])
        for item in convention.call_specifications:
            _render_call_specification(lines, item)

    if convention.protocol_frames:
        lines.extend(["", "### Protocol Frames"])
        for frame in convention.protocol_frames:
            lines.extend(
                [
                    "",
                    f"- `{frame.id}`: `{frame.frame_type}`",
                    f"  - Context: {_format_context(frame.context)}",
                    f"  - Source call: `{frame.source_call}`",
                    f"  - Variables: {_format_mapping(frame.variables)}",
                ]
            )
            if frame.description:
                lines.append(f"  - Notes: {frame.description.strip()}")

    if convention.bidding_plans:
        lines.extend(["", "### Bidding Plans"])
        for plan in convention.bidding_plans:
            _render_bidding_plan(lines, plan)

    if convention.call_selection_policies:
        lines.extend(["", "### Call Selection Policies"])
        for policy in convention.call_selection_policies:
            lines.extend(
                [
                    "",
                    f"- `{policy.id}`",
                    f"  - Algorithm: `{policy.algorithm}`",
                    f"  - Scope: {_format_mapping(policy.scope)}",
                    f"  - Tie breaker: `{policy.tie_breaker}`",
                    f"  - Choices: {_format_list(policy.choices)}",
                    f"  - Fallback: `{policy.fallback}`",
                ]
            )
            if policy.description:
                lines.append(f"  - Notes: {policy.description.strip()}")

    if convention.named_evaluators:
        lines.extend(["", "### Named Evaluators"])
        for evaluator in convention.named_evaluators:
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


def _render_call_specification(lines: list[str], item: CallSpecification) -> None:
    lines.extend(
        [
            "",
            f"- `{item.id}`",
            f"  - Context: {_format_context(item.context)}",
            f"  - Call: `{item.call}`",
            f"  - Call Act Types: {_format_list(item.call_act_types)}",
            f"  - Requires: {_format_mapping(item.requires)}",
            f"  - Meaning: {_format_mapping(item.meaning)}",
            f"  - Applicability: {_format_mapping(item.applicability)}",
            f"  - Selection: {_format_mapping(item.selection)}",
            f"  - Effects: {_format_list(item.effects)}",
        ]
    )
    if item.description:
        lines.append(f"  - Notes: {item.description.strip()}")
    if item.system_notes:
        lines.append(f"  - System Notes: {item.system_notes.strip()}")


def _render_bidding_plan(lines: list[str], plan: BiddingPlan) -> None:
    lines.extend(
        [
            "",
            f"- `{plan.id}`",
            f"  - Owner: `{plan.owner}`",
            f"  - Goal: `{plan.goal}`",
            f"  - Context: {_format_context(plan.context)}",
            f"  - Entry call: `{plan.entry_call}`",
            f"  - Entry candidate: `{str(plan.entry_candidate).lower()}`",
            f"  - Entry score: `{plan.entry_score}`",
            f"  - Preconditions: {_format_mapping(plan.preconditions)}",
            f"  - Selection: {_format_mapping(plan.selection)}",
            f"  - Workflow start: `{plan.start_node}`",
            "  - Workflow nodes:",
        ]
    )
    for node_id, node in plan.workflow.get("nodes", {}).items():
        lines.append(f"    - `{node_id}`: `{node.get('kind')}`")
        if "actor" in node:
            lines.append(f"      - Actor: `{node['actor']}`")
        if "policy" in node:
            lines.append(f"      - Policy: `{node['policy']}`")
        for branch in node.get("branches", []) or []:
            lines.append(f"      - Branch: when {_format_mapping(branch.get('when', {}))} goto `{branch.get('goto')}`")
    if plan.description:
        lines.append(f"  - Notes: {plan.description.strip()}")


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
    if value == "":
        return '`""`'
    return f"`{value}`"


def _format_list(value: Any) -> str:
    if not value:
        return "`none`"
    if isinstance(value, (list, tuple)):
        return ", ".join(_format_mapping(item) for item in value)
    return _format_mapping(value)
