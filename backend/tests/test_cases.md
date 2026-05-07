# Human-Readable Test Cases

Version: `0.1.0`
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

This document is generated from the YAML fixtures in `backend/tests/cases/`. When those fixtures change, regenerate or update this file in the same checkpoint.

Current fixture coverage: 155 fixture cases: 128 single-call bidding cases, 11 full-auction simulations, 3 valid hand parser cases, 7 invalid hand parser cases, 5 legality cases, and 1 matcher case.

Unless a case says otherwise, the environment is dealer `n`, vulnerability `none`, and scoring `IMP`.

## Single-Call Bidding Cases

### `meow_opening_policy_prefers_1n_over_five_spades`

- Profile: `meow_2over1`
- Auction before call: empty auction
- Hand to bid: ♠ AQJ87 ♥ K2 ♦ A76 ♣ Q54
- Expected: call `1N`; origin `meow_one_notrump_opening:cs_1`; policy `meow_opening_seat_1_2`; compares `1N`, `1S`; no diagnostics

### `meow_opening_policy_prefers_1n_over_five_hearts`

- Profile: `meow_2over1`
- Auction before call: empty auction
- Hand to bid: ♠ K2 ♥ AQJ87 ♦ A76 ♣ Q54
- Expected: call `1N`; origin `meow_one_notrump_opening:cs_1`; policy `meow_opening_seat_1_2`; compares `1N`, `1H`; no diagnostics

### `meow_notrump_opening_seat_1`

- Profile: `meow_2over1`
- Auction before call: empty auction
- Hand to bid: ♠ AQ7 ♥ KJ8 ♦ A762 ♣ Q54
- Expected: call `1N`; origin `meow_one_notrump_opening:cs_1`; policy `meow_opening_seat_1_2`; no diagnostics

### `meow_notrump_opening_seat_2`

- Profile: `meow_2over1`
- Auction before call: P
- Hand to bid: ♠ AQ7 ♥ KJ8 ♦ A762 ♣ Q54
- Expected: call `1N`; origin `meow_one_notrump_opening:cs_1`; policy `meow_opening_seat_1_2`; no diagnostics

### `meow_notrump_opening_seat_3`

- Profile: `meow_2over1`
- Auction before call: P P
- Hand to bid: ♠ AQ7 ♥ KJ8 ♦ A762 ♣ Q54
- Expected: call `1N`; origin `meow_one_notrump_opening:cs_1`; policy `meow_opening_seat_3`; no diagnostics

### `meow_notrump_opening_seat_4`

- Profile: `meow_2over1`
- Auction before call: P P P
- Hand to bid: ♠ AQ7 ♥ KJ8 ♦ A762 ♣ Q54
- Expected: call `1N`; origin `meow_one_notrump_opening:cs_1`; policy `meow_opening_seat_4`; no diagnostics

### `meow_third_seat_light_spade_opening`

- Profile: `meow_2over1`
- Auction before call: P P
- Hand to bid: ♠ KQ987 ♥ 72 ♦ A83 ♣ J42
- Expected: call `1S`; origin `meow_two_over_one_core:cs_3`; policy `meow_opening_seat_3`; no diagnostics

### `meow_fourth_seat_rule_of_15_opens_spade`

- Profile: `meow_2over1`
- Auction before call: P P P
- Hand to bid: ♠ KQ987 ♥ 72 ♦ A3 ♣ J542
- Expected: call `1S`; origin `meow_two_over_one_core:cs_3`; policy `meow_opening_seat_4`; no diagnostics

### `meow_fourth_seat_rule_of_15_passes_heart_shape`

- Profile: `meow_2over1`
- Auction before call: P P P
- Hand to bid: ♠ 2 ♥ AKJ87 ♦ Q54 ♣ K432
- Expected: call `P`; origin `meow_two_over_one_core:cs_7`; policy `meow_opening_seat_4`; no diagnostics

### `meow_fourth_seat_rule_of_15_opens_minor`

- Profile: `meow_2over1`
- Auction before call: P P P
- Hand to bid: ♠ A72 ♥ K83 ♦ Q87 ♣ KJ62
- Expected: call `1C`; origin `meow_minor_opening_structure:cs_2`; policy `meow_opening_seat_4`; no diagnostics

### `meow_strong_two_club_opening`

- Profile: `meow_2over1`
- Auction before call: empty auction
- Hand to bid: ♠ AKQ2 ♥ AKQ ♦ AKQ ♣ AKQ
- Expected: call `2C`; origin `meow_strong_two_club:cs_1`; policy `meow_opening_seat_1_2`; no diagnostics

### `meow_strong_two_club_two_diamond_waiting`

- Profile: `meow_2over1`
- Auction before call: 2C P
- Hand to bid: ♠ 987 ♥ 765 ♦ 432 ♣ 9872
- Expected: call `2D`; origin `meow_strong_two_club:cs_2`; no diagnostics

### `meow_strong_two_club_balanced_rebid_two_notrump`

- Profile: `meow_2over1`
- Auction before call: 2C P 2D P
- Hand to bid: ♠ AQJ2 ♥ AKQ ♦ QJ2 ♣ KQ3
- Expected: call `2N`; origin `meow_strong_two_club:cs_7`; meaning `action_type`=`strong_two_club_notrump_rebid`; no diagnostics

### `meow_strong_two_club_spade_rebid`

- Profile: `meow_2over1`
- Auction before call: 2C P 2D P
- Hand to bid: ♠ AKQJ87 ♥ AKQ ♦ Q2 ♣ K2
- Expected: call `2S`; origin `meow_strong_two_club:cs_9`; meaning `action_type`=`strong_two_club_suit_rebid`, `target_suit`=`S`; no diagnostics

### `meow_strong_two_club_second_negative_after_spades`

- Profile: `meow_2over1`
- Auction before call: 2C P 2D P 2S P
- Hand to bid: ♠ 987 ♥ 765 ♦ 432 ♣ 9872
- Expected: call `3C`; origin `meow_strong_two_club:cs_13`; meaning `action_type`=`strong_two_club_second_negative`; no diagnostics

### `meow_weak_five_hearts_transfers_over_one_notrump`

- Profile: `meow_2over1`
- Auction before call: 1N P
- Hand to bid: ♠ 974 ♥ JT832 ♦ 976 ♣ 52
- Expected: call `2D`; origin `meow_four_way_transfers_over_1n:cs_1`; policy `meow_notrump_response_route`; no diagnostics

### `meow_non_invitational_five_hearts_passes_one_notrump`

- Profile: `meow_2over1`
- Auction before call: 1N P
- Hand to bid: ♠ 74 ♥ KJ832 ♦ A762 ♣ 85
- Expected: call `P`; origin `meow_notrump_response_basics:ntb_1`; policy `meow_notrump_response_route`; no diagnostics

### `meow_opening_policy_prefers_spades_with_five_five_majors`

- Profile: `meow_2over1`
- Auction before call: empty auction
- Hand to bid: ♠ KQJ87 ♥ QJ984 ♦ A6 ♣ 2
- Expected: call `1S`; origin `meow_two_over_one_core:cs_1`; policy `meow_opening_seat_1_2`; compares `1S`, `1H`; no diagnostics

### `meow_club_transfer_gap_superaccept`

