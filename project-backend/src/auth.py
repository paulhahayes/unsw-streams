"""
This Python program contains the functions that gernate user IDs
and Implement the run login process for the UNSW streams Project

"""
import pickle
import re
import datetime
from datetime import timezone
import pytz
import hashlib
from src.data_store import data_store
from src.error import AccessError, InputError
from src.create_token import generate_session_id, generate_jwt, decode_jwt
from src.secret import get_email, get_password
from src import config
import smtplib
import random
import ssl
from email.message import EmailMessage


OWNER = 1
MEMBER = 2

def make_random_string():
    random_string = ""
    for _  in range (6):
        # these are assci code ranges
        char = chr(random.randrange(48, 57))
        random_string += char
    return random_string


def check_email(email):
    """Given an email this fucntion checks that is within the characters set out"""

    # Sets a pattern to follow
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    if re.fullmatch(pattern, email):
        return True
    else:  # pragma: no cover
        return False  # pragma: no cover


def create_handle(name_first, name_last):
    """Given a first and last name create a unqiue username as a str"""

    store = data_store.get()
    # concatinate string
    raw_string = name_first.lower() + name_last.lower()
    # create a pattern for the strings
    pattern = r'[^a-z0-9]'
    # filter out the chars not required
    filtered_string = re.sub(pattern, "", raw_string)
    # reduce the size of the string to max 20 chars
    potential_handle = filtered_string[:20]

    # addresses edge case of clash - username1 and username1 = username10
    if potential_handle[-1].isnumeric():  # pylint: disable=simplifiable-if-statement
        case_number_last = True
    else:
        case_number_last = False

    for i in range(len(store['users'])):
        # if the handles clash
        if str(potential_handle) == str(store['users'][i]['handle_str']):

            # for readability create variable conflict handle
            conflict_handle = store['users'][i]['handle_str']

            if case_number_last or not conflict_handle[-1].isnumeric():
                # case 1
                # For example there is a clash paulhayes1 with paulhayes1
                # paulhayes1 with paulhayes1 = paulhayes10
                # if paulhayes10 is taken it would become paulhayes11
                # until it found a free number
                # case 2
                # paulhayes with paulhayes just becomes
                # paulhayes0
                # append a "0" to the username
                potential_handle = potential_handle + "0"
                case_number_last = False
                i = 0

            # if the last char is a letter
            elif conflict_handle[-1].isnumeric() and case_number_last == False:  # pylint: disable = singleton-comparison  # pragma: no branch
                # increment the number by 1
                # convert to a list
                potential_handle = list(potential_handle)
                # create a incremented number
                new_last_number = int(potential_handle[-1]) + 1
                # change the last charcter
                potential_handle[-1] = str(new_last_number)
                # update the handle
                potential_handle = "".join(potential_handle)
                i = 0
            # repeat the process

    # set the final handle
    unique_handle = potential_handle
    return unique_handle


def auth_login_v2(email, password):
    """Checks that the email and password match"""
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception:  # pragma: no cover
        store = data_store.get()  # pragma: no cover

    for index in store['users']:
        if email == store['users'][index]['email']:
            if hashlib.sha256(password.encode()).hexdigest() == store['users'][index]['password']:
                session_id = generate_session_id()
                store['users'][index]['session_id'].append(session_id)
                # get information
                u_id = store['users'][index]['u_id']
                permission_id = store['users'][index]['permission_id']
                handle_str = store['users'][index]['handle_str']
                token = generate_jwt(u_id, permission_id,
                                     handle_str, session_id)

                data_store.set(store)
                # with open('data.p', 'wb') as FILE:
                #     pickle.dump(store, FILE)

                return {

                    'token': token,
                    'auth_user_id': u_id,
                }
    raise InputError(description='Invalid user details')


def auth_logout_v1(token):

    decode_id = decode_jwt(token)
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception:  # pragma: no cover
        store = data_store.get()  # pragma: no cover

    removed_user = False
    for user in store['removed_users']:
        if decode_id['u_id'] == user['u_id']:
            removed_user = True
            break

    regular_user = False
    for user in store['users']:
        if decode_id['u_id'] == store['users'][user]['u_id']:
            regular_user = True
            break

    if not regular_user and not removed_user:
        raise AccessError(description="Unkown user")

    if decode_id['session_id'] not in store['users'][decode_id['u_id']]['session_id']:
        raise AccessError(description="User already logged out")

    store['users'][decode_id['u_id']]['session_id'].remove(
        decode_id['session_id'])
    data_store.set(store)
    return {}


