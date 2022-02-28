"""
History
1. Honggyo Suh implemented channel_invite_v2 & channel_details_v2 on 30th Sep 2021.
2. Honggyo Suh implemented search_channel, search_user & search_already_in.
3. Honggyo Suh revised & added functions for iteration 2 on 18th Oct 2021.
"""
from src.users import mod_user_stats_v1, user_stats_v1
from src.error import InputError, AccessError
from src.data_store import data_store
from src.create_token import decode_jwt
import pickle
from src.helper_functions import authorised
from src.users import mod_user_stats_v1


def search_channel(channel_id):
    """This function searches channel_id among the list and returns if it exists."""

    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get()  # pragma: no cover

    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            return True

    return False



def search_user_id(user_id):
    """This function searches token among the list and returns if they exist."""

    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover

    for user in store['users']:
        if user_id == store['users'][user]['u_id']:
            return True

    return False
    

def search_already_in_id(channel_id, u_id):
    """This function searches whether or not the user already in the channel with id."""
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover

    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            for user in channel['all_members']:
                if user == u_id:
                    return True 

    return False


def search_already_in_token(channel_id, token):
    """This function searches whether or not the user already in the channel with token."""

    user_id = decode_jwt(token)['u_id']
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover

    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            channel_match = channel
            for user in channel_match['all_members']:
                if user == user_id:
                    return True

    return False
    

def search_already_in_owner(channel_id, token):
    """This function searches whether or not the user already an owner with token."""

    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover 
        store = data_store.get() # pragma: no cover

    user_id = decode_jwt(token)['u_id']
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            channel_match = channel
            for user in channel_match['owner_members']:
                if user == user_id:
                    return True

    return False
    

@authorised
def channel_invite_v2(token, channel_id, u_id):
    """This function invites user into a channel by an authorised user"""
    
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover


    if not search_channel(channel_id):
         raise InputError(description='No such channel')

    if not search_already_in_owner(channel_id, token):
       raise AccessError(description='Not a owner of the channel')
       
    if search_already_in_id(channel_id, u_id):
         raise InputError(description='Already in channel')

    if not search_user_id(u_id):
        raise InputError(description='Unknown u_id')

    global invited
    t_id = decode_jwt(token)['u_id']
    invited = store['users'][u_id]['u_id']
    store['channels'][channel_id - 1]['all_members'].append(invited)

    #for notification
    u_handle = decode_jwt(token)['handle_str']
    ch_name = store['channels'][channel_id - 1]['name']
    message_notification = {'channel_id': channel_id, 'dm_id': -1, 'notification_message': f"{u_handle} added you to {ch_name}"}
    store['users'][u_id]['notification'].append(message_notification)


    mod_user_stats_v1(t_id, store)
    mod_user_stats_v1(u_id, store)
    data_store.set(store)
    return {}

@authorised
def channel_details_v2(token, channel_id):
    """This function shows details of a channel by an authorised user."""

    if not search_channel(channel_id):
         raise InputError(description='No such channel')

    if not search_already_in_token(channel_id, token):
       raise AccessError(description="Not a member of the channel")

    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover

    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            channel_match = channel

    owner_id_list = channel_match['owner_members']
    all_id_list = channel_match['all_members']

    owner_list = []
    all_list = []
    owner_details = {}

    for id in owner_id_list:
        owner_details = {}
        owner_details['u_id'] = store['users'][id]['u_id']
        owner_details['email'] = store['users'][id]['email']
        owner_details['name_first'] = store['users'][id]['name_first']
        owner_details['name_last'] =store['users'][id]['name_last']
        owner_details['handle_str'] = store['users'][id]['handle_str']
        owner_details ['profile_img_url'] = store['users'][id]['profile_img_url']
        owner_list.append(owner_details)

    for id in all_id_list:
        user_details = {}
        user_details['u_id'] = store['users'][id]['u_id']
        user_details['email'] = store['users'][id]['email']
        user_details['name_first'] = store['users'][id]['name_first']
        user_details['name_last'] =store['users'][id]['name_last']
        user_details['handle_str'] = store['users'][id]['handle_str'],
        user_details['profile_img_url'] = store['users'][id]['profile_img_url']
        all_list.append(user_details)
    

    return {
        'name': channel_match['name'],
        'is_public': channel_match['is_public'],
        'owner_members': owner_list,
        'all_members':  all_list,
    }

@authorised
def channel_join_v2(token, channel_id):

    """Channel join function was created by hansol choi z5338373"""
    

    if not search_channel(channel_id):
         raise InputError(description='No such channel')
        
    if search_already_in_token(channel_id, token):
         raise InputError(description='Already a member')
        
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover

    user_id = decode_jwt(token)['u_id']
    
    for channel in store['channels']:
        if channel['channel_id'] == int(channel_id):
            channel_match = channel
    
    for user in store['users']:
        if user_id == store['users'][user]['u_id']:
            user_match = store['users'][user]['u_id']
            
    for user in store['users']:
        if user_id == store['users'][user]['u_id']:
            if store['users'][user]['permission_id'] == 2 and channel_match['is_public'] == False:
               raise AccessError(description="Channel is private")
    
    channel_match['all_members'].append(user_match)
    mod_user_stats_v1(user_id, store)
    data_store.set(store)
    

    return { }


