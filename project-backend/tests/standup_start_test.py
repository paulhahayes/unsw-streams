from src.error import InputError, AccessError
from src import config
import pytest 
import json
import requests 
import time
from src.data_store import data_store
import pickle


def test_standup_start():
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
    #call the standup function 
    requests.post(f"{config.url}/standup/start/v1",
        json = {
            'token': user_data['token'],
            'channel_id': channel_id,
            'length': 2
        })
    #check if the standup is active using standup active
    standup_active = requests.get(f"{config.url}/standup/active/v1", 
        {
            'token': user_data['token'],
            'channel_id': channel_id
        })
    standup_active_response = standup_active.json()
    time.sleep(3)
    assert standup_active_response['is_active'] == True


def test_standup_start_channel_id_not_valid():
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
    #create a non valid channel
    channel_id = -42
    #call the standup function
    standup_start = requests.post(f"{config.url}/standup/start/v1",
        json = {
            'token': user_data['token'],
            'channel_id': channel_id,
            'length': 2
        })
    response = standup_start.json()
    #test if there is an input error
    time.sleep(3)
    assert response['code'] == InputError.code
    

def test_standup_start_length_lt_0():
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
    #call the standup function with a negative length
    standup_start = requests.post(f"{config.url}/standup/start/v1",
        json = {
            'token': user_data['token'],
            'channel_id': channel_id,
            'length': -42
        })
    response = standup_start.json()
    assert response['code'] == InputError.code 

def test_standup_start_already_running():
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
    #call the standup function 
    requests.post(f"{config.url}/standup/start/v1",
        json = {
            'token': user_data['token'],
            'channel_id': channel_id,
            'length': 4
        })
    #call the standup function again
    standup_second = requests.post(f"{config.url}/standup/start/v1",
        json = {
            'token': user_data['token'],
            'channel_id': channel_id,
            'length': 2
        })
    response = standup_second.json()
    time.sleep(5)
    assert response['code'] == InputError.code 
    

def test_standup_user_not_member():
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
        json = {
            'token': user_owner_data['token'],
            'name': 'test_channel',
            'is_public': True
        })
    channel_id = channel.json()['channel_id']
    #call stand up with the user thats not a member of the channel
    standup_start = requests.post(f"{config.url}/standup/start/v1",
        json = {
            'token': user_data['token'],
            'channel_id': channel_id,
            'length': 2
        })
    response = standup_start.json()
    time.sleep(3)
    assert response['code'] == AccessError.code
    


    
