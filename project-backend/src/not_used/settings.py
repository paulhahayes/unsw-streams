import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)
ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL")
ADMIN_PASS = os.environ.get("ADMIN_PASS)