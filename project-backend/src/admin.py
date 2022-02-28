# admin/user/remove/v1
# and
# admin/userpermission/change/v1 functions

import pickle
from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.create_token import decode_jwt
from src import config
from src.helper_functions import authorised
import os
OWNER = 1
MEMBER = 2




def count_admins():

    try:
        store = pickle.load(open("data.py", 'rb'))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover

    count = 0
    # checking if the only global owner is being demoted to user
    for user in store['users']:
        if store['users'][user]['permission_id'] == 1:
            count = count + 1

    return count



def search_user(u_id, store):
    """This function searches user_id among the list and returns if they exist."""

    for user in store['users']:
        if u_id == store['users'][user]['u_id']:
            return True

    return False

# function for admin/userpermission/change/v1

@authorised
def admin_userpermission_change_v1(token, u_id, permission_id):

    decoded = decode_jwt(token)

    try:
        store = pickle.load(open("data.p", 'rb'))
    except Exception:  # pragma: no cover
        store = data_store.get()  # pragma: no cover


    if not search_user(u_id, store):
        raise InputError(description="ID does not exist")

    if count_admins() == 1 and permission_id == MEMBER and store['users'][u_id]['permission_id'] == OWNER:
        raise InputError(description="Only global owner being demoted")

    if permission_id not in [OWNER, MEMBER]:
        raise AccessError(description="Unknown permission Request")

    # raising AccessError if user is not global owner

    if store['users'][decoded['u_id']]['permission_id'] == MEMBER:
        raise AccessError(description="User is not a global owner")

    # changing the permission_id to given permission ID
    store['users'][u_id]['permission_id'] = permission_id


    data_store.set(store)
    return {}


# function for admin/user/remove/v1
@authorised
def admin_user_remove_v1(token, u_id):

    try:
        store = pickle.load(open("data.p", 'rb'))
    except Exception:  # pragma: no cover
        store = data_store.get()  # pragma: no cover

    decoded = decode_jwt(token)

    if store['users'][decoded['u_id']]['permission_id'] == MEMBER:
        raise AccessError(description="User is not a global owner")


    if not search_user(u_id, store):
        raise InputError(description="ID does not exist")

    if count_admins() == 1 and store['users'][u_id]['permission_id'] == OWNER:
        raise InputError(description="Only global owner")


    for message in store['message']:
        if u_id == message['u_id']:
            message['message'] = "Removed user"

    for channel in store['channels']:
        if u_id in channel['all_members']:  # pragma: no branch
            channel['all_members'].remove(u_id)

    for channel in store['channels']:
        if u_id in channel['owner_members']:
            channel['owner_members'].remove(u_id)

    for msg in store['dms']:
        for index in range(len(store['dms'][msg]["messages"])):
            if u_id == store['dms'][msg]['messages'][index]['u_id']:
                store['dms'][msg]['messages'][index]['message'] = "Removed user"

    for dm in store['dms']:
        if u_id in store['dms'][dm]['users']:  # pragma: no branch
            store['dms'][dm]['users'].remove(u_id)

    del store['user_stats'][u_id] # pragma: no branch

    removed_user = store['users'][u_id]
    store['removed_users'].append(removed_user)

    store['users'][u_id] = {'email': "", 'password': "",
                            "name_first": "", "name_last": "",
                            "timestamp": "", "handle_str": "", "u_id": "", "session_id": [], "permission_id": "", "profile_img_url" : config.url+"static/unswstreams.jpg"}

    data_store.set(store)
    return {}
