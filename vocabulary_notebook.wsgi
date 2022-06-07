import sys
import os
import random
import string
sys.path.insert(0, '/var/www/portfolio/flask_app/vocabulary_notebook')
from app import app as application

os.environ["DATABASE_HOST"] = "localhost"
os.environ["DATABASE_PORT"] = "3306"
os.environ["DATABASE_USER"] = "yuto"
os.environ["DATABASE_PASS"] = "@Amuamu923"
os.environ["MAIL_ID"] = "tailangh830@gmail.com"
os.environ["MAIL_PASS"] = "takukihime4"
os.environ["MAIL_HOST"] = "smtp.gmail.com"
os.environ["MAIL_PORT"] = "587"
