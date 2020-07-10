# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020/06/05
Desc: key_checker的测试模块
"""
import unittest
import sys
if '../' not in sys.path:
    sys.path.append('../')
from common.key_checker import check_if_have_these_keys, check_if_have_this_key


class TestKeyChecker(unittest.TestCase):
    """
    测试
    """
    def test_check_if_have_these_keys(self):
        """
        check_if_have_these_keys的单元测试
        检查字典dict_to_check中是否含有key_list中的键值
        :return: null
        """
        dict_to_test = {'read': True, 'hhh': 'gabulei'}
        self.assertTrue(check_if_have_these_keys(dict_to_test, ['read', 'hhh']))
        self.assertFalse(check_if_have_these_keys(dict_to_test, ['read', 'hhh', 'gabulei']))
        # 不传字典进去
        self.assertRaises(TypeError, check_if_have_these_keys, {'read', 'gabulei'}, ['read'])
        self.assertRaises(TypeError, check_if_have_these_keys, ['read', 'gabulei'], ['read'])

    def test_check_if_have_this_key(self):
        """
        check_if_have_this_key的单元测试
        检查字典dict_to_check中是否含有键值key
        :return: null
        """
        dict_to_test = {'read': True, 'hhh': 'gabulei'}
        self.assertTrue(check_if_have_this_key(dict_to_test, 'read'))
        self.assertFalse(check_if_have_this_key(dict_to_test, 'galeha'))
        # 不传字典进去
        self.assertRaises(TypeError, check_if_have_this_key, {'read', 'gabulei'}, 'read')
