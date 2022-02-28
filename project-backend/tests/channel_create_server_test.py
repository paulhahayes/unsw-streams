from src.error import InputError
import pytest
import json
import requests
from src import config
from src.channels import channels_create_v2
from src.auth import auth_register_v2


def test_channels_create_v2_new_public_channel():
    data = {
        'email': 'test@gmail.com',
        'name_first': "name",
        'name_last': 'last',
        'password': 'password'
    }
    requests.delete(f"{config.url}/clear/v1")
    user = requests.post(f"{config.url}/auth/register/v2", json=data)
    user_data = user.json()
    new_channel = requests.post(f"{config.url}/channels/create/v2",
                                json={"token": user_data['token'], "name": "new_channel", "is_public": True})
    new_channel_data = new_channel.json()
    all_channels = requests.get(
        f"{config.url}/channels/listall/v2", {"token": user_data['token']})
    all_channels_data = all_channels.json()

    expected_output = {
        'channel_id': new_channel_data['channel_id'],
        'name': "new_channel",
    }
    print(all_channels_data)
    assert expected_output in all_channels_data['channels']


def test_channels_create_v2_new_private_channel():
    data = {
        'email': 'test@gmail.com',
        'name_first': "name",
        'name_last': 'last',
        'password': 'password'
    }
    requests.delete(f"{config.url}/clear/v1")
    user = requests.post(f"{config.url}/auth/register/v2", json=data)
    user_data = user.json()
    new_channel = requests.post(f"{config.url}/channels/create/v2",
                                json={"token": user_data['token'], "name": "new_channel", "is_public": False})
    new_channel_data = new_channel.json()
    all_channels = requests.get(
        f"{config.url}/channels/listall/v2", {"token": user_data['token']})
    all_channels_data = all_channels.json()
    expected_output = {
        'channel_id': new_channel_data['channel_id'],
        'name': "new_channel",
    }
    assert expected_output in all_channels_data['channels']


def test_channels_create_v2_name_mt_20_chars():
    data = {
        'email': 'test@gmail.com',
        'name_first': "name",
        'name_last': 'last',
        'password': 'password'
    }
    requests.delete(f"{config.url}/clear/v1")
    user = requests.post(f"{config.url}/auth/register/v2", json=data)
    user_data = user.json()
    new_channel = requests.post(f"{config.url}/channels/create/v2",
                                json={
                                    "token": user_data['token'],
                                    "name": "TheChannelNameIsMoreThan20CharactersLong",
                                    "is_public": True
                                })
    new_channel_data = new_channel.json()
    assert new_channel_data['code'] == InputError.code


def test_channels_create_v2_name_lt_1_chars():
    data = {
        'email': 'test@gmail.com',
        'name_first': "name",
        'name_last': 'last',
        'password': 'password'
    }
    requests.delete(f"{config.url}/clear/v1")
    user = requests.post(f"{config.url}/auth/register/v2", json=data)
    user_data = user.json()
    new_channel = requests.post(f"{config.url}/channels/create/v2",
                                json={"token": user_data['token'], "name": "", "is_public": False})
    new_channel_data = new_channel.json()
    assert new_channel_data['code'] == InputError.code
