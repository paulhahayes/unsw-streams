from src.error import InputError, AccessError
import pytest
import json
import requests
from src import config


def is_in_owner(u_id, channel_id, token):
    channel = requests.get(f"{config.url}/channel/details/v2",
                           {"token": token,
                                 'channel_id': channel_id})
    channel = channel.json()
    for index in range(len(channel['owner_members'])):
        if u_id == channel['owner_members'][index]['u_id']:
            return True
    return False


def test_channel_addowner_v1_owner_added():
    data1 = {
        'email': 'test@gmail.com',
        'name_first': "name",
        'name_last': 'last',
        'password': 'password'
    }
    data2 = {
        'email': 'test2@gmail.com',
        'name_first': 'name2',
        'name_last': 'last2',
        'password': 'password2'
    }
    requests.delete(f"{config.url}/clear/v1")
    # create two new users
    user_owner = requests.post(f"{config.url}/auth/register/v2", json=data1)
    user_owner_data = user_owner.json()
    user = requests.post(f"{config.url}/auth/register/v2", json=data2)
    user_data = user.json()
    # create new channel
    channel = requests.post(f"{config.url}/channels/create/v2",
                            json={
                                'token': user_owner_data['token'],
                                'name': "new_channel",
                                'is_public': True
                            })
    channel_id = channel.json()['channel_id']
    # let the user be a member of the channel
    requests.post(f"{config.url}/channel/join/v2",
                  json={'token': user_data['token'], 'channel_id': channel_id})
    requests.post(f"{config.url}/channel/addowner/v1",
                  json={
                      'token': user_owner_data['token'],
                      'channel_id': channel_id,
                      'u_id': user_data['auth_user_id']
                  })
    assert is_in_owner(user_data['auth_user_id'],
                       channel_id, user_data['token'])


def test_channel_addowner_v1_invalid_channel_id():
    data1 = {
        'email': 'test@gmail.com',
        'name_first': "name",
        'name_last': 'last',
        'password': 'password'
    }
    requests.delete(f"{config.url}/clear/v1")
    # create new user
    user = requests.post(f"{config.url}/auth/register/v2", json=data1)
    user_data = user.json()
    channel_id = 42
    add_owner = requests.post(f"{config.url}/channel/addowner/v1",
                              json={
                                  'token': user_data['token'],
                                  'channel_id': channel_id,
                                  'u_id': user_data['auth_user_id']
                              })
    add_owner_response = add_owner.json()
    assert add_owner_response['code'] == InputError.code


def test_channel_addowner_v1_invalid_u_id():
    data1 = {
        'email': 'test@gmail.com',
        'name_first': "name",
        'name_last': 'last',
        'password': 'password'
    }
    requests.delete(f"{config.url}/clear/v1")
    # create new user
    test_user = 42
    user_owner = requests.post(f"{config.url}/auth/register/v2", json=data1)
    user_owner_data = user_owner.json()
    # create channel
    channel = requests.post(f"{config.url}/channels/create/v2",
                            json={
                                'token': user_owner_data['token'],
                                'name': "new_channel",
                                'is_public': True
                            })
    channel_id = channel.json()['channel_id']
    add_owner = requests.post(f"{config.url}/channel/addowner/v1",
                              json={
                                  'token': user_owner_data['token'],
                                  'channel_id': channel_id,
                                  'u_id': test_user
                              })
    add_owner_response = add_owner.json()
    assert add_owner_response['code'] == InputError.code


def test_channel_addowner_v1_not_a_member():
    data1 = {
        'email': 'test@gmail.com',
        'name_first': "name",
        'name_last': 'last',
        'password': 'password'
    }
    data2 = {
        'email': 'test2@gmail.com',
        'name_first': 'name2',
        'name_last': 'last2',
        'password': 'password2'
    }
    requests.delete(f"{config.url}/clear/v1")
    # create two new users
    user_owner = requests.post(f"{config.url}/auth/register/v2", json=data1)
    user_owner_data = user_owner.json()
    user = requests.post(f"{config.url}/auth/register/v2", json=data2)
    user_data = user.json()
    # create channel
    channel = requests.post(f"{config.url}/channels/create/v2",
                            json={
                                'token': user_owner_data['token'],
                                'name': "new_channel",
                                'is_public': True
                            })
    channel_id = channel.json()['channel_id']
    add_owner = requests.post(f"{config.url}/channel/addowner/v1",
                              json={
                                  'token': user_owner_data['token'],
                                  'channel_id': channel_id,
                                  'u_id': user_data['auth_user_id']
                              })
    add_owner_response = add_owner.json()
    assert add_owner_response['code'] == InputError.code


def test_channel_addowner_v1_already_owner():
    data1 = {
        'email': 'test@gmail.com',
        'name_first': "name",
        'name_last': 'last',
        'password': 'password'
    }
    requests.delete(f"{config.url}/clear/v1")
    # create new user
    user_owner = requests.post(f"{config.url}/auth/register/v2", json=data1)
    user_owner_data = user_owner.json()
    channel = requests.post(f"{config.url}/channels/create/v2",
                            json={
                                'token': user_owner_data['token'],
                                'name': "new_channel",
                                'is_public': True
                            })
    channel_id = channel.json()['channel_id']
    add_owner = requests.post(f"{config.url}/channel/addowner/v1",
                              json={
                                  'token': user_owner_data['token'],
                                  'channel_id': channel_id,
                                  'u_id': user_owner_data['auth_user_id']
                              })
    add_owner_response = add_owner.json()
    assert add_owner_response['code'] == InputError.code


def test_channel_addowner_v1_accesserror():
    data1 = {
        'email': 'test@gmail.com',
        'name_first': "name",
        'name_last': 'last',
        'password': 'password'
    }
    data2 = {
        'email': 'test2@gmail.com',
        'name_first': 'name2',
        'name_last': 'last2',
        'password': 'password2'
    }
    data3 = {
        'email': 'test3@gmail.com',
        'name_first': 'name3',
        'name_last': 'last3',
        'password': 'password3'
    }
    requests.delete(f"{config.url}/clear/v1")
    # create three new users
    user_owner = requests.post(f"{config.url}/auth/register/v2", json=data1)
    user_owner_data = user_owner.json()
    user = requests.post(f"{config.url}/auth/register/v2", json=data2)
    user_data = user.json()
    user2 = requests.post(f"{config.url}/auth/register/v2", json=data3)
    user2_data = user2.json()
    # create channel
    channel = requests.post(f"{config.url}/channels/create/v2",
                            json={
                                'token': user_owner_data['token'],
                                'name': "new_channel",
                                'is_public': True
                            })
    channel_id = channel.json()['channel_id']
    requests.post(f"{config.url}/channel/join/v2",
                  json={'token': user2_data['token'], 'channel_id': channel_id})
    is_in_owner(user2_data['auth_user_id'], channel_id, user2_data['token'])

    add_owner = requests.post(f"{config.url}/channel/addowner/v1",
                              json={
                                  'token': user_data['token'],
                                  'channel_id': channel_id,
                                  'u_id': user2_data['auth_user_id']
                              })
    add_owner_response = add_owner.json()
    assert add_owner_response['code'] == AccessError.code
