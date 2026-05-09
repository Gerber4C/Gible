def meow_two_over_one_opener_major_rebid(ctx, candidates):
    calls = ctx.auction.calls
    if not _is_two_over_one_opener_rebid(calls):
        return None
    opening_major = calls[0][1]
    if ctx.hand.length(opening_major) >= 6:
        return candidates.get("2" + opening_major)
    return None


def meow_two_over_one_opener_side_suit_rebid(ctx, candidates):
    calls = ctx.auction.calls
    if not _is_two_over_one_opener_rebid(calls):
        return None
    for call in _side_rebid_order(calls[0], calls[2]):
        candidate = candidates.get(call)
        if candidate is None:
            continue
        suit = call[1]
        if ctx.hand.length(suit) >= 4:
            return candidate
    return None


def meow_two_over_one_responder_placement(ctx, candidates):
    calls = ctx.auction.calls
    if not _is_after_two_over_one_major_rebid(calls):
        return None
    opener_major = calls[0][1]
    if ctx.hand.length(opener_major) >= 2:
        return candidates.get("4" + opener_major)
    return candidates.get("3N")


def meow_two_over_one_responder_after_side_suit(ctx, candidates):
    calls = ctx.auction.calls
    if not _is_after_two_over_one_side_suit(calls):
        return None
    side_suit = calls[4][1]
    if side_suit in ("H", "S") and ctx.hand.length(side_suit) >= 4:
        return candidates.get("4" + side_suit)
    return candidates.get("3N")


def _is_two_over_one_opener_rebid(calls):
    return (
        len(calls) == 4
        and calls[0] in ("1H", "1S")
        and calls[1] == "P"
        and calls[2] in _two_over_one_responses(calls[0])
        and calls[3] == "P"
    )


def _is_after_two_over_one_major_rebid(calls):
    return (
        len(calls) == 6
        and calls[0] in ("1H", "1S")
        and calls[1] == "P"
        and calls[2] in _two_over_one_responses(calls[0])
        and calls[3] == "P"
        and calls[4] == "2" + calls[0][1]
        and calls[5] == "P"
    )


def _is_after_two_over_one_side_suit(calls):
    return (
        len(calls) == 6
        and calls[0] in ("1H", "1S")
        and calls[1] == "P"
        and calls[2] in _two_over_one_responses(calls[0])
        and calls[3] == "P"
        and calls[4] in _side_rebid_order(calls[0], calls[2])
        and calls[5] == "P"
    )


def _two_over_one_responses(opening):
    if opening == "1S":
        return ("2C", "2D", "2H")
    return ("2C", "2D")


def _side_rebid_order(opening, response):
    if opening == "1S" and response == "2C":
        return ("2H", "2D")
    if opening == "1S" and response == "2D":
        return ("2H",)
    if opening == "1H" and response == "2C":
        return ("2S", "2D")
    if opening == "1H" and response == "2D":
        return ("2S",)
    return ()


policy_functions = [
    meow_two_over_one_opener_major_rebid,
    meow_two_over_one_opener_side_suit_rebid,
    meow_two_over_one_responder_placement,
    meow_two_over_one_responder_after_side_suit,
]
