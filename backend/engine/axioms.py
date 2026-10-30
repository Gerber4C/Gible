"""Mandatory decision constraints, independent of profile Policy ordering."""
from .axiom_facts import (INVITES, configuration, gf_satisfied, is_game, loses_partner_turn,
                          natural, partner, public_facts, tags)
from .hand_quality import (assess_quality, minor_game_control_points,
                           shapely_combined_effective_points)
from .legality import is_call_legal, last_contract_state


def invitation_action(own, low, high, threshold):
    if own + (low if low is not None else 0) >= threshold:
        return 'game'
    if low is not None and high is not None and 1 <= threshold-own-low <= 2 and own+high >= threshold:
        return 'invite'
    if high is not None and own+high < threshold:
        return 'signoff'
    return None


def certified_game_strength(meaning, quality, config, hand=None):
    """Let a profile supply a checkable non-HCP game valuation for this call."""
    evidence = meaning.get('strength_evidence')
    if not isinstance(evidence, dict) or evidence.get('model') not in (
            'kaplan_rubens', 'kaplan_rubens_or_shapely_effective'):
        return False
    suit = meaning.get('target_suit')
    partner_min = evidence.get('partner_min')
    if suit not in config['game_hcp'] or isinstance(partner_min, bool) or not isinstance(partner_min, (int, float)):
        return False
    if quality['kr_points'] + partner_min >= config['game_hcp'][suit]:
        return True
    if evidence['model'] != 'kaplan_rubens_or_shapely_effective' or hand is None:
        return False
    shape_minimum = evidence.get('shape_minimum')
    shape_lengths = evidence.get('shape_lengths')
    if (isinstance(shape_minimum, bool) or not isinstance(shape_minimum, (int, float))
            or not isinstance(shape_lengths, (tuple, list))):
        return False
    patterns = (shape_lengths if shape_lengths and isinstance(shape_lengths[0], (tuple, list))
                else (shape_lengths,))
    if any(len(pattern) != 4 or any(isinstance(length, bool) or not isinstance(length, int)
                                   for length in pattern) for pattern in patterns):
        return False
    actual_shape = sorted(hand.length(other) for other in 'SHDC')
    if not any(actual_shape == sorted(pattern) for pattern in patterns):
        return False
    return shapely_combined_effective_points(hand) >= shape_minimum


def certified_shape_invitation(meaning, hand):
    """Check a profile's explicit effective-point exception to raw-HCP signoff."""
    evidence = meaning.get('shape_invitation')
    if not isinstance(evidence, dict) or not isinstance(evidence.get('minimum'), (int, float)):
        return False
    lengths = evidence.get('min_lengths')
    if not isinstance(lengths, dict) or not lengths:
        return False
    if any(suit not in 'SHDC' or not isinstance(length, int) or length < 4
           or hand.length(suit) < length for suit, length in lengths.items()):
        return False
    return shapely_combined_effective_points(hand) >= evidence['minimum']


