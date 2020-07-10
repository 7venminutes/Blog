# -*- coding: utf-8 -*-
"""
Arthur: Baixu
Date: 2020/06/03
Desc: 数据表file_tree的相关操作
"""
import os
import queue
import platform
import sys
import pymysql

if '../../' not in sys.path:
    sys.path.append('../../')
# 自定义的python脚本
from common.address_transfer import resolve_path_to_actual_path, resolve_actual_path_to_path
from common.args_filter import filter_args
from const_var import DB_NAME, DATABASE_PWD, DATABASE_USER, DATABASE_PORT, DATABASE_HOST

sys_str = platform.system()  # sys_str = 'Linux' 或 'Windows'
file_tree = 'file_tree'  # 数据表file_tree的名称


def create_file_tree():
    """
    创建文件树数据表，用于存储整个hfs系统的目录结构
    ID 无符号整数、自增序列、表的主键，用于唯一标识文件树中的每个数据项，可理解为Linux中的inode\n
    size 长度不超过10位的字符串，表示对应文件的大小，若数据项的类型为dir，则此项为 '-'\n
    type 数据项类型， 为'file'或'dir'中的一种， 后续可能对此项进行扩展， 增加'img'、'text'等类型\n
    name 数据项名称、长度不超过128的字符串\n
    dir 数据项的路径（数据项所在目录的路径+数据项的名称，若数据项类型为文件夹，还要在末尾再加上'/'），长度不超过512的字符串\n
    parent_id 无符号整型，与ID相关联，表示该数据项的父节点，无父节点的数据项将此列留空\n
    :return: null
    """
    conn = pymysql.connect(host=DATABASE_HOST, port=DATABASE_PORT, user=DATABASE_USER,
                           passwd=DATABASE_PWD, db=DB_NAME, charset='utf8')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE file_tree
            (ID INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
            size VARCHAR(10) NOT NULL ,
            type ENUM('file','dir') NOT NULL,
            name VARCHAR(128) NOT NULL ,
            dir VARCHAR(512) NOT NULL,
            parent_id INT unsigned,FOREIGN KEY(parent_id) REFERENCES file_tree(ID) ON DELETE CASCADE ON UPDATE CASCADE);
            ''')
    conn.commit()
    conn.close()


def if_path_exists(path):
    """
    文件系统中是否有此路径
    :param path: 待查询的路径
    :return: BOOL
    """
    path = str(path)
    conn = pymysql.connect(host=DATABASE_HOST, port=DATABASE_PORT, user=DATABASE_USER,
                           passwd=DATABASE_PWD, db=DB_NAME, charset='utf8')
    cursor = conn.cursor()
    count = cursor.execute("SELECT * FROM " + file_tree + " WHERE dir='"+path+"';")
    if count == 0:
        result = False
    else:
        result = True
    conn.close()
    return result


def get_file_tree(*args):
    """
    获取数据表file_tree，参数指定希望返还的列的名称，
    :param args: 'ID','size','type','name','dir','parent_id'中的一项或多项
    :return: {'state':...,'details':...}
    state = 'failed' or 'success'; details为报错信息或查询出的数据（字典的列表）
    """
    parameters_allowed = ['ID', 'size', 'type', 'name', 'dir', 'parent_id']
    columns_selected = filter_args(parameters_allowed, *args)
    result = {'state': 'unknown', 'details': 'unknown'}
    query_result = []  # 通过sql查询出的数据，为字典的列表
    if len(columns_selected) == 0:
        result['state'] = 'failed'
        result['details'] = '传入的有效参数为零'
    else:
        sql_str = ",".join(columns_selected)
        conn = pymysql.connect(host=DATABASE_HOST, port=DATABASE_PORT, user=DATABASE_USER,
                               passwd=DATABASE_PWD, db=DB_NAME, charset='utf8')
        cursor = conn.cursor()
        cursor.execute("SELECT " + sql_str + " FROM " + file_tree)
        raw_result = cursor.fetchall()
        for row in raw_result:
            tmp_result_detail = {columns_selected[i]: row[i] for i in range(len(columns_selected))}
            query_result.append(tmp_result_detail)
        result['state'] = 'success'
        result['details'] = query_result
        conn.close()
    return result


# WARN[baixu] 下面这个函数是从操作系统层面获取并计算文件大小、放在此处似乎不是很妥当
def get_file_size(file_dir):
    """
    根据传入的文件实际存储的位置，计算并返回文件的大小
    :param file_dir: 文件或文件夹的实际存储位置
    :return: 若file_dir为文件夹则返回‘-’，若为文件则返回以'B'、'KB'或'MB'结尾的字符串
    """
    if not os.path.exists(file_dir):
        return '文件失效, 计算大小时已被其他程序删除'
    elif os.path.isdir(file_dir):
        return '-'
    else:
        size = os.path.getsize(file_dir) / 1024 / 1024
        if size >= 1:
            return str(round(size, 2)) + 'MB'
        else:
            size *= 1024
            if size >= 1:
                return str(round(size, 2)) + 'KB'
            else:
                return str(round(size * 1024, 2)) + 'B'


def list_dir(hfs_dir_path):
    """
    输入文件夹路径，返回文件夹下一级的文件列表
    :param hfs_dir_path: hfs系统中某文件夹的路径
    :return: {'state':...,'details':[{'type':...,'name':...,'id':...,'dir':...,'size':...}]}
    """
    hfs_dir_path = str(hfs_dir_path)
    conn = pymysql.connect(host=DATABASE_HOST, port=DATABASE_PORT, user=DATABASE_USER,
                           passwd=DATABASE_PWD, db=DB_NAME, charset='utf8')
    cursor = conn.cursor()
    count = cursor.execute("SELECT id, type FROM file_tree WHERE dir = '"+hfs_dir_path+"';")
    if count == 0:
        state = 'failed'
        details = '路径不存在'
    elif count == 1:
        query_result = cursor.fetchone()
        if query_result[1] != 'dir':
            state = 'failed'
            details = '路径不是文件夹'
        else:
            cursor.execute("SELECT type, name, id, dir, size FROM file_tree "
                           "WHERE parent_id="+str(query_result[0])+";")
            state = 'success'
            details = []
            file_list = cursor.fetchall()
            for file in file_list:
                details.append({'type': file[0], 'name': file[1],
                                'id': file[2], 'dir': file[3],
                                'size': file[4]})
    else:
        conn.close()
        raise Exception("file_tree 表中发现重名目录项，dir="+hfs_dir_path)
    conn.close()
    return {'state': state, 'details': details}


def copy_fs_info_from_os_to_db(rt_dir, volume_name):
    """
    以当前所运行的操作系统上某一文件夹为根目录，将其下所属子树的目录信息同步至hfs系统中
    :param rt_dir: 作为根目录的操作系统上的某文件夹的路径
    :param volume_name: rt_dir在hfs系统上的对应路径
    :return: null
    """

    class Item:
        """
        数据类型，表示一个目录项的信息，用来往waiting_queue里面插入
        """

        def __init__(self):
            self.id = 1
            self.name = ""
            self.parent_id = -1
            self.type = "dir"
            self.dir = ""
            self.size = '-'

    print(rt_dir)
    print(resolve_actual_path_to_path(rt_dir))
    if not resolve_actual_path_to_path(rt_dir)['state']:
        print('---卷映射关系不存在，请检查卷是否配置成功---')
        return

    root_dir = Item()
    root_dir.size = get_file_size(rt_dir)
    root_dir.dir = resolve_actual_path_to_path(rt_dir)['path_in_hfs']
    root_dir.name = volume_name

    waiting_queue = queue.Queue()
    waiting_queue.put(root_dir)
    conn = pymysql.connect(host=DATABASE_HOST, port=DATABASE_PORT, user=DATABASE_USER,
                           passwd=DATABASE_PWD, db=DB_NAME, charset='utf8')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO file_tree(type, name, dir, size)\
     VALUES ('" + str(root_dir.type) + "','" + str(root_dir.name) + "','" + root_dir.dir
                   + "','" + root_dir.size + "');")
    while not waiting_queue.empty():
        data_dir = waiting_queue.get()
        actual_data_dir = resolve_path_to_actual_path(data_dir.dir)['actual_path']
        cursor.execute("SELECT ID from file_tree WHERE dir='" + data_dir.dir + "';")
        query_result = cursor.fetchall()
        for row in query_result:
            data_dir.id = row[0]
        for file in os.listdir(actual_data_dir):
            if os.path.isdir(actual_data_dir + file):
                if sys_str == 'Windows':
                    new_actual_dir = actual_data_dir + file + '\\'
                else:
                    new_actual_dir = actual_data_dir + file + '/'
                new_dir = resolve_actual_path_to_path(new_actual_dir)['path_in_hfs']
                cursor.execute("INSERT INTO file_tree(type, name, parent_id, dir, size) \
                            VALUES ('dir','" + file + "','" + str(data_dir.id) + "','" + new_dir + "','-')")
                cursor.execute("SELECT ID from file_tree WHERE dir='" + new_dir + "'")
                new_file = Item()
                query_result = cursor.fetchone()
                new_file.id = query_result[0]
                new_file.name = file
                new_file.parent_id = data_dir.id
                new_file.type = 'dir'
                new_file.dir = new_dir
                waiting_queue.put(new_file)
            else:
                new_dir = data_dir.dir + file
                cursor.execute("INSERT INTO file_tree(type, name, parent_id, dir, size) \
                                VALUES ('file','" + str(file) + "','" + str(data_dir.id) + "','" +
                               new_dir + "','" + get_file_size(actual_data_dir + file) + "')")
    conn.commit()
    conn.close()
