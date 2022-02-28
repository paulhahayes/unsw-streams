from locale import resetlocale
import re
from src.error import AccessError, InputError
import pytest
import json
import requests
from src import config
from src.server import dm_create
from datetime import datetime, timedelta

@pytest.fixture
def datas():
	requests.delete(f"{config.url}/clear/v1")
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

def test_message_sendlaterdm_wrong_dm_id(datas):
	
    data = datas[0]
    data1 = datas[1]
	
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    requests.post(f"{config.url}/auth/register/v2", json=data1)
    data = user1.json()
    dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    later = datetime.now() + timedelta(seconds=2)
    later = later.timestamp()
    result = requests.post(f"{config.url}/message/sendlaterdm/v1", json = {'token': data['token'], 'dm_id': 999, 'message': 'hello', 'time_sent': later})
    response_data = result.json()
    #it will raise 400 error
    assert(response_data['code'] == 400)

def test_message_sendlaterdm_message_too_long(datas):
	
    data = datas[0]
    data1 = datas[1]
	
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    requests.post(f"{config.url}/auth/register/v2", json=data1)
    data = user1.json()
    dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    later = datetime.now() + timedelta(seconds=2)
    later = later.timestamp()
    message = 'a'
    for _ in range(1002):
        message += 'a'
    result = requests.post(f"{config.url}/message/sendlaterdm/v1", json = {'token': data['token'], 'dm_id': dm_id, 'message': message, 'time_sent': later})
    response_data = result.json()
    #it will raise 400 error
    assert(response_data['code'] == 400)

def test_message_sendlaterdm_wrong_time(datas):
	
    data = datas[0]
    data1 = datas[1]
	
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    requests.post(f"{config.url}/auth/register/v2", json=data1)
    data = user1.json()
    dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    later = datetime.now() - timedelta(seconds=2)
    later = later.timestamp()
    result = requests.post(f"{config.url}/message/sendlaterdm/v1", json = {'token': data['token'], 'dm_id': dm_id, 'message': 'hello', 'time_sent': later})
    response_data = result.json()
    #it will raise 400 error
    assert(response_data['code'] == 400)


def test_message_sendlaterdm_non_member(datas):
	
    data, data1, data2 = datas
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    requests.post(f"{config.url}/auth/register/v2", json=data1)
    user3 = requests.post(f"{config.url}/auth/register/v2", json=data2)
    data = user1.json()
    data2 = user3.json()
    dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    later = datetime.now() + timedelta(seconds=2)
    later = later.timestamp()
    result = requests.post(f"{config.url}/message/sendlaterdm/v1", json = {'token': data2['token'], 'dm_id': dm_id, 'message': 'hello', 'time_sent': later})
    response_data = result.json()
    #it will raise 400 error
    assert(response_data['code'] == 403)

def test_message_sendlaterdm_v1(datas):
	
    data = datas[0]
    data1 = datas[1]
	
    requests.delete(f"{config.url}/clear/v1")
    user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
    requests.post(f"{config.url}/auth/register/v2", json=data1)
    data = user1.json()
    dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    dm_id = dm_id['dm_id']
    later = datetime.now() + timedelta(seconds=2)
    later = later.timestamp()
    result = requests.post(f"{config.url}/message/sendlaterdm/v1", json = {'token': data['token'], 'dm_id': dm_id, 'message': 'hello', 'time_sent': later})
    #it will raise 400 error
    assert(result.status_code == 200)
