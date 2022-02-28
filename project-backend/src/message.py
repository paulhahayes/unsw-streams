"""
History
1. Honggyo Suh implemented functions for iteration 2 on 18th Oct 2021.
"""

from os import truncate
import src.channel
from src.error import InputError, AccessError
from src.dm import dm_details_v1
from src.channel import channel_details_v2
from src.data_store import data_store
from src.create_token import decode_jwt
from src.helper_functions import authorised
import time
from datetime import datetime
from datetime import timezone
import datetime
import pickle
import pytz
import re
from src.users import mod_user_stats_v1, update_workspace_stats

DM = "2"
MSG = "1"



def check_messages(message_id, store):
    """This is a helper function to check whether the message_id is valid."""
    
    
    for message in store['message']:
        if message['message_id'] == message_id:
            return message['channel_id']
    
    return False



def check_dms(message_id, store, token):
    """This is a helper function to check whether the message_id is valid."""
    # for some reason enum and other for loop techniques weren't working so I wrote it like this
    u_id = decode_jwt(token)['u_id']
    for dm in store['dms']:
        for message in store['dms'][dm]['messages']:
            if store['dms'][dm]['messages'][message]['message_id'] == message_id:
                if store['dms'][dm]['messages'][message]['u_id'] == u_id: 
                    return store['dms'][dm]['messages'][message]
    return False


def check_dms_messages(message_id, store):
    """This is a helper function to check whether the message_id is valid."""
    # for some reason enum and other for loop techniques weren't working so I wrote it like this
    
    for dm in store['dms']:
        for message in store['dms'][dm]['messages']:
            if store['dms'][dm]['messages'][message]['message_id'] == message_id:
                return store['dms'][dm]['messages'][message]

    return False



@authorised
def message_send_v1(token, channel_id, message):
    """This function sends message to specific channel by user."""
    
    if len(message) > 1000 or len(message) < 1:
        raise InputError(description='message input error')
    
    if not src.channel.search_channel(channel_id):
        raise InputError(description='channel id is invalid')

    
    if not src.channel.search_already_in_token(channel_id, token):
        raise AccessError(description='user is not a member of the channel')
        
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover
    


    dt = datetime.datetime.now(tz=pytz.UTC)
    timestamp = int(dt.timestamp())
    user_id = decode_jwt(token)['u_id']
    u_handle = decode_jwt(token)['handle_str']
    ch_name = store['channels'][channel_id - 1]['name']
    users = store['users']
    
    #tagging user and send notification
    tag = re.findall(r'@([^\s@]+)', message)
    if tag != []:
        msg = message[0 : 20]
        for target in tag:
            for user in users:
                if target == store['users'][user]['handle_str']:
                    notification_msg = {'channel_id': channel_id, 'dm_id': -1, 'notification_message': f'{u_handle} tagged you in {ch_name}: {msg}'}
                    store['users'][user]['notification'].append(notification_msg)


    message_id = MSG + str(channel_id) + str(timestamp)
    message_id = int(message_id)
    created_message = {'u_id': user_id, 'channel_id': channel_id, 'message': message, 'message_id': message_id, "time_created" : timestamp, 'reacts': [ {"react_id" : -1,  "u_ids" : [], "is_this_user_reacted" : False } ], 'is_pinned': False }
    store['message'].append(created_message)

    update_workspace_stats(store)
    mod_user_stats_v1(user_id, store)
    data_store.set(store)

    return { 'message_id' : message_id }

