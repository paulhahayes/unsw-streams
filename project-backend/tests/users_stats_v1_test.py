from src.error import InputError, AccessError
from src import config
import pytest 
import json
import requests 
import time
from src.data_store import data_store
import pickle

def test_users_stats_v1_num_channels():
    requests.delete(f"{config.url}/clear/v1")
    #create new user
    data =  {
        'email' : 'test@gmail.com',
        'name_first' : "name",
        'name_last' : 'last',
        'password' : 'password'
    }
    user = requests.post(f"{config.url}/auth/register/v2", json=data)
    user_token = user.json()['token']
    #create new channel
    requests.post(f"{config.url}/channels/create/v2", 
        json = {
            'token': user_token,
            'name': 'test_channel',
            'is_public': True
        })
    requests.post(f"{config.url}/channels/create/v2", 
        json = {
            'token': user_token,
            'name': 'test2_channel',
            'is_public': True
        })
    users_stats = requests.get(f"{config.url}/users/stats/v1", {'token':user_token})
    response = users_stats.json()['workspace_stats']
    assert response['channels_exist'][1]['num_channels_exist'] == 2
    assert response['utilization_rate'] == 1

def test_users_stats_v1_num_dms():
    requests.delete(f"{config.url}/clear/v1")
    #create new user
    data =  {
        'email' : 'test@gmail.com',
        'name_first' : "name",
        'name_last' : 'last',
        'password' : 'password'
    }
    data2 =  {
        'email' : 'test2@gmail.com',
        'name_first' : "name2",
        'name_last' : 'last2',
        'password' : 'password2'
    }
    user = requests.post(f"{config.url}/auth/register/v2", json=data)
    user2 = requests.post(f"{config.url}/auth/register/v2", json=data2)
    token = user.json()['token']
    user_2_u_id = user2.json()['auth_user_id']
    #create new dm
    requests.post(f"{config.url}/dm/create/v1", 
        json = {
            'token': token,
            'u_ids': [user_2_u_id]
        })
    users_stats = requests.get(f"{config.url}/users/stats/v1", {'token':token})
    response = users_stats.json()['workspace_stats']
    assert response['dms_exist'][1]['num_dms_exist'] == 1
    assert response['utilization_rate'] == 1

def test_users_stats_v1_num_messages():
    requests.delete(f"{config.url}/clear/v1")
    #create new user
    data =  {
        'email' : 'test@gmail.com',
        'name_first' : "name",
        'name_last' : 'last',
        'password' : 'password'
    }
    user = requests.post(f"{config.url}/auth/register/v2", json=data)
    user_token = user.json()['token']
    #create new channel
    channel = requests.post(f"{config.url}/channels/create/v2", 
        json = {
            'token': user_token,
            'name': 'test_channel',
            'is_public': True
        })
    channel_id = channel.json()['channel_id']
    #send messages
    requests.post(f"{config.url}/message/send/v1", 
        json= {
            'token': user_token,
            'channel_id': channel_id,
            'message': "hello this is comp1531"
        })
    users_stats = requests.get(f"{config.url}/users/stats/v1", {'token':user_token})
    response = users_stats.json()['workspace_stats']
    assert response['messages_exist'][1]['num_messages_exist'] == 1
    assert response['utilization_rate'] == 1

def test_users_stats_v1_utilization_rate():
    requests.delete(f"{config.url}/clear/v1")
    #create new users
    data =  {
        'email' : 'test@gmail.com',
        'name_first' : "name",
        'name_last' : 'last',
        'password' : 'password'
    }
    data2 =  {
        'email' : 'test2@gmail.com',
        'name_first' : "name2",
        'name_last' : 'last2',
        'password' : 'password2'
    }
    user = requests.post(f"{config.url}/auth/register/v2", json=data)
    requests.post(f"{config.url}/auth/register/v2", json=data2)
    user_token = user.json()['token']
    #create new channel
    channel = requests.post(f"{config.url}/channels/create/v2", 
        json = {
            'token': user_token,
            'name': 'test_channel',
            'is_public': True
        })
    channel.json()['channel_id']
    users_stats = requests.get(f"{config.url}/users/stats/v1", {'token':user_token})
    response = users_stats.json()['workspace_stats']
    assert response['channels_exist'][1]['num_channels_exist'] == 1
    assert response['utilization_rate'] == 0.5