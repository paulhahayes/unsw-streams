import pickle
from src.data_store import data_store
from src.error import InputError, AccessError


def search_user_id(user_id):
    """This function searches token among the list and returns if they exist."""

    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception:  # pragma: no cover
        store = data_store.get()  # pragma: no cover

    for user in store['users']:
        if user_id == store['users'][user]['u_id']:
            return True
    return False


def search_removed_users(u_id):
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception:  # pragma: no cover
        store = data_store.get()  # pragma: no cover

    for user in store['removed_users']:
        if u_id == user['u_id']:
            return True
    return False

def check_token(u_id, session_id):

    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception:  # pragma: no cover
        store = data_store.get()  # pragma: no cover

    if not search_user_id(u_id):
        if not search_removed_users(u_id):
            raise AccessError(description="Unknown user")

    if session_id not in store['users'][u_id]['session_id']:
        raise AccessError(description="User logged out")