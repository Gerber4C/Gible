# Human-Readable Test Cases

This document is the readable companion to the YAML fixtures in `backend/tests/cases/`. When a fixture changes, update this document in the same checkpoint.

Unless a case says otherwise, the environment is dealer `n`, vulnerability `none`, and scoring `IMP`.

Current fixture coverage: 118 total cases across bidding decisions, full-auction simulations, legality, hand parsing, and matcher behavior.

## Single-Call Bidding Cases

### Expert 2/1 Starter Convention Set

- `transfer_to_hearts_superaccept_is_selected`
  - Auction: `1N P 2D P`
  - Hand to bid: ♠ AQ74 ♥ KJ83 ♦ A62 ♣ Q5
  - Expected call: `3H`
  - Expected origin: `four_way_jacoby_transfer`, Call Specification `cs_3`
  - Expected comparison: `3H` beats `2H`
  - Expected replay facts: `notrump_opening`, `transfer`
  - Expected selected criterion: `pending_heart_transfer`

- `transfer_to_hearts_normal_completion_is_selected`
  - Auction: `1N P 2D P`
  - Hand to bid: ♠ AKQ ♥ 83 ♦ Q762 ♣ KJ54
  - Expected call: `2H`
  - Expected origin: Call Specification `cs_2`
  - Expected replay facts: `notrump_opening`, `transfer`

- `responder_uses_2d_transfer_with_five_hearts`
  - Auction: `1N P`
  - Hand to bid: ♠ 74 ♥ KJ832 ♦ A762 ♣ Q5
  - Expected call: `2D`
  - Expected origin: `four_way_jacoby_transfer`, Call Specification `cs_1`
  - Expected selected criterion: `jacoby_transfer_heart_length`

- `notrump_opening_seat_1`
  - Auction: empty
  - Hand to bid: ♠ AQ7 ♥ KJ8 ♦ A762 ♣ Q54
  - Expected call: `1N`
  - Expected origin: Call Specification `cs_1`

- `notrump_opening_seat_2`
  - Auction: `P`
  - Hand to bid: ♠ AQ7 ♥ KJ8 ♦ A762 ♣ Q54
  - Expected call: `1N`
  - Expected origin: Call Specification `cs_1`

- `notrump_opening_seat_3`
  - Auction: `P P`
  - Hand to bid: ♠ AQ7 ♥ KJ8 ♦ A762 ♣ Q54
  - Expected call: `1N`
  - Expected origin: Call Specification `cs_1`

- `notrump_opening_seat_4`
  - Auction: `P P P`
  - Hand to bid: ♠ AQ7 ♥ KJ8 ♦ A762 ♣ Q54
  - Expected call: `1N`
  - Expected origin: Call Specification `cs_1`

- `notrump_2n_opening`
  - Auction: empty
  - Hand to bid: ♠ AK7 ♥ KJ8 ♦ AQ76 ♣ K54
  - Expected call: `2N`
  - Expected origin: Call Specification `cs_2`

- `one_heart_opening_seat_1_2`
  - Auction: empty
  - Hand to bid: ♠ K2 ♥ AKQ87 ♦ 765 ♣ 432
  - Expected call: `1H`
  - Expected origin: Call Specification `cs_3`

- `one_spade_opening_seat_1_2`
  - Auction: empty
  - Hand to bid: ♠ AKQ87 ♥ 32 ♦ 765 ♣ K32
  - Expected call: `1S`
  - Expected origin: Call Specification `cs_4`

- `one_club_opening_seat_1_2`
  - Auction: empty
  - Hand to bid: ♠ A32 ♥ KQ7 ♦ 865 ♣ K432
  - Expected call: `1C`
  - Expected origin: Call Specification `cs_5`

- `one_diamond_opening_seat_1_2`
  - Auction: empty
  - Hand to bid: ♠ A432 ♥ KQ7 ♦ K432 ♣ 65
  - Expected call: `1D`
  - Expected origin: Call Specification `cs_6`

- `one_major_placeholder_seat_3_4`
  - Auction: `P P`
  - Hand to bid: ♠ 432 ♥ 8765 ♦ 765 ♣ 432
  - Environment override: `enable_placeholder_openings: true`
  - Expected call: `1H`
  - Expected origin: Call Specification `cs_7`

- `one_minor_placeholder_seat_3_4`
  - Auction: `P P P`
  - Hand to bid: ♠ 432 ♥ 876 ♦ 7654 ♣ 432
  - Environment override: `enable_placeholder_openings: true`
  - Expected call: `1C`
  - Expected origin: Call Specification `cs_8`

- `strong_two_club_opening`
  - Auction: empty
  - Hand to bid: ♠ AKQ ♥ AKQ ♦ AKQ7 ♣ 543
  - Expected call: `2C`
  - Expected origin: Call Specification `cs_9`

- `weak_two_diamond_opening`
  - Auction: empty
  - Hand to bid: ♠ J32 ♥ 87 ♦ KQ9876 ♣ 54
  - Expected call: `2D`
  - Expected origin: Call Specification `cs_10`

- `weak_two_heart_opening`
  - Auction: empty
  - Hand to bid: ♠ J32 ♥ KQ9876 ♦ 87 ♣ 54
  - Expected call: `2H`
  - Expected origin: Call Specification `cs_11`

