from pickle import FLOAT
from src.error import AccessError, InputError
import pytest
import json
import requests
from src import config, notification
from src.create_token import decode_jwt
from datetime import datetime, timedelta
import time

@pytest.fixture
def datas():
	requests.delete(f"{config.url}/clear/v1")
	global data
	global data1
	global data2
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
	data2 =  {
        'email' : 'qzxce@gmailw.com',
        'name_first' : "zxc11",
        'name_last' : 'razxcdfry',
        'password' : 'pazxcqword'
	}
	return (data, data1, data2)

def test_notification_adddm_tag(datas):
	
    data = datas[0]
    data1 = datas[1]
	
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    user2 = requests.post(f"{config.url}/auth/register/v2", json=data1)
    data = user1.json()
    data1 = user2.json()
    u2 = decode_jwt(data1['token'])
    handle = u2['handle_str']
    dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    #senddm will return message id. Since the message is empty, message id will be 0
    requests.post(f"{config.url}/message/senddm/v1", json = {'token': data['token'], 'dm_id': dm_id, 'message': f'hello @{handle}'})
    resp = requests.get(f"{config.url}/notifications/get/v1", {'token' : data1['token']})
    response_data = resp.json()
    assert(len(response_data['notifications']) == 2)

def test_notification_ch_invite_tag(datas):
	
    data = datas[0]
    data1 = datas[1]
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    user2 = requests.post(f"{config.url}/auth/register/v2", json=data1)
    data = user1.json()
    data1 = user2.json()
    u2 = decode_jwt(data1['token'])
    handle = u2['handle_str']
    uid = u2['u_id']
    ch_id = requests.post(f"{config.url}/channels/create/v2", json = {'token':data['token'], 'name': 'sdfsd', 'is_public': True})
    ch_id = ch_id.json()
    ch_id = ch_id['channel_id']
    requests.post(f"{config.url}/channel/invite/v2", json = {'token':data['token'], 'channel_id': ch_id, 'u_id': uid})
    #senddm will return message id. Since the message is empty, message id will be 0
    requests.post(f"{config.url}/message/send/v1", json = {'token': data['token'], 'channel_id': ch_id, 'message': f'hello @{handle}'})
    resp = requests.get(f"{config.url}/notifications/get/v1", {'token' : data1['token']})
    response_data = resp.json()
    assert(len(response_data['notifications']) == 2)


def test_notification_sendlaterdm_tag(datas):
	
    data = datas[0]
    data1 = datas[1]
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    user2 = requests.post(f"{config.url}/auth/register/v2", json=data1)
    data = user1.json()
    data1 = user2.json()
    u2 = decode_jwt(data1['token'])
    handle = u2['handle_str']
    dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    later = datetime.now() + timedelta(seconds=1)
    later = later.timestamp()
    #senddm will return message id. Since the message is empty, message id will be 0
    a = requests.post(f"{config.url}/message/sendlaterdm/v1", json = {'token': data['token'], 'dm_id': dm_id, 'message': f'hello @{handle}', 'time_sent': later})
    print(a.json())
    time.sleep(4)
    resp = requests.get(f"{config.url}/dm/messages/v1", {'token': data['token'], 'dm_id': dm_id, 'start': 0})
    print(resp.json())
    resp = requests.get(f"{config.url}/notifications/get/v1", {'token' : data1['token']})
    response_data = resp.json()
    print(response_data)
    assert(len(response_data['notifications']) == 2)

def test_twenty_limit_notifications(datas):
    data = datas[0]
    data1 = datas[1]
	
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    user2 = requests.post(f"{config.url}/auth/register/v2", json=data1)
    data = user1.json()
    data1 = user2.json()
    u2 = decode_jwt(data1['token'])
    handle = u2['handle_str']
    dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    #senddm will return message id. Since the message is empty, message id will be 0
    requests.post(f"{config.url}/message/senddm/v1", json = {'token': data['token'], 'dm_id': dm_id, 'message': f'hello @{handle}'})
    for _ in range (20):
        requests.post(f"{config.url}/message/senddm/v1", json = {'token': data['token'], 'dm_id': dm_id, 'message': f'hello @{handle}'})
    requests.post(f"{config.url}/message/senddm/v1", json = {'token': data['token'], 'dm_id': dm_id, 'message': f'hello @{handle}'})
    resp = requests.get(f"{config.url}/notifications/get/v1", {'token' : data1['token']})
    response_data = resp.json()
    assert(len(response_data['notifications']) == 20)



def test_dm_react(datas):
    data = datas[0]
    data1 = datas[1]
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    user2 = requests.post(f"{config.url}/auth/register/v2", json=data1)
    data = user1.json()
    data1 = user2.json()
    dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    #senddm will return message id. Since the message is empty, message id will be 0
    dm_id = requests.post(f"{config.url}/message/senddm/v1", json = {'token': data['token'], 'dm_id': dm_id, 'message': 'hello'})
    dm_id = dm_id.json()
    input1 = {
        'token': data['token'], 
        'message_id': dm_id['message_id'],
        'react_id': 1
    }
    result = requests.post(f'{config.url}/message/react/v1', json=input1)
    assert result.status_code == 200


def test_msg_react(datas):
    data = datas[0]
    data1 = datas[1]
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    user2 = requests.post(f"{config.url}/auth/register/v2", json=data1)
    data = user1.json()
    data1 = user2.json()
    u2 = decode_jwt(data1['token'])
    uid = u2['u_id']
    ch_id = requests.post(f"{config.url}/channels/create/v2", json = {'token':data['token'], 'name': 'sdfsd', 'is_public': True})
    ch_id = ch_id.json()
    ch_id = ch_id['channel_id']
    requests.post(f"{config.url}/channel/invite/v2", json = {'token':data['token'], 'channel_id': ch_id, 'u_id': uid})
    #senddm will return message id. Since the message is empty, message id will be 0
    msg_id = requests.post(f"{config.url}/message/send/v1", json = {'token': data['token'], 'channel_id': ch_id, 'message': 'hello'})
    msg_id = msg_id.json()
    input1 = {
        'token': data['token'], 
        'message_id': msg_id['message_id'],
        'react_id': 1
    }
    result = requests.post(f'{config.url}/message/react/v1', json=input1)
    assert result.status_code == 200