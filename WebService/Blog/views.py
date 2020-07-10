"""
Author: Baixu
Date: 2020-07-10
Desc: Blog 模块的视图处理
"""
from django.http import HttpResponseRedirect


def Blog(request, path):
    """
    将所有应该转入BLog站点的请求全部301至443端口的apache服务器处理
    :param request: whatever
    :param path: 请求url中的博客网站部分的路由地址
    :return: HttpResponseRedirect
    """
    return HttpResponseRedirect('https://7venminutes.com/'+path)
