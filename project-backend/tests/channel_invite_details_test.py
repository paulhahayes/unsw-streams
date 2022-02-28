"""
These tests are for channel_invite_v2 function and channel details
History
1. Honggyo Suh implemented test cases & setup function on 28th Sep 2021.
2. Honggyo Suh revised test cases & added count_members function on 30th Sep 2021.
3. Honggyo Suh revised test cases for iteration 2 on 17th Oct 2021.
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
    test_channel = src.channels.channels_create_v2(
        tester1_token, "test_channel", True)
    test_channel = test_channel['channel_id']


def test_channel_invite(setup_data):  # pylint: disable=unused-argument
    """This function tests the function channel_invite_v2 is working properly by checking
        the member of channel."""

    details = src.channel.channel_details_v2(tester1_token, test_channel)
    num_of_members = len(details['all_members'])
    assert num_of_members == 1

    src.channel.channel_invite_v2(tester1_token, test_channel, tester2_id)
    details = src.channel.channel_details_v2(tester1_token, test_channel)
    num_of_members = len(details['all_members'])
    assert num_of_members == 2

    src.channel.channel_invite_v2(tester1_token, test_channel, tester3_id)
    details = src.channel.channel_details_v2(tester1_token, test_channel)
    num_of_members = len(details['all_members'])
    assert num_of_members == 3

    src.channel.channel_invite_v2(tester1_token, test_channel, tester4_id)
    details = src.channel.channel_details_v2(tester1_token, test_channel)
    num_of_members = len(details['all_members'])
    assert num_of_members == 4


def test_channel_already_invited(setup_data):  # pylint: disable=unused-argument:
    """This function tests how the function works when we are trying to invite themselves
        or the person who is already in the channel."""

    with pytest.raises(src.error.InputError):
        src.channel.channel_invite_v2(tester1_token, test_channel, tester1_id)

    src.channel.channel_invite_v2(tester1_token, test_channel, tester2_id)
    details = src.channel.channel_details_v2(tester1_token, test_channel)
    num_of_members = len(details['all_members'])
    assert num_of_members == 2

    with pytest.raises(src.error.InputError):
        src.channel.channel_invite_v2(tester1_token, test_channel, tester2_id)


def test_channel_invite_wrong_channel_id(setup_data):  # pylint: disable=unused-argument
    """This function tests whether the function raises InputError
        when we enter the wrongchannel ID."""

    with pytest.raises(src.error.InputError):
        src.channel.channel_invite_v2(tester1_token, 9, tester1_id)


def test_channel_invite_wrong_user_id(setup_data):  # pylint: disable=unused-argument
    """This function tests whether the function raises InputError when we enter the wrong
        user ID."""

    with pytest.raises(src.error.InputError):
        src.channel.channel_invite_v2(tester1_token, test_channel, 9)


def test_channel_invite_not_authorised(setup_data):  # pylint: disable=unused-argument
    """This function tests whether the function raises AccessError when the person
        who is not in the channel tries to invite others."""

    with pytest.raises(src.error.AccessError):
        src.channel.channel_invite_v2(tester2_token, test_channel, tester3_id)


def test_channel_details_not_authorised(setup_data):  # pylint: disable=unused-argument
    """This function tests whether the function raises AccessError when the person
        who is not in the channel tries to get details."""

    with pytest.raises(src.error.AccessError):
        src.channel.channel_details_v2(tester2_token, test_channel)


def test_channel_details_wrong_channel_id(setup_data):  # pylint: disable=unused-argument
    """This function tests whether the function raises InputError when we enter the wrong
    user ID."""

    with pytest.raises(src.error.InputError):
        src.channel.channel_details_v2(tester1_token, 9)


def test_channel_detail(setup_data):  # pylint: disable=unused-argument
    """This function tests the function channel_details_v2 is working properly by
    checking the member of channel."""

    details = src.channel.channel_details_v2(tester1_token, test_channel)
    print(details)
    assert details['name'] == 'test_channel'
    assert details['is_public'] == True
    assert details['owner_members'][0]['u_id'] == tester1_id
    assert details['all_members'][0]['u_id'] == tester1_id

