# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020-06-04
Desc: 数据表 Access_for_path 的相关操作
"""
import sys

import pymysql

if '../../' not in sys.path:
    sys.path.append('../../')

from const_var import DB_NAME, DATABASE_USER, DATABASE_PWD, DATABASE_PORT, DATABASE_HOST


def modify_access(user_id, path, opt='recursive', access='all_TRUE'):
    """
    修改用户权限
    :param user_id: 用户ID
    :param path: 路径
    :param opt: 权限以何种方式赋予到该路径上，'recursive' or 'current'
    :param access: 'all_True' or 'all_False'
    :return: null
    """
    conn = pymysql.connect(host=DATABASE_HOST, port=DATABASE_PORT, user=DATABASE_USER, passwd=DATABASE_PWD,
                           db=DB_NAME, charset='utf8')
    cursor = conn.cursor()
    user_id = str(user_id)
    path = str(path)
    opt = str(opt)
    cursor.execute("SELECT path, read, new, download, remove, modify, admin, opt from Access_for_path \
                WHERE ID='" + user_id + "'")
    access_list = cursor.fetchall()
    done = False
    for row in access_list:
        if row[0] == str(path):
            if row[7] == opt:
                if access == 'all_TRUE':
                    cursor.execute("UPDATE Access_for_path SET read=TRUE,new=TRUE,download=TRUE,remove=TRUE,\
                        modify=TRUE,admin=TRUE WHERE path='" + str(path) + "' \
                        AND opt='" + opt + "'AND ID='" + user_id + "'")
                    done = True
                    break
                elif access == 'all_FALSE':
                    cursor.execute("UPDATE Access_for_path SET read=FALSE,new=FALSE,download=FALSE,remove=FALSE,\
                        modify=FALSE,admin=FALSE WHERE path='" + str(path) + "' \
                        AND opt='" + opt + "' AND ID='" + user_id + "'")
                    done = True
                    break
    if not done:
        if access == 'all_TRUE':
            cursor.execute("INSERT INTO Access_for_path(path, read, new, download, remove, modify, admin, opt, ID) \
            VALUES('" + path + "',TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,'" + opt + "','" + user_id + "') ")
        elif access == 'all_FALSE':
            cursor.execute("INSERT INTO Access_for_path(path, read, new, download, remove, modify, admin, opt, ID) \
            VALUES('" + path + "',FALSE,FALSE,FALSE,FALSE,FALSE,FALSE,'" + opt + "','" + user_id + "') ")
    conn.commit()
    conn.close()


def remove_access_by_id(user_id):
    """
    删除该用户ID下所有权限，删除用户时调用该函数
    :param user_id: 用户ID
    :return: {'state':...,'details':...}
    """
    try:
        conn = pymysql.connect(host=DATABASE_HOST, port=DATABASE_PORT, user=DATABASE_USER,
                               passwd=DATABASE_PWD, db=DB_NAME, charset='utf8')
        cursor = conn.cursor()
        user_id = str(user_id)
        cursor.execute("DELETE FROM Access_for_path WHERE ID='" + user_id + "';")
        conn.commit()
        conn.close()
    except Exception as error_msg:
        print(error_msg)
        return {'state': 'failed', 'details': user_id + '所拥有的权限未能删除'}

    return {'state': 'success', 'details': user_id + '拥有的权限均已删除'}


def modify_some_access(user_id, path, read, new, download, remove, modify, admin, opt='recursive'):
    """
    修改用户权限，可指定具体修改哪些权限
    :param user_id: 用户ID
    :param path: 路径
    :param read: 进入该路径浏览的权限，BOOL
    :param new: 在该路径下新建文件夹或上传文件的权限，BOOL
    :param download: 下载该路径下文件的权限，BOOL
    :param remove: 删除该路径下文件或文件夹的权限，BOOL
    :param modify: 修改文件的权限，重命名需要修改权限，移动需要源路径和目标路径下均有修改权限，BOOL
    :param admin: 该路径下的管理权限，有管理权限的用户可以管理其他用户在该路径下的权限，BOOL
    :param opt: 赋予的权限是仅在path路径下生效，还是在path及其所有子目录下均生效，
    opt = 'recursive' or 'current'
    :return: null
    """
    conn = pymysql.connect(host=DATABASE_HOST, port=DATABASE_PORT, user=DATABASE_USER,
                           passwd=DATABASE_PWD, db=DB_NAME, charset='utf8')
    cursor = conn.cursor()
    user_id = str(user_id)
    path = str(path)
    opt = str(opt)
    read = str(read).upper()
    new = str(new).upper()
    download = str(download).upper()
    remove = str(remove).upper()
    modify = str(modify).upper()
    admin = str(admin).upper()
    cursor.execute("SELECT path, `read`, new, download, remove, modify, admin, opt from Access_for_path \
                    WHERE ID='" + user_id + "'")
    access_list = cursor.fetchall()
    done = False
    for row in access_list:
        if row[0] == path and row[7] == opt:
            cursor.execute("UPDATE Access_for_path SET `read`=" + read + ",new=" + new + ",download=" + download + ",\
            remove=" + remove + ",modify=" + modify + ",admin=" + admin + " \
            WHERE path='" + path + "' AND opt='" + opt + "' AND ID='" + user_id + "'")
            done = True
            break
    if not done:
        cursor.execute("INSERT INTO Access_for_path(path, `read`, new, download, remove, modify, admin, opt, ID) \
                VALUES('" + path + "'," + read + "," + new + "," + download + "," + remove + "," + modify + "," + admin + ",'" + opt + "','" + user_id + "')")
    conn.commit()
    conn.close()


def get_access_list():
    """
    获取权限表Access_for_path
    :return: {'state':...,'details':...}
    details = [{'path':...,'read':...,'new':...,'download':...,
                'remove':...,'modify':...,'admin':...,'opt':...,
                'ID':...}] 或报错信息
    """
    access_list = []
    conn = pymysql.connect(host=DATABASE_HOST, port=DATABASE_PORT, user=DATABASE_USER,
                           passwd=DATABASE_PWD, db=DB_NAME, charset='utf8')
    cursor = conn.cursor()
    cursor.execute("SELECT path, `read`, new, download, remove, modify,"
                   " admin, opt, ID FROM Access_for_path")
    query_result = cursor.fetchall()
    for record in query_result:
        access_list.append({'path': record[0], 'read': record[1], 'new': record[2],
                            'download': record[3], 'remove': record[4], 'modify': record[5],
                            'admin': record[6], 'opt': record[7], 'ID': record[8]})
    conn.close()
    return {'state': 'success', 'details': access_list}


def get_access_list_by_id(user_id):
    """
    获取某个用户的权限列表
    :param user_id: 用户ID
    :return: [{'path':...,'read':...,'new':...,'download':...,
    'remove':...,'modify':...,'admin':...,'opt':...}]
    """
    conn = pymysql.connect(host=DATABASE_HOST, port=DATABASE_PORT, user=DATABASE_USER,
                           passwd=DATABASE_PWD, db=DB_NAME, charset='utf8')
    cursor = conn.cursor()
    user_id = str(user_id)
    cursor.execute("SELECT path, `read`, new, download, remove, modify, admin, opt "
                   "FROM Access_for_path WHERE ID='" + user_id + "'")
    access_list = cursor.fetchall()
    data_list = []
    for row in access_list:
        data_list.append({'path': row[0], 'read': row[1], 'new': row[2], 'download': row[3],
                          'remove': row[4], 'modify': row[5], 'admin': row[6], 'opt': row[7]})
    conn.close()
    return data_list


def get_access_list_excluding_id(user_id):
    """
    获取除某个用户之外其他用户的权限
    :param user_id: 用户ID
    :return: [{'user_id':...,'path':...,'read':...,'new':...,'download':...,
    'remove':...,'modify':...,'admin':...,'opt':...}]
    """
    conn = pymysql.connect(host=DATABASE_HOST, port=DATABASE_PORT, user=DATABASE_USER,
                           passwd=DATABASE_PWD, db=DB_NAME, charset='utf8')
    cursor = conn.cursor()
    user_id = str(user_id)
    cursor.execute("SELECT path, `read`, new, download, remove, modify, admin, opt, ID "
                   "FROM Access_for_path WHERE ID!='" + user_id + "'")
    access_list = cursor.fetchall()
    data_list = []
    for row in access_list:
        data_list.append({'path': row[0], 'read': row[1], 'new': row[2], 'download': row[3],
                          'remove': row[4], 'modify': row[5], 'admin': row[6], 'opt': row[7],
                          'user_id': row[8]})
    conn.close()
    return data_list
