from src.error import AccessError, InputError
import pytest
import json
import requests
from src import config
from src.auth import auth_register_v2


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

def test_dm_create_wrong_users(datas): # pylint: disable=unused-argument
	
	data = datas[0]
	user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
	data = user1.json()
	#create dm with invalid user id [1]
	resp = requests.post(f"{config.url}/dm/create/v1", json = {"token":data['token'], "u_ids": [1]})
	response_data = resp.json()
	# it will raise 400 error
	assert response_data['code'] == 400

def test_dm_create(datas): # pylint: disable=unused-argument
	
	data, data1 = datas 
	requests.delete(f"{config.url}/clear/v1")
	user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
	requests.post(f"{config.url}/auth/register/v2", json=data1)
	data = user1.json()
	#create dm with valid user id
	resp = requests.post(f"{config.url}/dm/create/v1", json = {"token":data['token'], "u_ids": [1]})
	response_data = resp.json()
	#it will return dm_id 0
	assert response_data['dm_id'] == 0


