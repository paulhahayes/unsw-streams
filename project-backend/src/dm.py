
from src.auth import auth_login_v2
from src.data_store import data_store
from src.error import AccessError, InputError
import pickle
from src.create_token import decode_jwt
import src.users
#from src.users import check_token
from src.helper_functions import authorised
from src.users import mod_user_stats_v1
import sys


@authorised
def dm_create_v1(token, u_ids): 
	'''
	this function will create dm.
	'''
	try:
		store = pickle.load(open("data.p", "rb"))
	except Exception: # pragma: no cover
		store = data_store.get() # pragma: no cover

	users = store['users']
	dms = store['dms']
	
	#decode token & extract u_id and handle_str inside token
	#token = token['token']
	decoded = decode_jwt(token)
	t_id = decoded['u_id']
	#t_handle = decoded['handle_str']

	valid_users = False
	id_list = []
	#checking the users that DM is directed to is valid
	'''
	for user in users:
		for u_id in u_ids:
			if u_id == user:
				id_list.append[u_id]
	'''
	id_list = [u_id for u_id in u_ids if u_id in users]
	
	if set(u_ids) == set(id_list):
		valid_users = True

	#name should be generated based on the users that are in this DM
	if valid_users:
		#creator of dm should be included...

		handle_list = [users[t_id]['handle_str']]
		for user in range(len(users)):
			if store['users'][user]['u_id'] in u_ids:
				handle_list.append(users[user]['handle_str'])
		
		sorted_list = sorted(handle_list, key=str.lower)
		name = ', '.join(sorted_list)
		
		
		dm_id = len(dms.keys())
		dms[dm_id] = {}
		dms[dm_id]['messages'] = {}
		dms[dm_id]['name'] = name
		dms[dm_id]['users'] = [t_id]
		dms[dm_id]['dm_id'] = dm_id
		for u_id in id_list:
			#this will generate user0, user1 user2.... 
			dms[dm_id]['users'].append(u_id)
		
		#for notification
		message_notification = {'channel_id': -1, 'dm_id': dm_id, 'notification_message': f"{users[t_id]['handle_str']} added you to {name}"}
		for id in id_list:
			store['users'][id]['notification'].append(message_notification)


	if not valid_users:
		raise InputError(description='the users are not valid')


	for id in u_ids:
		mod_user_stats_v1(id, store)
	mod_user_stats_v1(t_id, store)
	src.users.update_workspace_stats(store)

	data_store.set(store)
	
	return { "dm_id": dm_id }

@authorised
def dm_list_v1(token):
	'''
	this will return list of dms that the user is in
	'''
	try:
		store = pickle.load(open("data.p", "rb"))
	except Exception: # pragma: no cover
		store = data_store.get() # pragma: no cover


	token = decode_jwt(token)
	t_id = token['u_id']
	dmss = store['dms']

	
	
	#search list of DM that the user is a member of
	if len(store['dms']) > 0:
		dms = []
		for index in range(len(dmss)):
			if t_id in dmss[index]['users']:
				dict = {
					"dm_id" : index,
					"name" : dmss[index]['name']

				}
				
				dms.append(dict)
		
		return {'dms': dms }
	return {'dms': []}

@authorised
def dm_remove_v1(token, dm_id):
	'''
	only creator will remove existing dm
	'''
	try:
		store = pickle.load(open("data.p", "rb"))
	except Exception: # pragma: no cover
		store = data_store.get() # pragma: no cover
	#token = token['token'] 
	decoded = decode_jwt(token)
	t_id = decoded['u_id']
	users = store['users']
	dms = store['dms']

	#check user is valid
	valid_user = False
	for user in users:
		if t_id == user:
			valid_user = True

	#check dm_id is valid
	valid_dm = False
	creator = False
	for dm in dms:
		if dm_id == dm:
			valid_dm = True
			ids = dms[dm_id]['users']
			if t_id == dms[dm_id]['users'][0]:
				creator = True

	
	#remove dm
	if valid_dm and valid_user and creator:
		dms.pop(dm_id)
		#del dms[dm_id]

	if valid_dm:
		#if dm is valid but the user is not a creator
		if not creator:
			raise AccessError(description='Not a creator')

	if not valid_dm:
		raise InputError(description='not valid dm id')
	for id in ids:
		mod_user_stats_v1(id, store)
	mod_user_stats_v1(t_id, store)
	data_store.set(store)

	return {}

