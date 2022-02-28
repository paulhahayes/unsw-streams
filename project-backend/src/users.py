r"""
This file cotnains ...
"""
from src.error import InputError
from src.data_store import data_store

import pickle
from src.create_token import decode_jwt, generate_jwt
from src.auth import check_email
import requests
import urllib.request
from urllib.error import HTTPError
from datetime import datetime
from datetime import timezone
import datetime
from PIL import Image
from src import config
import pytz
from src.helper_functions import authorised


def is_jpg_image(img_url):
    image_formats = ("image/jpeg", "image/jpg")
    r = requests.head(img_url)
    if r.headers["content-type"] in image_formats:
        return True
    return False


def generate_filename(token):
    base = decode_jwt(token)['handle_str']
    suffix = str(datetime.datetime.now())
    filename = "_".join([base, suffix])
    return filename


def download_image(token, img_url):

    filename = generate_filename(token)
    img = urllib.request.urlopen(img_url).read()

    save_path = "src/static/" + filename + ".jpg"
    img_data = open(save_path, 'wb')
    img_data.write(img)
    img_data.close()
    return save_path, filename


def check_img_shape(profile_image, x_start, y_start, x_end, y_end):

    image_width, image_height = profile_image.size

    if x_start < 0 or y_start < 0:
        raise InputError(description='Invalid co-ordinates 1')
    if x_end < x_start:
        raise InputError(description='Invalid co-ordinates 2')
    if y_end < y_start:
        raise InputError(description='Invalid co-ordinates 3')
    if x_end > image_width:
        raise InputError(description='Invalid co-ordinates 4')
    if y_end > image_height:
        raise InputError(description='Invalid co-ordinates 5')


def crop_image(profile_image, save_path, x_start, y_start, x_end, y_end):

    check_img_shape(profile_image, x_start, y_start, x_end, y_end)
    cropped_image = profile_image.crop((x_start, y_start, x_end, y_end))
    cropped_image.save(save_path)


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



@authorised
def users_all_v1(token):

    try:
        store = pickle.load(open("data.p", "rb"))

    except Exception:  # pragma: no cover
        store = data_store.get()  # pragma: no cover

    ######################
    user_list = []
    for index in store['users']:
        # removed user
        if len(store['users'][index]) == 0:
            pass
        elif store['users'][index]['email'] != "":
            new_user = {
                'u_id': store['users'][index]['u_id'],
                'email': store['users'][index]['email'],
                'name_first': store['users'][index]['name_first'],
                'name_last': store['users'][index]['name_last'],
                'handle_str': store['users'][index]['handle_str'],
                'profile_img_url': store['users'][index]['profile_img_url']
            }
            user_list.append(new_user)

    return {'users': user_list}

@authorised
def user_profile_v1(token, u_id):

    ######## TESTS #######
    decode_jwt(token)
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception:  # pragma: no cover
        store = data_store.get()  # pragma: no cover

    if search_removed_users(u_id):
        for user in store['removed_users']:
            if u_id == user['u_id']:
                info = user

        user_info = {
            'u_id': info['u_id'],
            'email': info['email'],
            'name_first': 'Removed',
            'name_last': 'user',
            'handle_str': info['handle_str'],
            'profile_img_url': store['users'][u_id]['profile_img_url']
        }
        return {"user": user_info}

    if search_user_id(u_id):
        user_info = {
            'u_id': store['users'][u_id]['u_id'],
            'email': store['users'][u_id]['email'],
            'name_first': store['users'][u_id]['name_first'],
            'name_last': store['users'][u_id]['name_last'],
            'handle_str': store['users'][u_id]['handle_str'],
            'profile_img_url': store['users'][u_id]['profile_img_url']
        }
        return {"user": user_info}

    raise InputError(description="user id not found")

@authorised
def user_profile_setname_v1(token, name_first, name_last):

    ######## TESTS #######
    decode_id = decode_jwt(token)
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception:  # pragma: no cover
        store = data_store.get()  # pragma: no cover

    

    if len(name_first) < 1 or len(name_first) > 50:  # pylint: disable = len-as-condition
        raise InputError(description='Invalid Name')
    if len(name_last) < 1 or len(name_last) > 50:  # pylint: disable = len-as-condition
        raise InputError(description='Invalid Name')
    ######################

    store['users'][decode_id['u_id']]['name_first'] = name_first
    store['users'][decode_id['u_id']]['name_last'] = name_last
    data_store.set(store)

    return {}

@authorised
def user_profile_setemail_v1(token, email):
    ######## TESTS #######
    decode_id = decode_jwt(token)

    try:
        store = pickle.load(open("data.p", "rb"))

    except Exception:  # pragma: no cover
        store = data_store.get()  # pragma: no cover

    

    if not check_email(email):
        raise InputError(description='Invalid email')

    for user in store['users']:
        if email == store['users'][user]['email']:
            raise InputError(description='Email already exists')

    store['users'][decode_id['u_id']]['email'] = email
    data_store.set(store)

    return {}

@authorised
def user_profile_sethandle_v1(token, handle_str):
    ######## TESTS #######
    decode_id = decode_jwt(token)
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception:  # pragma: no cover
        store = data_store.get()  # pragma: no cover
    

    for user in store['users']:
        if handle_str == store['users'][user]['handle_str']:
            raise InputError(description='Handle already exists')

    if len(handle_str) < 3 or len(handle_str) > 20:
        raise InputError(description='Invalid length')

    if not handle_str.isalnum():
        raise InputError(description='Invalid characters')

    store['users'][decode_id['u_id']]['handle_str'] = handle_str
    data_store.set(store)

    return {}

