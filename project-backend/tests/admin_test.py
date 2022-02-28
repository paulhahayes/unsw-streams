import pytest
import json
import requests
from src.error import InputError, AccessError
from src.auth import auth_register_v2, auth_login_v2, auth_logout_v1
from src.other import clear_v1
from src.admin import MEMBER, admin_user_remove_v1, admin_userpermission_change_v1
from src.channels import channels_create_v2
from src.channel import channel_details_v2, channel_join_v2, channel_invite_v2, channel_messages_v2
from src.dm import dm_create_v1, dm_messages_v1
from src.message import message_send_v1, message_senddm_v1
from src.users import user_profile_v1, users_all_v1
from src.data_store import data_store
import pickle
from src import config
OWNER = 1
MEMBER = 2


@pytest.fixture
def add_owner_and_member():
    requests.delete(f"{config.url}/clear/v1")
    global owner
    global member
    user1 = {
        'email': 'hqw@gmailw.com',
        'name_first': "hansol11",
        'name_last': 'raspberry',
        'password': 'password'
    }
    user2 = {
        'email': 'qweqwe@gmailw.com',
        'name_first': "hqwel11",
        'name_last': 'rasasdfry',
        'password': 'passqword'
    }
    owner = requests.post(f'{config.url}/auth/register/v2', json=user1)
    member = requests.post(f'{config.url}/auth/register/v2', json=user2)
    owner = owner.json()
    member = member.json()
    return (owner, member)


def test_change_permission_route(add_owner_and_member):

    input = {'token': owner['token'], 'u_id': 1, "permission_id": 1}
    resp = requests.post(
        f'{config.url}/admin/userpermission/change/v1', json=input)
    input = {'token': member['token'], 'u_id': 0, "permission_id": 2}
    resp = requests.post(
        f'{config.url}/admin/userpermission/change/v1', json=input)
    assert resp.status_code == 200

# def test_change_invalid_permission_route(add_owner_and_member):

#     input = {'token': owner['token'], 'u_id': 0, "permission_id": 2}
#     resp = requests.post(
#         f'{config.url}/admin/userpermission/change/v1', json=input)
#     resp = json.loads(resp.text)
#     assert resp['code'] == InputError.code


# def test_valid_remove_route(add_owner_and_member):

#     input = {'token': owner['token'], 'u_id': member['auth_user_id']}
#     delete_response = requests.delete(
#         f'{config.url}/admin/user/remove/v1', json=input)
#     delete_response = json.loads(delete_response.text)
#     assert delete_response == {}


# def test_logged_out_route(add_owner_and_member):

#     token = {'token': owner['token']}
#     input = {'token': owner['token'], 'u_id': member['auth_user_id']}
#     requests.post(f'{config.url}/auth/logout/v1', json=token)
#     delete_response = requests.delete(
#         f'{config.url}/admin/user/remove/v1', json=input)
#     delete_response = json.loads(delete_response.text)
#     assert delete_response['code'] == AccessError.code
#     input = {'token': input['token'], 'u_id': 0, "permission_id": 2}
#     resp = requests.post(
#         f'{config.url}/admin/userpermission/change/v1', json=input)
#     resp = json.loads(resp.text)
#     assert delete_response['code'] == AccessError.code


# def test_bad_token_out_route(add_owner_and_member):

#     input = {'token': "bad token", 'u_id': member['auth_user_id']}
#     delete_response = requests.delete(
#         f'{config.url}/admin/user/remove/v1', json=input)
#     delete_response = json.loads(delete_response.text)
#     assert delete_response['code'] == AccessError.code
#     input = {'token': "bad token", 'u_id': 0, "permission_id": 2}
#     resp = requests.post(
#         f'{config.url}/admin/userpermission/change/v1', json=input)
#     resp = json.loads(resp.text)
#     assert delete_response['code'] == AccessError.code


# def test_removed_user_profile_route(add_owner_and_member):