@authorised
def message_edit_v1(token, message_id, message):
    """This function allows user to edit message."""
    
    if len(message) > 1000:
        raise InputError(description='Check the length of message')
        
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover

    user_id = decode_jwt(token)['u_id']
    if str(message_id).startswith(MSG):

        channel_id = check_messages(message_id, store)
        if not channel_id:
            raise InputError(description='Check if the message is valid')
            
        if not src.channel.search_already_in_owner(channel_id, token):
            raise AccessError(description='Check if you have owner permission')

        for msg in store['message']:
            if msg['message_id'] == message_id:
                if len(message) < 1:
                    store['message'].remove(msg)
                else:
                    msg['message'] = message

    elif str(message_id).startswith(DM):
        dm_info = check_dms(message_id, store, token)
        if not dm_info:
            raise InputError(description='Check if the message is valid')


        if dm_info['message_id'] == message_id:
            if len(message) < 1:
        
                store['dms'].remove(dm_info)
            else:
                dm_info['message'] = message
    else:
        raise InputError(description="invalid message id")

    mod_user_stats_v1(user_id, store)
    data_store.set(store)

    return {}

    
@authorised
def message_remove_v1(token, message_id):
    """This function allows user to remove message."""
    
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover
    user_id = decode_jwt(token)['u_id']

    if str(message_id).startswith(MSG):
        channel_id = check_messages(message_id, store)
        if not channel_id:
            raise InputError(description='the message id is invalid')
            
        if not src.channel.search_already_in_owner(channel_id, token):
            raise AccessError(description='user does not have owner permission')

        for message in store['message']:
            if message['message_id'] == message_id:
                store['message'].remove(message)

    elif str(message_id).startswith(DM):

        dm_info = check_dms(message_id, store, token)
        if not dm_info:
            raise InputError(description='Check if the message is valid')
        for dm_index in store['dms']:
            for message_index in store['dms'][dm_index]['messages']:
                if store['dms'][dm_index]['messages'][message_index]['message_id'] == message_id:
                    del store['dms'][dm_index]['messages'][message_index]
                    break
        
    else:
        raise InputError(description='Cannot remove message. check again')

    update_workspace_stats(store)
    mod_user_stats_v1(user_id, store)
    data_store.set(store)
    return {}

@authorised
def message_senddm_v1(token, dm_id, message):
    """This function sends message to specific user."""
    if len(message) > 1000 or len(message) < 1:
        raise InputError(description='Check the length of message')

    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover

    token = decode_jwt(token) 

    t_id = token['u_id']
    t_handle = token['handle_str']
    users = store['users']
    dms = store['dms']


    #check dm is valid
    valid_dm = False
    existing_member =False


    for index in range(len(dms)):
        if dm_id == dms[index]['dm_id']:
            valid_dm = True
            if t_id in dms[index]['users']:
                existing_member = True
    

    if not valid_dm:
        raise InputError(description='The dm is not valid')

    if not existing_member:
        raise AccessError(description='The user is not a member of dm')

    
    #tagging user and send notification
    tag = re.findall(r'@([^\s@]+)', message)
    if tag != []:
        msg = message[0 : 20]
        for target in tag:
            for user in users:
                if target == store['users'][user]['handle_str']:
                    notification_msg = {'channel_id': -1, 'dm_id': dm_id, 'notification_message': f"{t_handle} tagged you in {store['dms'][dm_id]['name']}: {msg}"}
                    store['users'][user]['notification'].append(notification_msg)

    dt = datetime.datetime.now(tz=pytz.UTC)
    timestamp = int(dt.timestamp())
    #message id will be generated based on number of messages in the dm
    message_id = DM + str(dm_id) + str(len(dms[dm_id]['messages'])) + str(timestamp)
    message_id = int(message_id)
    # idx = int(str(message_id)[1:])
    
    created_message = {'message_id': message_id,'u_id': t_id, 'message': message, 'time_created': timestamp, 'reacts': [ {"react_id" : -1,  "u_ids" : [], "is_this_user_reacted" : False } ], 'is_pinned': False}
    append = { len(dms[dm_id]['messages']) : created_message }
    dms[dm_id]['messages'].update(append)
    #ben check this
    mod_user_stats_v1(t_id, store)
    data_store.set(store)
    return { 'message_id' : message_id }


