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


def test_dm_detail_wrong_dm(datas): #pylint: disable=unused-argument
	
	data = datas[0] #pylint: disable=unused-argument
	data1 = datas[1]

	requests.delete(f"{config.url}/clear/v1")
	user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
	requests.post(f"{config.url}/auth/register/v2", json=data1)
	data = user1.json()
	dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [0,1]})
	dm_id = dm_id.json()
	dm_id = dm_id['dm_id']
	#request dm detail with wrong dm_id
	resp = requests.get(f"{config.url}/dm/details/v1", { 'token': data['token'], 'dm_id': 999})
	response_data = resp.json()
	# it will raise 400 error
	assert(response_data['code'] == 400)

def test_dm_detail_non_member(datas): #pylint: disable=unused-argument
	
	data, data1, data2 = datas #pylint: disable=unused-argument
	requests.delete(f"{config.url}/clear/v1")
	user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
	requests.post(f"{config.url}/auth/register/v2", json=data1)
	user3 = requests.post(f"{config.url}/auth/register/v2", json=data2)
	data = user1.json()
	u3_data = user3.json()
	dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
	
	dm_id = dm_id.json()
	dm_id = dm_id['dm_id']
	#non-member of dm request dm detail
	resp = requests.get(f"{config.url}/dm/details/v1", {'token': u3_data['token'], 'dm_id': dm_id})
	response_data = resp.json()
	#it will raise 403 error
	assert(response_data['code'] == 403)

def test_dm_detail(datas): # pylint: disable=unused-argument

	data = datas[0] # pylint: disable=unused-argument
	data1 = datas[1]


	requests.delete(f"{config.url}/clear/v1")
	user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
	requests.post(f"{config.url}/auth/register/v2", json=data1)
	data = user1.json()
	dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'], 'u_ids': [1]})
	dm_id = dm_id.json()
	dm_id = dm_id['dm_id']
	resp = requests.get(f"{config.url}/dm/details/v1", {'token': data['token'], 'dm_id': dm_id})
	response_data = resp.json()
	#it will return user id in dm and name of them
	assert(len(response_data['members'])) == 2

