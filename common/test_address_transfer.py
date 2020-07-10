# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020/06/01
Desc: address_transfer的测试模块
"""
import sys
import unittest
from unittest import mock

if '../' not in sys.path:
    sys.path.append('../')

from common import address_transfer


class TestAddressTransfer(unittest.TestCase):
    """
    TestAddressTransfer用于测试路径解析模块的路径解析函数，测试结果与address_transfer.get_volume_relationship()相关。
    单元测试类中模拟了get_volume_relationship的返回数据，与之进行了解耦
    """
    # address_transfer.get_volume_relationship的返回数据与数据库中存储的信息有关，此处模拟该函数返回的数据进行单元测试
    address_transfer.get_volume_relationship = \
        mock.Mock(return_value=[{'volume': 'zhfs/A/', 'actual_path': '/home/ubuntu/hhhh/', 'sys_str': 'Linux'},
                                {'volume': 'zhfs/A/B/', 'actual_path': '/home/ubuntu/HHHH/', 'sys_str': 'Linux'},
                                {'volume': 'zhfs/', 'actual_path': 'E:\\zhfs\\', 'sys_str': 'Windows'}])

    def test_path_transfer_to_actual_path(self):
        """
        测试 address_transfer.resolve_path_to_actual_path 的功能
        """
        self.assertEqual(address_transfer.resolve_path_to_actual_path('zhfs/A/yanbx/lib')['actual_path'],
                         '/home/ubuntu/hhhh/yanbx/lib')
        self.assertEqual(address_transfer.resolve_path_to_actual_path('zhfs/A/B/heiheihei')['actual_path'],
                         '/home/ubuntu/HHHH/heiheihei')
        self.assertEqual(address_transfer.resolve_path_to_actual_path('zhfs/wanghb/novel/')['actual_path'],
                         'E:\\zhfs\\wanghb\\novel\\')
        self.assertFalse(address_transfer.resolve_path_to_actual_path('blank')['state'])
        self.assertEqual(address_transfer.resolve_path_to_actual_path('blank')['actual_path'],
                         'blank')

    def test_actual_path_transfer_to_path(self):
        """
        测试 address_transfer.resolve_actual_path_to_path 的功能
        """
        self.assertEqual(address_transfer.resolve_actual_path_to_path('E:\\zhfs\\wanghb\\novel\\')['path_in_hfs'],
                         'zhfs/wanghb/novel/')
        self.assertEqual(address_transfer.resolve_actual_path_to_path('/home/ubuntu/HHHH/heiheihei')['path_in_hfs'],
                         'zhfs/A/B/heiheihei')
        self.assertEqual(address_transfer.resolve_actual_path_to_path('/home/ubuntu/hhhh/yanbx/lib')['path_in_hfs'],
                         'zhfs/A/yanbx/lib')
        self.assertEqual(address_transfer.resolve_actual_path_to_path('blank')['path_in_hfs'],
                         'blank')
        self.assertFalse(address_transfer.resolve_actual_path_to_path('blank')['state'])


if __name__ == '__main__':
    unittest.main()
