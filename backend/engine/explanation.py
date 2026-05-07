from __future__ import annotations

from dataclasses import asdict

from .context import BidDecision


def explain(selection: BidDecision) -> dict:
    selected = selection.selected_candidate
    pool = selection.context.candidates if selection.context is not None else None
    return {
        "call": selection.call,
        "public_meaning": _public_meaning(selected),
        "internal_origin": {
            "selected": _selected_origin(selected),
            "compared_candidates": [
                {
                    "call": candidate.call,
                    "origin": candidate.origin,
                    "private_route_origin": candidate.private_route_origin,
                    "source_kind": candidate.source_kind,
                    "source_id": candidate.source_id,
                    "implementation_origin": candidate.implementation_origin,
                    "capabilities": candidate.capabilities,
                    "selection_algorithm": candidate.metadata.get("selection_algorithm"),
                    "score": candidate.score,
                    "criteria_results": list(candidate.criterion_results),
                    "metadata": candidate.metadata,
                    "features": asdict(pool.features(candidate)) if pool is not None else None,
                }
                for candidate in selection.candidate_pool.candidates
            ],
            "applied_meanings": selection.trace.applied_meanings,
            "state_records": [record.to_dict() for record in selection.trace.state_records],
            "state_view": selection.context.state.to_dict() if selection.context is not None else None,
            "frame_states": [frame.to_dict() for frame in selection.trace.frame_states],
            "private_route_states": [route_state.to_dict() for route_state in selection.trace.private_route_states],
            "selection_policy": selection.policy_origin,
        },
        "diagnostics": selection.trace.diagnostics,
        "private_memory": selection.private_memory.to_dict(),
    }


def _public_meaning(candidate) -> dict | None:
    if candidate is None:
        return None
    return {
        "origin": candidate.origin,
        "meaning": candidate.public_meaning,
    }


def _selected_origin(candidate) -> dict | None:
    if candidate is None:
        return None
    return {
        "call": candidate.call,
        "origin": candidate.origin,
        "source_kind": candidate.source_kind,
        "source_id": candidate.source_id,
        "private_route_origin": candidate.private_route_origin,
        "implementation_origin": candidate.implementation_origin,
        "capabilities": candidate.capabilities,
        "selection_algorithm": candidate.metadata.get("selection_algorithm"),
        "score": candidate.score,
        "criteria_results": list(candidate.criterion_results),
        "metadata": candidate.metadata,
    }
