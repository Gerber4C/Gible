def meow_minor_responder_rebid(ctx, candidates):
    calls = ctx.auction.calls
    if not _is_minor_responder_rebid_auction(calls):
        return None

    spiral = _candidate_from_gadget(candidates, "meow_spiral_3344")
    if spiral is not None and ctx.hand.hcp >= 11:
        return spiral

    signoff = _natural_long_major_signoff(ctx, candidates)
    if signoff is not None and ctx.hand.hcp <= 10:
        return signoff

    if ctx.hand.hcp <= 7:
        if ctx.hand.length("C") >= 5:
            club_drop_dead = _candidate_with(candidates, action_type="checkback_two_notrump_club_relay")
            if club_drop_dead is not None:
                return club_drop_dead
        if ctx.hand.length("D") >= 5:
            diamond_drop_dead = _candidate_with(candidates, action_type="checkback_two_club_relay")
            if diamond_drop_dead is not None:
                return diamond_drop_dead

    if ctx.hand.hcp >= 16:
        natural_slam_try = _longest_candidate_with(ctx, candidates, action_type="natural_slam_try")
        if natural_slam_try is not None:
            return natural_slam_try

    if ctx.hand.hcp >= 13:
        game_force = _candidate_with(candidates, action_type="checkback_game_force")
        if game_force is not None:
            return game_force

    if 11 <= ctx.hand.hcp <= 12:
        invite = _candidate_with(candidates, action_type="checkback_two_club_relay")
        if invite is not None:
            return invite

    return signoff


def _is_minor_responder_rebid_auction(calls):
    return (
        len(calls) == 6
        and calls[0] in ("1C", "1D")
        and calls[1] == "P"
        and calls[2] in ("1D", "1H", "1S")
        and calls[3] == "P"
        and calls[5] == "P"
    )


def _natural_long_major_signoff(ctx, candidates):
    response = ctx.auction.calls[2]
    if response not in ("1H", "1S"):
        return None
    suit = response[1]
    if ctx.hand.length(suit) < 6:
        return None
    return _candidate_with(candidates, action_type="responder_major_rebid", target_suit=suit)


def _candidate_from_gadget(candidates, gadget_id):
    for candidate in candidates:
        if candidate.origin.get("gadget_id") == gadget_id:
            return candidate
    return None


def _candidate_with(candidates, **meaning):
    for candidate in candidates:
        candidate_meaning = candidate.public_meaning or {}
        if all(candidate_meaning.get(key) == value for key, value in meaning.items()):
            return candidate
    return None


def _longest_candidate_with(ctx, candidates, **meaning):
    best = None
    best_length = -1
    for candidate in candidates:
        candidate_meaning = candidate.public_meaning or {}
        if not all(candidate_meaning.get(key) == value for key, value in meaning.items()):
            continue
        suit = candidate_meaning.get("target_suit")
        length = ctx.hand.length(suit) if suit in ("S", "H", "D", "C") else 0
        if length > best_length:
            best = candidate
            best_length = length
    return best


selection_policies = [meow_minor_responder_rebid]