#     remove_user = {'token': member['token'], 'u_id': member['auth_user_id']}
#     input = {'token': owner['token'], 'u_id': member['auth_user_id']}
#     requests.delete(
#         f'{config.url}/admin/user/remove/v1', json=input)
#     resp = requests.get(f'{config.url}/user/profile/v1', remove_user)
#     resp.status_code == AccessError.code


# def test_bad_inputs_admisn(add_owner_and_member):

#     # invalid user id
#     input = {'token': owner['token'], 'u_id':  99999999999, "permission_id": 1}
#     resp = requests.post(
#         f'{config.url}/admin/userpermission/change/v1', json=input)
#     resp = resp.json()
#     assert resp['code'] == InputError.code

#     # invalid permission code
#     input = {'token': owner['token'],
#              'u_id':  member['auth_user_id'], "permission_id": 9999999999}
#     resp = requests.post(
#         f'{config.url}/admin/userpermission/change/v1', json=input)
#     resp = resp.json()
#     assert resp['code'] == InputError.code

#     # no admin rights
#     input = {'token': member['token'],
#              'u_id':  member['auth_user_id'], "permission_id": 1}
#     resp = requests.post(
#         f'{config.url}/admin/userpermission/change/v1', json=input)
#     resp = resp.json()
#     assert resp['code'] == AccessError.code

#     # invalid user id
#     input = {'token': owner['token'], 'u_id': 999999999}
#     resp = requests.delete(
#         f'{config.url}/admin/user/remove/v1', json=input)
#     resp = resp.json()
#     assert resp['code'] == InputError.code

#     # only global owner
#     input = {'token': owner['token'], 'u_id': owner['auth_user_id']}
#     resp = requests.delete(
#         f'{config.url}/admin/user/remove/v1', json=input)
#     resp = resp.json()
#     assert resp['code'] == InputError.code

#     # no admin rights
#     input = {'token': member['token'], 'u_id': member['auth_user_id']}
#     resp = requests.delete(
#         f'{config.url}/admin/user/remove/v1', json=input)
#     resp = resp.json()
#     assert resp['code'] == AccessError.code


# def test_removed_messages(add_owner_and_member):

#     input = {'token': member['token'],
#              'name': "Paul", "is_public": "True"}
#     requests.post(f'{config.url}/channels/create/v2', json=input)

#     requests.post(f'{config.url}/channel/join/v2', json={
#         'token': owner['token'],
#         'channel_id': 1
#     })
#     message = {
#         'token': member['token'], 'channel_id': 1,
#         'message': "dont delete this message"

#     }
#     requests.post(f'{config.url}//message/send/v1', json=message)

#     message2 = {
#         'token': member['token'], 'channel_id': 1,
#         'message': "Please"

#     }
#     requests.post(f'{config.url}//message/send/v1', json=message2)
#     message3 = {
#         'token': owner['token'], 'channel_id': 1,
#         'message': "No"

#     }
#     requests.post(f'{config.url}//message/send/v1', json=message3)

#     channel_messages = requests.get(f"{config.url}/channel/messages/v2",
#                                     {
#                                         'token': owner['token'],
#                                         'channel_id': 1,
#                                         'start': 0
#                                     })

#     channel_messages = channel_messages.json()
#     assert channel_messages['messages'][0]['message'] == "dont delete this message"
#     assert channel_messages['messages'][1]['message'] == "Please"
#     assert channel_messages['messages'][2]['message'] == "No"

#     input = {'token': owner['token'], 'u_id': member['auth_user_id']}
#     requests.delete(
#         f'{config.url}/admin/user/remove/v1', json=input)

#     channel_messages = requests.get(f"{config.url}/channel/messages/v2",
#                                     {
#                                         'token': owner['token'],
#                                         'channel_id': 1,
#                                         'start': 0
#                                     })
#     channel_messages = channel_messages.json()
#     assert channel_messages['messages'][0]['message'] == "Removed user"
#     assert channel_messages['messages'][1]['message'] == "Removed user"
#     assert channel_messages['messages'][2]['message'] == "No"


