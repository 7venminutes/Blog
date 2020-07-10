# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020/06/08
Desc: volume_management模块的路由控制文件，根据不同的路径判断由哪个视图函数来处理请求
"""
from django.conf.urls import url
from WebService.FilesCube.views.volume_management import views as volume_management

urlpatterns = [
    url(r'display_volume_mapping/$', volume_management.display_volume),
    url(r'make_new_volume/$', volume_management.create_normal_volume),
    url(r'remove_volume/$', volume_management.remove_normal_volume),
]
