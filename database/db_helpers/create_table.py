# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020/05/15
Desc: 创建表
"""
import sys
import pymysql

if '../../' not in sys.path:
    sys.path.append('../../')

from const_var import DB_NAME, DATABASE_HOST, DATABASE_PORT, DATABASE_USER, DATABASE_PWD
from database.db_helpers import table_volume_mapping

table_volume_mapping.create_volume_mapping()


def create_access_for_path():
    """
    创建数据表 Access_for_path，用于存储每个用户在对应路径下的权限
    :return: null
    """
    conn = pymysql.connect(host=DATABASE_HOST, port=DATABASE_PORT, user=DATABASE_USER,
                           passwd=DATABASE_PWD, db=DB_NAME, charset='utf8')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE Access_for_path
                (path VARCHAR(128) NOT NULL,
                `read` BOOL NOT NULL,
                new BOOL NOT NULL,
                download BOOL NOT NULL,
                remove BOOL NOT NULL,
                modify BOOL NOT NULL,
                admin BOOL NOT NULL,
                opt   ENUM('recursive','current') NOT NULL,
                ID    VARCHAR(20), FOREIGN KEY(ID) REFERENCES USER(ID) ON DELETE CASCADE ON UPDATE CASCADE,
                PRIMARY KEY (path,ID));''')
    conn.commit()
    conn.close()
