# BSL source for Partner bidding agreements.
# Edit this file as the source of truth for this Gadget object set.


def cs_1_applies(ctx):
    return True
Call(
    id='cs_1',
    when=Auction(''),
    bid=Bid('4N'),
    applies=cs_1_applies,
    meaning=Meaning(nature=['artificial'], acts=['inquiry'], action='test_meaning_a', alertable=False),
    description='Test 4N meaning A.',
)


def cs_2_applies(ctx):
    return True
Call(
    id='cs_2',
    when=Auction(''),
    bid=Bid('4N'),
    applies=cs_2_applies,
    meaning=Meaning(nature=['natural'], acts=['invitation'], action='test_meaning_b', alertable=False),
    description='Test 4N meaning B.',
)
