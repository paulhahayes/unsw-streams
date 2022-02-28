import pytest
import requests
import json
from src import config
from src.error import InputError, AccessError
from src.create_token import generate_jwt, decode_jwt

@pytest.fixture
def add_owner_and_member_one_channel():
    requests.delete(f"{config.url}/clear/v1")
    global owner
    global member
    global channel
    user1 = {
        'email': 'paul@gmail.com',
        'name_first': "paul", 
        'name_last': 'hayes',
        'password': 'password'
    }
    user2 = {
        'email': 'paul2@gmail.com',
        'name_first': "paul",
        'name_last': 'hayes',
        'password': 'passqword'
    }
    owner = requests.post(f'{config.url}/auth/register/v2', json=user1)
    member = requests.post(f'{config.url}/auth/register/v2', json=user2)
    owner = owner.json()
    member = member.json()
    channel_data = { 'token': owner['token'], 'name': "Comp1531", "is_public": True }
    channel  = requests.post(f'{config.url}/channels/create/v2', json=channel_data)
    channel = channel.json()

    return (owner, member, channel)




def test_message_details_success(add_owner_and_member_one_channel):
    """This function tests message_send_v1 on web server."""

    channel_invite = {
        'token': owner['token'], 'channel_id': 1, 'u_id': member['auth_user_id']}
    requests.post(f'{config.url}/channel/invite/v2', json=channel_invite)
    test_message = requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "Hello world"
    })

    channel_details = requests.get(f'{config.url}/channel/details/v2', {
        'token': owner['token'],
        'channel_id': 1
    })

    channel_details = json.loads(channel_details.text)
    test_message = test_message.json()
    orginal_msg = requests.get(f'{config.url}/channel/messages/v2', {
        'token': owner['token'],
        'channel_id': 1,
        'start': 0
    })

    orginal_msg = json.loads(orginal_msg.text)
    assert orginal_msg['messages'][0]['message'] == "Hello world"

    requests.put(f'{config.url}/message/edit/v1', json={
        'token': owner['token'],
        'message_id': test_message['message_id'],
        'message': "Hello mars"
    })
    edit_msg = requests.get(f'{config.url}/channel/messages/v2', {
        'token': owner['token'],
        'channel_id': 1,
        'start': 0
    })
    edit_msg = json.loads(edit_msg.text)
    assert edit_msg['messages'][0]['message'] == "Hello mars"

    requests.delete(f'{config.url}/message/remove/v1', json={
        'token': owner['token'],
        'message_id': test_message['message_id']
    })
    remove_msg = requests.get(f'{config.url}/channel/messages/v2', {
        'token': owner['token'],
        'channel_id': 1,
        'start': 0
    })
    remove_msg = json.loads(remove_msg.text)
    assert len(remove_msg['messages']) == 0

    list = requests.get(f'{config.url}/channels/list/v2', {
        'token': owner['token']
    })
    list = json.loads(list.text)
    assert list['channels'][0]['channel_id'] == 1



def test_bad_message_id(add_owner_and_member_one_channel):
    requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "Hello world"
    })
    resp = requests.put(f'{config.url}/message/edit/v1', json={
        'token': owner['token'],
        'message_id': 99999999,
        'message': "Hello mars"
    })
    resp = resp.json()
    assert resp['code'] == InputError.code


def test_message_send_too_short(add_owner_and_member_one_channel):

    resp = requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': ""
    })
    resp = resp.json()
    assert resp['code'] == InputError.code


def test_message_edit_delete(add_owner_and_member_one_channel):
    test_message = requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "hello world"
    })
    test_message = test_message.json()
    # delete empty
    requests.put(f'{config.url}/message/edit/v1', json={
        'token': owner['token'],
        'message_id': test_message['message_id'],
        'message': ""
    })
    messages = requests.get(f'{config.url}/channel/messages/v2', {
        'token': owner['token'],
        'channel_id': 1,
        'start' : 0
    })
    messages = messages.json()
    assert len(messages['messages']) == 0



