def meow_major_response_spade_over_heart_policy(ctx, candidates):
    if not _is_direct_major_response_auction(ctx) or ctx.auction.calls[0] != "1H":
        return None
    if ctx.hand.length("S") >= 4 and ctx.hand.hcp >= 6:
        return candidates.get("1S")
    return None


def meow_major_response_two_over_one_policy(ctx, candidates):
    if not _is_direct_major_response_auction(ctx) or ctx.hand.hcp < 12:
        return None
    opening = ctx.auction.calls[0]
    if opening == "1S":
        return _longest_available(candidates, ctx, ("2H", "2D", "2C")) or candidates.get("1N")
    return _longest_available(candidates, ctx, ("2D", "2C")) or candidates.get("1N")


def meow_major_response_forcing_notrump_policy(ctx, candidates):
    if not _is_direct_major_response_auction(ctx):
        return None
    if 6 <= ctx.hand.hcp <= 12:
        return candidates.get("1N")
    return None


def _is_direct_major_response_auction(ctx):
    return (
        len(ctx.auction.calls) == 2
        and ctx.auction.calls[1] == "P"
        and ctx.auction.calls[0] in ("1H", "1S")
    )


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


policy_functions = [
    meow_major_response_spade_over_heart_policy,
    meow_major_response_two_over_one_policy,
    meow_major_response_forcing_notrump_policy,
]
