from src.error import InputError, AccessError
from src import config
import pytest 
import json
import requests 
import pickle
import time
from src.data_store import data_store


def test_standup_active_active():
    data = {
        'email': 'test@gmail.com',
        'name_first': "name",
        'name_last': 'last',
        'password': 'password'
    }
    requests.delete(f"{config.url}/clear/v1")
    user = requests.post(f"{config.url}/auth/register/v2", json=data)
    user_data = user.json()
    #create new channel
    channel = requests.post(f"{config.url}/channels/create/v2",
                            json={
                                'token': user_data['token'],
                                'name': "new_channel",
                                'is_public': True
                            })
    channel_id = channel.json()['channel_id']
    token = {'token': user_data['token']}
    list1 = requests.get(f'{config.url}/channels/list/v2', token)
    list1 = list1.json()
    #call the standup function 
    requests.post(f"{config.url}/standup/start/v1",
        json = {
            'token': user_data['token'],
            'channel_id': channel_id,
            'length': 5
        })
    #check if the standup is active using standup active
    standup_active = requests.get(f"{config.url}/standup/active/v1", 
        {
            'token': user_data['token'],
            'channel_id': channel_id
        })
    standup_active_response = standup_active.json()
    assert standup_active_response['is_active'] == True
    time.sleep(6)

def test_standup_active_inactive():
    requests.delete(f"{config.url}/clear/v1")
    #create new user
    data =  {
        'email' : 'test@gmail.com',
        'name_first' : "name",
        'name_last' : 'last',
        'password' : 'password'
    }
    user = requests.post(f"{config.url}/auth/register/v2", json=data)
    user_data = user.json()
    #create new channel
    channel = requests.post(f"{config.url}/channels/create/v2", 
        json = {
            'token': user_data['token'],
            'name': 'test_channel',
            'is_public': True
        })
    channel_id = channel.json()['channel_id']
    #check if the standup is inactive using standup active
    standup_active = requests.get(f"{config.url}/standup/active/v1", 
        {
            'token': user_data['token'],
            'channel_id': channel_id
        })
    standup_active_response = standup_active.json()
    assert standup_active_response['is_active'] == False

def test_standup_active_channel_id_invalid():
    requests.delete(f"{config.url}/clear/v1")
    #create new user
    data =  {
        'email' : 'test@gmail.com',
        'name_first' : "name",
        'name_last' : 'last',
        'password' : 'password'
    }
    user = requests.post(f"{config.url}/auth/register/v2", json=data)
    user_data = user.json()
    #create invalid channel
    channel_id = -42
    #call standup_active
    standup_active = requests.get(f"{config.url}/standup/active/v1", 
        {
            'token': user_data['token'],
            'channel_id': channel_id
        })
    standup_active_response = standup_active.json()
    #standup active should respond with an input error as the 
    #channel_id is invalid
    assert standup_active_response['code'] == InputError.code

def test_standup_active_user_not_member():
    requests.delete(f"{config.url}/clear/v1")
    #create two users
    data1 =  {
        'email' : 'test@gmail.com',
        'name_first' : "name",
        'name_last' : 'last',
        'password' : 'password'
    }
    data2 = {
        'email': 'test2@gmail.com',
        'name_first': 'name2',
        'name_last': 'last2',
        'password': 'password2'
    }
    user_owner = requests.post(f"{config.url}/auth/register/v2", json=data1)
    user_owner_data = user_owner.json()
    user = requests.post(f"{config.url}/auth/register/v2", json=data2)
    user_data = user.json()
    #create new channel
    channel = requests.post(f"{config.url}/channels/create/v2",
                            json={
                                'token': user_owner_data['token'],
                                'name': "new_channel",
                                'is_public': True
                            })
    channel_id = channel.json()['channel_id']
    standup_active = requests.get(f"{config.url}/standup/active/v1", 
        {
            'token': user_data['token'],
            'channel_id': channel_id
        })
    standup_active_response = json.loads(standup_active.text)
    assert standup_active_response['code'] == AccessError.code

def test_standup_inactive_after_active():
    data = {
        'email': 'test@gmail.com',
        'name_first': "name",
        'name_last': 'last',
        'password': 'password'
    }
    requests.delete(f"{config.url}/clear/v1")
    user = requests.post(f"{config.url}/auth/register/v2", json=data)
    user_data = user.json()
    #create new channel
    channel = requests.post(f"{config.url}/channels/create/v2",
                            json={
                                'token': user_data['token'],
                                'name': "new_channel",
                                'is_public': True
                            })
    channel_id = channel.json()['channel_id']
    token = {'token': user_data['token']}
    list1 = requests.get(f'{config.url}/channels/list/v2', token)
    list1 = list1.json()
    #call the standup function 
    requests.post(f"{config.url}/standup/start/v1",
        json = {
            'token': user_data['token'],
            'channel_id': channel_id,
            'length': 5
        })
    time.sleep(6)
    #check if the standup is active using standup active
    standup_active = requests.get(f"{config.url}/standup/active/v1", 
        {
            'token': user_data['token'],
            'channel_id': channel_id
        })
    standup_active_response = standup_active.json()
    assert standup_active_response['is_active'] == False

