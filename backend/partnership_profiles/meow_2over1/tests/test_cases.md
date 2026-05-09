# Backend Fixture Cases

Platform Version: 0.0.8
Author: Meow Li
Copyright: Copyright by Meow Li 2026. All Rights Reserved.

This document is generated from the fixture files in `backend/partnership_profiles/meow_2over1/tests/cases/`. When fixture files change, update this file in the same checkpoint.

## Summary

- Single-call bidding cases: 159
- Full-auction simulations: 27
- Valid hand parser cases: 3
- Invalid hand parser cases: 7
- Legality cases: 5
- Matcher cases: 1

## Single-Call Bidding Cases

### `meow_opening_policy_prefers_1n_over_five_spades`

- Auction: ``
- Hand: `SAQJ87HK2DA76CQ54` -> ? AQJ87  ? K2  ? A76  ? Q54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `1N`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_one_notrump_opening'}`
- Expected policy: `{'object_id': 'meow_opening_notrump_policy', 'algorithm': 'python_bsl_function'}`
- Compared candidates: `['1N', '1S', 'P']`
- Expected diagnostics: `[]`

### `meow_opening_policy_prefers_1n_over_five_hearts`

- Auction: ``
- Hand: `SK2HAQJ87DA76CQ54` -> ? K2  ? AQJ87  ? A76  ? Q54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `1N`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_one_notrump_opening'}`
- Expected policy: `{'object_id': 'meow_opening_notrump_policy', 'algorithm': 'python_bsl_function'}`
- Compared candidates: `['1N', '1H', 'P']`
- Expected diagnostics: `[]`

### `meow_notrump_opening_seat_1`

- Auction: ``
- Hand: `SAQ7HKJ8DA762CQ54` -> ? AQ7  ? KJ8  ? A762  ? Q54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `1N`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_one_notrump_opening'}`
- Expected policy: `{'object_id': 'meow_opening_notrump_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_notrump_opening_seat_2`

- Auction: `P`
- Hand: `SAQ7HKJ8DA762CQ54` -> ? AQ7  ? KJ8  ? A762  ? Q54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `1N`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_one_notrump_opening'}`
- Expected policy: `{'object_id': 'meow_opening_notrump_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_notrump_opening_seat_3`

- Auction: `PP`
- Hand: `SAQ7HKJ8DA762CQ54` -> ? AQ7  ? KJ8  ? A762  ? Q54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `1N`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_one_notrump_opening'}`
- Expected policy: `{'object_id': 'meow_opening_notrump_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_notrump_opening_seat_4`

- Auction: `PPP`
- Hand: `SAQ7HKJ8DA762CQ54` -> ? AQ7  ? KJ8  ? A762  ? Q54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `1N`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_one_notrump_opening'}`
- Expected policy: `{'object_id': 'meow_opening_notrump_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_third_seat_light_spade_opening`

- Auction: `PP`
- Hand: `SKQ987H72DA83CJ42` -> ? KQ987  ? 72  ? A83  ? J42
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `1S`
- Expected origin: `{'object_id': 'cs_3', 'gadget_id': 'meow_two_over_one_core'}`
- Expected policy: `{'object_id': 'meow_opening_one_level_seat_3_light_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_fourth_seat_rule_of_15_opens_spade`

- Auction: `PPP`
- Hand: `SKQ987H72DA3CJ542` -> ? KQ987  ? 72  ? A3  ? J542
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `1S`
- Expected origin: `{'object_id': 'cs_3', 'gadget_id': 'meow_two_over_one_core'}`
- Expected policy: `{'object_id': 'meow_opening_one_level_seat_4_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_fourth_seat_rule_of_15_passes_heart_shape`

- Auction: `PPP`
- Hand: `S2HAKJ87DQ54CK432` -> ? 2  ? AKJ87  ? Q54  ? K432
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `P`
- Expected origin: `{'object_id': 'cs_7', 'gadget_id': 'meow_two_over_one_core'}`
- Expected policy: `{'object_id': 'meow_opening_fourth_seat_pass_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_fourth_seat_rule_of_15_opens_minor`

- Auction: `PPP`
- Hand: `SA72HK83DQ87CKJ62` -> ? A72  ? K83  ? Q87  ? KJ62
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `1C`
- Expected origin: `{'object_id': 'cs_2', 'gadget_id': 'meow_minor_opening_structure'}`
- Expected policy: `{'object_id': 'meow_opening_one_level_seat_4_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_strong_two_club_opening`

- Auction: ``
- Hand: `SAKQ2HAKQDAKQCAKQ` -> ? AKQ2  ? AKQ  ? AKQ  ? AKQ
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2C`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_strong_two_club'}`
- Expected policy: `{'object_id': 'meow_opening_strong_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_strong_two_club_two_diamond_waiting`

- Auction: `2CP`
- Hand: `S987H765D432C9872` -> ? 987  ? 765  ? 432  ? 9872
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2D`
- Expected origin: `{'object_id': 'cs_2', 'gadget_id': 'meow_strong_two_club'}`
- Expected diagnostics: `[]`

### `meow_strong_two_club_balanced_rebid_two_notrump`

- Auction: `2CP2DP`
- Hand: `SAQJ2HAKQDQJ2CKQ3` -> ? AQJ2  ? AKQ  ? QJ2  ? KQ3
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2N`
- Expected origin: `{'object_id': 'cs_7', 'gadget_id': 'meow_strong_two_club'}`
- Expected public meaning: `{'action_type': 'strong_two_club_notrump_rebid'}`
- Expected diagnostics: `[]`

### `meow_strong_two_club_spade_rebid`

- Auction: `2CP2DP`
- Hand: `SAKQJ87HAKQDQ2CK2` -> ? AKQJ87  ? AKQ  ? Q2  ? K2
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2S`
- Expected origin: `{'object_id': 'cs_9', 'gadget_id': 'meow_strong_two_club'}`
- Expected public meaning: `{'action_type': 'strong_two_club_suit_rebid', 'target_suit': 'S'}`
- Expected diagnostics: `[]`

### `meow_strong_two_club_second_negative_after_spades`

- Auction: `2CP2DP2SP`
- Hand: `S987H765D432C9872` -> ? 987  ? 765  ? 432  ? 9872
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3C`
- Expected origin: `{'object_id': 'cs_14', 'gadget_id': 'meow_strong_two_club'}`
- Expected public meaning: `{'action_type': 'strong_two_club_second_negative'}`
- Expected diagnostics: `[]`

### `meow_weak_five_hearts_transfers_over_one_notrump`

- Auction: `1NP`
- Hand: `S974HJT832D976C52` -> ? 974  ? JT832  ? 976  ? 52
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2D`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_four_way_transfers_over_1n'}`
- Expected policy: `{'object_id': 'meow_1n_weak_partscore_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_non_invitational_five_hearts_passes_one_notrump`

- Auction: `1NP`
- Hand: `S74HKJ832DA762C85` -> ? 74  ? KJ832  ? A762  ? 85
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `P`
- Expected origin: `{'object_id': 'ntb_1', 'gadget_id': 'meow_notrump_response_basics'}`
- Expected policy: `{'object_id': 'meow_1n_weak_partscore_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_opening_policy_prefers_spades_with_five_five_majors`

- Auction: ``
- Hand: `SKQJ87HQJ984DA6C2` -> ? KQJ87  ? QJ984  ? A6  ? 2
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `1S`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_two_over_one_core'}`
- Expected policy: `{'object_id': 'meow_opening_one_level_seat_1_2_policy', 'algorithm': 'python_bsl_function'}`
- Compared candidates: `['1S', '1H', 'P']`
- Expected diagnostics: `[]`

### `meow_club_transfer_gap_superaccept`

- Auction: `1NP2SP`
- Hand: `SA54HKQ2DK83CQJ76` -> ? A54  ? KQ2  ? K83  ? QJ76
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2N`
- Expected origin: `{'object_id': 'cs_5', 'gadget_id': 'meow_four_way_transfers_over_1n'}`
- Expected selected criteria include: `['honor_third_club_support']`

### `meow_club_transfer_normal_accept_without_honor_third`

- Auction: `1NP2SP`
- Hand: `SA54HKQ2DAK3C8764` -> ? A54  ? KQ2  ? AK3  ? 8764
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3C`
- Expected origin: `{'object_id': 'cs_6', 'gadget_id': 'meow_four_way_transfers_over_1n'}`

### `meow_diamond_transfer_gap_superaccept`

- Auction: `1NP2NP`
- Hand: `SA54HKQ2DK83CQJ76` -> ? A54  ? KQ2  ? K83  ? QJ76
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3C`
- Expected origin: `{'object_id': 'cs_8', 'gadget_id': 'meow_four_way_transfers_over_1n'}`
- Expected selected criteria include: `['honor_third_diamond_support']`

### `meow_heart_transfer_superaccept_selected`

- Auction: `1NP2DP`
- Hand: `SAQ74HKJ83DA62CQ5` -> ? AQ74  ? KJ83  ? A62  ? Q5
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3H`
- Expected origin: `{'object_id': 'cs_11', 'gadget_id': 'meow_four_way_transfers_over_1n'}`
- Compared candidates: `['3H', '2H']`
- Expected diagnostics: `[]`
- Expected selected criteria include: `['pending_heart_transfer', 'four_heart_support', 'maximum_notrump_values']`

### `meow_slam_heart_transfer_route_enters_with_2d`

- Auction: `1NP`
- Hand: `SA2HAKQJ87D53CKQ2` -> ? A2  ? AKQJ87  ? 53  ? KQ2
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2D`
- Expected origin: `{'object_id': 'cs_1', 'object_type': 'call_spec', 'gadget_id': 'meow_four_way_transfers_over_1n'}`
- Compared candidates: `['2D', '4D', '2C']`
- Expected diagnostics: `[]`

### `meow_rkcb_after_heart_transfer_superaccept_with_five_hearts`

- Auction: `1NP2DP3HP`
- Hand: `SA2HAKQJ8DA3CKQ32` -> ? A2  ? AKQJ8  ? A3  ? KQ32
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4N`
- Expected origin: `{'object_id': 'cs_1', 'object_type': 'call_spec', 'gadget_id': 'meow_rkcb_1430'}`
- Compared candidates: `['4N']`
- Expected private route states include route_1 at `pass_acceptance` and route_2 at `ask_keycards`.
- Expected diagnostics: `[]`

### `meow_control_bid_after_heart_superaccept_precedes_keycard`

- Auction: `1NP2DP3HP`
- Hand: `SA2HAKQJ87DA3CKQ2` -> ? A2  ? AKQJ87  ? A3  ? KQ2
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4D`
- Expected origin: `{'object_id': 'control_H_D_4D', 'gadget_id': 'meow_control_bidding'}`
- Expected public meaning: `{'action_type': 'control_bid', 'target_suit': 'D'}`
- Compared candidates: `['4D', '4N']`
- Expected diagnostics: `[]`
- Expected selected criteria include: `['diamond_control']`

### `meow_kickback_selected_when_heart_slam_hand_lacks_diamond_control`

- Auction: `1NP2DP3HP`
- Hand: `SA2HAKQJ87D53CKQ2` -> ? A2  ? AKQJ87  ? 53  ? KQ2
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4S`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_kickback_keycard'}`
- Expected public meaning: `{'action_type': 'kickback_1430', 'target_suit': 'H'}`
- Compared candidates: `['4S', '4N']`
- Expected diagnostics: `[]`

