import pytest
import time
from src.users import users_stats_v1
from src.dm import dm_create_v1
from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.message import message_send_v1
from src.other import clear_v1
from src.error import InputError, AccessError

def test_users_stats_v1_num_channels():
    clear_v1()
    #create new user
    test_user = auth_register_v2(
        "test@gmail.com", "password", "name", "last")
    #create new channel
    channels_create_v2(
        test_user['token'], "test_channel", True)['channel_id']
    channels_create_v2(
        test_user['token'], "test2_channel", True)['channel_id']
    response = users_stats_v1(test_user['token'])['workspace_stats']
    assert response['channels_exist'][1]['num_channels_exist'] == 2
    assert response['utilization_rate'] == 1

def test_users_stats_v1_num_dms():
    clear_v1()
    #create new user
    user = auth_register_v2(
        "test@gmail.com", "password", "name", "last")
    user2 = auth_register_v2(
        "test2@gmail.com", "password2", "name2", "last2")
    token = user['token']
    user_2_u_id = user2['auth_user_id']
    #create new dm
    dm_create_v1(token, [user_2_u_id])
    response = users_stats_v1(user['token'])['workspace_stats']
    assert response['dms_exist'][1]['num_dms_exist'] == 1
    assert response['utilization_rate'] == 1

def test_users_stats_v1_num_messages():
    clear_v1()
    #create new user
    test_user = auth_register_v2(
        "test@gmail.com", "password", "name", "last")
    #create new channel
    channel_id = channels_create_v2(
        test_user['token'], "test2_channel", True)['channel_id']
    #send messages
    message_send_v1(test_user['token'], channel_id, "hello this is comp1531")
    response = users_stats_v1(test_user['token'])['workspace_stats']
    assert response['messages_exist'][1]['num_messages_exist'] == 1
    assert response['utilization_rate'] == 1

def test_users_stats_v1_utilization_rate():
    clear_v1()
    #create new users
    user = auth_register_v2(
        "test@gmail.com", "password", "name", "last")
    auth_register_v2(
        "test2@gmail.com", "password2", "name2", "last2")
    #create new channel
    channels_create_v2(
        user['token'], "test2_channel", True)['channel_id']
    response = users_stats_v1(user['token'])['workspace_stats']
    assert response['channels_exist'][1]['num_channels_exist'] == 1
    assert response['utilization_rate'] == 0.5