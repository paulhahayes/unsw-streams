"""
These tests are for search
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
from src import config


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



def test_search_too_long(setup):

    input = {
        'token': user1['token'], 
        'query_str': 'string'*1000
    }
    result = requests.get(f'{config.url}/search/v1', input)
    result = json.loads(result.text)
    assert result['code'] == 400


def test_search_in_general(setup):

    input = {
        'token': user1['token'], 
        'query_str': 'Hello'
    }
    resp = requests.get(f'{config.url}/search/v1', input)
    resp = resp.json()
    assert 'Hello' in resp['messages'][0]['message']


def test_not_channel_member(setup):
    requests.post(f'{config.url}/channel/leave/v1', json = {
        'token' : user1['token'],
        'channel_id' : 1,
    })
    input = {
        'token': user1['token'], 
        'query_str': 'Hello'
    }
    resp = requests.get(f'{config.url}/search/v1', input)
    resp = resp.json()
    assert resp == {'messages': []}


def test_string_not_found(setup):
    input = {
        'token': user1['token'], 
        'query_str': 'BADSTRINGNOTGOOD'
    }
    resp = requests.get(f'{config.url}/search/v1', input)
    resp = resp.json()
    assert resp == {'messages': []}


def test_dm_working(setup):
    requests.post(f"{config.url}/dm/create/v1", json = {"token": user1['token'], "u_ids": [1, 2]})
    requests.post(f"{config.url}/message/senddm/v1", json = {'token': user1['token'], 'dm_id': 0, 'message': 'Hello'})
    input = {
        'token': user1['token'], 
        'query_str': 'Hello'
    }
    resp = requests.get(f'{config.url}/search/v1', input)
    resp = resp.json()
    assert 'Hello' in resp['messages'][0]['message']



def test_dm_member_working(setup):
    requests.post(f"{config.url}/dm/create/v1", json = {"token": user1['token'], "u_ids": [1, 2]})
    requests.post(f"{config.url}/message/senddm/v1", json = {'token': user1['token'], 'dm_id': 0, 'message': 'Hello'})
    input = {
        'token': user2['token'], 
        'query_str': 'Hello'
    }
    resp = requests.get(f'{config.url}/search/v1', input)
    resp = resp.json()
    assert 'Hello' in resp['messages'][0]['message']


def test_non_member_dm(setup):
    requests.post(f"{config.url}/dm/create/v1", json = {"token": user1['token'], "u_ids": [1]})
    requests.post(f"{config.url}/message/senddm/v1", json = {'token': user1['token'], 'dm_id': 0, 'message': 'Hello'})
    input = {
        'token': user3['token'], 
        'query_str': 'Hello'
    }
    resp = requests.get(f'{config.url}/search/v1', input)
    resp = resp.json()
    assert resp == {'messages': []}



def test_dm_bad_query(setup):
    requests.post(f"{config.url}/dm/create/v1", json = {"token": user1['token'], "u_ids": [1, 2]})
    requests.post(f"{config.url}/message/senddm/v1", json = {'token': user1['token'], 'dm_id': 0, 'message': 'Hello'})
    input = {
        'token': user2['token'], 
        'query_str': 'BADSTRINGNOTGOOD'
    }
    resp = requests.get(f'{config.url}/search/v1', input)
    resp = resp.json()
    assert resp == {'messages': []}

