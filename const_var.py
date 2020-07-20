"""
项目的配置参数
"""
#  database config:

Database_Config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'pwd': 'y2.71828',  # password
}

FileCube_DbConfig = {
    'host': Database_Config['host'],
    'port': Database_Config['port'],
    'user': Database_Config['user'],
    'pwd': Database_Config['pwd'],
    'db_name': 'web_hfs'
}

Starry_DbConfig = {
    'host': Database_Config['host'],
    'port': Database_Config['port'],
    'user': Database_Config['user'],
    'pwd': Database_Config['pwd'],
    'db_name': 'web_starry'
}

DATABASE_HOST = 'localhost'
DATABASE_PORT = 3306
DATABASE_USER = 'root'
DATABASE_PWD = 'y2.71828'
DB_NAME = 'hfs'
