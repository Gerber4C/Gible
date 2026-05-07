from __future__ import annotations

from .auction import Auction
from .model import CallSpec, PartnershipProfile
from .matcher import matches_context
from .trace import AuctionTrace, FrameState


def recover_frame_states(profile: PartnershipProfile, trace: AuctionTrace, call: str, prior_auction: Auction) -> None:
    for frame in profile.frame_specs:
        if frame.source_call != call:
            continue
        if not matches_context(frame.context, prior_auction):
            continue
        close_frames_for_new_frame(trace, frame.closes)
        trace.add_frame_state(
            FrameState(
                frame_id=frame.id,
                frame_type=frame.frame_type,
                status="active",
                variables=frame.variables,
                origin=frame.origin_dict(),
                current_stage=frame.stages[0] if frame.stages else None,
                obligation=frame.obligation,
                close_on_actions=frame.close_on_actions,
                close_on_act_types=frame.close_on_act_types,
            )
        )


def advance_frame_states(trace: AuctionTrace, call_specification: CallSpec) -> None:
    if not trace.frame_states:
        return

    action_type = call_specification.meaning.get("action_type")
    call_act_types = set(call_specification.call_act_types) | set(call_specification.meaning.get("call_act_types", []))
    updated = []
    for frame in trace.frame_states:
        if frame.status != "active":
            updated.append(frame)
            continue

        if _frame_should_close(frame, action_type, call_act_types):
            updated.append(_frame_with(status="closed", frame=frame))
            continue

        next_stage = _next_frame_stage(frame, action_type)
        if next_stage != frame.current_stage:
            updated.append(_frame_with(frame=frame, current_stage=next_stage))
            continue

        updated.append(frame)
    trace.frame_states = updated


def close_frames_for_new_frame(trace: AuctionTrace, closes: tuple[str, ...]) -> None:
    if not closes:
        return
    updated = []
    for frame in trace.frame_states:
        if frame.status == "active" and _frame_type_is_closed_by(frame.frame_type, closes):
            updated.append(_frame_with(status="closed", frame=frame))
        else:
            updated.append(frame)
    trace.frame_states = updated


def _next_frame_stage(frame: FrameState, action_type: str | None) -> str | None:
    if action_type not in ("transfer_completion", "superaccept"):
        return frame.current_stage
    if frame.current_stage == "opener_rebid" and frame.frame_type in ("major_transfer", "minor_transfer", "transfer"):
        return "responder_continuation"
    return frame.current_stage


def _frame_should_close(frame: FrameState, action_type: str | None, call_act_types: set[str]) -> bool:
    if action_type in frame.close_on_actions:
        return True
    if call_act_types.intersection(frame.close_on_act_types):
        return True
    if frame.frame_type not in ("major_transfer", "minor_transfer", "transfer"):
        return False
    return action_type in ("final_placement", "signoff") or "final_placement" in call_act_types


def _frame_type_is_closed_by(frame_type: str, closes: tuple[str, ...]) -> bool:
    normalized = {str(item).lower() for item in closes}
    return "*" in normalized or "all" in normalized or frame_type.lower() in normalized


def _frame_with(*, frame: FrameState, status: str | None = None, current_stage: str | None = None) -> FrameState:
    return FrameState(
        frame_id=frame.frame_id,
        frame_type=frame.frame_type,
        status=status if status is not None else frame.status,
        variables=frame.variables,
        origin=frame.origin,
        current_stage=current_stage if current_stage is not None else frame.current_stage,
        obligation=frame.obligation,
        close_on_actions=frame.close_on_actions,
        close_on_act_types=frame.close_on_act_types,
    )
