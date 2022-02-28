from re import A
import src.channel
from src.error import InputError, AccessError
from src.data_store import data_store
from src.create_token import decode_jwt
import time
from datetime import datetime
from src.helper_functions import authorised
import pickle


@authorised
def notifications_get_v1(token):
    """this shows 20 recent notification"""
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover
    token = decode_jwt(token)
    t_id = token['u_id']
    users = store['users']
    notifications = []

    twenty_notes = []

    for user in users:
        if t_id == user:
            notifications = users[t_id]['notification']

    length = len(notifications)
    if(length <= 20):
        twenty_notes = notifications
    else:
        for i in range(20, 0 , -1):
            twenty_notes.append(notifications[i])

    #tagged: "{User??s handle} tagged you in {channel/DM name}: {first 20 characters of the message}"
    #reacted message: "{User??s handle} reacted to your message in {channel/DM name}"
    #added to a channel/DM: "{User??s handle} added you to {channel/DM name}"

    
    return { "notifications" : twenty_notes }