# def test_remove_dm_messages(add_owner_and_member):

#     dm = requests.post(f"{config.url}/dm/create/v1",
#                        json={"token": owner['token'], "u_ids": [member['auth_user_id']]})
#     dm = dm.json()
#     requests.post(f"{config.url}/message/senddm/v1",
#                   json={'token': member['token'], 'dm_id': dm['dm_id'], 'message': 'hello'})
#     requests.post(f"{config.url}/message/senddm/v1",
#                   json={'token': owner['token'], 'dm_id': dm['dm_id'], 'message': 'bye'})
#     resp = requests.get(f"{config.url}/dm/messages/v1",
#                         {'token': owner['token'], 'dm_id': dm['dm_id'], 'start': 0})
#     resp = resp.json()
#     assert resp['messages'][0]['message'] == "hello"
#     assert resp['messages'][1]['message'] == "bye"
#     input = {'token': owner['token'], 'u_id': member['auth_user_id']}
#     requests.delete(
#         f'{config.url}/admin/user/remove/v1', json=input)
#     resp = requests.get(f"{config.url}/dm/messages/v1",
#                         {'token': owner['token'], 'dm_id': dm['dm_id'], 'start': 0})
#     resp = resp.json()
#     assert resp['messages'][0]['message'] == "Removed user"
#     assert resp['messages'][1]['message'] == "bye"


# def test_removed_from_channel(add_owner_and_member):
#     user3 = {
#         'email': 'shawty@gmail.com',
#         'name_first': "hansol11",
#         'name_last': 'raspberry',
#         'password': 'password'
#     }
#     user3 = requests.post(f'{config.url}/auth/register/v2', json=user3)
#     user3 = user3.json()

#     input = {'token': owner['token'],
#              'name': "Paul", "is_public": "True"}
#     requests.post(f'{config.url}/channels/create/v2', json=input)

#     input = {'token': owner['token'],
#              'name': "channel2", "is_public": "True"}
#     requests.post(f'{config.url}/channels/create/v2', json=input)

#     requests.post(f'{config.url}/channel/join/v2', json={
#         'token': member['token'],
#         'channel_id': 1
#     })
#     requests.post(f'{config.url}/channel/join/v2', json={
#         'token': member['token'],
#         'channel_id': 2
#     })
#     requests.post(f'{config.url}/channel/join/v2', json={
#         'token': user3['token'],
#         'channel_id': 1
#     })
#     requests.post(f"{config.url}/channel/addowner/v1",
#                   json={
#                       'token': owner['token'],
#                       'channel_id': 1,
#                       'u_id': member['auth_user_id']
#                   })
#     requests.post(f"{config.url}/channel/addowner/v1",
#                   json={
#                       'token': owner['token'],
#                       'channel_id': 1,
#                       'u_id': user3['auth_user_id']
#                   })

#     channel_details = requests.get(f'{config.url}/channel/details/v2', {
#         'token': owner['token'],
#         'channel_id': 1
#     })
#     channel_details = channel_details.json()

#     assert len(channel_details['all_members']) == 3
#     assert len(channel_details['owner_members']) == 3
#     input = {'token': owner['token'], 'u_id': member['auth_user_id']}
#     requests.delete(
#         f'{config.url}/admin/user/remove/v1', json=input)
#     channel_details = requests.get(f'{config.url}/channel/details/v2', {
#         'token': owner['token'],
#         'channel_id': 1
#     })
#     channel_details2 = requests.get(f'{config.url}/channel/details/v2', {
#         'token': owner['token'],
#         'channel_id': 1
#     })
    
#     resp = requests.get(f'{config.url}/channels/list/v2',
#                         {'token': member['token']})
#     resp = json.loads(resp.text)
#     assert resp['code'] == AccessError.code

