from src.error import InputError, AccessError
import pytest
import json
import requests
from src import config







def create_messages(start, num_of_messages):
    message_list = []
    for i in range(num_of_messages):
        message = "test" + str(i + start)
        message_list.append(message)
    return message_list

def create_channel(num_of_messages, channel_name, token):
    # create a test channel
    channel = requests.post(f"{config.url}/channels/create/v2", 
        json = {
            'token': token,
            'name': channel_name,
            'is_public': True
        })
    channel_id = channel.json()['channel_id']
    # create a message list
    message_ids = []
    # add the messages to the test channel
    for i in range(num_of_messages):
        message = requests.post(f"{config.url}/message/send/v1", 
            json = {
                'token': token, 
                'channel_id': channel_id, 
                'message': "test" + str(i)
            })
        message_id = message.json()
        message_ids.append(message_id)

    return {'channel_id':channel_id, 'message_ids': message_ids}




def test_messages_removed_user_only():
    data =  {
        'email' : 'test@gmail.com',
        'name_first' : "name",
        'name_last' : 'last',
        'password' : 'password'
    }
    requests.delete(f"{config.url}/clear/v1")
    user = requests.post(f"{config.url}/auth/register/v2", json=data)
    user_data = user.json()
    #create channel with messages
    channel = requests.post(f"{config.url}/channels/create/v2", json= {
        'token' : user_data['token'],
        "name" : "Admins",
        "is_public" : True
    })
    channel = channel.json()
    channel_id = channel['channel_id']


    data2 =  {
        'email' : 'user2@gmail.com',
        'name_first' : "name",
        'name_last' : 'last',
        'password' : 'password'
    }
    user2 = requests.post(f"{config.url}/auth/register/v2", json=data2)
    user_data2 = user2.json()

    requests.post(f"{config.url}/channel/join/v2", json = {
        'token' : user_data2['token'],
        'channel_id' :  channel_id
    })
    requests.post(f"{config.url}/message/send/v1", json= {
        'token' : user_data2['token'],
        'channel_id' :  channel_id,
        'message' : "Please don't remove this"
    })
    requests.post(f"{config.url}/message/send/v1", json= {
        'token' : user_data['token'],
        'channel_id' :  channel_id,
        'message' : "No"
    })
    requests.delete(f"{config.url}/admin/user/remove/v1", json={
        'token': user_data['token'], 
        'u_id': 1
    })

    channel_messages = requests.get(f"{config.url}/channel/messages/v2", 
        {
            'token': user_data['token'],
            'channel_id': channel_id,
            'start': 0
        }) 
    test_data = channel_messages.json()
    print(test_data)
    assert test_data['messages'][1]['message'] == "No"

def test_chanel_messages_v2_start_10():
    data =  {
        'email' : 'test@gmail.com',
        'name_first' : "name",
        'name_last' : 'last',
        'password' : 'password'
    }
    requests.delete(f"{config.url}/clear/v1")
    user = requests.post(f"{config.url}/auth/register/v2", json=data)
    user_data = user.json()
    #create channel with messages
    channel = create_channel(80, "new_channel", user_data['token'])
    channel_id = channel['channel_id']
    #call channel_messages
    channel_messages = requests.get(f"{config.url}/channel/messages/v2", 
        {
            'token': user_data['token'],
            'channel_id': channel_id,
            'start': 10
        }) 
    test_data = channel_messages.json()
    test_data_messages = []
    for dic in test_data['messages']:
        test_data_messages.append(dic['message'])
    assert test_data['start'] == 10
    assert test_data['end'] == 60


def test_chanel_messages_v2_start_15():
    data =  {
        'email' : 'test@gmail.com',
        'name_first' : "name",
        'name_last' : 'last',
        'password' : 'password'
    }
    requests.delete(f"{config.url}/clear/v1")
    user = requests.post(f"{config.url}/auth/register/v2", json=data)
    user_data = user.json()
    #create channel with messages
    channel = create_channel(20, "new_channel", user_data['token'])
    channel_id = channel['channel_id']
    #call channel_messages
    channel_messages = requests.get(f"{config.url}/channel/messages/v2", 
        {
            'token': user_data['token'],
            'channel_id': channel_id,
            'start': 15
        }) 
    test_data = channel_messages.json()
    test_data_messages = []
    for dic in test_data['messages']:
        test_data_messages.append(dic['message'])
    assert test_data['start'] == 15
    assert test_data['end'] == -1
    assert test_data_messages == create_messages(15, 5)

def test_chanel_messages_v2_start_0():
    data =  {
        'email' : 'test@gmail.com',
        'name_first' : "name",
        'name_last' : 'last',
        'password' : 'password'
    }
    requests.delete(f"{config.url}/clear/v1")
    user = requests.post(f"{config.url}/auth/register/v2", json=data)
    user_data = user.json()
    #create channel with messages
    channel = create_channel(80, "new_channel", user_data['token'])
    channel_id = channel['channel_id']
    #call channel_messages
    channel_messages = requests.get(f"{config.url}/channel/messages/v2", 
        {
            'token': user_data['token'],
            'channel_id': channel_id,
            'start': 0
        }) 
    test_data = channel_messages.json()
    test_data_messages = []
    for dic in test_data['messages']:
        test_data_messages.append(dic['message'])
    assert test_data['start'] == 0
    assert test_data['end'] == 50


def test_channel_messages_v1_invalid_channel_id():
    data =  {
        'email' : 'test@gmail.com',
        'name_first' : "name",
        'name_last' : 'last',
        'password' : 'password'
    }
    requests.delete(f"{config.url}/clear/v1")
    user = requests.post(f"{config.url}/auth/register/v2", json=data)
    user_data = user.json()
    channel_messages = requests.get(f"{config.url}/channel/messages/v2", 
        {
            'token': user_data['token'],
            'channel_id': -42,
            'start': 10
        }) 
    response = channel_messages.json()
    assert response['code'] == InputError.code

def test_channel_messages_v2_not_member():
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
    channel = create_channel(80, "new_channel", user_owner_data['token'])
    channel_id = channel['channel_id']
    channel_messages = requests.get(f"{config.url}/channel/messages/v2", 
        {
            'token': user_data['token'],
            'channel_id': channel_id,
            'start': 0
        }) 
    response = channel_messages.json()
    assert response['code'] == AccessError.code