- `weak_two_spade_opening`
  - Auction: empty
  - Hand to bid: ♠ KQ9876 ♥ J32 ♦ 87 ♣ 54
  - Expected call: `2S`
  - Expected origin: Call Specification `cs_12`

- `notrump_response_expands_by_seat_position`
  - Auction: `P P 1N P`
  - Hand to bid: ♠ 74 ♥ KJ832 ♦ A762 ♣ Q5
  - Expected call: `2D`
  - Expected origin: Call Specification `cs_1`

- `notrump_continuation_expands_by_seat_position`
  - Auction: `P P 1N P 2D P`
  - Hand to bid: ♠ AQ74 ♥ KJ83 ♦ A62 ♣ Q5
  - Expected call: `3H`
  - Expected replay facts: `notrump_opening`, `transfer`

- `responder_does_not_use_2d_transfer_with_four_hearts`
  - Auction: `1N P`
  - Hand to bid: ♠ A74 ♥ KJ83 ♦ A762 ♣ Q5
  - Expected call: `P`
  - Expected diagnostic includes: `defaulting to P`

- `unmatched_auction_defaults_to_pass`
  - Auction: `1C P 1D`
  - Hand to bid: ♠ A74 ♥ KJ83 ♦ A762 ♣ Q5
  - Expected call: `P`
  - Expected algorithm: `default_policy`
  - Expected diagnostics include: `Undefined prior call 1D`, `defaulting to P`

### Meow 2/1 Benchmark Convention Set

- `meow_opening_policy_prefers_1n_over_five_spades`
  - Auction: empty
  - Hand to bid: ♠ AQJ87 ♥ K2 ♦ A76 ♣ Q54
  - Expected call: `1N`
  - Expected origin: `meow_one_notrump_opening`, Call Specification `cs_1`
  - Expected comparison: `1N` beats `1S`
  - Expected policy: `policy_1`, `ordered_condition`, fallback `highest_score`
  - Bridge sense: This hand is 15-17 balanced, so the opening policy prefers 1N even though a natural 1S opening is also eligible.

- `meow_opening_policy_prefers_1n_over_five_hearts`
  - Auction: empty
  - Hand to bid: ♠ K2 ♥ AQJ87 ♦ A76 ♣ Q54
  - Expected call: `1N`
  - Expected origin: `meow_one_notrump_opening`, Call Specification `cs_1`
  - Expected comparison: `1N` beats `1H`
  - Expected policy: `policy_1`, `ordered_condition`, fallback `highest_score`
  - Bridge sense: This hand is 15-17 balanced, so the opening policy prefers 1N over a five-card heart opening.

- `meow_opening_policy_prefers_spades_with_five_five_majors`
  - Auction: empty
  - Hand to bid: ♠ KQJ87 ♥ QJ984 ♦ A6 ♣ 2
  - Expected call: `1S`
  - Expected origin: `meow_two_over_one_core`, Call Specification `cs_1`
  - Expected comparison: `1S` beats `1H`
  - Expected policy: `policy_1`, `ordered_condition`, fallback `highest_score`
  - Bridge sense: This hand is not a 1N opening. Both majors are eligible, and the opening policy chooses spades first with 5-5 majors.

- `meow_club_transfer_gap_superaccept`
  - Auction: `1N P 2S P`
  - Hand to bid: ♠ A54 ♥ KQ2 ♦ K83 ♣ QJ76
  - Expected call: `2N`
  - Expected origin: `meow_four_way_transfers_over_1n`, Call Specification `cs_5`
  - Expected selected criterion: `honor_third_club_support`

- `meow_club_transfer_normal_accept_without_honor_third`
  - Auction: `1N P 2S P`
  - Hand to bid: ♠ A54 ♥ KQ2 ♦ AK3 ♣ 8764
  - Expected call: `3C`
  - Expected origin: `meow_four_way_transfers_over_1n`, Call Specification `cs_6`

- `meow_diamond_transfer_gap_superaccept`
  - Auction: `1N P 2N P`
  - Hand to bid: ♠ A54 ♥ KQ2 ♦ K83 ♣ QJ76
  - Expected call: `3C`
  - Expected origin: `meow_four_way_transfers_over_1n`, Call Specification `cs_8`
  - Expected selected criterion: `honor_third_diamond_support`

- `meow_heart_transfer_superaccept_selected`
  - Auction: `1N P 2D P`
  - Hand to bid: ♠ AQ74 ♥ KJ83 ♦ A62 ♣ Q5
  - Expected call: `3H`
  - Expected origin: `meow_four_way_transfers_over_1n`, Call Specification `cs_11`
  - Expected comparison: `3H` beats `2H`
  - Expected selected criteria: pending heart transfer, four-card heart support, maximum notrump values
  - Bridge sense: Opener has four hearts and a maximum-style notrump hand, so opener superaccepts the heart transfer instead of merely completing at `2H`.