- Profile: `meow_2over1`
- Auction before call: 1N P 2S P
- Hand to bid: ♠ A54 ♥ KQ2 ♦ K83 ♣ QJ76
- Expected: call `2N`; origin `meow_four_way_transfers_over_1n:cs_5`

### `meow_club_transfer_normal_accept_without_honor_third`

- Profile: `meow_2over1`
- Auction before call: 1N P 2S P
- Hand to bid: ♠ A54 ♥ KQ2 ♦ AK3 ♣ 8764
- Expected: call `3C`; origin `meow_four_way_transfers_over_1n:cs_6`

### `meow_diamond_transfer_gap_superaccept`

- Profile: `meow_2over1`
- Auction before call: 1N P 2N P
- Hand to bid: ♠ A54 ♥ KQ2 ♦ K83 ♣ QJ76
- Expected: call `3C`; origin `meow_four_way_transfers_over_1n:cs_8`

### `meow_heart_transfer_superaccept_selected`

- Profile: `meow_2over1`
- Auction before call: 1N P 2D P
- Hand to bid: ♠ AQ74 ♥ KJ83 ♦ A62 ♣ Q5
- Expected: call `3H`; origin `meow_four_way_transfers_over_1n:cs_11`; compares `3H`, `2H`; no diagnostics

### `meow_slam_heart_transfer_route_enters_with_2d`

- Profile: `meow_2over1`
- Auction before call: 1N P
- Hand to bid: ♠ A2 ♥ AKQJ87 ♦ 53 ♣ KQ2
- Expected: call `2D`; origin `meow_four_way_transfers_over_1n:cs_1`; compares `2D`, `4D`, `2C`; no diagnostics

### `meow_rkcb_after_heart_transfer_superaccept_with_five_hearts`

- Profile: `meow_2over1`
- Auction before call: 1N P 2D P 3H P
- Hand to bid: ♠ A2 ♥ AKQJ8 ♦ A3 ♣ KQ32
- Expected: call `4N`; origin `meow_rkcb_1430:cs_1`; compares `4N`; no diagnostics

### `meow_control_bid_after_heart_superaccept_precedes_keycard`

- Profile: `meow_2over1`
- Auction before call: 1N P 2D P 3H P
- Hand to bid: ♠ A2 ♥ AKQJ87 ♦ A3 ♣ KQ2
- Expected: call `4D`; origin `meow_control_bidding:cs_1`; meaning `action_type`=`control_bid`, `target_suit`=`D`; compares `4D`, `4N`; no diagnostics

### `meow_kickback_selected_when_heart_slam_hand_lacks_diamond_control`

- Profile: `meow_2over1`
- Auction before call: 1N P 2D P 3H P
- Hand to bid: ♠ A2 ♥ AKQJ87 ♦ 53 ♣ KQ2
- Expected: call `4S`; origin `meow_kickback_keycard:cs_1`; meaning `action_type`=`kickback_1430`, `target_suit`=`H`; compares `4S`, `4N`; no diagnostics

### `meow_kickback_response_uses_semantic_keycard_context`

- Profile: `meow_2over1`
- Auction before call: 1N P 2D P 3H P 4S P
- Hand to bid: ♠ AQ74 ♥ KJ83 ♦ A62 ♣ Q5
- Expected: call `5C`; origin `meow_kickback_keycard:cs_3`; meaning `action_type`=`keycard_response`; no diagnostics

### `meow_exclusion_keycard_selected_with_diamond_void`

- Profile: `meow_2over1`
- Auction before call: 1N P 2D P 3H P
- Hand to bid: ♠ A2 ♥ AKQJ87 ♦ - ♣ KQJ24
- Expected: call `5D`; origin `meow_exclusion_keycard:cs_1`; meaning `action_type`=`exclusion_1430`, `excluded_suit`=`D`; compares `5D`, `4D`, `4N`; no diagnostics

### `meow_exclusion_response_counts_keycards_outside_void_suit`

- Profile: `meow_2over1`
- Auction before call: 1N P 2D P 3H P 5D P
- Hand to bid: ♠ AQ74 ♥ KJ83 ♦ A62 ♣ Q5
- Expected: call `5N`; origin `meow_exclusion_keycard:cs_4`; meaning `action_type`=`keycard_response`, `excluded_suit`=`D`; no diagnostics

### `meow_gerber_selected_over_notrump_focus`

- Profile: `meow_2over1`
- Auction before call: 1N P
- Hand to bid: ♠ AQ7 ♥ KQ8 ♦ KQ6 ♣ AJ42
- Expected: call `4C`; origin `meow_gerber_over_notrump:cs_1`; meaning `action_type`=`gerber_ace_ask`; compares `4C`, `3C`; no diagnostics

### `meow_gerber_response_counts_aces`

- Profile: `meow_2over1`
- Auction before call: 1N P 4C P
- Hand to bid: ♠ A54 ♥ KQ2 ♦ K83 ♣ QJ76
- Expected: call `4H`; origin `meow_gerber_over_notrump:cs_3`; meaning `action_type`=`ace_ask_response`, `ace_count`=`1`; no diagnostics

### `meow_minorwood_selected_after_diamond_transfer_superaccept`

- Profile: `meow_2over1`
- Auction before call: 1N P 2N P 3C P
- Hand to bid: ♠ 2 ♥ 84 ♦ AQJ987 ♣ KQ32
- Expected: call `4D`; origin `meow_minorwood_keycard:cs_1`; meaning `action_type`=`minorwood_1430`, `target_suit`=`D`; no diagnostics

### `meow_minorwood_response_uses_diamond_keycards`

- Profile: `meow_2over1`
- Auction before call: 1N P 2N P 3C P 4D P
- Hand to bid: ♠ A54 ♥ KQ2 ♦ K83 ♣ QJ76
- Expected: call `4N`; origin `meow_minorwood_keycard:cs_4`; meaning `action_type`=`keycard_response`, `keycard_count`=`2`; no diagnostics

### `meow_targeted_diamond_king_ask_after_heart_rkcb`

- Profile: `meow_2over1`
- Auction before call: 1N P 2D P 3H P 4N P 5D P
- Hand to bid: ♠ A2 ♥ AKQJ87 ♦ 53 ♣ KQ2
- Expected: call `5N`; origin `meow_targeted_king_ask:cs_1`; meaning `action_type`=`targeted_king_ask`, `target_suit`=`D`; no diagnostics

### `meow_targeted_diamond_king_response`

- Profile: `meow_2over1`
- Auction before call: 1N P 2D P 3H P 4N P 5D P 5N P
- Hand to bid: ♠ A54 ♥ KQ2 ♦ K83 ♣ QJ76
- Expected: call `6D`; origin `meow_targeted_king_ask:cs_2`; meaning `action_type`=`targeted_king_response`, `target_suit`=`D`; no diagnostics

### `meow_targeted_diamond_king_route_places_grand`

- Profile: `meow_2over1`
- Auction before call: 1N P 2D P 3H P 4N P 5D P 5N P 6D P
- Hand to bid: ♠ A2 ♥ AKQJ87 ♦ 53 ♣ KQ2
- Expected: call `7H`; origin `meow_targeted_king_ask:cs_3`; meaning `action_type`=`place_contract`, `target_suit`=`H`; no diagnostics

### `meow_rkcb_frame_opens_after_transfer_slam_route_4n`

