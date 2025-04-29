import pymysql
from flask import g
from config_manager import MYSQL_CONFIG


def get_db():
    if 'db' not in g:
        g.db = pymysql.connect(
            host=MYSQL_CONFIG['host'],
            port=MYSQL_CONFIG['port'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            database=MYSQL_CONFIG['database'],
            charset=MYSQL_CONFIG['charset'],
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()