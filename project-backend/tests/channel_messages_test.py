import pytest

from src.channel import channel_messages_v2
from src.channels import channels_create_v2
from src.message import message_send_v1
from src.auth import auth_register_v2
from src.data_store import data_store
from src.error import InputError
from src.error import AccessError
from src.other import clear_v1

# function that creates a list of messages


def create_messages(start, num_of_messages):
    message_list = []
    for i in range(num_of_messages):
        message = "test" + str(i + start)
        message_list.append(message)
    return message_list

# debugging function that shows a list of ints instead
# of dictionaries


def show_list(start, num_of_messages):
    test_list = []
    for i in range(num_of_messages):
        test_list.append(i + start)
    print(test_list)


# creates a new channel with a certain number of messages


def create_channel(num_of_messages, channel_name, token):
    # create a test channel
    channel_id = channels_create_v2(token, channel_name, True)['channel_id']
    # add the messages to the test channel
    for i in range(num_of_messages):
        message_send_v1(token, channel_id, "test" + str(i))
    return channel_id

# normal test cases


def test_channel_messages_v2_start_10():
    clear_v1()
    new_user = auth_register_v2("testemail@gmail.com",
                            "password", "name", "lastname")
    # create channel with messages
    test_channel = create_channel(80, "test_channel1", new_user['token'])
    # call channel_messages
    test_data = channel_messages_v2(new_user['token'], test_channel, 10)
    test_data_messages = []
    for dic in test_data['messages']:
        test_data_messages.append(dic['message'])
    assert test_data['start'] == 10
    assert test_data['end'] == 60
    assert test_data_messages == create_messages(10, 50)


def test_channel_messages_v2_start_15():
    clear_v1()
    new_user = auth_register_v2("testemail@gmail.com",
                            "password", "name", "lastname")
    # create channel with messages
    test_channel = create_channel(20, "test_channel1", new_user['token'])
    # call channel_messages
    test_data = channel_messages_v2(new_user['token'], test_channel, 15)
    test_data_messages = []
    for dic in test_data['messages']:
        test_data_messages.append(dic['message'])
    assert test_data['start'] == 15
    assert test_data['end'] == -1
    assert test_data_messages == create_messages(15, 5)


def test_channel_messages_v2_start_0():
    clear_v1()
    new_user = auth_register_v2("testemail@gmail.com",
                            "password", "name", "lastname")
    # create channel with messages
    test_channel = create_channel(80, "test_channel1", new_user['token'])
    # call channel_messages
    test_data = channel_messages_v2(new_user['token'], test_channel, 0)
    test_data_messages = []
    for dic in test_data['messages']:
        test_data_messages.append(dic['message'])
    assert test_data['start'] == 0
    assert test_data['end'] == 50
    assert test_data_messages == create_messages(0, 50)

# error cases

# test when not a valid channel_id


def test_channel_messages_v2_input_error():
    clear_v1()
    new_user = auth_register_v2("testemail@gmail.com",
                            "password", "name", "lastname")
    with pytest.raises(InputError):
        assert channel_messages_v2(new_user['token'], -42, 10)

# test when the authorised user is not a member of the channel


def test_channel_messages_v2_access_error():
    clear_v1()
    new_user = auth_register_v2("testemail@gmail.com",
                            "password", "name", "lastname")
    test_channel = create_channel(80, "test_channel4", new_user['token'])
    user_not_member = auth_register_v2(
        "testemail2@gmail.com", "password2", "name2", "lastname2")
    with pytest.raises(AccessError):
        assert channel_messages_v2(user_not_member['token'], test_channel, 0)
