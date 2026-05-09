def meow_game_try_route(ctx, candidates):
    agreed = _latest_record(ctx, "agreed_suit")
    if agreed is None:
        return None

    suit = agreed.attributes.get("suit")
    if suit not in ("S", "H"):
        return None

    accepted = _latest_record(ctx, "game_try_response")
    if accepted is not None and accepted.attributes.get("agreed_suit") == suit:
        return _candidate_with(candidates, action_type="accept_game_try", target_suit=suit)

    pending = _latest_record(ctx, "game_try")
    if pending is not None and pending.attributes.get("agreed_suit") == suit:
        target = pending.attributes.get("target_suit")
        if target is not None:
            return _candidate_with(candidates, action_type="game_try_response", target_suit=target)
        return _candidate_with(candidates, action_type="game_try_response", agreed_suit=suit)

    if ctx.hand.hcp < 14 or ctx.hand.hcp >= 18:
        return None

    if suit == "H":
        if _lacks_top_honor(ctx, "H"):
            return _candidate_with(candidates, action_type="trump_help_game_try", target_suit="H")
        return _candidate_with(candidates, action_type="help_suit_game_try", agreed_suit="H", ask_scope="any_help")

    if _diamond_help_style(ctx):
        candidate = _candidate_with(candidates, action_type="help_suit_game_try", target_suit="D", agreed_suit="S")
        if candidate is not None:
            return candidate
    if _lacks_top_honor(ctx, "S"):
        return _candidate_with(candidates, action_type="trump_help_game_try", target_suit="S")
    return _candidate_with(candidates, action_type="help_suit_game_try", agreed_suit="S", ask_scope="any_help")


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


def _lacks_top_honor(ctx, suit):
    return ctx.hand.honor_count(suit, ("A", "K", "Q")) == 0


def _diamond_help_style(ctx):
    return ctx.hand.length("D") >= 3 and ctx.hand.contains_rank("D", "Q")


policy_functions = [meow_game_try_route]

