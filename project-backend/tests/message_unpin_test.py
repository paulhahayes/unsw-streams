import re
from src.error import AccessError, InputError
import pytest
import json
import requests
from src import config


@pytest.fixture
def datas():
	requests.delete(f"{config.url}/clear/v1")
	global data
	global data1
	data =  {
        'email' : 'hqw@gmailw.com',
        'name_first' : "hansol11",
        'name_last' : 'raspberry',
        'password' : 'password'
    }
	data1 =  {
        'email' : 'qweqwe@gmailw.com',
        'name_first' : "hqwel11",
        'name_last' : 'rasasdfry',
        'password' : 'passqword'
    }
	
	return (data, data1)


def test_messages_unpin_dm_wrong_msg_id(datas):
	
    data = datas[0]
    data1 = datas[1]
	
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    requests.post(f"{config.url}/auth/register/v2", json=data1)
    data = user1.json()
    dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    resp = requests.post(f"{config.url}/message/senddm/v1", json = {'token': data['token'], 'dm_id': dm_id, 'message': 'hello'})
    response_data = resp.json()
    print(response_data)
    result = requests.post(f"{config.url}/message/unpin/v1", json = {'token': data['token'], 'message_id': '999'})
    print(result)
    #it will raise 400 error
    #result = requests.post(f"{config.url}/message/pin/v1", json = {'token': data['token'], 'message_id': response_data['message_id']})
    result = result.json()
    assert(result['code'] == 400)


def test_messages_unpin_dm_msg_wrong_id(datas):
	
    data = datas[0]
    data1 = datas[1]
	
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    requests.post(f"{config.url}/auth/register/v2", json=data1)
    data = user1.json()
    dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    resp = requests.post(f"{config.url}/message/senddm/v1", json = {'token': data['token'], 'dm_id': dm_id, 'message': 'hello'})
    response_data = resp.json()
    print(response_data)
    result = requests.post(f"{config.url}/message/unpin/v1", json = {'token': data['token'], 'message_id': '2999'})
    print(result)
    #it will raise 400 error
    #result = requests.post(f"{config.url}/message/pin/v1", json = {'token': data['token'], 'message_id': response_data['message_id']})
    result = result.json()
    assert(result['code'] == 400)

def test_messages_unpin_dm_no_permission(datas):
	
    data = datas[0]
    data1 = datas[1]
	
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    user2 = requests.post(f"{config.url}/auth/register/v2", json=data1)
    data = user1.json()
    data1 = user2.json()
    dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': []})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    resp = requests.post(f"{config.url}/message/senddm/v1", json = {'token': data['token'], 'dm_id': dm_id, 'message': 'hello'})
    response_data = resp.json()
    requests.post(f"{config.url}/message/pin/v1", json = {'token': data['token'], 'message_id': response_data['message_id']})
    #it will raise 400 error
    result = requests.post(f"{config.url}/message/unpin/v1", json = {'token': data1['token'], 'message_id': response_data['message_id']})
    print(result)
    result = result.json()
    assert(result['code'] == 403)

def test_messages_unpin_dm_alread_unpinned(datas):
	
    data = datas[0]
    data1 = datas[1]
	
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    requests.post(f"{config.url}/auth/register/v2", json=data1)
    data = user1.json()
    dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    resp = requests.post(f"{config.url}/message/senddm/v1", json = {'token': data['token'], 'dm_id': dm_id, 'message': 'hello'})
    response_data = resp.json()
    #requests.post(f"{config.url}/message/unpin/v1", json = {'token': data['token'], 'message_id': response_data['message_id']})
    #it will raise 400 error
    result = requests.post(f"{config.url}/message/unpin/v1", json = {'token': data['token'], 'message_id': response_data['message_id']})
    result = result.json()
    assert(result['code'] == 400)

def test_messages_unpin_dm(datas):
	
    data = datas[0]
    data1 = datas[1]
	
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    requests.post(f"{config.url}/auth/register/v2", json=data1)
    data = user1.json()
    dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    resp = requests.post(f"{config.url}/message/senddm/v1", json = {'token': data['token'], 'dm_id': dm_id, 'message': 'hello'})
    response_data = resp.json()
    result = requests.post(f"{config.url}/message/pin/v1", json = {'token': data['token'], 'message_id': response_data['message_id']})
    print(result)
    #it will raise 400 error
    result = requests.post(f"{config.url}/message/unpin/v1", json = {'token': data['token'], 'message_id': response_data['message_id']})
    result = result.json()
    assert(result == {})

