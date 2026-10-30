"""Public, seat-scoped evidence used by axioms. Never reads partner cards."""
from math import isfinite

from .auction import Auction
from .legality import SIDE_BY_SEAT, auction_is_complete, last_contract_state

INVITES = {'invite', 'invite_plus', 'invite_minus'}
ALIASES = {'invitation':'invite', 'invitational':'invite', 'invitation+':'invite_plus',
           'invitation-':'invite_minus', 'invitation_plus':'invite_plus',
           'invitation_minus':'invite_minus', 'acceptance':'accept', 'rejection':'reject'}


def tags(meaning):
    result = set()
    for key in ('axiom_tags', 'call_act_types'):
        values = meaning.get(key, ()) or ()
        if isinstance(values, str):
            values = (values,)
        result.update(ALIASES.get(v, v) for v in values)
    if meaning.get('forcing_status') in ('forcing', 'one_round', 'one_round_forcing'):
        result.add('forcing')
    if meaning.get('forcing_status') == 'game_forcing':
        result.add('game_forcing')
    if 'final_placement' in result:
        result.add('signoff')
    return result


def partner(seat):
    return {'n':'s','s':'n','e':'w','w':'e'}[seat]


def configuration(raw):
    if raw is not None and not isinstance(raw,dict):
        raise ValueError('axioms must be a mapping')
    raw = dict(raw or {})
    unknown = set(raw) - {'game_hcp', 'four_minor_exceptions', 'quality'}
    if unknown:
        raise ValueError('Unknown axiom settings: ' + ', '.join(sorted(unknown)))
    thresholds = {'N':25, 'H':25, 'S':25, 'C':28, 'D':28}
    if not isinstance(raw.get('game_hcp',{}),dict):
        raise ValueError('game_hcp must be a mapping')
    for suit, value in raw.get('game_hcp', {}).items():
        if suit not in thresholds or isinstance(value, bool) or not isinstance(value, (int,float)) or not isfinite(value) or not 1 <= value <= 40:
            raise ValueError('game_hcp requires SHDCN and finite thresholds in 1..40')
        thresholds[suit] = value
    exceptions = raw.get('four_minor_exceptions', [])
    if not isinstance(exceptions, list):
        raise ValueError('four_minor_exceptions must be a list')
    for rule in exceptions:
        if not isinstance(rule, dict) or set(rule) != {'source','auction','calls'}:
            raise ValueError('4m exception requires source, auction, calls')
        if not isinstance(rule['source'], str) or not rule['source'] or not isinstance(rule['auction'],str) or not rule['auction']:
            raise ValueError('4m exception requires explicit source and auction (or *)')
        if not isinstance(rule['calls'],list) or not rule['calls'] or any(c not in ('4C','4D') for c in rule['calls']):
            raise ValueError('4m exceptions permit only 4C/4D')
        if rule['auction'] != '*':
            Auction.parse(rule['auction'])
    if not isinstance(raw.get('quality',{}), dict):
        raise ValueError('quality must be a mapping')
    return {'game_hcp':thresholds, 'four_minor_exceptions':exceptions, 'quality':raw.get('quality',{})}


def is_game(call):
    return len(call) == 2 and call[0] in '1234567' and call[1] in 'CDHSN' and int(call[0]) >= {'C':5,'D':5,'H':4,'S':4,'N':3}[call[1]]


def natural(meaning):
    return 'artificial' not in meaning.get('nature_labels', ()) and bool(
        'natural' in meaning.get('nature_labels', ()) or tags(meaning) & {'signoff','accept','reject'})


def loses_partner_turn(auction):
    """If we pass and opponents pass, does the auction end before partner acts?"""
    target = partner(auction.actor_to_call)
    calls = auction.calls + ('P',)
    for _ in range(4):
        future = Auction(calls, auction.dealer, auction.vulnerability)
        if auction_is_complete(future):
            return True
        if future.actor_to_call == target:
            return False
        calls += ('P',)
    return True