- `meow_slam_heart_transfer_plan_enters_with_2d`
  - Auction: `1N P`
  - Hand to bid: ♠ A2 ♥ AKQJ87 ♦ 53 ♣ KQ2
  - Expected call: `2D`
  - Public expected origin: `meow_four_way_transfers_over_1n`, Call Specification `cs_1`
  - Internal expected plan origin: `meow_four_way_transfers_over_1n`, Bidding Plan `plan_2`
  - Expected comparison: `2D` beats `4D` and `2C`
  - Bridge sense: The public call is still a heart transfer, but internally the bot chooses the strong transfer-slam plan rather than treating `2D` as only a local heart-length bid.

- `meow_rkcb_after_heart_transfer_superaccept_with_five_hearts`
  - Auction: `1N P 2D P 3H P`
  - Hand to bid: ♠ A2 ♥ AKQJ8 ♦ A3 ♣ KQ32
  - Expected call: `4N`
  - Public expected origin: `meow_rkcb_1430`, Call Specification `cs_1`
  - Expected replay facts: `notrump_opening`, `notrump_focus`, `transfer`, `transfer_superaccept`, `agreed_suit`
  - Expected protocol frame: major transfer active at `responder_continuation`
  - Expected plan state: `plan_2` active at `make_1`
  - Bridge sense: The superaccept sets hearts as agreed. With only five hearts, the specialized six-heart slam tools are not eligible, so standalone RKCB supplies the public meaning of `4N`.

- `meow_control_bid_after_heart_superaccept_precedes_keycard`
  - Auction: `1N P 2D P 3H P`
  - Hand to bid: ♠ A2 ♥ AKQJ87 ♦ A3 ♣ KQ2
  - Expected call: `4D`
  - Expected origin: `meow_control_bidding`, Call Specification `cs_1`
  - Expected comparison: `4D` beats `4N`
  - Bridge sense: With hearts agreed, strong values, and diamond control, responder cooperates below keycard before asking.

- `meow_kickback_selected_when_heart_slam_hand_lacks_diamond_control`
  - Auction: `1N P 2D P 3H P`
  - Hand to bid: ♠ A2 ♥ AKQJ87 ♦ 53 ♣ KQ2
  - Expected call: `4S`
  - Expected origin: `meow_kickback_keycard`, Call Specification `cs_1`
  - Expected comparison: `4S` beats `4N`
  - Bridge sense: With hearts agreed and no diamond control to show, the safer keycard route is Kickback instead of ordinary `4N`.

- `meow_kickback_response_uses_semantic_keycard_context`
  - Auction: `1N P 2D P 3H P 4S P`
  - Hand to bid: ♠ AQ74 ♥ KJ83 ♦ A62 ♣ Q5
  - Expected call: `5C`
  - Expected origin: `meow_kickback_keycard`, Call Specification `cs_3`
  - Expected replay facts include `keycard_context`
  - Bridge sense: The response is selected from the active Kickback frame, not from the literal auction string alone.

- `meow_exclusion_keycard_selected_with_diamond_void`
  - Auction: `1N P 2D P 3H P`
  - Hand to bid: ♠ A2 ♥ AKQJ87 ♦ - ♣ KQJ24
  - Expected call: `5D`
  - Expected origin: `meow_exclusion_keycard`, Call Specification `cs_1`
  - Expected comparison: `5D` beats `4D` and `4N`
  - Bridge sense: The diamond void makes the exclusion ask more specific than a normal control bid or ordinary keycard ask.

- `meow_exclusion_response_counts_keycards_outside_void_suit`
  - Auction: `1N P 2D P 3H P 5D P`
  - Hand to bid: ♠ AQ74 ♥ KJ83 ♦ A62 ♣ Q5
  - Expected call: `5N`
  - Expected origin: `meow_exclusion_keycard`, Call Specification `cs_4`
  - Bridge sense: The response counts heart keycards while ignoring the diamond ace, then denies the heart queen.

- `meow_gerber_selected_over_notrump_focus`
  - Auction: `1N P`
  - Hand to bid: ♠ AQ7 ♥ KQ8 ♦ KQ6 ♣ AJ42
  - Expected call: `4C`
  - Expected origin: `meow_gerber_over_notrump`, Call Specification `cs_1`
  - Expected comparison: `4C` beats `3C`
  - Bridge sense: With notrump focus and no agreed suit, `4C` is an ace ask rather than a club call.

- `meow_gerber_response_counts_aces`
  - Auction: `1N P 4C P`
  - Hand to bid: ♠ A54 ♥ KQ2 ♦ K83 ♣ QJ76
  - Expected call: `4H`
  - Expected origin: `meow_gerber_over_notrump`, Call Specification `cs_3`
  - Bridge sense: The new `ace_count` expression operator lets Gerber responses be computed rather than hard-coded by prose.

- `meow_minorwood_selected_after_diamond_transfer_superaccept`
  - Auction: `1N P 2N P 3C P`
  - Hand to bid: ♠ 2 ♥ 84 ♦ AQJ987 ♣ KQ32
  - Expected call: `4D`
  - Expected origin: `meow_minorwood_keycard`, Call Specification `cs_1`
  - Bridge sense: The diamond-transfer superaccept creates `agreed_suit: D`, which standalone Minorwood consumes.