def test_messages_unpin_ch_wrong_msg_id(datas):
	
    data = datas[0]
    data1 = datas[1]
	
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    user2 = requests.post(f"{config.url}/auth/register/v2", json=data1)
    data = user1.json()
    data1 = user2.json()
    new_channel = requests.post(f"{config.url}/channels/create/v2",
                                json={"token": data['token'], "name": "new_channel", "is_public": True})
    new_channel_data = new_channel.json()
    requests.post(f'{config.url}/channel/invite/v2', json={'token' : data['token'], 'channel_id' : new_channel_data['channel_id'], 'u_id' : data['auth_user_id']})
    requests.post(f"{config.url}/message/send/v1", json = {'token': data['token'], 'channel_id': new_channel_data['channel_id'], 'message': 'hello'})
    result = requests.post(f"{config.url}/message/unpin/v1", json = {'token': data['token'], 'message_id': '999'})
    #it will raise 400 error
    result = result.json()
    assert(result['code'] == 400)

def test_messages_unpin_ch_no_permission(datas):
	
    data = datas[0]
    data1 = datas[1]
	
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    user2 = requests.post(f"{config.url}/auth/register/v2", json=data1)
    data = user1.json()
    data1 = user2.json()
    new_channel = requests.post(f"{config.url}/channels/create/v2",
                                json={"token": data['token'], "name": "new_channel", "is_public": True})
    new_channel_data = new_channel.json()
    requests.post(f'{config.url}/channel/invite/v2', json={'token' : data['token'], 'channel_id' : new_channel_data['channel_id'], 'u_id' : data['auth_user_id']})
    message = requests.post(f"{config.url}/message/send/v1", json = {'token': data['token'], 'channel_id': new_channel_data['channel_id'], 'message': 'hello'})

    response_data = message.json()

    result = requests.post(f"{config.url}/message/unpin/v1", json = {'token': data1['token'], 'message_id': response_data['message_id']})
 
    #it will raise 400 error
    result = result.json()
    assert(result['code'] == 403)

def test_messages_unpin_ch_alread_unpinned(datas):
	
    data = datas[0]
    data1 = datas[1]
	
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    user2 = requests.post(f"{config.url}/auth/register/v2", json=data1)
    data = user1.json()
    data1 = user2.json()
    new_channel = requests.post(f"{config.url}/channels/create/v2",
                                json={"token": data['token'], "name": "new_channel", "is_public": True})
    new_channel_data = new_channel.json()
    requests.post(f'{config.url}/channel/invite/v2', json={'token' : data['token'], 'channel_id' : new_channel_data['channel_id'], 'u_id' : data['auth_user_id']})
    message = requests.post(f"{config.url}/message/send/v1", json = {'token': data['token'], 'channel_id': new_channel_data['channel_id'], 'message': 'hello'})

    response_data = message.json()

    #requests.post(f"{config.url}/message/pin/v1", json = {'token': data['token'], 'message_id': response_data['message_id']})
    result = requests.post(f"{config.url}/message/unpin/v1", json = {'token': data['token'], 'message_id': response_data['message_id']})
 
    #it will raise 400 error
    result = result.json()
    assert(result['code'] == 400)

def test_messages_unpin_ch(datas):
	
    data = datas[0]
    data1 = datas[1]
	
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    user2 = requests.post(f"{config.url}/auth/register/v2", json=data1)
    data = user1.json()
    data1 = user2.json()
    new_channel = requests.post(f"{config.url}/channels/create/v2",
                                json={"token": data['token'], "name": "new_channel", "is_public": True})
    new_channel_data = new_channel.json()
    requests.post(f'{config.url}/channel/invite/v2', json={'token' : data['token'], 'channel_id' : new_channel_data['channel_id'], 'u_id' : data['auth_user_id']})
    message = requests.post(f"{config.url}/message/send/v1", json = {'token': data['token'], 'channel_id': new_channel_data['channel_id'], 'message': 'hello'})

    response_data = message.json()

    requests.post(f"{config.url}/message/pin/v1", json = {'token': data['token'], 'message_id': response_data['message_id']})
    result = requests.post(f"{config.url}/message/unpin/v1", json = {'token': data['token'], 'message_id': response_data['message_id']})

    #it will raise 400 error
    result = result.json()
    assert(result == {})


