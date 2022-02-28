"""
Tests for the clear function used to reset when testing other functions
"""


import pytest
import requests
import json
from src import config
from src.other import clear_v1
from src.channel import channel_join_v2
from src.error import InputError
from src.auth import auth_register_v2
from src.auth import auth_login_v2
from src.channels import channels_create_v2



def test_clear_user():
    """
    check user list will be cleared
    """

    data =  {
        'email' : 'hqw@gmailw.com',
        'name_first' : "hansol11",
        'name_last' : 'raspberry',
        'password' : 'password'
    }
    
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/login/v2", json=data)
    data = user1.json()
    
    assert(data['code'] == 400)


# check channel list will be cleared


def test_clear_channel():
    """
    check channel list will be cleared
    """
    data =  {
        'email' : 'hqw@gmailw.com',
        'name_first' : "hansol11",
        'name_last' : 'raspberry',
        'password' : 'password'
    }
    
    requests.delete(f"{config.url}/clear/v1")
    user0 = requests.post(f"{config.url}/auth/register/v2", json=data)
    data0 = user0.json()
    ch_id = requests.post(f"{config.url}/channels/create/v2", json={'token': data0['token'], 'name': 'ch1', 'is_public': True})
    ch_id = ch_id.json()
    requests.delete(f"{config.url}/clear/v1")

    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    data1 = user1.json()

    new_ch = requests.post(f"{config.url}/channels/create/v2", json={'token': data1['token'], 'name': 'ch1', 'is_public': True})
    new_ch = new_ch.json()
    assert(ch_id == new_ch)