def test_message_edit_too_long(add_owner_and_member_one_channel):
    test_message = requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "hello world"
    })
    test_message = test_message.json()
    resp = requests.put(f'{config.url}/message/edit/v1', json={
        'token': owner['token'],
        'message_id': test_message['message_id'],
        'message': "Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Aenean commodo ligula eget dolor. Aenean massa. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Donec quam felis, ultricies nec, pellentesque eu, pretium quis, sem. Nulla consequat massa quis enim. Donec pede justo, fringilla vel, aliquet nec, vulputate eget, arcu. In enim justo, rhoncus ut, imperdiet a, venenatis vitae, justo. Nullam dictum felis eu pede mollis pretium. Integer tincidunt. Cras dapibus. Vivamus elementum semper nisi. Aenean vulputate eleifend tellus. Aenean leo ligula, porttitor eu, consequat vitae, eleifend ac, enim. Aliquam lorem ante, dapibus in, viverra quis, feugiat a, tellus. Phasellus viverra nulla ut metus varius laoreet. Quisque rutrum. Aenean imperdiet. Etiam ultricies nisi vel augue. Curabitur ullamcorper ultricies nisi. Nam eget dui. Etiam rhoncus. Maecenas tempus, tellus eget condimentum rhoncus, sem quam semper libero, sit amet adipiscing sem neque sed ipsum. Nam quam nunc, blandit vel, luctus pulvinar, hendrerit id, lorem. Maecenas nec odio et ante tincidunt tempus. Donec vitae sapien ut libero venenatis faucibus. Nullam quis ante. Etiam sit amet orci eget eros faucibus tincidunt. Duis leo. Sed fringilla mauris sit amet nibh. Donec sodales sagittis magna. Sed consequat, leo eget bibendum sodales, augue velit cursus nunc, quis gravida magna mi a libero. Fusce vulputate eleifend sapien. Vestibulum purus quam, scelerisque ut, mollis sed, nonummy id, metus. Nullam accumsan lorem in dui. Cras ultricies mi eu turpis hendrerit fringilla. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; In ac dui quis mi consectetuer lacinia. Nam pretium turpis et arcu. Duis arcu tortor, suscipit eget, imperdiet nec, imperdiet iaculis, ipsum. Sed aliquam ultrices mauris. Integer ante arcu, accumsan a, consectetuer eget, posuere ut, mauris. Praesent adipiscing. Phasellus ullamcorper ipsum rutrum nunc. Nunc nonummy metus. Vestibulum volutpat pretium libero. Cras id dui. Aenean ut eros et nisl sagittis vestibulum. Nullam nulla eros, ultricies sit amet, nonummy id, imperdiet feugiat, pede. Sed lectus. Donec mollis hendrerit risus. Phasellus nec sem in justo pellentesque facilisis. Etiam imperdiet imperdiet orci. Nunc nec neque. Phasellus leo dolor, tempus non, auctor et, hendrerit quis, nisi. Curabitur ligula sapien, tincidunt non, euismod vitae, posuere imperdiet, leo. Maecenas malesuada. Praesent congue erat at massa. Sed cursus turpis vitae tortor. Donec posuere vulputate arcu. Phasellus accumsan cursus velit. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Sed aliquam, nisi quis porttitor congue, elit erat euismod orci, ac placerat dolor lectus quis orci. Phasellus consectetuer vestibulum elit. Aenean tellus metus, bibendum sed, posuere ac, mattis non, nunc. Vestibulum fringilla pede sit amet augue. In turpis. Pellentesque posuere. Praesent turpis. Aenean posuere, tortor sed cursus feugiat, nunc augue blandit nunc, eu sollicitudin urna dolor sagittis lacus. Donec elit libero, sodales nec, volutpat a, suscipit non, turpis. Nullam sagittis. Suspendisse pulvinar, augue ac venenatis condimentum, sem libero volutpat nibh, nec pellentesque velit pede quis nunc. Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Fusce id purus. Ut varius tincidunt libero. Phasellus dolor. Maecenas vestibulum mollis diam. Pellentesque ut neque. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. In dui magna, posuere eget, vestibulum et, tempor auctor, justo. In ac felis quis tortor malesuada pretium. Pellentesque auctor neque nec urna. Proin sapien ipsum, porta a, auctor quis, euismod ut, mi. Aenean viverra rhoncus pede. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Ut non enim eleifend felis pretium feugiat. Vivamus quis mi. Phasellus a est. Phasellus magna. In hac habitasse platea dictumst. Curabitur at lacus ac velit ornare lobortis. Curabitur a felis in nunc fringilla tristique. Morbi mattis ullamcorper velit. Phasellus gravida semper nisi. Nullam vel sem. Pellentesque libero tortor, tincidunt et, tincidunt eget, semper nec, quam. Sed hendrerit. Morbi ac felis. Nunc egestas, augue at pellentesque laoreet, felis eros vehicula leo, at malesuada velit leo quis pede. Donec interdum, metus et hendrerit aliquet, dolor diam sagittis ligula, eget egestas libero turpis vel mi. Nunc nulla. Fusce risus nisl, viverra et, tempor et, pretium in, sapien. Donec venenatis vulputate lorem. Morbi nec metus. Phasellus blandit leo ut odio. Maecenas ullamcorper, dui et placerat feugiat, eros pede varius nisi, condimentum viverra felis nunc et lorem. Sed magna purus, fermentum eu, tincidunt eu, varius ut, felis. In auctor lobortis lacus. Quisque libero metus, condimentum nec, tempor a, commodo mollis, magna. Vestibulum ullamcorper mauris at ligula. Fusce fermentum. Nullam cursus lacinia erat. Praesent blandit laoreet nibh. Fusce convallis metus id felis luctus adipiscing. Pellentesque egestas, neque sit amet convallis pulvinar, justo nulla eleifend augue, ac auctor orci leo non est. Quisque id mi. Ut tincidunt tincidunt erat. Etiam feugiat lorem non metus. Vestibulum dapibus nunc ac augue. Curabitur vestibulum aliquam leo. Praesent egestas neque eu enim. In hac habitasse platea dictumst. Fusce a quam. Etiam ut purus mattis mauris sodales aliquam. Curabitur nisi. Quisque malesuada placerat nisl. Nam ipsum risus, rutrum vitae, vestibulum eu, molestie vel, lacus. Sed augue ipsum, egestas nec, vestibulum et, malesuada adipiscing, dui. Vestibulum facilisis, purus nec pulvinar iaculis, ligula mi congue nunc, vitae euismod ligula urna in dolor. Mauris sollicitudin fermentum libero. Praesent nonummy mi in odio. Nunc interdum lacus sit amet orci. Vestibulum rutrum, mi nec elementum vehicula, eros quam gravida nisl, id fringilla neque ante vel mi. Morbi mollis tellus ac sapien. Phasellus volutpat, metus eget egestas mollis, lacus lacus blandit dui, id egestas quam mauris ut lacus. Fusce vel dui. Sed in libero ut nibh placerat accumsan. Proin faucibus arcu quis ante. In consectetuer turpis ut velit. Nulla sit amet est. Praesent metus tellus, elementum eu, semper a, adipiscing nec, purus. Cras risus ipsum, faucibus ut, ullamcorper id, varius ac, leo. Suspendisse feugiat. Suspendisse enim turpis, dictum sed, iaculis a, condimentum nec, nisi. Praesent nec nisl a purus blandit viverra. Praesent ac massa at ligula laoreet iaculis. Nulla neque dolor, sagittis eget, iaculis quis, molestie non, velit. Mauris turpis nunc, blandit et, volutpat molestie, porta ut, ligula. Fusce pharetra convallis urna. Quisque ut nisi. Donec mi odio, faucibus at, scelerisque quis,"
    })
    resp = resp.json()
    assert resp['code'] == InputError.code