### `meow_kickback_response_uses_semantic_keycard_context`

- Auction: `1NP2DP3HP4SP`
- Hand: `SAQ74HKJ83DA62CQ5` -> ? AQ74  ? KJ83  ? A62  ? Q5
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `5C`
- Expected origin: `{'object_id': 'cs_3', 'gadget_id': 'meow_kickback_keycard'}`
- Expected public meaning: `{'action_type': 'keycard_response'}`
- Expected diagnostics: `[]`

### `meow_exclusion_keycard_selected_with_diamond_void`

- Auction: `1NP2DP3HP`
- Hand: `SA2HAKQJ87D-CKQJ24` -> ? A2  ? AKQJ87  ? -  ? KQJ24
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `5D`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_exclusion_keycard'}`
- Expected public meaning: `{'action_type': 'exclusion_1430', 'excluded_suit': 'D'}`
- Compared candidates: `['5D', '4D', '4N']`
- Expected diagnostics: `[]`
- Expected selected criteria include: `['diamond_void']`

### `meow_exclusion_response_counts_keycards_outside_void_suit`

- Auction: `1NP2DP3HP5DP`
- Hand: `SAQ74HKJ83DA62CQ5` -> ? AQ74  ? KJ83  ? A62  ? Q5
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `5N`
- Expected origin: `{'object_id': 'cs_4', 'gadget_id': 'meow_exclusion_keycard'}`
- Expected public meaning: `{'action_type': 'keycard_response', 'excluded_suit': 'D'}`
- Expected diagnostics: `[]`

### `meow_gerber_selected_over_notrump_focus`

- Auction: `1NP`
- Hand: `SAQ7HKQ8DKQ6CAJ42` -> ? AQ7  ? KQ8  ? KQ6  ? AJ42
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4C`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_gerber_over_notrump'}`
- Expected public meaning: `{'action_type': 'gerber_ace_ask'}`
- Compared candidates: `['4C', '3C']`
- Expected diagnostics: `[]`

### `meow_gerber_response_counts_aces`

- Auction: `1NP4CP`
- Hand: `SA54HKQ2DK83CQJ76` -> ? A54  ? KQ2  ? K83  ? QJ76
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4H`
- Expected origin: `{'object_id': 'cs_3', 'gadget_id': 'meow_gerber_over_notrump'}`
- Expected public meaning: `{'action_type': 'ace_ask_response', 'ace_count': 1}`
- Expected diagnostics: `[]`

### `meow_minorwood_selected_after_diamond_transfer_superaccept`

- Auction: `1NP2NP3CP`
- Hand: `S2H84DAQJ987CKQ32` -> ? 2  ? 84  ? AQJ987  ? KQ32
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4D`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_minorwood_keycard'}`
- Expected public meaning: `{'action_type': 'minorwood_1430', 'target_suit': 'D'}`
- Expected diagnostics: `[]`

### `meow_minorwood_response_uses_diamond_keycards`

- Auction: `1NP2NP3CP4DP`
- Hand: `SA54HKQ2DK83CQJ76` -> ? A54  ? KQ2  ? K83  ? QJ76
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4N`
- Expected origin: `{'object_id': 'cs_4', 'gadget_id': 'meow_minorwood_keycard'}`
- Expected public meaning: `{'action_type': 'keycard_response', 'keycard_count': 2}`
- Expected diagnostics: `[]`

### `meow_targeted_diamond_king_ask_after_heart_rkcb`

- Auction: `1NP2DP3HP4NP5DP`
- Hand: `SA2HAKQJ87D53CKQ2` -> ? A2  ? AKQJ87  ? 53  ? KQ2
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `5N`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_targeted_king_ask'}`
- Expected public meaning: `{'action_type': 'targeted_king_ask', 'target_suit': 'D'}`
- Expected diagnostics: `[]`

### `meow_targeted_diamond_king_response`

- Auction: `1NP2DP3HP4NP5DP5NP`
- Hand: `SA54HKQ2DK83CQJ76` -> ? A54  ? KQ2  ? K83  ? QJ76
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `6D`
- Expected origin: `{'object_id': 'cs_2', 'gadget_id': 'meow_targeted_king_ask'}`
- Expected public meaning: `{'action_type': 'targeted_king_response', 'target_suit': 'D'}`
- Expected diagnostics: `[]`

### `meow_targeted_diamond_king_route_places_grand`

- Auction: `1NP2DP3HP4NP5DP5NP6DP`
- Hand: `SA2HAKQJ87D53CKQ2` -> ? A2  ? AKQJ87  ? 53  ? KQ2
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `7H`
- Expected origin: `{'object_id': 'cs_3', 'gadget_id': 'meow_targeted_king_ask'}`
- Expected public meaning: `{'action_type': 'place_contract', 'target_suit': 'H'}`
- Expected diagnostics: `[]`

### `meow_rkcb_frame_opens_after_transfer_slam_route_4n`

- Auction: `1NP2DP3HP4NP`
- Hand: `SAQ74HKJ83DA62CQ5` -> ? AQ74  ? KJ83  ? A62  ? Q5
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `5D`
- Expected origin: `{'object_id': 'cs_3', 'gadget_id': 'meow_rkcb_1430'}`
- Expected diagnostics: `[]`

### `meow_weak_heart_transfer_route_passes_completion`

- Auction: `1NP2DP2HP`
- Hand: `S74H98765D762CQ54` -> ? 74  ? 98765  ? 762  ? Q54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `P`
- Expected origin: `{'object_id': 'route_1', 'object_type': 'private_route_spec', 'gadget_id': 'meow_four_way_transfers_over_1n'}`
- Compared candidates: `['P']`
- Expected private route state includes route_1 at `pass_acceptance`.
- Expected diagnostics: `[]`

### `meow_stayman_two_notrump_invitational_alertable`

- Auction: `1NP2CP2DP`
- Hand: `SK874H92DQ83CK762` -> ? K874  ? 92  ? Q83  ? K762
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2N`
- Expected origin: `{'object_id': 'cs_3', 'gadget_id': 'meow_regular_stayman_over_1n'}`
- Expected public meaning: `{'alertable': True}`

### `meow_puppet_stayman_over_1n_is_standalone`

- Auction: `1NP`
- Hand: `S9876H76DAJ4CKQ72` -> S 9876  H 76  D AJ4  C KQ72
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3C`
- Expected origin: `{'object_id': 'puppet_1n_ask', 'gadget_id': 'meow_puppet_stayman_over_1n'}`

### `meow_puppet_stayman_over_2n_is_standalone`

- Auction: `2NP`
- Hand: `S9876H76DQJ4CK972` -> S 9876  H 76  D QJ4  C K972
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3C`
- Expected origin: `{'object_id': 'puppet_2n_ask', 'gadget_id': 'meow_puppet_stayman_over_2n'}`

### `meow_puppet_1n_opener_denies_major_length`

- Auction: `1NP3CP`
- Hand: `SAQ7HKJ8DA762CQ54` -> S AQ7  H KJ8  D A762  C Q54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3N`
- Expected origin: `{'object_id': 'puppet_1n_answer_3nt', 'gadget_id': 'meow_puppet_stayman_over_1n'}`
- Expected public meaning: `{'action_type': 'puppet_answer', 'target_suit': 'N'}`
- Expected policy: `{'object_id': 'meow_puppet_stayman_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_puppet_1n_opener_shows_five_hearts`

