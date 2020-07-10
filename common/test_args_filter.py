# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020/06/03
Desc: args_filter的测试模块
"""
import unittest
import sys
if '../' not in sys.path:
    sys.path.append('../')
from common.args_filter import filter_args


class TestFilterArgs(unittest.TestCase):
    """
    测试
    """
    def test_filter_args(self):
        """
        filter_args应满足的功能：在传入的合法参数列表中选出被*args选出的合法参数，将选出的合法参数放到列表中返回
        :return: null
        """
        self.assertEqual(len(filter_args(['1', '2', 3, '4'], '5', '6', '7', 8)), 0)
        self.assertEqual(len(filter_args(['1', '2', 3, '4'], '5', '6', '7', '3')), 0)
        self.assertEqual(len(filter_args(['1', '2', '3', '4'], '5', '6', '7', '3')), 1)
        self.assertEqual(filter_args(['1', '2', '3', '4'], '5', '6', '7', '3'), ['3'])
        self.assertEqual(filter_args(['volume_path', 'size', 'actual_path', 'path_type', 'is_localhost',
                                      'host_address'], 'volume_path', 'size', 'actual_path'),
                         ['volume_path', 'size', 'actual_path'])


if __name__ == '__main__':
    unittest.main()