- `meow_minorwood_response_uses_diamond_keycards`
  - Auction: `1N P 2N P 3C P 4D P`
  - Hand to bid: ♠ A54 ♥ KQ2 ♦ K83 ♣ QJ76
  - Expected call: `4N`
  - Expected origin: `meow_minorwood_keycard`, Call Specification `cs_4`
  - Bridge sense: The response counts diamond keycards and denies the diamond queen.

- `meow_targeted_diamond_king_ask_after_heart_rkcb`
  - Auction: `1N P 2D P 3H P 4N P 5D P`
  - Hand to bid: ♠ A2 ♥ AKQJ87 ♦ 53 ♣ KQ2
  - Expected call: `5N`
  - Expected origin: `meow_targeted_king_ask`, Call Specification `cs_1`
  - Bridge sense: After a heart RKCB answer, asker can ask for one named king as a separate follow-up Protocol Frame.

- `meow_targeted_diamond_king_response`
  - Auction: `1N P 2D P 3H P 4N P 5D P 5N P`
  - Hand to bid: ♠ A54 ♥ KQ2 ♦ K83 ♣ QJ76
  - Expected call: `6D`
  - Expected origin: `meow_targeted_king_ask`, Call Specification `cs_2`

- `meow_targeted_diamond_king_route_places_grand`
  - Auction: `1N P 2D P 3H P 4N P 5D P 5N P 6D P`
  - Hand to bid: ♠ A2 ♥ AKQJ87 ♦ 53 ♣ KQ2
  - Expected call: `7H`
  - Expected origin: `meow_targeted_king_ask`, Call Specification `cs_3`
  - Bridge sense: The targeted response writes formal state, and final placement reads that state.

- `meow_rkcb_frame_opens_after_transfer_slam_plan_4n`
  - Auction: `1N P 2D P 3H P 4N P`
  - Hand to bid: ♠ AQ74 ♥ KJ83 ♦ A62 ♣ Q5
  - Expected call: `5D`
  - Expected origin: `meow_rkcb_1430`, Call Specification `cs_3`
  - Expected replay facts: `notrump_opening`, `notrump_focus`, `transfer`, `transfer_superaccept`, `agreed_suit`, `keycard_context`
  - Expected protocol frames: major-transfer frame still active; RKCB 1430 frame active at `keycard_response`
  - Bridge sense: After `4N` is replayed as RKCB, the engine opens the RKCB protocol frame and opener answers 0 or 3 keycards with `5D`.

- `meow_weak_heart_transfer_plan_passes_completion`
  - Auction: `1N P 2D P 2H P`
  - Hand to bid: ♠ 74 ♥ 98765 ♦ 762 ♣ Q54
  - Expected call: `P`
  - Expected origin: `meow_four_way_transfers_over_1n`, Bidding Plan `plan_1`
  - Expected replay facts: `notrump_opening`, `notrump_focus`, `transfer`, `transfer_completion`
  - Expected protocol frame: `frame_1` is active at `responder_continuation`
  - Expected plan state: `plan_1` is active at `make_1`
  - Bridge sense: Responder started a weak transfer-signoff plan, opener completed the transfer, and the plan now generates the pass that places the contract in hearts.

- `meow_stayman_two_notrump_invitational_alertable`
  - Auction: `1N P 2C P 2D P`
  - Hand to bid: ♠ K874 ♥ 92 ♦ Q83 ♣ K762
  - Expected call: `2N`
  - Expected origin: `meow_regular_stayman_over_1n`, Call Specification `cs_3`
  - Expected public meaning: alertable

- `meow_puppet_stayman_over_1n_is_standalone`
  - Auction: `1N P`
  - Hand to bid: ♠ 82 ♥ 93 ♦ AQJ4 ♣ KQJ76
  - Expected call: `3C`
  - Expected origin: `meow_puppet_stayman_over_1n`, Call Specification `cs_1`

- `meow_puppet_stayman_over_2n_is_standalone`
  - Auction: `2N P`
  - Hand to bid: ♠ 82 ♥ 93 ♦ AQJ4 ♣ KQJ76
  - Expected call: `3C`
  - Expected origin: `meow_puppet_stayman_over_2n`, Call Specification `cs_1`

- `meow_rkcb_after_texas_is_standalone`
  - Auction: `1N P 4H P 4S P`
  - Hand to bid: ♠ KQJT98 ♥ A43 ♦ A2 ♣ AK
  - Expected call: `4N`
  - Expected origin: `meow_rkcb_1430`, Call Specification `cs_1`
  - Expected replay facts: `notrump_opening`, `notrump_focus`, `texas_transfer`, `texas_transfer`, `agreed_suit`

- `meow_bergen_raise_is_standalone`
  - Auction: `1S P`
  - Hand to bid: ♠ K987 ♥ 74 ♦ QJ7 ♣ K985
  - Expected call: `3C`
  - Expected origin: `meow_bergen_raises`, Call Specification `cs_1`

- `meow_drury_is_standalone`
  - Auction: `P P 1S P`
  - Hand to bid: ♠ 987 ♥ 74 ♦ AJ7 ♣ KQ854
  - Expected call: `2C`
  - Expected origin: `meow_two_way_reverse_drury`, Call Specification `cs_1`

