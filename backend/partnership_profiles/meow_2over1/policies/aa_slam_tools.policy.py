def meow_slam_tool_route(ctx, candidates):
    obligation = _frame_answer(ctx, candidates)
    if obligation is not None:
        return obligation

    exclusion = _candidate_with(candidates, action_type="exclusion_1430")
    if exclusion is not None:
        return exclusion

    kickback = _candidate_with(candidates, action_type="kickback_1430")
    if kickback is not None:
        return kickback

    minorwood = _candidate_with(candidates, action_type="minorwood_1430")
    if minorwood is not None:
        return minorwood

    gerber = _candidate_with(candidates, action_type="gerber_ace_ask")
    if gerber is not None:
        return gerber

    quantitative = _candidate_with(candidates, action_type="quantitative_notrump_invite")
    if quantitative is not None:
        return quantitative

    rkcb = _candidate_with(candidates, action_type="rkcb_1430")
    if rkcb is None:
        return None

    agreed_suit = _latest_attribute(ctx, "agreed_suit", "suit")
    if agreed_suit in ("H", "S") and ctx.hand.length(agreed_suit) >= 6:
        control = _candidate_with(candidates, action_type="control_bid")
        if control is not None and _has_safe_control_to_show(ctx, control):
            return None

    private_rkcb = [
        candidate
        for candidate in candidates.for_call(rkcb.call)
        if candidate.private_route_origin is not None
    ]
    if private_rkcb:
        return candidates.best(private_rkcb)
    return rkcb


def _frame_answer(ctx, candidates):
    answer_candidates = ctx.obligation_candidates
    if not answer_candidates:
        return None
    return candidates.best(answer_candidates)


def _candidate_with(candidates, **meaning):
    for candidate in candidates:
        candidate_meaning = candidate.public_meaning or {}
        if all(candidate_meaning.get(key) == value for key, value in meaning.items()):
            return candidate
    return None


def _latest_attribute(ctx, key, attribute):
    records = ctx.state.records_matching(key)
    if not records:
        return None
    return records[-1].attribute(attribute)


def _has_safe_control_to_show(ctx, candidate):
    suit = (candidate.public_meaning or {}).get("target_suit")
    if suit not in ("S", "H", "D", "C"):
        return False
    return (
        ctx.hand.contains_rank(suit, "A")
        or ctx.hand.contains_rank(suit, "K")
        or ctx.hand.length(suit) <= 1
    )


policy_functions = [meow_slam_tool_route]

