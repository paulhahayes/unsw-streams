"""
These tests are for message_react and unreact
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
from src.error import InputError
import src.other
import src.create_token



BASE_URL = "http://127.0.0.1:8010"


@pytest.fixture
def setup():

    requests.delete(f'{BASE_URL}/clear/v1')
    
    global user1
    global user2
    global user3
    user1 = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'tester1@gmail.com',
        'password': 'password',
        'name_first': 'tester1_first',
        'name_last': 'tesetr1_last'})
    user2 = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'tester2@gmail.com',
        'password': 'password',
        'name_first': 'tester2_first',
        'name_last': 'tesetr2_last'})
    user3 = requests.post(f'{BASE_URL}/auth/register/v2', json={
        'email': 'tester3@gmail.com',
        'password': 'password',
        'name_first': 'tester3_first',
        'name_last': 'tesetr3_last'})
    user1 = user1.json()
    user2 = user2.json()
    user3 = user3.json()
    
    global test_channel
    test_channel = requests.post(f'{BASE_URL}/channels/create/v2', json={
        'token': user1['token'],
        'name': 'test_channel',
        'is_public': True})
    test_channel = test_channel.json()

    requests.post(f'{BASE_URL}/channel/invite/v2', json={
        'token': user1['token'], 
        'channel_id': test_channel['channel_id'], 
        'u_id': user2['auth_user_id']
    })
    
    global test_message1
    test_message1 = requests.post(f'{BASE_URL}/message/send/v1', json={
        'token': user1['token'],
        'channel_id': test_channel['channel_id'],
        'message': "Hello world"
    })
    test_message1 = test_message1.json()


def test_message_react_invalid_message(setup):

    input = {
        'token': user1['token'], 
        'message_id': 9,
        'react_id': 1
    }
    result = requests.post(f'{BASE_URL}/message/react/v1', json=input)

    assert result.status_code == InputError.code
    

def test_message_react_invalid_reactID(setup):

    input = {
        'token': user1['token'], 
        'message_id': test_message1['message_id'],
        'react_id': 5
    }
    result = requests.post(f'{BASE_URL}/message/react/v1', json=input)

    assert result.status_code == InputError.code
    
   
def test_message_react_already_reacted(setup):

    input = {
        'token': user1['token'], 
        'message_id': test_message1['message_id'],
        'react_id': 1
    }
    requests.post(f'{BASE_URL}/message/react/v1', json=input)
    result = requests.post(f'{BASE_URL}/message/react/v1', json=input)

    assert result.status_code == InputError.code
    
    
def test_message_react_in_general(setup):

    input = {
        'token': user1['token'], 
        'message_id': test_message1['message_id'],
        'react_id': 1
    }
    input2 = {
        'token': user1['token'], 
        'message_id': test_message1['message_id'],
        'react_id': -1
    }
    
    result = requests.post(f'{BASE_URL}/message/react/v1', json=input)
    requests.post(f'{BASE_URL}/message/react/v1', json=input2)
    assert str(result) == '<Response [200]>'
    
    
def test_message_unreact_in_general(setup):

    input = {
        'token': user1['token'], 
        'message_id': test_message1['message_id'],
        'react_id': 1
    }
    input1 = {
        'token': user1['token'], 
        'message_id': test_message1['message_id'],
        'react_id': -1
    }

    result = requests.post(f'{BASE_URL}/message/react/v1', json=input)
    result = requests.post(f'{BASE_URL}/message/unreact/v1', json=input1)
    assert str(result) == '<Response [200]>'

def test_message_react_wrong_dm_msg(setup):
    dm_id = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token':user1['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    requests.post(f"{BASE_URL}/message/senddm/v1", json = {'token': user1['token'], 'dm_id': dm_id, 'message': 'hello'})
    result = requests.post(f"{BASE_URL}/message/react/v1", json = {'token': user1['token'], 'message_id': 29999, 'react_id': 1})
    #it will raise 400 error
    #result = requests.post(f"{config.url}/message/pin/v1", json = {'token': data['token'], 'message_id': response_data['message_id']})
    result = result.json()
    assert(result['code'] == 400)

def test_message_already_react(setup):

    input = {
        'token': user1['token'], 
        'message_id': test_message1['message_id'],
        'react_id': 1
    }
    requests.post(f'{BASE_URL}/message/react/v1', json=input)
    result = requests.post(f'{BASE_URL}/message/react/v1', json=input)
    #this will raise 400/ already reacted
    assert str(result) == '<Response [400]>'

def test_message_dm_react_non_member(setup):
    dm_id = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token':user1['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    msg=requests.post(f"{BASE_URL}/message/senddm/v1", json = {'token': user1['token'], 'dm_id': dm_id, 'message': 'hello'})
    msg = msg.json()
    result = requests.post(f"{BASE_URL}/message/react/v1", json = {'token': user3['token'], 'message_id': msg['message_id'], 'react_id': 1})
    #it will raise 400 error
    #result = requests.post(f"{config.url}/message/pin/v1", json = {'token': data['token'], 'message_id': response_data['message_id']})
    result = result.json()
    assert(result['code'] == 400)

def test_message_dm_already_react(setup):
    dm_id = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token':user1['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    msg=requests.post(f"{BASE_URL}/message/senddm/v1", json = {'token': user1['token'], 'dm_id': dm_id, 'message': 'hello'})
    msg = msg.json()
    requests.post(f"{BASE_URL}/message/react/v1", json = {'token': user1['token'], 'message_id': msg['message_id'], 'react_id': 1})
    result = requests.post(f"{BASE_URL}/message/react/v1", json = {'token': user1['token'], 'message_id': msg['message_id'], 'react_id': 1})
    #it will raise 400 error
    #result = requests.post(f"{config.url}/message/pin/v1", json = {'token': data['token'], 'message_id': response_data['message_id']})
    result = result.json()
    assert(result['code'] == 400)

def test_message_react_wrong_ch_msg(setup):
    dm_id = requests.post(f"{BASE_URL}/dm/create/v1", json = {'token':user1['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    requests.post(f"{BASE_URL}/message/senddm/v1", json = {'token': user1['token'], 'dm_id': dm_id, 'message': 'hello'})
    result = requests.post(f"{BASE_URL}/message/react/v1", json = {'token': user1['token'], 'message_id': 19999, 'react_id': 1})
    #it will raise 400 error
    #result = requests.post(f"{config.url}/message/pin/v1", json = {'token': data['token'], 'message_id': response_data['message_id']})
    result = result.json()
    assert(result['code'] == 400)

def test_message_non_member_react(setup):
    
    input = {
        'token': user3['token'], 
        'message_id': test_message1['message_id'],
        'react_id': 1
    }
    result = requests.post(f'{BASE_URL}/message/react/v1', json=input)
    #this will raise 400/ already reacted
    assert str(result) == '<Response [400]>'

def test_message_unreact_invalid_react(setup):

    input = {
        'token': user1['token'], 
        'message_id': test_message1['message_id'],
        'react_id': 1
    }
    input1 = {
        'token': user1['token'], 
        'message_id': test_message1['message_id'],
        'react_id': 0
    }

    result = requests.post(f'{BASE_URL}/message/react/v1', json=input)
    result = requests.post(f'{BASE_URL}/message/unreact/v1', json=input1)
    assert str(result) == '<Response [400]>'