- `meow_spade_simple_raise_three_card_support`
  - Auction: `1S P`
  - Hand to bid: ♠ 987 ♥ 74 ♦ AQ7 ♣ K9852
  - Expected call: `2S`
  - Expected origin: `meow_simple_major_raise`, Call Specification `cs_1`

- `meow_heart_simple_raise_three_card_support`
  - Auction: `1H P`
  - Hand to bid: ♠ 72 ♥ 987 ♦ KQ7 ♣ A9852
  - Expected call: `2H`
  - Expected origin: `meow_simple_major_raise`, Call Specification `cs_2`

- `meow_heart_bergen_constructive_raise`
  - Auction: `1H P`
  - Hand to bid: ♠ 72 ♥ K987 ♦ Q87 ♣ A982
  - Expected call: `3C`
  - Expected origin: `meow_bergen_raises`, Call Specification `cs_4`
  - Expected public meaning: constructive Bergen raise

- `meow_heart_bergen_limit_raise`
  - Auction: `1H P`
  - Hand to bid: ♠ 72 ♥ K987 ♦ KQ7 ♣ A982
  - Expected call: `3D`
  - Expected origin: `meow_bergen_raises`, Call Specification `cs_5`
  - Expected public meaning: limit Bergen raise

- `meow_heart_bergen_preemptive_raise`
  - Auction: `1H P`
  - Hand to bid: ♠ 72 ♥ 9876 ♦ 987 ♣ 9852
  - Expected call: `3H`
  - Expected origin: `meow_bergen_raises`, Call Specification `cs_6`
  - Expected public meaning: preemptive Bergen raise

- `meow_heart_any_help_game_try_selected`
  - Auction: `1H P 2H P`
  - Hand to bid: ♠ AQ2 ♥ AKJ74 ♦ 82 ♣ 983
  - Expected call: `2S`
  - Expected origin: `meow_kokish_game_tries`, Call Specification `cs_6`

- `meow_heart_trump_help_game_try_selected`
  - Auction: `1H P 2H P`
  - Hand to bid: ♠ AQ2 ♥ 98754 ♦ AK2 ♣ K3
  - Expected call: `2N`
  - Expected origin: `meow_kokish_game_tries`, Call Specification `cs_9`

- `meow_heart_any_help_response_shows_spades`
  - Auction: `1H P 2H P 2S P`
  - Hand to bid: ♠ K72 ♥ 987 ♦ Q76 ♣ A982
  - Expected call: `2N`
  - Expected origin: `meow_kokish_game_tries`, Call Specification `cs_7`

- `meow_rkcb_after_simple_raise_uses_semantic_agreed_suit`
  - Auction: `1S P 2S P`
  - Hand to bid: ♠ KQJT98 ♥ A43 ♦ A2 ♣ AK
  - Expected call: `4N`
  - Expected origin: `meow_rkcb_1430`, Call Specification `cs_1`
  - Expected replay facts: `major_opening`, `agreed_suit`, `major_raise`

- `meow_rkcb_response_after_simple_raise_uses_semantic_context`
  - Auction: `1S P 2S P 4N P`
  - Hand to bid: ♠ A54 ♥ 872 ♦ K83 ♣ Q762
  - Expected call: `5C`
  - Expected origin: `meow_rkcb_1430`, Call Specification `cs_2`
  - Expected replay facts include `keycard_context` with trump suit recovered from `agreed_suit`

- `meow_rkcb_specific_king_ask_after_simple_raise`
  - Auction: `1S P 2S P 4N P 5C P`
  - Hand to bid: ♠ KQJT98 ♥ A43 ♦ A2 ♣ AK
  - Expected call: `5N`
  - Expected origin: `meow_rkcb_1430`, Call Specification `cs_6`

- `meow_rkcb_specific_king_response_after_simple_raise`
  - Auction: `1S P 2S P 4N P 5C P 5N P`
  - Hand to bid: ♠ A54 ♥ 872 ♦ K83 ♣ Q762
  - Expected call: `6D`
  - Expected origin: `meow_rkcb_1430`, Call Specification `cs_7`

- `meow_rkcb_grand_placement_after_simple_raise`
  - Auction: `1S P 2S P 4N P 5C P 5N P 6D P`
  - Hand to bid: ♠ KQJT98 ♥ A43 ♦ A2 ♣ AK
  - Expected call: `7S`
  - Expected origin: `meow_rkcb_1430`, Call Specification `cs_8`

- `meow_quantitative_four_notrump_after_one_notrump`
  - Auction: `1N P`
  - Hand to bid: ♠ AQ7 ♥ KJ8 ♦ KJ6 ♣ Q542
  - Expected call: `4N`
  - Expected origin: `meow_quantitative_notrump`, Call Specification `cs_1`
  - Expected public meaning: quantitative notrump invite

- `meow_rkcb_not_quantitative_after_texas_sets_agreed_suit`
  - Auction: `1N P 4H P 4S P`
  - Hand to bid: ♠ KQJT98 ♥ A43 ♦ A2 ♣ AK
  - Expected call: `4N`
  - Expected origin: `meow_rkcb_1430`, Call Specification `cs_1`
  - Bridge sense: Texas completion created `agreed_suit`, so the standalone RKCB meaning wins and quantitative notrump is not eligible.

