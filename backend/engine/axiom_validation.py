"""Definition checks that are provable without a concrete hand or auction."""
from .axiom_facts import INVITES, configuration, tags
from .auction import Auction
from .cards import Hand
from .hand_quality import assess_quality
from .calls import normalize_call


class AxiomDefinitionError(ValueError):
    def __init__(self, errors):
        self.errors = errors
        super().__init__('; '.join(
            f"{e['code']}: {e['message']} ({e.get('origin',{}).get('qualified_id','profile')})"
            for e in errors))


def validate_profile_axioms(profile):
    errors = []
    try:
        config = configuration(profile.axioms)
        assess_quality(Hand.from_dict({}), weights=config['quality'])
    except (ValueError, TypeError) as error:
        errors.append({'code':'INVALID_AXIOM_CONFIGURATION','message':str(error)})
    known = INVITES | {'forcing','game_forcing','accept','reject','signoff'}
    for spec in profile.call_specifications:
        private_purpose = spec.private_purpose
        if private_purpose is not None and not callable(private_purpose):
            reason = _private_purpose_error(private_purpose)
            if reason:
                errors.append({'code': 'INVALID_PURPOSE', 'message': reason,
                               'origin': spec.origin_dict()})
        meaning = spec.meaning.to_dict()
        explicit = meaning.get('axiom_tags',[])
        if not isinstance(explicit,(list,tuple)) or any(not isinstance(t,str) or t not in known for t in explicit):
            errors.append({'code':'INVALID_AXIOM_TAGS','message':'axiom_tags must list canonical axiom tags','origin':spec.origin_dict()})
            continue
        marks = tags(meaning)
        if {'accept','reject'} <= marks:
            errors.append({'code':'CONFLICTING_TAGS','message':'A call cannot both accept and reject','origin':spec.origin_dict()})
        if spec.call != 'P' or not marks & (INVITES | {'forcing','game_forcing'}):
            continue
        pattern = spec.auction_pattern
        if '*' in pattern or '?' in pattern:
            continue  # Context-sensitive checks run when this rule is a candidate.
        try:
            prior = Auction.parse(pattern)
        except ValueError:
            continue
        if not prior.calls or prior.calls[-1] == 'P':
            errors.append({'code':'PASS_SEMANTICS','message':'Forcing/invitational Pass requires a non-Pass by RHO',
                           'origin':spec.origin_dict(),'auction':pattern,'call':'P'})
    if errors:
        raise AxiomDefinitionError(errors)


def _private_purpose_error(value):
    if not isinstance(value, dict) or value.get('kind') != 'response_plan':
        return 'private_purpose must be a response_plan mapping'
    if value.get('trump') not in ('C', 'D', 'H', 'S', 'N'):
        return 'response_plan requires a valid trump'
    replies = value.get('responses')
    if not isinstance(replies, dict) or not replies:
        return 'response_plan requires partner replies and planned calls'
    try:
        if any(not isinstance(reply, str) or not isinstance(call, str)
               or normalize_call(reply) != reply or normalize_call(call) != call
               for reply, call in replies.items()):
            return 'response_plan replies and planned calls must be normalized calls'
    except ValueError:
        return 'response_plan contains an invalid call'
    return None