def public_facts(auction, trace):
    entries = [e for e in trace.applied_meanings if 'seat' in e and 'index' in e and e['index'] < len(auction.calls)]
    actor = auction.actor_to_call
    side = SIDE_BY_SEAT[actor]
    ours = [e for e in entries if SIDE_BY_SEAT[e['seat']] == side]
    latest_partner_index = next((i for i in range(len(auction.calls)-1,-1,-1) if auction.actor_at(i) == partner(actor)), None)
    previous = next((e for e in reversed(ours) if e['index'] == latest_partner_index), None)
    ranges, conflicts, evidence = {}, [], []
    openers = {}
    for index, call in enumerate(auction.calls):
        if call[0] in '1234567':
            seat = auction.actor_at(index)
            openers.setdefault(SIDE_BY_SEAT[seat], seat)
    current_trump = trace.trump_state(side)
    agreed = current_trump.suit if current_trump.status == 'agreed' else None
    partner_suits, opponent_suits = set(), set()
    forces = []
    for entry in entries:
        m = entry['public_meaning']
        seat = entry['seat']
        own_side = SIDE_BY_SEAT[seat] == side
        if own_side and entry['call'] == 'P' and tags(m) & (INVITES | {'forcing','game_forcing'}):
            if entry['index'] == 0 or auction.calls[entry['index']-1] == 'P':
                conflicts.append({'code':'INVALID_PRIOR_PASS',
                                  'message':'Prior forcing/invitational Pass followed a Pass by RHO',
                                  'origin':entry['origin'],'index':entry['index'],'call':'P'})
        opener = openers.get(SIDE_BY_SEAT[seat])
        roles = {'opener':opener, 'responder':partner(opener) if opener else None,
                 'actor':seat, 'self':seat, 'partner':partner(seat)}
        if natural(m) and entry['call'][0] in '1234567' and entry['call'][1:] in 'SHDC':
            if seat == partner(actor):
                partner_suits.add(entry['call'][1:])
            elif not own_side:
                opponent_suits.add(entry['call'][1:])
        pieces = []
        if 'hcp_range' in m:
            pieces.append((seat, *m['hcp_range']))
        elif 'hcp_min' in m or 'hcp_max' in m:
            pieces.append((seat, m.get('hcp_min'), m.get('hcp_max')))
        game_force = 'game_forcing' in tags(m)
        if 'accept' in tags(m):
            invitation = next((e for e in reversed(entries) if e['index'] < entry['index'] and e['seat'] == partner(seat)),None)
            if invitation and tags(invitation['public_meaning']) & {'invite','invite_plus'} and not is_game(invitation['call']):
                game_force = True
        for effect in entry.get('effects', []):
            if effect.get('namespace','public') != 'public' or effect.get('visibility') == 'private':
                continue
            key = effect.get('key','')
            if own_side and key in ('forcing_status','partnership.force_status'):
                game_force |= effect.get('status',effect.get('value')) == 'game_forcing'
            if key.endswith('.hcp'):
                owner = key[:-4]
                owner = roles.get(owner, owner)
                if owner in ('n','s','e','w'):
                    pieces.append((owner,effect.get('value',effect.get('min_value')),effect.get('value',effect.get('max_value'))))
        if own_side and game_force:
            forces.append(entry)
        for owner, low, high in pieces:
            if SIDE_BY_SEAT.get(owner) != side:
                continue
            if any(v is not None and (isinstance(v,bool) or not isinstance(v,(int,float)) or not isfinite(v) or not 0 <= v <= 40) for v in (low,high)):
                conflicts.append({'code':'INVALID_RANGE','message':'Invalid public HCP range', 'origin':entry['origin']})
                continue
            old = ranges.get(owner, [None,None])
            lows = [v for v in (old[0],low) if v is not None]
            highs = [v for v in (old[1],high) if v is not None]
            ranges[owner] = [max(lows) if lows else None, min(highs) if highs else None]
            evidence.append({'seat':owner,'range':[low,high],'origin':entry['origin'],'index':entry['index']})
    for owner,(low,high) in ranges.items():
        if low is not None and high is not None and low > high:
            conflicts.append({'code':'CONFLICTING_RANGE','message':f'Public HCP range for {owner} is empty: {low}..{high}', 'seat':owner})
    contract = last_contract_state(auction)
    current = next((e for e in entries if contract and e['index'] == contract.index),None)
    own_game = bool(contract and contract.side == side and current and natural(current['public_meaning']) and is_game(contract.call))
    return dict(entries=entries, ours=ours, previous=previous, ranges=ranges, errors=conflicts, evidence=evidence,
                forces=forces, agreed=agreed, partner_suits=partner_suits, opponent_suits=opponent_suits,
                contract=contract, current=current, own_game=own_game)


def gf_satisfied(source, facts, auction, config, call=None, meaning=None):
    # Once our side reaches a natural game, that particular GF obligation is fulfilled.
    if any(e['index'] >= source['index'] and natural(e['public_meaning']) and is_game(e['call']) for e in facts['ours']):
        return True
    if call and natural(meaning or {}) and is_game(call):
        return True
    current = facts['current']
    if call is None or call == 'P':
        if not current or current not in facts['ours'] or current['index'] < source['index']:
            return False
        call, meaning = current['call'],current['public_meaning']
    if (is_game(call)
            and (meaning or {}).get('action_type') == 'quantitative_5c_feature_ask'):
        return True
    if not natural(meaning or {}):
        return False
    origin = source['origin'].get('qualified_id')
    for rule in config['four_minor_exceptions']:
        if rule['source'] in ('*',origin) and rule['auction'] in ('*',auction.compact_sequence()) and call in rule['calls']:
            return True
    return False
