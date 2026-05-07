def meow_minor_opener_rebid(ctx, candidates):
    calls = ctx.auction.calls
    if not _is_minor_opener_rebid_auction(calls):
        return None

    response_suit = _response_suit(calls[2])

    if response_suit in ("H", "S"):
        strong_raise = _raise_candidate(candidates, response_suit, strong=True)
        if strong_raise is not None and ctx.hand.length(response_suit) >= 4:
            return strong_raise

        simple_raise = _raise_candidate(candidates, response_suit, strong=False)
        if simple_raise is not None and ctx.hand.length(response_suit) >= 4:
            return simple_raise

    jump_shift = _candidate_by_action(ctx, candidates, "opener_jump_shift")
    if jump_shift is not None:
        return jump_shift

    one_level_major = _one_level_major_rebid(candidates)
    if one_level_major is not None:
        return one_level_major

    if response_suit in ("H", "S"):
        simple_raise = _raise_candidate(candidates, response_suit, strong=False)
        if simple_raise is not None and ctx.hand.length(response_suit) >= 3:
            return simple_raise

    if 18 <= ctx.hand.hcp <= 19 and ctx.hand.balanced:
        jump_notrump = candidates.get("2N")
        if jump_notrump is not None:
            return jump_notrump

    if 12 <= ctx.hand.hcp <= 14 and ctx.hand.balanced:
        minimum_notrump = candidates.get("1N")
        if minimum_notrump is not None:
            return minimum_notrump

    reverse = _candidate_by_action(ctx, candidates, "opener_reverse")
    if reverse is not None:
        return reverse

    natural_rebid = _natural_minor_rebid(ctx, candidates)
    if natural_rebid is not None:
        return natural_rebid

    return candidates.get("1N") or candidates.get("2N")


def _is_minor_opener_rebid_auction(calls):
    return (
        len(calls) == 4
        and calls[0] in ("1C", "1D")
        and calls[1] == "P"
        and calls[2] in ("1D", "1H", "1S")
        and calls[3] == "P"
    )


def _response_suit(response):
    if response in ("1D", "1H", "1S"):
        return response[1]
    return None


def _raise_candidate(candidates, suit, strong):
    target_action = "opener_jump_raise" if strong else "raise"
    for candidate in candidates.by_action_type(target_action):
        if _target_suit(candidate) == suit:
            return candidate
    return None


def _one_level_major_rebid(candidates):
    return candidates.get("1H") or candidates.get("1S")


def _candidate_by_action(ctx, candidates, action_type):
    best = None
    best_length = -1
    for candidate in candidates.by_action_type(action_type):
        suit = _target_suit(candidate)
        if suit is None or suit == "N":
            length = 0
        else:
            length = ctx.hand.length(suit)
        if length > best_length:
            best = candidate
            best_length = length
    return best


def _natural_minor_rebid(ctx, candidates):
    club = _candidate_for_action_and_suit(candidates, "opener_minor_rebid", "C") or _candidate_for_action_and_suit(candidates, "opener_second_suit_rebid", "C")
    diamond = _candidate_for_action_and_suit(candidates, "opener_minor_rebid", "D")
    if club is not None and diamond is not None:
        if ctx.hand.length("D") >= 5 and ctx.hand.length("D") >= ctx.hand.length("C"):
            return diamond
        return club
    return diamond or club


def _candidate_for_action_and_suit(candidates, action_type, suit):
    for candidate in candidates.by_action_type(action_type):
        if _target_suit(candidate) == suit:
            return candidate
    return None


def _target_suit(candidate):
    return (candidate.public_meaning or {}).get("target_suit")


selection_policies = [meow_minor_opener_rebid]