- Profile: `meow_2over1`
- Auction before call: 1N P 2D P 3H P 4N P
- Hand to bid: ♠ AQ74 ♥ KJ83 ♦ A62 ♣ Q5
- Expected: call `5D`; origin `meow_rkcb_1430:cs_3`; no diagnostics

### `meow_weak_heart_transfer_route_passes_completion`

- Profile: `meow_2over1`
- Auction before call: 1N P 2D P 2H P
- Hand to bid: ♠ 74 ♥ 98765 ♦ 762 ♣ Q54
- Expected: call `P`; origin `meow_four_way_transfers_over_1n:route_1`; compares `P`; no diagnostics

### `meow_stayman_two_notrump_invitational_alertable`

- Profile: `meow_2over1`
- Auction before call: 1N P 2C P 2D P
- Hand to bid: ♠ K874 ♥ 92 ♦ Q83 ♣ K762
- Expected: call `2N`; origin `meow_regular_stayman_over_1n:cs_3`; meaning `alertable`=`True`

### `meow_puppet_stayman_over_1n_is_standalone`

- Profile: `meow_2over1`
- Auction before call: 1N P
- Hand to bid: ♠ 82 ♥ 93 ♦ AQJ4 ♣ KQJ76
- Expected: call `3C`; origin `meow_puppet_stayman_over_1n:cs_1`

### `meow_puppet_stayman_over_2n_is_standalone`

- Profile: `meow_2over1`
- Auction before call: 2N P
- Hand to bid: ♠ 82 ♥ 93 ♦ AQJ4 ♣ KQJ76
- Expected: call `3C`; origin `meow_puppet_stayman_over_2n:cs_1`

### `meow_rkcb_after_texas_is_standalone`

- Profile: `meow_2over1`
- Auction before call: 1N P 4H P 4S P
- Hand to bid: ♠ KQJT98 ♥ A43 ♦ A2 ♣ AK
- Expected: call `4N`; origin `meow_rkcb_1430:cs_1`

### `meow_bergen_raise_is_standalone`

- Profile: `meow_2over1`
- Auction before call: 1S P
- Hand to bid: ♠ K987 ♥ 74 ♦ QJ7 ♣ K985
- Expected: call `3C`; origin `meow_bergen_raises:cs_1`

### `meow_drury_is_standalone`

- Profile: `meow_2over1`
- Auction before call: P P 1S P
- Hand to bid: ♠ 987 ♥ 74 ♦ AJ7 ♣ KQ854
- Expected: call `2C`; origin `meow_two_way_reverse_drury:cs_1`

### `meow_spade_simple_raise_three_card_support`

- Profile: `meow_2over1`
- Auction before call: 1S P
- Hand to bid: ♠ 987 ♥ 74 ♦ AQ7 ♣ K9852
- Expected: call `2S`; origin `meow_simple_major_raise:cs_1`; policy `meow_major_raise_route`

### `meow_heart_simple_raise_three_card_support`

- Profile: `meow_2over1`
- Auction before call: 1H P
- Hand to bid: ♠ 72 ♥ 987 ♦ KQ7 ♣ A9852
- Expected: call `2H`; origin `meow_simple_major_raise:cs_2`; policy `meow_major_raise_route`

### `meow_heart_bergen_constructive_raise`

- Profile: `meow_2over1`
- Auction before call: 1H P
- Hand to bid: ♠ 72 ♥ K987 ♦ Q87 ♣ A982
- Expected: call `3C`; origin `meow_bergen_raises:cs_4`; meaning `raise_strength`=`constructive`; policy `meow_major_raise_route`

### `meow_heart_bergen_limit_raise`

- Profile: `meow_2over1`
- Auction before call: 1H P
- Hand to bid: ♠ 72 ♥ K987 ♦ KQ7 ♣ A982
- Expected: call `3D`; origin `meow_bergen_raises:cs_5`; meaning `raise_strength`=`limit`; policy `meow_major_raise_route`

### `meow_heart_bergen_preemptive_raise`

- Profile: `meow_2over1`
- Auction before call: 1H P
- Hand to bid: ♠ 72 ♥ 9876 ♦ 987 ♣ 9852
- Expected: call `3H`; origin `meow_bergen_raises:cs_6`; meaning `raise_strength`=`preemptive`; policy `meow_major_raise_route`

### `meow_heart_any_help_game_try_selected`

- Profile: `meow_2over1`
- Auction before call: 1H P 2H P
- Hand to bid: ♠ AQ2 ♥ AKJ74 ♦ 82 ♣ 983
- Expected: call `2S`; origin `meow_kokish_game_tries:cs_6`; policy `meow_game_try_route`

### `meow_heart_trump_help_game_try_selected`

- Profile: `meow_2over1`
- Auction before call: 1H P 2H P
- Hand to bid: ♠ AQ2 ♥ 98754 ♦ AK2 ♣ K3
- Expected: call `2N`; origin `meow_kokish_game_tries:cs_9`; policy `meow_game_try_route`

### `meow_heart_any_help_response_shows_spades`

- Profile: `meow_2over1`
- Auction before call: 1H P 2H P 2S P
- Hand to bid: ♠ K72 ♥ 987 ♦ Q76 ♣ A982
- Expected: call `2N`; origin `meow_kokish_game_tries:cs_7`; policy `meow_game_try_route`

### `meow_rkcb_after_simple_raise_uses_semantic_agreed_suit`

- Profile: `meow_2over1`
- Auction before call: 1S P 2S P
- Hand to bid: ♠ KQJT98 ♥ A43 ♦ A2 ♣ AK
- Expected: call `4N`; origin `meow_rkcb_1430:cs_1`

### `meow_rkcb_response_after_simple_raise_uses_semantic_context`

- Profile: `meow_2over1`
- Auction before call: 1S P 2S P 4N P
- Hand to bid: ♠ A54 ♥ 872 ♦ K83 ♣ Q762
- Expected: call `5C`; origin `meow_rkcb_1430:cs_2`

### `meow_rkcb_specific_king_ask_after_simple_raise`

- Profile: `meow_2over1`
- Auction before call: 1S P 2S P 4N P 5C P
- Hand to bid: ♠ KQJT98 ♥ A43 ♦ A2 ♣ AK
- Expected: call `5N`; origin `meow_rkcb_1430:cs_6`

### `meow_rkcb_specific_king_response_after_simple_raise`

- Profile: `meow_2over1`
- Auction before call: 1S P 2S P 4N P 5C P 5N P
- Hand to bid: ♠ A54 ♥ 872 ♦ K83 ♣ Q762
- Expected: call `6D`; origin `meow_rkcb_1430:cs_7`

### `meow_rkcb_grand_placement_after_simple_raise`

- Profile: `meow_2over1`
- Auction before call: 1S P 2S P 4N P 5C P 5N P 6D P
- Hand to bid: ♠ KQJT98 ♥ A43 ♦ A2 ♣ AK
- Expected: call `7S`; origin `meow_rkcb_1430:cs_8`

### `meow_quantitative_four_notrump_after_one_notrump`

- Profile: `meow_2over1`
- Auction before call: 1N P
- Hand to bid: ♠ AQ7 ♥ KJ8 ♦ KJ6 ♣ Q542
- Expected: call `4N`; origin `meow_quantitative_notrump:cs_1`; meaning `action_type`=`quantitative_notrump_invite`

