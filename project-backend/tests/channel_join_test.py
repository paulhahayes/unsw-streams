"""
Tests for the join channel function
History
1. Honggyo Suh revised test cases for iteration 2 on 17th Oct 2021.
"""

import pytest
import src.channel
from src.error import InputError
from src.error import AccessError
from src.auth import auth_register_v2
from src.channels import channels_create_v2
from src.other import clear_v1
from src.channels import channels_listall_v2, channels_list_v2


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
    global test_channel1
    test_channel1 = src.channels.channels_create_v2(
        tester1_token, "test_channel", True)
    test_channel1 = test_channel1['channel_id']


def test_channel_join(setup_data):
    """Tests the channel_join_v2 function works in general."""

    test_channel2 = src.channels.channels_create_v2(
        tester1_token, "test_channel2", True)
    test_channel2 = test_channel2['channel_id']
    src.channel.channel_join_v2(tester2_token, test_channel2)
    assert len(src.channel.channel_details_v2(
        tester2_token, test_channel2)['all_members']) == 2

    # channel_id does not refer to a valid channel


def test_wrong_channel_id(setup_data):
    """Tests a wrong channel given"""

    with pytest.raises(InputError):
        src.channel.channel_join_v2(tester1_token, 9999)


def test_already_member(setup_data):
    """the authorised user is already a member of the channel"""

    with pytest.raises(InputError):
        src.channel.channel_join_v2(tester1_token, test_channel1)


def test_not_permitted(setup_data):
    """channel_id refers to a channel that is
        private and the authorised user is not a global owner"""

    # user2 doesn't have global permission, therefore user2 won't join
    test_channel2 = src.channels.channels_create_v2(
        tester1_token, "test_channel2", False)
    test_channel2 = test_channel2['channel_id']

    with pytest.raises(AccessError):
        src.channel.channel_join_v2(tester4_token, test_channel2)
