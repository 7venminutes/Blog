# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020/06/01
Desc: address_helper测试模块
"""
import unittest
import sys

if '../' not in sys.path:
    sys.path.append('../')
from common import address_helper


class TestAddressHelper(unittest.TestCase):
    """
    common.address_helper的测试函数
    """
    def test_separate_path(self):
        """
        测试 address_helper.separate_path(path)
        """
        self.assertEqual(address_helper.separate_path('zhfs/A/yanbx/lib'), ['zhfs', 'A', 'yanbx', 'lib'])
        self.assertEqual(address_helper.separate_path('/zhfs/A/yanbx/lib'), ['zhfs', 'A', 'yanbx', 'lib'])
        self.assertEqual(address_helper.separate_path('zhfs/A/yanbx/lib/'), ['zhfs', 'A', 'yanbx', 'lib'])
        self.assertEqual(address_helper.separate_path('\\zhfs\\A\\yanbx\\lib\\', '\\'),
                         ['zhfs', 'A', 'yanbx', 'lib'])
        self.assertEqual(address_helper.separate_path('\\zhfs\\A\\\\yanbx\\lib\\', '\\'),
                         ['zhfs', 'A', 'yanbx', 'lib'])
        self.assertEqual(address_helper.separate_path('\\zhfs\\A\\ \\yanbx\\lib\\', '\\'),
                         ['zhfs', 'A', ' ', 'yanbx', 'lib'])

    def test_is_contain_path(self):
        """
        测试 address_helper.is_contain_path(A,B) which checkes if A is contained in B
        """
        self.assertFalse(address_helper.is_contain_path('zhfs/1234', 'zhfs/123'))
        self.assertTrue(address_helper.is_contain_path('zhfs/1234', 'zhfs'))
        self.assertTrue(address_helper.is_contain_path('zhfs/1234', 'zhfs/'))
        self.assertFalse(address_helper.is_contain_path('/zhfs/1234', '/zhfs/123'))
        self.assertTrue(address_helper.is_contain_path('/zhfs/1234', '/zhfs'))
        self.assertTrue(address_helper.is_contain_path('/zhfs/1234', '/zhfs/'))
        self.assertFalse(address_helper.is_contain_path('zhfs/1234/hhhh', 'zhfs/123/hhhh'))
        self.assertFalse(address_helper.is_contain_path('E:\\zhfs\\1234', 'E:\\zhfs\\123', '\\'))
        self.assertTrue(address_helper.is_contain_path('E:\\zhfs\\1234', 'E:\\zhfs', '\\'))

    def test_find_parent_dir(self):
        """
        测试 address_helper.find_parent_dir(original_dir) 检验是否函数能够成功返回original_dir的父路径
        """
        self.assertEqual(address_helper.find_parent_dir('hfs/hhhh/123')['details'], 'hfs/hhhh/')
        self.assertEqual(address_helper.find_parent_dir('hfs/hhhh/123')['details'], 'hfs/hhhh/')

        # 测试以'/'开头的情况
        self.assertEqual(address_helper.find_parent_dir('/hfs/hhhh/123')['details'], '/hfs/hhhh/')
        self.assertEqual(address_helper.find_parent_dir('/hfs/hhhh/123')['details'], '/hfs/hhhh/')

        # original_dir 没有父路径时
        self.assertFalse(address_helper.find_parent_dir('hhh')['result'])
        self.assertFalse(address_helper.find_parent_dir('/hhh')['result'])

        # 传入的参数不是str类型时
        self.assertRaises(TypeError, address_helper.find_parent_dir, ['gabulei'])

        # 传入的路径不合法， 'hfs//11' 'https://."
        # TODO[baixu] 2020-06-28


if __name__ == '__main__':
    unittest.main()