### `meow_rkcb_not_quantitative_after_texas_sets_agreed_suit`

- Profile: `meow_2over1`
- Auction before call: 1N P 4H P 4S P
- Hand to bid: ♠ KQJT98 ♥ A43 ♦ A2 ♣ AK
- Expected: call `4N`; origin `meow_rkcb_1430:cs_1`

### `illegal_candidate_is_filtered_after_higher_contract`

- Profile: `meow_2over1`
- Auction before call: 1S P 2S P 5N P
- Hand to bid: ♠ KQJT98 ♥ A43 ♦ A2 ♣ AK
- Expected: call `P`; source kind `default_policy`; diagnostics include `Illegal candidate 4N`, `defaulting to P`

### `meow_minor_response_bypasses_diamonds_for_hearts`

- Profile: `meow_2over1`
- Auction before call: 1C P
- Hand to bid: ♠ 72 ♥ KJ87 ♦ Q876 ♣ 542
- Expected: call `1H`; origin `meow_minor_opening_structure:cs_4`; no diagnostics

### `meow_minor_response_bids_one_diamond_without_major`

- Profile: `meow_2over1`
- Auction before call: 1C P
- Hand to bid: ♠ 72 ♥ 83 ♦ KJ87 ♣ Q9652
- Expected: call `1D`; origin `meow_minor_opening_structure:cs_3`; compares `1D`, `1N`; no diagnostics

### `meow_minor_response_one_notrump_six_to_ten`

- Profile: `meow_2over1`
- Auction before call: 1C P
- Hand to bid: ♠ 72 ♥ K83 ♦ Q87 ♣ J9652
- Expected: call `1N`; origin `meow_minor_opening_structure:cs_8`; meaning `hcp_range`=`[6, 10]`

### `meow_minor_response_two_notrump_eleven_to_twelve`

- Profile: `meow_2over1`
- Auction before call: 1C P
- Hand to bid: ♠ Q72 ♥ K83 ♦ AQ7 ♣ J654
- Expected: call `2N`; origin `meow_minor_opening_structure:cs_10`; meaning `hcp_range`=`[11, 12]`

### `meow_minor_response_three_notrump_thirteen_to_fifteen`

- Profile: `meow_2over1`
- Auction before call: 1D P
- Hand to bid: ♠ A72 ♥ K83 ♦ Q7 ♣ KJ542
- Expected: call `3N`; origin `meow_minor_opening_structure:cs_13`; meaning `hcp_range`=`[13, 15]`

### `meow_minor_weak_jump_shift_spades_is_alertable`

- Profile: `meow_2over1`
- Auction before call: 1C P
- Hand to bid: ♠ KJ9876 ♥ 72 ♦ 83 ♣ 542
- Expected: call `2S`; origin `meow_minor_opening_structure:cs_15`; meaning `alertable`=`True`, `action_type`=`weak_jump_shift`

### `meow_inverted_club_raise_invitational_plus`

- Profile: `meow_2over1`
- Auction before call: 1C P
- Hand to bid: ♠ 72 ♥ 83 ♦ AQ7 ♣ KJ6542
- Expected: call `2C`; origin `meow_inverted_minors:cs_1`; meaning `alertable`=`True`, `raise_strength`=`invitational_plus`; compares `2C`, `1N`

### `meow_crisscross_club_raise_game_force`

- Profile: `meow_2over1`
- Auction before call: 1C P
- Hand to bid: ♠ 72 ♥ K3 ♦ AQ7 ♣ KJ6542
- Expected: call `2D`; origin `meow_crisscross_minor_raises:cs_1`; meaning `alertable`=`True`, `raise_strength`=`game_force`; compares `2D`, `2C`

### `meow_inverted_diamond_raise_invitational_plus`

- Profile: `meow_2over1`
- Auction before call: 1D P
- Hand to bid: ♠ 972 ♥ 83 ♦ KJ876 ♣ AQ2
- Expected: call `2D`; origin `meow_inverted_minors:cs_2`; meaning `raise_strength`=`invitational_plus`; compares `2D`, `1N`

### `meow_crisscross_diamond_raise_game_force`

- Profile: `meow_2over1`
- Auction before call: 1D P
- Hand to bid: ♠ 972 ♥ 83 ♦ AKJ76 ♣ KQ4
- Expected: call `3C`; origin `meow_crisscross_minor_raises:cs_2`; meaning `raise_strength`=`game_force`; compares `3C`, `2D`, `3N`

### `meow_inverted_club_raise_opener_rebids_two_notrump_with_stoppers`

- Profile: `meow_2over1`
- Auction before call: 1C P 2C P
- Hand to bid: ♠ A72 ♥ K83 ♦ Q87 ♣ KJ62
- Expected: call `2N`; origin `meow_inverted_minors:cs_3`; compares `2N`, `2D`, `3C`

### `meow_inverted_club_raise_opener_bids_stopper_up_the_line`

- Profile: `meow_2over1`
- Auction before call: 1C P 2C P
- Hand to bid: ♠ A72 ♥ 983 ♦ KQ7 ♣ AJ62
- Expected: call `2D`; origin `meow_inverted_minors:cs_4`; meaning `action_type`=`stopper_bid`, `target_suit`=`D`

### `meow_inverted_club_raise_game_values_place_three_notrump`

- Profile: `meow_2over1`
- Auction before call: 1C P 2C P 2N P
- Hand to bid: ♠ 72 ♥ K3 ♦ AQ7 ♣ KJ6542
- Expected: call `3N`; origin `meow_inverted_minors:cs_9`; meaning `action_type`=`place_contract`

### `meow_forcing_notrump_response_after_one_spade`

- Profile: `meow_2over1`
- Auction before call: 1S P
- Hand to bid: ♠ 2 ♥ 87 ♦ QJ65 ♣ KT9872
- Expected: call `1N`; origin `meow_forcing_notrump_after_major:fn_3`; meaning `action_type`=`forcing_notrump_response`; policy `meow_major_response_route`; no diagnostics

### `meow_one_heart_one_spade_response`

- Profile: `meow_2over1`
- Auction before call: 1H P
- Hand to bid: ♠ K987 ♥ 72 ♦ 876 ♣ AQ52
- Expected: call `1S`; origin `meow_forcing_notrump_after_major:fn_1`; meaning `action_type`=`one_level_response`, `target_suit`=`S`; no diagnostics

### `meow_two_over_one_heart_response_after_one_spade`

- Profile: `meow_2over1`
- Auction before call: 1S P
- Hand to bid: ♠ 2 ♥ AKJ87 ♦ Q76 ♣ AQ32
- Expected: call `2H`; origin `meow_forcing_notrump_after_major:fn_8`; meaning `action_type`=`two_over_one_game_force`; policy `meow_major_response_route`; no diagnostics

### `meow_forcing_notrump_opener_repeats_six_spades`

- Profile: `meow_2over1`
- Auction before call: 1S P 1N P
- Hand to bid: ♠ AKJ876 ♥ 2 ♦ 84 ♣ KQ32
- Expected: call `2S`; origin `meow_forcing_notrump_after_major:fn_17`; meaning `action_type`=`forcing_notrump_opener_rebid`, `target_suit`=`S`; policy `meow_forcing_notrump_opener_rebid`; no diagnostics

### `meow_forcing_notrump_opener_bids_longer_minor`