@authorised
def message_pin_v1(token, message_id):
    """pin message in dm or channel"""

    try:
       store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
       store = data_store.get() # pragma: no cover


    token = decode_jwt(token)
    t_id = token['u_id']
    dms = store['dms']
    chs = store['message']

    #token check?

    if str(message_id).startswith(DM):
        if check_dms_messages(message_id, store) == False:
            raise InputError(description='Check if the message is valid')
    else:
        ch_msg_id = message_id
        if not check_messages(ch_msg_id, store):
            raise InputError(description='Check if the message is valid')

    #check the user has owner permission in the channel or dm
    idx = int(str(message_id)[1:])


    owner_permission = False
    if str(message_id).startswith(DM):
        for dm in dms:
            for idx in dms[dm]['messages']:
                if dms[dm]['messages'][idx]['message_id'] == message_id and t_id in dms[dm]['users']:
                    if t_id == dms[dm]['users'][0]:
                        owner_permission = True
                    if dms[dm]['messages'][idx]['is_pinned'] == False and owner_permission:
                        dms[dm]['messages'][idx]['is_pinned'] = True


                    else: 
                        if owner_permission != True:
                            raise AccessError(description='Do not have owner permission')
                        elif dms[dm]['messages'][idx]['is_pinned'] == True:
                            raise InputError(description='The message is already pinned')
    else:
        
        for message in chs:
            if message['message_id'] == ch_msg_id:
                ch_id = message['channel_id']
                for channel in store['channels']:
                    if channel['channel_id'] == ch_id:
                        if t_id in channel['owner_members']:
                            owner_permission = True
                if message['is_pinned'] == False and owner_permission == True:
                    message['is_pinned'] = True
                else:
                    if owner_permission != True:
                        raise AccessError(description='Do not have owner permission')
                    elif message['is_pinned'] == True:
                        raise InputError(description='The message is already pinned')
    data_store.set(store)
    return

@authorised
def message_unpin_v1(token, message_id):
    """unpin message in dm or channel"""
    
    try:
       store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
       store = data_store.get() # pragma: no cover

    
    token = decode_jwt(token)
    t_id = token['u_id']
    dms = store['dms']
    chs = store['message']


    if str(message_id).startswith(DM):
        if not check_dms_messages(message_id, store):
            raise InputError(description='Check if the message is valid')
    else:
        ch_msg_id = message_id
        if not check_messages(ch_msg_id, store):
            raise InputError(description='Check if the message is valid')

    #check the user has owner permission in the channel or dm
    idx = int(str(message_id)[1:])
    owner_permission = False
    if str(message_id).startswith(DM):
        for dm in dms:
            for idx in dms[dm]['messages']:
                if dms[dm]['messages'][idx]['message_id'] == message_id and t_id in dms[dm]['users']:
                    if t_id == dms[dm]['users'][0]:
                        owner_permission = True
                        
                    if dms[dm]['messages'][idx]['is_pinned'] == True and owner_permission:
                        dms[dm]['messages'][idx]['is_pinned'] = False

                    elif dms[dm]['messages'][idx]['is_pinned'] == False:
                        raise InputError(description='The message is already unpinned')

        if owner_permission != True:
            raise AccessError(description='Do not have owner permission')

    elif str(message_id).startswith(MSG): 
        for message in chs:
            if message['message_id'] == ch_msg_id:
                ch_id = message['channel_id']
                for channel in store['channels']:
                    if channel['channel_id'] == ch_id:
                        if t_id in channel['owner_members']:
                            owner_permission = True
                if message['is_pinned'] == True and owner_permission == True:
                    message['is_pinned'] = False
                else:
                    if owner_permission != True:
                        raise AccessError(description='Do not have owner permission')
                    elif message['is_pinned'] == False:
                        raise InputError(description='The message is already pinned')
    data_store.set(store)
    return

