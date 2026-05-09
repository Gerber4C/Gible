def meow_strong_two_club_response(ctx, candidates):
    if ctx.auction.calls == ("2C", "P"):
        return candidates.get("2D")
    return None


def meow_strong_two_club_opener_rebid(ctx, candidates):
    if ctx.auction.calls != ("2C", "P", "2D", "P"):
        return None
    if _notrump_rebid_shape(ctx):
        if ctx.hand.hcp <= 24:
            return candidates.get("2N")
        return candidates.get("3N")
    return _longest_natural_strong_rebid(ctx, candidates)


def meow_strong_two_club_responder_rebid(ctx, candidates):
    calls = ctx.auction.calls
    if calls == ("2C", "P", "2D", "P", "2N", "P"):
        return _after_strong_two_club_two_notrump(ctx, candidates)
    if ctx.hand.hcp <= 3:
        if calls in (("2C", "P", "2D", "P", "2H", "P"), ("2C", "P", "2D", "P", "2S", "P")):
            return candidates.get("3C")
        if calls == ("2C", "P", "2D", "P", "3C", "P"):
            return candidates.get("3D")
        if calls == ("2C", "P", "2D", "P", "3D", "P"):
            return candidates.get("3N")
    return None


def meow_strong_two_club_after_second_negative(ctx, candidates):
    calls = ctx.auction.calls
    if calls == ("2C", "P", "2D", "P", "2H", "P", "3C", "P"):
        if ctx.hand.hcp >= 20 and ctx.hand.length("H") >= 6:
            return candidates.get("4H")
        return candidates.get("3H")
    if calls == ("2C", "P", "2D", "P", "2S", "P", "3C", "P"):
        if ctx.hand.hcp >= 20 and ctx.hand.length("S") >= 6:
            return candidates.get("4S")
        return candidates.get("3S")
    return None


def _after_strong_two_club_two_notrump(ctx, candidates):
    if ctx.hand.hcp <= 2:
        return candidates.get("P")
    hearts = ctx.hand.length("H")
    spades = ctx.hand.length("S")
    if hearts >= 5 and hearts >= spades:
        return candidates.get("3D")
    if spades >= 5:
        return candidates.get("3H")
    if hearts >= 4 or spades >= 4:
        return candidates.get("3C")
    if ctx.hand.length("C") >= 4 and ctx.hand.length("D") >= 4:
        return candidates.get("3S")
    return candidates.get("3N")


def _longest_natural_strong_rebid(ctx, candidates):
    calls_by_suit = {"H": "2H", "S": "2S", "C": "3C", "D": "3D"}
    available = [suit for suit in "HSDC" if candidates.get(calls_by_suit[suit]) is not None]
    if not available:
        return None
    ordered = sorted(available, key=lambda suit: (-ctx.hand.length(suit), _strong_rebid_tiebreak(suit)))
    return candidates.get(calls_by_suit[ordered[0]])


def _strong_rebid_tiebreak(suit):
    return {"H": 0, "S": 1, "C": 2, "D": 3}[suit]


def _notrump_rebid_shape(ctx):
    lengths = sorted((ctx.hand.length(suit) for suit in "SHDC"), reverse=True)
    return lengths in ([5, 3, 3, 2], [4, 4, 3, 2], [4, 3, 3, 3], [4, 4, 4, 1])


policy_functions = [
    meow_strong_two_club_response,
    meow_strong_two_club_opener_rebid,
    meow_strong_two_club_responder_rebid,
    meow_strong_two_club_after_second_negative,
]

