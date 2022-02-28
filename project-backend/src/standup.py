from src.data_store import data_store
from src.error import InputError, AccessError
from src.message import message_send_v1
from src.create_token import decode_jwt
import threading 
import time
import pickle
from datetime import datetime, timezone, timedelta
import datetime
import json
import pytz
from src.message import message_send_v1
import requests 
from src import config
import re
MSG = "1"

# def message_send(token, channel_id, message):
#     try:
#         store = pickle.load(open("data.p", "rb"))
#     except Exception: # pragma: no cover
#         store = data_store.get() # pragma: no cover
#     dt = datetime.datetime.now(tz=pytz.UTC)
#     timestamp = int(dt.timestamp())
#     user_id = decode_jwt(token)['u_id']
#     u_handle = decode_jwt(token)['handle_str']
#     ch_name = store['channels'][channel_id - 1]['name']
#     users = store['users']
    
#     #tagging user and send notification
#     tag = re.findall(r'@([^\s@]+)', message)
#     if tag != []:
#         msg = message[0 : 20]
#         for target in tag:
#             for user in users:
#                 if target == store['users'][user]['handle_str']:
#                     notification_msg = {'channel_id': channel_id, 'dm_id': -1, 'notification_message': f'{u_handle} tagged you in {ch_name}: {msg}'}
#                     store['users'][user]['notification'].append(notification_msg)

#     message_id = MSG + str(channel_id) + str(timestamp)
#     message_id = int(message_id)
#     created_message = {'u_id': user_id, 'channel_id': channel_id, 'message': message, 'message_id': message_id, "time_created" : timestamp, 'reacts': [ {"react_id" : -1,  "u_ids" : [], "is_this_user_reacted" : False } ], 'is_pinned': False}

#     store['message'].append(created_message)
#     src.users.update_workspace_stats(store)
#     data_store.set(store)
    
#     return { 'message_id' : message_id }

def is_member(token, channel_id):
    auth_user_id = decode_jwt(token)['u_id']
    try:
        store = pickle.load('data.p', 'rb')
    except Exception: 
        store = data_store.get() 
    for dic in store['channels']:
        if int(dic['channel_id']) == int(channel_id):
            if auth_user_id in dic['all_members']:
                return True
    return False

def channel_id_valid(channel_id):
    try:
        store = pickle.load('data.p', 'rb')
    except Exception: 
        store = data_store.get() 
    for dic in store['channels']:
        if dic['channel_id'] == int(channel_id):
            return True
    return False


def standup_active_v1(token, channel_id):
    try:
        store = pickle.load('data.p', 'rb')
    except Exception: 
        store = data_store.get() 
    #check if the channel_id is invalid
    if not channel_id_valid(channel_id):
        raise InputError(description='invalid channel_id')
    #check if auth user is a member of the channel
    if not is_member(token, channel_id):
        raise AccessError(description='Authorised user is not a member of the channel')
    #standup is inactive until the below code finds it in the
    #standup_active list
    time_finish = None
    #check if the channel is active
    standup_active = False
    for dic in store['standup']['standup_active']:
        if int(dic['channel_id']) == int(channel_id) and dic['is_active'] == True:
            #channel is in a list of active standups
            time_finish = dic['time_finish']
            standup_active = True

    return {'is_active': standup_active, 'time_finish': time_finish}


def send_standup(token, channel_id, time_finish):
    try:
        store = pickle.load('data.p', 'rb')
    except Exception: 
        store = data_store.get() 
    #make the standup inactive
    for dic in store['standup']['standup_active']:
        if dic['channel_id'] == channel_id:
            dic['is_active'] = False
    standup_active = {
        'channel_id': channel_id, 
        'time_finish': time_finish, 
        'is_active': False
    }
    store['standup']['standup_active'].pop(standup_active)
    #check if the channel_id is in standup
    if channel_id in store['standup'].keys():
        #send the standup as a single message
        standup_messages = store['standup'][channel_id]
        combined_message = ""
        for message in standup_messages:
            string = f"{message['handle']}: {message['message']}\n"
            combined_message += string
            message_send_v1(token, channel_id, combined_message)
    data_store.set(store)


def standup_start_v1(token, channel_id, length):
    try:
        store = pickle.load('data.p', 'rb')
    except Exception: 
        store = data_store.get() 
    #check if channel_id invalid
    if not channel_id_valid(channel_id):
        raise InputError(description='invalid channel_id')
    #length is negative
    if length < 0:
        raise InputError(description='Length is a negative integer')
    #standup already active
    if standup_active_v1(token, channel_id)['is_active']:
        raise InputError(description='Standup already active')
    #check if auth user is a member of the channel
    if not is_member(token, channel_id):
        raise AccessError(description='Authorised user is not a member of the channel')
    #get time finish

    dt = datetime.datetime.now(tz=pytz.UTC)
    delta = datetime.timedelta(seconds=length)
    time_finish = delta + dt
    time_finish = int(time_finish.replace(tzinfo=timezone.utc).timestamp())
    #clear the messages
    store['standup'][channel_id] = []
    #send standup from data store after timer
    standup = threading.Timer(int(length), send_standup, [token, channel_id, time_finish])
    standup.start()
    #make standup active
    standup_active = {
        'channel_id': channel_id, 
        'time_finish': time_finish, 
        'is_active': True
    }
    store['standup']['standup_active'].append(standup_active)
    data_store.set(store)
    return {'time_finish': time_finish}


def standup_send_v1(token, channel_id, message):
    try:
        store = pickle.load('data.p', 'rb')
    except Exception: 
        store = data_store.get() 
    #check if channel_id valid
    if not channel_id_valid(channel_id):
        raise InputError(description='invalid channel_id')
    #check if there is an active standup
    if not standup_active_v1(token, channel_id)['is_active']:
        raise InputError(description='There is no standup active')
    #check if the length of the message is over 1000
    if len(message) > 1000:
        raise InputError(description='length of message is over 1000 characters')
    #check if auth user is a member of the channel
    if not is_member(token, channel_id):
        raise AccessError(description='Authorised user is not a member of channel')
    handle = decode_jwt(token)['handle_str']
    standup_info = {'handle': handle, 'message': message}
    #check if the channel_id is in standup
    if channel_id in store['standup'].keys():
        store['standup'][channel_id].append(standup_info)
    else:
        store['standup'][channel_id] = [standup_info]

    data_store.set(store)
    