def test_message_send_bad_channel_id(add_owner_and_member_one_channel):
    resp = requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 9999999,
        'message': "Hello world"
    })
    resp = resp.json()
    assert resp['code'] == InputError.code


def test_message_send_bad_token(add_owner_and_member_one_channel):
    resp = requests.post(f'{config.url}/message/send/v1', json={
        'token': "bad token",
        'channel_id': 1,
        'message': "Hello world"
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code


def test_message_send_user_not_in_channel(add_owner_and_member_one_channel):
    resp = requests.post(f'{config.url}/message/send/v1', json={
        'token': member['token'],
        'channel_id': 1,
        'message': "Hello world"
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code


def test_message_edit_wrong_member(add_owner_and_member_one_channel):
    test_message = requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "hello world"
    })
    test_message = test_message.json()
    resp = requests.put(f'{config.url}/message/edit/v1', json={
        'token': member['token'],
        'message_id': test_message['message_id'],
        'message': "hello"
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code


def test_message_remove(add_owner_and_member_one_channel):
    test_message = requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "hello world"
    })
    test_message = test_message.json()
    requests.delete(f'{config.url}/message/remove/v1', json={
        'token': owner['token'],
        'message_id': test_message['message_id']
    })
    messages = requests.get(f'{config.url}/channel/messages/v2', {
        'token': owner['token'],
        'channel_id': 1,
        'start' : 0
    })
    messages = messages.json()
    assert len(messages['messages']) == 0


def test_message_edit_non_owner_id(add_owner_and_member_one_channel):
    test_message = requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "hello world"
    })
    test_message = test_message.json()
    resp = requests.delete(f'{config.url}/message/remove/v1', json={
        'token': member['token'],
        'message_id': test_message['message_id']
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code


def test_message_edit_wrong_message_id(add_owner_and_member_one_channel):
    test_message = requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "hello world"
    })
    test_message = test_message.json()
    resp = requests.delete(f'{config.url}/message/remove/v1', json={
        'token': owner['token'],
        'message_id': 999999
    })
    resp = resp.json()
    assert resp['code'] == InputError.code


