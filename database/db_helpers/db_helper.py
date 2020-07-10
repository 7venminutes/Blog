# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020-06-04
Desc: 一些关于路径筛选的函数
"""
# TODO[baixu] 为select_path_in_range添加单元测试， 解决L40注释中的问题
# TODO[baixu] 为if_path_in_the_list和select_root_node添加单元测试
import sys

if '../../' not in sys.path:
    sys.path.append('../../')

from common.key_checker import check_if_have_these_keys


# [baixu] 2020-06-04
# 该函数用来在权限管理界面进行筛选，筛选出A用户在自己拥有管理权限的各路径下的所有权限记录
def select_path_in_range(datalist, access_list):
    """
    利用权限表access_list中的路径权限判断传入的datalist中哪些路径是合法的，将合法路径存入列表中返回
    :param datalist: 待筛选的路径表
    :param access_list: 权限表、权限信息。每条权限信息为字典类型，应至少包含这两个键值：'opt','path'
    （'opt' = 'recursive' or 'current'， 指定了权限是在对应路径下递归生效还是仅在该路径下生效）
    :return: new_data_list 筛选出的合法路径列表
    """
    new_data_list = []
    count = len(datalist)
    for row in datalist:
        for i in access_list:
            if i['opt'] == 'current':
                if row['path'] == i['path']:
                    new_data_list.append(row)
                    break
                    # print(new_data_list)
            elif i['opt'] == 'recursive':
                if row['path'].find(i['path']) == 0:
                    new_data_list.append(row)
                    break
                    # count -= 1
                    # print(new_data_list)
            else:
                break
        count -= 1
        # print(count)
        if count == 0:
            return new_data_list
    # 不是很懂， 在测试时以下语句均未执行， 当时并没有在for循环内设置判断以返回new_data_list
    '''
    print(count)
    print('1111')
    new_data_list.append('111111')
    print(new_data_list)
    return new_data_list
    '''


def lookup_access_in_the_list(path, access, access_info_list):
    """
    在 access_info_list 查找在 path 下是否有 access 权限
    冲突处理规则： 细粒度优先：详情请看对应的测试函数中的描述
        test_if_path_in_the_list in class TestDbHelper in database/uniittest_for_database.py
    :param path: 待判断的路径
    :param access: 询问的权限，为'read','new','download','modify','remove' or 'admin'
    :param access_info_list: 权限列表，每一条权限信息至少含有这些键值：
    'opt','path','read','new','download','modify','remove' and 'admin'
    :return: True or False
    """
    allowed_access_list = ['read', 'new', 'download', 'modify', 'remove', 'admin']
    if access not in allowed_access_list:
        return False
    # access_info_list键值检查
    keys_should_at_least_have = \
        ['opt', 'path', 'read', 'new', 'download', 'modify', 'remove', 'admin']
    for access_record in access_info_list:
        have_keys = check_if_have_these_keys(access_record, keys_should_at_least_have)
        assert have_keys, "传入的access_list中某条数据的键值不全"
    # 开始查询
    access = str(access)
    # 'deciding_record'中'path'和'opt'的初始赋值是有意义的，初始值是一条作用范围最广的权限记录
    result = {'deciding_record': {'path': '', 'opt': 'recursive'}, 'have_access': False}
    # access_record[0] path access_record[1] access access_record[2] opt
    for access_record in access_info_list:
        if not str(access_record['path']).endswith('/'):
            access_record['path'] += '/'
        if access_record['opt'] == 'current' and access_record['path'] == path:
            if len(access_record['path']) >= len(result['deciding_record']['path']):
                result['have_access'] = access_record[access]
                result['deciding_record'] = {'path': access_record['path'], 'opt': 'current'}
        elif access_record['opt'] == 'recursive' and path.find(access_record['path']) == 0:
            # 如果之前的做出权限判断的权限记录中有opt==current的话，这个记录就不用生效了；
            # 若两个记录有交集，current的生效范围肯定比recursive要小
            if result['deciding_record']['opt'] != 'current':
                if len(access_record['path']) > len(result['deciding_record']['path']):
                    result['have_access'] = access_record[access]
                    result['deciding_record'] = {'path': access_record['path'], 'opt': 'recursive'}
    return result['have_access']


def select_root_node(path_list):
    """
    Desc1: 将每条路径看作以该路径为根节点的一棵树，用含最少路径的集合A去替换path_list，
    同时保证按照A与path_list中的路径生成的森林是等效的，用列表的形式返回集合A；
    Desc2: 找出path_list中存在包含关系的路径，将被包含的路径从列表中剔除掉，返回新列表
    :param path_list: 待筛选的路径列表
    :return: 筛选之后的路径列表
    """
    result = []
    while len(path_list) > 0:
        min_length = 0
        min_length_index = 0
        i = 0
        # 选出目前列表中最短的路径，其肯定不被任何其他路径所包含，将之作为基准看是否包含其他路径
        for path in path_list:
            if not str(path).endswith('/'):
                path += '/'
            length = len(str(path))
            if length < min_length:
                min_length = length
                min_length_index = i
            i += 1
        new_root_path = str(path_list.pop(min_length_index))
        result.append(new_root_path)
        # 倒序遍历path_list,避免在循环体内删除path_list数据时出错
        for i in range(len(path_list) - 1, -1, -1):
            # new_root_path包含path_list[i]
            if path_list[i].find(new_root_path) == 0:
                path_list.pop(i)
                # path_list已删除，下面的代码中不能再使用path_list[i],否则可能会数组越界
            # 此处不能将else的情况加入result中，因为不确定该路径是否与path_list中剩余其他路径存在包含关系
        # 继续while循环
    return result

# db_init()
# add_user("zhfs", "zhfs", "E:\zhfs\server\data\\", True)
# add_user("yanbx", "yan271828", "F:")
# data_insert()
# promote_admin("yanbx", "F:\hhhhh", 'curent')
# promote_admin("yanbx", "F:\hhhhh")
# data_display()
# path_list = ['/home/ubuntu/', '/home/ubuntu/ubuntu', '/home/1234/', '/home/ubuntu/learnUI']
# print(select_root_node(path_list))
