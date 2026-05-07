def meow_major_response_route(ctx, candidates):
    if len(ctx.auction.calls) != 2 or ctx.auction.calls[1] != "P":
        return None
    opening = ctx.auction.calls[0]
    if opening not in ("1H", "1S"):
        return None

    if opening == "1H" and ctx.hand.length("S") >= 4 and ctx.hand.hcp >= 6:
        return candidates.get("1S")

    if ctx.hand.hcp >= 12:
        if opening == "1S":
            return (
                _longest_available(candidates, ctx, ("2H", "2D", "2C"))
                or candidates.get("1N")
            )
        return _longest_available(candidates, ctx, ("2D", "2C")) or candidates.get("1N")

    if 6 <= ctx.hand.hcp <= 12:
        return candidates.get("1N")

    return None


def _longest_available(candidates, ctx, calls):
    best = None
    best_length = -1
    for call in calls:
        candidate = candidates.get(call)
        if candidate is None:
            continue
        suit = call[1]
        length = ctx.hand.length(suit)
        if length > best_length:
            best = candidate
            best_length = length
    return best


selection_policies = [meow_major_response_route]
