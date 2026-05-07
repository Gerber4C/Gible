# BSL source for Partner bidding agreements.
# Edit this file as the source of truth for this Gadget object set.

Call(
    id="cs_2",
    when=Auction("2C P", seats=[1, 2, 3, 4]),
    bid=Bid("2D"),
    selection=Selection(criteria=[Criterion("waiting_available", True, weight=5)]),
    meaning=Meaning(
        nature=["artificial", "waiting"],
        acts=["relay", "forcing"],
        action="strong_two_club_waiting",
        alertable=False,
    ),
    effects=[
        State("strong_two_club_response", owner="responder", response_type="waiting"),
    ],
    description="2D waiting response to strong 2C.",
    system_notes="After 2C, 2D is waiting.",
)

Call(
    id="cs_3",
    when=Auction("2C P", seats=[1, 2, 3, 4]),
    bid=Bid("2H"),
    selection=Selection(
        criteria=[
            Criterion("positive_values", self.hcp >= 7, weight=40),
            Criterion("five_hearts", Length(H) >= 5, weight=50),
            Criterion("good_heart_suit", Honors(H, top=3) >= 2, weight=20),
        ],
    ),
    meaning=Meaning(
        nature=["natural", "positive"],
        acts=["descriptive", "forcing"],
        action="strong_two_club_positive_response",
        target_suit=H,
        shown_length_min=5,
        alertable=False,
    ),
    effects=[
        State("strong_two_club_response", owner="responder", response_type="positive_suit", target_suit=H),
        State("responder.length.H", owner="responder", min_value=5),
        State("responder.hcp", owner="responder", min_value=7),
    ],
    description="Positive natural heart response to strong 2C.",
    system_notes="After 2C, 2H is a positive natural response with a good five-card or longer heart suit.",
)

Call(
    id="cs_4",
    when=Auction("2C P", seats=[1, 2, 3, 4]),
    bid=Bid("2S"),
    selection=Selection(
        criteria=[
            Criterion("positive_values", self.hcp >= 7, weight=40),
            Criterion("five_spades", Length(S) >= 5, weight=50),
            Criterion("good_spade_suit", Honors(S, top=3) >= 2, weight=20),
        ],
    ),
    meaning=Meaning(
        nature=["natural", "positive"],
        acts=["descriptive", "forcing"],
        action="strong_two_club_positive_response",
        target_suit=S,
        shown_length_min=5,
        alertable=False,
    ),
    effects=[
        State("strong_two_club_response", owner="responder", response_type="positive_suit", target_suit=S),
        State("responder.length.S", owner="responder", min_value=5),
        State("responder.hcp", owner="responder", min_value=7),
    ],
    description="Positive natural spade response to strong 2C.",
    system_notes="After 2C, 2S is a positive natural response with a good five-card or longer spade suit.",
)

Call(
    id="cs_5",
    when=Auction("2C P", seats=[1, 2, 3, 4]),
    bid=Bid("3C"),
    selection=Selection(
        criteria=[
            Criterion("positive_values", self.hcp >= 7, weight=40),
            Criterion("five_clubs", Length(C) >= 5, weight=50),
            Criterion("good_club_suit", Honors(C, top=3) >= 2, weight=20),
        ],
    ),
    meaning=Meaning(
        nature=["natural", "positive"],
        acts=["descriptive", "forcing"],
        action="strong_two_club_positive_response",
        target_suit=C,
        shown_length_min=5,
        alertable=False,
    ),
    effects=[
        State("strong_two_club_response", owner="responder", response_type="positive_suit", target_suit=C),
        State("responder.length.C", owner="responder", min_value=5),
        State("responder.hcp", owner="responder", min_value=7),
    ],
    description="Positive natural club response to strong 2C.",
    system_notes="After 2C, 3C is a positive natural response with a good five-card or longer club suit.",
)

Call(
    id="cs_6",
    when=Auction("2C P", seats=[1, 2, 3, 4]),
    bid=Bid("3D"),
    selection=Selection(
        criteria=[
            Criterion("positive_values", self.hcp >= 7, weight=40),
            Criterion("five_diamonds", Length(D) >= 5, weight=50),
            Criterion("good_diamond_suit", Honors(D, top=3) >= 2, weight=20),
        ],
    ),
    meaning=Meaning(
        nature=["natural", "positive"],
        acts=["descriptive", "forcing"],
        action="strong_two_club_positive_response",
        target_suit=D,
        shown_length_min=5,
        alertable=False,
    ),
    effects=[
        State("strong_two_club_response", owner="responder", response_type="positive_suit", target_suit=D),
        State("responder.length.D", owner="responder", min_value=5),
        State("responder.hcp", owner="responder", min_value=7),
    ],
    description="Positive natural diamond response to strong 2C.",
    system_notes="After 2C, 3D is a positive natural response with a good five-card or longer diamond suit.",
)
