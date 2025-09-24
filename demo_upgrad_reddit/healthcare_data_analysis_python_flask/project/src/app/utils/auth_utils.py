from functools import wraps
from flask import request, abort

VALID_TOKENS = {
    'valid_clinical_access_token': {'roles': ['clinical_access']},
    'valid_research_access_token': {'roles': ['research_access', 'clinical_access']},
}

def require_oauth2(required_role=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                abort(401, message='Missing or invalid Authorization header.')
            token = auth_header.split(' ', 1)[1]
            user = VALID_TOKENS.get(token)
            if not user:
                abort(401, message='Invalid or expired token.')
            if required_role and required_role not in user.get('roles', []):
                abort(403, message='Insufficient permissions.')
            return fn(*args, **kwargs)
        return wrapper
    return decorator
