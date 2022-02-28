import json
import requests
from src.error import InputError, AccessError
import pytest
from src import config
from src.other import clear_v1
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
        'email': 'paul1@gmailw.com',
        'name_first': "paul",
        'name_last': 'hayes',
        'password': 'passqword'
    }
    owner = requests.post(f'{config.url}/auth/register/v2', json=user1)
    member = requests.post(f'{config.url}/auth/register/v2', json=user2)
    owner = owner.json()
    member = member.json()
    return (owner, member)


def test_bad_regex_email():
    requests.delete(f"{config.url}/clear/v1")
    user1 = {
        'email': 'hqw@gmailw.com!',
        'name_first': "hansol11",
        'name_last': 'raspberry',
        'password': 'password'
    }
    resp = requests.post(f'{config.url}/auth/register/v2', json=user1)
    resp = resp.json()
    assert resp['code'] == InputError.code


def test_bad_password():
    requests.delete(f"{config.url}/clear/v1")
    user1 = {
        'email': 'paul@gmail.com',
        'name_first': "1231231",
        'name_last': 'raspberry',
        'password': ''
    }
    resp = requests.post(f'{config.url}/auth/register/v2', json=user1)
    resp = resp.json()
    assert resp['code'] == InputError.code


def test_short_name():
    requests.delete(f"{config.url}/clear/v1")
    user1 = {
        'email': 'paul@gmail.com',
        'name_first': "123456",
        'name_last': '',
        'password': 'password'
    }
    resp = requests.post(f'{config.url}/auth/register/v2', json=user1)
    resp = resp.json()
    assert resp['code'] == InputError.code

    requests.delete(f"{config.url}/clear/v1")
    user1 = {
        'email': 'paul@gmail.com',
        'name_first': "123456",
        'name_last': 'paul',
        'password': ''
    }
    resp = requests.post(f'{config.url}/auth/register/v2', json=user1)
    resp = resp.json()
    assert resp['code'] == InputError.code


def test_long_name():
    requests.delete(f"{config.url}/clear/v1")
    user1 = {
        'email': 'paul@gmail.com',
        'name_first': "1aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        'name_last': 'hayes',
        'password': 'password'
    }
    resp = requests.post(f'{config.url}/auth/register/v2', json=user1)
    resp = resp.json()
    assert resp['code'] == InputError.code

    requests.delete(f"{config.url}/clear/v1")
    user1 = {
        'email': 'paul@gmail.com',
        'name_first': "123456",
        'name_last': '1aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'password': 'hayes'
    }
    resp = requests.post(f'{config.url}/auth/register/v2', json=user1)
    resp = resp.json()
    assert resp['code'] == InputError.code


def test_handle_edge_cases(add_owner_and_member):
    user3 = {
        'email': 'paul2@gmail.com',
        'name_first': "paul",
        'name_last': 'hayes0',
        'password': 'password'
    }
    resp = requests.post(f'{config.url}/auth/register/v2', json=user3)
    resp = resp.json()
    user_profile = requests.get(f'{config.url}/user/profile/v1', {
        'token': resp['token'],
        'u_id': resp['auth_user_id']
    })
    user_profile = user_profile.json()
    assert user_profile['user']['handle_str'] == "paulhayes00"

    user4 = {
        'email': 'paul23@gmail.com',
        'name_first': "paul",
        'name_last': 'hayes0',
        'password': 'password'
    }
    resp = requests.post(f'{config.url}/auth/register/v2', json=user4)
    resp = resp.json()
    user_profile = requests.get(f'{config.url}/user/profile/v1', {
        'token': resp['token'],
        'u_id': resp['auth_user_id']
    })
    user_profile = user_profile.json()
    assert user_profile['user']['handle_str'] == "paulhayes01"

    user5 = {
        'email': 'paul13@gmail.com',
        'name_first': "paul",
        'name_last': 'hayes',
        'password': 'password'
    }
    resp = requests.post(f'{config.url}/auth/register/v2', json=user5)
    resp = resp.json()
    user_profile = requests.get(f'{config.url}/user/profile/v1', {
        'token': resp['token'],
        'u_id': resp['auth_user_id']
    })
    user_profile = user_profile.json()
    assert user_profile['user']['handle_str'] == "paulhayes1"


def test_duplciate_email(add_owner_and_member):
    user3 = {
        'email': 'paul@gmail.com',
        'name_first': "paul",
        'name_last': 'hayes',
        'password': 'password'
    }
    resp = requests.post(f'{config.url}/auth/register/v2', json=user3)
    resp = resp.json()
    assert resp['code'] == InputError.code


def test_login_bad_inputs(add_owner_and_member):
    requests.post(f'{config.url}/auth/logout/v1', json={
        'token': owner['token']
    })
    input = {
        'email': 'bademail@gmail.com',
        'password': 'password'

    }
    resp = requests.post(f'{config.url}/auth/login/v2', json=input)
    resp = resp.json()
    resp['code'] == AccessError.code

    input = {
        'email': 'paul@gmail.com',
        'password': 'badpassword'

    }
    resp = requests.post(f'{config.url}/auth/login/v2', json=input)
    resp = resp.json()
    resp['code'] == AccessError.code


def test_register_valid():

    requests.delete(f'{config.url}/clear/v1')

    data = {
        'email': 'hansolk@gmail.com',
        'name_first': "hansol",
        'name_last': 'raspberry',
        'password': 'password'
    }
    response = requests.post(f'{config.url}/auth/register/v2', json=data)
    response = response.json()
    assert response['auth_user_id'] == 0
    response = {'token': response['token'], 'u_id': response['auth_user_id']}
    info = requests.get(f'{config.url}/user/profile/v1', response)
    info = info.json()
    assert info['user']['email'] == "hansolk@gmail.com"
    assert info['user']['handle_str'] == "hansolraspberry"
    assert info['user']['u_id'] == 0
    assert info['user']['name_first'] == 'hansol'
    assert info['user']['name_last'] == 'raspberry'


def test_logout_login_basic():
    requests.delete(f'{config.url}/clear/v1')
    data = {
        'email': 'paul.hayes.k@gmail.com',
        'name_first': "paul",
        'name_last': 'hayes',
        'password': '123456'
    }
    resp = requests.post(f'{config.url}/auth/register/v2', json=data)
    resp = resp.json()
    resp = {'token': resp['token']}
    requests.post(f'{config.url}/auth/logout/v1', json=resp)

    requests.post(f'{config.url}/auth/login/v2', json={
        "email": "paul.hayes.k@gmail.com",
        "password": "123456"
    })


def test_removed_user_logout(add_owner_and_member):

    input = {'token': owner['token'], 'u_id': member['auth_user_id']}
    requests.delete(
        f'{config.url}/admin/user/remove/v1', json=input)

    resp = requests.post(f'{config.url}/auth/logout/v1',
                         json={'token': member['token']})

    assert resp.status_code == AccessError.code



def test_unknown_log_out():
    corrupt_token = decode_jwt(owner['token'])
    corrupt_token['u_id']
    corrupt_token['u_id'] = 999999
    corrupt_token = generate_jwt(
        corrupt_token['u_id'], corrupt_token['permission_id'], corrupt_token['handle_str'], corrupt_token['session_id'])
    resp = requests.post(f'{config.url}/auth/logout/v1',
                         json={'token': corrupt_token})
    resp = resp.json()
    assert resp['code'] == AccessError.code
