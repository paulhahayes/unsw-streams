"""
These tests are for message_share
History
1. Honggyo Suh implementd test cases for iteration 3 on 05th Nov 2021.
"""

import re
import json
import requests
import src.config
import pytest
import src.channel
import src.message
import src.channels
import src.auth
import src.error
import src.other
import src.create_token
from src import config
DM = "2"
MSG = "1"




@pytest.fixture
def setup():

    requests.delete(f'{config.url}/clear/v1')
    
    global user1
    global user2
    global user3
    user1 = requests.post(f'{config.url}/auth/register/v2', json={
        'email': 'tester1@gmail.com',
        'password': 'password',
        'name_first': 'tester1_first',
        'name_last': 'tesetr1_last'})
    user2 = requests.post(f'{config.url}/auth/register/v2', json={
        'email': 'tester2@gmail.com',
        'password': 'password',
        'name_first': 'tester2_first',
        'name_last': 'tesetr2_last'})
    user3 = requests.post(f'{config.url}/auth/register/v2', json={
        'email': 'tester3@gmail.com',
        'password': 'password',
        'name_first': 'tester3_first',
        'name_last': 'tesetr3_last'})
    user1 = user1.json()
    user2 = user2.json()
    user3 = user3.json()
    
    global test_channel
    test_channel = requests.post(f'{config.url}/channels/create/v2', json={
        'token': user1['token'],
        'name': 'test_channel',
        'is_public': True})
    test_channel = test_channel.json()

    requests.post(f'{config.url}/channel/invite/v2', json={
        'token': user1['token'], 
        'channel_id': test_channel['channel_id'], 
        'u_id': user2['auth_user_id']
    })
    
    global test_message1
    test_message1 = requests.post(f'{config.url}/message/send/v1', json={
        'token': user1['token'],
        'channel_id': test_channel['channel_id'],
        'message': "Hello world"
    })
    test_message1 = test_message1.json()

    global test_dm
    u_ids = src.create_token.decode_jwt(user2['token'])['u_id']
    test_dm = requests.post(f'{config.url}/dm/create/v1', json={
        'token': user1['token'],
        'u_ids': [u_ids]
    })
    test_dm = test_dm.json()

    global test_message2
    test_message2 = requests.post(f'{config.url}/message/senddm/v1', json={
        'token': user1['token'],
        'dm_id': test_dm['dm_id'],
        'message': 'Hello?'
    })
    test_message2 = test_message2.json()
    
    
    
    global dm_msg_id
    dm_msg_id = test_message2['message_id']


def test_message_share_invalid_channelID(setup):

    input = {
        'token': user1['token'], 
        'og_message_id': test_message1['message_id'],
        'message': '',
        'channel_id': 0,
        'dm_id': -1
    }
    result = requests.post(f'{config.url}/message/share/v1', json=input)
    result = json.loads(result.text)
    assert result['code'] == 400
    

def test_message_share_invalid_dmID(setup):
    
    input = {
        'token': user1['token'], 
        'og_message_id': dm_msg_id,
        'message': '',
        'channel_id': -1,
        'dm_id': 999
    }
    result = requests.post(f'{config.url}/message/share/v1', json=input)
    print(result)
    result = json.loads(result.text)
    
    assert result['code'] == 400


def test_message_share_both_id_default(setup):

    input = {
        'token': user1['token'], 
        'og_message_id': test_message1['message_id'],
        'message': '',
        'channel_id': -1,
        'dm_id': -1
    }
    result = requests.post(f'{config.url}/message/share/v1', json=input)
    result = json.loads(result.text)
    assert result['code'] == 400


def test_message_share_invalid_messageID(setup):

    input = {
        'token': user1['token'], 
        'og_message_id': 9,
        'message': '',
        'channel_id': test_channel['channel_id'],
        'dm_id': -1
    }
    result = requests.post(f'{config.url}/message/share/v1', json=input)
    result = json.loads(result.text)
    assert result['code'] == 400


def test_message_share_too_long(setup):

    input = {
        'token': user1['token'], 
        'og_message_id': 0,
        'message': 'Hello world' * 1000,
        'channel_id': test_channel['channel_id'],
        'dm_id': -1
    }
    result = requests.post(f'{config.url}/message/share/v1', json=input)
    result = json.loads(result.text)
    assert result['code'] == 400


def test_message_share_not_in_channel(setup):

    input = {
        'token': user3['token'], 
        'og_message_id': test_message1['message_id'],
        'message': '',
        'channel_id': test_channel['channel_id'],
        'dm_id': -1
    }
    result = requests.post(f'{config.url}/message/share/v1', json=input)
    result = json.loads(result.text)
    assert result['code'] == 403
    
# def test_message_share_in_general(setup):
    
#     input = {
#         'token': user1['token'], 
#         'og_message_id': test_message1['message_id'],
#         'message': '',
#         'channel_id': test_channel['channel_id'],
#         'dm_id': -1
#     }
#     result = requests.post(f'{config.url}/message/share/v1', json=input)

#     assert str(result) == '<Response [200]>'

def test_message_dm_to_ch_share(setup):
    dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':user1['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    msg=requests.post(f"{config.url}/message/senddm/v1", json = {'token': user1['token'], 'dm_id': dm_id, 'message': 'hello'})
    msg = msg.json()
    input = {
        'token': user1['token'], 
        'og_message_id': msg['message_id'],
        'message': '',
        'channel_id': test_channel['channel_id'],
        'dm_id': -1
    }
    result = requests.post(f'{config.url}/message/share/v1', json=input)
    assert(result.status_code == 200)

def test_message_ch_to_dm_share(setup):
    dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':user1['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    msg=requests.post(f"{config.url}/message/senddm/v1", json = {'token': user1['token'], 'dm_id': dm_id, 'message': 'hello'})
    msg = msg.json()
    input = {
        'token': user1['token'], 
        'og_message_id': test_message1['message_id'],
        'message': '',
        'channel_id': -1,
        'dm_id': dm_id
    }
    result = requests.post(f'{config.url}/message/share/v1', json=input)
    assert(result.status_code == 200)

def test_message_ch_to_ch_share(setup):
    test_channel2 = requests.post(f'{config.url}/channels/create/v2', json={
        'token': user1['token'],
        'name': 'test_channel2',
        'is_public': True})
    test_channel2 = test_channel2.json()

    requests.post(f'{config.url}/channel/invite/v2', json={
        'token': user1['token'], 
        'channel_id': test_channel2['channel_id'], 
        'u_id': user2['auth_user_id']
    })
    input = {
        'token': user1['token'], 
        'og_message_id': test_message1['message_id'],
        'message': '',
        'channel_id': test_channel2['channel_id'],
        'dm_id': -1
    }
    result = requests.post(f'{config.url}/message/share/v1', json=input)
    assert(result.status_code == 200)

def test_message_dm_to_dm_share(setup):
    dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':user1['token'], 'u_ids': [1]})
    dm_id2 = requests.post(f"{config.url}/dm/create/v1", json = {'token':user1['token'], 'u_ids': [2]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    dm_id2 = dm_id2.json()
    dm_id2 = dm_id2['dm_id']
    msg=requests.post(f"{config.url}/message/senddm/v1", json = {'token': user1['token'], 'dm_id': dm_id, 'message': 'hello'})
    msg = msg.json()
    input = {
        'token': user1['token'], 
        'og_message_id': msg['message_id'],
        'message': '',
        'channel_id': -1,
        'dm_id': dm_id2
    }
    result = requests.post(f'{config.url}/message/share/v1', json=input)
    assert(result.status_code == 200)