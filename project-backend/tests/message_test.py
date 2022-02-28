"""
These tests are for message.py
History
1. Honggyo Suh implementd test cases for iteration 2 on 19th Oct 2021.
"""

import pytest
import src.channel
import src.message
import src.channels
import src.auth
import src.error
import src.other
import src.create_token


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
    

# def test_message_send(setup_data):
#     """This function tests message_send_v1 in general."""
    
#     message = "Hello world"
#     message_id = src.message.message_send_v1(tester1_token, test_channel, message)
#     message_id = message_id['message_id']
    
#     assert src.message.find_message(message_id)['message'] == "Hello world"
    
    
def test_message_send_too_long(setup_data):
    """This function tests whether message_send_v1 raises error with too long message."""
    
    message = "Hello world" * 1000
    with pytest.raises(src.error.InputError):
        src.message.message_send_v1(tester1_token, test_channel, message)
    
    
def test_message_send_too_short(setup_data):
    """This function tests whether message_send_v1 raises error with empty message."""
    
    message = ""
    with pytest.raises(src.error.InputError):
        src.message.message_send_v1(tester1_token, test_channel, message)    
        
        
    
def test_message_send_invalid_channel(setup_data):
    """This function tests whether message_send_v1 raises error with invalid channel_id."""
    
    message = "Hello world"
    with pytest.raises(src.error.InputError):
        src.message.message_send_v1(tester1_token, 9, message)    
        
        
def test_message_send_invalid_user(setup_data):
    """This function tests whether message_send_v1 raises error with invalid user_id."""
    
    message = "Hello world"
    with pytest.raises(src.error.AccessError):
        src.message.message_send_v1(tester2_token, test_channel, message)   
        
        
# def test_message_edit(setup_data):
#     """This function tests message_edit_v1 in general."""
    
#     message = "Hello world"
#     message_id = src.message.message_send_v1(tester1_token, test_channel, message)   
#     message_id = message_id['message_id'] 
    
#     new_message = "Welcome to our channel"
#     src.message.message_edit_v1(tester1_token, message_id, new_message)
    
#     assert src.message.find_message(message_id)['message'] == "Welcome to our channel"
    
    
def test_message_edit_too_long(setup_data):
    """This function tests whether message_edit_v1 raises error with too long message."""
    
    message = "Hello world"
    message_id = src.message.message_send_v1(tester1_token, test_channel, message)  
    message_id = message_id['message_id']  

    with pytest.raises(src.error.InputError):
        src.message.message_edit_v1(tester1_token, message_id, "*" * 2000)
    

# def test_message_edit_too_short(setup_data):
#     """This function tests whether message_edit_v1 deletes message with empty string."""
    
#     message = "Hello world"
#     message_id = src.message.message_send_v1(tester1_token, test_channel, message)  
#     message_id = message_id['message_id']  
    
#     new_message = ""
#     src.message.message_edit_v1(tester1_token, message_id, new_message)
        
#     assert src.message.find_message(message_id) == False
    
    
def test_message_edit_invalid_message_id(setup_data):
    """This function tests whether message_edit_v1 raises error with invalid message_id."""
    
    message = "Hello world"
    src.message.message_send_v1(tester1_token, test_channel, message)    
    
    new_message = "Welcome to our channel"
    with pytest.raises(src.error.InputError):
        src.message.message_edit_v1(tester1_token, 9, new_message)
        

def test_message_edit_unauthorised_user(setup_data):
    """This function tests whether message_edit_v1 raises error with unauthorised user_id."""
    
    message = "Hello world"
    message_id = src.message.message_send_v1(tester1_token, test_channel, message) 
    message_id = message_id['message_id']   
    
    new_message = "Welcome to our channel"
    with pytest.raises(src.error.AccessError):
        src.message.message_edit_v1(tester2_token, message_id, new_message)
    
    src.channel.channel_invite_v2(tester1_token, test_channel, tester2_id)
    
    with pytest.raises(src.error.AccessError):
        src.message.message_edit_v1(tester2_token, message_id, new_message)
      
        
# def test_message_remove(setup_data):
#     """This function tests message_remove_v1 in general."""
    
#     message = "Hello world"
#     message_id = src.message.message_send_v1(tester1_token, test_channel, message)   
#     message_id = message_id['message_id'] 
    
#     src.message.message_remove_v1(tester1_token, message_id)
    
#     assert src.message.find_message(message_id) == False
        

def test_message_remove_invalid_message_id(setup_data):
    """This function tests whether message_remove_v1 raises error with invalid message_id."""
    
    message = "Hello world"
    src.message.message_send_v1(tester1_token, test_channel, message)    
    
    with pytest.raises(src.error.InputError):
        src.message.message_remove_v1(tester1_token, 9)
   

def test_message_remove_not_authorised(setup_data):
    """This function tests message_remove_v1 in general."""
    
    message = "Hello world"
    message_id = src.message.message_send_v1(tester1_token, test_channel, message)   
    message_id = message_id['message_id'] 
    
    with pytest.raises(src.error.AccessError):
        src.message.message_remove_v1(tester2_token, message_id)
    
    src.channel.channel_invite_v2(tester1_token, test_channel, tester2_id)
    
    with pytest.raises(src.error.AccessError):
        src.message.message_remove_v1(tester2_token, message_id)