- `illegal_candidate_is_filtered_after_higher_contract`
  - Auction: `1S P 2S P 5N P`
  - Hand to bid: ♠ KQJT98 ♥ A43 ♦ A2 ♣ AK
  - Expected call: `P`
  - Expected algorithm: `default_policy`
  - Expected diagnostics include: illegal `4N` candidate filtered, then default pass selected.

- `ambiguous_same_call_meaning_reports_diagnostic`
  - Convention Set: `test_ambiguous_4n`
  - Auction: empty
  - Hand to bid: ♠ AQ7 ♥ KJ8 ♦ KJ6 ♣ Q542
  - Expected call: `4N`
  - Expected diagnostics include: ambiguous meaning for call `4N`

### Minor Opening, Checkback, Preempt, And Gambling Cases

- `meow_minor_response_bypasses_diamonds_for_hearts`
  - Auction: `1C P`
  - Hand to bid: ♠ 72 ♥ KJ87 ♦ Q876 ♣ 542
  - Expected call: `1H`
  - Bridge sense: one-level major responses may bypass four diamonds.

- `meow_minor_response_bids_one_diamond_without_major`
  - Auction: `1C P`
  - Hand to bid: ♠ 72 ♥ 83 ♦ KJ87 ♣ Q9652
  - Expected call: `1D`, compared against `1N`

- `meow_minor_response_one_notrump_six_to_ten`
  - Auction: `1C P`
  - Hand to bid: ♠ 72 ♥ K83 ♦ Q87 ♣ J9652
  - Expected call: `1N`, showing 6-10

- `meow_minor_response_two_notrump_eleven_to_twelve`
  - Auction: `1C P`
  - Hand to bid: ♠ Q72 ♥ K83 ♦ AQ7 ♣ J654
  - Expected call: `2N`, showing 11-12

- `meow_minor_response_three_notrump_thirteen_to_fifteen`
  - Auction: `1D P`
  - Hand to bid: ♠ A72 ♥ K83 ♦ Q7 ♣ KJ542
  - Expected call: `3N`, showing 13-15

- `meow_minor_weak_jump_shift_spades_is_alertable`
  - Auction: `1C P`
  - Hand to bid: ♠ KJ9876 ♥ 72 ♦ 83 ♣ 542
  - Expected call: `2S`
  - Expected public meaning: weak jump shift, alertable

- `meow_inverted_club_raise_invitational_plus`
  - Auction: `1C P`
  - Hand to bid: ♠ 72 ♥ 83 ♦ AQ7 ♣ KJ6542
  - Expected call: `2C`, inverted club raise, alertable

- `meow_crisscross_club_raise_game_force`
  - Auction: `1C P`
  - Hand to bid: ♠ 72 ♥ K3 ♦ AQ7 ♣ KJ6542
  - Expected call: `2D`, game-forcing Crisscross club raise

- `meow_inverted_diamond_raise_invitational_plus`
  - Auction: `1D P`
  - Hand to bid: ♠ 972 ♥ 83 ♦ KJ876 ♣ AQ2
  - Expected call: `2D`, inverted diamond raise

- `meow_crisscross_diamond_raise_game_force`
  - Auction: `1D P`
  - Hand to bid: ♠ 972 ♥ 83 ♦ AKJ76 ♣ KQ4
  - Expected call: `3C`, game-forcing Crisscross diamond raise

- `meow_inverted_club_raise_opener_rebids_two_notrump_with_stoppers`
  - Auction: `1C P 2C P`
  - Hand to bid: ♠ A72 ♥ K83 ♦ Q87 ♣ KJ62
  - Expected call: `2N`
  - Bridge sense: opener has a minimum balanced hand with side-suit stoppers.

- `meow_inverted_club_raise_opener_bids_stopper_up_the_line`
  - Auction: `1C P 2C P`
  - Hand to bid: ♠ A72 ♥ 983 ♦ KQ7 ♣ AJ62
  - Expected call: `2D`
  - Bridge sense: opener shows the diamond stopper up the line instead of jumping to notrump.

- `meow_inverted_club_raise_game_values_place_three_notrump`
  - Auction: `1C P 2C P 2N P`
  - Hand to bid: ♠ 72 ♥ K3 ♦ AQ7 ♣ KJ6542
  - Expected call: `3N`

- `meow_two_way_nmf_two_club_invitational_relay`
  - Auction: `1C P 1H P 1N P`
  - Hand to bid: ♠ A72 ♥ KQJ83 ♦ 87 ♣ Q54
  - Expected call: `2C`, artificial relay to `2D`, alertable

- `meow_one_diamond_response_notrump_rebid_records_negative_major_state`
  - Auction: `1C P 1D P 1N P`
  - Hand to bid: ♠ A72 ♥ KJ3 ♦ Q876 ♣ Q54
  - Expected call: `2C`, artificial invitational relay
  - Expected recovered auction state: opener has `12-14` HCP, balanced shape, no four-card heart, and no four-card spade

- `meow_two_way_nmf_two_diamond_game_force`
  - Auction: `1C P 1H P 1N P`
  - Hand to bid: ♠ A72 ♥ AJ873 ♦ 87 ♣ KQ4
  - Expected call: `2D`, artificial game force, alertable