- Profile: `meow_2over1`
- Auction before call: 1S P 1N P
- Hand to bid: ♠ AKJ8 ♥ 72 ♦ Q876 ♣ 432
- Expected: call `2D`; origin `meow_forcing_notrump_after_major:fn_15`; meaning `action_type`=`forcing_notrump_opener_rebid`, `target_suit`=`D`; policy `meow_forcing_notrump_opener_rebid`; no diagnostics

### `meow_spiral_3344_query_after_minor_raise`

- Profile: `meow_2over1`
- Auction before call: 1C P 1H P 2H P
- Hand to bid: ♠ K2 ♥ AQJ87 ♦ K7 ♣ Q543
- Expected: call `2N`; origin `meow_spiral_3344:sp_1`; meaning `action_type`=`spiral_3344_query`, `alertable`=`True`; policy `meow_minor_responder_rebid`; no diagnostics

### `meow_spiral_3344_maximum_three_card_answer`

- Profile: `meow_2over1`
- Auction before call: 1C P 1H P 2H P 2N P
- Hand to bid: ♠ A72 ♥ K83 ♦ AQ7 ♣ KJ62
- Expected: call `3D`; origin `meow_spiral_3344:sp_6`; meaning `action_type`=`spiral_3344_answer`, `support_length`=`3`, `opener_strength`=`maximum`; no diagnostics

### `meow_spiral_3344_places_heart_game`

- Profile: `meow_2over1`
- Auction before call: 1C P 1H P 2H P 2N P 3D P
- Hand to bid: ♠ K2 ♥ AQJ87 ♦ K7 ♣ Q543
- Expected: call `4H`; origin `meow_spiral_3344:sp_13`; meaning `action_type`=`place_contract`, `target_suit`=`H`; no diagnostics

### `meow_inverted_club_raise_opener_places_three_notrump_with_extras`

- Profile: `meow_2over1`
- Auction before call: 1C P 2C P
- Hand to bid: ♠ A72 ♥ K83 ♦ Q87 ♣ AKJ4
- Expected: call `3N`; origin `meow_inverted_minors:im_17`; meaning `action_type`=`place_contract`, `target_suit`=`N`; compares `3N`, `2D`, `3C`; no diagnostics

### `meow_minor_opener_rebid_shows_spades_before_three_card_heart_raise`

- Profile: `meow_2over1`
- Auction before call: 1C P 1H P
- Hand to bid: ♠ AQ72 ♥ K83 ♦ 87 ♣ KJ62
- Expected: call `1S`; origin `meow_minor_opening_structure:cs_21`; meaning `action_type`=`opener_rebid`, `target_suit`=`S`; policy `meow_minor_opener_rebid`; compares `1S`, `1N`, `2H`; no diagnostics

### `meow_minor_opener_rebid_raises_four_card_heart_support_before_spades`

- Profile: `meow_2over1`
- Auction before call: 1C P 1H P
- Hand to bid: ♠ AQ72 ♥ KJ83 ♦ 7 ♣ Q632
- Expected: call `2H`; origin `meow_minor_opening_structure:cs_23`; meaning `action_type`=`raise`, `target_suit`=`H`; policy `meow_minor_opener_rebid`; compares `2H`, `1S`; no diagnostics

### `meow_minor_opener_rebid_jump_notrump_with_eighteen_nineteen_balanced`

- Profile: `meow_2over1`
- Auction before call: 1C P 1H P
- Hand to bid: ♠ AQ2 ♥ K3 ♦ AQ7 ♣ KJ632
- Expected: call `2N`; origin `meow_minor_opening_structure:cs_32`; meaning `action_type`=`opener_notrump_rebid`, `target_suit`=`N`, `hcp_range`=`[18, 19]`; policy `meow_minor_opener_rebid`; compares `2N`, `2C`; no diagnostics

### `meow_minor_opener_rebid_reverse_with_extras`

- Profile: `meow_2over1`
- Auction before call: 1C P 1S P
- Hand to bid: ♠ A2 ♥ AKJ7 ♦ Q7 ♣ KJ632
- Expected: call `2H`; origin `meow_minor_opening_structure:cs_45`; meaning `action_type`=`opener_reverse`, `target_suit`=`H`; policy `meow_minor_opener_rebid`; compares `2H`, `2C`; no diagnostics

### `meow_minor_opener_rebid_jump_raise_with_extras`

- Profile: `meow_2over1`
- Auction before call: 1D P 1S P
- Hand to bid: ♠ AQ72 ♥ 83 ♦ AKJ7 ♣ K32
- Expected: call `3S`; origin `meow_minor_opening_structure:cs_50`; meaning `action_type`=`opener_jump_raise`, `target_suit`=`S`; policy `meow_minor_opener_rebid`; compares `3S`; no diagnostics

### `meow_minor_opener_rebid_rebids_long_diamonds_over_lower_second_suit`

- Profile: `meow_2over1`
- Auction before call: 1D P 1H P
- Hand to bid: ♠ 72 ♥ K3 ♦ KJ876 ♣ AQ42
- Expected: call `2D`; origin `meow_minor_opening_structure:cs_39`; meaning `action_type`=`opener_minor_rebid`, `target_suit`=`D`; policy `meow_minor_opener_rebid`; compares `2D`, `2C`; no diagnostics

### `meow_minor_opener_rebid_one_club_one_diamond_shows_hearts_first`

- Profile: `meow_2over1`
- Auction before call: 1C P 1D P
- Hand to bid: ♠ AQ72 ♥ KJ83 ♦ 7 ♣ Q632
- Expected: call `1H`; origin `meow_minor_opening_structure:cs_18`; meaning `action_type`=`opener_rebid`, `target_suit`=`H`; policy `meow_minor_opener_rebid`; compares `1H`; no diagnostics

### `meow_minor_opener_strong_jump_shift_shows_minor_and_four_card_major`

- Profile: `meow_2over1`
- Auction before call: 1C P 1D P
- Hand to bid: ♠ A2 ♥ AKJ7 ♦ 87 ♣ AKJ63
- Expected: call `2H`; origin `meow_minor_opening_structure:cs_51`; meaning `action_type`=`opener_jump_shift`, `target_suit`=`H`, `shown_length_min`=`4`; policy `meow_minor_opener_rebid`; no diagnostics

### `meow_two_way_nmf_two_club_invitational_relay`

- Profile: `meow_2over1`
- Auction before call: 1C P 1H P 1N P
- Hand to bid: ♠ A72 ♥ KQJ83 ♦ 87 ♣ Q54
- Expected: call `2C`; origin `meow_two_way_nmf_xyz:cs_1`; meaning `alertable`=`True`, `action_type`=`checkback_two_club_relay`; policy `meow_minor_responder_rebid`

### `meow_one_diamond_response_notrump_rebid_records_negative_major_state`

- Profile: `meow_2over1`
- Auction before call: 1C P 1D P 1N P
- Hand to bid: ♠ A72 ♥ KJ3 ♦ Q876 ♣ Q54
- Expected: call `2C`; origin `meow_two_way_nmf_xyz:cs_1`; policy `meow_minor_responder_rebid`

### `meow_two_way_nmf_two_diamond_game_force`

