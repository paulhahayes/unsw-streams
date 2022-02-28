"""
This file contains the test for the login of UNSW streams
    -it includes different cases both valid and invalid

"""

import pytest
from src.auth import auth_login_v2  # Import the function to be testing
from src.auth import auth_register_v2, auth_logout_v1
from src.users import user_profile_v1
from src.error import InputError, AccessError  # Import the error types
from src.other import clear_v1


@pytest.fixture(name="clear_data")
def clean_data():
    """cleans the datastore so there is no interference with the test."""
    clear_v1()


@pytest.fixture(name="clear_data_valid_user", )
def clean_data_valid_user():
    """cleans the data and adds one valid user."""

    clear_v1()
    assert auth_register_v2("z5303576@gmail.com",

                            "Aceofspades1", "Paul", "Hayes")


def test_valid_user(clear_data_valid_user):  # pylint: disable=unused-argument
    """Tests a basic case - valid user and password"""

    assert auth_login_v2("z5303576@gmail.com", "Aceofspades1")


def test_login_twice(clear_data_valid_user):  # pylint: disable=unused-argument
    """Tests that the function is robust and can be repeated"""

    assert auth_login_v2("z5303576@gmail.com", "Aceofspades1")
    assert auth_login_v2("z5303576@gmail.com", "Aceofspades1")


def test_valid_mutlipe_users(clear_data_valid_user):  # pylint: disable=unused-argument
    """Tests mutlple different users can use the system and an invalid case"""

    auth_register_v2("1@gmail.com", "Password1", "1", "one")
    auth_register_v2("2@gmail.com", "Password1", "2", "two")
    auth_register_v2("3@gmail.com", "Password1", "3", "three")
    auth_register_v2("4@gmail.com", "Password1", "4", "four")
    auth_register_v2("5@gmail.com", "Password1", "5", "five")
    auth_register_v2("6@gmail.com", "Password1", "6", "six")
    auth_register_v2("7@gmail.com", "Password1", "7", "seven")
    auth_register_v2("8@gmail.com", "Password1", "8", "eight")
    # test randomly
    auth_login_v2("5@gmail.com", "Password1")
    auth_login_v2("6@gmail.com", "Password1")
    auth_login_v2("1@gmail.com", "Password1")
    auth_login_v2("2@gmail.com", "Password1")
    auth_login_v2("8@gmail.com", "Password1")
    auth_login_v2("4@gmail.com", "Password1")
    # test a login that doesn't exist
    with pytest.raises(InputError):
        assert auth_login_v2("9@gmail.com", "password1")




def test_correct_user_incorrect_pw(clear_data_valid_user):  # pylint: disable=unused-argument
    """Tests a wrong password"""

    with pytest.raises(InputError):
        assert auth_login_v2("z5303576@gmail.com", "Invalidpassword1")



def test_incorrect_user(clear_data_valid_user):  # pylint: disable=unused-argument
    """Tests a wrong user"""

    with pytest.raises(InputError):
        assert auth_login_v2("Invalid@email.com", "Invalidpassword1")



def test_incorrect_user_incorrect_pw(clear_data_valid_user):  # pylint: disable=unused-argument
    """Tests all details wrong"""

    with pytest.raises(InputError):
        assert auth_login_v2("Invalid@email.com", "Invalidpassword1")


def test_return_u_id(clear_data): # pylint: disable=unused-argument
    """Tests the return value"""

    dictionary_return = auth_register_v2(
        "z5303576@gmail.com", "Aceofspades1", "Paul", "Hayes")
    u_id = dictionary_return['auth_user_id']
    assert u_id == auth_login_v2(
        "z5303576@gmail.com", "Aceofspades1")['auth_user_id']



def test_logout_offline():
    clear_v1()
    token = auth_register_v2("1@gmail.com", "Password1", "john", "zero")['token']
    auth_logout_v1(token)
    with pytest.raises(AccessError):
        assert user_profile_v1(token, 0)
    token =auth_login_v2("1@gmail.com", "Password1")['token']
    data = user_profile_v1(token, 0)
    assert data['user']['u_id'] == 0
    assert data['user']['email'] == "1@gmail.com"
    assert data['user']['handle_str'] == "johnzero"
    assert data['user']['name_first'] == "john"
    assert data['user']['name_last'] == "zero"

