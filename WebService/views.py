"""
Author: Baixu
Date: 2020-07-10
Desc: 网站主入口的视图函数
"""
from django.http import HttpResponseRedirect
from django.shortcuts import render


def homepage(request):
    return render(request, 'homepage.html')


def redirect(request, path):
    """
    所有url均匹配失效时调用该函数，通知用户重定向至对应的https链接再尝试一次
    :param path: 用户提交的url
    :param request: WSGI对象，用户的这次网络请求
    :return: 重定向的回复
    """
    print('redirect %s' % path)
    return HttpResponseRedirect('https://7venminutes.com/' + path)