#     channel_details = channel_details.json()
#     channel_details2 = channel_details2.json()
#     for channel in channel_details['all_members']:
#         assert member['auth_user_id'] != channel['u_id']

#     for channel in channel_details['owner_members']:
#         assert member['auth_user_id'] != channel['u_id']

#     for channel in channel_details2['all_members']:
#         assert member['auth_user_id'] != channel['u_id']

#     for channel in channel_details2['owner_members']:
#         assert member['auth_user_id'] != channel['u_id']


# def test_no_messages_channels(add_owner_and_member):
#     input = {'token': owner['token'], 'u_id': member['auth_user_id']}
#     requests.delete(
#         f'{config.url}/admin/user/remove/v1', json=input)


# ##### OFFLINE TESTS #######


# def test_valid_admin_change():

#     clear_v1()
#     user1 = auth_register_v2("z5303576@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")
#     user2 = auth_register_v2("z5303ewew@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")
#     user3 = auth_register_v2("zuser3@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")
#     admin_userpermission_change_v1(
#         user1['token'], user2['auth_user_id'],  OWNER)
#     auth_logout_v1(user2['token'])
#     user2 = auth_login_v2("z5303ewew@gmail.com", "Aceofspades1")
#     assert admin_userpermission_change_v1(
#         user2['token'], user3['auth_user_id'], OWNER) == {}


# def test_unknown_u_id():

#     clear_v1()
#     user1 = auth_register_v2("z5303576@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")

#     with pytest.raises(InputError):
#         admin_userpermission_change_v1(user1['token'], 10000, OWNER)


# def test_bad_session_admin_change():
#     clear_v1()
#     user1 = auth_register_v2("z5303576@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")
#     user2 = auth_register_v2("z5303ewew@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")

#     auth_logout_v1(user1['token'])
#     with pytest.raises(AccessError):
#         admin_userpermission_change_v1(
#             user1['token'], user2['auth_user_id'], OWNER)


# def test_non_admin_request():
#     clear_v1()
#     auth_register_v2("z5303576@gmail.com",

#                      "Aceofspades1", "Paul", "Hayes")
#     user2 = auth_register_v2("z5303ewew@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")

#     with pytest.raises(AccessError):
#         admin_userpermission_change_v1(
#             user2['token'], user2['auth_user_id'], OWNER)


# def test_invalid_single_global_owner():
#     clear_v1()
#     user1 = auth_register_v2("z5303576@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")
#     auth_register_v2("z5303ewew@gmail.com",

#                      "Aceofspades1", "Paul", "Hayes")

#     with pytest.raises(InputError):
#         admin_userpermission_change_v1(
#             user1['token'], user1['auth_user_id'], MEMBER)


# def test_unknown_permission_id():
#     clear_v1()
#     user1 = auth_register_v2("z5303576@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")
#     user2 = auth_register_v2("z5303ewew@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")

#     with pytest.raises(InputError):
#         admin_userpermission_change_v1(
#             user1['token'], user2['auth_user_id'], 100000)


# def test_bad_token():
#     clear_v1()
#     user1 = auth_register_v2("z5303576@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")
#     user2 = auth_register_v2("z5303ewew@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")
#     badtoken = user1['token'] + "Hello"

#     with pytest.raises(AccessError):
#         admin_userpermission_change_v1(badtoken, user2['auth_user_id'], OWNER)


# def test_remove_user():
#     clear_v1()
#     user1 = auth_register_v2("z5303576@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")
#     user2 = auth_register_v2("z5303ewew@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")
#     channel_id = channels_create_v2(
#         user2['token'], "Channel", True)['channel_id']
#     channel_join_v2(user1['token'], channel_id)
#     admin_user_remove_v1(user1['token'], user2['auth_user_id'])
#     channel = channel_details_v2(user1['token'], channel_id)
#     assert user2['auth_user_id'] not in channel['owner_members']
#     assert user2['auth_user_id'] not in channel['all_members']


