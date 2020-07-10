# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020-06-04
Desc: 单元测试模块，测试database模块中的函数
"""
import sys
import unittest

if '../' not in sys.path:
    sys.path.append('../')
from database.db_helpers import db_helper


class TestDbHelper(unittest.TestCase):
    """
    测试db_helpers.db_helper中的各工具类函数
    """

    def test_lookup_access_in_the_list(self):
        """
        给定权限表C，确定是否有某路径A下的某项权限B
        依据表C中各权限记录为 “A路径下是否有权限B” 进行判断，则很可能依据表C中权限记录C1和C2会得出不同的判断结果
        冲突处理规则： 细粒度优先：C1、C2哪个记录生效范围更小，采用哪个记录的判断
        比如：
        一：
            C1记录在路径"hfs/gabulei/"下以"recursive"方式指定"read"权限为True,
            而C2记录在路径"hfs/gabulei/galeha/"下以"recursive"方式指定"read"权限为False,
            则路径"hfs/gabulei/galeha/111/"下没有"read"权限
        二：
            C1记录在路径"hfs/gabulei/"下以"recursive"方式指定"read"权限为True,
            而C2记录在路径"hfs/gabulei/"下以"current"方式指定"read"权限为False,
            则路径"hfs/gabulei/galeha/"下没有"read"权限
        若C中存在C1和C2的'path'和'opt'均完全相同的情况，函数无视即可
        :return: null
        """
        access_list_1 = [{'opt': 'recursive', 'path': 'hfs/gabulei/', 'read': True, 'new': True,
                          'download': True, 'modify': True, 'remove': True, 'admin': True}]
        access_list_2 = [{'opt': 'current', 'path': 'hfs/gabulei/', 'read': True, 'new': True,
                          'download': True, 'modify': True, 'remove': True, 'admin': True}]
        # 传入异常access参数
        self.assertFalse(db_helper.lookup_access_in_the_list('hfs/galeha/', 'read and delete', access_list_1))
        self.assertFalse(db_helper.lookup_access_in_the_list('hfs/galeha/', 'read and delete', access_list_2))
        # 各access均能正常接受并查询
        self.assertFalse(db_helper.lookup_access_in_the_list('hfs/galeha/', 'read', access_list_1))
        self.assertFalse(db_helper.lookup_access_in_the_list('hfs/galeha/', 'new', access_list_1))
        self.assertFalse(db_helper.lookup_access_in_the_list('hfs/galeha/', 'download', access_list_1))
        self.assertFalse(db_helper.lookup_access_in_the_list('hfs/galeha/', 'modify', access_list_1))
        self.assertFalse(db_helper.lookup_access_in_the_list('hfs/galeha/', 'remove', access_list_1))
        self.assertFalse(db_helper.lookup_access_in_the_list('hfs/galeha/', 'admin', access_list_1))
        # access表中权限指定方式为recursive
        self.assertFalse(db_helper.lookup_access_in_the_list('hfs/galeha/', 'read', access_list_1))
        self.assertTrue(db_helper.lookup_access_in_the_list('hfs/gabulei/galeha/', 'read', access_list_1))
        self.assertTrue(db_helper.lookup_access_in_the_list('hfs/gabulei/', 'read', access_list_1))
        self.assertFalse(db_helper.lookup_access_in_the_list('hfs/gabulei', 'read', access_list_1))
        # access表中权限指定方式为current
        self.assertFalse(db_helper.lookup_access_in_the_list('hfs/galeha/', 'read', access_list_2))
        self.assertFalse(db_helper.lookup_access_in_the_list('hfs/gabulei/galeha/', 'read', access_list_2))
        self.assertTrue(db_helper.lookup_access_in_the_list('hfs/gabulei/', 'read', access_list_2))
        self.assertFalse(db_helper.lookup_access_in_the_list('hfs/gabulei', 'read', access_list_2))
        # 冲突处理
        access_list_3 = [{'opt': 'recursive', 'path': 'hfs/gabulei/', 'read': False, 'new': False,
                          'download': False, 'modify': False, 'remove': False, 'admin': False},
                         {'opt': 'recursive', 'path': 'hfs/gabulei/galeha/', 'read': True, 'new': True,
                          'download': True, 'modify': True, 'remove': True, 'admin': True}]
        self.assertTrue(db_helper.lookup_access_in_the_list('hfs/gabulei/galeha/', 'read', access_list_3))
        access_list_4 = [{'opt': 'recursive', 'path': 'hfs/gabulei/', 'read': True, 'new': False,
                          'download': False, 'modify': False, 'remove': False, 'admin': False},
                         {'opt': 'recursive', 'path': 'hfs/gabulei/galeha/', 'read': False, 'new': True,
                          'download': True, 'modify': True, 'remove': True, 'admin': True}]
        self.assertFalse(db_helper.lookup_access_in_the_list('hfs/gabulei/galeha/', 'read', access_list_4))
        access_list_5 = [{'opt': 'recursive', 'path': 'hfs/gabulei/', 'read': True, 'new': False,
                          'download': False, 'modify': False, 'remove': False, 'admin': False},
                         {'opt': 'current', 'path': 'hfs/gabulei/', 'read': False, 'new': True,
                          'download': True, 'modify': True, 'remove': True, 'admin': True}]
        self.assertFalse(db_helper.lookup_access_in_the_list('hfs/gabulei/', 'read', access_list_5))
        access_list_6 = [{'opt': 'recursive', 'path': 'hfs/gabulei/', 'read': False, 'new': False,
                          'download': False, 'modify': False, 'remove': False, 'admin': False},
                         {'opt': 'current', 'path': 'hfs/gabulei/', 'read': True, 'new': True,
                          'download': True, 'modify': True, 'remove': True, 'admin': True}]
        self.assertTrue(db_helper.lookup_access_in_the_list('hfs/gabulei/', 'read', access_list_6))
        # 传入的权限表中某记录键值对不全
        access_list_7 = [{'opt': 'recursive', 'path': 'hfs/gabulei/', 'read': False, 'new': False,
                          'download': False, 'modify': False, 'remove': False, 'admin': False},
                         {'path': 'hfs/gabulei/', 'read': True, 'new': True,
                          'download': True, 'modify': True, 'remove': True, 'admin': True}]
        self.assertRaises(AssertionError, db_helper.lookup_access_in_the_list, 'hfs/gabulei/', 'read', access_list_7)

    def test_select_root_node(self):
        """
        对某路径的列表进行筛选，找出含有包含关系的路径，并将被包含的路径从列表中剔除
        :return: 筛选之后的列表
        """
        path_list = ['hfs/gabulei/', 'hfs/galeha/', 'hfs/galeha/gagagag/']
        self.assertEqual(db_helper.select_root_node(path_list), ['hfs/gabulei/', 'hfs/galeha/'])
        path_list = ['hfs/gabulei/', 'hfs/galeha/', 'hfs/galeha/']
        self.assertEqual(db_helper.select_root_node(path_list), ['hfs/gabulei/', 'hfs/galeha/'])
        path_list = ['hfs/gabulei/', 'hfs/galeha/', 'hfs/galeha/', 'hfs/galeha123/']
        self.assertEqual(db_helper.select_root_node(path_list), ['hfs/gabulei/', 'hfs/galeha/', 'hfs/galeha123/'])

    def test_select_path_in_range(self):
        """
        该函数用来在权限管理界面进行筛选，根据A用户拥有管理权限的路径列表A1，从权限表B中筛选并保留被A1中任一记录认可的权限
        :return: null
        """
        # TODO[baixu]: 脑子晕了，先不写了，这个函数时权限管理模块用的，权限管理模块还没写。