- `meow_long_hearts_uses_force_route_before_rebidding`
  - Auction: `1C P 1H P 1S P`
  - Hand to bid: ♠ Q7 ♥ AKQ9876 ♦ KJ ♣ 54
  - Expected call: `2D`, artificial game force
  - Expected recovered auction state: responder has shown hearts, opener has shown spades
  - Expected internal selection reason: establish the force before later describing the long heart suit

- `meow_xyz_two_notrump_club_drop_dead_relay`
  - Auction: `1C P 1D P 1H P`
  - Hand to bid: ♠ 72 ♥ 83 ♦ 876 ♣ J87652
  - Expected call: `2N`, transfer to `3C`, alertable

- `meow_xyz_club_drop_dead_opener_completes_three_clubs`
  - Auction: `1C P 1D P 1H P 2N P`
  - Hand to bid: ♠ A72 ♥ K83 ♦ 87 ♣ Q6542
  - Expected call: `3C`, relay completion, alertable

- `meow_weak_two_favorable_first_seat`
  - Auction: empty, vulnerability: `ew`
  - Hand to bid: ♠ 72 ♥ KQ9876 ♦ 83 ♣ 542
  - Expected call: `2H`

- `meow_weak_two_unfavorable_bad_hand_passes`
  - Auction: empty, vulnerability: `ns`
  - Hand to bid: ♠ 72 ♥ JT9876 ♦ 83 ♣ 542
  - Expected call: `P`

- `meow_weak_two_unfavorable_good_hand_opens`
  - Auction: empty, vulnerability: `ns`
  - Hand to bid: ♠ A72 ♥ KQ9876 ♦ 83 ♣ 54
  - Expected call: `2H`

- `meow_third_seat_light_weak_two_opens`
  - Auction: `P P`
  - Hand to bid: ♠ 72 ♥ JT9876 ♦ K3 ♣ 542
  - Expected call: `2H`

- `meow_fourth_seat_weak_two_style_passes`
  - Auction: `P P P`
  - Hand to bid: ♠ A72 ♥ KQ9876 ♦ 83 ♣ 54
  - Expected call: `P`

- `meow_three_spade_preempt_selected_over_weak_two_with_seven_cards`
  - Auction: empty
  - Hand to bid: ♠ KQJ9876 ♥ 72 ♦ 83 ♣ 54
  - Expected call: `3S`, compared against `2S`

- `meow_gambling_three_notrump_clubs_alertable`
  - Auction: empty
  - Hand to bid: ♠ 87 ♥ 83 ♦ 76 ♣ AKQJ987
  - Expected call: `3N`, Gambling, alertable

## Full-Auction Simulation Cases

- `meow_spade_help_suit_game_try_reaches_game`
  - North hand: ♠ AQJ76 ♥ 82 ♦ Q82 ♣ AJ3
  - South hand: ♠ K98 ♥ 74 ♦ KJ7 ♣ K9852
  - Expected auction: `1S P 2S P 3D P 4S P P P`
  - Expected calls chosen by the partnership engine: `1S`, `2S`, `3D`, `4S`, `P`
  - Expected diagnostics: none
  - Bridge sense: North opens a five-card spade suit, South makes a constructive three-card simple raise, North asks for diamond help with Q-third, South accepts with diamond help and enough constructive values, and North passes the placed game.

- `meow_texas_rkcb_specific_king_reaches_grand`
  - North hand: ♠ A54 ♥ KQ2 ♦ K83 ♣ QJ76
  - South hand: ♠ KQJT98 ♥ A43 ♦ A2 ♣ AK
  - Expected auction: `1N P 4H P 4S P 4N P 5C P 5N P 6D P 7S P P P`
  - Expected calls chosen by the partnership engine: `1N`, `4H`, `4S`, `4N`, `5C`, `5N`, `6D`, `7S`, `P`
  - Expected diagnostics: none
  - Bridge sense: North opens a 15-count balanced 1N, South uses Texas to set spades, South asks RKCB, North shows one keycard, South can infer all keycards are present, 5N asks for specific kings, North shows the diamond king, and South places the grand slam.

- `meow_simple_raise_rkcb_specific_king_reaches_grand`
  - North hand: ♠ KQJT98 ♥ A43 ♦ A2 ♣ AK
  - South hand: ♠ A54 ♥ 872 ♦ K83 ♣ Q762
  - Expected auction: `1S P 2S P 4N P 5C P 5N P 6D P 7S P P P`
  - Expected calls chosen by the partnership engine: `1S`, `2S`, `4N`, `5C`, `5N`, `6D`, `7S`, `P`
  - Expected diagnostics: none
  - Bridge sense: North opens spades, South makes a natural simple raise, North uses the standalone RKCB Convention from the recovered agreed-suit state, South shows one keycard and later the diamond king, and North places the grand slam.

