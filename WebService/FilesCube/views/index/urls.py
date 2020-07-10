# -*- coding: utf-8 -*-
"""
Author: Baixu
Date: 2020/06/08
Desc: index模块的路由控制文件，根据不同的路径判断由哪个视图函数来处理请求
"""
from django.conf.urls import url
from django.urls import path
from WebService.FilesCube.views.index import views as index

urlpatterns = [
    path('', index.homepage),
    url(r'display_file_list/$', index.get_file_list_under_dir),
    url(r'get_files_under_dir/$', index.get_file_list_under_dir),
    url(r'file_tree_navigation/$', index.display_file_tree),
    url(r'remove_file/$', index.remove_file),
    url(r'rename_or_move/$', index.rename_or_move),
    url(r'make_dir/$', index.make_dir),
    url(r'back_to_parent_dir/$', index.back_to_parent_dir),
]