def test_edit_and_remove_multiple(add_owner_and_member_one_channel):
    requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "hello world"
    })
    test_message = requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "I am the test"
    })
    requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "hello world"
    })
    requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "hello world"
    })
    test_message = test_message.json()
    resp = requests.put(f'{config.url}/message/edit/v1', json={
        'token': owner['token'],
        'message_id': test_message['message_id'],
        'message': "hello"
    })
    resp = resp.json()
    assert resp == {}
    resp = requests.delete(f'{config.url}/message/remove/v1', json={
        'token': owner['token'],
        'message_id': test_message['message_id']
    })
    resp = resp.json()
    assert resp  == {}


def dm_user_loggedout(add_owner_and_member_one_channel):
    input = {'token': owner['token']}
    requests.post(f"{config.url}/dm/create/v1", json = {'token':owner['token'], 'u_ids': [1]})
    requests.post(f'{config.url}/auth/logout/v1', json=input)
    resp = requests.post(f'{config.url}/message/senddm/v1', json={
        'token': owner['token'], 
        'dm_id': 1, 
        'message': 'hello'
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code


def dm_user_bad_token(add_owner_and_member_one_channel):
    requests.post(f"{config.url}/dm/create/v1", json = {'token':owner['token'], 'u_ids': [1]})
    corrupt_token = decode_jwt(owner['token'])
    corrupt_token['u_id'] = 999
    corrupt_token = generate_jwt(
        corrupt_token['u_id'], corrupt_token['permission_id'], corrupt_token['handle_str'], corrupt_token['session_id'])
    resp = requests.post(f'{config.url}/message/senddm/v1', json={
        'token': corrupt_token, 
        'dm_id': 1, 
        'message': 'hello'
    })
    resp = resp.json()
    assert resp['code'] == AccessError.code



def test_edit(add_owner_and_member_one_channel):
    test_message = requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "hello world"
    })

    test_message = test_message.json()
    resp = requests.put(f'{config.url}/message/edit/v1', json={
        'token': owner['token'],
        'message_id': test_message['message_id'],
        'message': "guten tag"
    })
    resp = resp.json()
    assert resp == {}
    messages = requests.get(f'{config.url}/channel/messages/v2', {
        'token': owner['token'],
        'channel_id': 1,
        'start' : 0
    })
    messages = messages.json()

