r'''

Auth register Tests - This file contains the the pytests for the Auth register functions
    - It tests both valid and invalid cases
    - The conditions for valid users include:
        - Email: prefix and domain regex = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
        - Password: Must be greater than 6 charcaters
        - First Name: between 1 and 50 characters inclusive
        - Last Name: between 1 and 50 characters inclusive

'''
# import pytest for testing functions
import pytest
# Import the function to be testing
from src.auth import auth_register_v2
# Import auth login to check return ID is correct
from src.auth import auth_login_v2
# Import channels details for blackbox testing
#from src.channels import channels_create_v1
#from src.channel import channel_details_v1
# Import the error types
from src.error import InputError
# Import clear to clean data for tests
from src.other import clear_v1

# pytest fixtures

@pytest.fixture(name="clear_data_valid_user", )
def clean_data_valid_user():
    """cleans the data and adds one valid user."""

    clear_v1()
    assert auth_register_v2("z5303576@gmail.com",

                            "Aceofspades1", "Paul", "Hayes")
# TESTS


def test_valid_register():  
    """Tests a valid user and make sure no errors are raised"""
    clear_v1()
    assert auth_register_v2("z5303576@gmail.com",

                            "Aceofspades1", "Paul", "Hayes")


def test_duplicate_register(clear_data_valid_user):
    """Excepts an error because the same email used twice."""
    
    with pytest.raises(InputError):
        assert auth_register_v2("z5303576@gmail.com",
                                "Aceofspades1", "Paul", "Hayes")


def test_mutli_valid_register():
    """Tests the function can handle mutliple registrations."""
    clear_v1()
    assert auth_register_v2(
        "validone@unsw.com", "Aceofspades1", "Sam", "Jones")
    assert auth_register_v2(
        "validtwo@unsw.com", "Aceofspades1", "Tina", "Jones")
    assert auth_register_v2(
        "validthree@unsw.com", "Aceofspades1", "Michael", "Jones")
    assert auth_register_v2(
        "validfour@unsw.com", "Aceofspades1", "Sarah", "Jones")
    assert auth_register_v2(
        "validfive@unsw.com", "Aceofspades1", "Bella", "Jones")
    assert auth_register_v2(
        "validsix@unsw.com", "Aceofspades1", "Nicole", "Jones")
    assert auth_register_v2(
        "validseven@unsw.com", "Aceofspades1", "Cindy", "Jones")
    #store = data_store.get()
    #assert (len(store['users'])) == 7


def test_email_no_atsign():
    """Excepts an error because of bad email."""
    clear_v1()
    with pytest.raises(InputError):
        assert auth_register_v2("suspectemailgmail.com",
                                "Aceofspades1", "Milton", "Martinez")


def test_email_bad_prefix():
    """Excepts an error because of bad email prefix."""
    clear_v1()
    with pytest.raises(InputError):
        assert auth_register_v2(
            "^@gmail.com", "Aceofspades1", "Shane", "Oneil")


def test_email_bad_domain():
    """Excepts an error because of bad email domain."""
    clear_v1()
    with pytest.raises(InputError):
        assert auth_register_v2("Ishod.wair@gmail.com$",
                                "Aceofspades1", "Ishod", "Wair")


def test_short_password():
    """Excepts an error because password < 6 chars."""
    clear_v1()
    with pytest.raises(InputError):
        assert auth_register_v2("goodemail@gmail.com",
                                "hello", "Emily", "Ratajkowski")


def test_short_firstname():
    """Excepts an error because short first name."""
    clear_v1()
    with pytest.raises(InputError):
        assert auth_register_v2("Gucci@gmail.com", "Aceofspades1", "", "Gucci")


def test_long_firstname():
    """Excepts an error because of long first name."""
    clear_v1()
    with pytest.raises(InputError):
        assert auth_register_v2("goodemail@gmail.com", "Aceofspades1",
                                "asseocarnisanguineoviscericartilaginonervomedullary", "")


def test_short_lastname():
    """Excepts an error because of last short name."""
    clear_v1()
    with pytest.raises(InputError):
        assert auth_register_v2("goodemail@gmail.com",
                                "Aceofspades1", "Sarah", "")


def test_long_lastname():
    """Excepts an error because of long last name."""
    clear_v1()
    with pytest.raises(InputError):
        assert auth_register_v2("goodemail@gmail.com", "Aceofspades1",
                                "Matt", "aequeosalinocalcalinoceraceoaluminosocupreovitriolic")


def test_register_return_works():
    """Tests that the return ID is store and valid"""
    clear_v1()
    dictionary_return = auth_register_v2(
        "z5303576@gmail.com", "Aceofspades1", "Paul", "Hayes")
    test_id = dictionary_return['auth_user_id']
    login_return = auth_login_v2("z5303576@gmail.com", "Aceofspades1")
    login_test_id = login_return['auth_user_id']
    assert test_id == login_test_id


def test_register_return_incorrect():
    """Tests that the return ID is unique."""
    clear_v1()
    dictionary_return = auth_register_v2(
        "z5303576@gmail.com", "Aceofspades1", "Paul", "Hayes")
    correct_id = dictionary_return['auth_user_id']
    fail_return = auth_login_v2("z5303576@gmail.com", "Aceofspades1")
    fail_test_id = fail_return['auth_user_id']
    # change the Id slightly to fail
    fail_test_id = fail_test_id + 1
    assert correct_id != fail_test_id
    