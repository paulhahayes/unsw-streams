import pytest
import requests
import json
from src.error import AccessError, InputError
from src import config
from src.create_token import generate_jwt, decode_jwt


@pytest.fixture
def add_owner_and_member():
    requests.delete(f"{config.url}/clear/v1")
    global owner
    global member
    user1 = {
        'email': 'paul@gmail.com',
        'name_first': "paul", 
        'name_last': 'hayes',
        'password': 'password'
    }
    user2 = {
        'email': 'paul2@gmail.com',
        'name_first': "paul",
        'name_last': 'hayes',
        'password': 'passqword'
    }
    owner = requests.post(f'{config.url}/auth/register/v2', json=user1)
    member = requests.post(f'{config.url}/auth/register/v2', json=user2)
    owner = owner.json()
    member = member.json()

    return (owner, member)




def test_dm_logged_out(add_owner_and_member):
    #log out
    token = {'token' : owner['token'] }
    requests.post(f'{config.url}/auth/logout/v1', json=token)
    #dm create
    resp  = requests.post(f'{config.url}/dm/create/v1', json ={
        'token' : owner['token'],
        'u_ids' : owner['auth_user_id']
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code
    assert resp['message'] == "<p>User logged out</p>"

    #dm list
    resp  = requests.get(f'{config.url}/dm/list/v1', {
        'token' : owner['token'],
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code
    assert resp['message'] == "<p>User logged out</p>"

    #dm remove
    resp = requests.delete(f'{config.url}/dm/remove/v1' , json= {
        'token' : owner['token'],
        'dm_id' : 0
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code
    assert resp['message'] == "<p>User logged out</p>"

    #dm details
    resp  = requests.get(f'{config.url}/dm/details/v1', {
        'token' : owner['token'],
        'dm_id' : 0
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code
    assert resp['message'] == "<p>User logged out</p>"

    #dm leave

    resp  = requests.post(f'{config.url}/dm/leave/v1', json = {
        'token' : owner['token'],
        'dm_id' : 0
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code
    assert resp['message'] == "<p>User logged out</p>"


    # dm messages
    resp  = requests.get(f'{config.url}/dm/messages/v1', {
        'token' : owner['token'],
        'dm_id' : 0,
        'start' : 0
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code
    assert resp['message'] == "<p>User logged out</p>"

def test_bad_u_ids(add_owner_and_member):

    resp  = requests.post(f'{config.url}/dm/create/v1', json ={
        'token' : owner['token'],
        'u_ids' : [9998, 9999] 
    })
    resp = resp.json()
    assert resp['code'] == InputError.code
    assert resp['message'] == "<p>the users are not valid</p>"\




def test_remove_dm_bad_dm_id(add_owner_and_member):

    requests.post(f'{config.url}/dm/create/v1', json ={
        'token' : owner['token'],
        'u_ids' : [1] 
    })
    resp = requests.delete(f'{config.url}/dm/remove/v1' , json= {
        'token' : owner['token'],
        'dm_id' : 9999999
    })
    resp = resp.json()
    assert resp['code'] == InputError.code
    assert resp['message'] == "<p>not valid dm id</p>"


def test_successful_dm_create(add_owner_and_member):

    resp = requests.post(f'{config.url}/dm/create/v1', json ={
        'token' : owner['token'],
        'u_ids' : [1] 
    })
    resp = resp.json()
    assert resp['dm_id'] == 0


def test_dm_corrupted_token(add_owner_and_member):
    corrupt_token = decode_jwt(owner['token'])
    corrupt_token['u_id']
    corrupt_token['u_id'] = 999999
    corrupt_token = generate_jwt(
    corrupt_token['u_id'], corrupt_token['permission_id'], corrupt_token['handle_str'], corrupt_token['session_id'])
    
    resp  = requests.get(f'{config.url}/dm/details/v1', {
        'token' : corrupt_token,
        'dm_id' : 0
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code
    assert resp['message'] == "<p>Unknown user</p>"

    resp  = requests.post(f'{config.url}/dm/leave/v1', json={
        'token' : corrupt_token,
        'dm_id' : 0
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code
    assert resp['message'] == "<p>Unknown user</p>"

    resp  = requests.get(f'{config.url}/dm/messages/v1', {
        'token' : corrupt_token,
        'dm_id' : 0,
        'start' : 0
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code
    assert resp['message'] == "<p>Unknown user</p>"


def test_bad_inputs_dm_details(add_owner_and_member):

    user3 = {
        'email': 'Hayes@gmail.com',
        'name_first': "paul", 
        'name_last': 'hayes',
        'password': 'password'
    }
    requests.post(f'{config.url}/auth/register/v2', json=user3)

    requests.post(f'{config.url}/dm/create/v1', json ={
        'token' : owner['token'],
        'u_ids' : [2] 
    })

    resp  = requests.get(f'{config.url}/dm/details/v1', {
        'token' : member['token'],
        'dm_id' : 0
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code
    assert resp['message'] == "<p>The user is not a member of dm</p>"

    resp  = requests.get(f'{config.url}/dm/details/v1', {
        'token' : owner['token'],
        'dm_id' : 9999
    })
    resp = resp.json()
    
    assert resp['code'] == InputError.code
    assert resp['message'] == "<p>The dm is not valid</p>"

def test_dm_details_successful(add_owner_and_member):
    user3 = {
        'email': 'Hayes@gmail.com',
        'name_first': "paul", 
        'name_last': 'hayes',
        'password': 'password'
    }
    requests.post(f'{config.url}/auth/register/v2', json=user3)

    requests.post(f'{config.url}/dm/create/v1', json ={
        'token' : owner['token'],
        'u_ids' : [2] 
    })
    
    resp  = requests.get(f'{config.url}/dm/details/v1', {
        'token' : owner['token'],
        'dm_id' : 0
    })
    resp = resp.json()

    assert resp['name'] == 'paulhayes, paulhayes1'


def test_rm_user_successful(add_owner_and_member):
    
    requests.post(f'{config.url}/dm/create/v1', json ={
        'token' : owner['token'],
        'u_ids' : [1] 
    })
    resp = requests.delete(f'{config.url}/dm/remove/v1' , json= {
        'token' : owner['token'],
        'dm_id' : 0
    })
    resp = resp.json()
    assert resp == {}



def test_dm_mutliples(add_owner_and_member):
            
    requests.post(f'{config.url}/dm/create/v1', json ={
        'token' : owner['token'],
        'u_ids' : [1] 
    })

    requests.post(f'{config.url}/dm/create/v1', json ={
        'token' : owner['token'],
        'u_ids' : [] 
    })
    requests.post(f'{config.url}/dm/create/v1', json ={
        'token' : member['token'],
        'u_ids' : [] 
    })
    requests.post(f"{config.url}/message/senddm/v1", json = {'token': owner['token'], 'dm_id': 0, 'message': 'hello'})
    requests.post(f"{config.url}/message/senddm/v1", json = {'token': owner['token'], 'dm_id': 1, 'message': 'hello'})
    requests.post(f"{config.url}/message/senddm/v1", json = {'token': member['token'], 'dm_id': 2, 'message': 'hello'})
    requests.post(f"{config.url}/message/senddm/v1", json = {'token' :member['token'], 'dm_id': 0, 'message': 'hello'})
    requests.post(f"{config.url}/message/senddm/v1", json = {'token': owner['token'], 'dm_id': 1, 'message': 'hello'})
    requests.post(f"{config.url}/message/senddm/v1", json = {'token': member['token'], 'dm_id': 2, 'message': 'hello'})


def test_dm_details(add_owner_and_member):
    requests.post(f'{config.url}/dm/create/v1', json ={
        'token' : member['token'],
        'u_ids' : [] 
    })
    resp = requests.get(f'{config.url}/dm/details/v1', {
        'token' : owner['token'],
        'dm_id' : 0
    })
    resp = resp.json()


def test_dm_messages_wrong_user(add_owner_and_member):
    requests.post(f'{config.url}/dm/create/v1', json ={
        'token' : member['token'],
        'u_ids' : [] 
    })

    msg_id = requests.post(f"{config.url}/message/senddm/v1", json = {'token': member['token'], 'dm_id': 0, 'message': 'hello'})
    msg_id = msg_id.json()

    resp  = requests.get(f'{config.url}/dm/messages/v1', {
        'token' : owner['token'],
        'dm_id' : 0,
        'start' : 0
    })
    assert resp.status_code == AccessError.code
    requests.post(f"{config.url}/message/react/v1", json = {'token': member['token'], 'message_id': msg_id['message_id'], 'react_id': 1})
    resp = requests.get(f'{config.url}/dm/messages/v1', {
        'token' : member['token'],
        'dm_id' : 0,
        'start' : 0
    })
    assert resp.status_code == 200