def test_edit_dm(add_owner_and_member_one_channel):
    dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':owner['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    msg=requests.post(f"{config.url}/message/senddm/v1", json = {'token': owner['token'], 'dm_id': dm_id['dm_id'], 'message': 'hello'})
    msg = msg.json()
    resp = requests.put(f'{config.url}/message/edit/v1', json={
        'token': owner['token'],
        'message_id': msg['message_id'],
        'message': "guten tag"
    })
    resp = resp.json()
    assert resp == {}
    messages = requests.get(f'{config.url}/dm/messages/v1', {
        'token': owner['token'],
        'dm_id': dm_id['dm_id'],
        'start' : 0
    })
    messages = messages.json()
    assert messages['messages'][0]['message'] == 'guten tag'

def test_remove_dm(add_owner_and_member_one_channel):
    dm_id = requests.post(f"{config.url}/dm/create/v1", json = {'token':owner['token'], 'u_ids': [1]})
    dm_id = dm_id.json()
    msg=requests.post(f"{config.url}/message/senddm/v1", json = {'token': owner['token'], 'dm_id': dm_id['dm_id'], 'message': 'hello'})
    msg = msg.json()
    resp = requests.delete(f'{config.url}/message/remove/v1', json={
        'token': owner['token'],
        'message_id': msg['message_id'],
    })
    resp = resp.json()
    assert resp == {}
    messages = requests.get(f'{config.url}/dm/messages/v1', {
        'token': owner['token'],
        'dm_id': dm_id['dm_id'],
        'start' : 0
    })
    messages = messages.json()
    assert messages['messages'] == []


def test_msg_remove_bad_message_id(add_owner_and_member_one_channel):
    requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "Hello world"
    })
    resp = requests.delete(f'{config.url}/message/remove/v1', json={
        'token': owner['token'],
        'message_id': 99999999,
        'message': "Hello mars"
    })
    resp = resp.json()
    assert resp['code'] == InputError.code



def test_chmsg_remove_bad_message_id(add_owner_and_member_one_channel):
    requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "Hello world"
    })
    resp = requests.delete(f'{config.url}/message/remove/v1', json={
        'token': owner['token'],
        'message_id': 19999999,
        'message': "Hello mars"
    })
    resp = resp.json()
    assert resp['code'] == InputError.code


def test_dmmsg_remove_bad_message_id(add_owner_and_member_one_channel):
    requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "Hello world"
    })
    resp = requests.delete(f'{config.url}/message/remove/v1', json={
        'token': owner['token'],
        'message_id': 29999999,
        'message': "Hello mars"
    })
    resp = resp.json()
    assert resp['code'] == InputError.code

def test_edit_dm_bad_message_id(add_owner_and_member_one_channel):
    requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "Hello world"
    })
    resp = requests.put(f'{config.url}/message/edit/v1', json={
        'token': owner['token'],
        'message_id': 29999999,
        'message': "Hello mars"
    })
    resp = resp.json()
    assert resp['code'] == InputError.code

def test_edit_ch_bad_message_id(add_owner_and_member_one_channel):
    requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "Hello world"
    })
    resp = requests.put(f'{config.url}/message/edit/v1', json={
        'token': owner['token'],
        'message_id': 19999999,
        'message': "Hello mars"
    })
    resp = resp.json()
    assert resp['code'] == InputError.code




def test_edit_2_message_id_2(add_owner_and_member_one_channel):
    requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "Hello world"
    })
    resp = requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "Hello world"
    })
    requests.post(f'{config.url}/message/send/v1', json={
        'token': owner['token'],
        'channel_id': 1,
        'message': "Hello world"
    })
    resp = resp.json()
    resp = requests.put(f'{config.url}/message/edit/v1', json={
        'token': owner['token'],
        'message_id': resp['message_id'],
        'message': "Hello mars"
    })
    assert resp.status_code == 200