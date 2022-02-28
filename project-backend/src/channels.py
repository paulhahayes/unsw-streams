"""Functions to do with listing and creating channels"""

from src.data_store import data_store
from src.error import InputError, AccessError
from src.users import mod_user_stats_v1
from src.create_token import decode_jwt
import src.users 
import pickle


def search_id(u_id):
    """This function searches user_id among the list and returns if they exist."""
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover

    for user in store['removed_users']:
        user['u_id'] == u_id
        return False
    
    for user in store['users']:
        if user == u_id:
            return True

    return False



def channels_list_v2(token):

    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get()  # pragma: no cover
    decoded = decode_jwt(token)

    if not search_id(decoded['u_id']):
        raise AccessError(description="ID does not exist")

    if decoded['session_id'] not in store['users'][decoded['u_id']]['session_id']:
        raise AccessError(description="Session ID does not exist")

    
    if len(store['channels']) > 0:
        channel_dict = { 'channels' : []}
        for data in store['channels']:
            if decoded['u_id'] in data['all_members']:
                new = {
                    'channel_id': data['channel_id'],
                    'name': data['name'],
                }
                channel_dict['channels'].append(new)
        return channel_dict
    

    return { 'channels' : []}



def channels_listall_v2(token):
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover
    decoded = decode_jwt(token)

    if not search_id(decoded['u_id']):
        raise AccessError(description="ID does not exist")

    if decoded['session_id'] not in store['users'][decoded['u_id']]['session_id']:
        raise AccessError(description="Session ID does not exist")

    
    if len(store['channels']) > 0:
        data_list = {'channels': []}
        for data in store['channels']:
            new = {
                'channel_id': data['channel_id'],
                'name': data['name'],
            }
            data_list['channels'].append(new)

            data_store.set(store)
        return data_list



    return { 'channels' : []}

def channels_create_v2(token, name, is_public):
    """
    channels_create_v1 implemented by Benedict Pamittan
    creates a channel

    """

    auth_user_id = decode_jwt(token)['u_id']
    if not search_id(auth_user_id):
        raise AccessError(description="ID does not exist")
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception:  # pragma: no cover
        store = data_store.get()  # pragma: no cover
    decoded = decode_jwt(token)
    
    if decoded['session_id'] not in store['users'][decoded['u_id']]['session_id']:
        raise AccessError(description="User logged out")

    channel_id = len(store['channels']) + 1

    # if the character length isn't inbetween 1 and 20
    if len(name) > 20 or len(name) < 1:
        raise InputError(
            description='Num of characters in name is less than 1 or more than 20')

    # create channel dict with channel information
    new_channel = {
        'channel_id': channel_id,
        'user_id': auth_user_id,
        'name': name,
        'is_public': is_public,
        'all_members': [auth_user_id],
        'owner_members': [auth_user_id],
    }

    # append dict to data_store
    store['channels'].append(new_channel)

    mod_user_stats_v1(auth_user_id, store)
    src.users.update_workspace_stats(store)

    data_store.set(store)
    
    return {'channel_id': channel_id}
