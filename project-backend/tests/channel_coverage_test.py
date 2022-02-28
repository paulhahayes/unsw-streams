
import pytest
import requests
import json
from src.error import AccessError, InputError
from src import config
from src.create_token import generate_jwt, decode_jwt


import pytest

@pytest.fixture
def add_owner_and_member_one_channel():
    requests.delete(f"{config.url}/clear/v1")
    global owner
    global member
    user1 = {
        'email': 'paul@gmail.com',
        'name_first': "paul", 
        'name_last': 'hayes',
        'password': 'password'
    }
    user2 = {
        'email': 'paul2@gmail.com',
        'name_first': "paul",
        'name_last': 'hayes',
        'password': 'passqword'
    }
    owner = requests.post(f'{config.url}/auth/register/v2', json=user1)
    member = requests.post(f'{config.url}/auth/register/v2', json=user2)
    owner = owner.json()
    member = member.json()
    channel_data = { 'token': owner['token'], 'name': "Comp1531", "is_public": True }
    channel  = requests.post(f'{config.url}/channels/create/v2', json=channel_data)
    channel = channel.json()

    return (owner, member, channel)



def test_logged_out_(add_owner_and_member_one_channel):
    token = {'token' : owner['token'] }
    requests.post(f'{config.url}/auth/logout/v1', json=token)
    input = {'token' : owner['token'], 'channel_id' : 1, 'u_id' : member['auth_user_id']}
    resp = requests.post(f'{config.url}/channel/invite/v2', json=input)
    resp = resp.json()
    assert resp['code'] == AccessError.code
    assert resp['message'] == "<p>User logged out</p>"


