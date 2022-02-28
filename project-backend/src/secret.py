from base64 import b64decode

def get_secret_string():
    return b64decode(b'cGc1N21KT0VSdTR3UUpCMTFnTFVWb2VkUWp4YUpnblI=').decode()

def get_email():
    return b64decode(b'dGVhbWJlYWdsZXVuc3dAZ21haWwuY29t').decode()

def get_password():
    return b64decode(b'S2lja2ZsaXAxMjMh').decode()



