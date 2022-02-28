"""
These tests are for channel_leave_v1 function
History
1. Honggyo Suh implementd test cases for iteration 2 on 19th Oct 2021.
"""


import pytest
import src.channel
import src.channels
import src.auth
import src.error
import src.other


# This function clear & sets up the program for further tests.
@pytest.fixture(name="setup_data")
def setup_data():
    """cleans the datastore so there is no interference with the test."""
    src.other.clear_v1()

# Create 4 testers & create 1 channel.
    global tester1_id
    global tester1_token
    tester1 = src.auth.auth_register_v2(
        "tester1@gmail.com", "password", "tester1_first", "tester1_last")
    tester1_id = tester1['auth_user_id']
    tester1_token = tester1['token']
    global tester2_id
    global tester2_token
    tester2 = src.auth.auth_register_v2(
        "tester2@gmail.com", "password", "tester2_first", "tester2_last")
    tester2_id = tester2['auth_user_id']
    tester2_token = tester2['token']
    global tester3_id
    global tester3_token
    tester3 = src.auth.auth_register_v2(
        "tester3@gmail.com", "password", "tester3_first", "tester3_last")
    tester3_id = tester3['auth_user_id']
    tester3_token = tester3['token']
    global tester4_id
    global tester4_token
    tester4 = src.auth.auth_register_v2(
        "tester4@gmail.com", "password", "tester4_first", "tester4_last")
    tester4_id = tester4['auth_user_id']
    tester4_token = tester4['token']
    global test_channel
    test_channel = src.channels.channels_create_v2(tester1_token, "test_channel", True)
    test_channel = test_channel['channel_id']
    

def test_channel_leave(setup_data):
    """This function tests channel_leave_v1 in general."""
    
    src.channel.channel_invite_v2(tester1_token, test_channel, tester2_id)
    src.channel.channel_leave_v1(tester2_token, test_channel)
    
    details = src.channel.channel_details_v2(tester1_token, test_channel)
    num_of_members = len(details['all_members'])
    assert num_of_members == 1
    

def test_channel_leave_invalid_channel(setup_data):
    """This function tests whether channel_leave_v1 raises InputError with invalid channel_id."""
    
    with pytest.raises(src.error.InputError):
        src.channel.channel_leave_v1(tester1_token, 9)


def test_channel_leave_not_a_member(setup_data):
    """This function tests whether channel_leave_v1 raises AccessError with user_id not in channel."""
    
    with pytest.raises(src.error.AccessError):
        src.channel.channel_leave_v1(tester2_token, test_channel)
    
    
    
