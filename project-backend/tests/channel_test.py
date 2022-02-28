# # tests for channels_list.py and channels_listall.py

import pytest
import requests
import json
from src.error import AccessError, InputError
from src import config
from src.create_token import generate_jwt, decode_jwt


import pytest

@pytest.fixture
def add_owner_and_member():
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
        'email': 'paul1@gmailw.com',
        'name_first': "paul",
        'name_last': 'hayes',
        'password': 'passqword'
    }
    owner = requests.post(f'{config.url}/auth/register/v2', json=user1)
    member = requests.post(f'{config.url}/auth/register/v2', json=user2)
    owner = owner.json()
    member = member.json()
    return (owner, member)




def test_channel_join_and_leave(add_owner_and_member):

    token = {'token': owner['token']}

    # channel1
    input = {'token': owner['token'],
             'name': "ACAB1312", "is_public": "True"}
    requests.post(f'{config.url}/channels/create/v2', json=input)
    # channel2
    input2 = {'token': member['token'], 'name': "SGK", "is_public": "True"}
    requests.post(f'{config.url}/channels/create/v2', json=input2)
    # channel3
    input2 = {'token': member['token'],
             'name': "Paul", "is_public": "False"}
    requests.post(f'{config.url}/channels/create/v2', json=input2)
    #join channel 2
    requests.post(f'{config.url}/channel/join/v2', json={
        'token': owner['token'],
        'channel_id': 2
    })
    #invite channel 3
    channel_invite = {
        'token': member['token'], 'channel_id': 3, 'u_id': owner['auth_user_id']}
    requests.post(f'{config.url}/channel/invite/v2', json=channel_invite)

    resp = requests.get(f'{config.url}/channels/list/v2', token)
    resp = json.loads(resp.text)
    print(resp)
    requests.post(f'{config.url}/channel/leave/v1', json={
        'token': owner['token'],
        'channel_id': 3
    })
    resp = requests.get(f'{config.url}/channels/list/v2', token)
    resp = json.loads(resp.text)
    assert resp['channels'][0]['name'] == "ACAB1312"
    assert resp['channels'][1]['name'] == "SGK"


def test_bad_token_channel_list(add_owner_and_member):

    token = {'token': "123faketoken"}
    resp = (requests.get(f'{config.url}/channels/list/v2', json=token))
    resp = resp.json()
    assert resp['code'] == AccessError.code


def test_mutltiple_channels(add_owner_and_member):

    token = {'token': owner['token']}
    input1 = {'token': owner['token'],
              'name': "ACAB1312", "is_public": "True"}
    input2 = {'token': owner['token'], 'name': "SGK", "is_public": "True"}
    input3 = {'token': owner['token'], 'name': "NT", "is_public": "True"}
    requests.post(f'{config.url}/channels/create/v2', json=input1)
    requests.post(f'{config.url}/channels/create/v2', json=input2)
    requests.post(f'{config.url}/channels/create/v2', json=input3)
    data = requests.get(f'{config.url}/channels/list/v2', token)
    data = data.json()
    assert data['channels'][0]['name'] == "ACAB1312"
    assert data['channels'][1]['name'] == "SGK"
    assert data['channels'][2]['name'] == "NT"


def test_list_all(add_owner_and_member):

    token = {'token': owner['token']}
    input1 = {'token': owner['token'],
              'name': "ACAB1312", "is_public": "True"}
    input2 = {'token': owner['token'], 'name': "SGK", "is_public": "True"}
    input3 = {'token': owner['token'], 'name': "NT", "is_public": "True"}
    requests.post(f'{config.url}/channels/create/v2', json=input1)
    requests.post(f'{config.url}/channels/create/v2', json=input2)
    requests.post(f'{config.url}/channels/create/v2', json=input3)
    data = requests.get(f'{config.url}/channels/listall/v2', token)
    data = data.json()
    assert data['channels'][0]['name'] == "ACAB1312"
    assert data['channels'][1]['name'] == "SGK"
    assert data['channels'][2]['name'] == "NT"
    assert data['channels'][0]['channel_id'] == 1
    assert data['channels'][1]['channel_id'] == 2
    assert data['channels'][2]['channel_id'] == 3


def test_logged_out_list_and_listall(add_owner_and_member):

    token = {'token': owner['token']}
    input1 = {'token': owner['token'],
              'name': "Group chat", "is_public": "True"}
    requests.post(f'{config.url}/channels/create/v2', json=input1)
    requests.post(f'{config.url}/auth/logout/v1', json=token)
    list1 = requests.get(f'{config.url}/channels/list/v2', json=token)
    list1 = json.loads(list1.text)
    list2 = requests.get(f'{config.url}/channels/listall/v2', json=token)
    list2 = list2.json()
    assert list1['code'] == AccessError.code
    assert list2['code'] == AccessError.code