- Auction: `1NP3CP`
- Hand: `S82HAQJ87DA76CKQ5` -> S 82  H AQJ87  D A76  C KQ5
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3H`
- Expected origin: `{'object_id': 'puppet_1n_answer_3h', 'gadget_id': 'meow_puppet_stayman_over_1n'}`
- Expected public meaning: `{'action_type': 'puppet_answer', 'target_suit': 'H'}`
- Expected policy: `{'object_id': 'meow_puppet_stayman_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_puppet_1n_responder_places_heart_game_after_five_card_answer`

- Auction: `1NP3CP3HP`
- Hand: `S9876HQT2DAJ4CKQ7` -> S 9876  H QT2  D AJ4  C KQ7
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4H`
- Expected origin: `{'object_id': 'puppet_1n_continuation_3h_4h', 'gadget_id': 'meow_puppet_stayman_over_1n'}`
- Expected public meaning: `{'action_type': 'place_contract', 'target_suit': 'H'}`
- Expected policy: `{'object_id': 'meow_puppet_stayman_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_puppet_1n_responder_places_notrump_without_heart_support`

- Auction: `1NP3CP3HP`
- Hand: `S9876H76DAJ4CKQ72` -> S 9876  H 76  D AJ4  C KQ72
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3N`
- Expected origin: `{'object_id': 'puppet_1n_continuation_3h_3nt', 'gadget_id': 'meow_puppet_stayman_over_1n'}`
- Expected public meaning: `{'action_type': 'place_contract', 'target_suit': 'N'}`
- Expected policy: `{'object_id': 'meow_puppet_stayman_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_puppet_1n_responder_shows_four_spades_after_three_diamonds`

- Auction: `1NP3CP3DP`
- Hand: `S9876H76DAJ4CKQ72` -> S 9876  H 76  D AJ4  C KQ72
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3H`
- Expected origin: `{'object_id': 'puppet_1n_continuation_3d_3h', 'gadget_id': 'meow_puppet_stayman_over_1n'}`
- Expected public meaning: `{'action_type': 'puppet_responder_continuation', 'target_suit': 'S'}`
- Expected policy: `{'object_id': 'meow_puppet_stayman_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_puppet_1n_opener_confirms_four_four_spade_fit`

- Auction: `1NP3CP3DP3HP`
- Hand: `SAQ76HKJ8DA76CQ54` -> S AQ76  H KJ8  D A76  C Q54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4S`
- Expected origin: `{'object_id': 'puppet_1n_resolution_3d_3h_4s', 'gadget_id': 'meow_puppet_stayman_over_1n'}`
- Expected public meaning: `{'action_type': 'place_contract', 'target_suit': 'S'}`
- Expected policy: `{'object_id': 'meow_puppet_stayman_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_puppet_1n_opener_places_notrump_without_spade_fit`

- Auction: `1NP3CP3DP3HP`
- Hand: `SAQ7HKJ83DA76CQ54` -> S AQ7  H KJ83  D A76  C Q54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3N`
- Expected origin: `{'object_id': 'puppet_1n_resolution_3d_3h_3nt', 'gadget_id': 'meow_puppet_stayman_over_1n'}`
- Expected public meaning: `{'action_type': 'place_contract', 'target_suit': 'N'}`
- Expected policy: `{'object_id': 'meow_puppet_stayman_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_puppet_1n_responder_shows_both_majors`

- Auction: `1NP3CP3DP`
- Hand: `S9876HQT76DA4CKQ7` -> S 9876  H QT76  D A4  C KQ7
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4D`
- Expected origin: `{'object_id': 'puppet_1n_continuation_3d_4d', 'gadget_id': 'meow_puppet_stayman_over_1n'}`
- Expected public meaning: `{'action_type': 'puppet_responder_continuation'}`
- Expected policy: `{'object_id': 'meow_puppet_stayman_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_puppet_1n_opener_chooses_spades_with_both_major_fits`

- Auction: `1NP3CP3DP4DP`
- Hand: `SAQ76HKJ8DA76CQ54` -> S AQ76  H KJ8  D A76  C Q54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4S`
- Expected origin: `{'object_id': 'puppet_1n_resolution_3d_4d_4s', 'gadget_id': 'meow_puppet_stayman_over_1n'}`
- Expected public meaning: `{'action_type': 'place_contract', 'target_suit': 'S'}`
- Expected policy: `{'object_id': 'meow_puppet_stayman_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_puppet_1n_opener_chooses_hearts_without_spade_fit`

- Auction: `1NP3CP3DP4DP`
- Hand: `SAQ7HKJ83DA76CQ54` -> S AQ7  H KJ83  D A76  C Q54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4H`
- Expected origin: `{'object_id': 'puppet_1n_resolution_3d_4d_4h', 'gadget_id': 'meow_puppet_stayman_over_1n'}`
- Expected public meaning: `{'action_type': 'place_contract', 'target_suit': 'H'}`
- Expected policy: `{'object_id': 'meow_puppet_stayman_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_puppet_2n_opener_answers_four_card_major`

- Auction: `2NP3CP`
- Hand: `SAQ76HKJ8DAQ7CKJ2` -> S AQ76  H KJ8  D AQ7  C KJ2
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3D`
- Expected origin: `{'object_id': 'puppet_2n_answer_3d', 'gadget_id': 'meow_puppet_stayman_over_2n'}`
- Expected public meaning: `{'action_type': 'puppet_answer'}`
- Expected policy: `{'object_id': 'meow_puppet_stayman_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_rkcb_after_texas_is_standalone`

- Auction: `1NP4HP4SP`
- Hand: `SKQJT98HA43DA2CAK` -> ? KQJT98  ? A43  ? A2  ? AK
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4N`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_rkcb_1430'}`

### `meow_bergen_raise_is_standalone`

- Auction: `1SP`
- Hand: `SK987H74DQJ7CK985` -> ? K987  ? 74  ? QJ7  ? K985
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3C`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_bergen_raises'}`

### `meow_drury_is_standalone`

- Auction: `PP1SP`
- Hand: `S987H74DAJ7CKQ854` -> ? 987  ? 74  ? AJ7  ? KQ854
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2C`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_two_way_reverse_drury'}`

### `meow_spade_simple_raise_three_card_support`

- Auction: `1SP`
- Hand: `S987H74DAQ7CK9852` -> ? 987  ? 74  ? AQ7  ? K9852
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2S`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_simple_major_raise'}`
- Expected policy: `{'object_id': 'meow_major_raise_simple_policy', 'algorithm': 'python_bsl_function'}`

### `meow_heart_simple_raise_three_card_support`

- Auction: `1HP`
- Hand: `S72H987DKQ7CA9852` -> ? 72  ? 987  ? KQ7  ? A9852
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2H`
- Expected origin: `{'object_id': 'cs_2', 'gadget_id': 'meow_simple_major_raise'}`
- Expected policy: `{'object_id': 'meow_major_raise_simple_policy', 'algorithm': 'python_bsl_function'}`

### `meow_heart_bergen_constructive_raise`

- Auction: `1HP`
- Hand: `S72HK987DQ87CA982` -> ? 72  ? K987  ? Q87  ? A982
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3C`
- Expected origin: `{'object_id': 'cs_4', 'gadget_id': 'meow_bergen_raises'}`
- Expected public meaning: `{'raise_strength': 'constructive'}`
- Expected policy: `{'object_id': 'meow_major_raise_bergen_policy', 'algorithm': 'python_bsl_function'}`

### `meow_heart_bergen_limit_raise`

- Auction: `1HP`
- Hand: `S72HK987DKQ7CA982` -> ? 72  ? K987  ? KQ7  ? A982
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3D`
- Expected origin: `{'object_id': 'cs_5', 'gadget_id': 'meow_bergen_raises'}`
- Expected public meaning: `{'raise_strength': 'limit'}`
- Expected policy: `{'object_id': 'meow_major_raise_bergen_policy', 'algorithm': 'python_bsl_function'}`

### `meow_heart_bergen_preemptive_raise`

- Auction: `1HP`
- Hand: `S72H9876D987C9852` -> ? 72  ? 9876  ? 987  ? 9852
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3H`
- Expected origin: `{'object_id': 'cs_6', 'gadget_id': 'meow_bergen_raises'}`
- Expected public meaning: `{'raise_strength': 'preemptive'}`
- Expected policy: `{'object_id': 'meow_major_raise_bergen_policy', 'algorithm': 'python_bsl_function'}`

### `meow_heart_any_help_game_try_selected`

- Auction: `1HP2HP`
- Hand: `SAQ2HAKJ74D82C983` -> ? AQ2  ? AKJ74  ? 82  ? 983
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2S`
- Expected origin: `{'object_id': 'cs_6', 'gadget_id': 'meow_kokish_game_tries'}`
- Expected policy: `{'object_id': 'meow_game_try_route', 'algorithm': 'python_bsl_function'}`

### `meow_heart_trump_help_game_try_selected`

- Auction: `1HP2HP`
- Hand: `SAQ2H98754DAK2CK3` -> ? AQ2  ? 98754  ? AK2  ? K3
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2N`
- Expected origin: `{'object_id': 'cs_9', 'gadget_id': 'meow_kokish_game_tries'}`
- Expected policy: `{'object_id': 'meow_game_try_route', 'algorithm': 'python_bsl_function'}`

### `meow_heart_any_help_response_shows_spades`

- Auction: `1HP2HP2SP`
- Hand: `SK72H987DQ76CA982` -> ? K72  ? 987  ? Q76  ? A982
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2N`
- Expected origin: `{'object_id': 'cs_7', 'gadget_id': 'meow_kokish_game_tries'}`
- Expected policy: `{'object_id': 'meow_game_try_route', 'algorithm': 'python_bsl_function'}`

### `meow_rkcb_after_simple_raise_uses_semantic_agreed_suit`

- Auction: `1SP2SP`
- Hand: `SKQJT98HA43DA2CAK` -> ? KQJT98  ? A43  ? A2  ? AK
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4N`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_rkcb_1430'}`

### `meow_rkcb_response_after_simple_raise_uses_semantic_context`

- Auction: `1SP2SP4NP`
- Hand: `SA54H872DK83CQ762` -> ? A54  ? 872  ? K83  ? Q762
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `5C`
- Expected origin: `{'object_id': 'cs_2', 'gadget_id': 'meow_rkcb_1430'}`

### `meow_rkcb_specific_king_ask_after_simple_raise`

- Auction: `1SP2SP4NP5CP`
- Hand: `SKQJT98HA43DA2CAK` -> ? KQJT98  ? A43  ? A2  ? AK
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `5N`
- Expected origin: `{'object_id': 'cs_6', 'gadget_id': 'meow_rkcb_1430'}`

### `meow_rkcb_specific_king_response_after_simple_raise`

- Auction: `1SP2SP4NP5CP5NP`
- Hand: `SA54H872DK83CQ762` -> ? A54  ? 872  ? K83  ? Q762
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `6D`
- Expected origin: `{'object_id': 'cs_7', 'gadget_id': 'meow_rkcb_1430'}`

### `meow_rkcb_grand_placement_after_simple_raise`

- Auction: `1SP2SP4NP5CP5NP6DP`
- Hand: `SKQJT98HA43DA2CAK` -> ? KQJT98  ? A43  ? A2  ? AK
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `7S`
- Expected origin: `{'object_id': 'cs_8', 'gadget_id': 'meow_rkcb_1430'}`

### `meow_quantitative_four_notrump_after_one_notrump`

- Auction: `1NP`
- Hand: `SAQ7HKJ8DKJ6CQ542` -> ? AQ7  ? KJ8  ? KJ6  ? Q542
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4N`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_quantitative_notrump'}`
- Expected public meaning: `{'action_type': 'quantitative_notrump_invite'}`

### `meow_rkcb_not_quantitative_after_texas_sets_agreed_suit`

- Auction: `1NP4HP4SP`
- Hand: `SKQJT98HA43DA2CAK` -> ? KQJT98  ? A43  ? A2  ? AK
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4N`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_rkcb_1430'}`

### `illegal_candidate_is_filtered_after_higher_contract`

- Auction: `1SP2SP5NP`
- Hand: `SKQJT98HA43DA2CAK` -> ? KQJT98  ? A43  ? A2  ? AK
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `P`
- Expected diagnostics include: `['Illegal candidate 4N', 'defaulting to P']`

### `meow_minor_response_bypasses_diamonds_for_hearts`

- Auction: `1CP`
- Hand: `S72HKJ87DQ876C542` -> ? 72  ? KJ87  ? Q876  ? 542
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `1H`
- Expected origin: `{'object_id': 'cs_4', 'gadget_id': 'meow_minor_opening_structure'}`
- Expected diagnostics: `[]`

### `meow_minor_response_bids_one_diamond_without_major`

- Auction: `1CP`
- Hand: `S72H83DKJ87CQ9652` -> ? 72  ? 83  ? KJ87  ? Q9652
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `1D`
- Expected origin: `{'object_id': 'cs_3', 'gadget_id': 'meow_minor_opening_structure'}`
- Compared candidates: `['1D', '1N']`
- Expected diagnostics: `[]`

### `meow_minor_response_one_notrump_six_to_ten`

- Auction: `1CP`
- Hand: `S72HK83DQ87CJ9652` -> ? 72  ? K83  ? Q87  ? J9652
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `1N`
- Expected origin: `{'object_id': 'cs_8', 'gadget_id': 'meow_minor_opening_structure'}`
- Expected public meaning: `{'hcp_range': [6, 10]}`

### `meow_minor_response_two_notrump_eleven_to_twelve`

- Auction: `1CP`
- Hand: `SQ72HK83DAQ7CJ654` -> ? Q72  ? K83  ? AQ7  ? J654
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2N`
- Expected origin: `{'object_id': 'cs_10', 'gadget_id': 'meow_minor_opening_structure'}`
- Expected public meaning: `{'hcp_range': [11, 12]}`

### `meow_minor_response_three_notrump_thirteen_to_fifteen`

- Auction: `1DP`
- Hand: `SA72HK83DQ7CKJ542` -> ? A72  ? K83  ? Q7  ? KJ542
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3N`
- Expected origin: `{'object_id': 'cs_13', 'gadget_id': 'meow_minor_opening_structure'}`
- Expected public meaning: `{'hcp_range': [13, 15]}`

### `meow_minor_weak_jump_shift_spades_is_alertable`

- Auction: `1CP`
- Hand: `SKJ9876H72D83C542` -> ? KJ9876  ? 72  ? 83  ? 542
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2S`
- Expected origin: `{'object_id': 'cs_15', 'gadget_id': 'meow_minor_opening_structure'}`
- Expected public meaning: `{'alertable': True, 'action_type': 'weak_jump_shift'}`

### `meow_inverted_club_raise_invitational_plus`

- Auction: `1CP`
- Hand: `S72H83DAQ7CKJ6542` -> ? 72  ? 83  ? AQ7  ? KJ6542
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2C`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_inverted_minors'}`
- Expected public meaning: `{'alertable': True, 'raise_strength': 'invitational_plus'}`
- Compared candidates: `['2C', '1N']`

### `meow_crisscross_club_raise_game_force`

- Auction: `1CP`
- Hand: `S72HK3DAQ7CKJ6542` -> ? 72  ? K3  ? AQ7  ? KJ6542
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2D`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_crisscross_minor_raises'}`
- Expected public meaning: `{'alertable': True, 'raise_strength': 'game_force'}`
- Compared candidates: `['2D', '2C']`

### `meow_inverted_diamond_raise_invitational_plus`

- Auction: `1DP`
- Hand: `S972H83DKJ876CAQ2` -> ? 972  ? 83  ? KJ876  ? AQ2
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2D`
- Expected origin: `{'object_id': 'cs_2', 'gadget_id': 'meow_inverted_minors'}`
- Expected public meaning: `{'raise_strength': 'invitational_plus'}`
- Compared candidates: `['2D', '1N']`

### `meow_crisscross_diamond_raise_game_force`

- Auction: `1DP`
- Hand: `S972H83DAKJ76CKQ4` -> ? 972  ? 83  ? AKJ76  ? KQ4
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3C`
- Expected origin: `{'object_id': 'cs_2', 'gadget_id': 'meow_crisscross_minor_raises'}`
- Expected public meaning: `{'raise_strength': 'game_force'}`
- Compared candidates: `['3C', '2D', '3N']`

### `meow_inverted_club_raise_opener_rebids_two_notrump_with_stoppers`

- Auction: `1CP2CP`
- Hand: `SA72HK83DQ87CKJ62` -> ? A72  ? K83  ? Q87  ? KJ62
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2N`
- Expected origin: `{'object_id': 'cs_3', 'gadget_id': 'meow_inverted_minors'}`
- Compared candidates: `['2N', '2D', '3C']`
- Expected selected criteria include: `['diamond_stopper', 'heart_stopper', 'spade_stopper']`

### `meow_inverted_club_raise_opener_bids_stopper_up_the_line`

- Auction: `1CP2CP`
- Hand: `SA72H983DKQ7CAJ62` -> ? A72  ? 983  ? KQ7  ? AJ62
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2D`
- Expected origin: `{'object_id': 'cs_4', 'gadget_id': 'meow_inverted_minors'}`
- Expected public meaning: `{'action_type': 'stopper_bid', 'target_suit': 'D'}`

### `meow_inverted_club_raise_game_values_place_three_notrump`

- Auction: `1CP2CP2NP`
- Hand: `S72HK3DAQ7CKJ6542` -> ? 72  ? K3  ? AQ7  ? KJ6542
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3N`
- Expected origin: `{'object_id': 'cs_9', 'gadget_id': 'meow_inverted_minors'}`
- Expected public meaning: `{'action_type': 'place_contract'}`

### `meow_forcing_notrump_response_after_one_spade`

- Auction: `1SP`
- Hand: `S2H87DQJ65CKT9872` -> ? 2  ? 87  ? QJ65  ? KT9872
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `1N`
- Expected origin: `{'object_id': 'fn_3', 'gadget_id': 'meow_forcing_notrump_after_major'}`
- Expected public meaning: `{'action_type': 'forcing_notrump_response'}`
- Expected policy: `{'object_id': 'meow_major_response_forcing_notrump_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_one_heart_one_spade_response`

- Auction: `1HP`
- Hand: `SK987H72D876CAQ52` -> ? K987  ? 72  ? 876  ? AQ52
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `1S`
- Expected origin: `{'object_id': 'fn_1', 'gadget_id': 'meow_forcing_notrump_after_major'}`
- Expected public meaning: `{'action_type': 'one_level_response', 'target_suit': 'S'}`
- Expected diagnostics: `[]`

### `meow_two_over_one_heart_response_after_one_spade`

- Auction: `1SP`
- Hand: `S2HAKJ87DQ76CAQ32` -> ? 2  ? AKJ87  ? Q76  ? AQ32
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2H`
- Expected origin: `{'object_id': 'fn_8', 'gadget_id': 'meow_forcing_notrump_after_major'}`
- Expected public meaning: `{'action_type': 'two_over_one_game_force'}`
- Expected policy: `{'object_id': 'meow_major_response_two_over_one_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_forcing_notrump_opener_repeats_six_spades`

- Auction: `1SP1NP`
- Hand: `SAKJ876H2D84CKQ32` -> ? AKJ876  ? 2  ? 84  ? KQ32
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2S`
- Expected origin: `{'object_id': 'fn_17', 'gadget_id': 'meow_forcing_notrump_after_major'}`
- Expected public meaning: `{'action_type': 'forcing_notrump_opener_rebid', 'target_suit': 'S'}`
- Expected policy: `{'object_id': 'meow_forcing_notrump_opener_rebid', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_forcing_notrump_opener_bids_longer_minor`

- Auction: `1SP1NP`
- Hand: `SAKJ8H72DQ876C432` -> ? AKJ8  ? 72  ? Q876  ? 432
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2D`
- Expected origin: `{'object_id': 'fn_15', 'gadget_id': 'meow_forcing_notrump_after_major'}`
- Expected public meaning: `{'action_type': 'forcing_notrump_opener_rebid', 'target_suit': 'D'}`
- Expected policy: `{'object_id': 'meow_forcing_notrump_opener_rebid', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_spiral_3344_query_after_minor_raise`

- Auction: `1CP1HP2HP`
- Hand: `SK2HAQJ87DK7CQ543` -> ? K2  ? AQJ87  ? K7  ? Q543
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2N`
- Expected origin: `{'object_id': 'sp_1', 'gadget_id': 'meow_spiral_3344'}`
- Expected public meaning: `{'action_type': 'spiral_3344_query', 'alertable': True}`
- Expected policy: `{'object_id': 'meow_minor_responder_rebid', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_spiral_3344_maximum_three_card_answer`

- Auction: `1CP1HP2HP2NP`
- Hand: `SA72HK83DAQ7CKJ62` -> ? A72  ? K83  ? AQ7  ? KJ62
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3D`
- Expected origin: `{'object_id': 'sp_6', 'gadget_id': 'meow_spiral_3344'}`
- Expected public meaning: `{'action_type': 'spiral_3344_answer', 'support_length': 3, 'opener_strength': 'maximum'}`
- Expected diagnostics: `[]`

### `meow_spiral_3344_places_heart_game`

- Auction: `1CP1HP2HP2NP3DP`
- Hand: `SK2HAQJ87DK7CQ543` -> ? K2  ? AQJ87  ? K7  ? Q543
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4H`
- Expected origin: `{'object_id': 'sp_13', 'gadget_id': 'meow_spiral_3344'}`
- Expected public meaning: `{'action_type': 'place_contract', 'target_suit': 'H'}`
- Expected diagnostics: `[]`

### `meow_inverted_club_raise_opener_places_three_notrump_with_extras`

- Auction: `1CP2CP`
- Hand: `SA72HK83DQ87CAKJ4` -> ? A72  ? K83  ? Q87  ? AKJ4
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3N`
- Expected origin: `{'object_id': 'im_17', 'gadget_id': 'meow_inverted_minors'}`
- Expected public meaning: `{'action_type': 'place_contract', 'target_suit': 'N'}`
- Compared candidates: `['3N', '2D', '3C']`
- Expected diagnostics: `[]`

### `meow_minor_opener_rebid_shows_spades_before_three_card_heart_raise`

- Auction: `1CP1HP`
- Hand: `SAQ72HK83D87CKJ62` -> ? AQ72  ? K83  ? 87  ? KJ62
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `1S`
- Expected origin: `{'object_id': 'cs_21', 'gadget_id': 'meow_minor_opening_structure'}`
- Expected public meaning: `{'action_type': 'opener_rebid', 'target_suit': 'S'}`
- Expected policy: `{'object_id': 'meow_minor_opener_rebid', 'algorithm': 'python_bsl_function'}`
- Compared candidates: `['1S', '1N', '2H']`
- Expected diagnostics: `[]`

### `meow_minor_opener_rebid_raises_four_card_heart_support_before_spades`

- Auction: `1CP1HP`
- Hand: `SAQ72HKJ83D7CQ632` -> ? AQ72  ? KJ83  ? 7  ? Q632
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2H`
- Expected origin: `{'object_id': 'cs_23', 'gadget_id': 'meow_minor_opening_structure'}`
- Expected public meaning: `{'action_type': 'raise', 'target_suit': 'H'}`
- Expected policy: `{'object_id': 'meow_minor_opener_rebid', 'algorithm': 'python_bsl_function'}`
- Compared candidates: `['2H', '1S']`
- Expected diagnostics: `[]`

### `meow_minor_opener_rebid_jump_notrump_with_eighteen_nineteen_balanced`

- Auction: `1CP1HP`
- Hand: `SAQ2HK3DAQ7CKJ632` -> ? AQ2  ? K3  ? AQ7  ? KJ632
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2N`
- Expected origin: `{'object_id': 'cs_32', 'gadget_id': 'meow_minor_opening_structure'}`
- Expected public meaning: `{'action_type': 'opener_notrump_rebid', 'target_suit': 'N', 'hcp_range': [18, 19]}`
- Expected policy: `{'object_id': 'meow_minor_opener_rebid', 'algorithm': 'python_bsl_function'}`
- Compared candidates: `['2N', '2C']`
- Expected diagnostics: `[]`

### `meow_minor_opener_rebid_reverse_with_extras`

- Auction: `1CP1SP`
- Hand: `SA2HAKJ7DQ7CKJ632` -> ? A2  ? AKJ7  ? Q7  ? KJ632
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2H`
- Expected origin: `{'object_id': 'cs_45', 'gadget_id': 'meow_minor_opening_structure'}`
- Expected public meaning: `{'action_type': 'opener_reverse', 'target_suit': 'H'}`
- Expected policy: `{'object_id': 'meow_minor_opener_rebid', 'algorithm': 'python_bsl_function'}`
- Compared candidates: `['2H', '2C']`
- Expected diagnostics: `[]`

### `meow_minor_opener_rebid_jump_raise_with_extras`

- Auction: `1DP1SP`
- Hand: `SAQ72H83DAKJ7CK32` -> ? AQ72  ? 83  ? AKJ7  ? K32
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3S`
- Expected origin: `{'object_id': 'cs_50', 'gadget_id': 'meow_minor_opening_structure'}`
- Expected public meaning: `{'action_type': 'opener_jump_raise', 'target_suit': 'S'}`
- Expected policy: `{'object_id': 'meow_minor_opener_rebid', 'algorithm': 'python_bsl_function'}`
- Compared candidates: `['3S']`
- Expected diagnostics: `[]`

### `meow_minor_opener_rebid_rebids_long_diamonds_over_lower_second_suit`

- Auction: `1DP1HP`
- Hand: `S72HK3DKJ876CAQ42` -> ? 72  ? K3  ? KJ876  ? AQ42
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2D`
- Expected origin: `{'object_id': 'cs_39', 'gadget_id': 'meow_minor_opening_structure'}`
- Expected public meaning: `{'action_type': 'opener_minor_rebid', 'target_suit': 'D'}`
- Expected policy: `{'object_id': 'meow_minor_opener_rebid', 'algorithm': 'python_bsl_function'}`
- Compared candidates: `['2D', '2C']`
- Expected diagnostics: `[]`

### `meow_minor_opener_rebid_one_club_one_diamond_shows_hearts_first`

- Auction: `1CP1DP`
- Hand: `SAQ72HKJ83D7CQ632` -> ? AQ72  ? KJ83  ? 7  ? Q632
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `1H`
- Expected origin: `{'object_id': 'cs_18', 'gadget_id': 'meow_minor_opening_structure'}`
- Expected public meaning: `{'action_type': 'opener_rebid', 'target_suit': 'H'}`
- Expected policy: `{'object_id': 'meow_minor_opener_rebid', 'algorithm': 'python_bsl_function'}`
- Compared candidates: `['1H']`
- Expected diagnostics: `[]`

### `meow_minor_opener_strong_jump_shift_shows_minor_and_four_card_major`

- Auction: `1CP1DP`
- Hand: `SA2HAKJ7D87CAKJ63` -> ? A2  ? AKJ7  ? 87  ? AKJ63
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2H`
- Expected origin: `{'object_id': 'cs_51', 'gadget_id': 'meow_minor_opening_structure'}`
- Expected public meaning: `{'action_type': 'opener_jump_shift', 'target_suit': 'H', 'shown_length_min': 4}`
- Expected policy: `{'object_id': 'meow_minor_opener_rebid', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_two_way_nmf_two_club_invitational_relay`

- Auction: `1CP1HP1NP`
- Hand: `SA72HKQJ83D87CQ54` -> ? A72  ? KQJ83  ? 87  ? Q54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2C`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_two_way_nmf_xyz'}`
- Expected public meaning: `{'alertable': True, 'action_type': 'checkback_two_club_relay'}`
- Expected policy: `{'object_id': 'meow_minor_responder_rebid', 'algorithm': 'python_bsl_function'}`

### `meow_one_diamond_response_notrump_rebid_records_negative_major_state`

- Auction: `1CP1DP1NP`
- Hand: `SA72HKJ3DQ876CQ54` -> ? A72  ? KJ3  ? Q876  ? Q54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2C`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_two_way_nmf_xyz'}`
- Expected policy: `{'object_id': 'meow_minor_responder_rebid', 'algorithm': 'python_bsl_function'}`
- Expected state records include: `[{'key': 'opener.hcp', 'owner': 'opener', 'min_value': 12, 'max_value': 14}, {'key': 'opener.length.H', 'owner': 'opener', 'max_value': 3}, {'key': 'opener.length.S', 'owner': 'opener', 'max_value': 3}]`

### `meow_two_way_nmf_two_diamond_game_force`

- Auction: `1CP1HP1NP`
- Hand: `SA72HAJ873D87CKQ4` -> ? A72  ? AJ873  ? 87  ? KQ4
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2D`
- Expected origin: `{'object_id': 'cs_2', 'gadget_id': 'meow_two_way_nmf_xyz'}`
- Expected public meaning: `{'alertable': True, 'action_type': 'checkback_game_force'}`
- Expected policy: `{'object_id': 'meow_minor_responder_rebid', 'algorithm': 'python_bsl_function'}`

### `meow_long_hearts_uses_force_route_before_rebidding`

- Auction: `1CP1HP1SP`
- Hand: `SQ7HAKQ9876DKJC54` -> ? Q7  ? AKQ9876  ? KJ  ? 54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2D`
- Expected origin: `{'object_id': 'cs_2', 'gadget_id': 'meow_two_way_nmf_xyz'}`
- Expected public meaning: `{'alertable': True, 'action_type': 'checkback_game_force'}`
- Expected policy: `{'object_id': 'meow_minor_responder_rebid', 'algorithm': 'python_bsl_function'}`
- Expected state records include: `[{'key': 'responder.length.H', 'owner': 'responder', 'min_value': 4}, {'key': 'opener.length.S', 'owner': 'opener', 'min_value': 4}, {'key': 'opener.length.H', 'owner': 'opener', 'max_value': 3}]`
- Expected selected criteria include: `['force_before_long_suit_rebid']`

### `meow_xyz_two_notrump_club_drop_dead_relay`

- Auction: `1CP1DP1HP`
- Hand: `S72H83D876CJ87652` -> ? 72  ? 83  ? 876  ? J87652
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2N`
- Expected origin: `{'object_id': 'cs_3', 'gadget_id': 'meow_two_way_nmf_xyz'}`
- Expected public meaning: `{'alertable': True, 'action_type': 'checkback_two_notrump_club_relay'}`
- Expected policy: `{'object_id': 'meow_minor_responder_rebid', 'algorithm': 'python_bsl_function'}`

### `meow_xyz_two_club_diamond_drop_dead_relay`

- Auction: `1CP1DP1NP`
- Hand: `S72H83DJ8765C5423` -> ? 72  ? 83  ? J8765  ? 5423
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2C`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_two_way_nmf_xyz'}`
- Expected public meaning: `{'alertable': True, 'action_type': 'checkback_two_club_relay'}`
- Expected policy: `{'object_id': 'meow_minor_responder_rebid', 'algorithm': 'python_bsl_function'}`

### `meow_minor_responder_rebids_long_major_to_sign_off`

- Auction: `1CP1HP1SP`
- Hand: `S7HQT9876D83CQ542` -> ? 7  ? QT9876  ? 83  ? Q542
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2H`
- Expected origin: `{'object_id': 'cs_55', 'gadget_id': 'meow_minor_opening_structure'}`
- Expected public meaning: `{'action_type': 'responder_major_rebid', 'target_suit': 'H', 'shown_length_min': 6}`
- Expected policy: `{'object_id': 'meow_minor_responder_rebid', 'algorithm': 'python_bsl_function'}`

### `meow_xyz_club_drop_dead_opener_completes_three_clubs`

- Auction: `1CP1DP1HP2NP`
- Hand: `SA72HK83D87CQ6542` -> ? A72  ? K83  ? 87  ? Q6542
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3C`
- Expected origin: `{'object_id': 'cs_9', 'gadget_id': 'meow_two_way_nmf_xyz'}`
- Expected public meaning: `{'alertable': True, 'action_type': 'checkback_club_relay_completion'}`

### `meow_weak_two_favorable_first_seat`

- Auction: ``
- Hand: `S72HKQ9876D83C542` -> ? 72  ? KQ9876  ? 83  ? 542
- Environment: dealer=n, vulnerability=ew, scoring=IMP
- Expected call: `2H`
- Expected origin: `{'object_id': 'cs_2', 'gadget_id': 'meow_preemptive_openings'}`
- Expected public meaning: `{'alertable': False, 'action_type': 'weak_two_opening'}`

### `meow_second_seat_six_hcp_good_suit_weak_two_passes`

- Auction: `P`
- Hand: `S72HKQ9876DJ3C542` -> ? 72  ? KQ9876  ? J3  ? 542
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `P`
- Expected diagnostics: `[]`

### `meow_second_seat_sound_weak_two_opens`

- Auction: `P`
- Hand: `S72HKQ9876DK3C542` -> ? 72  ? KQ9876  ? K3  ? 542
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2H`
- Expected origin: `{'object_id': 'cs_2', 'gadget_id': 'meow_preemptive_openings'}`
- Expected policy: `{'object_id': 'meow_opening_preempt_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_weak_two_unfavorable_bad_hand_passes`

- Auction: ``
- Hand: `S72HJT9876D83C542` -> ? 72  ? JT9876  ? 83  ? 542
- Environment: dealer=n, vulnerability=ns, scoring=IMP
- Expected call: `P`
- Expected diagnostics: `[]`

### `meow_weak_two_unfavorable_good_hand_opens`

- Auction: ``
- Hand: `SA72HKQ9876D83C54` -> ? A72  ? KQ9876  ? 83  ? 54
- Environment: dealer=n, vulnerability=ns, scoring=IMP
- Expected call: `2H`
- Expected origin: `{'object_id': 'cs_2', 'gadget_id': 'meow_preemptive_openings'}`

### `meow_third_seat_light_weak_two_opens`

- Auction: `PP`
- Hand: `S72HJT9876DK3C542` -> ? 72  ? JT9876  ? K3  ? 542
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2H`
- Expected origin: `{'object_id': 'cs_2', 'gadget_id': 'meow_preemptive_openings'}`

### `meow_fourth_seat_weak_two_style_passes`

- Auction: `PPP`
- Hand: `SA72HKQ9876D83C54` -> ? A72  ? KQ9876  ? 83  ? 54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `P`
- Expected origin: `{'object_id': 'cs_7', 'gadget_id': 'meow_two_over_one_core'}`
- Expected policy: `{'object_id': 'meow_opening_fourth_seat_pass_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_three_spade_preempt_selected_over_weak_two_with_seven_cards`

- Auction: ``
- Hand: `SKQJ9876H72D83C54` -> ? KQJ9876  ? 72  ? 83  ? 54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3S`
- Expected origin: `{'object_id': 'cs_7', 'gadget_id': 'meow_preemptive_openings'}`
- Compared candidates: `['3S', '2S', 'P']`

### `meow_gambling_three_notrump_clubs_alertable`

- Auction: ``
- Hand: `S87H83D76CAKQJ987` -> ? 87  ? 83  ? 76  ? AKQJ987
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3N`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_gambling_3nt'}`
- Expected public meaning: `{'alertable': True, 'action_type': 'gambling_3nt_opening'}`
- Compared candidates: `['3N', '3C', '1C', 'P']`

### `meow_two_notrump_opening_balanced_twenty_count`

- Auction: ``
- Hand: `SAQ7HKJ8DAQ7CKJ54` -> ? AQ7  ? KJ8  ? AQ7  ? KJ54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2N`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_two_notrump_opening'}`
- Expected public meaning: `{'action_type': 'opening', 'target_suit': 'N'}`
- Expected policy: `{'object_id': 'meow_opening_strong_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_one_diamond_opening_with_longer_diamonds`

- Auction: ``
- Hand: `SA72HK83DKQ87C982` -> ? A72  ? K83  ? KQ87  ? 982
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `1D`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_minor_opening_structure'}`
- Expected public meaning: `{'action_type': 'opening', 'target_suit': 'D'}`
- Expected policy: `{'object_id': 'meow_opening_one_level_seat_1_2_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_one_club_opening_with_longer_clubs`

- Auction: ``
- Hand: `SA72HK83DQ87CKJ62` -> ? A72  ? K83  ? Q87  ? KJ62
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `1C`
- Expected origin: `{'object_id': 'cs_2', 'gadget_id': 'meow_minor_opening_structure'}`
- Expected public meaning: `{'action_type': 'opening', 'target_suit': 'C'}`
- Expected policy: `{'object_id': 'meow_opening_one_level_seat_1_2_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_no_opening_values_defaults_to_pass`

- Auction: ``
- Hand: `S872H83DQ87CKJ652` -> ? 872  ? 83  ? Q87  ? KJ652
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `P`
- Expected diagnostics: `[]`

### `meow_spade_transfer_over_one_notrump`

- Auction: `1NP`
- Hand: `SJ9832H974D976C52` -> ? J9832  ? 974  ? 976  ? 52
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2H`
- Expected origin: `{'object_id': 'cs_2', 'gadget_id': 'meow_four_way_transfers_over_1n'}`
- Expected public meaning: `{'action_type': 'transfer', 'target_suit': 'S'}`
- Expected policy: `{'object_id': 'meow_1n_weak_partscore_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_spade_transfer_superaccept_selected`

- Auction: `1NP2HP`
- Hand: `SAQ74HKJ83DA62CQ5` -> ? AQ74  ? KJ83  ? A62  ? Q5
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3S`
- Expected origin: `{'object_id': 'cs_12', 'gadget_id': 'meow_four_way_transfers_over_1n'}`
- Expected public meaning: `{'action_type': 'superaccept', 'target_suit': 'S'}`
- Compared candidates: `['3S', '2S']`
- Expected diagnostics: `[]`
- Expected selected criteria include: `['pending_spade_transfer', 'four_spade_support', 'maximum_notrump_values']`

### `meow_diamond_transfer_normal_accept_without_honor_third`

- Auction: `1NP2NP`
- Hand: `SA54HKQ2D876CQJ75` -> ? A54  ? KQ2  ? 876  ? QJ75
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3D`
- Expected origin: `{'object_id': 'cs_9', 'gadget_id': 'meow_four_way_transfers_over_1n'}`
- Expected public meaning: `{'action_type': 'transfer_completion', 'target_suit': 'D'}`
- Expected diagnostics: `[]`

### `meow_texas_heart_transfer_game_values`

- Auction: `1NP`
- Hand: `S72HAQJ987D53CK42` -> ? 72  ? AQJ987  ? 53  ? K42
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4D`
- Expected origin: `{'object_id': 'cs_3', 'gadget_id': 'meow_texas_transfers_over_1n'}`
- Expected public meaning: `{'action_type': 'texas_transfer', 'target_suit': 'H'}`
- Expected policy: `{'object_id': 'meow_1n_major_transfer_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_texas_spade_transfer_game_values`

- Auction: `1NP`
- Hand: `SKQJ987H72D53CA42` -> ? KQJ987  ? 72  ? 53  ? A42
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4H`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_texas_transfers_over_1n'}`
- Expected public meaning: `{'action_type': 'texas_transfer', 'target_suit': 'S'}`
- Expected policy: `{'object_id': 'meow_1n_major_transfer_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_direct_three_notrump_over_one_notrump`

- Auction: `1NP`
- Hand: `SKQ7HQJ8DQ76CKJ54` -> ? KQ7  ? QJ8  ? Q76  ? KJ54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3N`
- Expected origin: `{'object_id': 'ntb_2', 'gadget_id': 'meow_notrump_response_basics'}`
- Expected public meaning: `{'action_type': 'place_contract', 'target_suit': 'N'}`
- Expected policy: `{'object_id': 'meow_1n_terminal_notrump_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_five_five_minors_game_force_over_one_notrump`

- Auction: `1NP`
- Hand: `S2H43DAQJ87CKQJ76` -> ? 2  ? 43  ? AQJ87  ? KQJ76
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3D`
- Expected origin: `{'object_id': 'ntb_3', 'gadget_id': 'meow_notrump_response_basics'}`
- Expected public meaning: `{'action_type': 'five_five_minors_game_force', 'alertable': True}`
- Expected policy: `{'object_id': 'meow_1n_two_suiter_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_five_five_majors_invitational_over_one_notrump`

- Auction: `1NP`
- Hand: `SKJ987HQJ987D3CQ2` -> ? KJ987  ? QJ987  ? 3  ? Q2
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3H`
- Expected origin: `{'object_id': 'ntb_4', 'gadget_id': 'meow_notrump_response_basics'}`
- Expected public meaning: `{'action_type': 'five_five_majors_invitational', 'alertable': True}`
- Expected policy: `{'object_id': 'meow_1n_two_suiter_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_five_five_majors_game_force_over_one_notrump`

- Auction: `1NP`
- Hand: `SKQ987HAQJ87D3C42` -> ? KQ987  ? AQJ87  ? 3  ? 42
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3S`
- Expected origin: `{'object_id': 'ntb_5', 'gadget_id': 'meow_notrump_response_basics'}`
- Expected public meaning: `{'action_type': 'five_five_majors_game_force', 'alertable': True}`
- Expected policy: `{'object_id': 'meow_1n_two_suiter_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_quantitative_four_notrump_without_agreed_suit`

- Auction: `1NP`
- Hand: `SAQ7HKJ8DQ76CKJ54` -> ? AQ7  ? KJ8  ? Q76  ? KJ54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4N`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_quantitative_notrump'}`
- Expected public meaning: `{'action_type': 'quantitative_notrump_invite', 'target_suit': 'N'}`
- Expected diagnostics: `[]`

### `meow_spade_jacoby_two_notrump_major_raise`

- Auction: `1SP`
- Hand: `SK987H74DAKQCAQ85` -> ? K987  ? 74  ? AKQ  ? AQ85
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2N`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_jacoby_2nt_major_raise'}`
- Expected public meaning: `{'action_type': 'jacoby_2n', 'target_suit': 'S'}`
- Expected policy: `{'object_id': 'meow_major_raise_jacoby_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_heart_jacoby_two_notrump_major_raise`

- Auction: `1HP`
- Hand: `S72HAQ87DKQ7CA982` -> ? 72  ? AQ87  ? KQ7  ? A982
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2N`
- Expected origin: `{'object_id': 'cs_2', 'gadget_id': 'meow_jacoby_2nt_major_raise'}`
- Expected public meaning: `{'action_type': 'jacoby_2n', 'target_suit': 'H'}`
- Expected policy: `{'object_id': 'meow_major_raise_jacoby_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_heart_drury_three_card_support`

- Auction: `PP1HP`
- Hand: `S754HA87DQJ7CKQ85` -> ? 754  ? A87  ? QJ7  ? KQ85
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2C`
- Expected origin: `{'object_id': 'cs_3', 'gadget_id': 'meow_two_way_reverse_drury'}`
- Expected public meaning: `{'action_type': 'two_way_reverse_drury', 'target_suit': 'H', 'support_length': 3}`
- Expected diagnostics: `[]`

### `meow_heart_drury_four_card_support`

- Auction: `PP1HP`
- Hand: `S754HAQ87DJ7CK985` -> ? 754  ? AQ87  ? J7  ? K985
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2D`
- Expected origin: `{'object_id': 'cs_4', 'gadget_id': 'meow_two_way_reverse_drury'}`
- Expected public meaning: `{'action_type': 'two_way_reverse_drury', 'target_suit': 'H', 'support_length_min': 4}`
- Expected diagnostics: `[]`

### `meow_spade_any_help_game_try_selected`

- Auction: `1SP2SP`
- Hand: `SAKJ76H82D82CAQ43` -> ? AKJ76  ? 82  ? 82  ? AQ43
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2N`
- Expected origin: `{'object_id': 'cs_3', 'gadget_id': 'meow_kokish_game_tries'}`
- Expected public meaning: `{'action_type': 'help_suit_game_try', 'agreed_suit': 'S', 'ask_scope': 'any_help'}`
- Expected policy: `{'object_id': 'meow_game_try_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_spade_trump_help_game_try_selected`

- Auction: `1SP2SP`
- Hand: `S98765HAKQD82CKQ3` -> ? 98765  ? AKQ  ? 82  ? KQ3
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3S`
- Expected origin: `{'object_id': 'cs_4', 'gadget_id': 'meow_kokish_game_tries'}`
- Expected public meaning: `{'action_type': 'trump_help_game_try', 'target_suit': 'S'}`
- Expected policy: `{'object_id': 'meow_game_try_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `ambiguous_same_call_meaning_reports_diagnostic`

- Auction: ``
- Hand: `SAQ7HKJ8DKJ6CQ542` -> ? AQ7  ? KJ8  ? KJ6  ? Q542
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4N`
- Expected diagnostics include: `['Ambiguous meaning for call 4N']`

### `meow_strong_two_club_very_strong_unbalanced_opens_two_club`

- Auction: ``
- Hand: `SAKQJT98HAK2DA2C3` -> ? AKQJT98  ? AK2  ? A2  ? 3
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2C`
- Expected origin: `{'object_id': 'cs_1', 'gadget_id': 'meow_strong_two_club'}`
- Expected policy: `{'object_id': 'meow_opening_strong_policy', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_strong_two_club_positive_values_still_bid_waiting_two_diamond`

- Auction: `2CP`
- Hand: `SAQJ87HK2DA76CQ54` -> ? AQJ87  ? K2  ? A76  ? Q54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2D`
- Expected origin: `{'object_id': 'cs_2', 'gadget_id': 'meow_strong_two_club'}`
- Expected policy: `{'object_id': 'meow_strong_two_club_response', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_strong_two_club_balanced_25_rebids_three_notrump`

- Auction: `2CP2DP`
- Hand: `SAKQHAKQDQJ2CKQ3X` -> ? AKQ  ? AKQ  ? QJ2  ? KQ3X
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3N`
- Expected origin: `{'object_id': 'cs_12', 'gadget_id': 'meow_strong_two_club'}`
- Expected public meaning: `{'action_type': 'strong_two_club_three_notrump_rebid'}`
- Expected policy: `{'object_id': 'meow_strong_two_club_opener_rebid', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_strong_two_club_equal_majors_rebids_hearts_first`

- Auction: `2CP2DP`
- Hand: `SAKQJ2HAKQJ2D2CA2` -> ? AKQJ2  ? AKQJ2  ? 2  ? A2
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2H`
- Expected origin: `{'object_id': 'cs_8', 'gadget_id': 'meow_strong_two_club'}`
- Expected public meaning: `{'action_type': 'strong_two_club_suit_rebid', 'target_suit': 'H'}`
- Expected policy: `{'object_id': 'meow_strong_two_club_opener_rebid', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_strong_two_club_second_negative_after_diamonds_uses_three_notrump`

- Auction: `2CP2DP3DP`
- Hand: `S987H765D432C9872` -> ? 987  ? 765  ? 432  ? 9872
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3N`
- Expected origin: `{'object_id': 'cs_16', 'gadget_id': 'meow_strong_two_club'}`
- Expected public meaning: `{'action_type': 'strong_two_club_second_negative'}`
- Expected policy: `{'object_id': 'meow_strong_two_club_responder_rebid', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_strong_two_club_two_notrump_true_bust_passes`

- Auction: `2CP2DP2NP`
- Hand: `S987H765D432C9872` -> ? 987  ? 765  ? 432  ? 9872
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `P`
- Expected origin: `{'object_id': 'cs_17', 'gadget_id': 'meow_strong_two_club'}`
- Expected policy: `{'object_id': 'meow_strong_two_club_responder_rebid', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_strong_two_club_two_notrump_transfers_to_hearts`

- Auction: `2CP2DP2NP`
- Hand: `S72HAQ987D543C62X` -> ? 72  ? AQ987  ? 543  ? 62X
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3D`
- Expected origin: `{'object_id': 'cs_19', 'gadget_id': 'meow_strong_two_club'}`
- Expected public meaning: `{'action_type': 'transfer', 'target_suit': 'H'}`
- Expected policy: `{'object_id': 'meow_strong_two_club_responder_rebid', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_strong_two_club_two_notrump_uses_puppet_with_four_card_major`

- Auction: `2CP2DP2NP`
- Hand: `S9876H765D432CK98` -> ? 9876  ? 765  ? 432  ? K98
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3C`
- Expected origin: `{'object_id': 'cs_18', 'gadget_id': 'meow_strong_two_club'}`
- Expected public meaning: `{'action_type': 'puppet_stayman'}`
- Expected policy: `{'object_id': 'meow_strong_two_club_responder_rebid', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_weak_two_heart_responder_uses_ogust_with_game_interest`

- Auction: `2HP`
- Hand: `SAJ4HKQ5DAQ4C854X` -> ? AJ4  ? KQ5  ? AQ4  ? 854X
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2N`
- Expected origin: `{'object_id': 'cs_27', 'gadget_id': 'meow_preemptive_openings'}`
- Expected public meaning: `{'action_type': 'ogust_inquiry', 'target_suit': 'H'}`
- Expected policy: `{'object_id': 'meow_weak_two_responder_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_weak_two_heart_responder_bids_forcing_spades_with_misfit`

- Auction: `2HP`
- Hand: `SAQJ987H4DKQ3CA4X` -> ? AQJ987  ? 4  ? KQ3  ? A4X
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `2S`
- Expected origin: `{'object_id': 'cs_30', 'gadget_id': 'meow_preemptive_openings'}`
- Expected public meaning: `{'action_type': 'new_suit_forcing_over_preempt', 'target_suit': 'S'}`
- Expected policy: `{'object_id': 'meow_weak_two_responder_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_weak_two_spade_responder_raises_to_game_without_ogust`

- Auction: `2SP`
- Hand: `SAJ4H65XDAQ4CQ854` -> ? AJ4  ? 65X  ? AQ4  ? Q854
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `4S`
- Expected origin: `{'object_id': 'cs_36', 'gadget_id': 'meow_preemptive_openings'}`
- Expected policy: `{'object_id': 'meow_weak_two_responder_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_weak_two_spade_responder_simple_raise`

- Auction: `2SP`
- Hand: `S984H65XDAQ4CJ854` -> ? 984  ? 65X  ? AQ4  ? J854
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3S`
- Expected origin: `{'object_id': 'cs_35', 'gadget_id': 'meow_preemptive_openings'}`
- Expected policy: `{'object_id': 'meow_weak_two_responder_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_weak_two_heart_responder_passes_misfit`

- Auction: `2HP`
- Hand: `SK74H5XDAQ74CJ854` -> ? K74  ? 5X  ? AQ74  ? J854
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `P`
- Expected origin: `{'object_id': 'cs_26', 'gadget_id': 'meow_preemptive_openings'}`
- Expected policy: `{'object_id': 'meow_weak_two_responder_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_ogust_heart_minimum_poor_suit_answers_three_clubs`

- Auction: `2HP2NP`
- Hand: `S72HJT8765D43C82X` -> ? 72  ? JT8765  ? 43  ? 82X
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3C`
- Expected origin: `{'object_id': 'cs_45', 'gadget_id': 'meow_preemptive_openings'}`
- Expected public meaning: `{'action_type': 'ogust_response', 'hand_quality': 'minimum', 'suit_quality': 'poor'}`
- Expected policy: `{'object_id': 'meow_ogust_answer_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_ogust_heart_minimum_good_suit_answers_three_diamonds`

- Auction: `2HP2NP`
- Hand: `S72HKQ8765D43C82X` -> ? 72  ? KQ8765  ? 43  ? 82X
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3D`
- Expected origin: `{'object_id': 'cs_46', 'gadget_id': 'meow_preemptive_openings'}`
- Expected public meaning: `{'action_type': 'ogust_response', 'hand_quality': 'minimum', 'suit_quality': 'good'}`
- Expected policy: `{'object_id': 'meow_ogust_answer_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_ogust_heart_maximum_poor_suit_answers_three_hearts`

- Auction: `2HP2NP`
- Hand: `S72HJ98765DAK3C82` -> ? 72  ? J98765  ? AK3  ? 82
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3H`
- Expected origin: `{'object_id': 'cs_47', 'gadget_id': 'meow_preemptive_openings'}`
- Expected public meaning: `{'action_type': 'ogust_response', 'hand_quality': 'maximum', 'suit_quality': 'poor'}`
- Expected policy: `{'object_id': 'meow_ogust_answer_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_ogust_heart_maximum_good_suit_answers_three_spades`

- Auction: `2HP2NP`
- Hand: `S72HKQ8765DA3C82X` -> ? 72  ? KQ8765  ? A3  ? 82X
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3S`
- Expected origin: `{'object_id': 'cs_48', 'gadget_id': 'meow_preemptive_openings'}`
- Expected public meaning: `{'action_type': 'ogust_response', 'hand_quality': 'maximum', 'suit_quality': 'good'}`
- Expected policy: `{'object_id': 'meow_ogust_answer_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_ogust_heart_solid_suit_answers_three_notrump`

- Auction: `2HP2NP`
- Hand: `S72HAKQ765D43C82X` -> ? 72  ? AKQ765  ? 43  ? 82X
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3N`
- Expected origin: `{'object_id': 'cs_49', 'gadget_id': 'meow_preemptive_openings'}`
- Expected public meaning: `{'action_type': 'ogust_response', 'suit_quality': 'solid'}`
- Expected policy: `{'object_id': 'meow_ogust_answer_route', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_new_suit_forcing_opener_supports_spades`

- Auction: `2HP2SP`
- Hand: `S987HKT8765D32C2X` -> ? 987  ? KT8765  ? 32  ? 2X
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3S`
- Expected origin: `{'object_id': 'cs_57', 'gadget_id': 'meow_preemptive_openings'}`
- Expected public meaning: `{'action_type': 'support_new_suit_forcing', 'target_suit': 'S'}`
- Expected policy: `{'object_id': 'meow_new_suit_forcing_rebid', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

### `meow_new_suit_forcing_opener_rebids_preempt_suit_without_support`

- Auction: `2HP2SP`
- Hand: `S7HKT8765D932C82X` -> ? 7  ? KT8765  ? 932  ? 82X
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected call: `3H`
- Expected origin: `{'object_id': 'cs_58', 'gadget_id': 'meow_preemptive_openings'}`
- Expected public meaning: `{'action_type': 'rebid_preempt_suit', 'target_suit': 'H'}`
- Expected policy: `{'object_id': 'meow_new_suit_forcing_rebid', 'algorithm': 'python_bsl_function'}`
- Expected diagnostics: `[]`

## Full-Auction Simulations

### `meow_spade_help_suit_game_try_reaches_game`

- N: `SAQJ76H82DQ82CAJ3` -> ? AQJ76  ? 82  ? Q82  ? AJ3
- S: `SK98H74DKJ7CK9852` -> ? K98  ? 74  ? KJ7  ? K9852
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `1SP2SP3DP4SPPP`
- Expected controlled calls: `['1S', '2S', '3D', '4S', 'P']`
- Expected diagnostics: `[]`

### `meow_texas_rkcb_specific_king_reaches_grand`

- N: `SA54HKQ2DK83CQJ76` -> ? A54  ? KQ2  ? K83  ? QJ76
- S: `SKQJT98HA43DA2CAK` -> ? KQJT98  ? A43  ? A2  ? AK
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `1NP4HP4SP4NP5CP5NP6DP7SPPP`
- Expected controlled calls: `['1N', '4H', '4S', '4N', '5C', '5N', '6D', '7S', 'P']`
- Expected diagnostics: `[]`

### `meow_simple_raise_rkcb_specific_king_reaches_grand`

- N: `SKQJT98HA43DA2CAK` -> ? KQJT98  ? A43  ? A2  ? AK
- S: `SA54H872DK83CQ762` -> ? A54  ? 872  ? K83  ? Q762
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `1SP2SP4NP5CP5NP6DP7SPPP`
- Expected controlled calls: `['1S', '2S', '4N', '5C', '5N', '6D', '7S', 'P']`
- Expected diagnostics: `[]`

### `meow_heart_any_help_game_try_reaches_game`

- N: `SAQ2HAKJ74D82C983` -> ? AQ2  ? AKJ74  ? 82  ? 983
- S: `SK72H987DQ76CA982` -> ? K72  ? 987  ? Q76  ? A982
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `1HP2HP2SP2NP4HPPP`
- Expected controlled calls: `['1H', '2H', '2S', '2N', '4H', 'P']`
- Expected diagnostics: `[]`

### `meow_inverted_minor_invite_stops_in_two_notrump`

- N: `SA72HK83DQ87CKJ62` -> ? A72  ? K83  ? Q87  ? KJ62
- S: `S72H83DAQ7CKJ6542` -> ? 72  ? 83  ? AQ7  ? KJ6542
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `1CP2CP2NPPP`
- Expected controlled calls: `['1C', '2C', '2N', 'P']`
- Expected diagnostics: `[]`

### `meow_forcing_notrump_sequence_stops_in_two_spades`

- N: `SAKJ876H2D84CKQ32` -> ? AKJ876  ? 2  ? 84  ? KQ32
- S: `S2H87DQJ65CKT9872` -> ? 2  ? 87  ? QJ65  ? KT9872
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `1SP1NP2SPPP`
- Expected controlled calls: `['1S', '1N', '2S', 'P']`
- Expected diagnostics: `[]`

### `meow_forcing_notrump_invite_is_accepted`

- N: `SAKJ76H2DAQ4CK432` -> S AKJ76  H 2  D AQ4  C K432
- S: `S2HA87DKQ65CQ9872` -> S 2  H A87  D KQ65  C Q9872
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `1SP1NP2CP2NP3NPPP`
- Expected controlled calls: `['1S', '1N', '2C', '2N', '3N', 'P']`
- Expected diagnostics: `[]`

### `meow_two_over_one_six_spade_rebid_places_three_notrump`

- N: `SAKJ765H2DQ8CK432` -> S AKJ765  H 2  D Q8  C K432
- S: `S2HA87DAK65CQ9872` -> S 2  H A87  D AK65  C Q9872
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `1SP2CP2SP3NPPP`
- Expected controlled calls: `['1S', '2C', '2S', '3N', 'P']`
- Expected diagnostics: `[]`

### `meow_two_over_one_six_spade_rebid_finds_game_fit`

- N: `SAKJ765H2DQ8CK432` -> S AKJ765  H 2  D Q8  C K432
- S: `S82HA87DAK65CQ987` -> S 82  H A87  D AK65  C Q987
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `1SP2DP2SP4SPPP`
- Expected controlled calls: `['1S', '2D', '2S', '4S', 'P']`
- Expected diagnostics: `[]`

### `meow_crisscross_game_force_reaches_three_notrump`

- N: `SA72HK83DQ87CKJ62` -> ? A72  ? K83  ? Q87  ? KJ62
- S: `S72HK3DAQ7CKJ6542` -> ? 72  ? K3  ? AQ7  ? KJ6542
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `1CP2DP3NPPP`
- Expected controlled calls: `['1C', '2D', '3N', 'P']`
- Expected diagnostics: `[]`

### `meow_crisscross_fallback_reaches_club_game`

- N: `SA72HA83D87CKJ762` -> S A72  H A83  D 87  C KJ762
- S: `S72H3DAKQ72CAQT84` -> S 72  H 3  D AKQ72  C AQT84
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `1CP2DP3CP5CPPP`
- Expected controlled calls: `['1C', '2D', '3C', '5C', 'P']`
- Expected diagnostics: `[]`

### `meow_xyz_two_notrump_relay_drops_in_three_clubs`

- N: `SA72HK873D87CKQ64` -> ? A72  ? K873  ? 87  ? KQ64
- S: `S72H8DKQ76CJ87652` -> ? 72  ? 8  ? KQ76  ? J87652
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `1CP1DP1HP2NP3CPPP`
- Expected controlled calls: `['1C', '1D', '1H', '2N', '3C', 'P']`
- Expected diagnostics: `[]`

### `meow_gambling_three_notrump_full_auction`

- N: `S87H83D76CAKQJ987` -> ? 87  ? 83  ? 76  ? AKQJ987
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `3NPPP`
- Expected controlled calls: `['3N']`
- Expected diagnostics: `[]`

### `meow_direct_three_notrump_over_one_notrump_full_auction`

- N: `SAQ7HKJ8DA762CQ54` -> ? AQ7  ? KJ8  ? A762  ? Q54
- S: `SKQ7HQJ8DQ76CKJ54` -> ? KQ7  ? QJ8  ? Q76  ? KJ54
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `1NP3NPPP`
- Expected controlled calls: `['1N', '3N', 'P']`
- Expected diagnostics: `[]`

### `meow_puppet_four_four_spade_fit_reaches_game`

- N: `SAQ76HKJ8DA76CQ54` -> S AQ76  H KJ8  D A76  C Q54
- S: `S9876H76DAJ4CKQ72` -> S 9876  H 76  D AJ4  C KQ72
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `1NP3CP3DP3HP4SPPP`
- Expected controlled calls: `['1N', '3C', '3D', '3H', '4S', 'P']`
- Expected diagnostics: `[]`

### `meow_puppet_five_three_heart_fit_reaches_game`

- N: `S82HAQJ87DA76CKQ5` -> S 82  H AQJ87  D A76  C KQ5
- S: `S9876HQT2DAJ4CKQ7` -> S 9876  H QT2  D AJ4  C KQ7
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `1NP3CP3HP4HPPP`
- Expected controlled calls: `['1N', '3C', '3H', '4H', 'P']`
- Expected diagnostics: `[]`

### `meow_texas_heart_game_signoff_full_auction`

- N: `SAQ7HKJ8DA762CQ54` -> ? AQ7  ? KJ8  ? A762  ? Q54
- S: `S72HAQJ987D53CK42` -> ? 72  ? AQJ987  ? 53  ? K42
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `1NP4DP4HPPP`
- Expected controlled calls: `['1N', '4D', '4H', 'P']`
- Expected diagnostics: `[]`

### `meow_two_notrump_puppet_four_four_spade_fit_reaches_game`

- N: `SKQ76HKJ8DAQ6CKQ4` -> S KQ76  H KJ8  D AQ6  C KQ4
- S: `S9876H76DAJ4C8765` -> S 9876  H 76  D AJ4  C 8765
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `2NP3CP3DP3HP4SPPP`
- Expected controlled calls: `['2N', '3C', '3D', '3H', '4S', 'P']`
- Expected diagnostics: `[]`

### `meow_strong_two_club_second_negative_places_heart_game`

- N: `SAKHAKJ987DKQ3CAQ` -> S AK  H AKJ987  D KQ3  C AQ
- S: `S876H32D8765C8765` -> S 876  H 32  D 8765  C 8765
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `2CP2DP2HP3CP4HPPP`
- Expected controlled calls: `['2C', '2D', '2H', '3C', '4H', 'P']`
- Expected diagnostics: `[]`

### `meow_weak_two_ogust_places_heart_game`

- N: `S76HAQJ987D83C432` -> S 76  H AQJ987  D 83  C 432
- S: `SAK3H54DAJ76CKQJ5` -> S AK3  H 54  D AJ76  C KQJ5
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `2HP2NP3DP4HPPP`
- Expected controlled calls: `['2H', '2N', '3D', '4H', 'P']`
- Expected diagnostics: `[]`

### `meow_weak_two_ogust_signs_off_after_minimum`

- N: `S76HKJ9876DQ3C432` -> S 76  H KJ9876  D Q3  C 432
- S: `SAQ3H54DAJ76CK542` -> S AQ3  H 54  D AJ76  C K542
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `2HP2NP3CP3HPPP`
- Expected controlled calls: `['2H', '2N', '3C', '3H', 'P']`
- Expected diagnostics: `[]`

### `meow_bergen_limit_raise_accepts_game`

- N: `S72HAKJ87DQ82CKJ3` -> S 72  H AKJ87  D Q82  C KJ3
- S: `S83HQ976DKJ7CA982` -> S 83  H Q976  D KJ7  C A982
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `1HP3DP4HPPP`
- Expected controlled calls: `['1H', '3D', '4H', 'P']`
- Expected diagnostics: `[]`

### `meow_drury_declines_to_partscore`

- N: `SKJ987H82DQ83CA42` -> S KJ987  H 82  D Q83  C A42
- S: `S987H74DAJ7CKQ854` -> S 987  H 74  D AJ7  C KQ854
- Environment: dealer=s, vulnerability=none, scoring=IMP
- Expected auction: `PP1SP2CP2SPPP`
- Expected controlled calls: `['P', '1S', '2C', '2S', 'P']`
- Expected diagnostics: `[]`

### `meow_drury_accepts_game`

- N: `SAK987H82DAQ3CJ42` -> S AK987  H 82  D AQ3  C J42
- S: `SQT2H74DKJ7CKQ852` -> S QT2  H 74  D KJ7  C KQ852
- Environment: dealer=s, vulnerability=none, scoring=IMP
- Expected auction: `PP1SP2CP4SPPP`
- Expected controlled calls: `['P', '1S', '2C', '4S', 'P']`
- Expected diagnostics: `[]`

### `meow_jacoby_shortness_places_game`

- N: `SAKJ87H2DQ84CK432` -> S AKJ87  H 2  D Q84  C K432
- S: `SQ976H87DAK7CAQ82` -> S Q976  H 87  D AK7  C AQ82
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `1SP2NP3HP4SPPP`
- Expected controlled calls: `['1S', '2N', '3H', '4S', 'P']`
- Expected diagnostics: `[]`

### `meow_two_over_one_side_major_fit_reaches_game`

- N: `SAQJ76HKJ82DK8C32` -> S AQJ76  H KJ82  D K8  C 32
- S: `S2HAQ74DAQ76CKQ32` -> S 2  H AQ74  D AQ76  C KQ32
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `1SP2DP2HP4HPPP`
- Expected controlled calls: `['1S', '2D', '2H', '4H', 'P']`
- Expected diagnostics: `[]`

### `meow_two_over_one_side_minor_places_three_notrump`

- N: `SQ2HAKJ76DKJ82C32` -> S Q2  H AKJ76  D KJ82  C 32
- S: `SA83H2DQ76CAQJ932` -> S A83  H 2  D Q76  C AQJ932
- Environment: dealer=n, vulnerability=none, scoring=IMP
- Expected auction: `1HP2CP2DP3NPPP`
- Expected controlled calls: `['1H', '2C', '2D', '3N', 'P']`
- Expected diagnostics: `[]`

## Hand Parser Cases

### Valid

- `any_suit_order_and_10_alias`: `H8763SK10C2DAKQ987` -> ? KT  ? 8763  ? AKQ987  ? 2; expected `{'spades': 'KT', 'hearts': '8763', 'diamonds': 'AKQ987', 'clubs': '2', 'hcp': 12}`
- `repeated_suit_sections_are_concatenated`: `S9S8HAKQJD7654C432` -> ? 98  ? AKQJ  ? 7654  ? 432; expected `{'spades': '98', 'hearts': 'AKQJ', 'diamonds': '7654', 'clubs': '432', 'hcp': 10}`
- `void_marker_and_x_placeholders`: `SAKQJH-DxxxxCxxxxx` -> ? AKQJ  ? -  ? XXXX  ? XXXXX; expected `{'spades': 'AKQJ', 'hearts': '', 'diamonds': 'XXXX', 'clubs': 'XXXXX', 'hcp': 10}`

### Invalid

- `wrong_card_count`: `SAKQHJT9D876C54`; error contains `Wrong number of cards`
- `repeated_known_card`: `SASAHKQJTD987C654`; error contains `Repeated card`
- `unknown_symbol`: `SAZHKQJTD987C654`; error contains `Unknown symbol`
- `rank_before_suit`: `ASAKQHJT9D876C54`; error contains `Rank appears before suit marker`
- `bad_single_one`: `S1HKQJTD987C65432`; error contains `use 10 or T`
- `void_marker_with_cards`: `S-AHKQJTD987C654`; error contains `Void marker`
- `dictionary_input_rejected`: `{'spades': 'AKQ', 'hearts': 'JT9', 'diamonds': '876', 'clubs': '5432'}`; error contains `compact string`

## Legality Cases

- `opening_position_all_contracts_and_pass_are_legal`: auction ``, expected `{'complete': False, 'legal': ['P', '1C', '1D', '1H', '1S', '1N', '7N'], 'illegal': ['X', 'R']}`
- `lower_contracts_are_illegal_after_one_spade`: auction `1S`, expected `{'complete': False, 'legal': ['P', '1N', '2C', 'X'], 'illegal': ['1C', '1D', '1H', '1S', 'R']}`
- `opener_side_can_redouble_after_opponent_double`: auction `1SX`, expected `{'complete': False, 'legal': ['P', 'R', '1N', '2C'], 'illegal': ['X', '1S']}`
- `auction_complete_after_contract_and_three_passes`: auction `1SPPP`, expected `{'complete': True, 'legal': [], 'illegal': ['P', '1N', 'X', 'R']}`
- `auction_complete_after_four_passes`: auction `PPPP`, expected `{'complete': True, 'legal': [], 'illegal': ['P', '1C', 'X', 'R']}`

## Matcher Cases

- `seat_positions_expand_any_pattern`: context `{'auction_pattern': '1HP', 'seat_positions': [3, 4]}`, matches `['PP1HP', 'PPP1HP']`, rejects `['1HP', 'P1HP']`
