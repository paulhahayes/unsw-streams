from requests.models import to_native_string


def authorised(function):
    def wrapper(*args, **kwargs):
        return funct(*args, **kwargs)
    return wrapper


@authorised
def funct(string):
    return string


x = funct("hello")
print(x)