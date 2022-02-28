from re import A
import re
import sys
import signal
import pickle
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from src.error import InputError
from src import config

from src.admin import admin_user_remove_v1, admin_userpermission_change_v1
from src.other import clear_v1
from src.users import users_all_v1, user_profile_v1, user_profile_setname_v1, user_profile_setemail_v1, user_profile_sethandle_v1, user_profile_uploadphoto_v1
from src.auth import auth_register_v2, auth_login_v2, auth_logout_v1, auth_passwordreset_request_v1, auth_passwordreset_reset_v1
from src.channels import channels_list_v2, channels_create_v2, channels_listall_v2
from src.dm import dm_create_v1, dm_list_v1, dm_details_v1, dm_messages_v1, dm_leave_v1, dm_remove_v1
from src.data_store import data_store
from src.message import message_senddm_v1, message_edit_v1, message_remove_v1, message_pin_v1, message_unpin_v1, message_sendlaterdm_v1
import src.channel
from src.channel import channel_messages_v2
from src.standup import standup_start_v1, standup_active_v1, standup_send_v1
from src.search import search_v1
from src.message import message_share_v1, message_react_v1, message_unreact_v1, message_sendlater_v1
from src.users import user_stats_v1, users_stats_v1
from src.notification import notifications_get_v1
from src.users import update_workspace_stats
from datetime import datetime


def quit_gracefully(*args):
    '''For coverage'''
    exit(0)


def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response


APP = Flask(__name__, static_url_path='/static/')
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# NO NEED TO MODIFY ABOVE THIS POINT, EXCEPT IMPORTS


def save():
    store = data_store.get()
    try:
        with open('data.p', 'wb') as FILE:
            pickle.dump(store, FILE)
            FILE.close()
    except Exception:
        with open('data.p', 'wb') as FILE:
            pickle.dump(store, FILE)
            FILE.close()


# Example


# @APP.route("/echo", methods=['GET'])
# def echo():
#     data = request.args.get('data')
#     if data == 'echo':
#         raise InputError(description='Cannot echo "echo"')
#     return dumps({
#         'data': data,
#     })


@APP.route('/channel/invite/v2', methods=['POST'])
def channel_invite():
    data = request.get_json()
    token = data['token']
    channel_id = int(data['channel_id'])
    u_id = int(data['u_id'])
    src.channel.channel_invite_v2(token, channel_id, u_id)
    save()
    return dumps({})


@APP.route("/channel/messages/v2", methods=['GET'])
def channel_messages():
    data = request.args.to_dict()
    token = data['token']
    channel_id = int(data['channel_id'])
    start = int(data['start'])
    result = src.channel.channel_messages_v2(token, channel_id, start)
    save()
    return dumps(result)


@APP.route("/channel/addowner/v1", methods=['POST'])
def channel_addowner():
    data = request.get_json()
    token = data['token']
    channel_id = int(data['channel_id'])
    u_id = int(data['u_id'])
    src.channel.channel_addowner_v1(token, channel_id, u_id)
    save()
    return dumps({})


@APP.route("/channel/removeowner/v1", methods=['POST'])
def channel_removeowner():
    data = request.get_json()
    token = data['token']
    channel_id = int(data['channel_id'])
    u_id = int(data['u_id'])
    src.channel.channel_removeowner_v1(token, channel_id, u_id)
    save()
    return dumps({})


@APP.route('/channel/leave/v1', methods=['POST'])
def channel_leave():
    data = request.get_json()
    token = data['token']
    channel_id = int(data['channel_id'])
    src.channel.channel_leave_v1(token, channel_id)
    save()
    return dumps({})


@APP.route('/channel/join/v2', methods=['POST'])
def channel_join():
    data = request.get_json()
    token = data['token']
    channel_id = int(data['channel_id'])
    src.channel.channel_join_v2(token, channel_id)
    save()
    return dumps({})


@APP.route('/channel/details/v2', methods=['GET'])
def channel_details():
    data = request.args.to_dict()
    token = data['token']
    channel_id = int(data['channel_id'])
    result = src.channel.channel_details_v2(token, channel_id)
    save()
    return dumps(result)


@APP.route('/message/send/v1', methods=['POST'])
def send_message():
    data = request.get_json()
    token = data['token']
    channel_id = int(data['channel_id'])
    message = data['message']
    message_id = src.message.message_send_v1(token, channel_id, message)
    #update_workspace_stats()
    save()
    return dumps(message_id)


@APP.route('/message/edit/v1', methods=['PUT'])
def edit_message():
    data = request.get_json()
    token = data['token']
    message_id = data['message_id']
    message = data['message']
    message_edit_v1(token, message_id, message)
    save()
    return dumps({})


@APP.route('/message/remove/v1', methods=['DELETE'])
def remove_message():
    data = request.get_json()
    token = data['token']
    message_id = data['message_id']
    message_remove_v1(token, message_id)
    save()
    return dumps({})


