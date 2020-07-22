# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020/06/02
Desc: 对数据表volume_mapping的相关操作
"""
import logging
import sys
import pymysql

if '../../' not in sys.path:
    sys.path.append('../../')
from const_var import FileCube_DbConfig, DEBUG_MODE
from common import args_filter


def create_volume_mapping():
    """
    创建卷映射关系表
    # volume_path: 卷路径
    # size： 给卷规定的大小
    # actual_path: 卷所对应的实际路径
    # path_type: 实际路径的路径风格，windows 或 linux
    # is_localhost: TRUE 或 FALSE, 实际路径是否在本机上
    # host_address: is_localhost 为 FALSE 时使用该字段获取实际路径所在主机的地址
    # volume_path 为主键， actual_path 和 host_address 组合起来是唯一的
    :return: void
    """
    conn = pymysql.connect(host=FileCube_DbConfig['host'],
                           port=FileCube_DbConfig['port'],
                           user=FileCube_DbConfig['user'],
                           passwd=FileCube_DbConfig['pwd'],
                           db=FileCube_DbConfig['db_name'],
                           charset='utf8')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE volume_mapping
                (volume_path VARCHAR(512) PRIMARY KEY NOT NULL,
                size VARCHAR(10) NOT NULL ,
                actual_path VARCHAR(512) NOT NULL,
                path_type ENUM('Windows','Linux') NOT NULL,
                is_localhost BOOL NOT NULL,
                host_address VARCHAR(20),
                UNIQUE(actual_path, host_address));
                ''')
    conn.commit()
    conn.close()


def get_volume_mapping(*args):
    """
    获取卷映射关系表，参数指定希望返还的列名，
    卷映射关系表的列：volume_path, size, actual_path, path_type, is_localhost, host_address
    如 get_volume_mapping('volume_path', 'actual_path', 'path_type')
    :param args: 'volume_path','size','actual_path','path_type','is_localhost','host_address'中的一种或多种
    :return: state, details state = 'failed' or 'success'; details为报错信息或字典的列表
    """
    # 记录数据表中所有的列的名称
    column_type = ['volume_path', 'size', 'actual_path',
                   'path_type', 'is_localhost', 'host_address']
    selected_columns = args_filter.filter_args(column_type, *args)  # 字符串数组，参数指定的列名称

    if DEBUG_MODE:
        logging.debug('get_volume_mapping()函数接收到的有效参数：')
        for column in selected_columns:
            logging.debug('\t%s', column)
        logging.debug('------')

    sql_str = ",".join(selected_columns)  # sql_str 为将送入SQL语句中拼接查询的字符串
    query_result = []  # query_result 为按照参数要求查询出的数据，为字典的列表

    if len(selected_columns) <= 0:
        state = 'failed'
        details = "无有效参数传入，请传入volume_mapping的列名"
    else:
        # -------------连接数据库开始查询--------------------
        conn = pymysql.connect(host=FileCube_DbConfig['host'],
                               port=FileCube_DbConfig['port'],
                               user=FileCube_DbConfig['user'],
                               passwd=FileCube_DbConfig['pwd'],
                               db=FileCube_DbConfig['db_name'],
                               charset='utf8')
        cursor = conn.cursor()
        cursor.execute("SELECT " + sql_str + " FROM volume_mapping")
        raw_result = cursor.fetchall()
        for row in raw_result:
            new_tuple_for_result = {}
            for i in range(len(selected_columns)):
                new_tuple_for_result[selected_columns[i]] = row[i]
            query_result.append(new_tuple_for_result)
        conn.close()
        state = 'success'
        details = query_result
    return state, details
