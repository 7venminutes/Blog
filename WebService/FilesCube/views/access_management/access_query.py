# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020/06/09
Desc: 权限的查询及处理
"""
from database.db_helpers.db_helper import lookup_access_in_the_list
from database.db_helpers import table_access


def get_access_under_path(user_id, path):
    """
    获取某用户在某一路径下的权限
    :param user_id: 用户ID
    :param path: 路径
    :return: {'state':...,'details':...}
    state = 'failed' or 'success'
    details = {'read':BOOL,'new':BOOL,'download':BOOL,'remove':BOOL,'modify':BOOL,'admin':BOOL}
    """
    access_list = table_access.get_access_list_by_id(user_id)
    result = {'read': lookup_access_in_the_list(path, 'read', access_list),
              'new': lookup_access_in_the_list(path, 'new', access_list),
              'download': lookup_access_in_the_list(path, 'download', access_list),
              'remove': lookup_access_in_the_list(path, 'remove', access_list),
              'modify': lookup_access_in_the_list(path, 'modify', access_list),
              'admin': lookup_access_in_the_list(path, 'admin', access_list)}
    return {'state': 'success', 'details': result}
