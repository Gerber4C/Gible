def meow_notrump_response_route(ctx, candidates):
    calls = ctx.auction.calls
    if len(calls) < 2 or calls[-2:] != ("1N", "P") or any(call != "P" for call in calls[:-2]):
        return None

    hcp = ctx.hand.hcp
    hearts = ctx.hand.length("H")
    spades = ctx.hand.length("S")
    diamonds = ctx.hand.length("D")
    clubs = ctx.hand.length("C")

    planned_major = _planned_major_transfer(candidates)
    if planned_major is not None:
        return planned_major

    if diamonds >= 5 and clubs >= 5 and hcp >= 10:
        return _candidate_with(candidates, action_type="five_five_minors_game_force")

    if hearts >= 5 and spades >= 5:
        if hcp >= 10:
            return _candidate_with(candidates, action_type="five_five_majors_game_force")
        if hcp >= 8:
            return _candidate_with(candidates, action_type="five_five_majors_invitational")

    if hcp <= 6:
        return _major_transfer(ctx, candidates) or _minor_transfer(diamonds, clubs, candidates) or candidates.get("P")

    if hcp <= 8:
        if hearts >= 5 or spades >= 5:
            return candidates.get("P")
        if hcp == 8 and (hearts >= 4 or spades >= 4):
            return candidates.get("2C")
        return _minor_transfer(diamonds, clubs, candidates) or candidates.get("P")

    if hcp >= 10 and hearts >= 6:
        return candidates.get("4D") or candidates.get("2D")

    if hcp >= 10 and spades >= 6:
        return candidates.get("4H") or candidates.get("2H")

    if hcp >= 9 and (hearts >= 5 or spades >= 5):
        return _major_transfer(ctx, candidates)

    if hcp >= 8 and (hearts >= 4 or spades >= 4):
        return candidates.get("2C") or _major_transfer(ctx, candidates)

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


selection_policies = [meow_notrump_response_route]
