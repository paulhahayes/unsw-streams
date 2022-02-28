from pluggy.hooks import HookImpl
import pytest
import requests
import imaplib
import email
from src.error import InputError
from src import config
HOST = 'imap.gmail.com'
DEMO_EMAIL = 'teambeagleunsw@gmail.com'
DEMO_PASS = 'Kickflip123!'

@pytest.fixture
def add_owner_and_member():
    requests.delete(f"{config.url}/clear/v1")
    global owner
    global member
    user1 = {
        'email': 'teambeagleunsw@gmail.com',
        'name_first': "paul",
        'name_last': 'hayes',
        'password': 'password'
    }
    user2 = {
        'email': 'paul1@gmailw.com',
        'name_first': "paul",
        'name_last': 'hayes',
        'password': 'passqword'
    }
    owner = requests.post(f'{config.url}/auth/register/v2', json=user1)
    member = requests.post(f'{config.url}/auth/register/v2', json=user2)
    owner = owner.json()
    member = member.json()
    return (owner, member)


def test_password_reset_success(add_owner_and_member):
    token = {'token': owner['token']}
    requests.post(f'{config.url}/auth/logout/v1', json=token)

    requests.post(f'{config.url}/auth/passwordreset/request/v1', json={
        "email": DEMO_EMAIL
    })

    Emails = imaplib.IMAP4_SSL(HOST)
    Emails.login(DEMO_EMAIL, DEMO_PASS)
    Emails.select("inbox")
    # search inbox for all unseen emails
    _, search_data = Emails.search(None, 'UNSEEN')
    _, data = Emails.fetch(search_data[0].split()[0], '(RFC822)')
    # parse data
    _, latest_email = data[0]
    email_message = email.message_from_bytes(latest_email)
    for part in email_message.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True)
            body = body.decode('utf-8')
            body = body.splitlines()
            reset_code = body[2]


    requests.post(f'{config.url}/auth/passwordreset/reset/v1', json={
        'reset_code': reset_code,
        "new_password": "Password123!"
    })

    input = {
        'email': DEMO_EMAIL,
        'password': "Password123!"
    }
    resp = requests.post(f'{config.url}/auth/login/v2', json=input)
    assert resp.status_code == 200


def test_bad_password(add_owner_and_member):
    token = {'token': owner['token']}
    requests.post(f'{config.url}/auth/logout/v1', json=token)
    requests.post(f'{config.url}/auth/passwordreset/request/v1', json={
        "email": DEMO_EMAIL
    })
    Emails = imaplib.IMAP4_SSL(HOST)
    Emails.login(DEMO_EMAIL, DEMO_PASS)
    Emails.select("inbox")
    # search inbox for all unseen emails
    _, search_data = Emails.search(None, 'UNSEEN')
    _, data = Emails.fetch(search_data[0].split()[0], '(RFC822)')
    # parse data
    _, latest_email = data[0]
    email_message = email.message_from_bytes(latest_email)
    for part in email_message.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True)
            body = body.decode('utf-8')
            body = body.splitlines()
            reset_code = body[2]

    resp = requests.post(f'{config.url}/auth/passwordreset/reset/v1', json={
        'reset_code': reset_code,
        "new_password": "1"
    })

    assert resp.status_code == InputError.code


def test_bad_input(add_owner_and_member):
    token = {'token': owner['token']}
    requests.post(f'{config.url}/auth/logout/v1', json=token)
    requests.post(f'{config.url}/auth/passwordreset/request/v1', json={
        "email": DEMO_EMAIL
    })
    Emails = imaplib.IMAP4_SSL(HOST)
    Emails.login(DEMO_EMAIL, DEMO_PASS)
    Emails.select("inbox")
    # search inbox for all unseen emails
    _, search_data = Emails.search(None, 'UNSEEN')
    _, data = Emails.fetch(search_data[0].split()[0], '(RFC822)')
    # parse data
    _, latest_email = data[0]
    email_message = email.message_from_bytes(latest_email)
    for part in email_message.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True)
            body = body.decode('utf-8')
            body = body.splitlines()

    resp = requests.post(f'{config.url}/auth/passwordreset/reset/v1', json={
        'reset_code': "bad reset code",
        "new_password": "GoodPassword"
    })

    assert resp.status_code == InputError.code


def test_cannot_use_reset_code_twice(add_owner_and_member):
    token = {'token': owner['token']}
    requests.post(f'{config.url}/auth/logout/v1', json=token)
    requests.post(f'{config.url}/auth/passwordreset/request/v1', json={
        "email": DEMO_EMAIL
    })
    Emails = imaplib.IMAP4_SSL(HOST)
    Emails.login(DEMO_EMAIL, DEMO_PASS)
    Emails.select("inbox")
    # search inbox for all unseen emails
    _, search_data = Emails.search(None, 'UNSEEN')
    _, data = Emails.fetch(search_data[0].split()[0], '(RFC822)')
    # parse data
    _, latest_email = data[0]
    email_message = email.message_from_bytes(latest_email)
    for part in email_message.walk():
        if part.get_content_type() == "text/plain":
            body = part.get_payload(decode=True)
            body = body.decode('utf-8')
            body = body.splitlines()
            reset_code = body[2]

    requests.post(f'{config.url}/auth/passwordreset/reset/v1', json={
        'reset_code': reset_code,
        "new_password": "Password123!"
    })

    resp = requests.post(f'{config.url}/auth/passwordreset/reset/v1', json={
        'reset_code': reset_code,
        "new_password": "Password123!"
    })

    assert resp.status_code == InputError.code