- Profile: `meow_2over1`
- Auction before call: 1C P 1H P 1N P
- Hand to bid: ♠ A72 ♥ AJ873 ♦ 87 ♣ KQ4
- Expected: call `2D`; origin `meow_two_way_nmf_xyz:cs_2`; meaning `alertable`=`True`, `action_type`=`checkback_game_force`; policy `meow_minor_responder_rebid`

### `meow_long_hearts_uses_force_route_before_rebidding`

- Profile: `meow_2over1`
- Auction before call: 1C P 1H P 1S P
- Hand to bid: ♠ Q7 ♥ AKQ9876 ♦ KJ ♣ 54
- Expected: call `2D`; origin `meow_two_way_nmf_xyz:cs_2`; meaning `alertable`=`True`, `action_type`=`checkback_game_force`; policy `meow_minor_responder_rebid`

### `meow_xyz_two_notrump_club_drop_dead_relay`

- Profile: `meow_2over1`
- Auction before call: 1C P 1D P 1H P
- Hand to bid: ♠ 72 ♥ 83 ♦ 876 ♣ J87652
- Expected: call `2N`; origin `meow_two_way_nmf_xyz:cs_3`; meaning `alertable`=`True`, `action_type`=`checkback_two_notrump_club_relay`; policy `meow_minor_responder_rebid`

### `meow_xyz_two_club_diamond_drop_dead_relay`

- Profile: `meow_2over1`
- Auction before call: 1C P 1D P 1N P
- Hand to bid: ♠ 72 ♥ 83 ♦ J8765 ♣ 5423
- Expected: call `2C`; origin `meow_two_way_nmf_xyz:cs_1`; meaning `alertable`=`True`, `action_type`=`checkback_two_club_relay`; policy `meow_minor_responder_rebid`

### `meow_minor_responder_rebids_long_major_to_sign_off`

- Profile: `meow_2over1`
- Auction before call: 1C P 1H P 1S P
- Hand to bid: ♠ 7 ♥ QT9876 ♦ 83 ♣ Q542
- Expected: call `2H`; origin `meow_minor_opening_structure:cs_55`; meaning `action_type`=`responder_major_rebid`, `target_suit`=`H`, `shown_length_min`=`6`; policy `meow_minor_responder_rebid`

### `meow_xyz_club_drop_dead_opener_completes_three_clubs`

- Profile: `meow_2over1`
- Auction before call: 1C P 1D P 1H P 2N P
- Hand to bid: ♠ A72 ♥ K83 ♦ 87 ♣ Q6542
- Expected: call `3C`; origin `meow_two_way_nmf_xyz:cs_9`; meaning `alertable`=`True`, `action_type`=`checkback_club_relay_completion`

### `meow_weak_two_favorable_first_seat`

- Profile: `meow_2over1`
- Auction before call: empty auction
- Hand to bid: ♠ 72 ♥ KQ9876 ♦ 83 ♣ 542
- Expected: call `2H`; origin `meow_preemptive_openings:cs_2`; meaning `alertable`=`False`, `action_type`=`weak_two_opening`

### `meow_second_seat_six_hcp_good_suit_weak_two_passes`

- Profile: `meow_2over1`
- Auction before call: P
- Hand to bid: ♠ 72 ♥ KQ9876 ♦ J3 ♣ 542
- Expected: call `P`; source kind `default_policy`; diagnostics include `defaulting to P`

### `meow_second_seat_sound_weak_two_opens`

- Profile: `meow_2over1`
- Auction before call: P
- Hand to bid: ♠ 72 ♥ KQ9876 ♦ K3 ♣ 542
- Expected: call `2H`; origin `meow_preemptive_openings:cs_2`; policy `meow_opening_seat_1_2`; no diagnostics

### `meow_weak_two_unfavorable_bad_hand_passes`

- Profile: `meow_2over1`
- Auction before call: empty auction
- Hand to bid: ♠ 72 ♥ JT9876 ♦ 83 ♣ 542
- Expected: call `P`; source kind `default_policy`; diagnostics include `defaulting to P`

### `meow_weak_two_unfavorable_good_hand_opens`

- Profile: `meow_2over1`
- Auction before call: empty auction
- Hand to bid: ♠ A72 ♥ KQ9876 ♦ 83 ♣ 54
- Expected: call `2H`; origin `meow_preemptive_openings:cs_2`

### `meow_third_seat_light_weak_two_opens`

- Profile: `meow_2over1`
- Auction before call: P P
- Hand to bid: ♠ 72 ♥ JT9876 ♦ K3 ♣ 542
- Expected: call `2H`; origin `meow_preemptive_openings:cs_2`

### `meow_fourth_seat_weak_two_style_passes`

- Profile: `meow_2over1`
- Auction before call: P P P
- Hand to bid: ♠ A72 ♥ KQ9876 ♦ 83 ♣ 54
- Expected: call `P`; origin `meow_two_over_one_core:cs_7`; policy `meow_opening_seat_4`; no diagnostics

### `meow_three_spade_preempt_selected_over_weak_two_with_seven_cards`

- Profile: `meow_2over1`
- Auction before call: empty auction
- Hand to bid: ♠ KQJ9876 ♥ 72 ♦ 83 ♣ 54
- Expected: call `3S`; origin `meow_preemptive_openings:cs_7`; compares `3S`, `2S`

### `meow_gambling_three_notrump_clubs_alertable`

- Profile: `meow_2over1`
- Auction before call: empty auction
- Hand to bid: ♠ 87 ♥ 83 ♦ 76 ♣ AKQJ987
- Expected: call `3N`; origin `meow_gambling_3nt:cs_1`; meaning `alertable`=`True`, `action_type`=`gambling_3nt_opening`; compares `3N`, `3C`

### `meow_two_notrump_opening_balanced_twenty_count`

- Profile: `meow_2over1`
- Auction before call: empty auction
- Hand to bid: ♠ AQ7 ♥ KJ8 ♦ AQ7 ♣ KJ54
- Expected: call `2N`; origin `meow_two_notrump_opening:cs_1`; meaning `action_type`=`opening`, `target_suit`=`N`; policy `meow_opening_seat_1_2`; no diagnostics

### `meow_one_diamond_opening_with_longer_diamonds`

- Profile: `meow_2over1`
- Auction before call: empty auction
- Hand to bid: ♠ A72 ♥ K83 ♦ KQ87 ♣ 982
- Expected: call `1D`; origin `meow_minor_opening_structure:cs_1`; meaning `action_type`=`opening`, `target_suit`=`D`; policy `meow_opening_seat_1_2`; no diagnostics

### `meow_one_club_opening_with_longer_clubs`

- Profile: `meow_2over1`
- Auction before call: empty auction
- Hand to bid: ♠ A72 ♥ K83 ♦ Q87 ♣ KJ62
- Expected: call `1C`; origin `meow_minor_opening_structure:cs_2`; meaning `action_type`=`opening`, `target_suit`=`C`; policy `meow_opening_seat_1_2`; no diagnostics

### `meow_no_opening_values_defaults_to_pass`

- Profile: `meow_2over1`
- Auction before call: empty auction
- Hand to bid: ♠ 872 ♥ 83 ♦ Q87 ♣ KJ652
- Expected: call `P`; source kind `default_policy`; diagnostics include `defaulting to P`

### `meow_spade_transfer_over_one_notrump`

