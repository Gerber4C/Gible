def meow_major_raise_jacoby_policy(ctx, candidates):
    suit = _direct_major_opening_suit(ctx)
    if suit is None or ctx.hand.length(suit) < 4 or ctx.hand.hcp < 13:
        return None
    return _candidate_with(candidates, action_type="jacoby_2n", target_suit=suit)


def meow_major_raise_bergen_policy(ctx, candidates):
    suit = _direct_major_opening_suit(ctx)
    if suit is None or ctx.hand.length(suit) < 4 or ctx.hand.hcp >= 13:
        return None

    hcp = ctx.hand.hcp
    if hcp >= 10:
        return _candidate_with(candidates, action_type="bergen_raise", target_suit=suit, raise_strength="limit")
    if hcp >= 7:
        return _candidate_with(candidates, action_type="bergen_raise", target_suit=suit, raise_strength="constructive")
    return _candidate_with(candidates, action_type="bergen_raise", target_suit=suit, raise_strength="preemptive")


def meow_major_raise_simple_policy(ctx, candidates):
    suit = _direct_major_opening_suit(ctx)
    if suit is None:
        return None
    if ctx.hand.length(suit) == 3 and 6 <= ctx.hand.hcp <= 10:
        return _candidate_with(candidates, action_type="simple_raise", target_suit=suit)
    return None


def meow_bergen_opener_continuation_policy(ctx, candidates):
    calls = ctx.auction.calls
    if not _is_bergen_continuation(calls):
        return None
    suit = calls[0][1]
    response = calls[2]
    if response == "3C":
        return candidates.get("4" + suit) if ctx.hand.hcp >= 16 else candidates.get("3" + suit)
    if response == "3D":
        return candidates.get("4" + suit) if ctx.hand.hcp >= 14 else candidates.get("3" + suit)
    if response == "3" + suit:
        return candidates.get("4" + suit) if ctx.hand.hcp >= 18 else candidates.get("P")
    return None


def meow_drury_opener_continuation_policy(ctx, candidates):
    calls = ctx.auction.calls
    if not _is_drury_continuation(calls):
        return None
    suit = calls[-4][1]
    return candidates.get("4" + suit) if ctx.hand.hcp >= 14 else candidates.get("2" + suit)


def meow_jacoby_opener_continuation_policy(ctx, candidates):
    calls = ctx.auction.calls
    if not _is_jacoby_opener_continuation(calls):
        return None
    suit = calls[0][1]
    for short_suit in _side_suits(suit):
        if ctx.hand.length(short_suit) <= 1:
            candidate = _candidate_with(candidates, action_type="jacoby_shortness_response", short_suit=short_suit)
            if candidate is not None:
                return candidate
    if ctx.hand.hcp >= 15:
        return _candidate_with(candidates, action_type="jacoby_extras_no_shortness", target_suit=suit)
    return _candidate_with(candidates, action_type="jacoby_minimum_game", target_suit=suit)


def meow_jacoby_responder_placement_policy(ctx, candidates):
    calls = ctx.auction.calls
    if not _is_after_jacoby_opener_answer(calls):
        return None
    suit = calls[0][1]
    rkcb = _candidate_with(candidates, action_type="rkcb_1430")
    if rkcb is not None and ctx.hand.hcp >= 18 and ctx.hand.length(suit) >= 5:
        return rkcb
    return _candidate_with(candidates, action_type="place_contract", target_suit=suit)


def _direct_major_opening_suit(ctx):
    if len(ctx.auction.calls) != 2 or ctx.auction.calls[1] != "P":
        return None
    if ctx.auction.calls[0] not in ("1S", "1H"):
        return None

    opening = _latest_record(ctx, "major_opening")
    if opening is None:
        return None

    suit = opening.attributes.get("target_suit")
    return suit if suit in ("S", "H") else None


def _is_bergen_continuation(calls):
    return (
        len(calls) == 4
        and calls[0] in ("1H", "1S")
        and calls[1] == "P"
        and calls[2] in ("3C", "3D", "3" + calls[0][1])
        and calls[3] == "P"
    )


def _is_drury_continuation(calls):
    if len(calls) < 6 or calls[-1] != "P":
        return False
    opening = calls[-4]
    response = calls[-2]
    return opening in ("1H", "1S") and response in ("2C", "2D")


def _is_jacoby_opener_continuation(calls):
    return (
        len(calls) == 4
        and calls[0] in ("1H", "1S")
        and calls[1] == "P"
        and calls[2] == "2N"
        and calls[3] == "P"
    )


def _is_after_jacoby_opener_answer(calls):
    return (
        len(calls) == 6
        and calls[0] in ("1H", "1S")
        and calls[1] == "P"
        and calls[2] == "2N"
        and calls[3] == "P"
        and calls[4] in ("3C", "3D", "3H", "3S")
        and calls[5] == "P"
    )


def _side_suits(trump_suit):
    return tuple(suit for suit in ("C", "D", "H", "S") if suit != trump_suit)


def _latest_record(ctx, key):
    matches = ctx.state.records_matching(key)
    if not matches:
        return None
    return matches[-1]


def _candidate_with(candidates, **meaning):
    for candidate in candidates:
        candidate_meaning = candidate.public_meaning or {}
        if all(candidate_meaning.get(key) == value for key, value in meaning.items()):
            return candidate
    return None


policy_functions = [
    meow_major_raise_jacoby_policy,
    meow_major_raise_bergen_policy,
    meow_major_raise_simple_policy,
    meow_bergen_opener_continuation_policy,
    meow_drury_opener_continuation_policy,
    meow_jacoby_opener_continuation_policy,
    meow_jacoby_responder_placement_policy,
]
