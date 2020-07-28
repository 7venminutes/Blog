# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020/06/01
Desc: 与数据表USER有关的操作

TODO[baixu] simplify functions
TODO[baixu] L72 ~ L85 unfinished block
"""
import logging
import os
import platform
import sys

import pymysql

if '../../' not in sys.path:
    sys.path.append('../../')

from common.address_transfer import resolve_path_to_actual_path
from const_var import FileCube_DbConfig, DEBUG_MODE

sys_str = platform.system()


def create_user():
    """
    数据表USER的创建
    :return: null
    """
    conn = pymysql.connect(host=FileCube_DbConfig['host'], port=FileCube_DbConfig['port'], user=FileCube_DbConfig['user'],
                           passwd=FileCube_DbConfig['pwd'], db=FileCube_DbConfig['db_name'], charset='utf8')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE USER
                (ID VARCHAR(20) PRIMARY KEY NOT NULL,
                pwd VARCHAR(20) NOT NULL,
                root_dir VARCHAR(100) NOT NULL,
                sys_admin BOOL NOT NULL);''')
    conn.commit()
    conn.close()


def validation_for_login(user, pwd):
    """
    验证用户名和密码是否匹配
    :param user: 用户ID，字符串类型
    :param pwd: 用户密码，字符串类型
    :return: {'result': BOOL类型, 'sys_admin': BOOL类型, 'root_dir': 字符串类型}
    """
    conn = pymysql.connect(host=FileCube_DbConfig['host'], port=FileCube_DbConfig['port'], user=FileCube_DbConfig['user'],
                           passwd=FileCube_DbConfig['pwd'], db=FileCube_DbConfig['db_name'], charset='utf8')
    cursor = conn.cursor()

    if DEBUG_MODE:
        logging.debug('validation_for_login(%s, %s) is called', str(user), str(pwd))

    cursor.execute("SELECT pwd,sys_admin,root_dir from USER WHERE ID='" + str(user) + "'")
    query_result = cursor.fetchall()
    for row in query_result:
        if DEBUG_MODE:
            logging.debug('another record to match: (\'pwd\',\'sys_admin\',\'root_dir\')(%s)', str(row))
        if pwd == row[0]:
            conn.close()
            return {'result': True, 'sys_admin': row[1], 'root_dir': row[2]}
    conn.close()
    return {'result': False, 'sys_admin': False, 'root_dir': False}


def add_user(user_id, pwd, root_dir, is_sysadmin=False):
    """
    创建用户
    :param user_id: 用户ID，字符串类型
    :param pwd: 用户密码，字符串类型
    :param root_dir: 用户根目录，字符串类型
    :param is_sysadmin: 是否新建管理员用户，布尔类型
    :return: {'state':...,'details':...} 'state'为'failed'或'success'，'details'为附加的详细说明
    """
    user_id = str(user_id)
    pwd = str(pwd)
    root_dir = str(root_dir)
    if not root_dir.endswith('/'):
        raise ValueError(r'传入用来新建用户的用户根目录没有以/结尾')

    _, actual_root_dir = resolve_path_to_actual_path(str(root_dir))
    differ_num = 1  # 当用户根目录与操作系统上某一目录重复时，将该值添加到尾部
    actual_root_dir_temp = actual_root_dir[:-1]  # 去除了末尾的'/'的actual_root_dir
    root_dir_temp = root_dir[:-1]  # 去除了末尾的'/'的root_dir
    while os.path.exists(actual_root_dir):
        actual_root_dir = actual_root_dir_temp + str(differ_num) + '/'
        root_dir = root_dir_temp + str(differ_num) + '/'
        differ_num += 1

    conn = pymysql.connect(host=FileCube_DbConfig['host'], port=FileCube_DbConfig['port'], user=FileCube_DbConfig['user'],
                           passwd=FileCube_DbConfig['pwd'], db=FileCube_DbConfig['db_name'], charset='utf8')
    cursor = conn.cursor()
    try:
        if is_sysadmin:
            cursor.execute("INSERT INTO USER(ID, pwd, root_dir, sys_admin) \
               VALUES ('" + str(user_id) + "','" + str(pwd) + "','" + str(root_dir) + "',TRUE)")
        else:
            logging.debug('添加一个非系统管理员用户: %s', str(user_id))
            cursor.execute("INSERT INTO USER(ID, pwd, root_dir, sys_admin) \
               VALUES ('" + str(user_id) + "','" + str(pwd) + "','" + str(root_dir) + "',FALSE)")
        cursor.execute("INSERT INTO Access_for_path(path, `read`, new, download, remove, modify, admin,"
                       " opt, ID) VALUES ('" + str(root_dir) + "',TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,"
                                                               "'recursive','" + str(user_id) + "')")

        os.mkdir(actual_root_dir)
        state = 'success'
        details = '新建用户成功'
    except Exception as error:
        logging.error('尝试新建用户失败，用户名：%s，密码：%s，根目录：%s，是否为系统管理员：%s',
                      str(user_id), str(pwd), str(root_dir), str(is_sysadmin))
        logging.error(str(error), exc_info=True)
        state = 'failed'
        details = error
        conn.rollback()
    finally:
        conn.commit()
        conn.close()
    return {'state': state, 'details': details}


def remove_user(user_id):
    """
    按照传入的用户ID的值，删除用户表中的某条数据
    :param user_id: 用户ID、str类型
    :return: {'state':...,'details':...} state = 'success' or 'failed'; details = 'XXX'
    """
    user_id = str(user_id)
    # TODO[baixu] 对user_id进行检查，防止SQL注入攻击
    conn = pymysql.connect(host=FileCube_DbConfig['host'], port=FileCube_DbConfig['port'], user=FileCube_DbConfig['user'],
                           passwd=FileCube_DbConfig['pwd'], db=FileCube_DbConfig['db_name'], charset='utf8')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM USER WHERE ID='" + user_id + "'")
    conn.commit()
    conn.close()
    return {'state': 'success', 'details': '用户删除成功'}


def get_user_info(*args):
    """
    获取用户表，参数指定希望返还的数据项，
    :param args: 'ID', 'root_dir', 'sys_admin' 中的一项或多项
    :return: [{'ID':...,'root_dir':...,'sys_admin':...}...] 字典的列表
    """
    # 记录数据表中所有的列的名称
    column_type = ['ID', 'root_dir', 'sys_admin']
    # 过滤传入的参数
    is_selected = {'ID': False, 'root_dir': False, 'sys_admin': False}
    for item in args:
        if item in column_type:
            is_selected[item] = True
        else:
            logging.warning('get_user_info()收到了一个无效参数，数据表USER中没有此列： %s', str(item))
    # --------------------------------
    selected_column = []  # 字符串数组，参数指定的列名称
    sql_str = ""  # sql_str 为将送入SQL语句中拼接查询的字符串
    column_nums = 0  # 希望返回的列的数量
    result = []  # result 为待返回的数据，为字典的数组
    for column in column_type:
        if is_selected[column]:
            selected_column.append(column)
            sql_str += (',' + column)
            column_nums += 1
    if column_nums > 0:
        sql_str = sql_str[1:]  # 去掉第一个逗号
    else:
        return "无有效参数传入，请传入USER的列名"
    # -------------连接数据库开始查询--------------------
    conn = pymysql.connect(host=FileCube_DbConfig['host'], port=FileCube_DbConfig['port'], user=FileCube_DbConfig['user'],
                           passwd=FileCube_DbConfig['pwd'], db=FileCube_DbConfig['db_name'], charset='utf8')
    cursor = conn.cursor()
    cursor.execute("SELECT " + sql_str + " FROM USER")
    raw_result = cursor.fetchall()
    for row in raw_result:
        new_tuple_for_result = {}
        for i in range(column_nums):
            new_tuple_for_result[selected_column[i]] = row[i]
        result.append(new_tuple_for_result)
    conn.close()
    return result


def get_all_user_info():
    """
    返回用户表中存储的所有数据信息
    :return: [{'user_ID':...,'root_dir':...,'sys_admin':...}] 字典的列表
    """
    conn = pymysql.connect(host=FileCube_DbConfig['host'], port=FileCube_DbConfig['port'], user=FileCube_DbConfig['user'],
                           passwd=FileCube_DbConfig['pwd'], db=FileCube_DbConfig['db_name'], charset='utf8')
    cursor = conn.cursor()
    cursor.execute("SELECT ID, root_dir, sys_admin FROM USER")
    datalist = []
    result = cursor.fetchall()
    for row in result:
        datalist.append({'user_ID': row[0],
                         'root_dir': row[1],
                         'sys_admin': row[2]})
    conn.close()
    return datalist


def if_user_exists(user_id):
    """
    用户是否存在
    :param user_id: 用户id
    :return: BOOL
    """
    user_id = str(user_id)
    conn = pymysql.connect(host=FileCube_DbConfig['host'], port=FileCube_DbConfig['port'], user=FileCube_DbConfig['user'],
                           passwd=FileCube_DbConfig['pwd'], db=FileCube_DbConfig['db_name'], charset='utf8')
    cursor = conn.cursor()
    count = cursor.execute("SELECT * FROM USER WHERE ID='" + user_id + "';")
    if count == 0:
        result = False
    else:
        result = True
    conn.close()
    return result
