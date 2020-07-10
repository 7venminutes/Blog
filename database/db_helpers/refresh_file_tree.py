# -*- coding: utf-8 -*-
"""
以某目录为根目录，进行文件系统内路径结构信息同步
"""
import sys

import pymysql

if '../../' not in sys.path:
    sys.path.append('../../')

from const_var import DB_NAME, DATABASE_USER, DATABASE_PWD, DATABASE_PORT, DATABASE_HOST
import table_file_tree

conn = pymysql.connect(host=DATABASE_HOST, port=DATABASE_PORT, user=DATABASE_USER,
                       passwd=DATABASE_PWD, db=DB_NAME, charset='utf8')
c = conn.cursor()
c.execute("truncate table file_tree;")
conn.commit()
conn.close()
table_file_tree.copy_fs_info_from_os_to_db('E:\\zhfs\\', 'zhfs')
