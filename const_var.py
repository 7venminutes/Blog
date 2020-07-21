"""
项目的配置参数
"""
Database_for_Test = False   # 是否切换到测试用数据库

Database_Config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'pwd': 'y2.71828',  # password
}  # 数据库服务器位置及账号信息

FileCube_DbConfig = {
    'host': Database_Config['host'],
    'port': Database_Config['port'],
    'user': Database_Config['user'],
    'pwd': Database_Config['pwd'],
    'db_name': 'test_web_hfs' if Database_for_Test else 'web_hfs'
}

Starry_DbConfig = {
    'host': Database_Config['host'],
    'port': Database_Config['port'],
    'user': Database_Config['user'],
    'pwd': Database_Config['pwd'],
    'db_name': 'test_web_starry' if Database_for_Test else 'web_starry'
}

DATABASE_HOST = 'localhost'
DATABASE_PORT = 3306
DATABASE_USER = 'root'
DATABASE_PWD = 'y2.71828'
DB_NAME = 'hfs'


