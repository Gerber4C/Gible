def meow_crisscross_minor_continuation_route(ctx, candidates):
    calls = ctx.auction.calls
    if not _is_crisscross_raise_auction(calls):
        return None

    notrump_game = _candidate_with(candidates, action_type="place_contract", target_suit="N")
    if notrump_game is not None:
        return notrump_game

    return _candidate_with(candidates, action_type="minor_fallback")


def _is_crisscross_raise_auction(calls):
    return (
        len(calls) == 4
        and (
            calls == ("1C", "P", "2D", "P")
            or calls == ("1D", "P", "3C", "P")
        )
    )


def _candidate_with(candidates, **meaning):
    for candidate in candidates:
        candidate_meaning = candidate.public_meaning or {}
        if all(candidate_meaning.get(key) == value for key, value in meaning.items()):
            return candidate
    return None


policy_functions = [meow_crisscross_minor_continuation_route]

