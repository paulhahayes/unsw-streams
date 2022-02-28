import jwt
from src.error import AccessError
from src.secret import get_secret_string

SECRET = get_secret_string()
SESSION_TRACKER = 0


def generate_session_id():
    global SESSION_TRACKER
    SESSION_TRACKER += 1
    return SESSION_TRACKER


def generate_jwt(u_id, permission_id, handle, session_id=None): 

    if session_id is None: # pragma: no branch
        session_id = generate_session_id() # pragma: no branch


        # valid id
    return jwt.encode({'u_id': u_id, 'permission_id': permission_id, 'handle_str': handle, 'session_id': session_id, }, SECRET, algorithm='HS256')


def decode_jwt(token):
    try:
        return jwt.decode(token, SECRET, algorithms=['HS256'])
    except Exception as e:
        raise AccessError(description=e) from e
