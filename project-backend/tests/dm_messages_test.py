from src.error import AccessError, InputError
import pytest
import json
import requests
from src import config
from src.data_store import data_store


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


def test_dm_messages_wrong_dm(datas):
	
	data = datas[0]
	data1 = datas[1]
	
	requests.delete(f"{config.url}/clear/v1")
	user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
	requests.post(f"{config.url}/auth/register/v2", json=data1)
	data = user1.json()
	dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
	dm_id = dm_id.json()
	dm_id = dm_id['dm_id']
	#request dm message with wrong dm_id
	resp = requests.get(f"{config.url}/dm/messages/v1", {'token': data['token'], 'dm_id': 999, 'start': 0})
	response_data = resp.json()
	#it will raise 400 error
	assert(response_data['code'] == 400)


def test_dm_dessages_bigger_start(datas):
	
	data = datas[0]
	data1 = datas[1]
	
	requests.delete(f"{config.url}/clear/v1")
	user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
	requests.post(f"{config.url}/auth/register/v2", json=data1)
	data = user1.json()
	dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
	dm_id = dm_id.json()
	dm_id = dm_id['dm_id']
	#the start is bigger than total number of message
	resp = requests.get(f"{config.url}/dm/messages/v1", {'token': data['token'], 'dm_id': dm_id, 'start': 10})
	response_data = resp.json()
	#this will raise 400 error
	assert(response_data['code'] == 400)

def test_dm_dessages_non_member(datas):
	data, data1, data2 = datas

	requests.delete(f"{config.url}/clear/v1")
	user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
	requests.post(f"{config.url}/auth/register/v2", json=data1)
	user3 = requests.post(f"{config.url}/auth/register/v2", json=data2)
	data = user1.json()
	dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
	dm_id = dm_id.json()
	dm_id = dm_id['dm_id']
	u3_data = user3.json()
	#non member of dm reuqest dm message
	resp = requests.get(f"{config.url}/dm/messages/v1", {'token': u3_data['token'], 'dm_id': dm_id, 'start': 0})
	response_data = resp.json()
	#this will raise 403 error
	assert(response_data['code'] == 403)

def test_dm_message(datas):
	
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
	resp = requests.get(f"{config.url}/dm/messages/v1", {'token': data['token'], 'dm_id': dm_id, 'start': 0})
	response_data = resp.json()
	#since the message is empty, it will show empty 
	assert(response_data['messages'] == [])
	requests.post(f"{config.url}/message/senddm/v1", json = {'token': data['token'], 'dm_id': dm_id, 'message': 'how are you'})
	requests.post(f"{config.url}/message/senddm/v1", json = {'token': data1['token'], 'dm_id': dm_id, 'message': 'hello'})
	resp3 = requests.get(f"{config.url}/dm/messages/v1", {'token': data['token'], 'dm_id': dm_id, 'start': 0})
	response_data3 = resp3.json()
	#since the message is empty, it will show empty 
	assert(response_data3['messages'][0]['message'] == 'how are you')
	assert(response_data3['messages'][1]['message'] == 'hello')

def test_dm_message_50(datas):
	
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
	resp = requests.get(f"{config.url}/dm/messages/v1", {'token': data['token'], 'dm_id': dm_id, 'start': 0})
	response_data = resp.json()
	#since the message is empty, it will show empty 
	assert(response_data['messages'] == [])
	for _ in range(55):
		requests.post(f"{config.url}/message/senddm/v1", json = {'token': data['token'], 'dm_id': dm_id, 'message': 'how are you'})
	resp3 = requests.get(f"{config.url}/dm/messages/v1", {'token': data['token'], 'dm_id': dm_id, 'start': 0})
	response_data3 = resp3.json()
	#since the message is empty, it will show empty 
	assert(len(response_data3['messages']) == 50)
	