def evaluate_axioms(auction, hand, trace, candidates, raw_config=None):
    report = {'obligations':[], 'errors':[], 'rejected':[], 'evidence':[], 'quality':{},
              'auction':auction.compact_sequence(), 'seat':auction.actor_to_call}
    try:
        config = configuration(raw_config)
        facts = public_facts(auction, trace)
        quality = assess_quality(hand, facts['partner_suits'], facts['opponent_suits'],facts['agreed'],config['quality'])
    except (ValueError, TypeError) as error:
        report['errors'].append({'code':'INVALID_AXIOM_CONFIGURATION','message':str(error)})
        return (), report
    report['quality'] = quality
    report['evidence'] = facts['evidence']
    report['ranges'] = facts['ranges']
    report['errors'].extend(facts['errors'])
    obligations = report['obligations']
    actor = auction.actor_to_call
    rho_pass = not auction.calls or auction.calls[-1] == 'P'
    previous = facts['previous']
    previous_tags = tags(previous['public_meaning']) if previous else set()
    forces = [e for e in facts['forces'] if not gf_satisfied(e,facts,auction,config)]
    for entry in forces:
        obligations.append({'kind':'game_forcing','origin':entry['origin'],'index':entry['index']})
    forced = rho_pass and bool(previous_tags & {'forcing','game_forcing'})
    if forced:
        obligations.append({'kind':'forcing','origin':previous['origin'],'index':previous['index']})

    # Invitations to slam are outside the game-invitation axiom.
    invitation = (bool(previous_tags & {'invite','invite_plus'})
                  and 'slam_try' not in previous_tags
                  and not facts['own_game'])
    action = None
    if invitation:
        low,high = facts['ranges'].get(actor,(None,None))
        if low is None or high is None or high == low:
            report['errors'].append({'code':'UNKNOWN_INVITATION_RANGE',
                'message':'Cannot answer invitation without a non-exact public HCP range for the responder',
                'origin':previous['origin']})
        elif not low <= hand.hcp <= high:
            report['errors'].append({'code':'HAND_OUTSIDE_SHOWN_RANGE','message':f'Actual {hand.hcp} HCP is outside shown {low}..{high}'})
        else:
            special = previous['public_meaning'].get('invite_acceptance')
            if isinstance(special, dict) and special.get('mode') == 'minor_controls':
                control_score = minor_game_control_points(
                    hand, special['trump'],
                    partner_long_suits=special.get('normal_suits', ()))
                accepts = control_score >= special['minimum']
                obligations.append({'kind':'minor_control_assessment','score':control_score,
                                    'minimum':special['minimum'],'trump':special['trump']})
            elif isinstance(special, dict) and special.get('mode') == 'best_minor_controls':
                control_scores = {s:minor_game_control_points(
                    hand, s, partner_long_suits=special.get('normal_suits', ()))
                                  for s in 'CD'}
                control_score = max(control_scores.values())
                accepts = control_score >= special['minimum']
                obligations.append({'kind':'minor_control_assessment','score':control_score,
                                    'minimum':special['minimum'],'scores':control_scores})
            else:
                width = high-low
                accepts = hand.hcp >= (high if width == 1 else low+2) or (width == 2 and hand.hcp == low+1 and quality['good'])
            action = 'accept' if accepts else 'reject'
            obligations.append({'kind':action,'range':[low,high],'hcp':hand.hcp,'quality_good':quality['good'],'origin':previous['origin']})
    elif not facts['own_game'] and not forced and not forces:
        # Inquiry answers must first deliver the requested information.
        answering = bool(previous_tags & {'inquiry','directive','relay'})
        invitation_resolved = (bool(previous_tags & {'accept', 'reject'})
                               and previous is not None
                               and any(entry['seat'] == actor
                                       and entry['index'] < previous['index']
                                       and tags(entry['public_meaning']) & INVITES
                                       for entry in facts['ours']))
        low,high = facts['ranges'].get(partner(actor),(None,None))
        threshold = config['game_hcp'][facts['agreed'] or 'N']
        if not answering and not invitation_resolved:
            action = invitation_action(hand.hcp,low,high,threshold)
            if action:
                obligations.append({'kind':action,'own_hcp':hand.hcp,'partner_range':[low,high],
                                    'threshold':threshold,'target_suit':facts['agreed'] or 'N'})

    if report['errors']:
        return (),report
    allowed = []
    for candidate in candidates:
        m = candidate.public_meaning
        candidate_tags = tags(m)
        # Strength labels are optional meanings, not a required classification
        # of every call. An unclassified non-Pass call can open or advance an
        # auction; explicit strength actions and terminal Passes remain checked.
        strength_labels = INVITES | {'accept','reject','signoff','forcing',
                                     'game_forcing','inquiry','slam_try','control_showing'}
        unclassified_continuation = (candidate.call != 'P'
                                     and not candidate_tags & strength_labels)
        reasons, errors = [], []
        def reject(code, message, error=False):
            reason = {'code':code,'message':message,'call':candidate.call,'origin':candidate.origin}
            reasons.append(reason)
            if error:
                errors.append(reason)
        if not is_call_legal(auction,candidate.call):
            reject('ILLEGAL_CALL','Call is not legal in this auction',True)
        if {'accept','reject'} <= candidate_tags:
            reject('CONFLICTING_TAGS','A call cannot both accept and reject the same invitation',True)
        if candidate.call == 'P' and rho_pass and candidate_tags & (INVITES | {'forcing','game_forcing'}):
            reject('PASS_SEMANTICS','Pass cannot be forcing or invitational after RHO passes',True)
        if candidate.call == 'P' and forced:
            reject('FORCING_PASS','Current actor must answer the forcing call; a signoff must be a suitable non-Pass call',True)
        if forces:
            for source in forces:
                if gf_satisfied(source,facts,auction,config,candidate.call,m):
                    continue
                if (candidate.call == 'P' and loses_partner_turn(auction)) or (candidate.call != 'P' and 'signoff' in candidate_tags):
                    reject('GAME_FORCE_UNFULFILLED','Cannot terminate below the configured game-force target')
        if action == 'game':
            is_target = natural(m) and is_game(candidate.call)
            continues = bool(candidate_tags & {'forcing','game_forcing','inquiry','slam_try','control_showing'})
            contract = last_contract_state(auction)
            passing_game = (candidate.call == 'P' and contract is not None
                            and is_game(contract.call))
            if not is_target and not continues and not unclassified_continuation and not passing_game and not (candidate.call == 'P' and not rho_pass and not loses_partner_turn(auction)):
                reject('GAME_REQUIRED','Public strength guarantees game; choose game or a defined continuation')
        elif action == 'invite' and not (candidate_tags & INVITES or 'game_forcing' in candidate_tags
                                         or unclassified_continuation
                                         or (candidate.source_kind == 'purpose_axiom'
                                             and candidate.source_id == 'terminal_pass')
                                         or (natural(m) and is_game(candidate.call)
                                             and (candidate.source_kind == 'purpose_axiom'
                                                  or m.get('quality_upgrade')
                                                  or previous and previous['public_meaning'].get('action_type') in
                                                  ('minor_transfer_superaccept', 'transfer_superaccept')))):
            reject('INVITATION_REQUIRED','Choose an invitation or a defined game-forcing route')
        elif action == 'signoff' and not (candidate_tags & {'invite_minus','signoff'} or unclassified_continuation
                                          or certified_game_strength(m, quality, config, hand)
                                          or (candidate_tags & INVITES and certified_shape_invitation(m, hand))
                                          or (m.get('shape_invitation') and candidate_tags & INVITES
                                              and hand.length(m.get('target_suit')) >= 7
                                              and quality['kr_delta'] >= 2)
                                          or candidate_tags & {'slam_try','inquiry','control_showing'}):
            reject('SIGNOFF_REQUIRED','Even partner maximum is insufficient; choose invite_minus or signoff')
        elif action in ('accept','reject') and action not in candidate_tags:
            reject('INVITATION_RESPONSE_REQUIRED',f'Choose a call explicitly marked {action}')
        if action == 'accept' and not (natural(m) and is_game(candidate.call)):
            if (candidate.call == 'P' and loses_partner_turn(auction)) or (candidate.call != 'P' and 'signoff' in candidate_tags):
                reject('ACCEPTANCE_BELOW_GAME','Accepting a game invitation cannot terminate below game',True)
        if reasons:
            report['rejected'].append({'call':candidate.call,'origin':candidate.origin,'reasons':reasons})
            report['errors'].extend(errors)
        else:
            allowed.append(candidate)
    if not allowed:
        report['errors'].append({'code':'NO_COMPLIANT_CALL','message':'No candidate satisfies the active axioms; add the missing call definition'})
    return tuple(allowed),report
