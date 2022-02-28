import pytest
import time
from src.standup import standup_start_v1, standup_active_v1
from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.other import clear_v1
from src.error import InputError, AccessError

def test_standup_active_active():
    clear_v1()
    #create new user
    test_user = auth_register_v2(
        "test@gmail.com", "password", "name", "last")
    #create new channel
    channel_id = channels_create_v2(
        test_user['token'], "test_channel", True)['channel_id']
    #call the standup function 
    standup_start_v1(test_user['token'], channel_id, 2)
    #check if the standup is active using standup active
    assert standup_active_v1(test_user['token'], channel_id)['is_active']
    time.sleep(2)

def test_standup_active_inactive():
    clear_v1()
    #create new user
    test_user = auth_register_v2(
        "test@gmail.com", "password", "name", "last")
    #create new channel
    channel_id = channels_create_v2(
        test_user['token'], "test_channel", True)['channel_id']
    #check if the standup is inactive using standup active
    assert not standup_active_v1(test_user['token'], channel_id)['is_active']

def test_standup_active_channel_id_invalid():
    clear_v1()
    #create new user
    test_user = auth_register_v2(
        "test@gmail.com", "password", "name", "last")
    #create invalid channel
    channel_id = -42
    #call standup_active
    with pytest.raises(InputError):
        assert standup_active_v1(test_user['token'], channel_id)

def test_standup_active_user_not_member():
    clear_v1()
    #create two users
    test_owner = auth_register_v2(
        "test@gmail.com", "password", "name", "last")
    test_user = auth_register_v2(
        "test@gmail1.com", "password1", "name1", "last1")
    #create new channel
    channel_id = channels_create_v2(
        test_owner['token'], "test_channel", True)['channel_id']
    with pytest.raises(AccessError):
        assert standup_active_v1(test_user['token'], channel_id)

def test_standup_inactive_after_active():
    clear_v1()
    #create new user
    test_user = auth_register_v2(
        "test@gmail.com", "password", "name", "last")
    #create new channel
    channel_id = channels_create_v2(
        test_user['token'], "test_channel", True)['channel_id']
    #call the standup function 
    standup_start_v1(test_user['token'], channel_id, 2)
    #check if the standup is active using standup active
    time.sleep(3)
    assert not standup_active_v1(test_user['token'], channel_id)['is_active']
    