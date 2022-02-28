"""
History
1. Honggyo Suh implemented functions for iteration 3 on 5th Nov 2021.
"""

from src.data_store import data_store
from src.create_token import decode_jwt
import src.error
import pickle
import src.channel
from src.helper_functions import authorised


@authorised
def search_v1(token, query_str):
    
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get()
    
        
    if len(query_str) > 1000 or len(query_str) < 1:
        raise src.error.InputError(description='Check the length of query')
        
    messages = []

    decoded = decode_jwt(token)
    t_id = decoded['u_id']

    channel_ids = []
    for channel in store['channels']:
        if t_id in channel['all_members']:
            channel_ids.append(channel['channel_id'])

    for message in store['message']:
            if message['channel_id'] in channel_ids:
                if query_str in message['message']:
                    addition = message
                    messages.append(addition)


    dms = store['dms']
    for dm in dms:
        if t_id in dms[dm]['users']:
            for message in  dms[dm]['messages']:
                if query_str in dms[dm]['messages'][message]['message']:
                    messages.append(dms[dm]['messages'][message])


    messages = sorted(messages, key=lambda d: d['time_created'])

    return { "messages" : messages }

