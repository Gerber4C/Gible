# BSL source for Partner bidding agreements.
# Edit this file as the source of truth for this Gadget object set.

Call(
    id="cs_1",
    when=Auction("", seats=[1, 2, 3, 4]),
    bid=Bid("2C"),
    selection=Selection(
        criteria=[
            Criterion("strong_two_club_values", self.hcp >= 22, weight=150),
        ],
    ),
    meaning=Meaning(
        nature=["artificial", "strong", "forcing"],
        acts=["descriptive", "context_initiating"],
        action="strong_two_club_opening",
        target_suit=C,
        hcp_min=22,
        alertable=False,
    ),
    effects=[
        State("strong_two_club_opening", owner="opener", status="active"),
        State("opener.hcp", owner="opener", min_value=22),
        State("force_status", owner="partnership", value="game_forcing"),
    ],
    description="Artificial strong 2C opening, used for 22+ HCP hands in this executable benchmark slice.",
    system_notes="2C opening is artificial, strong, and forcing. The current executable threshold is 22+ HCP.",
)