- Profile: `meow_2over1`
- Auction before call: 1N P
- Hand to bid: ♠ J9832 ♥ 974 ♦ 976 ♣ 52
- Expected: call `2H`; origin `meow_four_way_transfers_over_1n:cs_2`; meaning `action_type`=`transfer`, `target_suit`=`S`; policy `meow_notrump_response_route`; no diagnostics

### `meow_spade_transfer_superaccept_selected`

- Profile: `meow_2over1`
- Auction before call: 1N P 2H P
- Hand to bid: ♠ AQ74 ♥ KJ83 ♦ A62 ♣ Q5
- Expected: call `3S`; origin `meow_four_way_transfers_over_1n:cs_12`; meaning `action_type`=`superaccept`, `target_suit`=`S`; compares `3S`, `2S`; no diagnostics

### `meow_diamond_transfer_normal_accept_without_honor_third`

- Profile: `meow_2over1`
- Auction before call: 1N P 2N P
- Hand to bid: ♠ A54 ♥ KQ2 ♦ 876 ♣ QJ75
- Expected: call `3D`; origin `meow_four_way_transfers_over_1n:cs_9`; meaning `action_type`=`transfer_completion`, `target_suit`=`D`; no diagnostics

### `meow_texas_heart_transfer_game_values`

- Profile: `meow_2over1`
- Auction before call: 1N P
- Hand to bid: ♠ 72 ♥ AQJ987 ♦ 53 ♣ K42
- Expected: call `4D`; origin `meow_texas_transfers_over_1n:cs_3`; meaning `action_type`=`texas_transfer`, `target_suit`=`H`; policy `meow_notrump_response_route`; no diagnostics

### `meow_texas_spade_transfer_game_values`

- Profile: `meow_2over1`
- Auction before call: 1N P
- Hand to bid: ♠ KQJ987 ♥ 72 ♦ 53 ♣ A42
- Expected: call `4H`; origin `meow_texas_transfers_over_1n:cs_1`; meaning `action_type`=`texas_transfer`, `target_suit`=`S`; policy `meow_notrump_response_route`; no diagnostics

### `meow_direct_three_notrump_over_one_notrump`

- Profile: `meow_2over1`
- Auction before call: 1N P
- Hand to bid: ♠ KQ7 ♥ QJ8 ♦ Q76 ♣ KJ54
- Expected: call `3N`; origin `meow_notrump_response_basics:ntb_2`; meaning `action_type`=`place_contract`, `target_suit`=`N`; policy `meow_notrump_response_route`; no diagnostics

### `meow_five_five_minors_game_force_over_one_notrump`

- Profile: `meow_2over1`
- Auction before call: 1N P
- Hand to bid: ♠ 2 ♥ 43 ♦ AQJ87 ♣ KQJ76
- Expected: call `3D`; origin `meow_notrump_response_basics:ntb_3`; meaning `action_type`=`five_five_minors_game_force`, `alertable`=`True`; policy `meow_notrump_response_route`; no diagnostics

### `meow_five_five_majors_invitational_over_one_notrump`

- Profile: `meow_2over1`
- Auction before call: 1N P
- Hand to bid: ♠ KJ987 ♥ QJ987 ♦ 3 ♣ Q2
- Expected: call `3H`; origin `meow_notrump_response_basics:ntb_4`; meaning `action_type`=`five_five_majors_invitational`, `alertable`=`True`; policy `meow_notrump_response_route`; no diagnostics

### `meow_five_five_majors_game_force_over_one_notrump`

- Profile: `meow_2over1`
- Auction before call: 1N P
- Hand to bid: ♠ KQ987 ♥ AQJ87 ♦ 3 ♣ 42
- Expected: call `3S`; origin `meow_notrump_response_basics:ntb_5`; meaning `action_type`=`five_five_majors_game_force`, `alertable`=`True`; policy `meow_notrump_response_route`; no diagnostics

### `meow_quantitative_four_notrump_without_agreed_suit`

- Profile: `meow_2over1`
- Auction before call: 1N P
- Hand to bid: ♠ AQ7 ♥ KJ8 ♦ Q76 ♣ KJ54
- Expected: call `4N`; origin `meow_quantitative_notrump:cs_1`; meaning `action_type`=`quantitative_notrump_invite`, `target_suit`=`N`; no diagnostics

### `meow_spade_jacoby_two_notrump_major_raise`

- Profile: `meow_2over1`
- Auction before call: 1S P
- Hand to bid: ♠ K987 ♥ 74 ♦ AKQ ♣ AQ85
- Expected: call `2N`; origin `meow_jacoby_2nt_major_raise:cs_1`; meaning `action_type`=`jacoby_2n`, `target_suit`=`S`; policy `meow_major_raise_route`; no diagnostics

### `meow_heart_jacoby_two_notrump_major_raise`

- Profile: `meow_2over1`
- Auction before call: 1H P
- Hand to bid: ♠ 72 ♥ AQ87 ♦ KQ7 ♣ A982
- Expected: call `2N`; origin `meow_jacoby_2nt_major_raise:cs_2`; meaning `action_type`=`jacoby_2n`, `target_suit`=`H`; policy `meow_major_raise_route`; no diagnostics

### `meow_heart_drury_three_card_support`

- Profile: `meow_2over1`
- Auction before call: P P 1H P
- Hand to bid: ♠ 754 ♥ A87 ♦ QJ7 ♣ KQ85
- Expected: call `2C`; origin `meow_two_way_reverse_drury:cs_3`; meaning `action_type`=`two_way_reverse_drury`, `target_suit`=`H`, `support_length`=`3`; no diagnostics

### `meow_heart_drury_four_card_support`

- Profile: `meow_2over1`
- Auction before call: P P 1H P
- Hand to bid: ♠ 754 ♥ AQ87 ♦ J7 ♣ K985
- Expected: call `2D`; origin `meow_two_way_reverse_drury:cs_4`; meaning `action_type`=`two_way_reverse_drury`, `target_suit`=`H`, `support_length_min`=`4`; no diagnostics

### `meow_spade_any_help_game_try_selected`

- Profile: `meow_2over1`
- Auction before call: 1S P 2S P
- Hand to bid: ♠ AKJ76 ♥ 82 ♦ 82 ♣ AQ43
- Expected: call `2N`; origin `meow_kokish_game_tries:cs_3`; meaning `action_type`=`help_suit_game_try`, `agreed_suit`=`S`, `ask_scope`=`any_help`; policy `meow_game_try_route`; no diagnostics

### `meow_spade_trump_help_game_try_selected`

- Profile: `meow_2over1`
- Auction before call: 1S P 2S P
- Hand to bid: ♠ 98765 ♥ AKQ ♦ 82 ♣ KQ3
- Expected: call `3S`; origin `meow_kokish_game_tries:cs_4`; meaning `action_type`=`trump_help_game_try`, `target_suit`=`S`; policy `meow_game_try_route`; no diagnostics

### `ambiguous_same_call_meaning_reports_diagnostic`

- Profile: `test_ambiguous_4n`
- Auction before call: empty auction
- Hand to bid: ♠ AQ7 ♥ KJ8 ♦ KJ6 ♣ Q542
- Expected: call `4N`; diagnostics include `Ambiguous meaning for call 4N`

## Full-Auction Simulation Cases

### `meow_spade_help_suit_game_try_reaches_game`