@authorised
def dm_details_v1(token, dm_id):
	'''
	this will return names and users in the dm
	'''
	try:
		store = pickle.load(open("data.p", "rb"))
	except Exception: # pragma: no cover
		store = data_store.get() # pragma: no cover
	#token = token['token']
	token = decode_jwt(token)
	t_id = token['u_id']
	users = store['users']
	dms = store['dms']



	

	#check dm is valid
	valid_dm = False
	valid_user = True
	existing_member =False
	for index in range(len(dms)):
		if dm_id == dms[index]['dm_id']:
			valid_dm = True
			if t_id in dms[index]['users']:
				existing_member = True
	if not valid_dm:
		raise InputError(description='The dm is not valid')
	name = []
	members = []
	if valid_dm and valid_user and existing_member:
		name = dms[dm_id]['name']
		memeber_ids = dms[dm_id]['users']

		for index in range(len(users)):
			for member in memeber_ids:
				if member == users[index]['u_id']:
					user_info = {
						'u_id': users[index]['u_id'],
						'email': users[index]['email'],
						'name_first': users[index]['name_first'],
						'name_last': users[index]['name_last'],
						'handle_str': users[index]['handle_str'],
						'profile_img_url' : users[index]['profile_img_url']
						
					}
					members.append(user_info)


	if not existing_member:
		raise AccessError(description='The user is not a member of dm')

	return{ 'name': name, 'members': members }

@authorised
def dm_leave_v1(token, dm_id):
	'''
	the user will be removed from list of users in dm
	'''
	try:
		store = pickle.load(open("data.p", "rb"))
	except Exception: # pragma: no cover
		store = data_store.get() # pragma: no cover
	#token = token['token']
	decoded = decode_jwt(token)
	t_id = decoded['u_id']
	dms = store['dms']



	

	#check dm is valid
	dm_id = int(dm_id)
	valid_dm = False
	existing_member =False
	for dm in dms:
		if dm_id == dm:
			if t_id in dms[dm_id]['users']:
				existing_member = True
			valid_dm = True

	if not valid_dm:
		raise InputError(description='The dm is not valid')

	if not existing_member:
		raise AccessError(description='The user is not a member of dm')

	#remove user from list of user in the dm
	dms[dm_id]['users'].remove(t_id)
	mod_user_stats_v1(t_id, store)
	data_store.set(store)
	
	return{}

@authorised
def dm_messages_v1(token, dm_id, start):
	'''
	checking messages in dm
	'''
	try:
		store = pickle.load(open("data.p", "rb"))
	except Exception: # pragma: no cover
		store = data_store.get() # pragma: no cover
	#token = token['token']
	decoded = decode_jwt(token)
	t_id = decoded['u_id']
	dms = store['dms']
	#check user is valid




	#check dm is valid
	valid_dm = False
	existing_member =False
	start = int(start)
	for dm in dms:
		if dm == dm_id:
			valid_dm = True
			if t_id in dms[dm_id]['users']:
				existing_member = True
	
	if not valid_dm:
		raise InputError(description='The dm is not valid')

	if not existing_member:
		raise AccessError(description='The user is not a member of dm')
	
	messages = dms[dm_id]['messages']
	

	for index in messages:
		if t_id in messages[index]["reacts"][0]["u_ids"]:
			messages[index]["reacts"][0]['is_this_user_reacted'] = True




	num_of_messages = len(messages)
	
	if start > num_of_messages:
		raise InputError(description='Start is bigger than total number of message')
	fifty_messages = []
    # append the fifty most recent messages
	for i in range(50):
		if (start + i) < num_of_messages:

			fifty_messages.append(messages[start + i])

    # append start and fifty_messages into output dictionary
	output = {}
	output['messages'] = sorted(fifty_messages, key=lambda d: d['time_created'], reverse=True)
	output['start'] = start

	if start + 50 < num_of_messages:
		# if end in range then append it
		# to the output dictionary
		output['end'] = start + 50
	else:
		# output end is -1 when there are less than 50
		# most recent messages from start
		output['end'] = -1
	
	return output

