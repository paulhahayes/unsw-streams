import pytest
import json
import requests
from src.error import InputError, AccessError
from src.auth import auth_register_v2, auth_login_v2
from src.other import clear_v1
from src.users import users_all_v1, user_profile_v1, user_profile_setname_v1, user_profile_setemail_v1, user_profile_sethandle_v1
from src import config
from src.create_token import generate_jwt, decode_jwt


@pytest.fixture
def add_owner_and_member():
    requests.delete(f"{config.url}/clear/v1")
    global owner
    global member
    user1 = {
        'email': 'hansolk@gmail.com',
        'name_first': "hansol",
        'name_last': 'raspberry',
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


def test_offline_functions_valid_user_update():
    clear_v1()
    info = auth_register_v2("111111@gmail.com", "Password1", "paul", "hayes")
    auth_register_v2("1rock11@gmail.com", "Password1", "jason", "linda")
    auth_register_v2("111ra@gmail.com", "Password1", "randy", "rocky")
    modified = info['token'] + " yellow"
    with pytest.raises(AccessError):
        assert(users_all_v1(modified))
    info = auth_login_v2("111111@gmail.com", "Password1")
    user_profile_v1(info['token'], info['auth_user_id'])
    user_profile_setname_v1(info['token'], "Jimmy", "rickard")
    user_profile_setemail_v1(info['token'], "Jimmy@gmail.com")
    user_profile_sethandle_v1(info['token'], "jimmyrichard")
    user_profile_v1(info['token'], info['auth_user_id'])
    assert user_profile_v1(info['token'], info['auth_user_id']) == {'user': {
        'u_id': 0, 'email': 'Jimmy@gmail.com', 'name_first': 'Jimmy', 'name_last': 'rickard', 'handle_str': 'jimmyrichard', 'profile_img_url': config.url+"static/unswstreams.jpg"}}


def test_user_all_route(add_owner_and_member):

    input = {'token': owner['token']}
    info = requests.get(f'{config.url}/users/all/v1', input)
    info = info.json()
    assert 'hansolk@gmail.com' == info['users'][0]['email']
    assert 0 == info['users'][0]['u_id']
    assert 'hansol' == info['users'][0]['name_first']
    assert 'raspberry' == info['users'][0]['name_last']
    assert 'hansolraspberry' == info['users'][0]['handle_str']


def test_user_all_route_bad_token(add_owner_and_member):

    input = {'token': "bad token"}
    resp = requests.get(f'{config.url}/users/all/v1', input)
    resp = json.loads(resp.text)
    assert resp['code'] == AccessError.code


def test_user_all_route_logged_out(add_owner_and_member):

    input = {'token': owner['token']}
    requests.post(f'{config.url}/auth/logout/v1', json=input)
    resp = requests.get(f'{config.url}/users/all/v1', input)
    resp = json.loads(resp.text)
    assert resp['code'] == AccessError.code


def test__valid_user_details():

    owner = requests.post(f'{config.url}/auth/login/v2', json={
        'email': 'hansolk@gmail.com',
        'password': 'password'
    })
    owner = owner.json()
    input = {'token': owner['token'], 'u_id': owner['auth_user_id']}
    info = requests.get(f'{config.url}/user/profile/v1', input)
    info = info.json()
    assert info['user']['email'] == "hansolk@gmail.com"
    assert info['user']['handle_str'] == "hansolraspberry"
    assert info['user']['u_id'] == 0
    assert info['user']['name_first'] == 'hansol'
    assert info['user']['name_last'] == 'raspberry'


def test_user_details_logged_out(add_owner_and_member):

    input = {'token': owner['token'], 'u_id': owner['auth_user_id']}
    token = {'token': owner['token']}
    requests.post(f'{config.url}/auth/logout/v1', json=token)
    resp = requests.get(f'{config.url}/user/profile/v1', input)
    resp = json.loads(resp.text)
    assert resp['code'] == AccessError.code


def test_user_detail_route_bad_token(add_owner_and_member):

    input = {'token': "bad_token", 'u_id': owner['auth_user_id']}
    resp = requests.get(f'{config.url}/user/profile/v1', input)
    resp = json.loads(resp.text)
    assert resp['code'] == 403


def test_user_detail_route_bad_id(add_owner_and_member):
    input = {'token': owner['token'], 'u_id': 999999}
    resp = requests.get(f'{config.url}/user/profile/v1', input)
    resp = json.loads(resp.text)
    assert resp['code'] == InputError.code


def test__valid_set_name(add_owner_and_member):
    profile = {'token': owner['token'], 'u_id': owner['auth_user_id']}
    input = {'token': owner['token']}
    names = {"name_first": "paul", "name_last": "hayes"}
    input.update(names)
    requests.put(f'{config.url}/user/profile/setname/v1', json=input)
    input = {'token': input['token']}
    info = requests.get(f'{config.url}/user/profile/v1', profile)
    info = json.loads(info.text)
    assert info['user']['u_id'] == 0
    assert info['user']['name_first'] == 'paul'
    assert info['user']['name_last'] == 'hayes'


def test_bad_token_detail_route_profile(add_owner_and_member):
    input = {'token': "bad token"}
    names = {"name_first": "john", "name_last": "hayes"}
    input.update(names)
    resp = requests.put(f'{config.url}/user/profile/setname/v1', json=input)
    resp = json.loads(resp.text)
    assert resp['code'] == AccessError.code


def test__invalid_set_name():
    requests.delete(f'{config.url}/clear/v1')
    data = {
        'email': 'hansolk@gmail.com',
        'name_first': "hansol",
        'name_last': 'raspberry',
        'password': 'password'
    }
    response = requests.post(f'{config.url}/auth/register/v2', json=data)
    input = response.json()

    input = {'token': input['token']}
    names = {"name_first": "", "name_last": "hayes"}
    input.update(names)
    resp = requests.put(f'{config.url}/user/profile/setname/v1', json=input)
    resp = json.loads(resp.text)
    assert resp['code'] == 400
    names = {"name_first": "paul", "name_last": ""}
    input = {'token': input['token']}
    input.update(names)
    resp = requests.put(f'{config.url}/user/profile/setname/v1', json=input)
    resp = json.loads(resp.text)
    assert resp['code'] == 400
    names = {"name_first": "paulaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "name_last": "hayes"}
    input = {'token': input['token']}
    input.update(names)
    resp = requests.put(f'{config.url}/user/profile/setname/v1', json=input)
    resp = json.loads(resp.text)
    assert resp['code'] == 400
    names = {"name_first": "paa",
             "name_last": "paulaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"}
    input = {'token': input['token']}
    input.update(names)
    resp = requests.put(f'{config.url}/user/profile/setname/v1', json=input)
    resp = json.loads(resp.text)
    assert resp['code'] == InputError.code


def test__valid_set_email(add_owner_and_member):

    profile = {'token': owner['token'], 'u_id': owner['auth_user_id']}
    input = {'token': owner['token']}
    email = {"email": "paul.hayes.k@gmail.com"}
    input.update(email)
    requests.put(f'{config.url}/user/profile/setemail/v1', json=input)
    input = {'token': input['token']}
    info = requests.get(f'{config.url}/user/profile/v1', profile)
    info = json.loads(info.text)
    assert info['user']['email'] == "paul.hayes.k@gmail.com"


def test_invalid_set_email():
    requests.delete(f'{config.url}/clear/v1')
    data = {
        'email': 'paul.hayes.k@gmail.com',
        'name_first': "hansol",
        'name_last': 'raspberry',
        'password': 'password'
    }
    response = requests.post(f'{config.url}/auth/register/v2', json=data)
    input = response.json()
    input = {'token': input['token']}
    email = {"email": "paul.hayes.k@gmail.com"}
    input.update(email)
    resp = requests.put(f'{config.url}/user/profile/setemail/v1', json=input)
    resp = json.loads(resp.text)
    assert resp['code'] == InputError.code


def test_set_email_bad_token(add_owner_and_member):
    input = {'token': "bad token"}
    email = {"email": "paul.hayes.k@gmail.com"}
    input.update(email)
    resp = requests.put(f'{config.url}/user/profile/setemail/v1', json=input)
    resp = json.loads(resp.text)
    assert resp['code'] == AccessError.code


def test_set_email_loggedout():
    requests.delete(f'{config.url}/clear/v1')
    data = {
        'email': 'hansolk@gmail.com',
        'name_first': "hansol",
        'name_last': 'raspberry',
        'password': 'password'
    }
    response = requests.post(f'{config.url}/auth/register/v2', json=data)
    input = response.json()
    token = {'token': input['token']}
    input = {'token': input['token']}
    email = {"email": "paul.hayes.k@gmail.com"}
    input.update(email)
    requests.post(f'{config.url}/auth/logout/v1', json=token)
    resp = requests.put(f'{config.url}/user/profile/setemail/v1', json=input)
    resp = json.loads(resp.text)
    assert resp['code'] == AccessError.code


def test_set_email_invalid(add_owner_and_member):

    input = {'token': owner['token']}
    email = {"email": "pauWQ!@#!l.hayes.k@gmail.com!@#"}
    input.update(email)
    resp = requests.put(f'{config.url}/user/profile/setemail/v1', json=input)
    resp = json.loads(resp.text)
    assert resp['code'] == InputError.code


def test_set_valid_handle_str():

    requests.delete(f'{config.url}/clear/v1')
    data = {
        'email': 'hansolk@gmail.com',
        'name_first': "hansol",
        'name_last': 'raspberry',
        'password': 'password'
    }
    response = requests.post(f'{config.url}/auth/register/v2', json=data)
    input = response.json()
    profile = {'token': input['token'], 'u_id': input['auth_user_id']}
    input = {'token': input['token']}
    handle_str = {"handle_str": "newhandle"}
    input.update(handle_str)
    requests.put(f'{config.url}/user/profile/sethandle/v1', json=input)
    info = requests.get(f'{config.url}/user/profile/v1', profile)
    info = json.loads(info.text)
    assert info['user']['handle_str'] == "newhandle"


def test_set_handle_bad_token():
    requests.delete(f'{config.url}/clear/v1')
    data = {
        'email': 'hansolk@gmail.com',
        'name_first': "hansol",
        'name_last': 'raspberry',
        'password': 'password'
    }
    response = requests.post(f'{config.url}/auth/register/v2', json=data)
    input = response.json()
    input['token'] = input['token'] + "hello"
    handle_str = {"handle_str": "newhandle"}
    input.update(handle_str)
    resp = requests.put(f'{config.url}/user/profile/sethandle/v1', json=input)
    resp = json.loads(resp.text)
    assert resp['code'] == AccessError.code


def test_set_handle_already_exists():
    requests.delete(f'{config.url}/clear/v1')
    data = {
        'email': 'hansolk@gmail.com',
        'name_first': "hansol",
        'name_last': 'raspberry',
        'password': 'password'
    }
    response = requests.post(f'{config.url}/auth/register/v2', json=data)
    input = response.json()
    handle_str = {"handle_str": "hansolraspberry"}
    input.update(handle_str)
    resp = requests.put(f'{config.url}/user/profile/sethandle/v1', json=input)
    resp = json.loads(resp.text)
    assert resp['code'] == InputError.code


def test_set_handle_logged_out():
    requests.delete(f'{config.url}/clear/v1')
    data = {
        'email': 'hansolk@gmail.com',
        'name_first': "hansol",
        'name_last': 'raspberry',
        'password': 'password'
    }
    response = requests.post(f'{config.url}/auth/register/v2', json=data)
    input = response.json()
    input = {'token': input['token']}
    token = {'token': input['token']}
    handle_str = {"handle_str": "newhandle"}
    input.update(handle_str)
    requests.post(f'{config.url}/auth/logout/v1', json=token)
    resp = requests.put(f'{config.url}/user/profile/sethandle/v1', json=input)
    resp = json.loads(resp.text)
    assert resp['code'] == AccessError.code


def test_set_handle_invalid_handle(add_owner_and_member):

    input = {'token': owner['token']}
    handle_str = {"handle_str": "newhandle!"}
    input.update(handle_str)
    resp = requests.put(f'{config.url}/user/profile/sethandle/v1', json=input)
    resp = json.loads(resp.text)
    assert resp['code'] == InputError.code
    input = {'token': owner['token']}
    handle_str = {"handle_str": "it"}
    input.update(handle_str)
    resp = requests.put(f'{config.url}/user/profile/sethandle/v1', json=input)
    resp = json.loads(resp.text)
    assert resp['code'] == InputError.code
    input = {'token': owner['token']}
    handle_str = {"handle_str": "0123456789012345678901"}
    input.update(handle_str)
    resp = requests.put(f'{config.url}/user/profile/sethandle/v1', json=input)
    resp = json.loads(resp.text)
    assert resp['code'] == InputError.code


def test_removed_user(add_owner_and_member):
    input = {'token': owner['token'], 'u_id': member['auth_user_id']}
    requests.delete(
        f'{config.url}/admin/user/remove/v1', json=input)
    info = requests.get(f'{config.url}/user/profile/v1', input)
    info = info.json()
    assert info['user']['email'] == "paul1@gmailw.com"
    assert info['user']['handle_str'] == "paulhayes"
    assert info['user']['u_id'] == 1
    assert info['user']['name_first'] == 'Removed'
    assert info['user']['name_last'] == 'user'


def test_removed_user_all(add_owner_and_member):
    input = {'token': owner['token'], 'u_id': member['auth_user_id']}
    requests.delete(
        f'{config.url}/admin/user/remove/v1', json=input)
    resp = requests.get(f'{config.url}/users/all/v1',
                        {'token': owner['token']})
    resp = resp.json()
    assert resp == {'users': [{'u_id': 0, 'email': 'hansolk@gmail.com',
                               'name_first': 'hansol', 'name_last': 'raspberry', 'handle_str': 'hansolraspberry', "profile_img_url": config.url+"static/unswstreams.jpg"}]}


def test_bad_user_id():
    input = {'token': owner['token'], 'u_id': 99999999}
    info = requests.get(f'{config.url}/user/profile/v1', input)
    info = info.json()
    assert info['code'] == InputError.code


def test_hacked_token_user_all(add_owner_and_member):
    corrupt_token = decode_jwt(owner['token'])
    corrupt_token['u_id'] = 999
    corrupt_token = generate_jwt(
        corrupt_token['u_id'], corrupt_token['permission_id'], corrupt_token['handle_str'], corrupt_token['session_id'])
    resp = requests.get(f'{config.url}/users/all/v1', {'token': corrupt_token})
    resp = resp.json()
    assert resp['code'] == AccessError.code


def test_session_id():
    requests.delete(f"{config.url}/clear/v1")
    token = generate_jwt(
        0, 1, "jason", None)
    token = decode_jwt(token)
    assert token['session_id'] != None


def test_normal_user(add_owner_and_member):

    info = requests.get(f'{config.url}/user/profile/v1',
                        {'token': owner['token'], 'u_id': owner['auth_user_id']})
    info = info.json()
    assert info == {'user': {'u_id': 0, 'email': 'hansolk@gmail.com',
                             'name_first': 'hansol', 'name_last': 'raspberry', 'handle_str': 'hansolraspberry', 'profile_img_url': config.url+"static/unswstreams.jpg"}}

    resp = requests.get(f'{config.url}/users/all/v1',
                        {'token': owner['token']})
    resp = resp.json()
    assert resp == {'users': [{'u_id': 0, 'email': 'hansolk@gmail.com', 'name_first': 'hansol', 'name_last': 'raspberry', 'handle_str': 'hansolraspberry', "profile_img_url": config.url+"static/unswstreams.jpg"}, {
        'u_id': 1, 'email': 'paul1@gmailw.com', 'name_first': 'paul', 'name_last': 'hayes', 'handle_str': 'paulhayes', 'profile_img_url': config.url+"static/unswstreams.jpg"}]}


def test_user_image_success(add_owner_and_member):
    resp = requests.post(f'{config.url}/user/profile/uploadphoto/v1', json={
        'token': owner['token'],
        'img_url': "http://cgi.cse.unsw.edu.au/~morri/morriphoto.jpg",
        'x_start': 1000,
        'y_start': 1000,
        'x_end': 2000,
        'y_end': 2000
    })
    resp = resp.json()
    assert resp == {}


def test_bad_image_size(add_owner_and_member):
    resp = requests.post(f'{config.url}/user/profile/uploadphoto/v1', json={
        'token': owner['token'],
        'img_url': "http://cgi.cse.unsw.edu.au/~morri/morriphoto.jpg",
        'x_start': -500,
        'y_start': -500,
        'x_end': 2000,
        'y_end': 2000
    })
    assert resp.status_code == InputError.code


def test_bad_cooridnates(add_owner_and_member):
    resp = requests.post(f'{config.url}/user/profile/uploadphoto/v1', json={
        'token': owner['token'],
        'img_url': "http://cgi.cse.unsw.edu.au/~morri/morriphoto.jpg",
        'x_start': 2500,
        'y_start': 2500,
        'x_end': 2000,
        'y_end': 2000
    })
    assert resp.status_code == InputError.code


def test_crop_size_too_big(add_owner_and_member):
    resp = requests.post(f'{config.url}/user/profile/uploadphoto/v1', json={
        'token': owner['token'],
        'img_url': "http://cgi.cse.unsw.edu.au/~morri/morriphoto.jpg",
        'x_start': 1000000,
        'y_start': 1000000,
        'x_end': 2000,
        'y_end': 2000
    })
    assert resp.status_code == InputError.code


def test_bad_address_success(add_owner_and_member):
    resp = requests.post(f'{config.url}/user/profile/uploadphoto/v1', json={
        'token': owner['token'],
        'img_url': "google.com",
        'x_start': 100,
        'y_start': 100,
        'x_end': 101,
        'y_end': 101
    })
    resp.json()
    assert resp.status_code == InputError.code


def test_non_jpg(add_owner_and_member):
    resp = requests.post(f'{config.url}/user/profile/uploadphoto/v1', json={
        'token': owner['token'],
        'img_url': "http://www.cse.unsw.edu.au/~richardb/index_files/RichardBuckland-200.png",
        'x_start': 0,
        'y_start': 0,
        'x_end': 1,
        'y_end': 1
    })
    assert resp.status_code == InputError.code


def test_random_image_from_the_internet(add_owner_and_member):
    resp = requests.post(f'{config.url}/user/profile/uploadphoto/v1', json={
        'token': owner['token'],
        'img_url': "https://www.edigitalagency.com.au/wp-content/uploads/instagram-logo-svg-vector-for-print.svg",
        'x_start': 0,
        'y_start': 0,
        'x_end': 1,
        'y_end': 1
    })
    assert resp.status_code == InputError.code


def test_random_png(add_owner_and_member):
    resp = requests.post(f'{config.url}/user/profile/uploadphoto/v1', json={
        'token': owner['token'],
        'img_url': "https://upload.wikimedia.org/wikipedia/commons/thumb/9/9a/PNG_transparency_demonstration_2.png/220px-PNG_transparency_demonstration_2.png",
        'x_start': 0,
        'y_start': 0,
        'x_end': 1,
        'y_end': 1
    })
    assert resp.status_code == InputError.code

def test_y_cooridnates(add_owner_and_member):
    resp = requests.post(f'{config.url}/user/profile/uploadphoto/v1', json={
        'token': owner['token'],
        'img_url': "http://cgi.cse.unsw.edu.au/~morri/morriphoto.jpg",
        'x_start': 20,
        'y_start': 25,
        'x_end': 25,
        'y_end': 19
    })
    assert resp.status_code == InputError.code




def test_x_end_cooridnates(add_owner_and_member):
    resp = requests.post(f'{config.url}/user/profile/uploadphoto/v1', json={
        'token': owner['token'],
        'img_url': "http://cgi.cse.unsw.edu.au/~morri/morriphoto.jpg",
        'x_start': 1,
        'y_start': 1,
        'x_end': 10000,
        'y_end': 19
    })
    assert resp.status_code == InputError.code



def test_y_end_cooridnates(add_owner_and_member):
    resp = requests.post(f'{config.url}/user/profile/uploadphoto/v1', json={
        'token': owner['token'],
        'img_url': "http://cgi.cse.unsw.edu.au/~morri/morriphoto.jpg",
        'x_start': 1,
        'y_start': 1,
        'x_end': 2,
        'y_end': 10000
    })
    assert resp.status_code == InputError.code



def test_removed_users(add_owner_and_member):

    user3 = {
        'email': 'pauergergl1@gmailw.com',
        'name_first': "paul",
        'name_last': 'hayes',
        'password': 'passqword'
    }
    user3 = requests.post(f'{config.url}/auth/register/v2', json=user3)
    user3 = user3.json()
    input = {'token': owner['token'], 'u_id': member['auth_user_id']}
    input2 = {'token': owner['token'], 'u_id': user3['auth_user_id']}
    input3 = {'token': owner['token'], 'u_id': owner['auth_user_id']}
    requests.delete(
        f'{config.url}/admin/user/remove/v1', json=input)
    input = {'token': owner['token'], 'u_id': member['auth_user_id']}
    resp = requests.get(f'{config.url}/user/profile/v1', input2)
    assert resp.status_code == 200
    resp = requests.get(f'{config.url}/user/profile/v1', input3)
    assert resp.status_code == 200





# def test_bad_cooridnates(add_owner_and_member):
#     resp = requests.post(f'{config.url}/user/profile/uploadphoto/v1', json={
#         'token': owner['token'],
#         'img_url': "http://cgi.cse.unsw.edu.au/~morri/morriphoto.jpg",
#         'x_start': 2500,
#         'y_start': 2500,
#         'x_end': 2000,
#         'y_end': 2000
#     })
#     assert resp.status_code == InputError.code