@authorised
def user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end):

    # check the token
    decode_id = decode_jwt(token)
    

    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception:  # pragma: no cover
        store = data_store.get()  # pragma: no cover

    # check the request

    try:
        urllib.request.urlopen(img_url)
    except Exception as error:
        raise InputError(description="url not valid") from error

    if not is_jpg_image(img_url):
        raise InputError(description="image type not jpg")

    # downlaod to server
    save_path, filename = download_image(token, img_url)
    # prepare image for modifcation
    profile_image = Image.open(save_path)
    # crop image
    crop_image(profile_image, save_path, x_start, y_start, x_end, y_end)
    profile_url = config.url + "static/" + filename + ".jpg"
    store['users'][decode_id['u_id']]['profile_img_url'] = profile_url
    data_store.set(store)
    return {}

        
@authorised
def user_stats_v1(token):

    """This function returns the stat of user"""

    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception:    # pragma: no cover
        store = data_store.get()  # pragma: no cover
    decode_id = decode_jwt(token)['u_id']
    

    return  {"user_stats" : store['user_stats'][decode_id]}
    


def update_workspace_stats(store):
    #count number of channels
    num_channels = len(store['channels'])
    #count number of dms
    num_dms = len(store['dms'].keys())
    #count number of messages
    num_messages = len(store['message'])
    #count number of messages in each dm
    num_dm_messages = 0
    for dm in store['dms'].keys():
        num_dm_messages += len(store['dms'][dm]['messages'].keys())

    num_messages += num_dm_messages
    if not store['workspace_stats_initialised'] and (num_channels + num_dms + num_messages) == 1:
        dt = datetime.datetime.now(tz=pytz.UTC)
        time_stamp = int(dt.timestamp())
        store['workspace_stats_initialised'] = True
    else:
        dt = datetime.datetime.now(tz=pytz.UTC)
        time_stamp = int(dt.timestamp())
    #append to the dictionary
    store['workspace_stats']['channels_exist'].append(\
        {'num_channels_exist': num_channels, 'time_stamp': time_stamp})
    
    store['workspace_stats']['dms_exist'].append(\
        {'num_dms_exist': num_dms, 'time_stamp': time_stamp})

    store['workspace_stats']['messages_exist'].append(\
        {'num_messages_exist': num_messages, 'time_stamp': time_stamp})
    #total of users
    num_users = len(store['users'].keys())
    #len(store['users']) - len(store['removed_users'])
    #get users that are apart of dms or channels
    active_users = []
    for channel in store['channels']:
        for user in channel['all_members']:
            if user not in active_users:
                active_users.append(user)

    for dm in store['dms'].keys():
        for user in store['dms'][dm]['users']:
            if user not in active_users:
                active_users.append(user)
    #number of users apart of dms or channels
    num_active_users = len(active_users)
    
    if num_users != 0: # pragma: no cover
        utilization_rate = num_active_users / num_users # pragma: no cover
    else:
        utilization_rate = 0
    store['workspace_stats']['utilization_rate'] = utilization_rate
    return store['workspace_stats']
    
    
@authorised
def users_stats_v1(token):
    
    try:
        data_file = open('data.p', "rb")
        store = pickle.load(data_file)
    except Exception: # pragma: no cover
        store = data_store.get() # pragma: no cover
    return {'workspace_stats': update_workspace_stats(store)}
    



    
def mod_user_stats_v1(u_id, store):

    """This function returns the stat of user"""

    # the most last recorded stats
    old_channels = store['user_stats'][u_id]["channels_joined"][-1]['num_channels_joined']
    old_dms = store['user_stats'][u_id]["dms_joined"][-1]["num_dms_joined"]
    old_msgs = store['user_stats'][u_id]["messages_sent"][-1]["num_messages_sent"]

    user_channel = 0
    user_msgs = 0
    user_dms = 0
    total_channel = 0
    total_dm = 0
    total_message = 0
    
    # user message count

    for channel in store['channels']:
        total_channel += 1
        for user in channel['all_members']:
            if user == u_id:
                user_channel += 1

    msgs = store['message']
    for msg in msgs:
        total_message += 1
        if u_id == msg['u_id']:
            user_msgs += 1

    dms = store['dms']
    for dm in dms:
        total_dm += 1
        if u_id in dms[dm]['users']:
            user_dms += 1

    dms = store['dms']
    for dm in dms:
        for idx in dms[dm]['messages']:
            total_message += 1
            if u_id == dms[dm]['messages'][idx]['u_id']:
                user_msgs += 1
    

    # sum(num_channels_joined, num_dms_joined, num_msgs_sent)/sum(num_channels, num_dms, num_msgs)

    user_sum = user_channel + user_dms + user_msgs
    total_sum = total_channel + total_dm + total_message

    # this impossible to test for in blackbox testing
    
    if total_sum == 0: # pragma: no cover  
        involvement_rate = 0 # pragma: no cover  
    else:
        involvement_rate = user_sum / total_sum

    if involvement_rate > 1: # pragma: no cover  
        involvement_rate = 1 # pragma: no cover  



    dt = datetime.datetime.now(tz=pytz.UTC)
    time_stamp = int(dt.timestamp())
    #check if there is any changes
    if user_channel != old_channels:
        store['user_stats'][u_id]['channels_joined'].append( {"num_channels_joined" : user_channel, "time_stamp" :  time_stamp} )
    #check if there is any changes
    if user_dms != old_dms:
        store['user_stats'][u_id]['dms_joined'].append( {"num_dms_joined" : user_dms, "time_stamp" :  time_stamp} )
    #check if there is any changes
    if user_msgs != old_msgs:
        store['user_stats'][u_id]['messages_sent'].append( { "num_messages_sent" : user_msgs, "time_stamp" :  time_stamp})

    store['user_stats'][u_id]['involvement_rate'] = float(involvement_rate)
    data_store.set(store)
    return