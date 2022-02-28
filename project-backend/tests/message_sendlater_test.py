"""
These tests are for message_sendlater
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
import datetime
from datetime import timedelta

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


def test_message_sendlater_in_general(setup):
    later = datetime.datetime.now() + timedelta(seconds=2)
    later = later.timestamp()
    input = {
        'token': user1['token'], 
        'channel_id': test_channel['channel_id'],
        'message': 'see u later',
        'time_sent': later
    }
    result = requests.post(f'{BASE_URL}/message/sendlater/v1', json=input)

    assert str(result) == '<Response [200]>'


def test_message_sendlater_invalid_channel(setup):

    input = {
        'token': user1['token'], 
        'channel_id': -1,
        'message': 'see u later',
        'time_sent': 5
    }
    result = requests.post(f'{BASE_URL}/message/sendlater/v1', json=input)
    result = json.loads(result.text)
    assert result['code'] == 400


def test_message_sendlater_too_long(setup):
    
    input = {
        'token': user1['token'], 
        'channel_id': test_channel['channel_id'],
        'message': 'see u later'*1000,
        'time_sent': 5
    }
    result = requests.post(f'{BASE_URL}/message/sendlater/v1', json=input)
    result = json.loads(result.text)
    assert result['code'] == 400


def test_message_sendlater_invalid_time(setup):

    input = {
        'token': user1['token'], 
        'channel_id': test_channel['channel_id'],
        'message': 'see u later',
        'time_sent': -20
    }
    result = requests.post(f'{BASE_URL}/message/sendlater/v1', json=input)
    result = json.loads(result.text)
    assert result['code'] == 400


def test_message_sendlater_not_authorized(setup):

    input = {
        'token': user3['token'], 
        'channel_id': test_channel['channel_id'],
        'message': 'see u later'*1000,
        'time_sent': 5
    }
    result = requests.post(f'{BASE_URL}/message/sendlater/v1', json=input)
    result = json.loads(result.text)
    assert result['code'] == 400