@APP.route('/message/react/v1', methods=['POST'])
def message_react():
    data = request.get_json()
    token = data['token']
    message_id = data['message_id']
    react_id = data['react_id']
    src.message.message_react_v1(token, message_id, react_id)
    save()
    return dumps({})
    
    
@APP.route('/message/unreact/v1', methods=['POST'])
def message_unreact():
    data = request.get_json()
    token = data['token']
    message_id = int(data['message_id'])
    react_id = int(data['react_id'])
    src.message.message_unreact_v1(token, message_id, react_id)
    save()
    return dumps({})
    
    
@APP.route('/message/sendlater/v1', methods=['POST'])
def message_sendlater():
    data = request.get_json()
    token = data['token']
    channel_id = data['channel_id']
    message = data['message']
    time_sent = data['time_sent']
    message_id = src.message.message_sendlater_v1(token, channel_id, message, time_sent)
    save()
    return dumps(message_id)
    
    
@APP.route('/message/share/v1', methods=['POST'])
def message_share():
    data = request.get_json()
    token = data['token']
    og_message_id = data['og_message_id']
    message = data['message']
    channel_id = data['channel_id']
    dm_id = data['dm_id']
    output = src.message.message_share_v1(token, og_message_id, message, channel_id, dm_id)
    save()
    return dumps(output)
    
    
@APP.route('/search/v1', methods=['GET'])
def message_search():
    data = request.args.to_dict()
    token = data['token']
    query_str = data['query_str']
    messages = src.search.search_v1(token, query_str)
    save()
    return dumps(messages)


@APP.route("/clear/v1", methods=['DELETE'])
def clear():
    clear_v1()
    save()
    return dumps({})

@APP.route("/user/stats/v1", methods=['GET'])
def user_stats():
    data = request.args.to_dict()
    token = data['token']
    user_stats = src.users.user_stats_v1(token)
    save()
    return dumps(user_stats)

@APP.route("/users/stats/v1", methods=['GET'])
def users_stats():
    data = request.args.to_dict()
    token = data['token']
    users_stats = users_stats_v1(token)
    save()
    return dumps(users_stats)


@APP.route("/auth/register/v2", methods=['POST'])
def register():
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    name_first = data['name_first']
    name_last = data['name_last']
    user_info = auth_register_v2(email, password, name_first, name_last)
    save()
    return dumps(user_info)


@APP.route("/channels/create/v2", methods=['POST'])
def channel_create():
    payload = request.get_json()
    token = payload['token']
    name = payload['name']
    is_public = payload['is_public']
    return_info = channels_create_v2(token, name, is_public)
    #update_workspace_stats()
    save()
    return dumps(return_info)


@APP.route("/channels/list/v2", methods=['GET'])
def channel_list():
    token = request.args.get('token')
    return_info = channels_list_v2(token)
    save()
    return dumps(return_info)


@APP.route("/channels/listall/v2", methods=['GET'])
def channel_list_all():
    token = request.args.get('token')
    return_info = channels_listall_v2(token)
    save()
    return dumps(return_info)


@APP.route("/auth/login/v2", methods=['POST'])
def login():
    data = request.get_json()
    email = data["email"]
    password = data["password"]
    user_info = auth_login_v2(email, password)
    save()
    return dumps(user_info)


@APP.route("/auth/logout/v1", methods=['POST'])
def logout():
    token = request.get_json()
    token = token['token']
    auth_logout_v1(token)
    save()
    return dumps({})


@APP.route("/dm/create/v1", methods=['POST'])
def dm_create():
    data = request.get_json()
    token = data['token']
    u_ids = data['u_ids']
    dm_id = dm_create_v1(token, u_ids)
    #update_workspace_stats()
    save()
    return dumps(dm_id)


@APP.route("/dm/list/v1", methods=['GET'])
def dm_list():
    token = request.args.get('token')
    dms = dm_list_v1(token)
    save()
    return dumps(dms)


@APP.route("/dm/remove/v1", methods=['DELETE'])
def dm_remove():
    data = request.get_json()
    token = data['token']
    dm_id = int(data['dm_id'])
    dm_remove_v1(token, dm_id)

    save()
    return dumps({})


@APP.route("/dm/leave/v1", methods=['POST'])
def dm_leave():
    data = request.get_json()
    token = data['token']
    dm_id = int(data['dm_id'])
    dm_leave_v1(token, dm_id)
    save()
    return dumps({})


@APP.route("/dm/details/v1", methods=['GET'])
def dm_details():
    data = request.args.to_dict()
    token = data['token']
    dm_id = int(data['dm_id'])
    dms = dm_details_v1(token, dm_id)
    save()
    return dumps(dms)


@APP.route("/dm/messages/v1", methods=['GET'])
def dm_messages():
    data = request.args.to_dict()
    token = data['token']
    dm_id = int(data['dm_id'])
    start = int(data['start'])
    dms = dm_messages_v1(token, dm_id, start)
    save()
    return dumps(dms)


@APP.route("/message/senddm/v1", methods=['POST'])
def dm_senddm():
    data = request.get_json()
    token = data['token']
    dm_id = int(data['dm_id'])
    msg = data['message']
    msg_id = message_senddm_v1(token, dm_id, msg)
    save()
    return dumps(msg_id)


