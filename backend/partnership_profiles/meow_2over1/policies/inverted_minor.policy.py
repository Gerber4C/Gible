def meow_inverted_minor_continuation_route(ctx, candidates):
    calls = ctx.auction.calls
    if not _is_inverted_raise_auction(calls):
        return None

    game = _candidate_with(candidates, action_type="place_contract", target_suit="N")
    if game is not None and ctx.hand.hcp >= 15:
        return game

    notrump = _candidate_with(candidates, action_type="stopper_notrump_rebid")
    if notrump is not None:
        return notrump

    stopper = _lowest_call(candidates.by_action_type("stopper_bid"))
    if stopper is not None:
        return stopper

    fallback = _candidate_with(candidates, action_type="minor_fallback")
    if fallback is not None:
        return fallback

    return None


def _is_inverted_raise_auction(calls):
    return (
        len(calls) == 4
        and calls[0] in ("1C", "1D")
        and calls[1] == "P"
        and calls[2] in ("2C", "2D")
        and calls[3] == "P"
    )


def _candidate_with(candidates, **meaning):
    for candidate in candidates:
        candidate_meaning = candidate.public_meaning or {}
        if all(candidate_meaning.get(key) == value for key, value in meaning.items()):
            return candidate
    return None


def _lowest_call(candidates):
    values = tuple(candidates)
    if not values:
        return None
    return sorted(values, key=lambda candidate: _call_order(candidate.call))[0]


def _call_order(call):
    denominations = {"C": 0, "D": 1, "H": 2, "S": 3, "N": 4}
    if not call or call[0] not in "1234567":
        return (99, 99)
    return (int(call[0]), denominations.get(call[1], 99))


policy_functions = [meow_inverted_minor_continuation_route]

