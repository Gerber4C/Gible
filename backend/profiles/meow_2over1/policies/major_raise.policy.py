def meow_major_raise_route(ctx, candidates):
    if len(ctx.auction.calls) != 2 or ctx.auction.calls[1] != "P":
        return None
    if ctx.auction.calls[0] not in ("1S", "1H"):
        return None

    opening = _latest_record(ctx, "major_opening")
    if opening is None:
        return None

    suit = opening.attributes.get("target_suit")
    if suit not in ("S", "H"):
        return None

    support = ctx.hand.length(suit)
    hcp = ctx.hand.hcp

    if support >= 4:
        if hcp >= 13:
            return _candidate_with(candidates, action_type="jacoby_2n", target_suit=suit)
        if hcp >= 10:
            return _candidate_with(candidates, action_type="bergen_raise", target_suit=suit, raise_strength="limit")
        if hcp >= 7:
            return _candidate_with(candidates, action_type="bergen_raise", target_suit=suit, raise_strength="constructive")
        return _candidate_with(candidates, action_type="bergen_raise", target_suit=suit, raise_strength="preemptive")

    if support == 3 and 6 <= hcp <= 10:
        return _candidate_with(candidates, action_type="simple_raise", target_suit=suit)

    return None


def _latest_record(ctx, key):
    matches = ctx.state.records_matching(key)
    if not matches:
        return None
    return matches[-1]


def _candidate_with(candidates, **meaning):
    for candidate in candidates:
        candidate_meaning = candidate.public_meaning or {}
        if all(candidate_meaning.get(key) == value for key, value in meaning.items()):
            return candidate
    return None


selection_policies = [meow_major_raise_route]
