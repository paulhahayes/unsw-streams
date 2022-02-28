from src.create_token import decode_jwt
from src.error import AccessError, InputError
from src.data_store import data_store
import pickle



def authorised(function):
    def wrapper(*args, **kwargs):
        token = args[0]
        check_token(token)
        return function(*args, **kwargs)
    return wrapper



def search_user_id(user_id, store):
    """This function searches token among the list and returns if they exist."""

    for user in store['users']:
        if user_id == store['users'][user]['u_id']:
            return True
    return False


def search_removed_users(u_id, store):


    for user in store['removed_users']:
        if u_id == user['u_id']:
            return True
    return False


def check_token(token):

    token = decode_jwt(token)
    u_id = token['u_id']
    session_id = token['session_id']
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception:  # pragma: no cover
        store = data_store.get()  # pragma: no cover

    if not search_user_id(u_id, store):
        if not search_removed_users(u_id, store):
            raise AccessError(description="Unknown user")

    if session_id not in store['users'][u_id]['session_id']:
        raise AccessError(description="User logged out")

    return store