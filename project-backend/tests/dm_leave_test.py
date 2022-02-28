from src.error import AccessError, InputError
import pytest
import json
import requests
from src import config
from src.auth import auth_register_v2
from src.dm import dm_create_v1, dm_leave_v1, dm_list_v1

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

def test_dm_leave_wrong_dm(datas):
	
	data = datas[0]
	data1 = datas[1]

	requests.delete(f"{config.url}/clear/v1")
	user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
	requests.post(f"{config.url}/auth/register/v2", json=data1)
	data = user1.json()
	dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
	dm_id = dm_id.json()
	dm_id = dm_id['dm_id']
	#request to leave dm with wrong dm id
	resp = requests.post(f"{config.url}/dm/leave/v1", json = {'token': data['token'], 'dm_id': 999})
	response_data = resp.json()
	#it will raise 400 error
	assert(response_data['code'] == 400)

def test_dm_leave_non_member(datas):
	data, data1, data2 = datas

	requests.delete(f"{config.url}/clear/v1")
	user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
	requests.post(f"{config.url}/auth/register/v2", json=data1)
	user3 = requests.post(f"{config.url}/auth/register/v2", json=data2)
	data = user1.json()
	dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'],  'u_ids': [1]})
	dm_id = dm_id.json()
	dm_id = dm_id['dm_id']
	u3_data = user3.json()
	#non-member of dm request to leave dm
	resp = requests.post(f"{config.url}/dm/leave/v1", json = {'token': u3_data['token'], 'dm_id': dm_id})
	response_data = resp.json()
	#it will raise 403 error
	assert(response_data['code'] == 403)	

def test_dm_leave(datas):

	data = datas[0]
	data1 = datas[1]

	requests.delete(f"{config.url}/clear/v1")
	user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
	requests.post(f"{config.url}/auth/register/v2", json=data1)
	data = user1.json()
	dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'],  'u_ids': [1]})
	dm_id = dm_id.json()
	dm_id = dm_id['dm_id']
	
	#shows list of DMs that the user is a member of
	# this will show [0], since the user is a member of dm having dm_id 0
	resp = requests.get(f"{config.url}/dm/list/v1", {'token': data['token']})
	requests.post(f"{config.url}/dm/leave/v1", json = {'token': data['token'], 'dm_id': dm_id})
	#after leave dm, the list of DMs that the user is a member of will be empty
	resp = requests.get(f"{config.url}/dm/list/v1", {'token': data['token']})
	response_data = resp.json()
	assert(response_data == {"dms": []})

