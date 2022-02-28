from src.error import AccessError, InputError
import pytest
import json
import requests
from src import config, notification
from src.create_token import decode_jwt

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


def test_dm_senddm_msg_wrong_dm(datas):
	
	data = datas[0]
	data1 = datas[1]
	
	requests.delete(f"{config.url}/clear/v1")
	user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
	requests.post(f"{config.url}/auth/register/v2", json=data1)
	data = user1.json()
	dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
	dm_id = dm_id.json()
	dm_id = dm_id['dm_id']
	#request senddm with wrong dm_id
	resp = requests.post(f"{config.url}/message/senddm/v1", json = {'token': data['token'], 'dm_id': 999, 'message': 'Hi'})
	response_data = resp.json()
	#it will raise 400 error
	assert(response_data['code'] == 400)

def test_dm_senddm_msg_length_too_small(datas):
	
	data = datas[0]
	data1 = datas[1]
	
	requests.delete(f"{config.url}/clear/v1")
	user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
	requests.post(f"{config.url}/auth/register/v2", json=data1)
	data = user1.json()
	dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
	dm_id = dm_id.json()
	dm_id = dm_id['dm_id']
	#senddm with 0 length message
	resp = requests.post(f"{config.url}/message/senddm/v1", json = {'token': data['token'], 'dm_id': dm_id, 'message': ''})
	response_data = resp.json()
	#it will raise 400 error
	assert(response_data['code'] == 400)


def test_dm_senddm_msg_length_too_big(datas):
	
	data = datas[0]
	data1 = datas[1]
	
	requests.delete(f"{config.url}/clear/v1")
	user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
	requests.post(f"{config.url}/auth/register/v2", json=data1)
	data = user1.json()
	dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
	dm_id = dm_id.json()
	dm_id = dm_id['dm_id']
	#senddm with exceeding limit (1000) of characters
	message = 'a'
	for _ in range(1002):
		message += 'a'
	resp = requests.post(f"{config.url}/message/senddm/v1", json = {'token': data['token'], 'dm_id': dm_id, 'message': message})
	response_data = resp.json()
	#it will raise 400 error
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
	#non-member is asking to senddm
	resp = requests.post(f"{config.url}/message/senddm/v1", json = {'token': u3_data['token'], 'dm_id': dm_id, 'message': 'hello'})
	response_data = resp.json()
	#it will raise 403 error
	assert(response_data['code'] == 403)


def test_dm_senddm(datas):
	
	data = datas[0]
	data1 = datas[1]
	
	requests.delete(f"{config.url}/clear/v1")
	user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
	user2 = requests.post(f"{config.url}/auth/register/v2", json=data1)
	data = user1.json()
	data1 = user2.json()
	u2 = decode_jwt(data1['token'])
	print(u2)
	handle = u2['handle_str']
	print(handle)
	dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
	dm_id = dm_id.json()
	dm_id = dm_id['dm_id']
	#senddm will return message id. Since the message is empty, message id will be 0
	resp = requests.post(f"{config.url}/message/senddm/v1", json = {'token': data['token'], 'dm_id': dm_id, 'message': f'hello @{handle}'})
	response_data = resp.json()
	assert(str(response_data['message_id'])[0] == "2")


def test_dm_conversation(datas):
	
	data = datas[0]
	data1 = datas[1]

	requests.delete(f"{config.url}/clear/v1")
	user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
	user2=requests.post(f"{config.url}/auth/register/v2", json=data1)
	u_data = user1.json()
	u_data1 = user2.json()
	dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':u_data['token'], 'u_ids': [1]})
	dm_id = dm_id.json()
	dm_id = dm_id['dm_id']
	#user1 and user2 sending dm to each other.
	#the message id will be 0 and then 1
	resp = requests.post(f"{config.url}/message/senddm/v1", json = {'token': u_data['token'], 'dm_id': dm_id, 'message': 'hello'})
	resp1 = requests.post(f"{config.url}/message/senddm/v1", json = {'token': u_data1['token'], 'dm_id': dm_id, 'message': 'how are you'})
	response_data = resp.json()
	response_data1 = resp1.json()
	assert(str(response_data['message_id'])[0] == "2")
	assert(response_data1['message_id'] != response_data['message_id'])
