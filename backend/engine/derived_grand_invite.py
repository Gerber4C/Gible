"""Rule-based grand-slam invitations after a two-suit keycard answer.

The two-suit keycard already knows both trumps and both minor kings.  A grand
invitation therefore only has to reason about the remaining side kings.  The
mechanism is intentionally expressed in terms of suits and bid rank, not in
terms of one auction string:

* hold a lower side king -> skip it and invite in a higher side suit;
* lack a side king -> invite in that suit;
* after an invitation, the invited king accepts, a higher king counter-invites,
  and a skipped lower king is ignored;
* seven of the lower trump is pass-or-correct.

`Invitation` and `Response` are public facts.  The caller owns the keycard
state record; this module only decides which calls the rules make available.
"""

from __future__ import annotations

from dataclasses import dataclass

from .rkcb_continuation import bid_rank

# Answers that already establish at least one queen and therefore allow the
# asker to consider a grand.  Five of the agreed minor (5C) and the 5D answer
# still need the queen ask first.
GRAND_READY_ANSWERS = frozenset({'5S', '5N', '6C', '6H', '6S', '6N'})


@dataclass(frozen=True)
class Invitation:
    call: str
    kind: str  # 'five_notrump' or 'six_level'
    suit: str | None
    skipped_kings: tuple[str, ...]
    unintentionally_skipped_kings: tuple[str, ...]
    score: int


@dataclass(frozen=True)
class Response:
    call: str
    kind: str  # 'accept', 'k_answer', 'signoff'
    control_suit: str | None = None


def side_suits(low_suit: str, high_suit: str) -> tuple[str, ...]:
    return tuple(suit for suit in 'CDHS' if suit not in (low_suit, high_suit))


def invitation_candidates(hand, answer_call: str, low_suit: str, high_suit: str,
                          allowed, *, allow_five_notrump: bool = True
                          ) -> tuple[Invitation, ...]:
    """Derive the asker's grand invitations from the hand's side kings.

    A six-level invitation is useful only when the asker lacks that suit's
    king.  Side kings below the invitation that the asker already holds are
    deliberately skipped; lower side kings the asker lacks are *unintentionally*
    skipped and must not be shown by responder.
    """
    if hand is None or answer_call not in GRAND_READY_ANSWERS:
        return ()
    sides = side_suits(low_suit, high_suit)

    # After the 5S answer the first step is the generic 5NT grand invitation.
    # A direct six-level invitation is used only once that step has narrowed
    # which side king is still missing.  This invitation stays available even
    # when the asker already holds both side kings: responder's no-king reply
    # can still be converted to seven of a trump by the asker.
    if answer_call == '5S':
        if allow_five_notrump and '5N' in allowed:
            return (Invitation('5N', 'five_notrump', None, (), (), 6),)
        return ()

    held = {suit for suit in sides if hand.contains_rank(suit, 'K')}
    if len(held) == len(sides):
        return ()

    result: list[Invitation] = []
    for suit in sides:
        if suit in held:
            continue
        call = '6' + suit
        if call not in allowed:
            continue
        lower = [other for other in sides
                 if bid_rank('6' + other) < bid_rank(call)]
        skipped = tuple(other for other in lower if other in held)
        unintentional = tuple(other for other in lower if other not in held)
        score = 6 if call == '6H' else 5
        result.append(Invitation(call, 'six_level', suit, skipped,
                                 unintentional, score))
    return tuple(result)


def response_candidates(hand, invitation: Invitation, low_suit: str,
                        high_suit: str, allowed, *,
                        prefer_accept_when_ready: bool = False
                        ) -> tuple[Response, ...]:
    """Derive responder's K answer, counter-invite, signoff, or grand accept."""
    if hand is None:
        return ()
    sides = side_suits(low_suit, high_suit)
    held = {suit for suit in sides if hand.contains_rank(suit, 'K')}

    if invitation.kind == 'five_notrump':
        if held == set(sides):
            result = []
            if '7C' in allowed:
                result.append(Response('7C', 'accept'))
            if not prefer_accept_when_ready:
                result.append(Response('6H', 'k_answer', 'H'))
            return tuple(result)
        if 'H' in held:
            return (Response('6H', 'k_answer', 'H'),) if '6H' in allowed else ()
        if 'S' in held:
            return (Response('6S', 'k_answer', 'S'),) if '6S' in allowed else ()
        no_king = '6C' if '6C' in allowed else '6N'
        return (Response(no_king, 'signoff'),) if no_king in allowed else ()

    suit = invitation.suit
    if suit in held:
        return (Response('7C', 'accept'),) if '7C' in allowed else ()
    higher = [other for other in sides
              if bid_rank('6' + other) > bid_rank(invitation.call)
              and other in held]
    if higher:
        call = '6' + min(higher, key=lambda item: bid_rank('6' + item))
        return (Response(call, 'k_answer', call[1]),) if call in allowed else ()
    if '6N' in allowed:
        return (Response('6N', 'signoff'),)
    return ()


def invitation_meaning(invitation: Invitation, low_suit: str,
                       high_suit: str) -> dict:
    return {
        'nature_labels': ['artificial'],
        'call_act_types': ['invite', 'slam_try'],
        'action_type': 'two_suit_keycard_grand_invitation',
        'target_suit': low_suit,
        'suits': [low_suit, high_suit],
        'invitation_kind': invitation.kind,
        'invitation_suit': invitation.suit,
        'skipped_kings': list(invitation.skipped_kings),
        'unintentionally_skipped_kings': list(
            invitation.unintentionally_skipped_kings),
    }


def response_meaning(response: Response, invitation: Invitation,
                     low_suit: str, high_suit: str) -> dict:
    if response.kind == 'accept':
        return {
            'nature_labels': ['natural'],
            'call_act_types': ['signoff', 'final_placement', 'grand_accept'],
            'action_type': 'two_suit_keycard_grand_accept',
            'target_suit': low_suit,
            'agreed_suit': low_suit,
            'pass_or_correct': 'pure',
            'control_suit': invitation.suit,
            'purpose_completed': True,
        }
    if response.kind == 'k_answer':
        return {
            'nature_labels': ['artificial'],
            'call_act_types': ['descriptive', 'control_showing', 'slam_try',
                               'invite'],
            'action_type': 'two_suit_keycard_grand_k_answer',
            'target_suit': low_suit,
            'suits': [low_suit, high_suit],
            'control_suit': response.control_suit,
            'invitation_call': invitation.call,
            'skipped_kings': list(invitation.skipped_kings),
        }
    target = 'N' if response.call == '6N' else low_suit
    return {
        'nature_labels': ['natural'],
        'call_act_types': ['signoff', 'final_placement', 'invite_minus'],
        'action_type': 'two_suit_keycard_grand_signoff',
        'target_suit': target,
        'suits': [low_suit, high_suit],
        'purpose_completed': True,
    }


def response_score(response: Response) -> int:
    return {'accept': 7, 'k_answer': 5, 'signoff': 4}[response.kind]
