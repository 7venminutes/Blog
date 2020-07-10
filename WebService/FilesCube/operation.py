# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020-06-04
Desc:
根据业务需求封装定义了一系列的原子操作，
创建文件夹、上传文件、删除文件或文件夹、重命名或移动文件或文件夹、修改用户根目录、查找上级目录等等
"""

import os
import platform
import sys
import pymysql

if '../../' not in sys.path:
    sys.path.append('../../')

from common.address_helper import change_backslash_to_slash, double_backslash
from common.address_transfer import resolve_path_to_actual_path
from const_var import DB_NAME, DATABASE_HOST, DATABASE_PORT, DATABASE_PWD, DATABASE_USER
from database.db_helpers.table_file_tree import get_file_size
sys_str = platform.system()


def make_dir(path, operator_name, dir_name):
    """
    新建文件夹
    :param path: 所在路径
    :param operator_name: 操作者
    :param dir_name: 新建的文件夹名
    :return: {'state':...,'details':...} state = 'failed' or 'success'; details为报错信息或新建的文件夹的信息
    """
    # 此处的path是数据库所存储的路径格式的path
    conn = pymysql.connect(host=DATABASE_HOST, port=DATABASE_PORT, user=DATABASE_USER,
                           passwd=DATABASE_PWD, db=DB_NAME, charset='utf8')
    cursor = conn.cursor()
    result = {'state': 'unknown', 'details': 'unknown'}
    try:
        count = cursor.execute("SELECT * FROM file_tree "
                               "WHERE dir = '" + str(path) + str(dir_name) + "'")
        print('1')
        if count > 0:
            print('2')
            result['state'] = 'failed'
            result['details'] = "已存在同名文件夹"
        else:
            print('3')
            print(path+dir_name)
            path_transferred = resolve_path_to_actual_path(path + dir_name)
            print('3.0.1sss')
            if not path_transferred['state']:
                print('3.1')
                result['state'] = 'failed'
                result['details'] = "路径无法解析"
            else:
                print('3.2')
                os.mkdir(path_transferred['actual_path'])
                print('3.3')
        if result['state'] != 'failed':
            print('4')
            cursor.execute("SELECT ID FROM file_tree WHERE dir='" + str(path) + "'")
            parent_id = -1
            query_result = cursor.fetchall()
            for row in query_result:
                parent_id = row[0]
            if parent_id == -1:
                result['state'] = 'failed'
                result['details'] = "所指定路径不存在"
            else:
                print(parent_id)
                cursor.execute("INSERT INTO file_tree(SIZE, TYPE, NAME, DIR, PARENT_ID) "
                               "VALUES ('-','dir','" + str(dir_name) + "','" + str(path)
                               + str(dir_name) + "/'," + str(parent_id) + ")")
                # 接下来进行操作记录的数据库更新
                # 暂略
                print("新建文件夹成功" + str(dir_name))
                cursor.execute("SELECT ID, size, type, name, dir, parent_id from file_tree "
                               "WHERE dir='" + str(path) + str(dir_name) + "/';")
                row = cursor.fetchone()
                conn.commit()
                conn.close()
                result['state'] = 'success'
                result['details'] = {'ID': row[0], 'name': row[3],
                                     'dir': row[4], 'parent_id': row[5]}
    except Exception as error:
        print(error)
        print("新建文件夹失败，进行回滚")
        conn.rollback()
        conn.close()
        result['state'] = 'failed'
        result['details'] = "新建文件夹失败，进行回滚"
    return result


def upload_file(upload_path, uploader_name, my_file):
    """
    上传文件
    :param upload_path: 上传路径，hfs系统中的路径
    :param uploader_name: 操作者
    :param my_file: request.FILE对象，待上传的文件
    :return: unknown
    """
    if not my_file:
        print('operation.py upload_file: 无上传文件')
        # 文件是否为空的判断应该在函数外完成，此处仅作调试用
    else:
        try:
            conn = pymysql.connect(host=DATABASE_HOST, port=DATABASE_PORT, user=DATABASE_USER,
                                   passwd=DATABASE_PWD, db=DB_NAME, charset='utf8')
            cursor = conn.cursor()
            count = cursor.execute("SELECT * FROM file_tree "
                                   "WHERE dir = '" + str(upload_path) + str(my_file.name) + "'")
            if count > 0:
                print("已存在同名文件或文件夹")
                return
            count = cursor.execute("SELECT * FROM file_tree "
                                   "WHERE dir = '" + str(upload_path) + str(my_file.name) + "/'")
            if count > 0:
                print("已存在同名文件或文件夹")
                return
            actual_upload_path = resolve_path_to_actual_path(upload_path)['actual_path']
            with open(actual_upload_path + my_file.name, 'wb') as file:
                for chunk in my_file.chunks():
                    file.write(chunk)
            file_size = get_file_size(actual_upload_path + my_file.name)
            cursor.execute("SELECT ID FROM file_tree WHERE dir='" + str(upload_path) + "'")
            result = cursor.fetchall()
            parent_id = -1
            for row in result:
                parent_id = row[0]
            if parent_id == -1:
                print("上传路径不存在")
            else:
                print(parent_id)
                cursor.execute("INSERT INTO file_tree(SIZE, TYPE, NAME, DIR, PARENT_ID) "
                               "VALUES ('" + str(file_size) + "','file','" + str(my_file.name) +
                               "','" + str(upload_path) + str(my_file.name) + "','" +
                               str(parent_id) + "')")
                # 接下来进行操作记录的数据库更新
                # 暂略
                print("上传文件成功" + str(my_file.name))
                conn.commit()
                conn.close()
        except Exception as error:
            print(error)
            print("上传失败，进行回滚")
            conn.rollback()
            conn.close()


def remove_file(remove_dir, operator_name):
    """
    删除目录项
    :param remove_dir: 待删除目录项的路径，为hfs系统中的路径，非实际路径
    :param operator_name: 操作者
    :return: unknown
    """
    path_transferred = resolve_path_to_actual_path(remove_dir)
    if not path_transferred['state']:
        print("路径无法解析，不知道删除什么文件")
        return
    else:
        actual_remove_dir = path_transferred['actual_path']
    if os.path.exists(actual_remove_dir):
        if os.path.isdir(actual_remove_dir):
            del_file(actual_remove_dir)
        else:
            os.remove(actual_remove_dir)
    else:
        print("解析后的实际路径不存在！这可能是其他程序对之造成的修改，建议及时做数据同步。")
    # 增加操作记录到数据库中
    # 略


def rename_and_move_file(curr_path, curr_name, des_path, des_name, operator_name):
    """
    重命名或移动目录项（文件或文件夹），并返回操作最后的状态信息
    :param curr_path: 目录项当前所处文件夹的路径
    :param curr_name: 目录项的名称
    :param des_path: 目录项移动至该路径下
    :param des_name: 目录项的新名称
    :param operator_name: 操作者
    :return: {'state':...,'details':...} state = 'failed' or 'success'; details为相关信息
    """
    curr_name = str(curr_name)
    curr_path_transferred = resolve_path_to_actual_path(str(curr_path))
    des_name = str(des_name)
    des_path_transferred = resolve_path_to_actual_path(str(des_path))
    if not curr_path_transferred['state'] or not des_path_transferred['state']:
        state = 'failed'
        details = '路径无法解析'
    else:
        actual_curr_path = curr_path_transferred['actual_path']
        actual_des_path = des_path_transferred['actual_path']
        if not os.path.exists(actual_curr_path + curr_name):
            print(actual_curr_path + curr_name)
            print("当前文件位置不存在")
            state = 'failed'
            details = '当前文件位置不存在'
        elif os.path.exists(actual_des_path + des_name):
            print("目标路径存在同名文件")
            state = 'failed'
            details = '目标路径存在同名文件'
        else:
            try:
                src = "%s%s" % (actual_curr_path, curr_name)
                dst = "%s%s" % (actual_des_path, des_name)
                # print("%s||%s" % (src,dst))
                os.rename(src, dst)
                print("操作完成")
                state = 'success'
                details = '操作完成'
            except OSError as error:
                print(error)
                state = 'failed'
                details = '操作系统移动文件失败' + str(error)

    return {'state': state, 'details': details}


# fixme[baixu][2020-07-03]
def modify_user_root_dir(username, original_root_dir, new_root_dir, append_allowed=True):
    """
    修改用户根目录
    :param username: 用户ID
    :param original_root_dir: 用户原来的根目录
    :param new_root_dir: 用户希望切换到的新的根目录
    :param append_allowed:
    :return:
    """
    username = str(username)
    original_root_dir = str(original_root_dir)
    new_root_dir = str(new_root_dir)
    conn = pymysql.connect(host=DATABASE_HOST, port=DATABASE_PORT, user=DATABASE_USER,
                           passwd=DATABASE_PWD, db=DB_NAME, charset='utf8')
    cursor = conn.cursor()
    count = cursor.execute("SELECT root_dir FROM USER WHERE ID=='" + username + "'")
    root_dir_in_db = ''
    result = cursor.fetchall()
    for row in result:
        root_dir_in_db = row[0]
    if count == 0:
        return {'state': False, 'details': '待修改用户不存在'}
    elif root_dir_in_db is not original_root_dir:
        return {'state': False, 'details': '用户根目录已经变化，可能其他进程修改所致，请刷新后重新发起修改请求'}
    else:
        actual_original_dir = ''
        actual_new_dir = ''
        if sys_str == 'Linux':
            actual_original_dir = change_backslash_to_slash(original_root_dir)
            actual_new_dir = change_backslash_to_slash(new_root_dir)
        original_root_dir_exist = False
        new_root_dir_exist = False
        new_dir_parent_id = None
        new_name = ''
        count = cursor.execute("SELECT parent_id, name FROM file_tree "
                               "WHERE dir='" + new_root_dir + "'")
        result = cursor.fetchall()
        for row in result:
            new_dir_parent_id = row[0]
            new_name = row[1]
        if os.path.exists(actual_original_dir):
            original_root_dir_exist = True
        if os.path.exists(actual_new_dir) and count > 0:
            new_root_dir_exist = True
        if original_root_dir_exist and not new_root_dir_exist:
            # 原路径存在而新路径不存在，重命名
            try:
                if new_dir_parent_id is None:
                    cursor.execute("UPDATE file_tree SET parent_id=null, name='" + new_name + "', \
                    dir='" + new_root_dir + "' WHERE dir='" + original_root_dir + "'")
                else:
                    cursor.execute("UPDATE file_tree SET parent_id='" + new_dir_parent_id + "',\
                    name='" + new_name + "', dir='" + new_root_dir + "' \
                    WHERE dir='" + original_root_dir + "'")
                os.rename(original_root_dir, new_root_dir)
                conn.commit()
                conn.close()
                print("重命名用户根目录，操作完成")
                return {'state': True, 'details': '重命名用户根目录，操作完成'}
            except Exception as error:
                print(error)
                print("操作失败，进行回滚")
                conn.rollback()
                conn.close()
                return {'state': False, 'details': error + '\n重命名用户根目录失败，已进行回滚'}
        elif not original_root_dir_exist and not new_root_dir_exist:
            # 原路径和新路径均不存在，则创建新路径，并更改用户主目录
            try:
                count = cursor.execute("SELECT COUNT(*) FROM file_tree "
                                       "WHERE dir='" + original_root_dir + "'")
                for row in count:
                    count = row[0]
                if count > 0:
                    if new_dir_parent_id is None:
                        cursor.execute("UPDATE file_tree SET parent_id=null, name='" + new_name + "', \
                        dir='" + new_root_dir + "' WHERE dir='" + original_root_dir + "'")
                    else:
                        cursor.execute("UPDATE file_tree SET parent_id='" + new_dir_parent_id + "', \
                        name='" + new_name + "', dir='" + new_root_dir + "' WHERE dir='" + original_root_dir + "'")
                else:
                    if new_dir_parent_id is None:
                        cursor.execute("INSERT INTO file_tree(SIZE, TYPE, NAME, DIR, PARENT_ID) \
                        VALUES ('-','dir','" + new_name + "','" + new_root_dir + "',null)")
                    else:
                        cursor.execute("INSERT INTO file_tree(SIZE, TYPE, NAME, DIR, PARENT_ID) \
                        VALUES ('-','dir','" + new_name + "','" + new_root_dir + "','"
                                       + new_dir_parent_id + "')")
                os.mkdir(actual_new_dir)
                conn.commit()
                conn.close()
                print("新建用户根目录，操作完成")
                return {'state': True, 'details': '新建用户根目录，操作完成'}
            except Exception as error:
                print(error)
                print('新建用户根目录失败，——operation.py modify_user_root_dir '
                      '\'original_root_dir_exist=false,new_root_dir_exist=false\'')
                conn.rollback()
                conn.close()
                return {'state': True, 'details': '新建用户根目录，操作失败，已回滚' + error}
        elif not original_root_dir_exist and new_root_dir_exist:
            # 原路径不存在，新路径存在，按照参数内append_allowed来决定是否进行更改用户主目录， True则更改
            if append_allowed:
                do_something = 2
        else:
            # 原路径与新路径均存在，若参数append_allowed为True，则将目前用户主目录中文件合并至新文件夹中，更改用户主目录
            do_something = 3


def del_file(path):
    """
    递归删除文件夹中所有
    :param path: 待删除的文件夹的路径
    :return: null
    """
    file_list = os.listdir(path)
    for i in file_list:
        c_path = os.path.join(path, i)
        print(c_path)
        if os.path.isdir(c_path):
            try:
                del_file(c_path)
            except OSError:
                pass
        else:
            os.remove(c_path)
    print("remove " + path)
    try:
        os.rmdir(path)
    except OSError:
        pass