- `meow_heart_any_help_game_try_reaches_game`
  - North hand: ♠ AQ2 ♥ AKJ74 ♦ 82 ♣ 983
  - South hand: ♠ K72 ♥ 987 ♦ Q76 ♣ A982
  - Expected auction: `1H P 2H P 2S P 2N P 4H P P P`
  - Expected calls chosen by the partnership engine: `1H`, `2H`, `2S`, `2N`, `4H`, `P`
  - Expected diagnostics: none
  - Bridge sense: North opens hearts, South gives a natural simple raise, North asks where South can help, South shows spade help with `2N`, and North places the heart game.

- `meow_inverted_minor_invite_stops_in_two_notrump`
  - North hand: ♠ A72 ♥ K83 ♦ Q87 ♣ KJ62
  - South hand: ♠ 72 ♥ 83 ♦ AQ7 ♣ KJ6542
  - Expected auction: `1C P 2C P 2N P P P`
  - Expected calls chosen by the partnership engine: `1C`, `2C`, `2N`, `P`
  - Expected diagnostics: none
  - Bridge sense: South makes an invitational-plus inverted club raise, North has side stoppers and rebids `2N`, and South's invitational values stop there.

- `meow_crisscross_game_force_reaches_three_notrump`
  - North hand: ♠ A72 ♥ K83 ♦ Q87 ♣ KJ62
  - South hand: ♠ 72 ♥ K3 ♦ AQ7 ♣ KJ6542
  - Expected auction: `1C P 2D P 3N P P P`
  - Expected calls chosen by the partnership engine: `1C`, `2D`, `3N`, `P`
  - Expected diagnostics: none
  - Bridge sense: South uses the game-forcing Crisscross club raise and North places notrump game with stoppers.

- `meow_xyz_two_notrump_relay_drops_in_three_clubs`
  - North hand: ♠ A72 ♥ K873 ♦ 87 ♣ KQ64
  - South hand: ♠ 72 ♥ 8 ♦ KQ76 ♣ J87652
  - Expected auction: `1C P 1D P 1H P 2N P 3C P P P`
  - Expected calls chosen by the partnership engine: `1C`, `1D`, `1H`, `2N`, `3C`, `P`
  - Expected diagnostics: none
  - Bridge sense: XYZ is active after the third one-level call; South uses `2N` to transfer to `3C` and then passes.

- `meow_gambling_three_notrump_full_auction`
  - North hand: ♠ 87 ♥ 83 ♦ 76 ♣ AKQJ987
  - Expected auction: `3N P P P`
  - Expected calls chosen by the partnership engine: `3N`
  - Expected diagnostics: none
  - Bridge sense: North has a solid long club suit and no outside ace or king, so Gambling `3N` outranks the natural `3C` preempt candidate.

## Legality Cases

- `opening_position_all_contracts_and_pass_are_legal`
  - Auction: empty
  - Expected complete: false
  - Legal examples: `P`, all one-level contracts, `7N`
  - Illegal examples: `X`, `R`

- `lower_contracts_are_illegal_after_one_spade`
  - Auction: `1S`
  - Expected complete: false
  - Legal examples: `P`, `1N`, `2C`, `X`
  - Illegal examples: `1C`, `1D`, `1H`, `1S`, `R`

- `opener_side_can_redouble_after_opponent_double`
  - Auction: `1S X`
  - Expected complete: false
  - Legal examples: `P`, `R`, `1N`, `2C`
  - Illegal examples: `X`, `1S`

- `auction_complete_after_contract_and_three_passes`
  - Auction: `1S P P P`
  - Expected complete: true
  - Illegal examples after completion: `P`, `1N`, `X`, `R`

- `auction_complete_after_four_passes`
  - Auction: `P P P P`
  - Expected complete: true
  - Illegal examples after completion: `P`, `1C`, `X`, `R`

## Matcher Cases

- `seat_positions_expand_any_pattern`
  - Context pattern: `1H P`
  - Seat positions: `3`, `4`
  - Should match: `P P 1H P`, `P P P 1H P`
  - Should reject: `1H P`, `P 1H P`

## Hand Parser Cases

### Valid Hands

- `any_suit_order_and_10_alias`
  - Raw: `H8763SK10C2DAKQ987`
  - Parsed: ♠ KT ♥ 8763 ♦ AKQ987 ♣ 2
  - HCP: `12`

- `repeated_suit_sections_are_concatenated`
  - Raw: `S9S8HAKQJD7654C432`
  - Parsed: ♠ 98 ♥ AKQJ ♦ 7654 ♣ 432
  - HCP: `10`

- `void_marker_and_x_placeholders`
  - Raw: `SAKQJH-DxxxxCxxxxx`
  - Parsed: ♠ AKQJ ♥ void ♦ XXXX ♣ XXXXX
  - HCP: `10`

### Invalid Hands

- `wrong_card_count`: `SAKQHJT9D876C54` should report `Wrong number of cards`.
- `repeated_known_card`: `SASAHKQJTD987C654` should report `Repeated card`.
- `unknown_symbol`: `SAZHKQJTD987C654` should report `Unknown symbol`.
- `rank_before_suit`: `ASAKQHJT9D876C54` should report `Rank appears before suit marker`.
- `bad_single_one`: `S1HKQJTD987C65432` should report `use 10 or T`.
- `void_marker_with_cards`: `S-AHKQJTD987C654` should report `Void marker`.
- `dictionary_input_rejected`: dictionary-shaped input should report `compact string`.