# def test_remove_user_bad_u_id():
#     clear_v1()
#     user1 = auth_register_v2("z5303576@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")

#     with pytest.raises(InputError):
#         admin_user_remove_v1(user1['token'], 69)


# def test_remove_user_bad_session():
#     clear_v1()
#     user1 = auth_register_v2("123@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")
#     user2 = auth_register_v2("321@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")
#     auth_logout_v1(user1['token'])
#     with pytest.raises(AccessError):
#         admin_user_remove_v1(user1['token'], user2['auth_user_id'])


# def test_only_admin_remove():
#     clear_v1()
#     user1 = auth_register_v2("123@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")

#     with pytest.raises(InputError):
#         admin_user_remove_v1(user1['token'], user1['auth_user_id'])


# def test_non_admin_remove():
#     clear_v1()
#     auth_register_v2("123@gmail.com",

#                      "Aceofspades1", "Paul", "Hayes")
#     user2 = auth_register_v2("321@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")
#     user3 = auth_register_v2("543@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")

#     with pytest.raises(AccessError):
#         admin_user_remove_v1(user2['token'], user3['auth_user_id'])


# def test_remove_user_details():
#     clear_v1()
#     user1 = auth_register_v2("123@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")
#     user2 = auth_register_v2("321@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")

#     admin_user_remove_v1(user1['token'], user2['auth_user_id'])
#     payload = user_profile_v1(user1['token'], user2['auth_user_id'])
#     assert payload['user']['name_first'] == 'Removed'
#     assert payload['user']['name_last'] == 'user'
#     assert payload['user']['email'] == '321@gmail.com'
#     assert payload['user']['u_id'] == 1
#     assert payload['user']['handle_str'] == 'paulhayes0'


# def test_remove_user_alluser_details():
#     clear_v1()
#     user1 = auth_register_v2("123@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")
#     user2 = auth_register_v2("321@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")

#     admin_user_remove_v1(user1['token'], user2['auth_user_id'])

#     auth_register_v2("321@gmail.com",

#                      "Aceofspades1", "Paul", "Hayes")

#     assert len(users_all_v1(user1['token'])['users']) == 2


# def test_remove_message():
#     clear_v1()
#     user1 = auth_register_v2("1@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")
#     user2 = auth_register_v2("2@gmail.com",

#                              "Aceofspades1", "michael", "Hayes")

#     user3 = auth_register_v2("3@gmail.com",

#                              "Aceofspades1", "john", "Hayes")
#     channel_id = channels_create_v2(
#         user1['token'], "Channel", True)['channel_id']
#     channel_join_v2(user2['token'], 1)
#     channel_invite_v2(user1['token'], 1, user3['auth_user_id'])
#     message_send_v1(user2['token'], 1, "hi")
#     channel_messages_v2(user2['token'], channel_id, 0)


# def test_remove_dm_message():
#     clear_v1()
#     user1 = auth_register_v2("z5303576@gmail.com",

#                              "Aceofspades1", "Paul", "Hayes")
#     user2 = auth_register_v2("john@gmail.com",

#                              "Aceofspades1", "michael", "Hayes")

#     dm = dm_create_v1(user1['token'], [user2['auth_user_id']])['dm_id']
#     message_senddm_v1(user2['token'], dm, "Hello World")
#     message_senddm_v1(user2['token'], dm, "Hello World2")
#     message_senddm_v1(user2['token'], dm, "Hello World")
#     admin_user_remove_v1(user1['token'], user2['auth_user_id'])
#     dm_one = dm_messages_v1(user1['token'], dm, 0)['messages'][0]['message']
#     dm_two = dm_messages_v1(user1['token'], dm, 0)['messages'][1]['message']
#     assert dm_one == "Removed user"
#     assert dm_two == "Removed user"
