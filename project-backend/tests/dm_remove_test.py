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

def test_dm_remove_wrong_dm(datas):
	
	data, data1 = datas
	
	requests.delete(f"{config.url}/clear/v1")
	user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
	requests.post(f"{config.url}/auth/register/v2", json=data1)
	data = user1.json()
	dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
	dm_id = dm_id.json()
	dm_id = dm_id['dm_id']
	#request dm remove with wrong dm_id
	resp = requests.delete(f"{config.url}/dm/remove/v1", json = {'token': data['token'], 'dm_id': 999})
	response_data = resp.json()
	#it will raise 400 error
	assert(response_data['code'] == 400)


def test_dm_remove_non_creator(datas):
	
	data, data1 = datas
	
	requests.delete(f"{config.url}/clear/v1")
	user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
	user2 = requests.post(f"{config.url}/auth/register/v2", json=data1)
	data = user1.json()
	global data2
	data2 = user2.json()
	dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'],  'u_ids': [1]})
	dm_id = dm_id.json()
	dm_id = dm_id['dm_id']
	#non-creator request dm remove
	resp = requests.delete(f"{config.url}/dm/remove/v1", json = {'token': data2['token'], 'dm_id': dm_id})
	response_data = resp.json()
	#this will raise 403 error
	assert(response_data['code'] == 403)

def test_dm_remove(datas):
	
	data, data1 = datas
	
	requests.delete(f"{config.url}/clear/v1")
	user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
	requests.post(f"{config.url}/auth/register/v2", json=data1)
	data = user1.json()
	dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'],  'u_ids': [1]})
	dm_id = dm_id.json()
	dm_id = dm_id['dm_id']
	#this will show [0], which is dm_id that the user is a member of
	resp = requests.get(f"{config.url}/dm/list/v1", {'token': data['token']})
	requests.delete(f"{config.url}/dm/remove/v1", json = {'token': data['token'], 'dm_id': dm_id})
	#since the dm that the user is in is removed, dm list will show empty list
	resp = requests.get(f"{config.url}/dm/list/v1", {'token': data['token']})
	response_data = resp.json()
	assert(response_data == {"dms": []})

