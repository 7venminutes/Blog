# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020/06/02
Desc: user_management模块的路由控制文件，根据不同的路径判断由哪个视图函数来处理请求
"""
from django.conf.urls import url
from django.urls import path
from WebService.FilesCube.views.user_management import views as user_management

urlpatterns = [
    path('', user_management.user_manage),
    url(r'display_user/?$', user_management.get_user_list),
    url(r'make_new_user/?$', user_management.new_user),
    url(r'remove_user/?$', user_management.remove_user),
    url(r'modify_root_dir_of_user/?$', user_management.modify_root_dir_of_user),
]