def auth_register_v2(email, password, name_first, name_last):
    """If information is valid this function will store the data and create a user """
    # set up
    #############
    # collect the data
    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception:  # pragma: no cover
        store = data_store.get()  # pragma: no cover

    # create the current length of the list
    u_id = (len(store['users']))
    # create a timestamp
    dt = datetime.datetime.now(tz=pytz.UTC)
    timestamp = int(dt.timestamp())
  
    #############

    # tests
    #############
    if not check_email(email):
        raise InputError(description='Invalid email')
    if len(password) < 6:
        raise InputError(description='Invalid Password')
    if len(name_first) < 1 or len(name_first) > 50:  # pylint: disable = len-as-condition
        raise InputError(description='Invalid Name')
    if len(name_last) < 1 or len(name_last) > 50:  # pylint: disable = len-as-condition
        raise InputError(description='Invalid Name')
    # test duplicates
    for user in store['users']:
        if email == store['users'][user]['email']:
            raise InputError(description='Duplicate email')
    ############

    # handle
    handle = create_handle(name_first, name_last)

    # password
    password = hashlib.sha256(password.encode()).hexdigest()
    # permssion
    permission_id = MEMBER
    if u_id == 0:
        permission_id = OWNER
    # session id
    session_id = generate_session_id()

    token = generate_jwt(u_id, permission_id, handle, session_id)

    new_valid_user = {u_id: {'email': email, 'password': password,
                             "name_first": name_first, "name_last": name_last,
                             "timestamp": timestamp, "handle_str": handle, "u_id": u_id, "session_id": [session_id], "permission_id": permission_id, 'profile_img_url' : config.url+"static/unswstreams.jpg", 'notification': []}}

    store['user_stats'][u_id] = {}
    store['user_stats'][u_id].update({'channels_joined' : [{"num_channels_joined" : 0, "time_stamp" :  timestamp }] })
    store['user_stats'][u_id].update({'dms_joined' : [  {"num_dms_joined" : 0, "time_stamp" :  timestamp }] })
    store['user_stats'][u_id].update( {'messages_sent' : [{"num_messages_sent" : 0, "time_stamp" :  timestamp }] })
    store['user_stats'][u_id].update({ 'involvement_rate' : float(0) })

    store['users'].update(new_valid_user)
    data_store.set(store)

    return {
        'token': token,
        'auth_user_id': u_id,
    }



def auth_passwordreset_request_v1(email):
    # check current sessions

    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception:  # pragma: no cover
        store = data_store.get()  # pragma: no cover

    
    reset_code = make_random_string()
    valid_email = False
    for index in range(len(store['users'])):
        if store['users'][index]['email'] == email:
            valid_email = True
            store['users'][index]['session_id'] == []
            store['users'][index].update({'reset_code': reset_code})

    if valid_email:
        Auth_Email = get_email()
        Auth_Password = get_password()
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(Auth_Email, Auth_Password)
            resetmessage = EmailMessage()
            resetmessage['Subject'] = "UNSW Streams password reset"
            resetmessage['From'] = Auth_Email
            resetmessage['To'] = email

            resetmessage.set_content(f"""
Hi, Your password reset code is:
{reset_code}""")

            server.send_message(resetmessage)
    data_store.set(store)
    return {}


def auth_passwordreset_reset_v1(reset_code, new_password):

    try:
        store = pickle.load(open("data.p", "rb"))
    except Exception:  # pragma: no cover
        store = data_store.get()  # pragma: no cover

    if len(new_password) < 6:
        raise InputError(description='password length is invalid')

    reset_success = False
    for index in range(len(store['users'])):
        response_status = store['users'][index].get('reset_code')
        if response_status == reset_code:
            # encrypt the password
            new_password = hashlib.sha256(new_password.encode()).hexdigest()
            store['users'][index]['password'] = new_password
            # delete the old pw
            del store['users'][index]['reset_code']
            reset_success = True
            break

    if not reset_success:
        raise InputError(description='reset code not valid')
    data_store.set(store)
    return {}