- Profile: `meow_2over1`
- Hands: N: ♠ AQJ76 ♥ 82 ♦ Q82 ♣ AJ3; S: ♠ K98 ♥ 74 ♦ KJ7 ♣ K9852
- Expected auction: 1S P 2S P 3D P 4S P P P
- Calls made by controlled seats: `1S`, `2S`, `3D`, `4S`, `P`
- Expected diagnostics: none

### `meow_texas_rkcb_specific_king_reaches_grand`

- Profile: `meow_2over1`
- Hands: N: ♠ A54 ♥ KQ2 ♦ K83 ♣ QJ76; S: ♠ KQJT98 ♥ A43 ♦ A2 ♣ AK
- Expected auction: 1N P 4H P 4S P 4N P 5C P 5N P 6D P 7S P P P
- Calls made by controlled seats: `1N`, `4H`, `4S`, `4N`, `5C`, `5N`, `6D`, `7S`, `P`
- Expected diagnostics: none

### `meow_simple_raise_rkcb_specific_king_reaches_grand`

- Profile: `meow_2over1`
- Hands: N: ♠ KQJT98 ♥ A43 ♦ A2 ♣ AK; S: ♠ A54 ♥ 872 ♦ K83 ♣ Q762
- Expected auction: 1S P 2S P 4N P 5C P 5N P 6D P 7S P P P
- Calls made by controlled seats: `1S`, `2S`, `4N`, `5C`, `5N`, `6D`, `7S`, `P`
- Expected diagnostics: none

### `meow_heart_any_help_game_try_reaches_game`

- Profile: `meow_2over1`
- Hands: N: ♠ AQ2 ♥ AKJ74 ♦ 82 ♣ 983; S: ♠ K72 ♥ 987 ♦ Q76 ♣ A982
- Expected auction: 1H P 2H P 2S P 2N P 4H P P P
- Calls made by controlled seats: `1H`, `2H`, `2S`, `2N`, `4H`, `P`
- Expected diagnostics: none

### `meow_inverted_minor_invite_stops_in_two_notrump`

- Profile: `meow_2over1`
- Hands: N: ♠ A72 ♥ K83 ♦ Q87 ♣ KJ62; S: ♠ 72 ♥ 83 ♦ AQ7 ♣ KJ6542
- Expected auction: 1C P 2C P 2N P P P
- Calls made by controlled seats: `1C`, `2C`, `2N`, `P`
- Expected diagnostics: none

### `meow_forcing_notrump_sequence_stops_in_two_spades`

- Profile: `meow_2over1`
- Hands: N: ♠ AKJ876 ♥ 2 ♦ 84 ♣ KQ32; S: ♠ 2 ♥ 87 ♦ QJ65 ♣ KT9872
- Expected auction: 1S P 1N P 2S P P P
- Calls made by controlled seats: `1S`, `1N`, `2S`, `P`
- Expected diagnostics: none

### `meow_crisscross_game_force_reaches_three_notrump`

- Profile: `meow_2over1`
- Hands: N: ♠ A72 ♥ K83 ♦ Q87 ♣ KJ62; S: ♠ 72 ♥ K3 ♦ AQ7 ♣ KJ6542
- Expected auction: 1C P 2D P 3N P P P
- Calls made by controlled seats: `1C`, `2D`, `3N`, `P`
- Expected diagnostics: none

### `meow_xyz_two_notrump_relay_drops_in_three_clubs`

- Profile: `meow_2over1`
- Hands: N: ♠ A72 ♥ K873 ♦ 87 ♣ KQ64; S: ♠ 72 ♥ 8 ♦ KQ76 ♣ J87652
- Expected auction: 1C P 1D P 1H P 2N P 3C P P P
- Calls made by controlled seats: `1C`, `1D`, `1H`, `2N`, `3C`, `P`
- Expected diagnostics: none

### `meow_gambling_three_notrump_full_auction`

- Profile: `meow_2over1`
- Hands: N: ♠ 87 ♥ 83 ♦ 76 ♣ AKQJ987
- Expected auction: 3N P P P
- Calls made by controlled seats: `3N`
- Expected diagnostics: none

### `meow_direct_three_notrump_over_one_notrump_full_auction`

- Profile: `meow_2over1`
- Hands: N: ♠ AQ7 ♥ KJ8 ♦ A762 ♣ Q54; S: ♠ KQ7 ♥ QJ8 ♦ Q76 ♣ KJ54
- Expected auction: 1N P 3N P P P
- Calls made by controlled seats: `1N`, `3N`, `P`
- Expected diagnostics: none

### `meow_texas_heart_game_signoff_full_auction`

- Profile: `meow_2over1`
- Hands: N: ♠ AQ7 ♥ KJ8 ♦ A762 ♣ Q54; S: ♠ 72 ♥ AQJ987 ♦ 53 ♣ K42
- Expected auction: 1N P 4D P 4H P P P
- Calls made by controlled seats: `1N`, `4D`, `4H`, `P`
- Expected diagnostics: none

## Hand Parser Cases

- `any_suit_order_and_10_alias`: `H8763SK10C2DAKQ987` -> ♠ KT ♥ 8763 ♦ AKQ987 ♣ 2

- `repeated_suit_sections_are_concatenated`: `S9S8HAKQJD7654C432` -> ♠ 98 ♥ AKQJ ♦ 7654 ♣ 432

- `void_marker_and_x_placeholders`: `SAKQJH-DxxxxCxxxxx` -> ♠ AKQJ ♥ - ♦ XXXX ♣ XXXXX

- `wrong_card_count`: `SAKQHJT9D876C54` should fail with `Wrong number of cards`

- `repeated_known_card`: `SASAHKQJTD987C654` should fail with `Repeated card`

- `unknown_symbol`: `SAZHKQJTD987C654` should fail with `Unknown symbol`

- `rank_before_suit`: `ASAKQHJT9D876C54` should fail with `Rank appears before suit marker`

- `bad_single_one`: `S1HKQJTD987C65432` should fail with `use 10 or T`

- `void_marker_with_cards`: `S-AHKQJTD987C654` should fail with `Void marker`

- `dictionary_input_rejected`: `{'spades': 'AKQ', 'hearts': 'JT9', 'diamonds': '876', 'clubs': '5432'}` should fail with `compact string`

## Legality Cases

- `opening_position_all_contracts_and_pass_are_legal`: auction empty auction; complete=`false`; legal `P`, `1C`, `1D`, `1H`, `1S`, `1N`, `7N`; illegal `X`, `R`

- `lower_contracts_are_illegal_after_one_spade`: auction 1S; complete=`false`; legal `P`, `1N`, `2C`, `X`; illegal `1C`, `1D`, `1H`, `1S`, `R`

- `opener_side_can_redouble_after_opponent_double`: auction 1S X; complete=`false`; legal `P`, `R`, `1N`, `2C`; illegal `X`, `1S`

- `auction_complete_after_contract_and_three_passes`: auction 1S P P P; complete=`true`; illegal `P`, `1N`, `X`, `R`

- `auction_complete_after_four_passes`: auction P P P P; complete=`true`; illegal `P`, `1C`, `X`, `R`

## Matcher Cases

- `seat_positions_expand_any_pattern`: context `{'auction_pattern': '1HP', 'seat_positions': [3, 4]}`
  - Matches: P P 1H P, P P P 1H P
  - Rejects: 1H P, P 1H P
