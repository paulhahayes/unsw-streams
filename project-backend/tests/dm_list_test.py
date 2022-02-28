from src.error import AccessError, InputError
import pytest
import json
import requests
from src import config



def test_dm_list():
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
	requests.delete(f"{config.url}/clear/v1")
	user1 = requests.post(f"{config.url}/auth/register/v2", json=data)
	requests.post(f"{config.url}/auth/register/v2", json=data1)
	data = user1.json()
	requests.post(f"{config.url}/dm/create/v1", json = {'token':data['token'],  'u_ids': [1]})
	#shows list of DMs that the user is a member of
	#Since the user joined dm_id0, it will show only 0
	resp = requests.get(f"{config.url}/dm/list/v1", {'token': data['token']})
	response_data = resp.json()
	assert(response_data == {"dms": [{'name':"hansol11raspberry, hqwel11rasasdfry", "dm_id" : 0}]})

