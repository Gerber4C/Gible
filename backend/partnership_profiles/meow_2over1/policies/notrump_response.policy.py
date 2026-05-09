def meow_transfer_completion_route(ctx, candidates):
    calls = ctx.auction.calls
    if len(calls) < 4 or calls[-1] != "P":
        return None

    sequence = calls[-4:]
    transfer_map = {
        ("1N", "P", "2D", "P"): ("H", "3H", "2H"),
        ("1N", "P", "2H", "P"): ("S", "3S", "2S"),
        ("1N", "P", "2S", "P"): ("C", "2N", "3C"),
        ("1N", "P", "2N", "P"): ("D", "3C", "3D"),
    }
    route = transfer_map.get(sequence)
    if route is None:
        return None
    _target_suit, superaccept_call, normal_call = route
    return candidates.get(superaccept_call) or candidates.get(normal_call)


def meow_puppet_stayman_route(ctx, candidates):
    calls = ctx.auction.calls
    if not calls or calls[-1] != "P":
        return None

    if _suffix(calls, ("1N", "P", "3C", "P")) or _suffix(calls, ("2N", "P", "3C", "P")):
        hearts = ctx.hand.length("H")
        spades = ctx.hand.length("S")
        if hearts >= 5:
            return candidates.get("3H")
        if spades >= 5:
            return candidates.get("3S")
        if hearts == 4 or spades == 4:
            return candidates.get("3D")
        return candidates.get("3N")

    if _suffix(calls, ("3C", "P", "3H", "P")):
        return candidates.get("4H") if ctx.hand.length("H") >= 3 else candidates.get("3N")

    if _suffix(calls, ("3C", "P", "3S", "P")):
        return candidates.get("4S") if ctx.hand.length("S") >= 3 else candidates.get("3N")

    if _suffix(calls, ("3C", "P", "3D", "P")):
        hearts = ctx.hand.length("H")
        spades = ctx.hand.length("S")
        if hearts == 4 and spades == 4:
            return candidates.get("4D")
        if spades == 4:
            return candidates.get("3H")
        if hearts == 4:
            return candidates.get("3S")
        return candidates.get("3N")

    if _suffix(calls, ("3C", "P", "3D", "P", "3H", "P")):
        return candidates.get("4S") if ctx.hand.length("S") == 4 else candidates.get("3N")

    if _suffix(calls, ("3C", "P", "3D", "P", "3S", "P")):
        return candidates.get("4H") if ctx.hand.length("H") == 4 else candidates.get("3N")

    if _suffix(calls, ("3C", "P", "3D", "P", "4D", "P")):
        if ctx.hand.length("S") == 4:
            return candidates.get("4S")
        if ctx.hand.length("H") == 4:
            return candidates.get("4H")
        return candidates.get("3N")

    return None


def meow_1n_private_route_policy(ctx, candidates):
    if not _is_clean_1n_response(ctx):
        return None

    return _planned_major_transfer(candidates)


def meow_1n_two_suiter_policy(ctx, candidates):
    if not _is_clean_1n_response(ctx):
        return None

    hcp = ctx.hand.hcp
    hearts = ctx.hand.length("H")
    spades = ctx.hand.length("S")
    diamonds = ctx.hand.length("D")
    clubs = ctx.hand.length("C")

    if diamonds >= 5 and clubs >= 5 and hcp >= 10:
        return _candidate_with(candidates, action_type="five_five_minors_game_force")

    if hearts >= 5 and spades >= 5:
        if hcp >= 10:
            return _candidate_with(candidates, action_type="five_five_majors_game_force")
        if hcp >= 8:
            return _candidate_with(candidates, action_type="five_five_majors_invitational")

    return None


def meow_1n_weak_partscore_policy(ctx, candidates):
    if not _is_clean_1n_response(ctx):
        return None

    hcp = ctx.hand.hcp
    hearts = ctx.hand.length("H")
    spades = ctx.hand.length("S")
    diamonds = ctx.hand.length("D")
    clubs = ctx.hand.length("C")

    if hcp <= 6:
        return _major_transfer(ctx, candidates) or _minor_transfer(diamonds, clubs, candidates) or candidates.get("P")

    if hcp <= 8:
        if hearts >= 5 or spades >= 5:
            return candidates.get("P")
        if hcp == 8 and (hearts >= 4 or spades >= 4):
            return candidates.get("2C")
        return _minor_transfer(diamonds, clubs, candidates) or candidates.get("P")

    return None


def meow_1n_major_transfer_policy(ctx, candidates):
    if not _is_clean_1n_response(ctx):
        return None

    hcp = ctx.hand.hcp
    hearts = ctx.hand.length("H")
    spades = ctx.hand.length("S")

    if hcp >= 10 and hearts >= 6:
        return candidates.get("4D") or candidates.get("2D")

    if hcp >= 10 and spades >= 6:
        return candidates.get("4H") or candidates.get("2H")

    if hcp >= 9 and (hearts >= 5 or spades >= 5):
        return _major_transfer(ctx, candidates)

    return None


def meow_1n_major_search_policy(ctx, candidates):
    if not _is_clean_1n_response(ctx):
        return None

    hcp = ctx.hand.hcp
    hearts = ctx.hand.length("H")
    spades = ctx.hand.length("S")

    if hcp >= 10 and hearts <= 4 and spades <= 4 and (hearts == 4 or spades == 4):
        puppet = _candidate_with(candidates, action_type="puppet_stayman")
        if puppet is not None:
            return puppet

    if hcp >= 8 and (hearts >= 4 or spades >= 4):
        return candidates.get("2C") or _major_transfer(ctx, candidates)

    return None


def meow_1n_terminal_notrump_policy(ctx, candidates):
    if not _is_clean_1n_response(ctx):
        return None

    return _major_transfer(ctx, candidates) or candidates.first_available("3N", "2N", "P")


def _planned_major_transfer(candidates):
    for call in ("2D", "2H"):
        planned = [candidate for candidate in candidates.for_call(call) if candidate.private_route_origin is not None]
        if planned:
            return candidates.best(planned)
    return None


def _major_transfer(ctx, candidates):
    hearts = ctx.hand.length("H")
    spades = ctx.hand.length("S")
    if spades >= 5 and spades >= hearts:
        return candidates.get("2H")
    if hearts >= 5:
        return candidates.get("2D")
    return None


def _candidate_with(candidates, **meaning):
    for candidate in candidates:
        candidate_meaning = candidate.public_meaning or {}
        if all(candidate_meaning.get(key) == value for key, value in meaning.items()):
            return candidate
    return None


def _minor_transfer(diamonds, clubs, candidates):
    if clubs >= 6 and clubs >= diamonds:
        return candidates.get("2S")
    if diamonds >= 6:
        return candidates.get("2N")
    return None


def _is_clean_1n_response(ctx):
    calls = ctx.auction.calls
    return len(calls) >= 2 and calls[-2:] == ("1N", "P") and all(call == "P" for call in calls[:-2])


def _suffix(calls, expected):
    return len(calls) >= len(expected) and tuple(calls[-len(expected):]) == tuple(expected)


policy_functions = [
    meow_puppet_stayman_route,
    meow_transfer_completion_route,
    meow_1n_private_route_policy,
    meow_1n_two_suiter_policy,
    meow_1n_weak_partscore_policy,
    meow_1n_major_transfer_policy,
    meow_1n_major_search_policy,
    meow_1n_terminal_notrump_policy,
]
