# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020/06/08
Desc: access_management模块的路由控制文件，根据不同的路径判断由哪个视图函数来处理请求
"""
from django.conf.urls import url
from django.urls import path
from WebService.FilesCube.views.access_management import views as access_management

urlpatterns = [
    path('', access_management.access_manage),
    url(r'add_access_record/?$', access_management.add_access_record),
    url(r'display_access/?$', access_management.get_access_list_can_be_managed),
    url(r'display_user_access/?$', access_management.get_access_list_owned_by_userself),
    url(r'remove_redundant_access_records/?$', access_management.clean_up_redundant_records),
]
