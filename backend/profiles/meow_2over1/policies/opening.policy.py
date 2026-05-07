def meow_opening_seat_1_2(ctx, candidates):
    if not _is_opening_auction(ctx) or _seat_position(ctx) not in (1, 2):
        return None
    return (
        _strong_opening(candidates)
        or candidates.get("1N")
        or _one_level_opening(ctx, candidates)
        or _preemptive_opening(ctx, candidates)
    )


def meow_opening_seat_3(ctx, candidates):
    if not _is_opening_auction(ctx) or _seat_position(ctx) != 3:
        return None
    if _strong_opening(candidates) is not None:
        return _strong_opening(candidates)
    if candidates.get("1N") is not None:
        return candidates.get("1N")
    if ctx.hand.hcp >= 12:
        return _one_level_opening(ctx, candidates) or _preemptive_opening(ctx, candidates)
    return _preemptive_opening(ctx, candidates) or _major_opening(ctx, candidates) or candidates.get("P")


def meow_opening_seat_4(ctx, candidates):
    if not _is_opening_auction(ctx) or _seat_position(ctx) != 4:
        return None
    if _strong_opening(candidates) is not None:
        return _strong_opening(candidates)
    if candidates.get("1N") is not None:
        return candidates.get("1N")
    if not _rule_of_15_allows_opening(ctx):
        return candidates.get("P")
    return _one_level_opening(ctx, candidates) or candidates.get("P")


def _is_opening_auction(ctx):
    return len(ctx.auction.calls) <= 3 and all(call == "P" for call in ctx.auction.calls)


def _seat_position(ctx):
    return ctx.environment.get("seat_position")


def _strong_opening(candidates):
    return candidates.get("2C") or candidates.get("2N")


def _one_level_opening(ctx, candidates):
    return _major_opening(ctx, candidates) or _minor_opening(ctx, candidates)


def _major_opening(ctx, candidates):
    spade = candidates.get("1S")
    heart = candidates.get("1H")
    if spade is not None and heart is not None:
        if ctx.hand.length("S") >= ctx.hand.length("H"):
            return spade
        return heart
    return spade or heart


def _minor_opening(ctx, candidates):
    diamond = candidates.get("1D")
    club = candidates.get("1C")
    if diamond is not None and club is not None:
        if ctx.hand.length("D") >= ctx.hand.length("C"):
            return diamond
        return club
    return diamond or club


def _preemptive_opening(ctx, candidates):
    gambling = candidates.get("3N")
    if gambling is not None:
        return gambling
    for call in ("3S", "3H", "3D", "3C", "2S", "2H", "2D"):
        candidate = candidates.get(call)
        if candidate is not None and _preempt_style_allows(ctx, call):
            return candidate
    return None


def _preempt_style_allows(ctx, call):
    seat = _seat_position(ctx)
    if seat == 4:
        return False
    suit = call[1]
    hcp = ctx.hand.hcp
    vulnerability = ctx.environment.get("vulnerability_relation")
    good_suit = _good_suit(ctx, suit)
    if seat == 2:
        return hcp >= 7 and good_suit
    if seat == 3:
        if vulnerability == "unfavorable":
            return hcp >= 5 or good_suit
        return hcp >= 4
    if vulnerability == "unfavorable":
        return hcp >= 7 and good_suit
    if vulnerability == "favorable":
        return hcp >= 5
    return hcp >= 6


def _good_suit(ctx, suit):
    return _top_honor_count(ctx, suit, ("A", "K", "Q")) >= 2 or _top_honor_count(ctx, suit, ("A", "K", "Q", "J", "T")) >= 3


def _top_honor_count(ctx, suit, ranks):
    holding = ctx.hand.holding(suit)
    return sum(1 for rank in holding if rank in ranks)


def _rule_of_15_allows_opening(ctx):
    return ctx.hand.hcp + ctx.hand.length("S") >= 15


selection_policies = [
    meow_opening_seat_1_2,
    meow_opening_seat_3,
    meow_opening_seat_4,
]
