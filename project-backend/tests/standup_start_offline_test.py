import pytest
import time
from src.standup import standup_start_v1, standup_active_v1
from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.other import clear_v1
from src.error import InputError, AccessError

def test_standup_start():
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

def test_standup_start_channel_id_not_valid():
    clear_v1()
    #create new user
    test_user = auth_register_v2(
        "test@gmail.com", "password", "name", "last")
    #create a non valid channel
    channel_id = -42
    with pytest.raises(InputError):
        assert standup_start_v1(test_user['token'], channel_id, 2)
    time.sleep(2)

def test_standup_start_length_lt_0():
    clear_v1()
    #create new user
    test_user = auth_register_v2(
        "test@gmail.com", "password", "name", "last")
    #create new channel
    channel_id = channels_create_v2(
        test_user['token'], "test_channel", True)['channel_id']
    #call the standup function with a negative length
    with pytest.raises(InputError):
        assert standup_start_v1(test_user['token'], channel_id, -42)

def test_standup_start_already_running():
    clear_v1()
    #create new user
    test_user = auth_register_v2(
        "test@gmail.com", "password", "name", "last")
    #create new channel
    channel_id = channels_create_v2(
        test_user['token'], "test_channel", True)['channel_id']
    #call the standup function 
    standup_start_v1(test_user['token'], channel_id, 4)
    #call the standup function again
    with pytest.raises(InputError):
        assert standup_start_v1(test_user['token'], channel_id, 2)
    time.sleep(5)

def test_standup_user_not_member():
    clear_v1()
    #create two users
    test_owner = auth_register_v2(
        "test@gmail.com", "password", "name", "last")
    test_user = auth_register_v2(
        "test@gmail1.com", "password1", "name1", "last1")
    #create new channel
    channel_id = channels_create_v2(
        test_owner['token'], "test_channel", True)['channel_id']
    #call stand up with the user thats not a member of the channel
    with pytest.raises(AccessError):
        assert standup_start_v1(test_user['token'], channel_id, 2)
    time.sleep(2)
    