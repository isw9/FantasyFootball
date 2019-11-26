import os

class Config(object):
    SECRET_KEY = os.urandom(32)
    MYSQL_DATABASE_USER = 'secret'
    MYSQL_DATABASE_PASSWORD = 'secret'
    MYSQL_DATABASE_DB = 'secret'
    MYSQL_DATABASE_HOST = 'secret'
