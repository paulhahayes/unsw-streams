"""
These tests are for user_stats
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
import src.search
import src.create_token
from src.users import mod_user_stats_v1
from src import config
from src.other import clear_v1


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


def test_user_stats_in_general(setup):

    input = {
        'token': user1['token']
    }
    result = requests.get(f'{config.url}/user/stats/v1', input)

    assert str(result) == '<Response [200]>'


def test_mutliple_messages(setup):


    requests.post(f'{config.url}/channels/create/v2', json={
        'token': user2['token'],
        'name': 'test_channel',
        'is_public': True})
    requests.post(f'{config.url}/message/send/v1', json={
        'token': user2['token'],
        'channel_id': 2,
        'message': "Hello world"
    })
    requests.post(f'{config.url}/message/send/v1', json={
        'token': user2['token'],
        'channel_id': 1,
        'message': "Hello world"
    })
    requests.post(f'{config.url}/message/send/v1', json={
        'token': user1['token'],
        'channel_id': 1,
        'message': "Hello world2"
    })
    input = {
        'token': user1['token']
    }
    resp = requests.get(f'{config.url}/user/stats/v1', input)
    assert resp.status_code == 200


def test_mutliple_dms(setup):
    resp  = requests.post(f'{config.url}/dm/create/v1', json ={
        'token' : user1['token'],
        'u_ids' : [1]
    })
    assert resp.status_code == 200
    requests.post(f"{config.url}/message/senddm/v1", json = {'token': user1['token'], 'dm_id': 0, 'message': 'hello'})
    requests.post(f"{config.url}/message/senddm/v1", json = {'token': user2['token'], 'dm_id': 0, 'message': 'hi'})
    input = {
        'token': user1['token']
    }
    resp = requests.post(f'{config.url}/dm/create/v1', json ={
        'token' : user2['token'],
        'u_ids' : [1]
    })
    assert resp.status_code == 200
    requests.post(f"{config.url}/message/senddm/v1", json = {'token': user2['token'], 'dm_id': 1, 'message': 'hello'})
    resp = requests.get(f'{config.url}/user/stats/v1', input)
    assert resp.status_code == 200
    
def test_no_channels_dms_or_msgs():
    requests.delete(f'{config.url}/clear/v1')
    user1 = requests.post(f'{config.url}/auth/register/v2', json={
        'email': 'tester1@gmail.com',
        'password': 'password',
        'name_first': 'tester1_first',
        'name_last': 'tesetr1_last'})
    user1 = user1.json()
    input = {
        'token': user1['token']
    }
    resp = requests.get(f'{config.url}/user/stats/v1', input)
    assert resp.status_code == 200


def test_no_changes(setup):
    input = {
        'token': user1['token']
    }
    resp1 = requests.get(f'{config.url}/user/stats/v1', input)
    input = {
        'token': user1['token']
    }
    resp2 = requests.get(f'{config.url}/user/stats/v1', input)
    
    resp1 = resp1.json()
    resp2 = resp2.json()

    assert resp1 == resp2


def test_changes(setup):
    input = {
        'token': user1['token']
    }
    resp = requests.get(f'{config.url}/user/stats/v1', input)
    requests.post(f'{config.url}/message/send/v1', json={
        'token': user2['token'],
        'channel_id': 1,
        'message': "Hello world"
    })
    requests.post(f'{config.url}/channels/create/v2', json={
        'token': user1['token'],
        'name': 'test_channel2',
        'is_public': True})

    requests.post(f'{config.url}/dm/create/v1', json ={
        'token' : user1['token'],
        'u_ids' : [1]
    })
    input = {
        'token': user1['token']
    }
    resp2 = requests.get(f'{config.url}/user/stats/v1', input)

    resp = resp.json()
    resp2 = resp2.json()

    assert resp != resp2

def test_remove_user_stats(setup):
    input = {
        'token': user1['token']
    }
    requests.get(f'{config.url}/user/stats/v1', input)


def test_dm_stats(setup):
    requests.post(f'{config.url}/dm/create/v1', json ={
        'token' : user1['token'],
        'u_ids' : [0, 1, 2]
    })
    requests.post(f"{config.url}/message/senddm/v1", json = {'token': user1['token'], 'dm_id': 0, 'message': 'hello'})

    requests.post(f'{config.url}/dm/create/v1', json ={
        'token' : user2['token'],
        'u_ids' : [1, 2]
    })
    requests.post(f'{config.url}/dm/create/v1', json ={
        'token' : user2['token'],
        'u_ids' : [2]
    })
    requests.post(f"{config.url}/message/senddm/v1", json = {'token': user2['token'], 'dm_id': 1, 'message': 'hello'})

    requests.post(f"{config.url}/message/senddm/v1", json = {'token': user2['token'], 'dm_id': 0, 'message': 'hello'})




def test_new_user(setup):

    requests.post(f'{config.url}/dm/create/v1', json ={
        'token' : user2['token'],
        'u_ids' : []
    })
    
    requests.post(f"{config.url}/message/senddm/v1", json = {'token': user2['token'], 'dm_id': 0, 'message': 'hello'})

    requests.post(f"{config.url}/message/senddm/v1", json = {'token': user2['token'], 'dm_id': 0, 'message': 'hello'})
    requests.post(f'{config.url}/dm/create/v1', json ={
        'token' : user1['token'],
        'u_ids' : []
    })
    input = {
        'token': user1['token']
    }
    requests.get(f'{config.url}/user/stats/v1', input)


def test_empty():
    requests.delete(f'{config.url}/clear/v1')
    user4 = requests.post(f'{config.url}/auth/register/v2', json={
        'email': 'testergeergerr1@gmail.com',
        'password': 'password',
        'name_first': 'tester1_first',
        'name_last': 'tesetr1_last'})
    user4 = user4.json()
    input = {
        'token': user4['token']
    }
    requests.get(f'{config.url}/user/stats/v1', input)