@authorised
def message_sendlaterdm_v1(token, dm_id, message, time_sent):
    
    
    #time input conversion need to be fixed
    #target = datetime.timestamp(datetime.strptime(time_sent, "%Y-%m-%d %H:%M:%S.%f"))
    #target = time.mktime(datetime.strptime(time_sent, "%b %d %Y %I:%M%p").timetuple())
    
    ct = datetime.datetime.now(tz=pytz.UTC)
    now = int(ct.timestamp())
    dif = int(time_sent) - int(now)
    if dif < 0:
        raise InputError(description='Invalid time')

    time.sleep(dif)
    
    message_id = message_senddm_v1(token, dm_id, message)

    #ben needs to add msgs

    return {'message_id': message_id['message_id']}

    
@authorised
def message_sendlater_v1(token, channel_id, message, time_sent):
    """This function sends message after delayed time amount in seconds"""
    
    if time_sent < 0:
        raise InputError(description='Check if time sent is valid')
        
    #time.sleep(time_sent)
    
    ct = datetime.datetime.now(tz=pytz.UTC)
    now = int(ct.timestamp())
    dif = int(time_sent) - int(now)
    if dif < 0:
        raise InputError(description='Invalid time')

    time.sleep(dif)
    message_id = message_send_v1(token, channel_id, message)
    
    return {'message_id': message_id['message_id']}

@authorised
def message_react_v1(token, message_id, react_id):
    """This function adds the react to the message or dm"""

    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover

    decoded = decode_jwt(token)
    t_id = decoded['u_id']

        
    if react_id != 1 and react_id != -1:
        raise InputError(description='Check if the react id is valid')

    if str(message_id).startswith(DM):
        dms = store['dms']
     
        if not check_dms_messages(message_id, store):
            raise InputError(description='Check if the dm is valid')
        valid_member = False

        for dm in dms:
            for idx in dms[dm]['messages']:
                if dms[dm]['messages'][idx]['message_id'] == message_id and t_id in dms[dm]['users']:
                    target_dm = dms[dm]['messages'][idx]
                    if len(target_dm['reacts'][0]['u_ids']) + react_id >= 1:
                        target_dm['reacts'][0]['react_id'] = 1
                    else:
                        target_dm['reacts'][0]['react_id'] = -1

                    if t_id in target_dm['reacts'][0]['u_ids'] and react_id == 1:
                        raise InputError(description='already reacted')
        
                    if react_id == 1:
                        target_dm['reacts'][0]['u_ids'].append(t_id)
                    elif react_id == -1:
                        target_dm['reacts'][0]['u_ids'].remove(t_id)
                    valid_member = True
                    dm_name = dm_details_v1(token, idx)['name']                                      
                    notification_msg = {'channel_id': -1, 'dm_id': idx, 'notification_message': f'{ decoded["handle_str"] } reacted to your message in {dm_name}'}
                    store['users'][target_dm['u_id']]['notification'].append(notification_msg)


        if not valid_member:
            raise InputError(description='Check if the user is a member of the dm')

    elif str(message_id).startswith(MSG):

        channel_id = check_messages(message_id, store)
        if not channel_id:
            raise InputError(description="invalid message_id")

        if not src.channel.search_already_in_token(channel_id, token):
            raise InputError(description='Check if the user is a member of the channel')

        for message in store['message']:
            if message['message_id'] == message_id:
                target_msg = message
                if len(target_msg['reacts'][0]['u_ids']) + react_id >= 1:
                    target_msg['reacts'][0]['react_id'] = 1
                else:
                    target_msg['reacts'][0]['react_id'] = -1

                if t_id in target_msg['reacts'][0]['u_ids'] and react_id == 1:
                        raise InputError(description='already reacted')
        
                if react_id == 1:
                        target_msg['reacts'][0]['u_ids'].append(t_id)
                elif react_id == -1:
                        target_msg['reacts'][0]['u_ids'].remove(t_id)
                channel_name = channel_details_v2(token, channel_id)['name']
                notification_msg = {'channel_id': channel_id, 'dm_id': -1, 'notification_message': f'{ decoded["handle_str"] } reacted to your message in {channel_name}'}
                store['users'][target_msg['u_id']]['notification'].append(notification_msg)

                        
    else:
        raise InputError(description='Unknown message id')

    data_store.set(store)  
    return {}


