# BSL source for Partner bidding agreements.
# Edit this file as the source of truth for this Gadget object set.

Call(
    id="cs_7",
    when=Auction("2C P 2D P", seats=[1, 2, 3, 4]),
    bid=Bid("2N"),
    selection=Selection(
        criteria=[
            Criterion("hcp_22_24", 22 <= self.hcp <= 24, weight=70),
            Criterion("balanced_shape", self.balanced == True, weight=60),
        ],
    ),
    meaning=Meaning(
        nature=["natural"],
        acts=["descriptive", "context_initiating"],
        action="strong_two_club_notrump_rebid",
        target_suit=N,
        hcp_min=22,
        hcp_max=24,
        shape_class="balanced",
        alertable=False,
    ),
    effects=[
        State("notrump_opening", owner="opener", target_suit=N, hcp_min=22, hcp_max=24, shape_class="balanced"),
        State("notrump_focus", status="active"),
        State("opener.hcp", owner="opener", min_value=22, max_value=24),
    ],
    description="After 2C-2D, opener rebids 2N with 22-24 balanced.",
    system_notes="After 2C-2D, opener's 2N rebid shows 22-24 balanced. Notrump continuations are intended to be system-on.",
)

Call(
    id="cs_8",
    when=Auction("2C P 2D P", seats=[1, 2, 3, 4]),
    bid=Bid("2H"),
    selection=Selection(
        criteria=[
            Criterion("strong_values", self.hcp >= 22, weight=40),
            Criterion("five_hearts", Length(H) >= 5, weight=60),
        ],
    ),
    meaning=Meaning(
        nature=["natural", "forcing"],
        acts=["descriptive", "forcing"],
        action="strong_two_club_suit_rebid",
        target_suit=H,
        shown_length_min=5,
        alertable=False,
    ),
    effects=[
        State("strong_two_club_rebid", owner="opener", target_suit=H),
        State("opener.length.H", owner="opener", min_value=5),
    ],
    description="After 2C-2D, opener rebids 2H naturally with a strong heart hand.",
    system_notes="After 2C-2D, 2H is natural and forcing.",
)

Call(
    id="cs_9",
    when=Auction("2C P 2D P", seats=[1, 2, 3, 4]),
    bid=Bid("2S"),
    selection=Selection(
        criteria=[
            Criterion("strong_values", self.hcp >= 22, weight=40),
            Criterion("five_spades", Length(S) >= 5, weight=60),
        ],
    ),
    meaning=Meaning(
        nature=["natural", "forcing"],
        acts=["descriptive", "forcing"],
        action="strong_two_club_suit_rebid",
        target_suit=S,
        shown_length_min=5,
        alertable=False,
    ),
    effects=[
        State("strong_two_club_rebid", owner="opener", target_suit=S),
        State("opener.length.S", owner="opener", min_value=5),
    ],
    description="After 2C-2D, opener rebids 2S naturally with a strong spade hand.",
    system_notes="After 2C-2D, 2S is natural and forcing.",
)

Call(
    id="cs_10",
    when=Auction("2C P 2D P", seats=[1, 2, 3, 4]),
    bid=Bid("3C"),
    selection=Selection(
        criteria=[
            Criterion("strong_values", self.hcp >= 22, weight=40),
            Criterion("five_clubs", Length(C) >= 5, weight=60),
        ],
    ),
    meaning=Meaning(
        nature=["natural", "forcing"],
        acts=["descriptive", "forcing"],
        action="strong_two_club_suit_rebid",
        target_suit=C,
        shown_length_min=5,
        alertable=False,
    ),
    effects=[
        State("strong_two_club_rebid", owner="opener", target_suit=C),
        State("opener.length.C", owner="opener", min_value=5),
    ],
    description="After 2C-2D, opener rebids 3C naturally with a strong club hand.",
    system_notes="After 2C-2D, 3C is natural and forcing.",
)

Call(
    id="cs_11",
    when=Auction("2C P 2D P", seats=[1, 2, 3, 4]),
    bid=Bid("3D"),
    selection=Selection(
        criteria=[
            Criterion("strong_values", self.hcp >= 22, weight=40),
            Criterion("five_diamonds", Length(D) >= 5, weight=60),
        ],
    ),
    meaning=Meaning(
        nature=["natural", "forcing"],
        acts=["descriptive", "forcing"],
        action="strong_two_club_suit_rebid",
        target_suit=D,
        shown_length_min=5,
        alertable=False,
    ),
    effects=[
        State("strong_two_club_rebid", owner="opener", target_suit=D),
        State("opener.length.D", owner="opener", min_value=5),
    ],
    description="After 2C-2D, opener rebids 3D naturally with a strong diamond hand.",
    system_notes="After 2C-2D, 3D is natural and forcing.",
)

Call(
    id="cs_12",
    when=Auction("2C P 2D P 2H P", seats=[1, 2, 3, 4]),
    bid=Bid("3C"),
    selection=Selection(criteria=[Criterion("second_negative_values", self.hcp <= 3, weight=80)]),
    meaning=Meaning(
        nature=["artificial", "negative"],
        acts=["descriptive"],
        action="strong_two_club_second_negative",
        alertable=False,
    ),
    effects=[
        State("strong_two_club_second_negative", owner="responder"),
        State("responder.hcp", owner="responder", max_value=3),
    ],
    description="Second negative after 2C-2D-2H.",
    system_notes="After 2C-2D and opener's 2H rebid, 3C is the second negative.",
)

Call(
    id="cs_13",
    when=Auction("2C P 2D P 2S P", seats=[1, 2, 3, 4]),
    bid=Bid("3C"),
    selection=Selection(criteria=[Criterion("second_negative_values", self.hcp <= 3, weight=80)]),
    meaning=Meaning(
        nature=["artificial", "negative"],
        acts=["descriptive"],
        action="strong_two_club_second_negative",
        alertable=False,
    ),
    effects=[
        State("strong_two_club_second_negative", owner="responder"),
        State("responder.hcp", owner="responder", max_value=3),
    ],
    description="Second negative after 2C-2D-2S.",
    system_notes="After 2C-2D and opener's 2S rebid, 3C is the second negative.",
)

Call(
    id="cs_14",
    when=Auction("2C P 2D P 3C P", seats=[1, 2, 3, 4]),
    bid=Bid("3D"),
    selection=Selection(criteria=[Criterion("second_negative_values", self.hcp <= 3, weight=80)]),
    meaning=Meaning(
        nature=["artificial", "negative"],
        acts=["descriptive"],
        action="strong_two_club_second_negative",
        alertable=False,
    ),
    effects=[
        State("strong_two_club_second_negative", owner="responder"),
        State("responder.hcp", owner="responder", max_value=3),
    ],
    description="Second negative after 2C-2D-3C.",
    system_notes="After 2C-2D and opener's 3C rebid, 3D is the second negative.",
)