def test_bad_token_list_and_listall():

    input1 = {'token': owner['token'],
              'name': "Group chat", "is_public": "True"}
    requests.post(f'{config.url}/channels/create/v2', json=input1)
    token = {'token': "bad_token"}
    list1 = requests.get(f'{config.url}/channels/list/v2', token)
    list1 = json.loads(list1.text)
    list2 = requests.get(f'{config.url}/channels/listall/v2', token)
    list2 = list2.json()
    assert list1['code'] == AccessError.code
    assert list2['code'] == AccessError.code


def test_removed_user_list_and_listall(add_owner_and_member):

    input1 = {'token': owner['token'],
              'name': "Group chat", "is_public": "True"}
    requests.post(f'{config.url}/channels/create/v2', json=input1)
    input2 = {'token': owner['token'], 'u_id': member['auth_user_id']}
    requests.delete(
        f'{config.url}/admin/user/remove/v1', json=input2)
    token = {'token': member['token']}
    list1 = requests.get(f'{config.url}/channels/list/v2', token)
    list1 = json.loads(list1.text)
    list2 = requests.get(f'{config.url}/channels/listall/v2', token)
    list2 = list2.json()
    assert list1['code'] == AccessError.code
    assert list2['code'] == AccessError.code



def test_no_channel():
    requests.delete(f'{config.url}/clear/v1')
    data = {
        'email': 'hansolk@gmail.com',
        'name_first': "hansol",
        'name_last': 'raspberry',
        'password': 'password'
    }
    response = requests.post(f'{config.url}/auth/register/v2', json=data)
    response = response.json()
    resp = requests.get(f'{config.url}/channels/list/v2', response)
    resp = json.loads(resp.text)
    assert resp == {'channels': []}
    resp = requests.get(f'{config.url}/channels/listall/v2', response)
    resp = resp.json()
    assert resp == {'channels': []}

def test_bad_session_list(add_owner_and_member):
    token = {'token': owner['token']}
    requests.post(f'{config.url}/auth/logout/v1', json=token)
    resp = requests.get(f'{config.url}/channels/list/v2', {
        'token' : owner['token']
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code
    assert resp['message'] == "<p>Session ID does not exist</p>"
    resp = requests.get(f'{config.url}/channels/listall/v2', token)
    resp = resp.json()
    assert resp['code'] == AccessError.code
    assert resp['message'] == "<p>Session ID does not exist</p>"
    input = {'token': owner['token'],
             'name': "ACAB1312", "is_public": "True"}
    resp = requests.post(f'{config.url}/channels/create/v2', json=input)
    resp = resp.json()
    assert resp['code'] == AccessError.code
    assert resp['message'] == "<p>User logged out</p>"


def test_bad_user_id_list(add_owner_and_member):
    corrupt_token = decode_jwt(owner['token'])
    corrupt_token['u_id']
    corrupt_token['u_id'] = 999999
    corrupt_token = generate_jwt(
    corrupt_token['u_id'], corrupt_token['permission_id'], corrupt_token['handle_str'], corrupt_token['session_id'])
    resp = requests.get(f'{config.url}/channels/list/v2', {
        'token' : corrupt_token
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code
    assert resp['message'] == "<p>ID does not exist</p>"
    input = {'token': corrupt_token,
             'name': "ACAB1312", "is_public": "True"}
    resp = requests.post(f'{config.url}/channels/create/v2', json=input)
    resp = resp.json()
    assert resp['code'] == AccessError.code
    assert resp['message'] == "<p>ID does not exist</p>"

def test_channel_create_bad_names(add_owner_and_member):
    #short name
    input = {'token': owner['token'],
             'name': "", "is_public": "True"}
    resp = requests.post(f'{config.url}/channels/create/v2', json=input)
    resp = resp.json()
    assert resp['code'] == InputError.code
    assert resp['message'] == "<p>Num of characters in name is less than 1 or more than 20</p>"
    #long name
    input = {'token': owner['token'],
             'name': "1234567891011122324252627282920", "is_public": "True"}
    resp = requests.post(f'{config.url}/channels/create/v2', json=input)
    resp = resp.json()
    assert resp['code'] == InputError.code
    assert resp['message'] == "<p>Num of characters in name is less than 1 or more than 20</p>"