@authorised
def message_unreact_v1(token, message_id, react_id):
    """This function unreacts the message or dm"""
    if react_id != 1 and react_id != -1:
        raise InputError(description='Check if the react id is valid')

    message_react_v1(token, message_id, -1)
    
    return {}

@authorised
def message_share_v1(token, og_message_id, message, channel_id, dm_id):
    """This function shares message to the specific channel or dm"""
  
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover
        
    global shared_message_id
    global comment
    t_id = src.create_token.decode_jwt(token)['u_id']
    dms = store['dms']    
    
    if not check_dms_messages(og_message_id, store) and not check_messages(og_message_id, store):
        raise InputError(description='Check if the dm is valid')
    idx = int(str(og_message_id)[1:])
    if channel_id == -1 and dm_id != -1:
        if str(og_message_id).startswith(DM):
            for dm in dms:
                for idx in dms[dm]['messages']:
                    if dms[dm]['messages'][idx]['message_id'] == og_message_id and t_id in dms[dm]['users']:
                        if t_id == dms[dm]['users'][0]:
                    #for dm in dms:
                    #    if dms[dm]['messages'][og_message_id]['message_id'] == og_message_id and t_id in dms[dm]['users']:
                    #        if t_id == dms[dm]['users'][0]:
                            comment = "\n".join([dms[dm]['messages'][idx]['message'], message])
                            shared_message_id = message_senddm_v1(token, dm_id, comment)
                            shared_message_id = shared_message_id['message_id']
                            return {'message_id': shared_message_id}
                    
        else:
            for messages in store['message']:
                if messages['message_id'] == og_message_id:
                    comment = "\n".join([messages['message'], message])
                    shared_message_id = message_senddm_v1(token, dm_id, comment)
                    shared_message_id = shared_message_id['message_id']
                    return {'message_id': shared_message_id}

    elif dm_id == -1 and channel_id != -1:
    
        if not src.channel.search_channel(channel_id):
            raise src.error.InputError(description='No such channel')
            
        #if not check_dms_messages(og_message_id, store) and not check_messages(og_message_id, store):
        #    raise InputError(description='Check if the message is valid')
            
        if not src.channel.search_already_in_token(channel_id, token):
            raise src.error.AccessError(description='Check if the user is a member of the channel')
        
        if str(og_message_id).startswith(DM):
            for dm in dms:
                for idx in dms[dm]['messages']:
                    if dms[dm]['messages'][idx]['message_id'] == og_message_id and t_id in dms[dm]['users']:
                        if t_id == dms[dm]['users'][0]:
                    #for dm in dms:
                    #    if dms[dm]['messages'][og_message_id]['message_id'] == og_message_id and t_id in dms[dm]['users']:
                    #        if t_id == dms[dm]['users'][0]:
                            comment = "\n".join([dms[dm]['messages'][idx]['message'], message])
                            
                            shared_message_id = message_send_v1(token, channel_id, comment)

                            shared_message_id = shared_message_id['message_id']
                            return {'message_id': shared_message_id}
        else:
            for messages in store['message']:
                if messages['message_id'] == og_message_id:
                    comment = "\n".join([messages['message'], message])
                    shared_message_id = message_send_v1(token, channel_id, comment)
                    shared_message_id = shared_message_id['message_id']
                    return {'message_id': shared_message_id}
          
    else:
        raise InputError(description='Check if channel_id and dm_id is valid')

    mod_user_stats_v1(t_id, store)
    data_store.set(store)


