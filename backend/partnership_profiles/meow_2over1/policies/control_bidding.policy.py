def meow_control_bidding_policy(ctx, candidates):
    agreed_suit = _latest_attribute(ctx, "agreed_suit", "suit")
    if agreed_suit is None:
        return None
    if not (
        ctx.state.exists("slam_interest", status="active")
        or (
            ctx.state.exists("transfer_superaccept", target_suit=agreed_suit, status="accepted")
            and ctx.hand.length(agreed_suit) >= 6
            and ctx.hand.hcp >= 16
        )
    ):
        return None
    control_candidates = candidates.by_action_type("control_bid")
    if not control_candidates:
        return None
    if (
        agreed_suit == "H"
        and ctx.state.exists("transfer_superaccept", target_suit="H", status="accepted")
        and ctx.hand.contains_rank("D", "A")
    ):
        diamond_control = _candidate_with(control_candidates, target_suit="D")
        if diamond_control is not None:
            return diamond_control
    ace_controls = [
        candidate
        for candidate in control_candidates
        if ctx.hand.contains_rank((candidate.public_meaning or {}).get("target_suit"), "A")
    ]
    values = ace_controls or list(control_candidates)
    return sorted(values, key=lambda candidate: _call_order(candidate.call))[0]


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


def _call_order(call):
    denominations = {"C": 0, "D": 1, "H": 2, "S": 3, "N": 4}
    if not call or call[0] not in "1234567":
        return (99, 99)
    return (int(call[0]), denominations.get(call[1], 99))


policy_functions = [meow_control_bidding_policy]

