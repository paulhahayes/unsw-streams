import pytest

from src.channel import channel_addowner_v1, channel_details_v2
from src.channel import channel_removeowner_v1
from src.channels import channels_listall_v2
from src.channels import channels_create_v2
from src.channel import channel_join_v2
from src.auth import auth_register_v2
from src.other import clear_v1
from src.error import InputError
from src.error import AccessError


def is_in_owner(u_id, channel_id, token):
    channel = channel_details_v2(token, channel_id)
    for index in range(len(channel['owner_members'])):
        if u_id == channel['owner_members'][index]['u_id']:
            return True
    return False


# ADD OWNER TESTS
def test_channel_addowner_v1_owner_added():
    clear_v1()
    test_user_owner = auth_register_v2(
        "owner@gmail.com", "password", "ownername", "ownerlastname")
    test_user = auth_register_v2(
        "test@gmail.com", "password", "name", "lastname")
    channel_id = channels_create_v2(
        test_user_owner['token'], "new_channel", True)['channel_id']
    channel_join_v2(test_user['token'], channel_id)
    channel_addowner_v1(
        test_user_owner['token'], channel_id, test_user['auth_user_id'])
    assert is_in_owner(test_user['auth_user_id'],
                       channel_id, test_user['token'])


def test_channel_addowner_v1_invalid_channel_id():
    clear_v1()
    test_user = auth_register_v2(
        "test@gmail.com", "password", "name", "lastname")
    channel_id = 42
    with pytest.raises(InputError):
        assert channel_addowner_v1(
            test_user['token'], channel_id, test_user['auth_user_id'])


def test_channel_addowner_v1_invalid_u_id():
    clear_v1()
    test_user = 42
    test_user_owner = auth_register_v2(
        "owner@gmail.com", "password", "ownername", "ownerlastname")
    channel_id = channels_create_v2(
        test_user_owner['token'], "new_channel", True)['channel_id']
    with pytest.raises(InputError):
        assert channel_addowner_v1(
            test_user_owner['token'], channel_id, test_user)


def test_channel_addowner_v1_not_a_member():
    clear_v1()
    test_user_owner = auth_register_v2(
        "owner@gmail.com", "password", "ownername", "ownerlastname")
    test_user = auth_register_v2(
        "test@gmail.com", "password", "name", "lastname")
    channel_id = channels_create_v2(
        test_user_owner['token'], "new_channel", True)['channel_id']
    with pytest.raises(InputError):
        assert channel_addowner_v1(
            test_user_owner['token'], channel_id, test_user['auth_user_id'])


def test_channel_addowner_v1_already_owner():
    clear_v1()
    test_user_owner = auth_register_v2(
        "owner@gmail.com", "password", "ownername", "ownerlastname")
    channel_id = channels_create_v2(
        test_user_owner['token'], "new_channel", True)['channel_id']
    with pytest.raises(InputError):
        assert channel_addowner_v1(
            test_user_owner['token'], channel_id, test_user_owner['auth_user_id'])


def test_channel_addowner_v1_accesserror():
    clear_v1()
    test_user_owner = auth_register_v2(
        "owner@gmail.com", "password", "ownername", "ownerlastname")
    test_user = auth_register_v2(
        "test@gmail.com", "password", "name", "lastname")
    test_user1 = auth_register_v2(
        "test1@gmail.com", "password1", "name1", "lastname1")
    channel_id = channels_create_v2(
        test_user_owner['token'], "new_channel", True)['channel_id']
    channel_join_v2(test_user1['token'], channel_id)
    with pytest.raises(AccessError):
        channel_addowner_v1(test_user['token'],
                            channel_id, test_user1['auth_user_id'])

# REMOVE OWNER TESTS


def test_channel_removeowner_v1_owner_removed():
    clear_v1()
    test_user_owner = auth_register_v2(
        "owner@gmail.com", "password", "ownername", "ownerlastname")
    test_user = auth_register_v2(
        "test@gmail.com", "password", "name", "lastname")
    channel_id = channels_create_v2(
        test_user_owner['token'], "new_channel", True)['channel_id']
    channel_join_v2(test_user['token'], channel_id)
    channel_addowner_v1(
        test_user_owner['token'], channel_id, test_user['auth_user_id'])
    channel_removeowner_v1(
        test_user_owner['token'], channel_id, test_user['auth_user_id'])
    assert not is_in_owner(
        test_user['auth_user_id'], channel_id, test_user['token'])


def test_channel_removeowner_v1_invalid_channel_id():
    clear_v1()
    test_user = auth_register_v2(
        "test@gmail.com", "password", "name", "lastname")
    channel_id = 42
    with pytest.raises(InputError):
        assert channel_removeowner_v1(
            test_user['token'], channel_id, test_user['auth_user_id'])


def test_channel_removeowner_v1_invalid_u_id():
    clear_v1()
    test_user = 42
    test_user_owner = auth_register_v2(
        "owner@gmail.com", "password", "ownername", "ownerlastname")
    channel_id = channels_create_v2(
        test_user_owner['token'], "new_channel", True)['channel_id']
    with pytest.raises(InputError):
        assert channel_removeowner_v1(
            test_user_owner['token'], channel_id, test_user)


def test_channel_removeowner_v1_not_an_owner():
    clear_v1()
    test_user_owner = auth_register_v2(
        "owner@gmail.com", "password", "ownername", "ownerlastname")
    test_user = auth_register_v2(
        "test@gmail.com", "password", "name", "lastname")
    channel_id = channels_create_v2(
        test_user_owner['token'], "new_channel", True)['channel_id']
    with pytest.raises(InputError):
        assert channel_removeowner_v1(
            test_user_owner['token'], channel_id, test_user['auth_user_id'])


def test_channel_removeowner_v1_only_1_owner():
    clear_v1()
    test_user_owner = auth_register_v2(
        "owner@gmail.com", "password", "ownername", "ownerlastname")
    channel_id = channels_create_v2(
        test_user_owner['token'], "new_channel", True)['channel_id']
    with pytest.raises(InputError):
        assert channel_removeowner_v1(
            test_user_owner['token'], channel_id, test_user_owner['auth_user_id'])


def test_channel_removeowner_v1_accesserror():
    clear_v1()
    test_user_owner = auth_register_v2(
        "owner@gmail.com", "password", "ownername", "ownerlastname")
    test_user = auth_register_v2(
        "test@gmail.com", "password", "name", "lastname")
    test_user1 = auth_register_v2(
        "test1@gmail.com", "password1", "name1", "lastname1")
    channel_id = channels_create_v2(
        test_user_owner['token'], "new_channel", True)['channel_id']
    channel_join_v2(test_user1['token'], channel_id)
    channel_addowner_v1(
        test_user_owner['token'], channel_id, test_user1['auth_user_id'])
    with pytest.raises(AccessError):
        channel_removeowner_v1(
            test_user['token'], channel_id, test_user1['auth_user_id'])
