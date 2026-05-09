def meow_opening_strong_policy(ctx, candidates):
    if not _is_opening_auction(ctx):
        return None
    return _strong_opening(ctx, candidates)


def meow_opening_notrump_policy(ctx, candidates):
    if not _is_opening_auction(ctx):
        return None
    return candidates.get("1N")


def meow_opening_fourth_seat_pass_policy(ctx, candidates):
    if not _is_opening_auction(ctx) or _seat_position(ctx) != 4:
        return None
    if _rule_of_15_allows_opening(ctx):
        return None
    return candidates.get("P")


def meow_opening_one_level_seat_1_2_policy(ctx, candidates):
    if not _is_opening_auction(ctx) or _seat_position(ctx) not in (1, 2):
        return None
    return _one_level_opening(ctx, candidates, require_opening_values=True)


def meow_opening_one_level_seat_3_sound_policy(ctx, candidates):
    if not _is_opening_auction(ctx) or _seat_position(ctx) != 3 or ctx.hand.hcp < 12:
        return None
    return _one_level_opening(ctx, candidates, require_opening_values=False)


def meow_opening_preempt_policy(ctx, candidates):
    if not _is_opening_auction(ctx) or _seat_position(ctx) == 4:
        return None
    return _preemptive_opening(ctx, candidates)


def meow_opening_one_level_seat_3_light_policy(ctx, candidates):
    if not _is_opening_auction(ctx) or _seat_position(ctx) != 3 or ctx.hand.hcp >= 12:
        return None
    return _one_level_opening(ctx, candidates, require_opening_values=False)


def meow_opening_one_level_seat_4_policy(ctx, candidates):
    if not _is_opening_auction(ctx) or _seat_position(ctx) != 4:
        return None
    if not _rule_of_15_allows_opening(ctx):
        return None
    return _one_level_opening(ctx, candidates, require_opening_values=False)


def meow_opening_pass_policy(ctx, candidates):
    if not _is_opening_auction(ctx):
        return None
    return candidates.get("P")


def _is_opening_auction(ctx):
    return len(ctx.auction.calls) <= 3 and all(call == "P" for call in ctx.auction.calls)


def _seat_position(ctx):
    return ctx.environment.get("seat_position")


def _strong_opening(ctx, candidates):
    two_club = candidates.get("2C")
    if two_club is not None and _two_club_opening_values(ctx):
        return two_club
    return candidates.get("2N")


def _two_club_opening_values(ctx):
    if ctx.hand.hcp >= 22 and _notrump_rebid_shape(ctx):
        return True
    longest = max(ctx.hand.length(suit) for suit in "SHDC")
    if ctx.hand.hcp >= 22 and longest >= 5:
        return True
    if ctx.hand.hcp >= 20 and longest >= 7 and any(_good_suit(ctx, suit) for suit in "SHDC" if ctx.hand.length(suit) == longest):
        return True
    return ctx.hand.hcp >= 19 and longest >= 8 and any(_top_honor_count(ctx, suit, ("A", "K", "Q")) >= 2 for suit in "SHDC" if ctx.hand.length(suit) == longest)


def _one_level_opening(ctx, candidates, require_opening_values):
    if require_opening_values and not _has_first_second_seat_opening_values(ctx):
        return None
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
    if not _preempt_shape_allows(ctx, call, suit, seat):
        return False
    hcp = ctx.hand.hcp
    vulnerability = ctx.environment.get("vulnerability_relation")
    good_suit = _good_suit(ctx, suit)
    if call.startswith("3"):
        if seat == 2:
            return hcp >= 7 and good_suit
        if seat == 3:
            return hcp >= 3
        if vulnerability == "unfavorable":
            return hcp >= 6
        if vulnerability == "favorable":
            return hcp >= 4
        return hcp >= 5
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


def _preempt_shape_allows(ctx, call, suit, seat):
    length = ctx.hand.length(suit)
    if call.startswith("2") and length != 6:
        return False
    if call.startswith("3") and length < 7:
        return False
    if seat == 3:
        return True
    if _has_side_void(ctx, suit):
        return False
    if any(ctx.hand.length(other) >= 5 for other in "SHDC" if other != suit):
        return False
    if suit in ("D", "H", "S") and any(ctx.hand.length(other) >= 4 for other in "SH" if other != suit):
        return False
    return True


def _has_side_void(ctx, suit):
    return any(ctx.hand.length(other) == 0 for other in "SHDC" if other != suit)


def _good_suit(ctx, suit):
    return _top_honor_count(ctx, suit, ("A", "K", "Q")) >= 2 or _top_honor_count(ctx, suit, ("A", "K", "Q", "J", "T")) >= 3


def _top_honor_count(ctx, suit, ranks):
    holding = ctx.hand.holding(suit)
    return sum(1 for rank in holding if rank in ranks)


def _rule_of_15_allows_opening(ctx):
    return ctx.hand.hcp + ctx.hand.length("S") >= 15


def _has_first_second_seat_opening_values(ctx):
    if ctx.hand.hcp >= 12:
        return True
    if ctx.hand.hcp < 10:
        return False
    return ctx.hand.hcp + sum(_two_longest_lengths(ctx)) >= 20


def _two_longest_lengths(ctx):
    return sorted((ctx.hand.length(suit) for suit in "SHDC"), reverse=True)[:2]


def _notrump_rebid_shape(ctx):
    lengths = sorted((ctx.hand.length(suit) for suit in "SHDC"), reverse=True)
    return lengths in ([5, 3, 3, 2], [4, 4, 3, 2], [4, 3, 3, 3], [4, 4, 4, 1])


policy_functions = [
    meow_opening_strong_policy,
    meow_opening_notrump_policy,
    meow_opening_fourth_seat_pass_policy,
    meow_opening_one_level_seat_1_2_policy,
    meow_opening_one_level_seat_3_sound_policy,
    meow_opening_preempt_policy,
    meow_opening_one_level_seat_3_light_policy,
    meow_opening_one_level_seat_4_policy,
    meow_opening_pass_policy,
]