def test_corrupted_token(add_owner_and_member_one_channel):
    corrupt_token = decode_jwt(owner['token'])
    corrupt_token['u_id']
    corrupt_token['u_id'] = 999999
    corrupt_token = generate_jwt(
    corrupt_token['u_id'], corrupt_token['permission_id'], corrupt_token['handle_str'], corrupt_token['session_id'])

    resp = requests.post(f'{config.url}/channel/invite/v2', json={
        'token' : corrupt_token,
        'channel_id' : 1,
        'u_id' : member['auth_user_id']
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code
    assert resp['message'] == "<p>Unknown user</p>"

    resp  = requests.post(f'{config.url}/channel/join/v2', json= {
        'token' : corrupt_token,
        'channel_id' : 1,
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code
    assert resp['message'] == "<p>Unknown user</p>"

    requests.get(f'{config.url}/channel/messages/v2', {
        'token' : corrupt_token,
        'channel_id' : 1,
        'start' : 0
    } )

    requests.post(f'{config.url}/channel/addowner/v1', json ={
        'token' : corrupt_token,
        'channel_id' : 1,
        'u_id' : member['auth_user_id']
    })


    requests.post(f'{config.url}/channel/removeowner/v1', json = {
        'token' : corrupt_token,
        'channel_id' : 1,
        'u_id' : member['auth_user_id']
    })

    requests.post(f'{config.url}/channel/leave/v1', json = {
        'token' : corrupt_token,
        'channel_id' : 1,
    })




def test_user_already_in_channel(add_owner_and_member_one_channel):
    input = {'token' : owner['token'], 'channel_id' : 1, 'u_id' : member['auth_user_id']}
    requests.post(f'{config.url}/channel/invite/v2', json=input)
    resp = requests.post(f'{config.url}/channel/invite/v2', json=input)
    resp  = resp.json()
    assert resp['code'] == InputError.code
    assert resp['message'] == "<p>Already in channel</p>"


def test_invite_unknown_user(add_owner_and_member_one_channel):
    input = {'token' : owner['token'], 'channel_id' : 1, 'u_id' : 99999999}
    resp = requests.post(f'{config.url}/channel/invite/v2', json=input)
    resp  = resp.json()
    assert resp['code'] == InputError.code
    assert resp['message'] == "<p>Unknown u_id</p>"


def test_unkown_channel_invite(add_owner_and_member_one_channel):
    input = {'token' : owner['token'], 'channel_id' : 99999999, 'u_id' : member['auth_user_id']}
    resp = requests.post(f'{config.url}/channel/invite/v2', json=input)
    resp  = resp.json()
    assert resp['code'] == InputError.code
    assert resp['message'] == "<p>No such channel</p>"


def test_invite_non_owner(add_owner_and_member_one_channel):
    input = {'token' : member['token'], 'channel_id' : 1, 'u_id' : member['auth_user_id'] }
    resp = requests.post(f'{config.url}/channel/invite/v2', json=input)
    resp  = resp.json()
    assert resp['code'] == AccessError.code
    assert resp['message'] == "<p>Not a owner of the channel</p>"


def channel_invite_successful(add_owner_and_member_one_channel):
    input = {'token' : owner['token'], 'channel_id' : 1, 'u_id' : member['auth_user_id'] }
    resp = requests.post(f'{config.url}/channel/invite/v2', json=input)
    resp  = resp.json()
    assert resp == {}


def test_channel_details_invalid_channel(add_owner_and_member_one_channel):
    input = {'token' : owner['token'], 'channel_id' : 99999999 }
    resp = requests.get(f'{config.url}/channel/details/v2', input)
    resp  = resp.json()
    assert resp['code'] == InputError.code   
    assert resp['message'] == "<p>No such channel</p>"


def test_non_member_requesting_details(add_owner_and_member_one_channel):
    input = {'token' : member['token'], 'channel_id' : 1 }
    resp = requests.get(f'{config.url}/channel/details/v2', input)
    resp  = resp.json()
    assert resp['code'] == AccessError.code   
    assert resp['message'] == "<p>Not a member of the channel</p>"


def test_join_unkown_channel(add_owner_and_member_one_channel):
    input = {'token' : owner['token'], 'channel_id' : 99999999 }
    resp  = requests.post(f'{config.url}/channel/join/v2', json=input)
    resp  = resp.json()
    assert resp['code'] == InputError.code 
    assert resp['message'] == "<p>No such channel</p>"

def test_join_already_a_member(add_owner_and_member_one_channel):
    input = {'token' : owner['token'], 'channel_id' : 1 }
    resp  = requests.post(f'{config.url}/channel/join/v2', json=input)
    resp  = resp.json()
    assert resp['code'] == InputError.code 
    assert resp['message'] == "<p>Already a member</p>"

def test_join_private_channel(add_owner_and_member_one_channel):
    channel_data = { 'token': owner['token'], 'name': "Comp1531", "is_public": False }
    requests.post(f'{config.url}/channels/create/v2', json=channel_data)
    input = {'token' : member['token'], 'channel_id' : 2 }
    resp  = requests.post(f'{config.url}/channel/join/v2', json=input)
    resp  = resp.json()
    assert resp['code'] == AccessError.code 
    assert resp['message'] == "<p>Channel is private</p>"


def channel_messages_bad_inputs(add_owner_and_member_one_channel):
    
    
    resp = requests.get(f'{config.url}/channel/messages/v2', {
       'token' : owner['token'],
       'channel_id' : 999999,
       'start' : 0
    })
    resp = resp.json()
    assert resp['code'] == InputError.code 
    assert resp['message'] == "<p>No such channel</p>"


def channel_no_messages(add_owner_and_member_one_channel):
    
    
    resp = requests.get(f'{config.url}/channel/messages/v2', {
       'token' : owner['token'],
       'channel_id' : 1,
       'start' : 0
    })
    resp = resp.json()
    assert resp == {}



def channel_add_unkown_id_owner(add_owner_and_member_one_channel):
    resp = requests.post(f'{config.url}/channel/addowner/v1', json={
        'token' : owner['token'],
       'channel_id' : 1,
       'u_id' : 99999999
     })
    resp = resp.json()

    assert resp['code'] == InputError.code
    assert resp['message'] == "<p>user-id invalid</p>"

def test_leave_channel_id(add_owner_and_member_one_channel):

    resp = requests.post(f'{config.url}/channel/leave/v1', json = {
        'token' : owner['token'],
        'channel_id' : 999999,
    })
    resp = resp.json()
    assert resp['code'] == InputError.code
    assert resp['message'] == "<p>No such channel</p>"

def test_leave_non_member(add_owner_and_member_one_channel):

    resp = requests.post(f'{config.url}/channel/leave/v1', json = {
        'token' : member['token'],
        'channel_id' : 1,
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code
    assert resp['message'] == "<p>Not a member of the channel</p>"


def test_successful_leave(add_owner_and_member_one_channel):
    
    resp = requests.post(f'{config.url}/channel/leave/v1', json = {
        'token' : owner['token'],
        'channel_id' : 1,
    })
    resp = resp.json()
    assert resp == {}


def test_two_channels_messages(add_owner_and_member_one_channel):

    channel_two = { 'token': owner['token'], 'name': "Comp2521", "is_public": True }
    requests.post(f'{config.url}/channels/create/v2', json=channel_two)

    requests.post(f"{config.url}/message/send/v1", 
        json = {
                'token': owner['token'], 
                'channel_id': 1, 
                'message': "Hello Comp1531"
        })

    requests.post(f"{config.url}/message/send/v1", 
        json = {
                'token': owner['token'], 
                'channel_id': 2, 
                'message': "Hello Comp2521"
        })

    resp = requests.get(f'{config.url}/channel/messages/v2', {
       'token' : owner['token'],
       'channel_id' : 1,
       'start' : 0
    })
    resp = resp.json()
    assert resp['messages'][0]['message'] == 'Hello Comp1531'


def test_add_owner_two_channel(add_owner_and_member_one_channel):

    channel_two = { 'token': owner['token'], 'name': "Comp2521", "is_public": True }
    requests.post(f'{config.url}/channels/create/v2', json=channel_two)

    resp = requests.post(f'{config.url}/channel/join/v2', json= {
        'token' : member['token'],
        'channel_id' : 2,
    })

    requests.post(f'{config.url}/channel/addowner/v1', json={
        'token' : owner['token'],
       'channel_id' : 2,
       'u_id' : member['auth_user_id']
     })
    input = {'token' : owner['token'], 'channel_id' : 2 }
    resp = requests.get(f'{config.url}/channel/details/v2', input)
    resp =resp.json()
    assert member['auth_user_id'] == resp['owner_members'][1]['u_id']
