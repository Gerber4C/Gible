from __future__ import annotations

from .selector import Selection


def explain(selection: Selection) -> dict:
    selected = selection.selected
    return {
        "call": selection.call,
        "public_meaning": _public_meaning(selected),
        "internal_origin": {
            "selected": _selected_origin(selected),
            "compared_candidates": [
                {
                    "call": candidate.call,
                    "origin": candidate.origin,
                    "plan_origin": candidate.plan_origin,
                    "algorithm": candidate.algorithm,
                    "score": candidate.score,
                    "criteria_results": list(candidate.criteria_results),
                }
                for candidate in selection.candidates
            ],
            "applied_meanings": selection.trace.applied_meanings,
            "semantic_facts": [fact.to_dict() for fact in selection.trace.facts],
            "auction_state": [variable.to_dict() for variable in selection.trace.auction_state],
            "protocol_frames": [frame.to_dict() for frame in selection.trace.protocol_frames],
            "plan_states": [plan_state.to_dict() for plan_state in selection.trace.plan_states],
            "selection_policy": selection.selection_policy,
        },
        "diagnostics": selection.trace.diagnostics,
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
        "algorithm": candidate.algorithm,
        "plan_origin": candidate.plan_origin,
        "score": candidate.score,
        "criteria_results": list(candidate.criteria_results),
    }
