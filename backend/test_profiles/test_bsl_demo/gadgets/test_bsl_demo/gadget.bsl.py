Gadget(
    id="test_bsl_demo",
    namespace="test",
    name="Test BSL Demo",
    version="0.1.0",
    author=Author("Partner Prototype"),
    description="Small gadget authored in restricted Python-shaped BSL.",
    system_notes="Demo gadget used to validate dataclass-style BSL loading.",
)


def cs_1_applies(ctx):
    return True
Call(
    id="cs_1",
    when=Auction("", seats=[1, 2, 3, 4]),
    bid=Bid("1S"),
    applies=cs_1_applies,
    meaning=Meaning(
        nature=["natural"],
        acts=["descriptive", "context_initiating"],
        action="opening",
        target_suit="S",
        shown_length_min=5,
        alertable=False,
    ),
    effects=[
        Update("major_opening", actor_role="opener", target_suit="S", shown_length_min=5),
        State("opener.length.S", owner="opener", min_value=5, source="bsl_demo"),
    ],
    description="Open 1S with opening values and at least five spades.",
    system_notes="1S opening is natural and shows at least five spades.",
)
