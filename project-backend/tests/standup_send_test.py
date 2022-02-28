from src.error import InputError, AccessError
from src.create_token import decode_jwt
from src import config
import pytest 
import json
import requests 
import time

def test_standup_send():
    #clear all data
    requests.delete(f"{config.url}/clear/v1")
    #create new_users
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
    requests.delete(f"{config.url}/clear/v1")
    #create two new users
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
    requests.post(f"{config.url}/channel/join/v2", 
        json = {
            'token': user_data['token'],
            'channel_id': channel_id
        })
    #start standup function
    requests.post(f"{config.url}/standup/start/v1",
        json = {
            'token': user_owner_data['token'],
            'channel_id': channel_id,
            'length': 4
        })
    requests.post(f"{config.url}/standup/send/v1",
        json = {
            'token': user_data['token'],
            'channel_id': channel_id, 
            'message': "hello" 
        })
    requests.post(f"{config.url}/standup/send/v1",
        json = {
            'token': user_owner_data['token'],
            'channel_id': channel_id, 
            'message': "this course is" 
        })
    requests.post(f"{config.url}/standup/send/v1",
        json = {
            'token': user_data['token'],
            'channel_id': channel_id, 
            'message': "comp1531" 
        })
    channel_messages = requests.get(f"{config.url}/channel/messages/v2", 
        {
            'token': user_data['token'],
            'channel_id': channel_id,
            'start': 0
        }) 
    channel_messages_data = channel_messages.json()
    user_handle = decode_jwt(user_data['token'])['handle_str']
    user_owner_handle = decode_jwt(user_owner_data['token'])['handle_str']
    expected_string = \
        f"{user_handle}: hello\n{user_owner_handle}: this course is\n{user_handle}: comp1531\n"
    for dic in channel_messages_data['messages']:
        if dic['u_id'] == user_owner_data['auth_user_id']:
            time.sleep(7)
            assert dic['message'] == expected_string
    
    


def test_standup_send_channel_id_invalid():
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
    #start the standup function
    requests.post(f"{config.url}/standup/start/v1",
        json = {
            'token': user_data['token'],
            'channel_id': channel_id,
            'length': 2
        })
    standup_send = requests.post(f"{config.url}/standup/send/v1",
        json = {
            'token': user_data['token'],
            'channel_id': -42, #call a invalid channel id
            'message': "test message" 
        })
    #test if there is an input error
    response = standup_send.json()
    time.sleep(3)
    assert response['code'] == InputError.code
    

def test_standup_send_length_gt_1000():
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
    #start the standup function
    requests.post(f"{config.url}/standup/start/v1",
        json ={
            'token': user_data['token'],
            'channel_id': channel_id,
            'length': 2
        })
    #create a message greater that 1000 characters
    test_message = ""
    for i in range(1100):
        test_message += 'a'
        i = i
    #send the message greater than 1000 characters to the standup
    standup_send = requests.post(f"{config.url}/standup/send/v1",
        json = {
            'token': user_data['token'],
            'channel_id': channel_id,
            'message': test_message
        })
    #test if there is an input error
    response = standup_send.json()
    assert response['code'] == InputError.code
    time.sleep(3)

def test_standup_send_standup_not_running():
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
    #send when there is no standup
    standup_send = requests.post(f"{config.url}/standup/send/v1",
        json = {
            'token': user_data['token'],
            'channel_id': channel_id,
            'message': "test message" 
        })
    #test if there is an input error
    response = standup_send.json()
    assert response['code'] == InputError.code

def test_standup_send_user_not_member():
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
    requests.post(f"{config.url}/standup/start/v1",
        json = {
            'token': user_owner_data['token'],
            'channel_id': channel_id,
            'length': 2
        })
    #send a standup with the user who is not a member of the channel
    standup_send = requests.post(f"{config.url}/standup/send/v1",
        json = {
            'token': user_data['token'],
            'channel_id': channel_id,
            'message': "test message" 
        })
    #test if there is an input error
    response = standup_send.json()
    assert response['code'] == AccessError.code
    time.sleep(3)
