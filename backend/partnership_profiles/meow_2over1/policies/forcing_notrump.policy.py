def meow_forcing_notrump_opener_rebid(ctx, candidates):
    calls = ctx.auction.calls
    if calls not in (("1H", "P", "1N", "P"), ("1S", "P", "1N", "P")):
        return None

    opening = calls[0]
    if candidates.get("2N") is not None and 18 <= ctx.hand.hcp <= 19 and ctx.hand.balanced:
        return candidates.get("2N")

    if opening == "1H":
        if ctx.hand.length("H") >= 6:
            return candidates.get("2H")
        if ctx.hand.hcp >= 16 and ctx.hand.length("S") >= 4:
            return candidates.get("2S")
        return _minor_rebid(ctx, candidates)

    if ctx.hand.length("S") >= 6:
        return candidates.get("2S")
    if ctx.hand.length("H") >= 4:
        return candidates.get("2H")
    return _minor_rebid(ctx, candidates)


def _minor_rebid(ctx, candidates):
    club = candidates.get("2C")
    diamond = candidates.get("2D")
    if club is not None and diamond is not None:
        clubs = ctx.hand.length("C")
        diamonds = ctx.hand.length("D")
        if diamonds >= 4 and diamonds >= clubs:
            return diamond
        return club
    return diamond or club


def meow_forcing_notrump_opener_after_invite(ctx, candidates):
    invite_auctions = {
        ("1H", "P", "1N", "P", "2C", "P", "2N", "P"),
        ("1H", "P", "1N", "P", "2D", "P", "2N", "P"),
        ("1S", "P", "1N", "P", "2C", "P", "2N", "P"),
        ("1S", "P", "1N", "P", "2D", "P", "2N", "P"),
    }
    if ctx.auction.calls not in invite_auctions:
        return None
    if ctx.hand.hcp >= 14:
        return candidates.get("3N")
    return candidates.get("P")


policy_functions = [
    meow_forcing_notrump_opener_rebid,
    meow_forcing_notrump_opener_after_invite,
]

