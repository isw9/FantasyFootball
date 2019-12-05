import os

class Config(object):
    SECRET_KEY = os.urandom(32)
    MYSQL_DATABASE_USER = 'admin'
    MYSQL_DATABASE_PASSWORD =  'PISkuqOD1QqBLm2ben67FuZSmzOLalxnFPD7UFdY'
    MYSQL_DATABASE_DB = 'fantasyfootball'
    MYSQL_DATABASE_HOST = 'fantasyfootball.crvtzg1tpa0m.us-east-1.rds.amazonaws.com'
