def meow_minor_response_route(ctx, candidates):
    calls = ctx.auction.calls
    if len(calls) != 2 or calls[1] != "P" or calls[0] not in ("1C", "1D"):
        return None

    opening_suit = calls[0][1]
    hcp = ctx.hand.hcp

    weak_jump = _weak_jump_shift(ctx, candidates)
    if weak_jump is not None:
        return weak_jump

    minor_raise = _minor_raise(opening_suit, hcp, ctx, candidates)
    if minor_raise is not None:
        return minor_raise

    notrump = _natural_notrump_response(ctx, candidates)
    if notrump is not None:
        return notrump

    if calls[0] == "1C":
        diamond_first = _walsh_diamond_first(ctx, candidates)
        if diamond_first is not None:
            return diamond_first
        major = _major_response(ctx, candidates)
        if major is not None:
            return major
        return candidates.get("1D")

    major = _major_response(ctx, candidates)
    if major is not None:
        return major
    return candidates.first_available("1N", "2N", "3N")


def _weak_jump_shift(ctx, candidates):
    if not 3 <= ctx.hand.hcp <= 7:
        return None
    if ctx.hand.length("S") >= 6 and ctx.hand.length("S") >= ctx.hand.length("H"):
        return _candidate_with(candidates, action_type="weak_jump_shift", target_suit="S")
    if ctx.hand.length("H") >= 6:
        return _candidate_with(candidates, action_type="weak_jump_shift", target_suit="H")
    return None


def _minor_raise(opening_suit, hcp, ctx, candidates):
    if ctx.hand.length(opening_suit) < 5:
        return None
    if _has_four_card_major(ctx):
        return None
    if hcp >= 13:
        crisscross = _candidate_with(candidates, action_type="crisscross_minor_raise", target_suit=opening_suit)
        if crisscross is not None:
            return crisscross
    if hcp >= 10:
        return _candidate_with(candidates, action_type="inverted_minor_raise", target_suit=opening_suit)
    return None


def _natural_notrump_response(ctx, candidates):
    if _has_four_card_major(ctx) or not ctx.hand.balanced:
        return None
    return candidates.first_available("3N", "2N", "1N")


def _walsh_diamond_first(ctx, candidates):
    if candidates.get("1D") is None or ctx.hand.length("D") < 4:
        return None
    if not _has_four_card_major(ctx):
        return candidates.get("1D")
    if ctx.hand.length("D") >= 7:
        return candidates.get("1D")
    if ctx.hand.hcp >= 12 and ctx.hand.length("D") >= 5:
        return candidates.get("1D")
    return None


def _major_response(ctx, candidates):
    spades = ctx.hand.length("S")
    hearts = ctx.hand.length("H")
    if spades >= 5 and hearts >= 4:
        return candidates.get("1S")
    if hearts >= 4:
        return candidates.get("1H")
    if spades >= 4:
        return candidates.get("1S")
    return None


def _has_four_card_major(ctx):
    return ctx.hand.length("H") >= 4 or ctx.hand.length("S") >= 4


def _candidate_with(candidates, **meaning):
    for candidate in candidates:
        candidate_meaning = candidate.public_meaning or {}
        if all(candidate_meaning.get(key) == value for key, value in meaning.items()):
            return candidate
    return None


policy_functions = [meow_minor_response_route]