def find_channel_id(channel_id, t_id, store):
    """looks for the dictionary of a specific channel and returns its
        messages.
        if the channel id dictionary doesn't exist then the function
        will raise an input error"""


    return_messages = []

    for dic in store['message']:
        if dic['channel_id'] == channel_id:
            info = {
                    "message_id" : dic['message_id'],
                    "u_id" : dic["u_id"],
                    "message" : dic["message"],
                    "time_created" : dic["time_created"],
                    "is_pinned" : dic["is_pinned"],
                     "reacts" : dic['reacts']
            }
            if t_id in dic['reacts'][0]['u_ids']:
                info['reacts'][0]['is_this_user_reacted'] = True
            return_messages.append(info)

    return return_messages



@authorised
def channel_messages_v2(token, channel_id, start):
    """
    channel_messages_v2 implemented by Benedict Pamittan
    add a message key to the channel dictionaries
    """
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover

    decoded = decode_jwt(token)
    t_id = decoded['u_id']


    if not search_channel(channel_id):
         raise InputError(description='No such channel')

    if not search_already_in_token(channel_id, token):
       raise AccessError(description="Not a member of the channel")



    messages = find_channel_id(channel_id, t_id, store)
    num_of_messages = len(messages) # 1
    fifty_messages = []


    # append the fifty most recent messages
    for i in range(50):
        if (start + i) < num_of_messages:
            fifty_messages.append(messages[start + i])

    # append start and fifty_messages into output dictionary
   
    output = {}
    output['messages'] = sorted(fifty_messages, key=lambda d: d['time_created'], reverse=True)
    output['start'] = start

    if start + 50 < num_of_messages:
        # if end in range then append it
        # to the output dictionary
        output['end'] = start + 50
    else:
        # output end is -1 when there are less than 50
        # most recent messages from start
        output['end'] = -1
        
    return output


@authorised
def channel_addowner_v1(token, channel_id, u_id):


    if not search_user_id(u_id):
         raise InputError(description='No such user')

    if not search_channel(channel_id):
         raise InputError(description='No such channel')

    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover
    #raises an input error if channel_id not in datastore

    #append u_id to owners list
    for dic in store['channels']:
        if dic['channel_id'] == channel_id:
            #raise error if user is not a member of the channel
            if u_id not in dic['all_members']:
                raise InputError(description="User is not a member of the channel")
            #raise error if u_id is already an owner
            if u_id in dic['owner_members']:
                raise InputError(description="User is already a member of the channel")
            #token doesn't have permissions
            if decode_jwt(token)['u_id'] not in dic['owner_members']:
                raise AccessError(description="Authorised user doesn't have owner permissions") 
            dic['owner_members'].append(u_id)

    data_store.set(store)


@authorised
def channel_removeowner_v1(token, channel_id, u_id):


    if not search_user_id(u_id):
         raise InputError(description='No such user')

    if not search_channel(channel_id):
         raise InputError(description='No such channel')

    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover
    #raises an input error if channel_id not in datastore
    

    for dic in store['channels']:
        if dic['channel_id'] == channel_id:
            #raise error if user is not an owner of the channel
            if u_id not in dic['owner_members']:
                raise InputError(description="User is not an owner of the channel")
            #raise error if removing the only owner of the channel
            if len(dic['all_members']) <= 1:
                raise InputError(description="Removing only owner of the channel")
            #authorized user doesn't have owner permissions
            if decode_jwt(token)['u_id'] not in dic['owner_members']:
                raise AccessError(description="Authorised user doesn't have owner permissions") 
            dic['owner_members'].remove(u_id)


    data_store.set(store)
    return {}
    

@authorised
def channel_leave_v1(token, channel_id):
    """This function let user leave the channel"""
    

    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover
    user_id = decode_jwt(token)['u_id']
    
    if not search_channel(channel_id):
        raise InputError(description='No such channel')
        
    if not search_already_in_token(channel_id, token):
        raise AccessError(description='Not a member of the channel')
    
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover
    
    for channel in store['channels']:
        if channel['channel_id'] == channel_id:
            channel_match = channel
    
    for user in channel_match['all_members']:
        if user == user_id:
            user_match = user
    
    if search_already_in_owner(channel_id, token):
        channel_match['owner_members'].remove(user_match)
        
    channel_match['all_members'].remove(user_match)
    mod_user_stats_v1(user_id, store)
    data_store.set(store)
    
    return {}
    



