import configparser
import os

config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
config.read(config_path, encoding='utf-8')

# MySQL 配置
MYSQL_CONFIG = {
    'host': config.get('mysql', 'host'),
    'port': config.getint('mysql', 'port'),
    'user': config.get('mysql', 'user'),
    'password': config.get('mysql', 'password'),
    'database': config.get('mysql', 'database'),
    'charset': 'utf8mb4'
}

# 应用配置
SECRET_KEY = config.get('app', 'secret_key')
UPLOAD_FOLDER = config.get('app', 'upload_folder')