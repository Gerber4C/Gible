def meow_weak_two_responder_route(ctx, candidates):
    calls = ctx.auction.calls
    if len(calls) != 2 or calls[1] != "P" or calls[0] not in ("2D", "2H", "2S"):
        return None
    preempt_suit = calls[0][1]
    own_suit = _best_new_suit(ctx, preempt_suit, candidates)
    support = ctx.hand.length(preempt_suit)

    if own_suit is not None and _new_suit_forcing_values(ctx, own_suit, preempt_suit):
        return candidates.get(_new_suit_call(calls[0], own_suit))

    if _ogust_values(ctx, preempt_suit):
        return candidates.get("2N")

    if preempt_suit in ("H", "S") and support >= 3 and _major_game_raise_values(ctx):
        return candidates.get("4" + preempt_suit)

    if support >= 3 and ctx.hand.hcp >= 6:
        return candidates.get("3" + preempt_suit)

    return candidates.get("P")


def meow_ogust_answer_route(ctx, candidates):
    calls = ctx.auction.calls
    if len(calls) != 4 or calls[1:] != ("P", "2N", "P") or calls[0] not in ("2D", "2H", "2S"):
        return None
    preempt_suit = calls[0][1]
    if _solid_preempt_suit(ctx, preempt_suit):
        return candidates.get("3N")
    good_hand = _good_weak_two_hand(ctx)
    good_suit = _good_preempt_suit(ctx, preempt_suit)
    if not good_hand and not good_suit:
        return candidates.get("3C")
    if not good_hand and good_suit:
        return candidates.get("3D")
    if good_hand and not good_suit:
        return candidates.get("3H")
    return candidates.get("3S")


def meow_ogust_responder_placement(ctx, candidates):
    calls = ctx.auction.calls
    if len(calls) != 6 or calls[1] != "P" or calls[2] != "2N" or calls[3] != "P" or calls[5] != "P":
        return None
    if calls[0] not in ("2D", "2H", "2S"):
        return None
    preempt_suit = calls[0][1]
    answer = calls[4]
    if preempt_suit in ("H", "S"):
        strong_answer = answer in ("3H", "3S", "3N")
        excellent_answer = answer in ("3S", "3N")
        if ctx.hand.length(preempt_suit) >= 2 and (
            ctx.hand.hcp >= 16
            or (ctx.hand.hcp >= 15 and strong_answer)
            or (ctx.hand.hcp >= 14 and excellent_answer)
        ):
            return candidates.get("4" + preempt_suit)
        if answer == "3" + preempt_suit:
            return candidates.get("P")
        return candidates.get("3" + preempt_suit)
    if ctx.hand.hcp >= 16 and ctx.hand.length("D") >= 3:
        return candidates.get("5D")
    if calls[4] == "3D":
        return candidates.get("P")
    return candidates.get("3D")


def meow_new_suit_forcing_rebid(ctx, candidates):
    calls = ctx.auction.calls
    if len(calls) != 4 or calls[1] != "P" or calls[3] != "P" or calls[0] not in ("2D", "2H", "2S"):
        return None
    if calls[2] == "2N":
        return None
    preempt_suit = calls[0][1]
    responder_suit = calls[2][1]
    if responder_suit == preempt_suit:
        return None
    support_call = _support_new_suit_call(calls[0], calls[2])
    if support_call is not None and ctx.hand.length(responder_suit) >= 3:
        supported = candidates.get(support_call)
        if supported is not None:
            return supported
    return candidates.get("3" + preempt_suit)


def _ogust_values(ctx, preempt_suit):
    support = ctx.hand.length(preempt_suit)
    if ctx.hand.hcp >= 14 and support >= 2:
        return True
    return ctx.hand.hcp >= 16


def _new_suit_forcing_values(ctx, suit, preempt_suit):
    if ctx.hand.length(suit) >= 6 and ctx.hand.hcp >= 12 and ctx.hand.length(preempt_suit) <= 1:
        return True
    return ctx.hand.length(suit) >= 5 and ctx.hand.hcp >= 15 and ctx.hand.length(preempt_suit) <= 2


def _major_game_raise_values(ctx):
    return ctx.hand.hcp >= 12 or _quick_tricks(ctx) >= 3


def _best_new_suit(ctx, preempt_suit, candidates):
    possible = []
    for suit in "SHDC":
        if suit == preempt_suit:
            continue
        call = _new_suit_call(ctx.auction.calls[0], suit)
        if call is not None and candidates.get(call) is not None:
            possible.append(suit)
    if not possible:
        return None
    ordered = sorted(possible, key=lambda suit: (-ctx.hand.length(suit), _new_suit_tiebreak(suit)))
    return ordered[0]


def _new_suit_call(opening_call, suit):
    table = {
        ("2D", "H"): "2H",
        ("2D", "S"): "2S",
        ("2D", "C"): "3C",
        ("2H", "S"): "2S",
        ("2H", "C"): "3C",
        ("2H", "D"): "3D",
        ("2S", "C"): "3C",
        ("2S", "D"): "3D",
        ("2S", "H"): "3H",
    }
    return table.get((opening_call, suit))


def _support_new_suit_call(opening_call, responder_call):
    table = {
        ("2D", "2H"): "3H",
        ("2H", "2S"): "3S",
        ("2S", "3C"): "4C",
    }
    return table.get((opening_call, responder_call))


def _new_suit_tiebreak(suit):
    return {"S": 0, "H": 1, "D": 2, "C": 3}[suit]


def _good_weak_two_hand(ctx):
    return ctx.hand.hcp >= 8


def _good_preempt_suit(ctx, suit):
    return _top_honor_count(ctx, suit, ("A", "K", "Q")) >= 2


def _solid_preempt_suit(ctx, suit):
    return _top_honor_count(ctx, suit, ("A", "K", "Q")) == 3


def _top_honor_count(ctx, suit, ranks):
    holding = ctx.hand.holding(suit)
    return sum(1 for rank in holding if rank in ranks)


def _quick_tricks(ctx):
    tricks = 0
    for suit in "SHDC":
        if ctx.hand.contains_rank(suit, "A"):
            tricks += 1
        if ctx.hand.contains_rank(suit, "K") and ctx.hand.length(suit) >= 2:
            tricks += 1
    return tricks


policy_functions = [
    meow_weak_two_responder_route,
    meow_ogust_answer_route,
    meow_ogust_responder_placement,
    meow_new_suit_forcing_rebid,
]

