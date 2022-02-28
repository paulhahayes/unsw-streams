import pytest
from src.secret import get_secret_string, get_email, get_password


def test_get_string():
    assert "pg57mJOERu4wQJB11gLUVoedQjxaJgnR" == get_secret_string()

def test_get_email():
    assert "teambeagleunsw@gmail.com" == get_email()

def test_get_password():
    assert "Kickflip123!" == get_password()