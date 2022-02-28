import pytest

from src.channels import channels_create_v2


from src.channel import channel_details_v2
from src.other import clear_v1
from src.auth import auth_register_v2
from src.error import InputError
from src.create_token import decode_jwt

# Checks if channel_id is in channels_listall_v1


def is_channel_in_data_store(channel_id, token, name, is_public):
    user_id = decode_jwt(token)['u_id']
    channel = channel_details_v2(token, channel_id)
    print(channel)
    if user_id == channel['all_members'][0]['u_id'] \
            and channel['name'] == name \
            and channel['is_public'] == is_public:
        return True
    return False


def test_channels_create_v2_name_true():
    clear_v1()
    test_user_1 = auth_register_v2(
        "test@gmail.com", "password", "name", "last")
    channel_id = channels_create_v2(
        test_user_1['token'], "Benedict", True)['channel_id']
    assert is_channel_in_data_store(
        channel_id, test_user_1['token'], "Benedict", True)


def test_channels_create_v2_my_channel_true():
    clear_v1()
    test_user_1 = auth_register_v2(
        "test@gmail.com", "password", "name", "last")
    channel_id1 = channels_create_v2(
        test_user_1['token'], "my_channel", True)['channel_id']
    assert is_channel_in_data_store(
        channel_id1, test_user_1['token'], "my_channel", True)


def test_channels_create_v2_com1531_false():
    clear_v1()
    test_user_2 = auth_register_v2(
        "test2@gmail.com", "password2", "name2", "last2")
    channel_id0 = channels_create_v2(
        test_user_2['token'], "comp1531_channel", False)['channel_id']
    assert is_channel_in_data_store(
        channel_id0, test_user_2['token'], "comp1531_channel", False)


def test_channels_create_v2_new_channel_false():
    clear_v1()
    test_user_2 = auth_register_v2(
        "test2@gmail.com", "password2", "name2", "last2")
    channel_id2 = channels_create_v2(
        test_user_2['token'], "New_Channel", False)['channel_id']
    assert is_channel_in_data_store(
        channel_id2, test_user_2['token'], "New_Channel", False)


def test_channels_create_v2_input_error_false():
    clear_v1()
    test_user_3 = auth_register_v2(
        "test3@gmail.com", "password3", "name3", "last3")
    with pytest.raises(InputError):
        assert channels_create_v2(
            test_user_3['token'], "TheChannelNameIsMoreThan20CharactersLong", False)


def test_channels_create_v2_input_error_true():
    clear_v1()
    test_user_3 = auth_register_v2(
        "test3@gmail.com", "password3", "name3", "last3")
    with pytest.raises(InputError):
        assert channels_create_v2(
            test_user_3['token'], "TheChannelNameIsMoreThan20CharactersLong", True)


def test_channels_create_v2_input_error_false_no_ch_name():
    clear_v1()
    test_user_3 = auth_register_v2(
        "test3@gmail.com", "password3", "name3", "last3")
    with pytest.raises(InputError):
        assert channels_create_v2(test_user_3['token'], "", False)


def test_channels_create_v2_input_error_true_no_ch_name():
    clear_v1()
    test_user_3 = auth_register_v2(
        "test3@gmail.com", "password3", "name3", "last3")
    with pytest.raises(InputError):
        assert channels_create_v2(test_user_3['token'], "", True)