@APP.route("/users/all/v1", methods=['GET'])
def user_list():
    token = request.args.get('token')
    return_info = users_all_v1(token)
    save()
    return dumps(return_info)


@APP.route("/user/profile/v1", methods=['GET'])
def user_profile():
    data = request.args.to_dict()
    token = data['token']
    u_id = int(data['u_id'])
    return_info = user_profile_v1(token, u_id)
    save()
    return dumps(return_info)


@APP.route("/user/profile/setname/v1", methods=['PUT'])
def user_put_name():
    input = request.get_json()
    token = input['token']
    name_first = input['name_first']
    name_last = input['name_last']
    return_info = user_profile_setname_v1(token, name_first, name_last)
    save()
    return dumps(return_info)


@APP.route("/user/profile/setemail/v1", methods=['PUT'])
def user_put_email():
    input = request.get_json()
    token = input['token']
    email = input['email']
    return_info = user_profile_setemail_v1(token, email)
    save()
    return dumps(return_info)


@APP.route("/user/profile/sethandle/v1", methods=['PUT'])
def user_put_handle():
    input = request.get_json()
    token = input['token']
    handle_str = input['handle_str']
    return_info = user_profile_sethandle_v1(token, handle_str)
    save()
    return dumps(return_info)

@APP.route("/user/profile/uploadphoto/v1", methods=['POST'])
def user_set_profile_image():
    input = request.get_json()
    token = input['token']
    img_url = input['img_url']
    x_start = input['x_start']
    y_start = input['y_start']
    x_end = input['x_end']
    y_end = input['y_end']
    return_info = user_profile_uploadphoto_v1(token, img_url, x_start, y_start, x_end, y_end)
    save()
    return dumps(return_info)

@APP.route('/static/<path:path>')
def send_image(path):
    return send_from_directory('', path)


@APP.route('/admin/user/remove/v1', methods=['DELETE'])
def remove_user():
    input = request.get_json()
    token = input['token']
    u_id = int(input['u_id'])
    return_info = admin_user_remove_v1(token, u_id)
    save()
    return dumps(return_info)


@APP.route('/admin/userpermission/change/v1', methods=['POST'])
def change_permissions():
    input = request.get_json()
    token = input['token']
    u_id = int(input['u_id'])
    permission_id = int(input['permission_id'])
    return_info = admin_userpermission_change_v1(token, u_id, permission_id)
    save()
    return dumps(return_info)

@APP.route('/message/pin/v1', methods=['POST'])
def message_pin():
    input = request.get_json()
    token = input['token']
    message_id = int(input['message_id'])
    message_pin_v1(token, message_id)
    save()
    return{}

@APP.route('/message/unpin/v1', methods=['POST'])
def message_unpin():
    input = request.get_json()
    token = input['token']
    message_id = int(input['message_id'])
    message_unpin_v1(token, message_id)
    save()
    return{}

@APP.route('/message/sendlaterdm/v1', methods=['POST'])
def message_sendlater_dm():
    input = request.get_json()
    token = input['token']
    dm_id = int(input['dm_id'])
    message = input['message']
    time_sent = input['time_sent']

    message_id = message_sendlaterdm_v1(token, dm_id, message, time_sent)
    save()
    return dumps(message_id)

@APP.route('/standup/start/v1', methods=['POST'])
def standup_start():
    args = request.get_json()
    token = args['token']
    channel_id = args['channel_id']
    length = args['length']
    time_finish = standup_start_v1(token, channel_id, length)
    save()
    return dumps(time_finish)

@APP.route('/standup/active/v1', methods=['GET'])
def standup_active():
    data = request.args.to_dict()
    token = data['token']
    channel_id = data['channel_id']
    return_info = standup_active_v1(token, channel_id)
    save()
    return dumps(return_info)

@APP.route('/standup/send/v1', methods=['POST'])
def standup_send():
    args = request.get_json()
    token = args['token']
    channel_id = args['channel_id']
    message = args['message']
    standup_send_v1(token, channel_id, message)
    save()
    return dumps({})

@APP.route('/notifications/get/v1', methods=['GET'])
def notifications_get():
    data = request.args.to_dict()
    token = data['token']
    return_info = notifications_get_v1(token)
    save()
    return dumps(return_info)

@APP.route('/auth/passwordreset/request/v1', methods=['POST'])
def request_password_reset_request():
    input = request.get_json()
    email = input['email']
    auth_passwordreset_request_v1(email)
    save()
    return dumps({})

@APP.route('/auth/passwordreset/reset/v1', methods=['POST'])
def request_password_reset():
    input = request.get_json()
    reset_code = input['reset_code']
    new_password = input['new_password']
    auth_passwordreset_reset_v1(reset_code, new_password)
    save()
    return dumps({})



# NO NEED TO MODIFY BELOW THIS POINT
if __name__ == "__main__":
    signal.signal(signal.SIGINT, quit_gracefully)  # For coverage
    APP.run(port=config.port)  # Do not edit this port
