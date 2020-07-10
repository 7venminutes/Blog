# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020-06-04
Desc: 初始化项目、（重置文件系统信息、重置用户信息、重置卷映射信息、重置用户权限信息）
"""
# TODO[baixu] :权限初始化和用户表的初始化没有考虑路径映射的问题
import platform
import sys
import pymysql

if '../' not in sys.path:
    sys.path.append('../')

from common import address_helper, address_transfer
from database.db_helpers import table_file_tree, table_user, table_access
from const_var import DB_NAME, DATABASE_PWD, DATABASE_PORT, DATABASE_USER, DATABASE_HOST

# root_path 为文件系统第一个卷所对应的实际路径
root_path = 'E:\\db_demo\\'
root_dir_name = 'db-demo'
USER_LIST = [{'id': 'yanbx', 'password': 'yan271828', 'root_dir': 'hfs/', 'is_sys_admin': 1}]
ACCESS_LIST = [{'path': 'hfs/', 'read': 1, 'new': 1, 'download': 1, 'remove': 1,
                'modify': 1, 'admin': 1, 'opt': 'recursive', 'id': 'yanbx'}]
# 自动获取本机运行系统
sys_str = platform.system()

conn = pymysql.connect(host=DATABASE_HOST, port=DATABASE_PORT, user=DATABASE_USER,
                       passwd=DATABASE_PWD, db=DB_NAME, charset='utf8')
c = conn.cursor()

# 1111111111111111111111111111111111111
# 重置卷映射表，添加卷
# 1111111111111111111111111111111111111
c.execute("TRUNCATE TABLE volume_mapping")
c.execute("INSERT INTO volume_mapping(volume_path, size, actual_path, path_type, is_localhost) \
            VALUES('hfs/','500GB','" + root_path.replace('\\', '\\\\') + "','" + sys_str + "', TRUE);")
conn.commit()
print('卷挂载完毕')

# 2222222222222222222222222222222222222
# 以卷的实际目录为根目录，同步实际目录下的目录结构
# 2222222222222222222222222222222222222
c.execute("TRUNCATE TABLE file_tree;")
table_file_tree.copy_fs_info_from_os_to_db(root_path, 'hfs')
print("所新增卷下的目录结构已与实际目录结构同步")

# 3333333333333333333333333333333333333
# 以下内容仍未修改
# 3333333333333333333333333333333333333
c.execute("DELETE FROM USER")
# 默认初始化一个无根目录的系统管理员
c.execute("INSERT INTO USER(ID, password, root_dir, sys_admin) VALUES ('zhfs', 'zhfs', 'blank', '1')")
for user in USER_LIST:
    c.execute("INSERT INTO USER(id, password, root_dir, sys_admin) values ('"
              + user['id'] + "','" + user['password'] + "','" + user['root_dir'] + "',"
              + str(user['is_sys_admin']) + ")")
conn.commit()
print("数据库中用户表已按指定数据初始化")

c.execute("DELETE FROM Access_for_path")
for access in ACCESS_LIST:
    c.execute("INSERT INTO Access_for_path(PATH, `READ`, NEW, DOWNLOAD, REMOVE, MODIFY, ADMIN, OPT, ID) \
        VALUES ('" + access['path'] + "','" + str(access['read']) + "','" + str(access['new']) + "','" +
              str(access['download']) + "','" + str(access['remove']) + "','" + str(access['modify']) + "','" +
              str(access['admin']) + "','" + str(access['opt']) + "','" + str(access['id']) + "')")
conn.commit()
print("数据库权限表初始化完成")

conn.close()
